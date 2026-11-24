<?php
/**
 * Push elementor/build/*.json into WordPress: theme templates, EN + ID pages (linked in Polylang),
 * one Contact Form 7 form per language and the header/footer menus per language.
 * Idempotent: documents are matched by _shcp_doc meta (fallback: page slug).
 *
 * Run: python3 -I elementor/build.py && scripts/wp eval-file "$PWD/scripts/push-elementor.php" --user=admin
 * (--user is required: Elementor silently skips saving without an editor-capable user.)
 *
 * Note: overwrites the Elementor layout of every generated document. Edits made in the
 * Elementor editor are lost on the next push, so stop pushing once hand-editing starts.
 */

use Elementor\Plugin;

$root = dirname( __DIR__ );
$site = json_decode( file_get_contents( "$root/elementor/build/site.json" ), true );
$docs = array();
foreach ( glob( "$root/elementor/build/*.json" ) as $file ) {
	if ( 'site.json' !== basename( $file ) ) {
		$doc                 = json_decode( file_get_contents( $file ), true );
		$docs[ $doc['key'] ] = $doc;
	}
}
// Templates first: pages reference them.
uasort( $docs, fn( $a, $b ) => ( 'page' === $a['type'] ) <=> ( 'page' === $b['type'] ) );

function shcp_find( $doc ) {
	$ids = get_posts( array( 'post_type' => array( 'page', 'elementor_library' ), 'post_status' => 'any', 'meta_key' => '_shcp_doc', 'meta_value' => $doc['key'], 'fields' => 'ids', 'numberposts' => 1, 'lang' => '' ) );
	if ( ! $ids && 'page' === $doc['type'] ) {
		$ids = get_posts( array( 'post_type' => 'page', 'name' => $doc['slug'], 'post_status' => 'any', 'fields' => 'ids', 'numberposts' => 1, 'lang' => '' ) );
	}
	return $ids ? $ids[0] : 0;
}

function shcp_contact_form( $lang, $spec ) {
	$existing = get_posts( array( 'post_type' => 'wpcf7_contact_form', 'title' => $spec['title'], 'fields' => 'ids', 'numberposts' => 1 ) );
	$form     = $existing ? WPCF7_ContactForm::get_instance( $existing[0] ) : WPCF7_ContactForm::get_template( array( 'title' => $spec['title'], 'locale' => 'en' === $lang ? 'en_US' : 'id_ID' ) );
	$id_lang  = 'id' === $lang;
	$form->set_properties( array(
		'form'   => $spec['form'],
		'mail'   => array(
			'active'             => true,
			'subject'            => '[_site_title] [inquiry] inquiry from [full-name]',
			'sender'             => '[_site_title] <wordpress@[_site_domain]>',
			'recipient'          => '[_site_admin_email]',
			'body'               => "Name: [full-name]\nCompany: [company]\nEmail: [your-email]\nPhone: [phone]\nInquiry: [inquiry]\nLanguage: " . strtoupper( $lang ) . "\n\n[your-message]",
			'additional_headers' => 'Reply-To: [your-email]',
			'attachments'        => '',
			'use_html'           => false,
			'exclude_blank'      => false,
		),
		// Copy to the visitor, promised by the success message.
		'mail_2' => array(
			'active'             => true,
			'subject'            => $id_lang ? 'Kami telah menerima permintaan Anda – SHCP' : 'We received your request – SHCP',
			'sender'             => '[_site_title] <wordpress@[_site_domain]>',
			'recipient'          => '[your-email]',
			'body'               => ( $id_lang
				? "Halo [full-name],\n\nTerima kasih telah menghubungi SHCP. Tim kami akan membalas dari enquiry@shcp.com.sg.\n\nRingkasan permintaan Anda:\n"
				: "Hi [full-name],\n\nThank you for contacting SHCP. Our team will reply from enquiry@shcp.com.sg.\n\nYour request:\n" )
				. "[inquiry]\n[your-message]\n\nSingapore Highpolymer Chemical Products Pte Ltd",
			'additional_headers' => 'Reply-To: enquiry@shcp.com.sg',
			'attachments'        => '',
			'use_html'           => false,
			'exclude_blank'      => false,
		),
	) );
	return $form->save();
}

$ids = array();
foreach ( $site['forms'] as $lang => $spec ) {
	$ids[ "cf7:$lang" ] = shcp_contact_form( $lang, $spec );
}
foreach ( get_terms( array( 'taxonomy' => 'product_line', 'hide_empty' => false, 'lang' => '' ) ) as $term ) {
	$ids[ "term:{$term->slug}" ] = $term->term_id;
}

// Create missing documents first so {{doc:*}} references resolve.
foreach ( $docs as $key => $doc ) {
	$id = shcp_find( $doc );
	if ( ! $id ) {
		$type     = 'page' === $doc['type'] ? 'wp-page' : $doc['type'];
		$document = Plugin::$instance->documents->create( $type, array(
			'post_title'  => $doc['title'],
			'post_name'   => $doc['slug'] ?? '',
			'post_status' => 'publish',
		) );
		$id = $document->get_main_id();
		WP_CLI::log( "created $key #$id" );
	}
	update_post_meta( $id, '_shcp_doc', $key );
	$ids[ "doc:$key" ] = $id;
}

$groups = array();
foreach ( $docs as $key => $doc ) {
	$raw = preg_replace_callback( '/\{\{([a-z0-9:@-]+)\}\}/', function ( $m ) use ( $ids, $key ) {
		if ( ! isset( $ids[ $m[1] ] ) ) {
			WP_CLI::error( "$key: unknown placeholder {$m[1]}" );
		}
		return (string) $ids[ $m[1] ];
	}, wp_json_encode( $doc['data'] ) );
	$id = $ids[ "doc:$key" ];

	if ( 'page' === $doc['type'] ) {
		wp_update_post( array( 'ID' => $id, 'post_title' => $doc['title'], 'post_name' => $doc['slug'] ) );
		update_post_meta( $id, '_wp_page_template', 'elementor_header_footer' );
		pll_set_post_language( $id, $doc['lang'] );
		$groups[ $doc['group'] ][ $doc['lang'] ] = $id;
	}
	Plugin::$instance->documents->get( $id, false )->save( array( 'elements' => json_decode( $raw, true ) ) );
	wp_update_post( array( 'ID' => $id, 'post_status' => 'publish' ) );
	if ( $doc['conditions'] ) {
		update_post_meta( $id, '_elementor_conditions', $doc['conditions'] );
	}
	WP_CLI::log( "saved $key #$id" );
}
foreach ( $groups as $translations ) {
	pll_save_post_translations( $translations );
}

// Menus per language; Polylang assigns them to the theme locations.
$opt = PLL()->options;
$nav = $opt['nav_menus'];
foreach ( $site['menus'] as $lang => $labels ) {
	$pages = array( $groups['about'][ $lang ], $groups['products'][ $lang ], $groups['applications'][ $lang ], $groups['contact'][ $lang ] );
	foreach ( array( 'shcp-primary' => 'Header', 'shcp-footer' => 'Footer' ) as $loc => $prefix ) {
		$name = "$prefix " . strtoupper( $lang );
		$menu = wp_get_nav_menu_object( $name );
		if ( $menu ) {
			wp_delete_nav_menu( $menu->term_id );
		}
		$mid = wp_create_nav_menu( $name );
		if ( 'shcp-primary' === $loc ) {
			wp_update_nav_menu_item( $mid, 0, array(
				'menu-item-title'     => $site['menu_home'][ $lang ],
				'menu-item-object'    => 'page',
				'menu-item-object-id' => $groups['home'][ $lang ],
				'menu-item-type'      => 'post_type',
				'menu-item-status'    => 'publish',
				'menu-item-classes'   => 'shcp-menu-home',
			) );
		}
		foreach ( $labels as $i => $label ) {
			wp_update_nav_menu_item( $mid, 0, array(
				'menu-item-title'     => $label,
				'menu-item-object'    => 'page',
				'menu-item-object-id' => $pages[ $i ],
				'menu-item-type'      => 'post_type',
				'menu-item-status'    => 'publish',
				'menu-item-classes'   => ( 'shcp-primary' === $loc && 3 === $i ) ? 'shcp-menu-cta' : '',
			) );
		}
		$nav[ get_stylesheet() ][ $loc ][ $lang ] = $mid;
	}
}
$opt['nav_menus'] = $nav;
$opt->save();

// Hero slides: seed only while empty so slides edited in WP admin survive later pushes.
foreach ( $site['hero_slides'] as $lang => $slides ) {
	if ( ! get_field( 'hero_slides', $groups['home'][ $lang ] ) ) {
		update_field( 'field_shcp_hero_slides', $slides, $groups['home'][ $lang ] );
		WP_CLI::log( "seeded hero slides ($lang)" );
	}
}

// Footer fields: seed the built-in text only while a field is empty, so edits made in WP admin survive later pushes.
$footer_keys = array(
	'footer_email' => 'field_shcp_footer_email', 'footer_tel' => 'field_shcp_footer_tel', 'footer_fax' => 'field_shcp_footer_fax',
	'footer_company_en' => 'field_shcp_footer_company_en', 'footer_address_en' => 'field_shcp_footer_address_en', 'footer_about_en' => 'field_shcp_footer_about_en',
	'footer_company_id' => 'field_shcp_footer_company_id', 'footer_address_id' => 'field_shcp_footer_address_id', 'footer_about_id' => 'field_shcp_footer_about_id',
);
foreach ( shcp_footer_defaults() as $name => $default ) {
	if ( '' === trim( (string) get_field( $name, 'option' ) ) ) {
		update_field( $footer_keys[ $name ], $default, 'option' );
	}
}

\ElementorPro\Plugin::instance()->modules_manager->get_modules( 'theme-builder' )->get_conditions_manager()->get_cache()->regenerate();
update_option( 'show_on_front', 'page' );
update_option( 'page_on_front', $groups['home']['en'] );
PLL()->model->clean_languages_cache();
Plugin::$instance->files_manager->clear_cache();
flush_rewrite_rules();
WP_CLI::success( 'pushed ' . count( $docs ) . ' documents' );
