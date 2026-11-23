#!/bin/sh
# Run on stelar-server-02: pull the latest theme/config and restart if the stack changed.
set -e
cd /opt/shcp-staging
git -C repo pull --ff-only
cp repo/deploy/staging/compose.yml repo/deploy/staging/php.ini repo/deploy/staging/fpm.conf .
docker compose up -d
docker compose --profile tools run --rm cli wp elementor flush-css 2>/dev/null || true
echo "staging updated: $(git -C repo log -1 --format='%h %s')"
