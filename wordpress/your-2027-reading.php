/**
 * Sage Reality 11: Your 2027 Reading (paid, auto-generated PDF).
 * - Unlocks the reading page for paid orders (private link with order key), logged-in buyers and site admins.
 * - Adds the "Create My Reading" link to the order confirmation page and the customer's order emails.
 * - Shortcode [sr_your_2027_reading] shows the birth-data form (city lookup from the SR11 Birth Chart plugin).
 * - REST route sr11y27/v1/reading forwards the details to the chart service, which returns the finished PDF.
 * The "Instant reports" snippets handle the emailed copies, saved birth details and auto-complete (prefix y27).
 */
if ( ! defined( 'SR_Y27_PRODUCT_ID' ) ) { define( 'SR_Y27_PRODUCT_ID', 7847 ); }
if ( ! defined( 'SR_Y27_PORTAL_PATH' ) ) { define( 'SR_Y27_PORTAL_PATH', '/your-2027-reading/' ); }

if ( ! function_exists( 'sr_y27_order_has_report' ) ) {
	function sr_y27_order_has_report( $order ) {
		if ( ! $order || ! is_a( $order, 'WC_Order' ) ) { return false; }
		if ( ! $order->is_paid() && ! in_array( $order->get_status(), array( 'processing', 'completed' ), true ) ) { return false; }
		foreach ( $order->get_items() as $item ) {
			if ( (int) $item->get_product_id() === (int) SR_Y27_PRODUCT_ID ) { return true; }
		}
		return false;
	}
	function sr_y27_portal_url( $order ) {
		return add_query_arg( array( 'y27_order' => $order->get_id(), 'y27_key' => $order->get_order_key() ), home_url( SR_Y27_PORTAL_PATH ) );
	}
	/** Returns the order this viewer may use, true for admins / logged-in buyers, or false. */
	function sr_y27_access( $order_id, $key ) {
		if ( ! function_exists( 'wc_get_order' ) ) { return false; }
		if ( $order_id && $key ) {
			$order = wc_get_order( absint( $order_id ) );
			if ( $order && hash_equals( (string) $order->get_order_key(), (string) $key ) && sr_y27_order_has_report( $order ) ) { return $order; }
		}
		if ( current_user_can( 'manage_options' ) ) { return true; }
		if ( is_user_logged_in() && function_exists( 'wc_customer_bought_product' ) ) {
			$user = wp_get_current_user();
			if ( wc_customer_bought_product( $user->user_email, $user->ID, SR_Y27_PRODUCT_ID ) ) { return true; }
		}
		return false;
	}
}

/* ---------- REST: create the reading ---------- */
add_action( 'rest_api_init', function () {
	register_rest_route( 'sr11y27/v1', '/reading', array(
		'methods'             => 'POST',
		'permission_callback' => '__return_true',
		'callback'            => function ( WP_REST_Request $req ) {
			$err = function ( $msg, $status ) {
				$r = new WP_REST_Response( array( 'status' => 'error', 'message' => $msg ), $status );
				$r->header( 'Cache-Control', 'no-store, private' );
				return $r;
			};
			if ( '1' !== $req->get_header( 'x_sr11_request' ) ) { return $err( 'Invalid request.', 400 ); }
			if ( strlen( (string) $req->get_body() ) > 4096 ) { return $err( 'Request too large.', 413 ); }
			$in     = $req->get_json_params();
			$in     = is_array( $in ) ? $in : array();
			$access = sr_y27_access( $in['order'] ?? 0, isset( $in['key'] ) ? sanitize_text_field( (string) $in['key'] ) : '' );
			if ( ! $access ) { return $err( 'This page is for Your 2027 buyers. Please use the link in your order email.', 403 ); }
			if ( is_a( $access, 'WC_Order' ) ) {
				$n = (int) $access->get_meta( '_sr_y27_created' );
				if ( $n >= 25 ) { return $err( 'This order has reached its limit of readings. Please reach out and I will help.', 429 ); }
			}
			if ( ! class_exists( 'SR11BC_Rest' ) || ! class_exists( 'SR11BC_Settings' ) ) {
				return $err( 'The reading service is temporarily unavailable. Please try again in a few minutes.', 503 );
			}
			$v = SR11BC_Rest::validate( $in );
			if ( is_wp_error( $v ) ) { return $err( $v->get_error_message(), 422 ); }
			unset( $v['house_system'], $v['points'], $v['asteroids'], $v['aspects'] );
			$v['name']   = mb_substr( sanitize_text_field( (string) ( $in['name'] ?? '' ) ), 0, 60 );
			$v['format'] = 'pdf';
			$s   = SR11BC_Settings::get();
			$res = wp_remote_post( $s['service_url'] . '/v1/year-ahead', array(
				'timeout'     => 60,
				'redirection' => 0,
				'headers'     => array( 'X-SR11-Key' => $s['api_key'], 'Content-Type' => 'application/json', 'Accept' => 'application/json' ),
				'body'        => wp_json_encode( $v ),
			) );
			if ( is_wp_error( $res ) ) { return $err( 'The reading service is busy. Please try again in a minute.', 502 ); }
			$code = (int) wp_remote_retrieve_response_code( $res );
			$json = json_decode( wp_remote_retrieve_body( $res ), true );
			if ( ! is_array( $json ) || $code >= 500 || 401 === $code ) { return $err( 'The reading service is busy. Please try again in a minute.', 502 ); }
			if ( 200 !== $code || empty( $json['pdf_base64'] ) ) {
				$r = new WP_REST_Response( $json, in_array( $code, array( 409, 422 ), true ) ? $code : 502 );
				$r->header( 'Cache-Control', 'no-store, private' );
				return $r;
			}
			if ( is_a( $access, 'WC_Order' ) ) {
				$access->update_meta_data( '_sr_y27_created', (int) $access->get_meta( '_sr_y27_created' ) + 1 );
				$access->save();
			}
			$r = new WP_REST_Response( array(
				'status'   => 'ok',
				'pdf'      => $json['pdf_base64'],
				'filename' => $json['filename'] ?? 'Your-2027-Reading.pdf',
				'subtitle' => $json['reading']['subtitle'] ?? '',
			), 200 );
			$r->header( 'Cache-Control', 'no-store, private' );
			return $r;
		},
	) );
} );

/* ---------- Shortcode: the reading page ---------- */
add_shortcode( 'sr_your_2027_reading', function () {
	$order_id = isset( $_GET['y27_order'] ) ? absint( $_GET['y27_order'] ) : 0;
	$key      = isset( $_GET['y27_key'] ) ? sanitize_text_field( wp_unslash( $_GET['y27_key'] ) ) : '';
	if ( ! sr_y27_access( $order_id, $key ) ) {
		$url   = get_permalink( SR_Y27_PRODUCT_ID );
		$price = '';
		if ( function_exists( 'wc_get_product' ) && ( $p = wc_get_product( SR_Y27_PRODUCT_ID ) ) ) { $price = wp_strip_all_tags( wc_price( $p->get_price() ) ); }
		return '<div class="sr-y27-locked" style="max-width:640px;margin:1.5rem auto;border:1px solid #dccdf3;border-top:6px solid #4b2a7b;border-radius:4px;padding:1.6rem;text-align:center;background:#fff">'
			. '<p style="font-style:italic;font-size:1.3rem;margin:0 0 .6rem;color:#4b2a7b">Your 2027 reading is waiting</p>'
			. '<p style="margin:0 0 1.1rem">This page creates your personal year-ahead reading after purchase. Already bought it? Use the link in your order confirmation email, or log in to your account.</p>'
			. '<a href="' . esc_url( $url ) . '" style="display:inline-block;background:#4b2a7b;color:#fff;padding:.8rem 1.4rem;border-radius:3px;text-decoration:none">Get Your 2027 Reading' . ( $price ? ' · ' . esc_html( $price ) : '' ) . '</a></div>';
	}
	$cfg = wp_json_encode( array(
		'endpoint' => esc_url_raw( rest_url( 'sr11y27/v1/reading' ) ),
		'places'   => esc_url_raw( rest_url( 'sr11bc/v1/places' ) ),
		'nonce'    => wp_create_nonce( 'wp_rest' ),
		'order'    => $order_id,
		'key'      => $key,
	) );
	ob_start(); ?>
<div id="sr-y27-app" class="sr-y27">
<style>
.sr-y27{--p:#4b2a7b;--p2:#6d5a8c;--l:#efe7fb;--l2:#dccdf3;--g:#c9a24d;max-width:640px;margin:1.5rem auto;color:#2e2340}
.sr-y27 .card{background:#fff;border:1px solid var(--l2);border-top:6px solid var(--p);border-radius:4px;padding:1.6rem}
.sr-y27 h2{color:var(--p);margin:0 0 .4rem;font-size:1.6rem}
.sr-y27 p.lede{margin:0 0 1.2rem}
.sr-y27 label{display:block;font-weight:600;color:var(--p);margin:0 0 1rem;font-size:.95rem}
.sr-y27 input[type=text],.sr-y27 input[type=date],.sr-y27 input[type=time]{display:block;width:100%;box-sizing:border-box;margin-top:.35rem;padding:.7rem .8rem;border:1px solid var(--l2);border-radius:3px;font-size:1rem;color:#2e2340;background:#fff}
.sr-y27 .row{display:block}
.sr-y27 label.check{font-weight:400;color:#2e2340;display:flex;gap:.5rem;align-items:center;margin-top:-.4rem}
.sr-y27 .city{position:relative;display:block}
.sr-y27 .sugg{position:absolute;left:0;right:0;top:100%;z-index:20;background:#fff;border:1px solid var(--l2);border-radius:3px;max-height:260px;overflow:auto;box-shadow:0 6px 18px rgba(75,42,123,.12)}
.sr-y27 .sugg button{display:block;width:100%;text-align:left;background:#fff;border:0;border-bottom:1px solid var(--l);padding:.6rem .8rem;font-size:.95rem;color:#2e2340;cursor:pointer}
.sr-y27 .sugg button:hover,.sr-y27 .sugg button:focus{background:var(--l)}
.sr-y27 .go{display:inline-block;background:var(--p);color:#fff;border:0;border-radius:3px;padding:.85rem 1.5rem;font-size:1rem;cursor:pointer}
.sr-y27 .go[disabled]{opacity:.6;cursor:wait}
.sr-y27 .msg{margin:1rem 0 0;padding:.8rem 1rem;border-radius:3px;background:var(--l);color:#2e2340}
.sr-y27 .msg.err{background:#fdecec;color:#7a1f1f}
.sr-y27 .done a{color:var(--p);font-weight:700}
.sr-y27 .fine{font-size:.85rem;color:var(--p2);margin-top:1.2rem}
</style>
<div class="card">
<h2>Create Your 2027 Reading</h2>
<p class="lede">Enter your birth details and your personal year-ahead reading is created in seconds. Your birth time places the planets in your houses, so use the most exact time you have.</p>
<form id="y27-form" novalidate>
<label for="y27-name">Your first name (shown on your reading)<input id="y27-name" type="text" maxlength="60" autocomplete="given-name"></label>
<div class="row">
<label for="y27-date">Birth date<input id="y27-date" type="date" min="1800-01-01" max="2026-12-31" required></label>
<label for="y27-time">Birth time (local)<input id="y27-time" type="time"></label>
</div>
<label class="check" for="y27-notime"><input id="y27-notime" type="checkbox"> I don't know my birth time</label>
<label for="y27-city">Birth city<span class="city"><input id="y27-city" type="text" autocomplete="off" placeholder="Start typing, then choose from the list" aria-autocomplete="list"><span class="sugg" id="y27-city-s" hidden></span></span></label>
<button class="go" id="y27-go" type="submit">Create My Reading</button>
<div id="y27-msg" class="msg" hidden></div>
</form>
<p class="fine">Your details are used only to create your reading. Because this is an instant digital download, all sales are final.</p>
</div>
</div>
<script data-jetpack-boost="ignore">
(function(){
  var C = <?php echo $cfg; ?>;
  var $ = function(id){ return document.getElementById(id); };
  var place = null, timer = null, busy = false, lastUrl = null;
  function msg(t, err, html){ var m=$('y27-msg'); m.hidden=false; m.className='msg'+(err?' err':''); if(html){m.innerHTML=t;}else{m.textContent=t;} }
  $('y27-notime').addEventListener('change', function(){ $('y27-time').disabled = this.checked; if(this.checked) $('y27-time').value=''; });
  var city = $('y27-city'), box = $('y27-city-s');
  city.addEventListener('input', function(){
    place = null; clearTimeout(timer);
    var q = city.value.trim(); if (q.length < 2) { box.hidden = true; return; }
    timer = setTimeout(function(){
      fetch(C.places + '?q=' + encodeURIComponent(q), { headers: { 'X-SR11-Request': '1' } })
        .then(function(r){ return r.json(); })
        .then(function(j){
          box.innerHTML = ''; var res = (j && j.results) || [];
          if (!res.length) { box.innerHTML = '<button type="button" disabled>No matches yet. Try the city name only.</button>'; box.hidden = false; return; }
          res.slice(0, 8).forEach(function(p){
            var b = document.createElement('button'); b.type = 'button'; b.textContent = p.label;
            b.addEventListener('click', function(){ place = p; city.value = p.label; box.hidden = true; });
            box.appendChild(b);
          });
          box.hidden = false;
        }).catch(function(){ box.hidden = true; });
    }, 250);
  });
  document.addEventListener('click', function(e){ if (!box.contains(e.target) && e.target !== city) box.hidden = true; });

  function send(extra){
    var d = $('y27-date').value, t = $('y27-time').value, nt = $('y27-notime').checked;
    var dp = d.split('-');
    var body = { order: C.order, key: C.key, name: $('y27-name').value.trim(),
      year: parseInt(dp[0],10), month: parseInt(dp[1],10), day: parseInt(dp[2],10),
      location: { mode: 'place', place_id: place.id } };
    if (nt) { body.time_known = false; } else { var tp = t.split(':'); body.hour = parseInt(tp[0],10); body.minute = parseInt(tp[1],10); }
    for (var k in (extra||{})) body[k] = extra[k];
    busy = true; $('y27-go').disabled = true; msg('Reading your chart and writing your year. This takes a few seconds....');
    fetch(C.endpoint, { method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-SR11-Request': '1', 'X-WP-Nonce': C.nonce },
      body: JSON.stringify(body) })
    .then(function(r){ return r.json().then(function(j){ return { s: r.status, j: j }; }); })
    .then(function(x){
      busy = false; $('y27-go').disabled = false;
      var j = x.j || {};
      if (x.s === 200 && j.pdf) {
        var bin = atob(j.pdf), bytes = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        var blob = new Blob([bytes], { type: 'application/pdf' });
        var url = URL.createObjectURL(blob); lastUrl = url;
        var a = document.createElement('a'); a.href = url; a.download = j.filename || 'Your-2027-Reading.pdf';
        document.body.appendChild(a); a.click(); setTimeout(function(){ a.remove(); }, 4000);
        msg('<span class="done">Your 2027 reading is ready' + (j.subtitle ? ': <em>' + j.subtitle.replace(/</g,'&lt;') + '</em>' : '') +
            '. It should download automatically. If it didn\'t, <a href="' + url + '" download="' + (j.filename || 'Your-2027-Reading.pdf') + '">tap here to download it</a>. A copy is also on its way to your email.</span>', false, true);
        return;
      }
      if (j.status === 'ambiguous') {
        msg('That birth time happened twice on that date because the clocks went back. Choose which one: ' +
            '<button type="button" class="go" id="y27-f0" style="padding:.4rem .8rem;margin:.4rem .3rem 0 0">The first one</button>' +
            '<button type="button" class="go" id="y27-f1" style="padding:.4rem .8rem;margin-top:.4rem">The second one</button>', false, true);
        $('y27-f0').onclick = function(){ send({ fold: 0 }); }; $('y27-f1').onclick = function(){ send({ fold: 1 }); };
        return;
      }
      if (j.status === 'needs_confirmation') { send({ accept_lmt: true }); return; }
      msg(j.message || 'Something went wrong creating your reading. Please try again in a minute.', true);
    })
    .catch(function(){ busy = false; $('y27-go').disabled = false; msg('We could not reach the reading service. Please check your connection and try again.', true); });
  }
  $('y27-form').addEventListener('submit', function(e){
    e.preventDefault(); if (busy) return;
    if (!$('y27-date').value) { msg('Please enter your birth date.', true); return; }
    if (!$('y27-notime').checked && !$('y27-time').value) { msg('Please enter your birth time, or tick "I don\'t know my birth time".', true); return; }
    if (!place) { msg('Please start typing your birth city and choose it from the list.', true); return; }
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
	if ( ! sr_y27_order_has_report( $order ) ) { return; }
	echo '<div style="border:1px solid #dccdf3;border-top:6px solid #4b2a7b;border-radius:4px;padding:1.4rem;margin:0 0 1.5rem;text-align:center;background:#fff">'
		. '<p style="font-style:italic;font-size:1.3rem;margin:0 0 .5rem;color:#4b2a7b">Your 2027 reading is ready to create</p>'
		. '<p style="margin:0 0 1rem">Click below, enter your birth details, and your reading downloads in seconds. We have also emailed you this link so you can come back anytime.</p>'
		. '<a href="' . esc_url( sr_y27_portal_url( $order ) ) . '" style="display:inline-block;background:#4b2a7b;color:#fff;padding:.8rem 1.4rem;border-radius:3px;text-decoration:none">Create My Reading</a></div>';
}, 5 );

add_action( 'woocommerce_email_after_order_table', function ( $order, $sent_to_admin, $plain_text, $email = null ) {
	if ( $sent_to_admin || ! sr_y27_order_has_report( $order ) ) { return; }
	$url = sr_y27_portal_url( $order );
	if ( $plain_text ) {
		echo "\nCreate your 2027 reading: " . esc_url_raw( $url ) . "\n";
		return;
	}
	echo '<p style="margin:16px 0"><strong>Your 2027 Reading</strong><br>Create your personal reading anytime here: <a href="' . esc_url( $url ) . '">Create My Reading</a></p>';
}, 10, 4 );
