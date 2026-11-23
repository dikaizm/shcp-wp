#!/bin/sh
# Screenshot a wp-admin path while logged in. Needs a temporary auto-login mu-plugin (removed after use; see git history of this note).
# scripts/shot-admin.sh /wp-admin/edit.php?post_type=application out.png [height]
TOKEN=$(cat "$SHOT_TOKEN_FILE")
TO=$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "http://localhost:10014$1")
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1440,"${3:-1200}" --virtual-time-budget=15000 --screenshot="$2" \
  "http://localhost:10014/?shcp_shot=$TOKEN&to=$TO" 2>/dev/null
