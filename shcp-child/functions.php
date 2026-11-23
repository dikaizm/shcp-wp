<?php
/**
 * SHCP child theme: application post type, ACF fields and shortcodes used by the Elementor templates.
 */

defined( 'ABSPATH' ) || exit;

add_action( 'wp_enqueue_scripts', function () {
	$ver = wp_get_theme()->get( 'Version' );
	wp_enqueue_style( 'shcp', get_stylesheet_uri(), array( 'hello-elementor' ), $ver );
	wp_enqueue_script( 'shcp', get_stylesheet_directory_uri() . '/assets/site.js', array(), $ver, array( 'strategy' => 'defer' ) );
} );

// Labels used inside templates shared by both languages.
function shcp_t( $key ) {
	$strings = array(
		'learn_more'   => array( 'en' => 'Learn More', 'id' => 'Selengkapnya' ),
		'detail_other' => array( 'en' => 'Explore Other Applications', 'id' => 'Lihat Aplikasi Lainnya' ),
		'detail_quote' => array( 'en' => 'Get Product Quotation', 'id' => 'Minta Penawaran Harga' ),
		'footer_about' => array(
			'en' => 'SHCP manufactures Unsaturated Polyester and Alkyd Resins in Singapore and Indonesia, also supplies a complete range of FRP materials. SHCP has been serving industrial customers since 1974.',
			'id' => 'SHCP memproduksi Unsaturated Polyester Resin dan Alkyd Resin di Singapura dan Indonesia, serta memasok rangkaian lengkap material FRP. SHCP telah melayani pelanggan industri sejak 1974.',
		),
	);
	$lang = function_exists( 'pll_current_language' ) ? pll_current_language() : 'en';
	return $strings[ $key ][ $lang ] ?? $strings[ $key ]['en'] ?? '';
}

// Link to a page in the current language, by its English slug.
function shcp_page_url( $en_slug ) {
	$page = get_page_by_path( $en_slug );
	$id   = $page && function_exists( 'pll_get_post' ) ? ( pll_get_post( $page->ID ) ?: $page->ID ) : ( $page->ID ?? 0 );
	return $id ? get_permalink( $id ) : home_url( '/' );
}

// [shcp_t key=footer_about]
add_shortcode( 'shcp_t', fn( $atts ) => '<p class="shcp-t">' . esc_html( shcp_t( $atts['key'] ?? '' ) ) . '</p>' );

// [shcp_btn key=learn_more href=#details icon=down]
add_shortcode( 'shcp_btn', function ( $atts ) {
	$atts = shortcode_atts( array( 'key' => '', 'href' => '#', 'icon' => 'right', 'style' => '' ), $atts );
	return sprintf( '<a class="shcp-btn %s" href="%s">%s<i class="shcp-btn__icon shcp-btn__icon--%s" aria-hidden="true"></i></a>',
		esc_attr( $atts['style'] ), esc_url( $atts['href'] ), esc_html( shcp_t( $atts['key'] ) ), esc_attr( $atts['icon'] ) );
} );

// [shcp_detail_buttons] bottom buttons of the application detail template.
add_shortcode( 'shcp_detail_buttons', function () {
	return '<div class="shcp-detail-buttons">'
		. sprintf( '<a class="shcp-btn shcp-btn--outline" href="%s">%s</a>', esc_url( shcp_page_url( 'applications' ) ), esc_html( shcp_t( 'detail_other' ) ) )
		. sprintf( '<a class="shcp-btn" href="%s">%s<i class="shcp-btn__icon shcp-btn__icon--right" aria-hidden="true"></i></a>', esc_url( shcp_page_url( 'contact-us' ) . '#form' ), esc_html( shcp_t( 'detail_quote' ) ) )
		. '</div>';
} );

add_action( 'after_setup_theme', function () {
	register_nav_menus( array(
		'shcp-primary' => 'Header menu',
		'shcp-footer'  => 'Footer menu',
	) );
} );

// [shcp_menu location="shcp-primary"] menu by location, so Polylang can swap it per language.
add_shortcode( 'shcp_menu', function ( $atts ) {
	$atts = shortcode_atts( array( 'location' => 'shcp-primary' ), $atts );
	return wp_nav_menu( array(
		'theme_location' => $atts['location'],
		'container'      => 'nav',
		'container_class' => 'shcp-menu shcp-menu--' . sanitize_html_class( $atts['location'] ),
		'fallback_cb'    => '__return_empty_string',
		'depth'          => 1,
		'echo'           => false,
	) );
} );

add_action( 'init', function () {
	register_post_type( 'application', array(
		'label'        => 'Applications',
		'labels'       => array(
			'singular_name' => 'Application',
			'add_new'       => 'Add Application',
			'add_new_item'  => 'Add New Application',
			'edit_item'     => 'Edit Application',
			'all_items'     => 'All Applications',
		),
		'public'       => true,
		'has_archive'  => false,
		'rewrite'      => array( 'slug' => 'applications' ),
		'menu_icon'    => 'dashicons-screenoptions',
		'supports'     => array( 'title', 'thumbnail', 'page-attributes' ),
		// Classic edit screen: title, featured image and the fields below. Simpler than the block editor for editors.
		'show_in_rest' => false,
	) );

	register_taxonomy( 'product_line', 'application', array(
		'label'             => 'Product lines',
		'hierarchical'      => true,
		'show_admin_column' => true,
		'show_in_rest'      => true,
		'rewrite'           => array( 'slug' => 'product-line' ),
	) );
} );

add_action( 'acf/include_fields', function () {
	acf_add_local_field_group( array(
		'key'      => 'group_shcp_application',
		'title'    => 'Application details',
		'location' => array( array( array( 'param' => 'post_type', 'operator' => '==', 'value' => 'application' ) ) ),
		'fields'   => array(
			array( 'key' => 'field_shcp_intro', 'name' => 'intro', 'label' => 'Hero intro', 'type' => 'textarea', 'rows' => 4 ),
			array(
				'key'          => 'field_shcp_benefits',
				'name'         => 'benefits',
				'label'        => 'Benefits',
				'type'         => 'repeater',
				'layout'       => 'table',
				'button_label' => 'Add benefit',
				'sub_fields'   => array(
					array( 'key' => 'field_shcp_benefit_title', 'name' => 'title', 'label' => 'Title', 'type' => 'text' ),
					array( 'key' => 'field_shcp_benefit_text', 'name' => 'text', 'label' => 'Text', 'type' => 'textarea', 'rows' => 3 ),
				),
			),
			array(
				'key'          => 'field_shcp_sections',
				'name'         => 'spec_sections',
				'label'        => 'Specification sections',
				'instructions' => 'Tables are managed under TablePress (CSV/Excel import, add rows/columns). A section without heading renders its table directly; with a heading it becomes a collapsible block.',
				'type'         => 'repeater',
				'layout'       => 'block',
				'button_label' => 'Add section',
				'sub_fields'   => array(
					array( 'key' => 'field_shcp_section_heading', 'name' => 'heading', 'label' => 'Heading', 'type' => 'text' ),
					array( 'key' => 'field_shcp_section_text', 'name' => 'text', 'label' => 'Description', 'type' => 'textarea', 'rows' => 2 ),
					array(
						'key'          => 'field_shcp_section_tabs',
						'name'         => 'tabs',
						'label'        => 'Variant tabs',
						'instructions' => 'One row per tab. A tab without a table shows greyed out. Use a single row with no label for an untabbed table.',
						'type'         => 'repeater',
						'layout'       => 'table',
						'button_label' => 'Add tab',
						'sub_fields'   => array(
							array( 'key' => 'field_shcp_tab_label', 'name' => 'label', 'label' => 'Tab label', 'type' => 'text' ),
							array( 'key' => 'field_shcp_tab_table', 'name' => 'table', 'label' => 'Table', 'type' => 'select', 'allow_null' => 1, 'ui' => 1, 'choices' => array() ),
						),
					),
				),
			),
		),
	) );
} );

// Tab "Table" dropdown lists TablePress tables.
add_filter( 'acf/load_field/key=field_shcp_tab_table', function ( $field ) {
	if ( class_exists( 'TablePress' ) ) {
		foreach ( TablePress::$model_table->load_all( false ) as $id ) {
			$table                    = TablePress::$model_table->load( $id, false, false );
			$field['choices'][ $id ] = "#$id " . ( $table['name'] ?? '' );
		}
	}
	return $field;
} );

// New TablePress tables start styled for this site: no DataTables JS, no zebra/hover.
add_filter( 'tablepress_table_template', function ( $table ) {
	$table['options']['use_datatables']         = false;
	$table['options']['alternating_row_colors'] = false;
	$table['options']['row_hover']              = false;
	$table['options']['print_name']             = false;
	return $table;
} );

// [shcp_lang] Eng / Ind pill switcher.
add_shortcode( 'shcp_lang', function () {
	if ( ! function_exists( 'pll_the_languages' ) ) {
		return '';
	}
	$labels = array( 'en' => 'Eng', 'id' => 'Ind' );
	$out    = '';
	foreach ( pll_the_languages( array( 'raw' => 1, 'hide_if_empty' => 0, 'hide_if_no_translation' => 0 ) ) as $lang ) {
		$out .= sprintf(
			'<a href="%s" class="%s" lang="%s">%s</a>',
			esc_url( $lang['url'] ),
			$lang['current_lang'] ? 'is-current' : '',
			esc_attr( $lang['locale'] ),
			esc_html( $labels[ $lang['slug'] ] ?? $lang['name'] )
		);
	}
	return '<nav class="shcp-lang" aria-label="Language">' . $out . '</nav>';
} );

// [shcp_benefits] benefit columns of the current application.
add_shortcode( 'shcp_benefits', function () {
	$out = '';
	foreach ( get_field( 'benefits' ) ?: array() as $b ) {
		$out .= '<div><h3>' . esc_html( $b['title'] ) . '</h3><p>' . esc_html( $b['text'] ) . '</p></div>';
	}
	return $out ? '<div class="shcp-benefits">' . $out . '</div>' : '';
} );

function shcp_render_table( $id ) {
	return $id ? do_shortcode( '[table id=' . absint( $id ) . ' use_datatables=false /]' ) : '';
}

// [shcp_spec] spec sections: optional collapsible heading, description, variant tabs of TablePress tables.
add_shortcode( 'shcp_spec', function () {
	$out = '';
	foreach ( get_field( 'spec_sections' ) ?: array() as $n => $section ) {
		$tabs = $section['tabs'] ?: array();
		$body = $section['text'] ? '<p class="shcp-spec-text">' . esc_html( $section['text'] ) . '</p>' : '';

		if ( 1 === count( $tabs ) && '' === trim( (string) $tabs[0]['label'] ) ) {
			$body .= '<div class="shcp-spec-panel">' . shcp_render_table( $tabs[0]['table'] ) . '</div>';
		} elseif ( $tabs ) {
			$current = null;
			foreach ( $tabs as $i => $tab ) {
				if ( null === $current && $tab['table'] ) {
					$current = $i;
				}
			}
			$body .= '<div class="shcp-spec-tabs" role="tablist">';
			foreach ( $tabs as $i => $tab ) {
				$body .= sprintf(
					'<button type="button" role="tab" aria-selected="%s"%s>%s</button>',
					$i === $current ? 'true' : 'false',
					$tab['table'] ? '' : ' disabled',
					esc_html( $tab['label'] )
				);
			}
			$body .= '</div>';
			foreach ( $tabs as $i => $tab ) {
				if ( $tab['table'] ) {
					$body .= sprintf( '<div class="shcp-spec-panel" role="tabpanel"%s>%s</div>', $i === $current ? '' : ' hidden', shcp_render_table( $tab['table'] ) );
				} else {
					$body .= '<div class="shcp-spec-panel" role="tabpanel" hidden></div>';
				}
			}
		}

		if ( $section['heading'] ) {
			$out .= sprintf( '<details class="shcp-spec"%s><summary>%s</summary>%s</details>', $n ? '' : ' open', esc_html( $section['heading'] ), $body );
		} else {
			$out .= '<div class="shcp-spec">' . $body . '</div>';
		}
	}
	return $out ? '<div class="shcp-specs">' . $out . '</div>' : '';
} );

// Our CF7 markup is laid out with CSS grid; auto <p>/<br> would break it.
add_filter( 'wpcf7_autop_or_not', '__return_false' );

// Homepage hero carousel: "Hero slides" repeater on the Home page (one per language via Polylang).
add_action( 'acf/include_fields', function () {
	acf_add_local_field_group( array(
		'key'      => 'group_shcp_hero',
		'title'    => 'Hero slides',
		'location' => array( array( array( 'param' => 'page_type', 'operator' => '==', 'value' => 'front_page' ) ) ),
		'position' => 'acf_after_title',
		'fields'   => array(
			array(
				'key'          => 'field_shcp_hero_slides',
				'name'         => 'hero_slides',
				'label'        => 'Slides',
				'instructions' => 'Slides rotate every 6 seconds. Drag rows to reorder. Background: wide photo (1920x720 or larger). Person: transparent PNG cut-out, square.',
				'type'         => 'repeater',
				'layout'       => 'block',
				'collapsed'    => 'field_shcp_slide_title',
				'button_label' => 'Add slide',
				'sub_fields'   => array(
					array( 'key' => 'field_shcp_slide_title', 'name' => 'title', 'label' => 'Title', 'type' => 'text', 'required' => 1 ),
					array( 'key' => 'field_shcp_slide_text', 'name' => 'text', 'label' => 'Text', 'type' => 'textarea', 'rows' => 3 ),
					array( 'key' => 'field_shcp_slide_button', 'name' => 'button', 'label' => 'Button', 'type' => 'link', 'instructions' => 'Leave empty for no button. Links starting with # scroll down the page.' ),
					array( 'key' => 'field_shcp_slide_bg', 'name' => 'background', 'label' => 'Background photo', 'type' => 'image', 'return_format' => 'id', 'required' => 1, 'wrapper' => array( 'width' => 50 ) ),
					array( 'key' => 'field_shcp_slide_person', 'name' => 'person', 'label' => 'Person cut-out', 'type' => 'image', 'return_format' => 'id', 'wrapper' => array( 'width' => 50 ) ),
				),
			),
		),
	) );
} );

// The Indonesian home page is the front page's translation, not page_on_front itself.
add_filter( 'acf/location/rule_match/page_type', function ( $match, $rule, $screen ) {
	if ( 'front_page' !== $rule['value'] || empty( $screen['post_id'] ) || ! function_exists( 'pll_get_post_translations' ) ) {
		return $match;
	}
	$is = in_array( (int) $screen['post_id'], array_map( 'intval', pll_get_post_translations( (int) get_option( 'page_on_front' ) ) ), true );
	return '==' === $rule['operator'] ? $is : ! $is;
}, 10, 3 );

// [shcp_hero_slider]
add_shortcode( 'shcp_hero_slider', function () {
	$slides = get_field( 'hero_slides', get_queried_object_id() ) ?: array();
	$out    = '';
	$dots   = '';
	foreach ( $slides as $i => $s ) {
		$first = 0 === $i;
		$tag   = $first ? 'h1' : 'h2';
		$btn   = '';
		if ( ! empty( $s['button']['url'] ) ) {
			$btn = sprintf( '<a class="shcp-btn" href="%s"%s>%s<i class="shcp-btn__icon shcp-btn__icon--%s" aria-hidden="true"></i></a>',
				esc_url( $s['button']['url'] ), $s['button']['target'] ? ' target="_blank" rel="noopener"' : '',
				esc_html( $s['button']['title'] ?: shcp_t( 'learn_more' ) ), str_starts_with( $s['button']['url'], '#' ) ? 'down' : 'right' );
		}
		$out .= sprintf( '<div class="shcp-slide%s" aria-roledescription="slide" aria-label="%d / %d"%s>%s<div class="shcp-slide__inner"><div class="shcp-glass shcp-slide__card"><%s class="shcp-slide__title">%s</%s>%s%s</div></div>%s</div>',
			$first ? ' is-active' : '', $i + 1, count( $slides ), $first ? '' : ' aria-hidden="true"',
			wp_get_attachment_image( $s['background'], 'full', false, array( 'class' => 'shcp-slide__bg', 'alt' => '', 'loading' => 'eager', 'sizes' => '100vw' ) ),
			$tag, esc_html( $s['title'] ), $tag,
			$s['text'] ? '<p class="shcp-slide__text">' . esc_html( $s['text'] ) . '</p>' : '', $btn,
			$s['person'] ? wp_get_attachment_image( $s['person'], 'full', false, array( 'class' => 'shcp-slide__person', 'alt' => '', 'loading' => 'eager' ) ) : '' );
		$dots .= sprintf( '<button type="button" aria-label="%d"%s></button>', $i + 1, $first ? ' aria-current="true"' : '' );
	}
	if ( ! $out ) {
		return '';
	}
	return '<section class="shcp-slider" aria-roledescription="carousel">' . $out
		. ( count( $slides ) > 1 ? '<div class="shcp-slider__dots">' . $dots . '</div>' : '' ) . '</section>';
} );
