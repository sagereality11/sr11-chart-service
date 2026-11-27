/**
 * Sage Reality 11: Your Monthly Transit Forecast ($33.33) and Your Shared Soul Journey ($55.55).
 * - [sr_transit_reading]: the buyer page. Unlocked by the order link (tm_order + tm_key), a logged-in buyer, or an admin.
 *   The order decides the form: one person, or two people with a relationship lens. One month per order
 *   (the first forecast locks the order to its month; birth details can be corrected, 25 creations per order).
 * - [sr_transit_calculator]: the free calculator (this month's wheel, theme and biggest currents, with both offers).
 * - REST sr11tm/v1/reading (buyers) and sr11tm/v1/preview (free, rate limited) forward to the chart service
 *   /v1/transit-month with the SR11 Birth Chart plugin's saved service URL and key.
 * - The reading is written by the chart service (Swiss Ephemeris); the private page "transit-forecast-code"
 *   holds the CSS and scripts that draw the wheels, the web view and the PDF ([sr_tm_core] prints it once).
 * - Order confirmation box and order email link. Prefix "tm" everywhere; app container #sr-tm-app (one person) or
 *   #sr-tmp-app (two people), which the shared "Instant reports" snippets map to products 'tm' and 'tmp'.
 */
if ( ! defined( 'SR_TM_PORTAL_PATH' ) ) { define( 'SR_TM_PORTAL_PATH', '/your-monthly-transit-forecast/' ); }

if ( ! function_exists( 'sr_tm_ids' ) ) {
	function sr_tm_ids() {
		static $ids = null;
		if ( null === $ids ) {
			$a   = get_page_by_path( 'monthly-transit-forecast', OBJECT, 'product' );
			$b   = get_page_by_path( 'shared-soul-journey', OBJECT, 'product' );
			$ids = array( 'solo' => $a ? (int) $a->ID : 0, 'pair' => $b ? (int) $b->ID : 0 );
		}
		return $ids;
	}
	function sr_tm_order_mode( $order ) {
		if ( ! $order || ! is_a( $order, 'WC_Order' ) ) { return ''; }
		if ( ! $order->is_paid() && ! in_array( $order->get_status(), array( 'processing', 'completed' ), true ) ) { return ''; }
		$ids = sr_tm_ids(); $solo = false; $pair = false;
		foreach ( $order->get_items() as $it ) {
			$pid = (int) $it->get_product_id();
			if ( $pid && $pid === $ids['pair'] ) { $pair = true; }
			if ( $pid && $pid === $ids['solo'] ) { $solo = true; }
		}
		return $pair && $solo ? 'both' : ( $pair ? 'pair' : ( $solo ? 'solo' : '' ) );
	}
	function sr_tm_portal_url( $order ) {
		return add_query_arg( array( 'tm_order' => $order->get_id(), 'tm_key' => $order->get_order_key() ), home_url( SR_TM_PORTAL_PATH ) );
	}
	/** array( 'order' => WC_Order|null, 'mode' => solo|pair|both ) or false. */
	function sr_tm_access( $order_id, $key ) {
		if ( $order_id && $key && function_exists( 'wc_get_order' ) ) {
			$o = wc_get_order( absint( $order_id ) );
			if ( $o && hash_equals( (string) $o->get_order_key(), (string) $key ) ) {
				$m = sr_tm_order_mode( $o );
				if ( $m ) { return array( 'order' => $o, 'mode' => $m ); }
			}
		}
		if ( current_user_can( 'manage_options' ) ) { return array( 'order' => null, 'mode' => 'both' ); }
		if ( is_user_logged_in() && function_exists( 'wc_customer_bought_product' ) ) {
			$u = wp_get_current_user(); $ids = sr_tm_ids();
			$s = $ids['solo'] && wc_customer_bought_product( $u->user_email, $u->ID, $ids['solo'] );
			$p = $ids['pair'] && wc_customer_bought_product( $u->user_email, $u->ID, $ids['pair'] );
			if ( $s || $p ) { return array( 'order' => null, 'mode' => $s && $p ? 'both' : ( $p ? 'pair' : 'solo' ) ); }
		}
		return false;
	}
	function sr_tm_month_options() {
		$now = new DateTime( 'first day of this month', wp_timezone() ); $out = array();
		for ( $i = 0; $i < 2; $i++ ) { $out[ $now->format( 'Y-n' ) ] = wp_date( 'F Y', $now->getTimestamp() ); $now->modify( '+1 month' ); }
		return $out;
	}
	function sr_tm_month_label( $ym ) {
		$p = array_map( 'intval', explode( '-', (string) $ym ) );
		if ( count( $p ) !== 2 || $p[1] < 1 || $p[1] > 12 ) { return ''; }
		return date_i18n( 'F Y', mktime( 12, 0, 0, $p[1], 1, $p[0] ) );
	}
	function sr_tm_err( $msg, $status ) {
		$r = new WP_REST_Response( array( 'status' => 'error', 'message' => $msg ), $status );
		$r->header( 'Cache-Control', 'no-store, private' );
		return $r;
	}
	/** Validate one person with the SR11 Birth Chart plugin; returns the cleaned body or WP_Error. */
	function sr_tm_person( $in ) {
		$v = SR11BC_Rest::validate( $in );
		if ( is_wp_error( $v ) ) { return $v; }
		unset( $v['house_system'], $v['points'], $v['asteroids'], $v['aspects'] );
		$v['name']    = mb_substr( sanitize_text_field( (string) ( $in['name'] ?? '' ) ), 0, 40 );
		$v['pronoun'] = in_array( $in['pronoun'] ?? '', array( 'she', 'he', 'they' ), true ) ? $in['pronoun'] : 'they';
		return $v;
	}
	/** Build the service body from the visitor's input and call /v1/transit-month. */
	function sr_tm_call( $in, $fy, $fm, $allow_pair ) {
		if ( ! class_exists( 'SR11BC_Rest' ) || ! class_exists( 'SR11BC_Settings' ) ) {
			return sr_tm_err( 'The calculator is temporarily unavailable. Please try again in a few minutes.', 503 );
		}
		$a = sr_tm_person( $in );
		if ( is_wp_error( $a ) ) { return sr_tm_err( $a->get_error_message(), 422 ); }
		$body = array_merge( $a, array( 'forecast_year' => $fy, 'forecast_month' => $fm,
			'forecast_tz' => mb_substr( preg_replace( '#[^A-Za-z0-9_+/-]#', '', (string) ( $in['forecast_tz'] ?? '' ) ), 0, 64 ),
			'node' => ( 'mean' === ( $in['node'] ?? '' ) ) ? 'mean' : 'true' ) );
		if ( ! empty( $in['partner'] ) && is_array( $in['partner'] ) ) {
			if ( ! $allow_pair ) { return sr_tm_err( 'This order is for a one-person forecast. The two-person forecast is Your Shared Soul Journey.', 403 ); }
			$b = sr_tm_person( $in['partner'] );
			if ( is_wp_error( $b ) ) { return sr_tm_err( 'The other person: ' . $b->get_error_message(), 422 ); }
			$body['partner']      = $b;
			$rels                 = array( 'romantic', 'spouse', 'mother_son', 'mother_daughter', 'father_son', 'father_daughter', 'parent_child', 'siblings', 'grandparent', 'friends', 'business' );
			$body['relationship'] = in_array( $in['relationship'] ?? '', $rels, true ) ? $in['relationship'] : 'parent_child';
		}
		$s   = SR11BC_Settings::get();
		$res = wp_remote_post( $s['service_url'] . '/v1/transit-month', array(
			'timeout' => 120, 'redirection' => 0,
			'headers' => array( 'X-SR11-Key' => $s['api_key'], 'Content-Type' => 'application/json', 'Accept' => 'application/json' ),
			'body'    => wp_json_encode( $body ),
		) );
		if ( is_wp_error( $res ) ) { return sr_tm_err( 'The calculator is busy. Please try again in a minute.', 502 ); }
		$code = (int) wp_remote_retrieve_response_code( $res );
		$json = json_decode( wp_remote_retrieve_body( $res ), true );
		if ( ! is_array( $json ) || $code >= 500 || 401 === $code ) { return sr_tm_err( 'The calculator is busy. Please try again in a minute.', 502 ); }
		if ( 200 !== $code ) {
			$r = new WP_REST_Response( $json, in_array( $code, array( 409, 422 ), true ) ? $code : 502 );
			$r->header( 'Cache-Control', 'no-store, private' );
			return $r;
		}
		return $json;
	}
	function sr_tm_core() {
		static $done = false;
		if ( $done ) { return ''; }
		$done = true;
		$p = get_page_by_path( 'transit-forecast-code' );
		return $p ? do_blocks( (string) $p->post_content ) : '';
	}
	function sr_tm_config( $extra ) {
		$ids = sr_tm_ids(); $price = function ( $id ) { $p = $id && function_exists( 'wc_get_product' ) ? wc_get_product( $id ) : null; return $p ? wp_strip_all_tags( wc_price( $p->get_price() ) ) : ''; };
		return '<script data-jetpack-boost="ignore">window.TMConfig=' . wp_json_encode( array_merge( array(
			'endpoint' => esc_url_raw( rest_url( 'sr11tm/v1/reading' ) ), 'preview' => esc_url_raw( rest_url( 'sr11tm/v1/preview' ) ),
			'nonce' => wp_create_nonce( 'wp_rest' ), 'soloUrl' => $ids['solo'] ? get_permalink( $ids['solo'] ) : home_url( '/shop/' ),
			'pairUrl' => $ids['pair'] ? get_permalink( $ids['pair'] ) : home_url( '/shop/' ), 'soloPrice' => $price( $ids['solo'] ), 'pairPrice' => $price( $ids['pair'] ),
		), $extra ) ) . ';</script>';
	}
	function sr_tm_fonts() {
		return '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&amp;family=Source+Serif+4:ital,wght@0,400;0,600;1,400&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;display=swap" rel="stylesheet">';
	}
}

/* ---------- REST routes ---------- */
add_action( 'rest_api_init', function () {
	register_rest_route( 'sr11tm/v1', '/reading', array(
		'methods' => 'POST', 'permission_callback' => '__return_true',
		'callback' => function ( WP_REST_Request $req ) {
			if ( '1' !== $req->get_header( 'x_sr11_request' ) ) { return sr_tm_err( 'Invalid request.', 400 ); }
			if ( strlen( (string) $req->get_body() ) > 6144 ) { return sr_tm_err( 'Request too large.', 413 ); }
			$in  = $req->get_json_params(); $in = is_array( $in ) ? $in : array();
			$acc = sr_tm_access( $in['order'] ?? 0, isset( $in['key'] ) ? sanitize_text_field( (string) $in['key'] ) : '' );
			if ( ! $acc ) { return sr_tm_err( 'This page is for Monthly Transit Forecast buyers. Please use the link in your order email.', 403 ); }
			$o = $acc['order'];
			if ( $o && (int) $o->get_meta( '_sr_tm_created' ) >= 25 ) { return sr_tm_err( 'This order has reached its limit of forecasts. Please reach out and I will help.', 429 ); }
			$ym     = preg_replace( '/[^0-9-]/', '', (string) ( $in['forecast'] ?? '' ) );
			$locked = $o ? (string) $o->get_meta( '_sr_tm_month' ) : '';
			if ( $locked && $ym !== $locked ) { return sr_tm_err( 'This order is for your ' . sr_tm_month_label( $locked ) . ' forecast. Each order covers one month, so for another month please place a new order.', 422 ); }
			if ( ! $locked && ! array_key_exists( $ym, sr_tm_month_options() ) ) { return sr_tm_err( 'Please choose this month or next month for your forecast.', 422 ); }
			if ( 'pair' === $acc['mode'] && empty( $in['partner'] ) ) { return sr_tm_err( 'Please add the second person for your Shared Soul Journey.', 422 ); }
			list( $fy, $fm ) = array_map( 'intval', explode( '-', $ym ) );
			$out = sr_tm_call( $in, $fy, $fm, in_array( $acc['mode'], array( 'pair', 'both' ), true ) );
			if ( $out instanceof WP_REST_Response ) { return $out; }
			if ( empty( $out['reading'] ) ) { return sr_tm_err( 'Something went wrong creating your forecast. Please try again in a minute.', 502 ); }
			if ( $o ) {
				$o->update_meta_data( '_sr_tm_created', (int) $o->get_meta( '_sr_tm_created' ) + 1 );
				if ( ! $locked ) { $o->update_meta_data( '_sr_tm_month', $ym ); }
				$o->save();
			}
			$r = new WP_REST_Response( array( 'status' => 'ok', 'reading' => $out['reading'], 'filename' => $out['filename'] ?? 'Monthly-Transit-Forecast.pdf' ), 200 );
			$r->header( 'Cache-Control', 'no-store, private' );
			return $r;
		},
	) );
	register_rest_route( 'sr11tm/v1', '/preview', array(
		'methods' => 'POST', 'permission_callback' => '__return_true',
		'callback' => function ( WP_REST_Request $req ) {
			if ( '1' !== $req->get_header( 'x_sr11_request' ) ) { return sr_tm_err( 'Invalid request.', 400 ); }
			if ( strlen( (string) $req->get_body() ) > 6144 ) { return sr_tm_err( 'Request too large.', 413 ); }
			$ip  = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : 'x';
			$k   = 'sr_tm_pv_' . md5( $ip );
			$n   = (int) get_transient( $k );
			if ( $n >= 15 && ! current_user_can( 'manage_options' ) ) { return sr_tm_err( 'You have looked at quite a few charts this hour. Please try again a little later.', 429 ); }
			set_transient( $k, $n + 1, HOUR_IN_SECONDS );
			$in  = $req->get_json_params(); $in = is_array( $in ) ? $in : array();
			$now = new DateTime( 'now', wp_timezone() );
			$out = sr_tm_call( $in, (int) $now->format( 'Y' ), (int) $now->format( 'n' ), true );
			if ( $out instanceof WP_REST_Response ) { return $out; }
			$r = $out['reading'] ?? array();
			if ( ! $r ) { return sr_tm_err( 'Something went wrong. Please try again in a minute.', 502 ); }
			$pair  = ! empty( $r['pair'] );
			$first = $r['parts'][0]['sections'][0] ?? array();
			$cur   = array();
			foreach ( $r['parts'] as $p ) {
				$t = (string) ( $p['title'] ?? '' );
				if ( 0 === strpos( $t, 'The Big Currents' ) || 0 === strpos( $t, 'Where ' ) && false !== strpos( $t, 'Touches You Both' ) ) {
					foreach ( array_slice( $p['sections'], 0, 3 ) as $s ) { $cur[] = array( (string) $s['title'], (string) ( $s['eyebrow'] ?? '' ) ); }
				}
			}
			$charts = $r['charts'];
			$snap   = array(
				'month' => (string) $r['month'], 'pair' => $pair, 'names' => $pair ? $r['name'] . ' and ' . $r['other'] : '',
				'theme' => (string) ( $first['title'] ?? '' ), 'lead' => (string) ( $first['paras'][0] ?? '' ), 'currents' => $cur,
				'charts' => array( 'a' => $charts['a'], 'b' => $pair ? $charts['b'] : null, 't' => $charts['t'] ),
				'caption' => $pair ? 'Inner ring ' . $r['name'] . ' · Middle ring ' . $r['other'] . ' · Outer ring this month' : 'Inner ring your birth chart · Outer ring this month',
				'more' => $pair ? 'The soul agreements between your charts, how this month presses on each one with diagrams, what belongs to each of you, your shared New and Full Moon, a shared calendar, both birth charts and questions to ask each other.'
					: 'The season you are in (profections, progressions, solar arcs and life cycles), every big current with its deeper meaning, your karmic pattern, your personal planets day by day, the New and Full Moon, a calendar of key dates and your charts.',
			);
			$res = new WP_REST_Response( array( 'status' => 'ok', 'snapshot' => $snap ), 200 );
			$res->header( 'Cache-Control', 'no-store, private' );
			return $res;
		},
	) );
} );

/* ---------- Shortcodes ---------- */
add_shortcode( 'sr_tm_core', function () { return sr_tm_core(); } );
add_shortcode( 'sr_transit_reading', function () {
	$oid = isset( $_GET['tm_order'] ) ? absint( $_GET['tm_order'] ) : 0;
	$key = isset( $_GET['tm_key'] ) ? sanitize_text_field( wp_unslash( $_GET['tm_key'] ) ) : '';
	$acc = sr_tm_access( $oid, $key );
	if ( ! $acc ) {
		$ids = sr_tm_ids();
		return '<div style="max-width:640px;margin:1.5rem auto;border:1px solid #dccdf3;border-top:6px solid #4b2a7b;border-radius:4px;padding:1.6rem;text-align:center;background:#fff">'
			. '<p style="font-style:italic;font-size:1.3rem;margin:0 0 .6rem;color:#4b2a7b">Your Monthly Transit Forecast is waiting</p>'
			. '<p style="margin:0 0 1.1rem">This page creates your forecast after purchase. Already bought it? Use the link in your order confirmation email, or log in to your account.</p>'
			. '<a href="' . esc_url( $ids['solo'] ? get_permalink( $ids['solo'] ) : home_url( '/shop/' ) ) . '" style="display:inline-block;background:#4b2a7b;color:#fff;padding:.8rem 1.4rem;border-radius:3px;text-decoration:none;margin:.2rem">Your Monthly Transit Forecast</a> '
			. '<a href="' . esc_url( $ids['pair'] ? get_permalink( $ids['pair'] ) : home_url( '/shop/' ) ) . '" style="display:inline-block;background:#6d5a8c;color:#fff;padding:.8rem 1.4rem;border-radius:3px;text-decoration:none;margin:.2rem">Your Shared Soul Journey</a></div>';
	}
	$o      = $acc['order'];
	$locked = $o ? (string) $o->get_meta( '_sr_tm_month' ) : '';
	$opts   = $locked ? array( $locked => sr_tm_month_label( $locked ) ) : sr_tm_month_options();
	$months = array(); foreach ( $opts as $k => $l ) { $months[] = array( $k, $l ); }
	$pair   = 'pair' === $acc['mode'];
	$title  = $pair ? 'Create Your Shared Soul Journey' : 'Create Your Monthly Transit Forecast';
	$lede   = $pair ? 'Enter both people\'s birth details, choose how you are connected and pick your month. Your forecast is written from your relationship\'s lens, shows right here with a section menu and downloads as a PDF. Each order covers one month.'
		: 'Enter your birth details and choose your month. Your forecast shows right here with a section menu and downloads as a PDF you can keep. Each order covers one month.';
	$pre    = $pair ? 'tmp' : 'tm'; // matches the "Instant reports" snippets (email copy + order note); fields use this prefix
	return sr_tm_fonts() . sr_tm_config( array( 'order' => $o ? $o->get_id() : 0, 'key' => $o ? $key : '', 'mode' => $acc['mode'], 'months' => $months, 'locked' => $locked ? sr_tm_month_label( $locked ) : '', 'pre' => $pre ) )
		. '<div id="sr-' . $pre . '-app"></div><div class="tm-page"><div class="tm-card"><h2>' . esc_html( $title ) . '</h2><p class="tm-lede">' . esc_html( $lede ) . '</p>'
		. '<div id="tm-app"></div><p class="tm-fine">Calculated with the Swiss Ephemeris. Birthplace search uses GeoNames (CC BY 4.0). Your details are used only to create your forecast. Because this is an instant digital download, all sales are final.</p></div>'
		. '<div id="tm-out" hidden></div></div>' . sr_tm_core();
} );
add_shortcode( 'sr_transit_calculator', function () {
	return sr_tm_fonts() . sr_tm_config( array() ) . '<div class="tm-page"><div class="tm-card"><div id="tm-free"></div>'
		. '<p class="tm-fine">Calculated with the Swiss Ephemeris. Birthplace search uses GeoNames (CC BY 4.0). Your details are used only to draw your chart and are not stored.</p></div></div>' . sr_tm_core();
} );

/* ---------- Order confirmation page + emails ---------- */
add_action( 'woocommerce_thankyou', function ( $order_id ) {
	$o = wc_get_order( $order_id );
	$m = sr_tm_order_mode( $o );
	if ( ! $m ) { return; }
	$nm = 'pair' === $m ? 'Shared Soul Journey' : 'Monthly Transit Forecast';
	echo '<div style="border:1px solid #dccdf3;border-top:6px solid #4b2a7b;border-radius:4px;padding:1.4rem;margin:0 0 1.5rem;text-align:center;background:#fff">'
		. '<p style="font-style:italic;font-size:1.3rem;margin:0 0 .5rem;color:#4b2a7b">Your ' . esc_html( $nm ) . ' is ready to create</p>'
		. '<p style="margin:0 0 1rem">Click below, enter the birth details, choose your month, and your forecast is created in about half a minute. I have also emailed you this link so you can come back anytime.</p>'
		. '<a href="' . esc_url( sr_tm_portal_url( $o ) ) . '" style="display:inline-block;background:#4b2a7b;color:#fff;padding:.8rem 1.4rem;border-radius:3px;text-decoration:none">Create My Forecast</a></div>';
}, 5 );
add_action( 'woocommerce_email_after_order_table', function ( $order, $sent_to_admin, $plain_text, $email = null ) {
	if ( $sent_to_admin ) { return; }
	$m = sr_tm_order_mode( $order );
	if ( ! $m ) { return; }
	$nm  = 'pair' === $m ? 'Shared Soul Journey' : 'Monthly Transit Forecast';
	$url = sr_tm_portal_url( $order );
	if ( $plain_text ) { echo PHP_EOL . 'Create your ' . $nm . ': ' . esc_url_raw( $url ) . PHP_EOL; return; }
	echo '<p style="margin:16px 0"><strong>Your ' . esc_html( $nm ) . '</strong><br>Create your forecast anytime here: <a href="' . esc_url( $url ) . '">Create My Forecast</a></p>';
}, 10, 4 );
