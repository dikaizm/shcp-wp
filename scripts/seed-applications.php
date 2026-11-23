<?php
/**
 * Seed product lines + application posts (EN + ID, linked in Polylang) from elementor/applications.json.
 * Idempotent: matches existing posts/terms by slug.
 * Run: scripts/wp eval-file "$PWD/scripts/seed-applications.php" --user=admin
 */

// Create (or update) a TablePress table by name; returns its id.
function shcp_seed_table( $spec ) {
	foreach ( TablePress::$model_table->load_all( false ) as $id ) {
		$table = TablePress::$model_table->load( $id, false, false );
		if ( $table['name'] === $spec['name'] ) {
			$table                        = TablePress::$model_table->load( $id );
			$table['data']                = $spec['rows'];
			$table['options']['table_head'] = $spec['head_rows'];
			TablePress::$model_table->save( $table );
			return $id;
		}
	}
	$table                          = TablePress::$model_table->get_table_template();
	$table['name']                  = $spec['name'];
	$table['data']                  = $spec['rows'];
	$table['options']['table_head'] = $spec['head_rows'];
	$table['visibility']['rows']    = array_fill( 0, count( $spec['rows'] ), 1 );
	$table['visibility']['columns'] = array_fill( 0, count( $spec['rows'][0] ), 1 );
	return TablePress::$model_table->add( $table );
}

$data = json_decode( file_get_contents( dirname( __DIR__ ) . '/elementor/applications.json' ), true );

$term_ids = array();
foreach ( $data['lines'] as $line ) {
	$ids = array();
	foreach ( array( 'en' => '', 'id' => '-id' ) as $lang => $suffix ) {
		$term = get_term_by( 'slug', $line['slug'] . $suffix, 'product_line' );
		$name = 'en' === $lang ? $line['name'] : $line['name_id'];
		$id   = $term ? $term->term_id : wp_insert_term( $name, 'product_line', array( 'slug' => $line['slug'] . $suffix ) )['term_id'];
		pll_set_term_language( $id, $lang );
		$ids[ $lang ] = $id;
	}
	pll_save_term_translations( $ids );
	$term_ids[ $line['slug'] ] = $ids;
}

// Indonesian copy of a table spec: translated head rows + Properties column (looked up by product code).
function shcp_table_id( $spec, $tr ) {
	$rows = $spec['rows'];
	foreach ( $tr['table_head'] ?? array() as $i => $row ) {
		$rows[ $i ] = $row;
	}
	foreach ( $rows as $i => $row ) {
		if ( $i >= $spec['head_rows'] && isset( $row[1], $tr['properties'][ $row[1] ] ) ) {
			$rows[ $i ][2] = $tr['properties'][ $row[1] ];
		}
	}
	return array( 'name' => $spec['name'] . ' (ID)', 'head_rows' => $spec['head_rows'], 'rows' => $rows );
}

function shcp_seed_application( $app, $order, $lang, $term_id ) {
	$tr       = 'id' === $lang ? $app['id'] : array();
	$slug     = $app['slug'] . ( 'id' === $lang ? '-id' : '' );
	$existing = get_posts( array( 'post_type' => 'application', 'name' => $slug, 'post_status' => 'any', 'numberposts' => 1, 'lang' => '' ) );
	$post_id  = wp_insert_post( array(
		'ID'          => $existing ? $existing[0]->ID : 0,
		'post_type'   => 'application',
		'post_status' => 'publish',
		'post_title'  => $tr['title'] ?? $app['title'],
		'post_name'   => $slug,
		'menu_order'  => $order,
	), true );
	if ( is_wp_error( $post_id ) ) {
		WP_CLI::warning( "$slug: " . $post_id->get_error_message() );
		return 0;
	}
	pll_set_post_language( $post_id, $lang );
	wp_set_object_terms( $post_id, $term_id, 'product_line' );

	// Remove meta from the old fixed-slot field layout.
	foreach ( array_keys( get_post_meta( $post_id ) ) as $key ) {
		if ( preg_match( '/^_?(benefit_\d|spec_\d|spec_heading|spec_text)/', $key ) ) {
			delete_post_meta( $post_id, $key );
		}
	}

	$placeholder = 'id' === $lang ? 'Deskripsi aplikasi akan disediakan oleh SHCP.' : 'Application description to be provided by SHCP.';
	update_field( 'intro', $tr['intro'] ?? $app['intro'] ?? $placeholder, $post_id );
	update_field( 'benefits', array_map( fn( $b ) => array( 'title' => $b[0], 'text' => $b[1] ), $tr['benefits'] ?? $app['benefits'] ?? array() ), $post_id );
	$sections = array();
	foreach ( $app['spec_sections'] ?? array() as $i => $section ) {
		$section['heading'] = $tr['sections'][ $i ]['heading'] ?? $section['heading'];
		$section['text']    = $tr['sections'][ $i ]['text'] ?? $section['text'];
		$section['tabs']    = array_map(
			fn( $t ) => array( 'label' => $t['label'], 'table' => $t['table'] ? shcp_seed_table( 'id' === $lang ? shcp_table_id( $t['table'], $tr ) : $t['table'] ) : '' ),
			$section['tabs']
		);
		$sections[] = $section;
	}
	update_field( 'spec_sections', $sections, $post_id );
	WP_CLI::log( ( $existing ? 'updated ' : 'created ' ) . "$slug #$post_id" );
	return $post_id;
}

foreach ( $data['applications'] as $order => $app ) {
	$ids = array();
	foreach ( array( 'en', 'id' ) as $lang ) {
		$ids[ $lang ] = shcp_seed_application( $app, $order, $lang, $term_ids[ $app['line'] ][ $lang ] );
	}
	pll_save_post_translations( array_filter( $ids ) );
}
