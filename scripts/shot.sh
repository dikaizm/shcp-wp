#!/bin/sh
# Full-page screenshot of a local URL path: scripts/shot.sh /about-us/ out.png [width]
# Narrow widths render inside an iframe: headless Chrome clamps windows to ~500px.
W="${3:-1440}"; H=8600; URL="http://localhost:10014$1"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ "$W" -lt 600 ]; then
  WRAP="$(mktemp -d)/wrap.html"
  printf '<body style="margin:0"><iframe src="%s" style="border:0;width:%spx;height:%spx"></iframe>' "$URL" "$W" "$H" > "$WRAP"
  URL="file://$WRAP"; WIN=800
else
  WIN="$W"
fi
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size="$WIN,$H" \
  --virtual-time-budget=15000 --screenshot="$2" "$URL" 2>/dev/null
