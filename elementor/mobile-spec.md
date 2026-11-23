# Mobile spec (Figma section 8606:2869, frames 390 wide)

Exact values read from get_design_context. Applied by build.py (`*_mobile` settings) and the
"Mobile" block in shcp-child/style.css (type roles `.m-*`).

## Type roles
- m-title: 28/36 SemiBold(600) ls 0 — section titles, hero titles ("subtitle/large")
- m-sub: 18/26 Medium ls .5 — card titles, mission items, policy items, "Our Subsidiary" ("body/medium")
- m-body: 14/20 Medium ls .5 — section body ("Mobile Size")
- m-body-r: 14/20 Regular ls 0 — text inside cards, NISER body ("Mobile Size 2")
- m-stat: 32/40 Bold ls .5 ("title/small")
- buttons: 16/24 Medium ls .5, padding 8×12 (hero), 8×16 (NISER), icon 16

## About
- Hero: section 824 tall; photo + rgba(56,56,56,.6) multiply; card x15 y65 w360, pad 24/24/80/24, gap 24, radius 16, 2px white border, gradient white→rgba(255,255,255,.5) top→bottom; person img top 468, 390×355 (overlaps card bottom ~91px).
- Highlights: py80, 2 rows gap16, cards w160 gap16, pad 16×8, gap16, icon 48.
- Vision & Mission: pt80 px24 (no bottom pad), gap80 between [vision][mission][image]; blocks gap24; mission items gap24, title↔text gap8 (16 for others); image full width (342) aspect 665/516.
- Strengths: py80 px24 gap40; header gap24, title centered; cards w240 pad16 gap24 (title↔text 16), row gap 16; image h200 r8.
- Policy: green, py80 px24 gap40; header gap24; items gap24, pad16, r8.
- NISER: py80 px24; card pad24 gap24 r16; kicker m-sub; title m-title (w295, centered); body m-body-r; button 8×16.
- Milestone: navy, py80 px24 gap40; items w240 gap24; dot 24; year m-sub; text m-body-r; item gap24 (dot→text), year↔text 16; line y12 x18.
- Plants: blue gradient (rgba(32,124,190,.5) 65%→white), py80 px24 gap40; title+image gap24, image h240 no radius; plant bar px16 py6 r8 text m-sub white; desc pl12 m-body-r; plant group gap12, list gap24; note m-body.
- Certifications: white, pt40 pb80 px24 gap40; title centered; items gap24, pad12 r8, blue gradient bg, text m-sub centered.
- CTA band (all pages): green, pt80 pb40 px24 gap24 (title↔body 16); button white 8×16; image full width h300 cover below.

## Shared
- Header: bg #F9F9F9, border-bottom 1px #DEE5ED, px32 py20 (76 tall); logo 80×36; burger 28×28, bars h5.6 r16 navy, widths 80% / 100% / 60%, tops 0 / 9.8 / 19.6.
- Footer: px24 py80 gap80; logos row gap16: SHCP 80×36, Nicekyd w105 (pt4), Nicemino w110 (py8); text 12/18 Medium ls .5 #383838; address block gap8, blocks gap40; no menu.
- Menu panel (open): bg #F9F9F9, px32 pt20; top row: lang switch (items px10 py6, 14/20, radius 4) left, close ✕ 28 right; gap80 to links; links 16/24 Medium, gap40; Contact button 8×16.

## Home
- Hero: section 800; card x15 y63 w360 pad 24/24/80/24 gap24; person top 445, 390×355; slider dots ignored.
- About: text block pt80 pb40 px24 gap24 centered (button 8×16), then image full width aspect 744/592 (no padding).
- Products: green gradient (rgba(28,166,74,.5) 88%→white), py80 px24 gap64; cards full width, gap24, image h200 r8 1px white border, title m-sub (gap16); navy card pad24 gap24 r8 2px white, title m-title, body m-body, button 8×16.
- Solutions: blue gradient, pt80, gap40; text px20 gap24 right-aligned; image h286 full width cover, offset left -15.73% width 178% (shows person).

## Products
- Hero: section 681; card x15 y63 w360 pad 24/24/80/24; person top 326, 390×355.
- Product blocks (UPR green / Alkyd red / Trading navy): py80 px24 gap40; header gap24 (Alkyd right-aligned); chips gap16, pad 8×10, radius 4, 14/20 Regular, white 1px border (Alkyd chips right-aligned); button full width white, 8×16, 16/24 navy.

## Applications
- Hero: section 681; card as Products; person top 326.
- List: blue gradient, py80 px24 gap40; title centered; group gap40; bar white pad 16×24 r8, label 18/26 Medium, chevron 20; grid 2 cols gap 8; card w164 pad12 gap8 r8, title 14/20 Medium centered, image h140 r8.

## Application detail (UPR + Alkyd)
- Hero: navy, pt40, gap40, centered; card w360 pad24 gap24 r16 2px white, gradient 117deg white 49% → rgba(255,255,255,.5); then photo full width h280 cover (no bottom padding).
- Body: white, py80 px24 gap80.
- Benefits: single column gap24; item gap8; title 16/24 Medium ls .5; text 14/20 Regular.
- Spec sections: list gap40; section gap24; header row (18/26 Medium + chevron 20) gap8 to 1px line; description m-body; tabs: pad 16×24, label 14/20 Regular green, active underline (gap4); table cells: head 14/20 Medium white pad 8×12, body 14/20 Regular pad 8×12, cols No44 Product120 Properties211 OilType134 OilLength99 Viscosity92 NonVol118 Acid105 Color71 (table scrolls).
- UPR table: same type, head pad 8×16, body pad 10×12.
- Buttons: stacked full width, gap24, 8×12, 16/24; outline navy + green.

## Contact
- Hero: green, 600 tall; card x15 y60 w360 pad24 gap24 (no button); people image top 317, 389×283 cover, bottom.
- Form: blue gradient, py80 gap40, title centered; card w360 pad24 gap24 r16 2px white; field: label 14/20 Medium #537DC4 ls .5, value 14/20 Regular navy, gap16, underline; email+phone group gap40; inquiry options gap16 (radio 14, gap4, 14/20 Regular); message gap8, 120 tall; submit full width 8×16 16/24.
- Offices: navy, py80 px24 gap40; title+photos gap40; photos row h200, gap24, each ~284 wide (scrolls); list gap24; item gap8: name 14/20 Medium white, row gap16: icon 32, text 14/20 Regular white.
