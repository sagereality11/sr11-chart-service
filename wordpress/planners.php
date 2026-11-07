/**
 * Sage Reality 11: Personalized Planners (Moon Cycles, Money & Business, Transits).
 * - [sr_planner product="moon|money|transits"]: the create-your-planner page, unlocked for paid orders
 *   (private link with order key), logged-in buyers and site admins. The buyer enters birth details, her
 *   current city and the month her planner begins; the PDF downloads in seconds.
 * - REST route sr11pl/v1/create forwards to the chart service (/v1/planner) using the SR11 Birth Chart
 *   plugin's saved service URL and key.
 * - Policy (Nov 3, 2026): each purchase is for one person. Birth details and start month are saved on the
 *   order the first time; the buyer may correct them once, after that the link re-creates the saved planner.
 * - Adds the "Create My Planner" link to the order confirmation page and the customer's order emails.
 * The "Instant reports" snippets handle the emailed copy to the buyer, the order note and auto-complete.
 */
if ( ! function_exists( 'sr_pl_products' ) ) {
	function sr_pl_products() {
		return array(
			'moon'     => array( 'id' => 9373, 'pre' => 'pmc', 'name' => 'Moon Cycles Planner', 'path' => '/your-moon-cycles-planner/' ),
			'money'    => array( 'id' => 9374, 'pre' => 'pmb', 'name' => 'Money & Business Planner', 'path' => '/your-money-business-planner/' ),
			'transits' => array( 'id' => 9375, 'pre' => 'ptr', 'name' => 'Transits Planner', 'path' => '/your-transits-planner/' ),
		);
	}
	function sr_pl_order_has( $order, $pid ) {
		if ( ! $order || ! is_a( $order, 'WC_Order' ) ) { return false; }
		if ( ! $order->is_paid() && ! in_array( $order->get_status(), array( 'processing', 'completed' ), true ) ) { return false; }
		foreach ( $order->get_items() as $item ) {
			if ( (int) $item->get_product_id() === (int) $pid ) { return true; }
		}
		return false;
	}
	function sr_pl_url( $order, $p ) {
		return add_query_arg( array( $p['pre'] . '_order' => $order->get_id(), $p['pre'] . '_key' => $order->get_order_key() ), home_url( $p['path'] ) );
	}
	/** Returns the WC_Order for a valid private link, true for admins and logged-in buyers, false otherwise. */
	function sr_pl_access( $p, $order_id, $key ) {
		if ( ! function_exists( 'wc_get_order' ) ) { return false; }
		if ( $order_id && $key ) {
			$order = wc_get_order( absint( $order_id ) );
			if ( $order && hash_equals( (string) $order->get_order_key(), (string) $key ) && sr_pl_order_has( $order, $p['id'] ) ) { return $order; }
		}
		if ( current_user_can( 'manage_options' ) ) { return true; }
		if ( is_user_logged_in() && function_exists( 'wc_customer_bought_product' ) ) {
			$user = wp_get_current_user();
			if ( wc_customer_bought_product( $user->user_email, $user->ID, $p['id'] ) ) { return true; }
		}
		return false;
	}
	function sr_pl_err( $msg, $status ) {
		$r = new WP_REST_Response( array( 'status' => 'error', 'message' => $msg ), $status );
		$r->header( 'Cache-Control', 'no-store, private' );
		return $r;
	}
	/** The months a buyer may start in: this month through the next twelve (site time). */
	function sr_pl_months() {
		$out = array();
		$y   = (int) current_time( 'Y' );
		$m   = (int) current_time( 'n' );
		for ( $i = 0; $i < 13; $i++ ) {
			$yy = $y + intdiv( $m - 1 + $i, 12 );
			$mm = ( $m - 1 + $i ) % 12 + 1;
			$out[ sprintf( '%04d-%02d', $yy, $mm ) ] = date_i18n( 'F Y', mktime( 0, 0, 0, $mm, 1, $yy ) );
		}
		return $out;
	}
	function sr_pl_details_sig( $d ) {
		return md5( wp_json_encode( array( $d['year'], $d['month'], $d['day'], $d['hour'], $d['minute'], $d['place_id'], $d['start'] ) ) );
	}
	/* Calendar add-on ($9.99 per planner): a checkbox on the planner's product page. */
	if ( ! defined( 'SR_PL_CAL_PRICE' ) ) { define( 'SR_PL_CAL_PRICE', 9.99 ); }
	function sr_pl_is_planner( $pid ) {
		foreach ( sr_pl_products() as $p ) { if ( (int) $p['id'] === (int) $pid ) { return true; } }
		return false;
	}
	function sr_pl_order_has_calendar( $order, $pid ) {
		if ( ! $order || ! is_a( $order, 'WC_Order' ) ) { return false; }
		foreach ( $order->get_items() as $item ) {
			if ( (int) $item->get_product_id() === (int) $pid && 'Yes' === $item->get_meta( 'Calendar add-on' ) ) { return true; }
		}
		return false;
	}
	function sr_pl_cal_steps_html() {
		return '<p><strong>iPhone or iPad:</strong> tap the calendar file (in this email, or the Add My Dates to My Calendar button on your planner page), then tap <strong>Add All</strong> and choose <strong>New Calendar</strong>.</p>'
			. '<p><strong>Mac:</strong> double-click the file and choose a calendar.</p>'
			. '<p><strong>Outlook:</strong> double-click the file, or in Outlook.com go to Calendar, then Add calendar, then Upload from file.</p>'
			. '<p><strong>Google Calendar:</strong> on a computer, go to calendar.google.com, then Settings, then Import &amp; export, and import the file. The dates then show on your phone too.</p>'
			. '<p>Each date has a reminder at 9:00 AM that morning. To remove everything at once, delete the calendar you created.</p>'
			. '<p><strong>Works with:</strong> Apple Calendar on iPhone, iPad and Mac, Outlook, and Google Calendar (imported on a computer). Most other calendar apps that can import a .ics file work too. Google Calendar and some versions of Outlook do not keep imported reminders, so turn on notifications in those apps if you want them. Calendar apps that cannot import files, such as the Google Calendar phone app on its own, will not open it directly.</p>';
	}
}

/* ---------- Calendar add-on on the product page, cart and order ---------- */
add_action( 'woocommerce_before_add_to_cart_button', function () {
	global $product;
	if ( ! $product || ! sr_pl_is_planner( $product->get_id() ) ) { return; }
	echo '<div class="sr-pl-cal" style="border:1px solid #dccdf3;border-left:5px solid #5b2a86;border-radius:4px;padding:.9rem 1rem;margin:0 0 1rem;background:#faf6fe">'
		. '<label style="display:flex;gap:.6rem;align-items:flex-start;cursor:pointer;font-weight:600;color:#3b1d5c">'
		. '<input type="checkbox" name="sr_pl_calendar" value="1" style="margin-top:.3rem">'
		. '<span>Add my planner dates to my calendar (+' . wp_strip_all_tags( wc_price( SR_PL_CAL_PRICE ) ) . ')'
		. '<span style="display:block;font-weight:400;color:#6d5a8c;font-size:.92rem;margin-top:.25rem">Every date in your planner as a calendar file with color-coded symbols and a reminder at 9:00 AM on the day. Works with Apple Calendar (iPhone, iPad, Mac), Outlook and Google Calendar. Google Calendar imports on a computer, and Google and some versions of Outlook may not keep the 9:00 AM reminder.</span></span>'
		. '</label></div>';
} );
add_filter( 'woocommerce_add_cart_item_data', function ( $data, $product_id ) {
	if ( sr_pl_is_planner( $product_id ) && ! empty( $_POST['sr_pl_calendar'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification
		$data['sr_pl_calendar'] = 1;
		$data['unique_key']     = md5( 'sr_pl_cal' . $product_id ); // keep planners with and without the add-on as separate lines
	}
	return $data;
}, 10, 2 );
add_action( 'woocommerce_before_calculate_totals', function ( $cart ) {
	if ( is_admin() && ! defined( 'DOING_AJAX' ) ) { return; }
	foreach ( $cart->get_cart() as $item ) {
		if ( empty( $item['sr_pl_calendar'] ) || empty( $item['data'] ) ) { continue; }
		$base = wc_get_product( $item['product_id'] );
		if ( $base ) { $item['data']->set_price( (float) $base->get_price() + SR_PL_CAL_PRICE ); }
	}
}, 20 );
add_filter( 'woocommerce_get_item_data', function ( $out, $item ) {
	if ( ! empty( $item['sr_pl_calendar'] ) ) {
		$out[] = array( 'key' => 'Calendar add-on', 'value' => 'Yes', 'display' => 'Yes' );
	}
	return $out;
}, 10, 2 );
add_action( 'woocommerce_checkout_create_order_line_item', function ( $item, $key, $values ) {
	if ( ! empty( $values['sr_pl_calendar'] ) ) { $item->add_meta_data( 'Calendar add-on', 'Yes', true ); }
}, 10, 3 );

/* ---------- REST route ---------- */
add_action( 'rest_api_init', function () {
	register_rest_route( 'sr11pl/v1', '/create', array(
		'methods'             => 'POST',
		'permission_callback' => '__return_true',
		'callback'            => function ( WP_REST_Request $req ) {
			if ( '1' !== $req->get_header( 'x_sr11_request' ) ) { return sr_pl_err( 'Invalid request.', 400 ); }
			if ( strlen( (string) $req->get_body() ) > 4096 ) { return sr_pl_err( 'Request too large.', 413 ); }
			$in    = $req->get_json_params();
			$in    = is_array( $in ) ? $in : array();
			$prods = sr_pl_products();
			$slug  = isset( $in['product'] ) ? sanitize_key( $in['product'] ) : '';
			if ( ! isset( $prods[ $slug ] ) ) { return sr_pl_err( 'Unknown planner.', 400 ); }
			$p      = $prods[ $slug ];
			$access = sr_pl_access( $p, $in['order'] ?? 0, isset( $in['key'] ) ? sanitize_text_field( (string) $in['key'] ) : '' );
			if ( ! $access ) { return sr_pl_err( 'This page is for ' . $p['name'] . ' buyers. Please use the link in your order email.', 403 ); }
			if ( ! class_exists( 'SR11BC_Rest' ) || ! class_exists( 'SR11BC_Settings' ) ) {
				return sr_pl_err( 'Your planner is temporarily unavailable. Please try again in a few minutes.', 503 );
			}
			$start = isset( $in['start'] ) ? sanitize_text_field( (string) $in['start'] ) : '';
			if ( ! isset( sr_pl_months()[ $start ] ) ) { return sr_pl_err( 'Please choose the month your planner begins.', 422 ); }
			$cur = isset( $in['current_place_id'] ) ? absint( $in['current_place_id'] ) : 0;
			if ( ! $cur ) { return sr_pl_err( 'Please start typing the city you live in now and choose it from the list.', 422 ); }

			$details = array(
				'year' => (int) ( $in['year'] ?? 0 ), 'month' => (int) ( $in['month'] ?? 0 ), 'day' => (int) ( $in['day'] ?? 0 ),
				'hour' => (int) ( $in['hour'] ?? 0 ), 'minute' => (int) ( $in['minute'] ?? 0 ),
				'place_id' => (int) ( $in['location']['place_id'] ?? 0 ), 'start' => $start, 'current' => $cur,
				'record_offset_minutes' => $in['location']['record_offset_minutes'] ?? null,
				'name' => mb_substr( sanitize_text_field( (string) ( $in['name'] ?? '' ) ), 0, 60 ),
			);
			$note = '';
			// One purchase is for one person: save the details, allow one correction, then re-create the saved planner.
			if ( is_a( $access, 'WC_Order' ) ) {
				$saved = $access->get_meta( '_sr_pl_details_' . $slug );
				$saved = is_array( $saved ) ? $saved : null;
				if ( $saved && sr_pl_details_sig( $saved ) !== sr_pl_details_sig( $details ) ) {
					if ( (int) $access->get_meta( '_sr_pl_changes_' . $slug ) >= 1 ) {
						$details = $saved;
						$note    = 'This planner has already been created with the birth details saved on your order, so your saved planner has been created again. If something needs fixing, please reach out.';
					} else {
						$access->update_meta_data( '_sr_pl_changes_' . $slug, 1 );
					}
				}
				if ( ! $note ) {
					$access->update_meta_data( '_sr_pl_details_' . $slug, $details );
				}
				if ( (int) $access->get_meta( '_sr_pl_created_' . $slug ) >= 25 ) {
					return sr_pl_err( 'This order has reached its limit of planners. Please reach out and I will help.', 429 );
				}
			}
			$body = array(
				'year' => $details['year'], 'month' => $details['month'], 'day' => $details['day'],
				'hour' => $details['hour'], 'minute' => $details['minute'],
				'location' => array_filter( array( 'mode' => 'place', 'place_id' => $details['place_id'], 'record_offset_minutes' => $details['record_offset_minutes'] ), function ( $v ) { return null !== $v && '' !== $v; } ),
			);
			if ( isset( $in['fold'] ) ) { $body['fold'] = (int) $in['fold']; }
			if ( ! empty( $in['accept_lmt'] ) ) { $body['accept_lmt'] = true; }
			$v = SR11BC_Rest::validate( $body );
			if ( is_wp_error( $v ) ) { return sr_pl_err( $v->get_error_message(), 422 ); }
			unset( $v['house_system'], $v['points'], $v['asteroids'], $v['aspects'] );
			list( $sy, $sm ) = array_map( 'intval', explode( '-', $details['start'] ) );
			$with_cal = is_a( $access, 'WC_Order' ) ? sr_pl_order_has_calendar( $access, $p['id'] ) : current_user_can( 'manage_options' );
			$v = array_merge( $v, array( 'product' => $slug, 'name' => $details['name'], 'start_year' => $sy, 'start_month' => $sm, 'current_place_id' => $details['current'], 'with_calendar' => (bool) $with_cal ) );
			$s   = SR11BC_Settings::get();
			$res = wp_remote_post( $s['service_url'] . '/v1/planner', array(
				'timeout'     => 90,
				'redirection' => 0,
				'headers'     => array( 'X-SR11-Key' => $s['api_key'], 'Content-Type' => 'application/json', 'Accept' => 'application/json' ),
				'body'        => wp_json_encode( $v ),
			) );
			if ( is_wp_error( $res ) ) { return sr_pl_err( 'The planner service is busy. Please try again in a minute.', 502 ); }
			$code = (int) wp_remote_retrieve_response_code( $res );
			$json = json_decode( wp_remote_retrieve_body( $res ), true );
			if ( ! is_array( $json ) || $code >= 500 || 401 === $code ) { return sr_pl_err( 'The planner service is busy. Please try again in a minute.', 502 ); }
			if ( 200 !== $code ) {
				$r = new WP_REST_Response( $json, in_array( $code, array( 409, 422 ), true ) ? $code : 502 );
				$r->header( 'Cache-Control', 'no-store, private' );
				return $r;
			}
			if ( empty( $json['pdf_base64'] ) ) { return sr_pl_err( 'Something went wrong creating your planner. Please try again in a minute.', 502 ); }
			if ( is_a( $access, 'WC_Order' ) ) {
				$access->update_meta_data( '_sr_pl_created_' . $slug, (int) $access->get_meta( '_sr_pl_created_' . $slug ) + 1 );
				// Email the calendar file to the buyer once per set of birth details.
				if ( ! empty( $json['ics_base64'] ) && function_exists( 'WC' ) ) {
					$sig  = sr_pl_details_sig( $details );
					$sent = (array) $access->get_meta( '_sr_pl_cal_sent_' . $slug );
					$to   = $access->get_billing_email();
					if ( $to && ! in_array( $sig, $sent, true ) && count( $sent ) < 5 ) {
						$file = trailingslashit( get_temp_dir() ) . sanitize_file_name( $json['ics_filename'] ?? 'Planner-Calendar.ics' );
						file_put_contents( $file, base64_decode( $json['ics_base64'] ) );
						$first  = $access->get_billing_first_name() ? $access->get_billing_first_name() : $details['name'];
						$body   = '<p>Hi ' . esc_html( $first ) . ',</p>'
							. '<p>Your ' . esc_html( $p['name'] ) . ' dates are attached as a calendar file, so every date in your planner can live right in your phone\'s calendar.</p>'
							. sr_pl_cal_steps_html()
							. '<p>With Love and Light,<br>Tiff</p>';
						$mailer = WC()->mailer();
						if ( $mailer->send( $to, 'Your ' . $p['name'] . ' dates for your calendar', $mailer->wrap_message( 'Your Planner Dates', $body ), "Content-Type: text/html\r\n", array( $file ) ) ) {
							$sent[] = $sig;
							$access->update_meta_data( '_sr_pl_cal_sent_' . $slug, $sent );
							$access->add_order_note( 'Calendar file for the ' . $p['name'] . ' emailed to the customer at ' . $to . '.' );
						}
						@unlink( $file );
					}
				}
				$access->save();
			}
			$r = new WP_REST_Response( array( 'status' => 'ok', 'pdf' => $json['pdf_base64'], 'filename' => $json['filename'] ?? 'Planner.pdf', 'note' => $note,
				'ics' => $json['ics_base64'] ?? '', 'ics_filename' => $json['ics_filename'] ?? '' ), 200 );
			$r->header( 'Cache-Control', 'no-store, private' );
			return $r;
		},
	) );
} );

/* ---------- Create-your-planner page ---------- */
add_shortcode( 'sr_planner', function ( $atts ) {
	$atts  = shortcode_atts( array( 'product' => 'moon' ), $atts );
	$prods = sr_pl_products();
	$slug  = isset( $prods[ $atts['product'] ] ) ? $atts['product'] : 'moon';
	$p     = $prods[ $slug ];
	$pre   = $p['pre'];
	$order_id = isset( $_GET[ $pre . '_order' ] ) ? absint( $_GET[ $pre . '_order' ] ) : 0;
	$key      = isset( $_GET[ $pre . '_key' ] ) ? sanitize_text_field( wp_unslash( $_GET[ $pre . '_key' ] ) ) : '';
	$access   = sr_pl_access( $p, $order_id, $key );
	if ( ! $access ) {
		$url   = get_permalink( $p['id'] );
		$price = '';
		if ( function_exists( 'wc_get_product' ) && ( $prod = wc_get_product( $p['id'] ) ) ) { $price = wp_strip_all_tags( wc_price( $prod->get_price() ) ); }
		return '<div style="max-width:640px;margin:1.5rem auto;border:1px solid #dccdf3;border-top:6px solid #4b2a7b;border-radius:4px;padding:1.6rem;text-align:center;background:#fff">'
			. '<p style="font-style:italic;font-size:1.3rem;margin:0 0 .6rem;color:#4b2a7b">Your ' . esc_html( $p['name'] ) . ' is waiting</p>'
			. '<p style="margin:0 0 1.1rem">This page creates your personal planner after purchase. Already bought it? Use the link in your order confirmation email, or log in to your account.</p>'
			. '<a href="' . esc_url( $url ) . '" style="display:inline-block;background:#4b2a7b;color:#fff;padding:.8rem 1.4rem;border-radius:3px;text-decoration:none">Get My ' . esc_html( $p['name'] ) . ( $price ? ' · ' . esc_html( $price ) : '' ) . '</a></div>';
	}
	$saved = is_a( $access, 'WC_Order' ) ? $access->get_meta( '_sr_pl_details_' . $slug ) : null;
	$months = sr_pl_months();
	$cfg = wp_json_encode( array(
		'endpoint' => esc_url_raw( rest_url( 'sr11pl/v1/create' ) ),
		'places'   => esc_url_raw( rest_url( 'sr11bc/v1/places' ) ),
		'nonce'    => wp_create_nonce( 'wp_rest' ),
		'order'    => $order_id,
		'key'      => $key,
		'product'  => $slug,
		'pre'      => $pre,
		'saved'    => is_array( $saved ) ? true : false,
	) );
	$opts = '';
	foreach ( $months as $val => $label ) { $opts .= '<option value="' . esc_attr( $val ) . '">' . esc_html( $label ) . '</option>'; }
	ob_start(); ?>
<style>
.sr-plf{--p:#4b2a7b;--p2:#6d5a8c;--l:#efe7fb;--l2:#dccdf3;--ink:#2e2340;color:var(--ink);max-width:680px;margin:0 auto}
.sr-plf .card{background:#fff;border:1px solid var(--l2);border-top:6px solid var(--p);border-radius:4px;padding:1.5rem;margin:0 0 1.6rem}
.sr-plf h2{font-family:"Cormorant Garamond",Georgia,serif;color:var(--p);margin:0 0 .5rem;font-size:1.7rem;font-weight:600}
.sr-plf .grid{display:grid;grid-template-columns:1fr 1fr;gap:0 1rem}
.sr-plf label{display:block;font-weight:600;color:var(--p);margin:0 0 1rem;font-size:.92rem}
.sr-plf input[type=text],.sr-plf input[type=date],.sr-plf input[type=time],.sr-plf select{display:block;width:100%;box-sizing:border-box;margin-top:.35rem;padding:.7rem .8rem;border:1px solid var(--l2);border-radius:3px;font-size:1rem;color:var(--ink);background:#fff}
.sr-plf .city{position:relative;display:block}
.sr-plf .sugg{position:absolute;left:0;right:0;top:100%;z-index:20;background:#fff;border:1px solid var(--l2);border-radius:3px;max-height:260px;overflow:auto;box-shadow:0 6px 18px rgba(75,42,123,.12)}
.sr-plf .sugg button{display:block;width:100%;text-align:left;background:#fff;border:0;border-bottom:1px solid var(--l);padding:.6rem .8rem;font-size:.95rem;color:var(--ink);cursor:pointer}
.sr-plf .sugg button:hover{background:var(--l)}
.sr-plf .go{display:inline-block;background:var(--p);color:#fff !important;border:0;border-radius:3px;padding:.85rem 1.5rem;font-size:1rem;cursor:pointer;text-decoration:none}
.sr-plf .go[disabled]{opacity:.6;cursor:wait}
.sr-plf .msg{margin:1rem 0 0;padding:.8rem 1rem;border-radius:3px;background:var(--l)}
.sr-plf .msg.err{background:#fdecec;color:#7a1f1f}
.sr-plf .fine{font-size:.85rem;color:var(--p2);margin-top:1rem}
.sr-plf p{font-size:1.05rem;line-height:1.7}
@media(max-width:600px){.sr-plf .grid{grid-template-columns:1fr}.sr-plf .card{padding:1.1rem}}
</style>
<div id="sr-<?php echo esc_attr( $pre ); ?>-app" class="sr-plf">
<div class="card">
<h2>Create Your <?php echo esc_html( $p['name'] ); ?></h2>
<p>Enter the birth details for the person this planner is for, the city they live in now, and the month the planner should begin. It's created in seconds and downloads as a PDF you can print or use in GoodNotes. A copy is emailed to you too.</p>
<?php if ( is_array( $saved ) ) : ?><p class="fine">Your planner has been created before. Each planner is for one person, so you can correct the birth details once if there was a typo. After that, this page re-creates your saved planner.</p><?php endif; ?>
<form id="<?php echo esc_attr( $pre ); ?>-form" novalidate>
<div class="grid">
<label for="<?php echo esc_attr( $pre ); ?>-name">First name (shown on the planner)<input id="<?php echo esc_attr( $pre ); ?>-name" type="text" maxlength="60" autocomplete="given-name"></label>
<label for="<?php echo esc_attr( $pre ); ?>-city">Birth city<span class="city"><input id="<?php echo esc_attr( $pre ); ?>-city" type="text" autocomplete="off" placeholder="Start typing, then choose from the list"><span class="sugg" id="<?php echo esc_attr( $pre ); ?>-city-s" hidden></span></span></label>
<label for="<?php echo esc_attr( $pre ); ?>-date">Birth date<input id="<?php echo esc_attr( $pre ); ?>-date" type="date" min="1800-01-01" max="<?php echo esc_attr( current_time( 'Y-m-d' ) ); ?>" required></label>
<label for="<?php echo esc_attr( $pre ); ?>-time">Birth time (local)<input id="<?php echo esc_attr( $pre ); ?>-time" type="time" required></label>
<label for="<?php echo esc_attr( $pre ); ?>-now">City you live in now<span class="city"><input id="<?php echo esc_attr( $pre ); ?>-now" type="text" autocomplete="off" placeholder="Used for the dates and times in your planner"><span class="sugg" id="<?php echo esc_attr( $pre ); ?>-now-s" hidden></span></span></label>
<label for="<?php echo esc_attr( $pre ); ?>-start">Start my planner in<select id="<?php echo esc_attr( $pre ); ?>-start"><?php echo $opts; // escaped above ?></select></label>
</div>
<button class="go" id="<?php echo esc_attr( $pre ); ?>-go" type="submit">Create My Planner</button>
<div id="<?php echo esc_attr( $pre ); ?>-msg" class="msg" hidden></div>
</form>
<div id="<?php echo esc_attr( $pre ); ?>-cal" class="card" style="margin-top:1.2rem;border-top-color:#4e8b5f" hidden>
<h2>Add Your Dates to Your Calendar</h2>
<p><a class="go" id="<?php echo esc_attr( $pre ); ?>-ics" href="#">Add My Dates to My Calendar</a></p>
<?php echo sr_pl_cal_steps_html(); // static markup ?>
<p class="fine">Your calendar file is in your email too.</p>
</div>
<p class="fine">Your details are used only to create your planner. Because this is an instant digital download, all sales are final.</p>
</div>
</div>
<script data-jetpack-boost="ignore">
(function(){
  var C = <?php echo $cfg; ?>, P = C.pre, $ = function(id){ return document.getElementById(P + '-' + id); }, birth = null, now = null, busy = false;
  function msg(t, err, html){ var m=$('msg'); m.hidden=!t; m.className='msg'+(err?' err':''); if(html){m.innerHTML=t;}else{m.textContent=t||'';} }
  function city(inputId, onPick){
    var inp=$(inputId), box=$(inputId+'-s'), timer=null;
    inp.addEventListener('input', function(){ inp.sr11Place=null; onPick(null); clearTimeout(timer); var q=inp.value.trim(); if(q.length<2){box.hidden=true;return;}
      timer=setTimeout(function(){ fetch(C.places+'?q='+encodeURIComponent(q),{headers:{'X-SR11-Request':'1'}}).then(function(r){return r.json();}).then(function(j){
        box.innerHTML=''; var res=(j&&j.results)||[]; if(!res.length){ box.innerHTML='<button type="button" disabled>No matches yet. Try the city name only.</button>'; box.hidden=false; return; }
        res.slice(0,8).forEach(function(p){ var b=document.createElement('button'); b.type='button'; b.textContent=p.label;
          b.addEventListener('click', function(){ inp.sr11Place={tz:p.tz,cc:p.country_code}; onPick(p); inp.value=p.label; box.hidden=true; }); box.appendChild(b); });
        box.hidden=false; }).catch(function(){ box.hidden=true; }); }, 250); });
    document.addEventListener('click', function(e){ if(!box.contains(e.target) && e.target!==inp) box.hidden=true; });
  }
  city('city', function(p){ birth=p; });
  city('now', function(p){ now=p; });
  function zone(){ if(window.SR11Chart){ SR11Chart.attachRecordZone($('city'), function(){ return $('date').value; }); } }
  if (window.SR11Chart) { zone(); } else { window.addEventListener('load', zone); }
  function body(extra){
    var d=$('date').value.split('-'), t=$('time').value.split(':');
    var b={ product:C.product, order:C.order, key:C.key, name:$('name').value.trim(), year:+d[0], month:+d[1], day:+d[2], hour:+t[0], minute:+t[1],
      location:{ mode:'place', place_id:birth.id }, current_place_id:now.id, start:$('start').value };
    if (window.SR11Chart) b = SR11Chart.withRecordOffset(b, $('city'));
    for (var k in (extra||{})) b[k]=extra[k];
    return b;
  }
  function send(extra){
    busy=true; $('go').disabled=true; msg('Reading your chart and building your planner. This takes a few seconds....');
    fetch(C.endpoint, { method:'POST', credentials:'same-origin', headers:{ 'Content-Type':'application/json', 'X-SR11-Request':'1', 'X-WP-Nonce':C.nonce }, body:JSON.stringify(body(extra)) })
    .then(function(r){ return r.json().then(function(j){ return { s:r.status, j:j }; }); })
    .then(function(x){
      busy=false; $('go').disabled=false; var j=x.j||{};
      if (x.s===200 && j.pdf) {
        var bin=atob(j.pdf), bytes=new Uint8Array(bin.length); for (var i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i);
        var url=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'})), fn=j.filename||'Planner.pdf';
        var a=document.createElement('a'); a.href=url; a.download=fn; document.body.appendChild(a); a.click(); setTimeout(function(){ a.remove(); }, 4000);
        if (j.ics) {
          var ib=atob(j.ics), iby=new Uint8Array(ib.length); for (var q=0;q<ib.length;q++) iby[q]=ib.charCodeAt(q);
          var iu=URL.createObjectURL(new Blob([iby],{type:'text/calendar'})), il=$('ics'); il.href=iu; il.setAttribute('download', j.ics_filename||'Planner-Calendar.ics');
          $('cal').hidden=false;
        }
        msg((j.note ? j.note + ' ' : '') + 'Your planner is ready and should download automatically. If it didn\'t start, <a href="'+url+'" download="'+fn+'">tap here to download it</a>. A copy is on its way to your email too.', false, true);
        return;
      }
      if (j.status==='ambiguous') {
        msg('That birth time happened twice on that date because the clocks went back. Choose which one: <button type="button" class="go" id="'+P+'-f0" style="padding:.4rem .8rem;margin:.4rem .3rem 0 0">The first one</button><button type="button" class="go" id="'+P+'-f1" style="padding:.4rem .8rem;margin-top:.4rem">The second one</button>', false, true);
        $('f0').onclick=function(){ send({fold:0}); }; $('f1').onclick=function(){ send({fold:1}); }; return;
      }
      if (j.status==='needs_confirmation') { send({accept_lmt:true}); return; }
      msg(j.message || 'Something went wrong creating your planner. Please try again in a minute.', true);
    })
    .catch(function(){ busy=false; $('go').disabled=false; msg('We could not reach the planner service. Please check your connection and try again.', true); });
  }
  $('form').addEventListener('submit', function(e){
    e.preventDefault(); if (busy) return;
    if (!$('date').value) { msg('Please enter the birth date.', true); return; }
    if (!$('time').value) { msg('Please enter the birth time. Your planner reads the houses of your chart, so it needs one.', true); return; }
    if (!birth) { msg('Please start typing the birth city and choose it from the list.', true); return; }
    if (!now) { msg('Please start typing the city you live in now and choose it from the list.', true); return; }
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
	foreach ( sr_pl_products() as $p ) {
		if ( ! sr_pl_order_has( $order, $p['id'] ) ) { continue; }
		echo '<div style="border:1px solid #dccdf3;border-top:6px solid #4b2a7b;border-radius:4px;padding:1.4rem;margin:0 0 1.5rem;text-align:center;background:#fff">'
			. '<p style="font-style:italic;font-size:1.3rem;margin:0 0 .5rem;color:#4b2a7b">Your ' . esc_html( $p['name'] ) . ' is ready to create</p>'
			. '<p style="margin:0 0 1rem">Click below, enter your birth details, the city you live in now and the month you want your planner to begin, and it is created in seconds. I have also emailed you this link so you can come back anytime.</p>'
			. '<a href="' . esc_url( sr_pl_url( $order, $p ) ) . '" style="display:inline-block;background:#4b2a7b;color:#fff;padding:.8rem 1.4rem;border-radius:3px;text-decoration:none">Create My Planner</a></div>';
	}
}, 5 );

add_action( 'woocommerce_email_after_order_table', function ( $order, $sent_to_admin, $plain_text, $email = null ) {
	if ( $sent_to_admin ) { return; }
	foreach ( sr_pl_products() as $p ) {
		if ( ! sr_pl_order_has( $order, $p['id'] ) ) { continue; }
		$url = sr_pl_url( $order, $p );
		if ( $plain_text ) {
			echo PHP_EOL . 'Create your ' . esc_html( $p['name'] ) . ': ' . esc_url_raw( $url ) . PHP_EOL;
			continue;
		}
		echo '<p style="margin:16px 0"><strong>Your ' . esc_html( $p['name'] ) . '</strong><br>Create your personal planner anytime here: <a href="' . esc_url( $url ) . '">Create My Planner</a></p>';
	}
}, 10, 4 );
