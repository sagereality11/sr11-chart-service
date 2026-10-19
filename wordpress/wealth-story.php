/**
 * Sage Reality 11: Your Birth Chart's Wealth Story.
 * - [sr_wealth_story_calculator]: free calculator (birth details in, Wealth Story snapshot out).
 * - [sr_wealth_story_reading]: the $66.66 reading page, unlocked for paid orders (private link with order key),
 *   logged-in buyers and site admins. Shows the reading on the page with a section menu and downloads the PDF.
 * - REST routes sr11ws/v1/snapshot and sr11ws/v1/reading forward to the chart service (/v1/wealth-story)
 *   using the SR11 Birth Chart plugin's saved service URL and key.
 * - Adds the "Create My Reading" link to the order confirmation page and the customer's order emails.
 * The "Instant reports" snippets handle the emailed copies, saved birth details and auto-complete (prefix ws).
 */
if ( ! defined( 'SR_WS_PRODUCT_ID' ) ) { define( 'SR_WS_PRODUCT_ID', 8589 ); }
if ( ! defined( 'SR_WS_PORTAL_PATH' ) ) { define( 'SR_WS_PORTAL_PATH', '/your-wealth-story-reading/' ); }

if ( ! function_exists( 'sr_ws_order_has_report' ) ) {
	function sr_ws_order_has_report( $order ) {
		if ( ! $order || ! is_a( $order, 'WC_Order' ) ) { return false; }
		if ( ! $order->is_paid() && ! in_array( $order->get_status(), array( 'processing', 'completed' ), true ) ) { return false; }
		foreach ( $order->get_items() as $item ) {
			if ( (int) $item->get_product_id() === (int) SR_WS_PRODUCT_ID ) { return true; }
		}
		return false;
	}
	function sr_ws_portal_url( $order ) {
		return add_query_arg( array( 'ws_order' => $order->get_id(), 'ws_key' => $order->get_order_key() ), home_url( SR_WS_PORTAL_PATH ) );
	}
	function sr_ws_access( $order_id, $key ) {
		if ( ! function_exists( 'wc_get_order' ) ) { return false; }
		if ( $order_id && $key ) {
			$order = wc_get_order( absint( $order_id ) );
			if ( $order && hash_equals( (string) $order->get_order_key(), (string) $key ) && sr_ws_order_has_report( $order ) ) { return $order; }
		}
		if ( current_user_can( 'manage_options' ) ) { return true; }
		if ( is_user_logged_in() && function_exists( 'wc_customer_bought_product' ) ) {
			$user = wp_get_current_user();
			if ( wc_customer_bought_product( $user->user_email, $user->ID, SR_WS_PRODUCT_ID ) ) { return true; }
		}
		return false;
	}
	function sr_ws_err( $msg, $status ) {
		$r = new WP_REST_Response( array( 'status' => 'error', 'message' => $msg ), $status );
		$r->header( 'Cache-Control', 'no-store, private' );
		return $r;
	}
	/** Validate the birth details with the SR11 Birth Chart plugin and call the chart service. */
	function sr_ws_call( $in, $extra ) {
		if ( ! class_exists( 'SR11BC_Rest' ) || ! class_exists( 'SR11BC_Settings' ) ) {
			return sr_ws_err( 'The calculator is temporarily unavailable. Please try again in a few minutes.', 503 );
		}
		if ( isset( $in['time_known'] ) && false === $in['time_known'] ) {
			return sr_ws_err( 'Your Wealth Story needs a birth time, because it reads your houses, your Part of Fortune and your Midheaven. A birth certificate or hospital record usually has it.', 422 );
		}
		$v = SR11BC_Rest::validate( $in );
		if ( is_wp_error( $v ) ) { return sr_ws_err( $v->get_error_message(), 422 ); }
		unset( $v['house_system'], $v['points'], $v['asteroids'], $v['aspects'] );
		$v    = array_merge( $v, $extra );
		$s    = SR11BC_Settings::get();
		$res  = wp_remote_post( $s['service_url'] . '/v1/wealth-story', array(
			'timeout'     => 90,
			'redirection' => 0,
			'headers'     => array( 'X-SR11-Key' => $s['api_key'], 'Content-Type' => 'application/json', 'Accept' => 'application/json' ),
			'body'        => wp_json_encode( $v ),
		) );
		if ( is_wp_error( $res ) ) { return sr_ws_err( 'The calculator is busy. Please try again in a minute.', 502 ); }
		$code = (int) wp_remote_retrieve_response_code( $res );
		$json = json_decode( wp_remote_retrieve_body( $res ), true );
		if ( ! is_array( $json ) || $code >= 500 || 401 === $code ) { return sr_ws_err( 'The calculator is busy. Please try again in a minute.', 502 ); }
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
	register_rest_route( 'sr11ws/v1', '/snapshot', array(
		'methods'             => 'POST',
		'permission_callback' => '__return_true',
		'callback'            => function ( WP_REST_Request $req ) {
			if ( '1' !== $req->get_header( 'x_sr11_request' ) ) { return sr_ws_err( 'Invalid request.', 400 ); }
			if ( strlen( (string) $req->get_body() ) > 4096 ) { return sr_ws_err( 'Request too large.', 413 ); }
			$ip   = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : 'x';
			$tkey = 'sr_ws_rl_' . md5( $ip );
			$n    = (int) get_transient( $tkey );
			if ( $n >= 30 && ! current_user_can( 'manage_options' ) ) { return sr_ws_err( 'You have run a lot of charts this hour. Please try again a little later.', 429 ); }
			set_transient( $tkey, $n + 1, HOUR_IN_SECONDS );
			$in = $req->get_json_params();
			$in = is_array( $in ) ? $in : array();
			$out = sr_ws_call( $in, array( 'mode' => 'snapshot', 'name' => mb_substr( sanitize_text_field( (string) ( $in['name'] ?? '' ) ), 0, 60 ) ) );
			if ( $out instanceof WP_REST_Response ) { return $out; }
			$r = new WP_REST_Response( array( 'status' => 'ok', 'snapshot' => $out['snapshot'] ?? array() ), 200 );
			$r->header( 'Cache-Control', 'no-store, private' );
			return $r;
		},
	) );
	register_rest_route( 'sr11ws/v1', '/reading', array(
		'methods'             => 'POST',
		'permission_callback' => '__return_true',
		'callback'            => function ( WP_REST_Request $req ) {
			if ( '1' !== $req->get_header( 'x_sr11_request' ) ) { return sr_ws_err( 'Invalid request.', 400 ); }
			if ( strlen( (string) $req->get_body() ) > 4096 ) { return sr_ws_err( 'Request too large.', 413 ); }
			$in     = $req->get_json_params();
			$in     = is_array( $in ) ? $in : array();
			$access = sr_ws_access( $in['order'] ?? 0, isset( $in['key'] ) ? sanitize_text_field( (string) $in['key'] ) : '' );
			if ( ! $access ) { return sr_ws_err( 'This page is for Wealth Story buyers. Please use the link in your order email.', 403 ); }
			if ( is_a( $access, 'WC_Order' ) && (int) $access->get_meta( '_sr_ws_created' ) >= 25 ) {
				return sr_ws_err( 'This order has reached its limit of readings. Please reach out and I will help.', 429 );
			}
			$out = sr_ws_call( $in, array( 'mode' => 'pdf', 'with_html' => true, 'name' => mb_substr( sanitize_text_field( (string) ( $in['name'] ?? '' ) ), 0, 60 ) ) );
			if ( $out instanceof WP_REST_Response ) { return $out; }
			if ( empty( $out['pdf_base64'] ) ) { return sr_ws_err( 'Something went wrong creating your reading. Please try again in a minute.', 502 ); }
			if ( is_a( $access, 'WC_Order' ) ) {
				$access->update_meta_data( '_sr_ws_created', (int) $access->get_meta( '_sr_ws_created' ) + 1 );
				$access->save();
			}
			$r = new WP_REST_Response( array(
				'status'   => 'ok',
				'pdf'      => $out['pdf_base64'],
				'html'     => $out['html'] ?? '',
				'filename' => $out['filename'] ?? 'Wealth-Story.pdf',
			), 200 );
			$r->header( 'Cache-Control', 'no-store, private' );
			return $r;
		},
	) );
} );

/* ---------- Shared form pieces ---------- */
if ( ! function_exists( 'sr_ws_style' ) ) {
	function sr_ws_style() {
		return '<style>
.sr-wsf{--p:#4b2a7b;--p2:#6d5a8c;--l:#efe7fb;--l2:#dccdf3;--g:#c9a24d;--ink:#2e2340;color:var(--ink)}
.sr-wsf .card{background:#fff;border:1px solid var(--l2);border-top:6px solid var(--p);border-radius:4px;padding:1.5rem;margin:0 0 1.6rem}
.sr-wsf h2{font-family:"Cormorant Garamond",Georgia,serif;color:var(--p);margin:0 0 .5rem;font-size:1.7rem;font-weight:600}
.sr-wsf .lede{margin:0 0 1.1rem}
.sr-wsf .grid{display:grid;grid-template-columns:1fr 1fr;gap:0 1rem}
.sr-wsf label{display:block;font-weight:600;color:var(--p);margin:0 0 1rem;font-size:.92rem}
.sr-wsf input[type=text],.sr-wsf input[type=date],.sr-wsf input[type=time]{display:block;width:100%;box-sizing:border-box;margin-top:.35rem;padding:.7rem .8rem;border:1px solid var(--l2);border-radius:3px;font-size:1rem;color:var(--ink);background:#fff}
.sr-wsf .city{position:relative;display:block}
.sr-wsf .sugg{position:absolute;left:0;right:0;top:100%;z-index:20;background:#fff;border:1px solid var(--l2);border-radius:3px;max-height:260px;overflow:auto;box-shadow:0 6px 18px rgba(75,42,123,.12)}
.sr-wsf .sugg button{display:block;width:100%;text-align:left;background:#fff;border:0;border-bottom:1px solid var(--l);padding:.6rem .8rem;font-size:.95rem;color:var(--ink);cursor:pointer}
.sr-wsf .sugg button:hover,.sr-wsf .sugg button:focus{background:var(--l)}
.sr-wsf .go{display:inline-block;background:var(--p);color:#fff !important;border:0;border-radius:3px;padding:.85rem 1.5rem;font-size:1rem;cursor:pointer;text-decoration:none}
.sr-wsf .go[disabled]{opacity:.6;cursor:wait}
.sr-wsf .msg{margin:1rem 0 0;padding:.8rem 1rem;border-radius:3px;background:var(--l)}
.sr-wsf .msg.err{background:#fdecec;color:#7a1f1f}
.sr-wsf .fine{font-size:.85rem;color:var(--p2);margin-top:1rem}
.sr-wsf .result{background:var(--l);border-radius:4px;padding:1.4rem;margin:0 0 1.6rem}
.sr-wsf .result h3{font-family:inherit;font-weight:700;font-size:.8rem;letter-spacing:1.5px;text-transform:uppercase;color:var(--p);margin:1.2rem 0 .4rem}
.sr-wsf table{width:100%;border-collapse:collapse;background:#fff;margin:.6rem 0 0}
.sr-wsf td{padding:.55rem .7rem;border-bottom:1px solid var(--l2);vertical-align:top;font-size:.96rem}
.sr-wsf td.k{color:var(--p);font-weight:600;width:44%;font-size:.88rem}
.sr-wsf .cta{border:1px solid var(--l2);border-left:5px solid var(--g);padding:1.2rem 1.3rem;border-radius:4px;background:#fff}
.sr-wsf .cta h3{font-family:"Cormorant Garamond",Georgia,serif;color:var(--p);font-size:1.45rem;margin:0 0 .4rem;letter-spacing:0;text-transform:none}
.sr-wsf .dl{margin:0 0 1.4rem}
.sr-wsf p,.sr-wsf li{font-size:1.05rem;line-height:1.7}
@media(max-width:600px){.sr-wsf .grid{grid-template-columns:1fr}.sr-wsf .card{padding:1.1rem}.sr-wsf .result{padding:1rem .9rem}.sr-wsf .cta{padding:1rem}.sr-wsf p,.sr-wsf li{font-size:1rem}.sr-wsf table,.sr-wsf tbody,.sr-wsf tr,.sr-wsf td{display:block;width:auto}.sr-wsf td.k{width:auto;border-bottom:0;padding-bottom:.1rem;font-size:.9rem}.sr-wsf td{padding:.35rem .7rem .6rem}}
</style>';
	}
	function sr_ws_fields( $pre, $with_name_label ) {
		return '<div class="grid">'
			. '<label for="' . $pre . '-name">' . esc_html( $with_name_label ) . '<input id="' . $pre . '-name" type="text" maxlength="60" autocomplete="given-name"></label>'
			. '<label for="' . $pre . '-city">Birth city<span class="city"><input id="' . $pre . '-city" type="text" autocomplete="off" placeholder="Start typing, then choose from the list" aria-autocomplete="list"><span class="sugg" id="' . $pre . '-city-s" hidden></span></span></label>'
			. '<label for="' . $pre . '-date">Birth date<input id="' . $pre . '-date" type="date" min="1800-01-01" max="2026-12-31" required></label>'
			. '<label for="' . $pre . '-time">Birth time (local)<input id="' . $pre . '-time" type="time" required></label>'
			. '</div>';
	}
	/** City lookup + request helper shared by both pages. */
	function sr_ws_js_common() {
		return 'function srwsCity(C,$,pre,onPick){var city=$(pre+"-city"),box=$(pre+"-city-s"),timer=null;
city.addEventListener("input",function(){onPick(null);clearTimeout(timer);var q=city.value.trim();if(q.length<2){box.hidden=true;return;}
timer=setTimeout(function(){fetch(C.places+"?q="+encodeURIComponent(q),{headers:{"X-SR11-Request":"1"}}).then(function(r){return r.json();}).then(function(j){
box.innerHTML="";var res=(j&&j.results)||[];if(!res.length){box.innerHTML="<button type=\"button\" disabled>No matches yet. Try the city name only.</button>";box.hidden=false;return;}
res.slice(0,8).forEach(function(p){var b=document.createElement("button");b.type="button";b.textContent=p.label;b.addEventListener("click",function(){onPick(p);city.value=p.label;box.hidden=true;});box.appendChild(b);});box.hidden=false;}).catch(function(){box.hidden=true;});},250);});
document.addEventListener("click",function(e){if(!box.contains(e.target)&&e.target!==city)box.hidden=true;});}
function srwsBody($,pre,place){var d=$(pre+"-date").value.split("-"),t=$(pre+"-time").value.split(":");
return {name:$(pre+"-name").value.trim(),year:parseInt(d[0],10),month:parseInt(d[1],10),day:parseInt(d[2],10),hour:parseInt(t[0],10),minute:parseInt(t[1],10),location:{mode:"place",place_id:place.id}};}
function srwsCheck($,pre,place){if(!$(pre+"-date").value)return "Please enter your birth date.";if(!$(pre+"-time").value)return "Please enter your birth time. Your Wealth Story reads your houses, so it needs one.";if(!place)return "Please start typing your birth city and choose it from the list.";return "";}';
	}
}

/* ---------- Free calculator ---------- */
add_shortcode( 'sr_wealth_story_calculator', function () {
	$cfg = wp_json_encode( array(
		'endpoint' => esc_url_raw( rest_url( 'sr11ws/v1/snapshot' ) ),
		'places'   => esc_url_raw( rest_url( 'sr11bc/v1/places' ) ),
		'product'  => esc_url_raw( get_permalink( SR_WS_PRODUCT_ID ) ),
	) );
	ob_start();
	echo sr_ws_style(); ?>
<div id="sr-wsc-app" class="sr-wsf">
<div class="card">
<h2>Your Birth Details</h2>
<p class="lede">Your birth time matters here. Your Wealth Story reads your houses, your Part of Fortune and your Midheaven, and all three move with the clock.</p>
<form id="wsc-form" novalidate>
<?php echo sr_ws_fields( 'wsc', 'First name' ); ?>
<button class="go" id="wsc-go" type="submit">Show My Wealth Story</button>
<div id="wsc-msg" class="msg" hidden></div>
</form>
</div>
<div id="wsc-out" hidden></div>
</div>
<script data-jetpack-boost="ignore">
(function(){
  var C = <?php echo $cfg; ?>, $ = function(id){ return document.getElementById(id); }, place = null, busy = false;
  <?php echo sr_ws_js_common(); ?>
  function esc(s){ return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c];}); }
  function msg(t, err){ var m=$('wsc-msg'); m.hidden=!t; m.className='msg'+(err?' err':''); m.textContent=t||''; }
  srwsCity(C, $, 'wsc', function(p){ place = p; });
  function show(s, name){
    var rows = (s.rows||[]).map(function(r){ return '<tr><td class="k">'+esc(r[0])+'</td><td>'+esc(r[1])+'</td></tr>'; }).join('');
    var th = (s.thresholds||[]).map(function(t){ return '<li>'+esc(t)+'</li>'; }).join('');
    var ct = (s.contents||[]).map(function(t){ return '<li>'+esc(t)+'</li>'; }).join('');
    var out = $('wsc-out');
    out.innerHTML = '<div class="result"><h2>'+(name ? esc(name)+', Your' : 'Your')+' Wealth Story at a Glance</h2><p>'+esc(s.theme||'')+'</p>'
      + '<table>'+rows+'</table>'
      + (s.watch ? '<h3>One Thing to Watch</h3><p style="margin:0">'+esc(s.watch)+'</p>' : '')
      + (th ? '<h3>Thresholds in Your Next Twelve Months</h3><ul>'+th+'</ul>' : '<h3>Your Next Twelve Months</h3><p style="margin:0">A quieter year for your money points. Quiet years are building years.</p>')
      + '</div><div class="cta"><h3>Your full Wealth Story tells the whole story.</h3>'
      + '<p>Your <a href="'+C.product+'"><strong>Wealth Story Reading</strong></a> ($66.66, instant PDF) walks through every part of your money picture in your own personal letter, with a clickable contents page so you can jump straight to the section you need:</p>'
      + '<ul>'+ct+'</ul><p><a class="go" href="'+C.product+'">Get My Wealth Story Reading →</a></p></div>';
    out.hidden = false;
    out.scrollIntoView({behavior:'smooth', block:'start'});
  }
  $('wsc-form').addEventListener('submit', function(e){
    e.preventDefault(); if (busy) return;
    var bad = srwsCheck($, 'wsc', place); if (bad) { msg(bad, true); return; }
    send({});
  });
  function send(extra){
    var body = srwsBody($, 'wsc', place); for (var k in extra) body[k] = extra[k];
    busy = true; $('wsc-go').disabled = true; msg('Reading your chart....');
    fetch(C.endpoint, { method:'POST', headers:{ 'Content-Type':'application/json', 'X-SR11-Request':'1' }, body: JSON.stringify(body) })
      .then(function(r){ return r.json().then(function(j){ return { s:r.status, j:j }; }); })
      .then(function(x){
        busy = false; $('wsc-go').disabled = false; var j = x.j || {};
        if (x.s === 200 && j.snapshot) { msg(''); show(j.snapshot, body.name); return; }
        if (j.status === 'ambiguous') {
          var m=$('wsc-msg'); m.hidden=false; m.className='msg';
          m.innerHTML = 'That birth time happened twice on that date because the clocks went back. Choose which one: <button type="button" class="go" id="wsc-f0" style="padding:.4rem .8rem;margin:.4rem .3rem 0 0">The first one</button><button type="button" class="go" id="wsc-f1" style="padding:.4rem .8rem;margin-top:.4rem">The second one</button>';
          $('wsc-f0').onclick=function(){ send({fold:0}); }; $('wsc-f1').onclick=function(){ send({fold:1}); }; return;
        }
        if (j.status === 'needs_confirmation') { send({ accept_lmt: true }); return; }
        msg(j.message || 'Something went wrong. Please try again in a minute.', true);
      })
      .catch(function(){ busy = false; $('wsc-go').disabled = false; msg('We could not reach the calculator. Please check your connection and try again.', true); });
  }
})();
</script>
<?php
	return ob_get_clean();
} );

/* ---------- Paid reading page ---------- */
add_shortcode( 'sr_wealth_story_reading', function () {
	$order_id = isset( $_GET['ws_order'] ) ? absint( $_GET['ws_order'] ) : 0;
	$key      = isset( $_GET['ws_key'] ) ? sanitize_text_field( wp_unslash( $_GET['ws_key'] ) ) : '';
	if ( ! sr_ws_access( $order_id, $key ) ) {
		$url   = get_permalink( SR_WS_PRODUCT_ID );
		$price = '';
		if ( function_exists( 'wc_get_product' ) && ( $p = wc_get_product( SR_WS_PRODUCT_ID ) ) ) { $price = wp_strip_all_tags( wc_price( $p->get_price() ) ); }
		return '<div style="max-width:640px;margin:1.5rem auto;border:1px solid #dccdf3;border-top:6px solid #4b2a7b;border-radius:4px;padding:1.6rem;text-align:center;background:#fff">'
			. '<p style="font-style:italic;font-size:1.3rem;margin:0 0 .6rem;color:#4b2a7b">Your Wealth Story is waiting</p>'
			. '<p style="margin:0 0 1.1rem">This page creates your personal reading after purchase. Already bought it? Use the link in your order confirmation email, or log in to your account.</p>'
			. '<a href="' . esc_url( $url ) . '" style="display:inline-block;background:#4b2a7b;color:#fff;padding:.8rem 1.4rem;border-radius:3px;text-decoration:none">Get My Wealth Story Reading' . ( $price ? ' · ' . esc_html( $price ) : '' ) . '</a></div>';
	}
	$cfg = wp_json_encode( array(
		'endpoint' => esc_url_raw( rest_url( 'sr11ws/v1/reading' ) ),
		'places'   => esc_url_raw( rest_url( 'sr11bc/v1/places' ) ),
		'nonce'    => wp_create_nonce( 'wp_rest' ),
		'order'    => $order_id,
		'key'      => $key,
	) );
	ob_start();
	echo sr_ws_style(); ?>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&amp;family=Source+Serif+4:ital,wght@0,400;0,600;1,400&amp;display=swap" rel="stylesheet">
<div id="sr-ws-app" class="sr-wsf">
<div class="card" id="ws-card" style="max-width:680px;margin-left:auto;margin-right:auto">
<h2>Create Your Wealth Story</h2>
<p class="lede">Enter the birth details for the person this reading is for. It's created in seconds, shows right here on the page with a section menu, and downloads as a PDF you can keep.</p>
<form id="ws-form" novalidate>
<?php echo sr_ws_fields( 'ws', 'First name (shown on the reading)' ); ?>
<input type="checkbox" id="ws-notime" hidden>
<button class="go" id="ws-go" type="submit">Create My Reading</button>
<div id="ws-msg" class="msg" hidden></div>
</form>
<p class="fine">Your details are used only to create your reading. Because this is an instant digital download, all sales are final.</p>
</div>
<div id="ws-out" hidden></div>
</div>
<script data-jetpack-boost="ignore">
(function(){
  var C = <?php echo $cfg; ?>, $ = function(id){ return document.getElementById(id); }, place = null, busy = false;
  <?php echo sr_ws_js_common(); ?>
  function msg(t, err, html){ var m=$('ws-msg'); m.hidden=!t; m.className='msg'+(err?' err':''); if(html){m.innerHTML=t;}else{m.textContent=t||'';} }
  srwsCity(C, $, 'ws', function(p){ place = p; });
  function send(extra){
    var body = srwsBody($, 'ws', place); body.order = C.order; body.key = C.key;
    for (var k in (extra||{})) body[k] = extra[k];
    busy = true; $('ws-go').disabled = true; msg('Reading your chart and writing your Wealth Story. This takes a few seconds....');
    fetch(C.endpoint, { method:'POST', credentials:'same-origin',
      headers:{ 'Content-Type':'application/json', 'X-SR11-Request':'1', 'X-WP-Nonce': C.nonce }, body: JSON.stringify(body) })
    .then(function(r){ return r.json().then(function(j){ return { s:r.status, j:j }; }); })
    .then(function(x){
      busy = false; $('ws-go').disabled = false; var j = x.j || {};
      if (x.s === 200 && j.pdf) {
        var bin = atob(j.pdf), bytes = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        var url = URL.createObjectURL(new Blob([bytes], { type:'application/pdf' }));
        var fn = j.filename || 'Wealth-Story.pdf';
        var a = document.createElement('a'); a.href = url; a.download = fn; document.body.appendChild(a); a.click(); setTimeout(function(){ a.remove(); }, 4000);
        msg('Your Wealth Story is ready. It should download automatically, and it is also below. If the download didn\'t start, <a href="'+url+'" download="'+fn+'">tap here to download it</a>. A copy is on its way to your email too.', false, true);
        var out = $('ws-out');
        out.innerHTML = '<p class="dl" style="text-align:center"><a class="go" href="'+url+'" download="'+fn+'">Download My PDF</a></p>' + (j.html || '');
        out.hidden = false;
        (function(){ var nav = out.querySelector('nav.ws-nav'); if (!nav) return;
          function pin(){ if (window.innerWidth > 820) { nav.style.top=''; return; } var b = 0;
            document.querySelectorAll('header, #wpadminbar, .site-header, [class*="sticky"], [class*="fixed"]').forEach(function(el){ if (out.contains(el)) return; var cs = getComputedStyle(el);
              if ((cs.position==='fixed'||cs.position==='sticky') && cs.display!=='none') { var r = el.getBoundingClientRect(); if (r.top <= 1 && r.bottom > b && r.bottom < 200) b = r.bottom; } });
            nav.style.top = b + 'px'; }
          pin(); var t; window.addEventListener('scroll', function(){ clearTimeout(t); t = setTimeout(pin, 250); }, {passive:true}); window.addEventListener('resize', pin);
        })();
        setTimeout(function(){ out.scrollIntoView({behavior:'smooth', block:'start'}); }, 300);
        return;
      }
      if (j.status === 'ambiguous') {
        msg('That birth time happened twice on that date because the clocks went back. Choose which one: <button type="button" class="go" id="ws-f0" style="padding:.4rem .8rem;margin:.4rem .3rem 0 0">The first one</button><button type="button" class="go" id="ws-f1" style="padding:.4rem .8rem;margin-top:.4rem">The second one</button>', false, true);
        $('ws-f0').onclick = function(){ send({ fold:0 }); }; $('ws-f1').onclick = function(){ send({ fold:1 }); };
        return;
      }
      if (j.status === 'needs_confirmation') { send({ accept_lmt: true }); return; }
      msg(j.message || 'Something went wrong creating your reading. Please try again in a minute.', true);
    })
    .catch(function(){ busy = false; $('ws-go').disabled = false; msg('We could not reach the reading service. Please check your connection and try again.', true); });
  }
  $('ws-form').addEventListener('submit', function(e){
    e.preventDefault(); if (busy) return;
    var bad = srwsCheck($, 'ws', place); if (bad) { msg(bad, true); return; }
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
	if ( ! sr_ws_order_has_report( $order ) ) { return; }
	echo '<div style="border:1px solid #dccdf3;border-top:6px solid #4b2a7b;border-radius:4px;padding:1.4rem;margin:0 0 1.5rem;text-align:center;background:#fff">'
		. '<p style="font-style:italic;font-size:1.3rem;margin:0 0 .5rem;color:#4b2a7b">Your Wealth Story is ready to create</p>'
		. '<p style="margin:0 0 1rem">Click below, enter your birth date, time and city, and your reading is created in seconds. I have also emailed you this link so you can come back anytime.</p>'
		. '<a href="' . esc_url( sr_ws_portal_url( $order ) ) . '" style="display:inline-block;background:#4b2a7b;color:#fff;padding:.8rem 1.4rem;border-radius:3px;text-decoration:none">Create My Reading</a></div>';
}, 5 );

add_action( 'woocommerce_email_after_order_table', function ( $order, $sent_to_admin, $plain_text, $email = null ) {
	if ( $sent_to_admin || ! sr_ws_order_has_report( $order ) ) { return; }
	$url = sr_ws_portal_url( $order );
	if ( $plain_text ) {
		echo PHP_EOL . 'Create your Wealth Story Reading: ' . esc_url_raw( $url ) . PHP_EOL;
		return;
	}
	echo '<p style="margin:16px 0"><strong>Your Wealth Story Reading</strong><br>Create your personal reading anytime here: <a href="' . esc_url( $url ) . '">Create My Reading</a></p>';
}, 10, 4 );
