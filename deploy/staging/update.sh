#!/bin/sh
# Run on stelar-server-02: pull the latest theme/config and restart if the stack changed.
set -e
cd /opt/shcp-staging
git -C repo pull --ff-only
cp repo/deploy/staging/compose.yml repo/deploy/staging/php.ini repo/deploy/staging/fpm.conf .
# Caddy (host) and PHP (container) both follow these absolute symlinks
mkdir -p html/wp-content/mu-plugins
[ -d html/wp-content/themes/shcp-child ] && [ ! -L html/wp-content/themes/shcp-child ] && rmdir html/wp-content/themes/shcp-child 2>/dev/null || true
ln -sfn /opt/shcp-staging/repo/shcp-child html/wp-content/themes/shcp-child
ln -sfn /opt/shcp-staging/repo/deploy/staging/shcp-staging-mail.php html/wp-content/mu-plugins/shcp-staging-mail.php
docker compose up -d
docker compose --profile tools run --rm cli wp elementor flush-css 2>/dev/null || true
echo "staging updated: $(git -C repo log -1 --format='%h %s')"
