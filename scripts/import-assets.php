<?php
/**
 * Import assets/* into the media library (idempotent via _shcp_asset meta),
 * set application featured images, and write elementor/media.json {name: {id, url}}.
 * Run: scripts/wp eval-file "$PWD/scripts/import-assets.php"
 */

require_once ABSPATH . 'wp-admin/includes/media.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/image.php';

$root  = dirname( __DIR__ );
$media = array();

foreach ( glob( "$root/assets/*.{jpg,png,svg}", GLOB_BRACE ) as $file ) {
	$name     = pathinfo( $file, PATHINFO_FILENAME );
	$existing = get_posts( array( 'post_type' => 'attachment', 'meta_key' => '_shcp_asset', 'meta_value' => $name, 'fields' => 'ids', 'numberposts' => 1 ) );
	if ( $existing ) {
		$id = $existing[0];
	} else {
		$tmp = wp_tempnam( basename( $file ) );
		copy( $file, $tmp );
		$id = media_handle_sideload( array( 'name' => basename( $file ), 'tmp_name' => $tmp ), 0 );
		if ( is_wp_error( $id ) ) {
			WP_CLI::warning( "$name: " . $id->get_error_message() );
			continue;
		}
		update_post_meta( $id, '_shcp_asset', $name );
	}
	$media[ $name ] = array( 'id' => $id, 'url' => wp_get_attachment_url( $id ) );
}

foreach ( get_posts( array( 'post_type' => 'application', 'numberposts' => -1, 'lang' => '' ) ) as $post ) {
	$slug = preg_replace( '/-id$/', '', $post->post_name );
	$key  = 'marine-boat-building' === $slug ? 'hero-marine' : "app-{$slug}";
	if ( isset( $media[ $key ] ) ) {
		set_post_thumbnail( $post, $media[ $key ]['id'] );
	}
}

file_put_contents( "$root/elementor/media.json", wp_json_encode( $media, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES ) . "\n" );
WP_CLI::success( count( $media ) . ' assets' );
