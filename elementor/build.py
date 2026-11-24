"""Generate Elementor documents (theme templates + EN/ID pages) for the SHCP site from Figma specs.

Usage: python3 -I elementor/build.py   -> writes elementor/build/<doc>.json (+ site.json: forms, menus)
Push with: scripts/wp eval-file "$PWD/scripts/push-elementor.php" --user=admin

Copy lives in content.py (T["en"], T["id"]). Placeholders resolved by push-elementor.php:
  {{term:<slug>}}  product_line term id   {{doc:<key>}}  post id of another document
  {{cf7:<lang>}}   Contact Form 7 id
"""
import importlib.util
import itertools
import json
import urllib.parse
from pathlib import Path

HERE = Path(__file__).parent
MEDIA = json.loads((HERE / "media.json").read_text())
_spec = importlib.util.spec_from_file_location("content", HERE / "content.py")
_content = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_content)
T = _content.T

NAVY, GREEN, RED, WHITE, GREY = "#1C3764", "#1CA64A", "#BE2026", "#FFFFFF", "#383838"
GREEN_FADE, BLUE_FADE = "rgba(28,166,74,0.5)", "rgba(32,124,190,0.5)"
ICONS = "/wp-content/themes/shcp-child/assets/icons/"
BOXED = 1216  # Figma content column (112px edges at 1440)
FRAME = 1244  # Figma header / hero frame (98px edges at 1440)

PAGES = {  # key: (en slug, id slug, en title, id title)
    "home": ("home", "beranda", "Home", "Beranda"),
    "about": ("about-us", "tentang-kami", "About Us", "Tentang Kami"),
    "products": ("our-products", "produk-kami", "Our Products", "Produk"),
    "applications": ("applications", "aplikasi", "Applications", "Aplikasi"),
    "contact": ("contact-us", "hubungi-kami", "Contact Us", "Hubungi Kami"),
}


def url(lang, page, anchor=""):
    slug = PAGES[page][0 if lang == "en" else 1]
    base = "/" if lang == "en" else "/id/"
    return (base if page == "home" else f"{base}{slug}/") + anchor


_ids = itertools.count(0x1000000)


def uid():
    return format(next(_ids), "x")[:7]


def px(size, unit="px"):
    return {"unit": unit, "size": size, "sizes": []}


def box(t, r=None, b=None, l=None, unit="px"):
    r = t if r is None else r
    b = t if b is None else b
    l = r if l is None else l
    return {"unit": unit, "top": str(t), "right": str(r), "bottom": str(b), "left": str(l), "isLinked": t == r == b == l}


def img(name):
    return {"url": MEDIA[name]["url"], "id": MEDIA[name]["id"], "source": "library"}


def tag(name, **settings):
    enc = urllib.parse.quote(json.dumps(settings, separators=(",", ":")))
    return f'[elementor-tag id="{uid()}" name="{name}" settings="{enc}"]'


def type_(size, weight="500", lh=None, ls=0.5):
    s = {"typography_typography": "custom", "typography_font_family": "Poppins",
         "typography_font_size": px(size), "typography_font_weight": weight,
         "typography_letter_spacing": px(ls)}
    if lh:
        s["typography_line_height"] = px(lh)
    return s


# Mobile (Figma "Mobile" frames, values in elementor/mobile-spec.md) comes from type-role classes
# (m-*, styled in style.css since Elementor can't vary font weight per device) plus *_mobile padding/gap.
HEADING_ROLE = {48: "m-title", 56: "m-stat", 21: "m-sub"}
TEXT_ROLE = {20: "m-body", 18: "m-body-r"}


def gm(n):
    return {"flex_gap_mobile": {"unit": "px", "size": n, "column": str(n), "row": str(n), "isLinked": True}}


def pm(*a):
    return {"padding_mobile": box(*a)}


# ---------- elements ----------

def con(*children, direction="column", boxed=False, full=False, width=None, gap=0, pad=None,
        bg=None, align=None, justify=None, wrap=False, min_h=None, classes="", mobile_dir="column", **extra):
    s = {"flex_direction": direction, "flex_gap": {"unit": "px", "size": gap, "column": str(gap), "row": str(gap), "isLinked": True}}
    if direction == "row":
        s["flex_direction_mobile"] = mobile_dir
        s["flex_direction_tablet"] = mobile_dir  # tablet (768-1024) stacks like mobile
    if boxed:
        s["content_width"] = "boxed"
        s["boxed_width"] = px(boxed if isinstance(boxed, int) and boxed > 1 else BOXED)
    else:  # Elementor's default is boxed at the kit width (1140), which indents nested rows
        s["content_width"] = "full"
    if width:
        s["content_width"] = "full"
        s["width"] = px(width, "%" if width <= 100 else "px")
        s["width_mobile"] = px(100, "%")
        s["width_tablet"] = px(100, "%")
    s["padding"] = box(*pad) if pad is not None else box(0)
    if bg:
        s.update(bg)
    if align:
        s["flex_align_items"] = align
    if justify:
        s["flex_justify_content"] = justify
    if wrap == "mobile":
        s["flex_wrap"] = "nowrap"
        s["flex_wrap_tablet"] = "wrap"
        s["flex_wrap_mobile"] = "wrap"
    elif wrap:
        s["flex_wrap"] = "wrap"
    if min_h:
        s["min_height"] = px(min_h)
        s["min_height_mobile"] = px(0)
    if boxed is True and pad is not None and box(*pad)["left"] == "16":
        # Content sections: 112px edges on desktop like the padded sections, 40px on tablet
        bx = box(*pad)
        s["padding"] = box(bx["top"], 112, bx["bottom"], 112)
        s.setdefault("padding_tablet", box(bx["top"], 40, bx["bottom"], 40))
        classes = " ".join(filter(None, [classes, "shcp-gl shcp-gr"]))
    if full and pad is not None:
        # Wider than 1440: 112px gutters grow so content stays in the centred 1216 column (style.css)
        bx = box(*pad)
        classes = " ".join(filter(None, [classes, "shcp-gl" if bx["left"] == "112" else "",
                                         "shcp-gr" if bx["right"] == "112" else ""]))
    if classes:
        s["css_classes"] = classes
    s.update(extra)
    return {"id": uid(), "elType": "container", "settings": s, "elements": list(children), "isInner": False}


def widget(kind, **settings):
    return {"id": uid(), "elType": "widget", "widgetType": kind, "settings": settings, "elements": []}


def _role(extra, role):
    if role:
        extra["_css_classes"] = (extra.get("_css_classes", "") + " " + role).strip()
    return extra


def heading(text, size=48, color=NAVY, tag_="h2", align="left", weight="700", lh=None, m=None, **extra):
    lh = lh or {48: 56, 56: 64, 21: 32, 20: 30, 18: 26}.get(size, round(size * 1.2))
    return widget("heading", title=text, header_size=tag_, align=align, title_color=color,
                  **type_(size, weight, lh, 0.15 if size == 21 else 0.5), **_role(extra, m or HEADING_ROLE.get(size)))


def text(html, size=20, color=NAVY, align="left", m=None, **extra):
    lh = {20: 30, 18: 26, 16: 24}.get(size, round(size * 1.5))
    if not html.lstrip().startswith("<"):
        html = f"<p>{html}</p>"
    return widget("text-editor", editor=html, text_color=color, align=align, **type_(size, "500", lh),
                  **_role(extra, m or TEXT_ROLE.get(size)))


def button(label, link, style="green", icon="fas fa-chevron-right", size=20, align=None, full=False, classes="", small=False):
    bg, fg, border = {"green": (GREEN, WHITE, WHITE), "white": (WHITE, GREEN, WHITE),
                      "white-navy": (WHITE, NAVY, WHITE), "outline": ("rgba(0,0,0,0)", NAVY, NAVY)}[style]
    s = {"text": label, "link": {"url": link, "is_external": "on" if link.startswith("http") else "", "nofollow": ""},
         "background_color": bg, "button_text_color": fg,
         "border_border": "solid", "border_width": box(1), "border_color": border,
         "border_radius": box(8), "text_padding": box(16, 24),
         "button_background_hover_color": NAVY, "hover_color": WHITE,
         **type_(size, "500", 30)}
    if icon:
        s.update(selected_icon={"value": icon, "library": "fa-solid"}, icon_align="row-reverse", icon_indent=px(10))
    # m-btn: 16/24, 8x16 on mobile; m-btn-sm: 8x12 (hero buttons)
    s["_css_classes"] = " ".join(filter(None, [classes, "m-btn", "m-btn-sm" if small else ""]))
    if full:
        s["align"] = "justify"
    elif align:
        s["align"] = align
    return widget("button", **s)


def image(name, radius=0, width=None, height=None, cover=False, m_height=None, **extra):
    s = {"image": img(name), "image_size": "full"}
    if radius:
        s["image_border_radius"] = box(radius)
    if width:
        s["width"] = px(width, "%" if width <= 100 else "px")
    if height:
        s["height"] = px(height)
        s["height_mobile"] = px(m_height or height)
    if cover:
        s["object-fit"] = "cover"
        s["object_fit"] = "cover"
    s.update(extra)
    return widget("image", **s)


def icon_img(name, size=48):
    return widget("image", image={"url": ICONS + name, "id": ""}, image_size="full", width=px(size), align="center")


def shortcode(code):
    return widget("shortcode", shortcode=code)


def html(markup):
    return widget("html", html=markup)


def solid(color):
    return {"background_background": "classic", "background_color": color}


def gradient(a, b, angle=180, a_stop=0, b_stop=100):
    return {"background_background": "gradient", "background_color": a, "background_color_b": b,
            "background_gradient_angle": px(angle, "deg"),
            "background_color_stop": px(a_stop, "%"), "background_color_b_stop": px(b_stop, "%")}


def photo(name, overlay="rgba(56,56,56,0.6)"):
    s = {"background_background": "classic", "background_image": img(name), "background_position": "center center",
         "background_size": "cover", "background_repeat": "no-repeat", "background_color": NAVY}
    if overlay:
        s.update(background_overlay_background="classic", background_overlay_color=overlay,
                 background_overlay_blend_mode="multiply")
    return s


def bg_image(name):
    return {"background_background": "classic", "background_image": img(name), "background_position": "center center",
            "background_size": "cover", "background_repeat": "no-repeat"}


# ---------- shared sections ----------

def hero(lang, bg_name, person, title, body, cta, cta_link, height=720, card_w=960, text_w=612,
         person_x=700, person_w=658, m_height=None):
    # Card and cut-out are siblings in one row: the person overlaps the card's right edge by Figma's amount
    # (ov) and stays attached to it at every width. Tablet/mobile stack it under the card (style.css).
    pr = 40 + card_w - 80 - text_w          # card right padding that keeps the text clear of the person
    ov = 98 + card_w - person_x             # overlap with the card at 1440
    card = con(heading(title, 48, tag_="h1"), text(body), button(cta, cta_link, icon="fas fa-chevron-down", small=True),
               width=card_w, gap=32, pad=(40, pr, 40, 40), classes=f"shcp-glass shcp-pr-{pr}",
               padding_tablet=box(40, 40, 80, 40), **pm(24, 24, 80, 24), **gm(24))
    people = image(person, _css_classes=f"shcp-hero-person shcp-attached shcp-hp-{person_w} shcp-ov-{ov}")
    wrap = con(card, people, direction="row", boxed=FRAME, pad=(0, 0, 0, 0), min_h=height, classes="shcp-hero-wrap",
               padding_tablet=box(60, 0, 0, 0), **pm(0))
    return con(wrap, full=True, min_h=height, bg=photo(bg_name), classes="shcp-hero shcp-fx", **pm(63, 15, 0, 15))


def stats(lang):
    icons = ["icon-quality.svg", "icon-countries.svg", "icon-plants.svg", "icon-capacity.svg"]
    cards = [con(icon_img(i), heading(n, 56, WHITE, "p", "center"), text(l, 20, WHITE, "center", m="m-body-r"),
                 width=280, gap=16, pad=(32,), align="center", classes="shcp-stat",
                 bg=gradient("rgba(255,255,255,0.5)", "rgba(255,255,255,0.25)"),
                 border_border="solid", border_width=box(2), border_color=WHITE, border_radius=box(8),
                 width_tablet=px(22, "%"), width_mobile=px(160), **pm(16, 8), **gm(16))
             for i, (n, l) in zip(icons, T[lang]["stats"])]
    return con(con(*cards, direction="row", boxed=True, wrap="mobile", justify="center", gap=40, mobile_dir="row", **gm(16)),
               full=True, pad=(80, 16), bg=solid(NAVY), **pm(80, 15))


def cta_band(lang, body=None, label=None):
    t = T[lang]
    left = con(con(heading(t["cta_title"], 48, WHITE, _element_width="initial", _element_custom_width=px(612),
                           _element_custom_width_mobile=px(100, "%")),
                   text(body or t["cta_body"], 20, WHITE), gap=16),
               button(label or t["cta_btn"], url(lang, "contact"), "white"),
               width=800, gap=40, pad=(120, 0, 120, 112), classes="shcp-gl-vw", **pm(80, 24, 40, 24), **gm(24))
    right = con(image("cta-team", _css_classes="shcp-cta-img"), width=743, justify="flex-end", align="flex-end",
                classes="shcp-cta-right")
    return con(left, right, direction="row", full=True, align="stretch", bg=solid(GREEN), classes="shcp-cta", **gm(0))


def section_title(text_, color=NAVY, align="center"):
    return heading(text_, 48, color, align=align)


# ---------- theme templates (shared by both languages) ----------

def header():
    burger = html('<button class="shcp-burger" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>')
    logo = image("logo-shcp", width=124, link_to="custom", link={"url": ""}, __dynamic__={"link": tag("site-url")})
    nav = con(shortcode('[shcp_menu location="shcp-primary"]'), shortcode("[shcp_lang]"),
              direction="row", align="center", gap=80, classes="shcp-nav")
    return con(con(logo, nav, burger, direction="row", boxed=FRAME, justify="space-between", align="center",
                   mobile_dir="row", flex_wrap_mobile="nowrap"),
               full=True, pad=(8, 16), min_h=120, align="center", justify="center", bg=bg_image("header-bg"),
               border_border="solid", border_width=box(0, 0, 1, 0), border_color="#C1C1C1",
               classes="shcp-header shcp-fx", min_height_mobile=px(76), **pm(20, 32))


def footer():
    logos = con(image("logo-shcp", width=124), image("logo-nicekyd", width=160), image("logo-nicemino", width=185),
                direction="row", gap=40, align="center", mobile_dir="row", wrap=True, classes="shcp-footer-logos", **gm(16))
    top = con(logos, con(shortcode('[shcp_menu location="shcp-footer"]'), classes="shcp-hide-mobile"), direction="row",
              justify="space-between", align="center", gap=40)
    address = text("<p><span style='font-size:18px;line-height:26px'>Singapore Highpolymer Chemical Products Pte Ltd</span></p>"
                   "<p>21 Tanjong Penjuru,<br>Jurong Industrial Estate, Singapore 609022<br>"
                   "Email: <a href='mailto:enquiry@shcp.com.sg'>enquiry@shcp.com.sg</a><br>"
                   "Tel: (65) 6268 8255, Fax: (65) 6265 6855</p>", 16, GREY, m="m-foot")
    bottom = con(con(address, width=50), con(shortcode("[shcp_t key=footer_about]"), width=360),
                 direction="row", justify="space-between", gap=40, **gm(40))
    return con(top, bottom, full=True, gap=120, pad=(120, 112), bg=bg_image("footer-bg"), **gm(80),
               classes="shcp-footer", **pm(80, 24))


def app_card():
    return con(
        heading(tag("post-title"), 21, NAVY, "h3", "center", "600", m="m-card-title", __dynamic__={"title": tag("post-title")}),
        widget("image", image={"url": "", "id": ""}, image_size="medium_large", image_border_radius=box(8),
               width=px(100, "%"), height=px(240), height_mobile=px(140), object_fit="cover", **{"object-fit": "cover"},
               __dynamic__={"image": tag("post-featured-image")}),
        gap=16, pad=(16,), classes="shcp-app-card", html_tag="a", link={"url": ""},
        __dynamic__={"link": tag("post-url")}, **pm(12), **gm(8),
    )


def single_application():
    hero_ = con(
        con(con(heading(tag("post-title"), 48, tag_="h1", __dynamic__={"title": tag("post-title")}),
                text("", 20, __dynamic__={"editor": tag("acf-text", key="field_shcp_intro:intro")}),
                shortcode("[shcp_btn key=learn_more href=#details icon=down]"),
                width=692, gap=32, pad=(40,), classes="shcp-glass shcp-glass--detail", **pm(24), **gm(24)),
            boxed=FRAME, pad=(104, 0, 104, 0), **pm(0)),
        full=True, min_h=600, classes="shcp-detail-hero shcp-fx", **pm(40, 15, 320, 15),
        bg={"background_background": "classic", "background_color": NAVY,
            "background_image": {"url": "", "id": ""}, "background_position": "center center",
            "background_size": "cover", "background_repeat": "no-repeat",
            "__dynamic__": {"background_image": tag("post-featured-image")}},
    )
    body = con(shortcode("[shcp_benefits]"), shortcode("[shcp_spec]"), shortcode("[shcp_detail_buttons]"),
               boxed=True, gap=80, pad=(120, 16, 120, 16), _element_id="details", **pm(80, 24), **gm(80))
    return [hero_, body]


# ---------- pages ----------

def chips(items, color, align=""):
    spans = "".join(f"<span>{i}</span>" for i in items)
    return html(f'<div class="shcp-chips {align}" style="color:{color}">{spans}</div>')


def home(lang):
    t = T[lang]
    about = con(
        image("home-about", width=687, _css_classes="shcp-flush"),
        con(heading(t["home_about_title"], 48, align="center"), text(t["home_about_body"], 20, align="center"),
            button(t["home_about_btn"], url(lang, "about")),
            gap=40, align="center", justify="center", pad=(120, 112, 120, 0), width=753, padding_tablet=box(80, 40),
            **pm(80, 24, 40, 24), **gm(24)),
        direction="row", full=True, align="flex-end", gap=48, bg=solid(WHITE), _element_id="about",
        mobile_dir="column-reverse", **gm(0),
    )
    products = [("product-upr", t["home_products"][0]), ("product-alkyd", t["home_products"][1]),
                ("product-amino", t["home_products"][2]), ("product-trading", t["home_products"][3])]
    prods = con(
        con(*[con(image(i, 8, width=100, height=200, cover=True, _css_classes="shcp-bordered"),
                  heading(n, 21, tag_="h3", weight="600"), width=277, gap=16, width_tablet=px(47, "%"),
                  width_mobile=px(100, "%"), **gm(16))
              for i, n in products],
            direction="row", gap=36, mobile_dir="column", flex_direction_tablet="row", flex_wrap_tablet="wrap", **gm(24)),
        con(heading(t["home_products_title"], 48, WHITE), text(t["home_products_body"], 20, WHITE),
            button(t["home_products_btn"], url(lang, "products")),
            width=880, gap=40, pad=(40,), bg=solid(NAVY), border_border="solid", border_width=box(2),
            border_color=WHITE, border_radius=box(16), border_radius_mobile=box(8), **pm(24), **gm(24)),
        boxed=True, gap=64, pad=(120, 16), **pm(80, 24), **gm(64))
    solutions = con(
        con(heading(t["home_apps_title"], 48, align="right"), text(t["home_apps_body"], 20, align="right"),
            button(t["home_apps_btn"], url(lang, "applications"), align="right"),
            boxed=True, align="flex-end", gap=40, pad=(0, 16), **pm(0, 20), **gm(24)),
        image("home-solutions", width=100, _css_classes="shcp-solutions-img"),
        full=True, gap=0, pad=(120, 0, 0, 0), bg=gradient(BLUE_FADE, WHITE, 180, 65, 100), **pm(80, 0, 0, 0), **gm(40))
    return [
        con(shortcode("[shcp_hero_slider]"), full=True),
        stats(lang), about,
        con(prods, full=True, bg=gradient(GREEN_FADE, WHITE, 180, 88, 100)),
        solutions, cta_band(lang),
    ]


def products_page(lang):
    t = T[lang]
    upr = ["General purpose", "Fire Retardant", "Plywood", "Roofing", "Artificial Marble", "Gelcoat", "Casting",
           "Heat Resistant", "Corrosion Resistant", "Button", "Flexible &amp; Semi-flexible", "Putty", "Pultrusion/Hot Press Moulding"]
    alkyd = ["Short Oil Alkyd (SOA)", "Medium Oil Alkyd (MOA)", "Long Oil Alkyd (LOA)", "Modified Alkyd", "Saturated Polyester", "Amino Resin"]
    trading = ["Fibreglass", "Curing Agent (Promotor)", "Aerosil", "Paraffin Wax", "Mold Release Agents", "Silicon Rubber", "Styrene Monomer"]

    def block(key, items, link, color, anchor, align="left"):
        return con(con(heading(t[f"{key}_title"], 48, WHITE, align=align),
                       text(t[f"{key}_body"], 20, WHITE, align),
                       chips(items, WHITE, "shcp-chips--end" if align == "right" else ""),
                       button(t[f"{key}_btn"], link, "white-navy", full=True),
                       boxed=True, gap=40, pad=(120, 16), **pm(80, 24), **gm(24)),
                   full=True, bg=solid(color), _element_id=anchor)

    return [
        hero(lang, "hero-products-bg", "hero-products-person", t["prod_title"], t["prod_body"], t["prod_btn"], "#upr",
             height=640, card_w=880, person_x=653, person_w=571, m_height=681),
        block("upr", upr, url(lang, "applications", "#upr"), GREEN, "upr"),
        block("alkyd", alkyd, url(lang, "applications", "#alkyd"), RED, "alkyd", "right"),
        block("trading", trading, "https://www.niser.com.sg/", NAVY, "trading"),
        cta_band(lang),
    ]


def applications_page(lang):
    t = T[lang]

    def group(slug, label):
        bar = html(f'<div class="shcp-group-bar"><span>{label}</span></div>')
        grid = widget("loop-grid", _skin="post", template_id="{{doc:app-card}}", columns="4", columns_tablet="3",
                      columns_mobile="2", posts_per_page=40, column_gap=px(40), row_gap=px(40),
                      column_gap_mobile=px(8), row_gap_mobile=px(8),
                      post_query_post_type="application", post_query_include=["terms"],
                      post_query_include_term_ids=["{{term:%s%s}}" % (slug, "" if lang == "en" else "-id")],
                      post_query_orderby="menu_order", post_query_order="asc")
        return con(bar, grid, gap=40, _element_id=slug, **gm(40))

    return [
        hero(lang, "hero-applications-bg", "hero-applications-person", t["apps_title"], t["apps_body"], t["apps_btn"],
             "#upr", height=640, card_w=880, text_w=560, person_x=659, person_w=571, m_height=681),
        con(con(section_title(t["apps_all"]), group("upr", t["line_upr"]), group("alkyd", t["line_alkyd"]),
                boxed=True, gap=80, pad=(120, 16), **pm(80, 24), **gm(40)),
            full=True, bg=gradient(BLUE_FADE, WHITE, 180, 65, 100)),
        cta_band(lang),
    ]


def about_page(lang):
    t = T[lang]
    vision = con(
        con(con(heading(t["vision_title"], 48, GREEN), text(t["vision_body"], 20), gap=40, pad=(120, 0, 0, 112),
                padding_tablet=box(80, 0, 0, 0), classes="shcp-gl-vw", **pm(0), **gm(24)),
            image("about-vision", width=665, _css_classes="shcp-flush shcp-vision-img"), width=740, gap=16,
            justify="space-between", classes="shcp-vision-col"),
        con(heading(t["mission_title"], 48),
            *[con(heading(a, 21, tag_="h3", weight="600"), text(b, 18), gap=16, **gm(8)) for a, b in t["mission"]],
            width=560, gap=24, pad=(120, 0, 120, 0), padding_tablet=box(40, 0, 80, 0), **pm(0), **gm(24)),
        direction="row", full=True, justify="space-between", gap=28, pad=(0, 112, 0, 0), padding_tablet=box(0, 40), bg=solid(WHITE),
        _element_id="vision", **pm(80, 24, 0, 24), **gm(80))
    motto = con(
        con(html(f'<p class="shcp-motto">{t["motto_1"]}<span>{t["motto_2"]}</span></p>'),
            text(f"<p><strong>{t['motto_bold']}</strong><br>{t['motto_body']}</p>", 20, WHITE, "right"),
            width=864, gap=40, align="flex-end"),
        full=True, min_h=502, align="flex-end", justify="center", pad=(120, 112), bg=bg_image("about-motto-bg"),
        classes="shcp-hide-mobile")
    strengths = con(
        con(section_title(t["strengths_title"]), text(t["strengths_body"], 20, align="center"), width=864, gap=40, **gm(24)),
        con(*[con(con(heading(a, 21, tag_="h3", weight="600"), text(b, 18), gap=16, **gm(16)),
                  image(i, 8, width=100, height=240, m_height=200, cover=True),
                  width=274, gap=16, pad=(16,), bg=gradient(WHITE, "rgba(255,255,255,0.5)"), border_radius=box(8), **gm(24))
              for (a, b), i in zip(t["strengths"], ["strength-integrated", "strength-manufacturing",
                                                    "strength-partnerships", "strength-support"])],
            direction="row", gap=40, justify="center", mobile_dir="row", classes="shcp-scroll-x", **gm(16)),
        full=True, gap=80, align="center", pad=(120, 112), bg=gradient(GREEN_FADE, WHITE, 180, 88, 100),
        **pm(80, 24), **gm(40))
    policy = con(
        con(heading(t["policy_title"], 48, WHITE), text(t["policy_body"], 20, WHITE), width=618, gap=40, **gm(24)),
        con(*[con(heading(p, 21, tag_="p", weight="600"), pad=(16,), bg=gradient(WHITE, "rgba(255,255,255,0.5)"),
                  border_radius=box(8)) for p in t["policy"]], gap=40, width=598, **gm(24)),
        direction="row", full=True, pad=(120, 112), bg=solid(GREEN), justify="space-between", gap=40,
        **pm(80, 24), **gm(40))
    niser = con(
        con(con(heading(t["niser_kicker"], 21, align="center", tag_="p", weight="600"),
                heading("NISER Composites PTE LTD", 48, align="center"), gap=24, **gm(16)),
            text("".join(f"<p>{p}</p>" for p in t["niser_body"]), 18, align="center"),
            button(t["niser_btn"], "https://www.niser.com.sg/"),
            width=800, gap=40, align="center", pad=(48,), classes="shcp-glass shcp-glass--down", **pm(24), **gm(24)),
        full=True, min_h=920, pad=(122, 112), bg=photo("niser-bg", "rgba(56,56,56,0.5)"), **pm(80, 24))
    milestone = con(
        heading(t["milestone_title"], 48, WHITE),
        html('<div class="shcp-milestones">' + "".join(f"<div><h3>{y}</h3><p>{d}</p></div>" for y, d in t["milestones"]) + "</div>"),
        full=True, gap=40, pad=(120, 0, 120, 112), bg=solid(NAVY), **pm(80, 24), **gm(40))
    plant_rows = []
    for name, d in t["plants"]:
        plant_rows.append(con(con(text(f"<p>{name}</p>", 20, WHITE, m="m-sub"), pad=(10, 24), bg=solid(NAVY),
                                  border_radius=box(8), **pm(6, 16)),
                              text(d, 18, _padding=box(0, 24), _padding_mobile=box(0, 0, 0, 12)), gap=16, **gm(12)))
    plants = con(
        con(heading(t["plants_title"], 48), image("about-plants", 8, width=100, height=439, m_height=240, cover=True,
                                                   image_border_radius_mobile=box(0)), width=656, gap=40, **gm(24)),
        con(con(*plant_rows, gap=16, **gm(24)), text(t["plants_note"], 20), width=480, gap=40, **gm(40)),
        direction="row", boxed=True, justify="space-between", gap=40, pad=(120, 16, 0, 16), **pm(80, 24), **gm(40))
    certs = con(
        section_title(t["certs_title"]),
        con(*[con(heading(c, 21, tag_="p", weight="600", align="center"), width=280, pad=(24,),
                  bg=gradient(WHITE, "rgba(83,125,196,0.25)"), border_radius=box(8), width_tablet=px(30, "%"), width_mobile=px(100, "%"), **pm(12))
              for c in t["certs"]],
            direction="row", gap=40, justify="center", mobile_dir="column", flex_direction_tablet="row", **gm(24)),
        boxed=True, gap=64, pad=(120, 16), **pm(40, 24, 80, 24), **gm(40))
    return [
        hero(lang, "hero-about-bg", "hero-about-person", t["about_title"], t["about_body"], t["learn_more"], "#vision", m_height=824),
        stats(lang), vision, motto, strengths, policy, niser, milestone,
        con(plants, certs, full=True, bg=solid(WHITE), classes="shcp-plants-wrap"),
        cta_band(lang, t["cta_about_body"], t["cta_about_btn"]),
    ]


def contact_page(lang):
    t = T[lang]
    hero_ = con(
        con(con(heading(t["contact_title"], 48, tag_="h1"), text(t["contact_body"]),
                button(t["contact_btn"], "#form", icon="fas fa-chevron-down", classes="shcp-hide-mobile"),
                width=640, gap=32, pad=(40,), classes="shcp-glass shcp-glass--down shcp-glass--top", **pm(24), **gm(24)),
            boxed=FRAME, pad=(120, 0, 0, 0), classes="shcp-hero-front", padding_tablet=box(60, 0, 0, 0), **pm(0)),
        image("cta-team", _position="absolute", _offset_orientation_h="end",
              _offset_x_end=px(0), _offset_orientation_v="end", _offset_y=px(0),
              _element_width="initial", _element_custom_width=px(880), _css_classes="shcp-hero-person shcp-hero-person--contact shcp-hp-880"),
        full=True, min_h=640, bg=solid(GREEN), classes="shcp-hero shcp-fx", **pm(60, 15, 0, 15))
    states = (f'<div class="shcp-form-state" data-state="ok" hidden><img src="{ICONS}icon-success.svg" alt="" width="200" height="199">'
              f'<p class="shcp-form-state__msg" data-template="{t["f_ok"]}"></p>'
              f'<a class="shcp-btn" href="{url(lang, "home")}">{t["f_ok_home"]}</a></div>'
              f'<div class="shcp-form-state" data-state="fail" hidden><img src="{ICONS}icon-fail.svg" alt="" width="200" height="199">'
              f'<p class="shcp-form-state__msg">{t["f_fail"]}</p>'
              f'<button type="button" class="shcp-btn" data-back>{t["f_fail_back"]}</button></div>')
    form = con(
        section_title(t["form_title"]),
        con(shortcode('[contact-form-7 id="{{cf7:%s}}"]' % lang), html(states), width=936, pad=(48,),
            classes="shcp-form-card", **pm(24), width_mobile=px(360)),
        full=True, align="center", gap=40, pad=(120, 16), bg=gradient(BLUE_FADE, WHITE, 180, 65, 100),
        _element_id="form", **pm(80, 15), **gm(40))
    offices = con(
        heading(t["offices_title"], 48, WHITE),
        con(*[image(n, 8, width=100, height=280, m_height=200, cover=True) for n in ("hero-home-bg", "niser-bg", "hero-about-bg")],
            direction="row", gap=24, classes="shcp-equal shcp-scroll-x", mobile_dir="row", **gm(24)),
        html('<div class="shcp-offices">' + "".join(
            f'<div><h3>{a}</h3><p><img src="{ICONS}icon-location.svg" alt="" width="32" height="32"><span>{b}</span></p></div>'
            for a, b in t["offices"]) + "</div>"),
        boxed=True, gap=40, pad=(120, 16), **pm(80, 24), **gm(40))
    return [hero_, form, con(offices, full=True, bg=solid(NAVY))]


TEMPLATES = [
    ("site-header", "Site Header", "header", ["include/general"], lambda: [header()]),
    ("site-footer", "Site Footer", "footer", ["include/general"], lambda: [footer()]),
    ("app-card", "Application Card", "loop-item", [], lambda: [app_card()]),
    ("single-application", "Single Application", "single-post", ["include/singular/application"], single_application),
]
PAGE_BUILDERS = {"home": home, "about": about_page, "products": products_page,
                 "applications": applications_page, "contact": contact_page}


def forms():
    """Contact Form 7 markup per language (consumed by push-elementor.php)."""
    out = {}
    for lang in ("en", "id"):
        t = T[lang]
        opts = " ".join(f'"{o}"' for o in t["f_options"])
        out[lang] = {
            "title": f"SHCP Contact ({lang.upper()})",
            "form": (f'<div class="shcp-form-grid">\n'
                     f'<label>{t["f_name"]} [text* full-name autocomplete:name placeholder "{t["f_name_ph"]}"]</label>\n'
                     f'<label>{t["f_company"]} [text company autocomplete:organization placeholder "{t["f_company_ph"]}"]</label>\n'
                     f'<label>{t["f_email"]} [email* your-email autocomplete:email placeholder "{t["f_email_ph"]}"]</label>\n'
                     f'<label>{t["f_phone"]} [tel* phone autocomplete:tel placeholder "{t["f_phone_ph"]}"]</label>\n'
                     f'</div>\n<fieldset class="shcp-form-inquiry"><legend>{t["f_inquiry"]}</legend>'
                     f'[radio inquiry use_label_element default:1 {opts}]</fieldset>\n'
                     f'<label>{t["f_message"]} [textarea* your-message placeholder "{t["f_message_ph"]}"]</label>\n'
                     f'<p class="shcp-form-submit">[submit "{t["f_submit"]}"]</p>'),
        }
    return out


if __name__ == "__main__":
    out = HERE / "build"
    out.mkdir(exist_ok=True)
    for f in out.glob("*.json"):
        f.unlink()
    n = 0
    for key, title, kind, conditions, build in TEMPLATES:
        doc = {"key": key, "title": title, "type": kind, "conditions": conditions, "data": build()}
        (out / f"{key}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1))
        n += 1
    for page, build in PAGE_BUILDERS.items():
        en_slug, id_slug, en_title, id_title = PAGES[page]
        for lang, slug, title in (("en", en_slug, en_title), ("id", id_slug, id_title)):
            doc = {"key": f"{page}@{lang}", "group": page, "lang": lang, "slug": slug, "title": title,
                   "type": "page", "conditions": [], "front": page == "home", "data": build(lang)}
            (out / f"{page}@{lang}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1))
            n += 1
    site = {"forms": forms(), "menus": {lang: T[lang]["menu"] for lang in ("en", "id")},
            "menu_home": {"en": "Homepage", "id": "Beranda"},
    # First-run content for the Home "Hero slides" field; push skips it once slides exist.
    "hero_slides": {lang: [{"title": T[lang][a], "text": T[lang][b],
                            "button": {"title": T[lang][c], "url": u(lang), "target": ""},
                            "background": MEDIA[bg]["id"], "person": MEDIA[pp]["id"]}
                           for a, b, c, u, bg, pp in [
                               ("home_title", "home_body", "learn_more", lambda l: "#about", "hero-home-bg", "hero-home-people"),
                               ("about_title", "about_body", "learn_more", lambda l: url(l, "about"), "hero-about-bg", "hero-about-person"),
                               ("prod_title", "prod_body", "prod_btn", lambda l: url(l, "products"), "hero-products-bg", "hero-products-person")]]
                    for lang in ("en", "id")},
            "pages": {lang: [url(lang, k) for k in ("about", "products", "applications", "contact")] for lang in ("en", "id")}}
    (out / "site.json").write_text(json.dumps(site, ensure_ascii=False, indent=1))
    print(f"{n} documents -> {out}")
