/**
 * Sage Reality 11: Your Monthly Money Forecast ($22.22, one month per order).
 * - [sr_money_forecast_reading]: the reading page, unlocked for paid orders (private link with order key),
 *   logged-in buyers and site admins. The buyer picks this month or next month; the first forecast created
 *   locks the order to that month (birth details can still be corrected). Shows the reading on the page and
 *   downloads the PDF.
 * - REST route sr11mon/v1/reading forwards to the chart service (/v1/money-month) using the SR11 Birth Chart
 *   plugin's saved service URL and key.
 * - Adds the "Create My Forecast" link to the order confirmation page and the customer's order emails.
 * The "Instant reports" snippets handle the emailed copies, saved birth details and auto-complete (prefix mon).
 */
if ( ! defined( 'SR_MON_PRODUCT_ID' ) ) { define( 'SR_MON_PRODUCT_ID', 10609 ); }
if ( ! defined( 'SR_MON_PORTAL_PATH' ) ) { define( 'SR_MON_PORTAL_PATH', '/your-monthly-money-forecast/' ); }

if ( ! function_exists( 'sr_mon_order_has_report' ) ) {
	function sr_mon_order_has_report( $order ) {
		if ( ! $order || ! is_a( $order, 'WC_Order' ) ) { return false; }
		if ( ! $order->is_paid() && ! in_array( $order->get_status(), array( 'processing', 'completed' ), true ) ) { return false; }
		foreach ( $order->get_items() as $item ) {
			if ( (int) $item->get_product_id() === (int) SR_MON_PRODUCT_ID ) { return true; }
		}
		return false;
	}
	function sr_mon_portal_url( $order ) {
		return add_query_arg( array( 'mon_order' => $order->get_id(), 'mon_key' => $order->get_order_key() ), home_url( SR_MON_PORTAL_PATH ) );
	}
	function sr_mon_access( $order_id, $key ) {
		if ( ! function_exists( 'wc_get_order' ) ) { return false; }
		if ( $order_id && $key ) {
			$order = wc_get_order( absint( $order_id ) );
			if ( $order && hash_equals( (string) $order->get_order_key(), (string) $key ) && sr_mon_order_has_report( $order ) ) { return $order; }
		}
		if ( current_user_can( 'manage_options' ) ) { return true; }
		if ( is_user_logged_in() && function_exists( 'wc_customer_bought_product' ) ) {
			$user = wp_get_current_user();
			if ( wc_customer_bought_product( $user->user_email, $user->ID, SR_MON_PRODUCT_ID ) ) { return true; }
		}
		return false;
	}
	/** "Y-n" keys for this month and next month in the site's time zone, with labels. */
	function sr_mon_month_options() {
		$now = new DateTime( 'first day of this month', wp_timezone() );
		$out = array();
		for ( $i = 0; $i < 2; $i++ ) {
			$out[ $now->format( 'Y-n' ) ] = wp_date( 'F Y', $now->getTimestamp() );
			$now->modify( '+1 month' );
		}
		return $out;
	}
	function sr_mon_month_label( $ym ) {
		$p = array_map( 'intval', explode( '-', (string) $ym ) );
		if ( count( $p ) !== 2 || $p[1] < 1 || $p[1] > 12 ) { return ''; }
		return date_i18n( 'F Y', mktime( 12, 0, 0, $p[1], 1, $p[0] ) );
	}
	function sr_mon_err( $msg, $status ) {
		$r = new WP_REST_Response( array( 'status' => 'error', 'message' => $msg ), $status );
		$r->header( 'Cache-Control', 'no-store, private' );
		return $r;
	}
	/** Validate the birth details with the SR11 Birth Chart plugin and call the chart service. */
	function sr_mon_call( $in, $extra ) {
		if ( ! class_exists( 'SR11BC_Rest' ) || ! class_exists( 'SR11BC_Settings' ) ) {
			return sr_mon_err( 'The calculator is temporarily unavailable. Please try again in a few minutes.', 503 );
		}
		$v = SR11BC_Rest::validate( $in );
		if ( is_wp_error( $v ) ) { return sr_mon_err( $v->get_error_message(), 422 ); }
		unset( $v['house_system'], $v['points'], $v['asteroids'], $v['aspects'] );
		$v    = array_merge( $v, $extra );
		$s    = SR11BC_Settings::get();
		$res  = wp_remote_post( $s['service_url'] . '/v1/money-month', array(
			'timeout'     => 90,
			'redirection' => 0,
			'headers'     => array( 'X-SR11-Key' => $s['api_key'], 'Content-Type' => 'application/json', 'Accept' => 'application/json' ),
			'body'        => wp_json_encode( $v ),
		) );
		if ( is_wp_error( $res ) ) { return sr_mon_err( 'The calculator is busy. Please try again in a minute.', 502 ); }
		$code = (int) wp_remote_retrieve_response_code( $res );
		$json = json_decode( wp_remote_retrieve_body( $res ), true );
		if ( ! is_array( $json ) || $code >= 500 || 401 === $code ) { return sr_mon_err( 'The calculator is busy. Please try again in a minute.', 502 ); }
		if ( 200 !== $code ) {
			$r = new WP_REST_Response( $json, in_array( $code, array( 409, 422 ), true ) ? $code : 502 );
			$r->header( 'Cache-Control', 'no-store, private' );
			return $r;
		}
		return $json;
	}
}

/* ---------- REST routes ---------- */
add_action( 'rest_api_init', function () {
	register_rest_route( 'sr11mon/v1', '/reading', array(
		'methods'             => 'POST',
		'permission_callback' => '__return_true',
		'callback'            => function ( WP_REST_Request $req ) {
			if ( '1' !== $req->get_header( 'x_sr11_request' ) ) { return sr_mon_err( 'Invalid request.', 400 ); }
			if ( strlen( (string) $req->get_body() ) > 4096 ) { return sr_mon_err( 'Request too large.', 413 ); }
			$in     = $req->get_json_params();
			$in     = is_array( $in ) ? $in : array();
			$access = sr_mon_access( $in['order'] ?? 0, isset( $in['key'] ) ? sanitize_text_field( (string) $in['key'] ) : '' );
			if ( ! $access ) { return sr_mon_err( 'This page is for Monthly Money Forecast buyers. Please use the link in your order email.', 403 ); }
			if ( is_a( $access, 'WC_Order' ) && (int) $access->get_meta( '_sr_mon_created' ) >= 25 ) {
				return sr_mon_err( 'This order has reached its limit of forecasts. Please reach out and I will help.', 429 );
			}
			$ym     = preg_replace( '/[^0-9-]/', '', (string) ( $in['forecast'] ?? '' ) );
			$locked = is_a( $access, 'WC_Order' ) ? (string) $access->get_meta( '_sr_mon_month' ) : '';
			if ( $locked && $ym !== $locked ) {
				return sr_mon_err( 'This order is for your ' . sr_mon_month_label( $locked ) . ' forecast. Each order covers one month, so for another month please place a new order.', 422 );
			}
			if ( ! $locked && ! array_key_exists( $ym, sr_mon_month_options() ) ) {
				return sr_mon_err( 'Please choose this month or next month for your forecast.', 422 );
			}
			list( $fy, $fm ) = array_map( 'intval', explode( '-', $ym ) );
			$tz  = preg_replace( '#[^A-Za-z0-9_+/-]#', '', (string) ( $in['forecast_tz'] ?? '' ) );
			$out = sr_mon_call( $in, array( 'with_html' => true, 'forecast_year' => $fy, 'forecast_month' => $fm, 'forecast_tz' => mb_substr( $tz, 0, 64 ), 'name' => mb_substr( sanitize_text_field( (string) ( $in['name'] ?? '' ) ), 0, 60 ) ) );
			if ( $out instanceof WP_REST_Response ) { return $out; }
			if ( empty( $out['pdf_base64'] ) ) { return sr_mon_err( 'Something went wrong creating your reading. Please try again in a minute.', 502 ); }
			if ( is_a( $access, 'WC_Order' ) ) {
				$access->update_meta_data( '_sr_mon_created', (int) $access->get_meta( '_sr_mon_created' ) + 1 );
				if ( ! $locked ) { $access->update_meta_data( '_sr_mon_month', $ym ); }
				$access->save();
			}
			$r = new WP_REST_Response( array(
				'status'   => 'ok',
				'pdf'      => $out['pdf_base64'],
				'html'     => $out['html'] ?? '',
				'filename' => $out['filename'] ?? 'Monthly-Money-Forecast.pdf',
			), 200 );
			$r->header( 'Cache-Control', 'no-store, private' );
			return $r;
		},
	) );
} );

/* ---------- Shared form pieces ---------- */
if ( ! function_exists( 'sr_mon_style' ) ) {
	function sr_mon_style() {
		return '<style>
.sr-monf{--p:#4b2a7b;--p2:#6d5a8c;--l:#efe7fb;--l2:#dccdf3;--g:#c9a24d;--ink:#2e2340;color:var(--ink)}
.sr-monf .card{background:#fff;border:1px solid var(--l2);border-top:6px solid var(--p);border-radius:4px;padding:1.5rem;margin:0 0 1.6rem}
.sr-monf h2{font-family:"Cormorant Garamond",Georgia,serif;color:var(--p);margin:0 0 .5rem;font-size:1.7rem;font-weight:600}
.sr-monf .lede{margin:0 0 1.1rem}
.sr-monf .grid{display:grid;grid-template-columns:1fr 1fr;gap:0 1rem}
.sr-monf label{display:block;font-weight:600;color:var(--p);margin:0 0 1rem;font-size:.92rem}
.sr-monf label.nt{display:flex;align-items:center;gap:.5rem;font-weight:400;color:#2e2340;grid-column:1/-1;margin-top:-.4rem}.sr-monf label.nt input{width:auto;margin:0}.sr-monf input[type=time]:disabled{opacity:.5}
.sr-monf .ntnote{background:#efe7fb;border-left:3px solid var(--p);padding:.6rem .8rem;font-size:.92rem;margin:-.2rem 0 1rem}
.sr-monf select,.sr-monf input[type=text],.sr-monf input[type=date],.sr-monf input[type=time]{display:block;width:100%;box-sizing:border-box;margin-top:.35rem;padding:.7rem .8rem;border:1px solid var(--l2);border-radius:3px;font-size:1rem;color:var(--ink);background:#fff}
.sr-monf .city{position:relative;display:block}
.sr-monf .sugg{position:absolute;left:0;right:0;top:100%;z-index:20;background:#fff;border:1px solid var(--l2);border-radius:3px;max-height:260px;overflow:auto;box-shadow:0 6px 18px rgba(75,42,123,.12)}
.sr-monf .sugg button{display:block;width:100%;text-align:left;background:#fff;border:0;border-bottom:1px solid var(--l);padding:.6rem .8rem;font-size:.95rem;color:var(--ink);cursor:pointer}
.sr-monf .sugg button:hover,.sr-monf .sugg button:focus{background:var(--l)}
.sr-monf .go{display:inline-block;background:var(--p);color:#fff !important;border:0;border-radius:3px;padding:.85rem 1.5rem;font-size:1rem;cursor:pointer;text-decoration:none}
.sr-monf .go[disabled]{opacity:.6;cursor:wait}
.sr-monf .msg{margin:1rem 0 0;padding:.8rem 1rem;border-radius:3px;background:var(--l)}
.sr-monf .msg.err{background:#fdecec;color:#7a1f1f}
.sr-monf .fine{font-size:.85rem;color:var(--p2);margin-top:1rem}
.sr-monf .result{background:var(--l);border-radius:4px;padding:1.4rem;margin:0 0 1.6rem}
.sr-monf .result h3{font-family:inherit;font-weight:700;font-size:.8rem;letter-spacing:1.5px;text-transform:uppercase;color:var(--p);margin:1.2rem 0 .4rem}
.sr-monf table{width:100%;border-collapse:collapse;background:#fff;margin:.6rem 0 0}
.sr-monf td{padding:.55rem .7rem;border-bottom:1px solid var(--l2);vertical-align:top;font-size:.96rem}
.sr-monf td.k{color:var(--p);font-weight:600;width:44%;font-size:.88rem}
.sr-monf .cta{border:1px solid var(--l2);border-left:5px solid var(--g);padding:1.2rem 1.3rem;border-radius:4px;background:#fff}
.sr-monf .cta h3{font-family:"Cormorant Garamond",Georgia,serif;color:var(--p);font-size:1.45rem;margin:0 0 .4rem;letter-spacing:0;text-transform:none}
.sr-monf .dl{margin:0 0 1.4rem}
.sr-monf p,.sr-monf li{font-size:1.05rem;line-height:1.7}
@media(max-width:600px){.sr-monf .grid{grid-template-columns:1fr}.sr-monf .card{padding:1.1rem}.sr-monf .result{padding:1rem .9rem}.sr-monf .cta{padding:1rem}.sr-monf p,.sr-monf li{font-size:1rem}.sr-monf table,.sr-monf tbody,.sr-monf tr,.sr-monf td{display:block;width:auto}.sr-monf td.k{width:auto;border-bottom:0;padding-bottom:.1rem;font-size:.9rem}.sr-monf td{padding:.35rem .7rem .6rem}}
</style>';
	}
	function sr_mon_fields( $pre, $with_name_label ) {
		return '<div class="grid">'
			. '<label for="' . $pre . '-name">' . esc_html( $with_name_label ) . '<input id="' . $pre . '-name" type="text" maxlength="60" autocomplete="given-name"></label>'
			. '<label for="' . $pre . '-city">Birth city<span class="city"><input id="' . $pre . '-city" type="text" autocomplete="off" placeholder="Start typing, then choose from the list" aria-autocomplete="list"><span class="sugg" id="' . $pre . '-city-s" hidden></span></span></label>'
			. '<label for="' . $pre . '-date">Birth date<input id="' . $pre . '-date" type="date" min="1800-01-01" max="' . esc_attr( wp_date( 'Y-m-d' ) ) . '" required></label>'
			. '<label for="' . $pre . '-time">Birth time (local)<input id="' . $pre . '-time" type="time"></label>'
			. '<label class="nt" for="' . $pre . '-notime"><input id="' . $pre . '-notime" type="checkbox"> I don&#39;t know my birth time</label>'
			. '</div>'
			. '<p class="ntnote" id="' . $pre . '-ntnote" hidden>That&#39;s okay. Without a birth time I read your houses from your Sun (solar houses), and I leave out the points that need the exact minute, like your Ascendant, Midheaven and Part of Fortune. If you can find your time later, a birth certificate or hospital record usually has it.</p>';
	}
	/** City lookup + request helper shared by both pages. */
	function sr_mon_js_common() {
		return 'function srmonCity(C,$,pre,onPick){var city=$(pre+"-city"),box=$(pre+"-city-s"),timer=null;
function srmonZone(){if(window.SR11Chart){SR11Chart.attachRecordZone(city,function(){return $(pre+"-date").value;});}}
if(window.SR11Chart){srmonZone();}else{window.addEventListener("load",srmonZone);}
city.addEventListener("input",function(){city.sr11Place=null;onPick(null);clearTimeout(timer);var q=city.value.trim();if(q.length<2){box.hidden=true;return;}
timer=setTimeout(function(){fetch(C.places+"?q="+encodeURIComponent(q),{headers:{"X-SR11-Request":"1"}}).then(function(r){return r.json();}).then(function(j){
box.innerHTML="";var res=(j&&j.results)||[];if(!res.length){box.innerHTML="<button type=\"button\" disabled>No matches yet. Try the city name only.</button>";box.hidden=false;return;}
res.slice(0,8).forEach(function(p){var b=document.createElement("button");b.type="button";b.textContent=p.label;b.addEventListener("click",function(){city.sr11Place={tz:p.tz,cc:p.country_code};onPick(p);city.value=p.label;box.hidden=true;});box.appendChild(b);});box.hidden=false;}).catch(function(){box.hidden=true;});},250);});
document.addEventListener("click",function(e){if(!box.contains(e.target)&&e.target!==city)box.hidden=true;});}
function srmonNoTime($,pre){var n=$(pre+"-notime"),t=$(pre+"-time"),note=$(pre+"-ntnote");if(!n)return;var f=function(){var l=t.closest("label")||t.parentNode;t.disabled=n.checked;if(n.checked)t.value="";l.querySelectorAll("input,button").forEach(function(x){if(x!==t){x.disabled=n.checked;if(n.checked&&x.tagName==="INPUT")x.value="";}});l.style.opacity=n.checked?".45":"";if(note)note.hidden=!n.checked;};n.addEventListener("change",f);f();}
function srmonBody($,pre,place){var d=$(pre+"-date").value.split("-"),nt=$(pre+"-notime")&&$(pre+"-notime").checked,t=$(pre+"-time").value.split(":");
var b={name:$(pre+"-name").value.trim(),year:parseInt(d[0],10),month:parseInt(d[1],10),day:parseInt(d[2],10),location:{mode:"place",place_id:place.id}};
if(nt){b.time_known=false;}else{b.hour=parseInt(t[0],10);b.minute=parseInt(t[1],10);}
return window.SR11Chart?SR11Chart.withRecordOffset(b,$(pre+"-city")):b;}
function srmonCheck($,pre,place){if(!$(pre+"-date").value)return "Please enter your birth date.";if(!$(pre+"-time").value&&!($(pre+"-notime")&&$(pre+"-notime").checked))return "Please enter your birth time, or tick \"I don\u2019t know my birth time\".";if(!place)return "Please start typing your birth city and choose it from the list.";return "";}';
	}
}

/* ---------- Paid reading page ---------- */
add_shortcode( 'sr_money_forecast_reading', function () {
	$order_id = isset( $_GET['mon_order'] ) ? absint( $_GET['mon_order'] ) : 0;
	$key      = isset( $_GET['mon_key'] ) ? sanitize_text_field( wp_unslash( $_GET['mon_key'] ) ) : '';
	if ( ! sr_mon_access( $order_id, $key ) ) {
		$url   = get_permalink( SR_MON_PRODUCT_ID );
		$price = '';
		if ( function_exists( 'wc_get_product' ) && ( $p = wc_get_product( SR_MON_PRODUCT_ID ) ) ) { $price = wp_strip_all_tags( wc_price( $p->get_price() ) ); }
		return '<div style="max-width:640px;margin:1.5rem auto;border:1px solid #dccdf3;border-top:6px solid #4b2a7b;border-radius:4px;padding:1.6rem;text-align:center;background:#fff">'
			. '<p style="font-style:italic;font-size:1.3rem;margin:0 0 .6rem;color:#4b2a7b">Your Monthly Money Forecast is waiting</p>'
			. '<p style="margin:0 0 1.1rem">This page creates your personal forecast after purchase. Already bought it? Use the link in your order confirmation email, or log in to your account.</p>'
			. '<a href="' . esc_url( $url ) . '" style="display:inline-block;background:#4b2a7b;color:#fff;padding:.8rem 1.4rem;border-radius:3px;text-decoration:none">Get My Monthly Money Forecast' . ( $price ? ' · ' . esc_html( $price ) : '' ) . '</a></div>';
	}
	$acc    = sr_mon_access( $order_id, $key );
	$locked = is_a( $acc, 'WC_Order' ) ? (string) $acc->get_meta( '_sr_mon_month' ) : '';
	$opts   = $locked ? array( $locked => sr_mon_month_label( $locked ) ) : sr_mon_month_options();
	$sel    = '<label for="mon-month">Your forecast month<select id="mon-month">';
	foreach ( $opts as $k => $lab ) { $sel .= '<option value="' . esc_attr( $k ) . '">' . esc_html( $lab ) . '</option>'; }
	$sel   .= '</select></label>';
	if ( $locked ) { $sel .= '<p class="ntnote" style="grid-column:1/-1">This order is for your ' . esc_html( sr_mon_month_label( $locked ) ) . ' forecast. You can create it again here anytime, for example to correct your birth details.</p>'; }
	$cfg = wp_json_encode( array(
		'endpoint' => esc_url_raw( rest_url( 'sr11mon/v1/reading' ) ),
		'places'   => esc_url_raw( rest_url( 'sr11bc/v1/places' ) ),
		'nonce'    => wp_create_nonce( 'wp_rest' ),
		'order'    => $order_id,
		'key'      => $key,
	) );
	ob_start();
	echo sr_mon_style(); ?>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&amp;family=Source+Serif+4:ital,wght@0,400;0,600;1,400&amp;display=swap" rel="stylesheet">
<div id="sr-mon-app" class="sr-monf">
<div class="card" id="mon-card" style="max-width:680px;margin-left:auto;margin-right:auto">
<h2>Create Your Monthly Money Forecast</h2>
<p class="lede">Enter the birth details for the person this forecast is for and choose your month. It's created in seconds, shows right here on the page with a section menu, and downloads as a PDF you can keep. Each order covers one month.</p>
<form id="mon-form" novalidate>
<?php echo sr_mon_fields( 'mon', 'First name (shown on the forecast)' ); ?>
<div class="grid"><?php echo $sel; ?></div>
<button class="go" id="mon-go" type="submit">Create My Forecast</button>
<div id="mon-msg" class="msg" hidden></div>
</form>
<p class="fine">Your details are used only to create your forecast. Because this is an instant digital download, all sales are final.</p>
</div>
<div id="mon-out" hidden></div>
</div>
<script data-jetpack-boost="ignore">
(function(){
  var C = <?php echo $cfg; ?>, $ = function(id){ return document.getElementById(id); }, place = null, busy = false;
  <?php echo sr_mon_js_common(); ?>
  function msg(t, err, html){ var m=$('mon-msg'); m.hidden=!t; m.className='msg'+(err?' err':''); if(html){m.innerHTML=t;}else{m.textContent=t||'';} }
  srmonCity(C, $, 'mon', function(p){ place = p; });
  srmonNoTime($, 'mon');
  function send(extra){
    var body = srmonBody($, 'mon', place); body.order = C.order; body.key = C.key; body.forecast = $('mon-month').value;
    try { body.forecast_tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) { body.forecast_tz = ''; }
    for (var k in (extra||{})) body[k] = extra[k];
    busy = true; $('mon-go').disabled = true; msg('Reading your chart against this month's sky. This takes a few seconds....');
    fetch(C.endpoint, { method:'POST', credentials:'same-origin',
      headers:{ 'Content-Type':'application/json', 'X-SR11-Request':'1', 'X-WP-Nonce': C.nonce }, body: JSON.stringify(body) })
    .then(function(r){ return r.json().then(function(j){ return { s:r.status, j:j }; }); })
    .then(function(x){
      busy = false; $('mon-go').disabled = false; var j = x.j || {};
      if (x.s === 200 && j.pdf) {
        var bin = atob(j.pdf), bytes = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        var url = URL.createObjectURL(new Blob([bytes], { type:'application/pdf' }));
        var fn = j.filename || 'Monthly-Money-Forecast.pdf';
        var a = document.createElement('a'); a.href = url; a.download = fn; document.body.appendChild(a); a.click(); setTimeout(function(){ a.remove(); }, 4000);
        msg('Your Monthly Money Forecast is ready. It should download automatically, and it is also below. If the download didn\'t start, <a href="'+url+'" download="'+fn+'">tap here to download it</a>. A copy is on its way to your email too.', false, true);
        var out = $('mon-out');
        out.innerHTML = '<p class="dl" style="text-align:center"><a class="go" href="'+url+'" download="'+fn+'">Download My PDF</a></p>' + (j.html || '');
        out.hidden = false;
        (function(){ var nav = out.querySelector('nav.ws-nav'); if (!nav) return;
          for (var e = nav.parentElement; e && e !== document.body; e = e.parentElement) { var ov = getComputedStyle(e); if (ov.overflowX !== 'visible' || ov.overflowY !== 'visible') e.style.overflow = 'clip'; }
          function pin(){ if (window.innerWidth > 820) { nav.style.top=''; return; } var b = 0;
            document.querySelectorAll('#wpadminbar, .mobmenu, .mob-menu-header-holder, header, .site-header, [class*="sticky"], [class*="fixed"]').forEach(function(el){
              if (out.contains(el)) return; var cs = getComputedStyle(el); if ((cs.position !== 'fixed' && cs.position !== 'sticky') || cs.display === 'none' || cs.visibility === 'hidden') return;
              var r = el.getBoundingClientRect(); if (r.height > 0 && r.top < 130 && r.bottom > b && r.bottom < 220 && r.width > window.innerWidth * 0.6) b = r.bottom; });
            nav.style.top = Math.round(b) + 'px'; }
          var ws = out.querySelector('.sr-ws'), host = ws && ws.closest('.post-content, .entry-content');
          function widen(){ if (!ws || !host) return; if (window.innerWidth <= 820) { ws.style.marginLeft = ws.style.marginRight = ''; return; }
            var cs = getComputedStyle(host), m = Math.max(0, Math.min(parseFloat(cs.paddingLeft), parseFloat(cs.paddingRight), 80) - 8);
            ws.style.marginLeft = ws.style.marginRight = (-m) + 'px'; }
          widen(); window.addEventListener('resize', widen);
          pin(); var t; window.addEventListener('scroll', function(){ clearTimeout(t); t = setTimeout(pin, 250); }, {passive:true}); window.addEventListener('resize', pin);
        })();
        setTimeout(function(){ out.scrollIntoView({behavior:'smooth', block:'start'}); }, 300);
        return;
      }
      if (j.status === 'ambiguous') {
        msg('That birth time happened twice on that date because the clocks went back. Choose which one: <button type="button" class="go" id="mon-f0" style="padding:.4rem .8rem;margin:.4rem .3rem 0 0">The first one</button><button type="button" class="go" id="mon-f1" style="padding:.4rem .8rem;margin-top:.4rem">The second one</button>', false, true);
        $('mon-f0').onclick = function(){ send({ fold:0 }); }; $('mon-f1').onclick = function(){ send({ fold:1 }); };
        return;
      }
      if (j.status === 'needs_confirmation') { send({ accept_lmt: true }); return; }
      msg(j.message || 'Something went wrong creating your reading. Please try again in a minute.', true);
    })
    .catch(function(){ busy = false; $('mon-go').disabled = false; msg('We could not reach the reading service. Please check your connection and try again.', true); });
  }
  $('mon-form').addEventListener('submit', function(e){
    e.preventDefault(); if (busy) return;
    var bad = srmonCheck($, 'mon', place); if (bad) { msg(bad, true); return; }
    send({});
  });
})();
</script>
<?php
	return ob_get_clean();
} );

/* ---------- Order confirmation page + emails ---------- */
add_action( 'woocommerce_thankyou', function ( $order_id ) {
	$order = wc_get_order( $order_id );
	if ( ! sr_mon_order_has_report( $order ) ) { return; }
	echo '<div style="border:1px solid #dccdf3;border-top:6px solid #4b2a7b;border-radius:4px;padding:1.4rem;margin:0 0 1.5rem;text-align:center;background:#fff">'
		. '<p style="font-style:italic;font-size:1.3rem;margin:0 0 .5rem;color:#4b2a7b">Your Monthly Money Forecast is ready to create</p>'
		. '<p style="margin:0 0 1rem">Click below, enter your birth date, time and city, choose your month, and your forecast is created in seconds. I have also emailed you this link so you can come back anytime.</p>'
		. '<a href="' . esc_url( sr_mon_portal_url( $order ) ) . '" style="display:inline-block;background:#4b2a7b;color:#fff;padding:.8rem 1.4rem;border-radius:3px;text-decoration:none">Create My Forecast</a></div>';
}, 5 );

add_action( 'woocommerce_email_after_order_table', function ( $order, $sent_to_admin, $plain_text, $email = null ) {
	if ( $sent_to_admin || ! sr_mon_order_has_report( $order ) ) { return; }
	$url = sr_mon_portal_url( $order );
	if ( $plain_text ) {
		echo PHP_EOL . 'Create your Monthly Money Forecast: ' . esc_url_raw( $url ) . PHP_EOL;
		return;
	}
	echo '<p style="margin:16px 0"><strong>Your Monthly Money Forecast</strong><br>Create your forecast anytime here: <a href="' . esc_url( $url ) . '">Create My Forecast</a></p>';
}, 10, 4 );
