<?php
/**
 * Plugin Name: SHCP staging mail catcher
 * Description: Sends all mail to the Mailpit container so the preview never emails real people.
 */
add_action( 'phpmailer_init', function ( $mailer ) {
	$mailer->isSMTP();
	$mailer->Host        = 'mailpit';
	$mailer->Port        = 1025;
	$mailer->SMTPAuth    = false;
	$mailer->SMTPAutoTLS = false;
} );
