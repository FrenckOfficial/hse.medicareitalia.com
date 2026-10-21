# -*- coding: utf-8 -*-
"""Genera il sito statico Medicare Italia HSE.

Uso:  python _build/build.py
Scrive le pagine HTML nella root del progetto mantenendo gli stessi URL del sito originale
(/corsi/, /sicurezza-sul-lavoro/, ...).
"""
import html as html_lib
import json
import os
import re
import shutil
from html import escape as e

from data import *  # noqa: F401,F403
from contenuti import *  # noqa: F401,F403

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = ROOT  # le pagine vengono generate nella cartella principale del progetto
MANIFEST = os.path.join(ROOT, "_build", "pagine-generate.txt")  # elenco delle pagine create dal generatore
SOURCE_DIRS = {"_build", "content", "admin", "assets", ".github", ".claude", ".git"}
GENERATED = []
VERSION = "4"

# --------------------------------------------------------------------------- icone
_I = {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "cart": '<circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.6 12.4a2 2 0 0 0 2 1.6h8.2a2 2 0 0 0 2-1.5L21.5 8H6.2"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "shield": '<path d="M12 3 4 6v6c0 5 3.4 8.3 8 9 4.6-.7 8-4 8-9V6l-8-3Z"/><path d="m9 12 2 2 4-4"/>',
    "doc": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    "steth": '<path d="M6 3v5a5 5 0 0 0 10 0V3"/><path d="M11 13v2a5 5 0 0 0 10 0v-2"/><circle cx="21" cy="11" r="2"/>',
    "food": '<path d="M7 3v8a3 3 0 0 0 6 0V3M10 3v18M17 3c-1.7 1.3-2.5 3.5-2.5 6.5V13H17v8"/>',
    "check": '<path d="m5 12 4.5 4.5L19 7"/>',
    "phone": '<path d="M5 3h3l2 5-2.5 1.5a11 11 0 0 0 5 5L14 12l5 2v3a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2Z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "pin": '<path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12Z"/><circle cx="12" cy="9" r="2.5"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "monitor": '<rect x="2" y="4" width="20" height="13" rx="2"/><path d="M8 21h8M12 17v4"/>',
    "video": '<rect x="2" y="6" width="14" height="12" rx="2"/><path d="m16 10 6-3v10l-6-3"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2 20a7 7 0 0 1 14 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 13.5a7 7 0 0 1 4 6.5"/>',
    "award": '<circle cx="12" cy="9" r="6"/><path d="m8.5 14-1.5 7 5-3 5 3-1.5-7"/>',
    "kit": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M12 10.5v6M9 13.5h6"/>',
    "heart": '<path d="M12 20s-8-4.6-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 9c0 6.4-8 11-8 11Z"/><path d="M7 11h2.5l1.5-2.5 2 5 1.5-2.5H17"/>',
    "sign": '<path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v4M12 17h.01"/>',
    "box": '<path d="m21 8-9-5-9 5 9 5 9-5Z"/><path d="M3 8v8l9 5 9-5V8M12 13v8"/>',
    "fire": '<path d="M12 22a7 7 0 0 0 7-7c0-4-3-6-4-10-2 2-3 4-3 6-1-1-2-2-2-4-2 2-5 5-5 8a7 7 0 0 0 7 7Z"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "wa": '<path d="M20.5 3.5A11 11 0 0 0 3.2 17.2L2 22l4.9-1.3A11 11 0 0 0 20.5 3.5Zm-8.5 17a9 9 0 0 1-4.6-1.3l-.3-.2-2.9.8.8-2.8-.2-.3A9 9 0 1 1 12 20.5Zm5-6.7c-.3-.1-1.6-.8-1.9-.9-.3-.1-.4-.1-.6.1l-.9 1.1c-.2.2-.3.2-.6.1a7.4 7.4 0 0 1-3.7-3.2c-.3-.5.3-.4.8-1.4.1-.2 0-.3 0-.5l-.9-2c-.2-.5-.5-.5-.6-.5h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-1 2.3 5.3 5.3 0 0 0 1.1 2.8 12 12 0 0 0 4.6 4.1c1.7.7 2.4.8 3.2.7.5-.1 1.6-.7 1.9-1.3.2-.6.2-1.2.2-1.3-.1-.2-.3-.2-.6-.4Z" fill="currentColor" stroke="none"/>',
    "fb": '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v7h4v-7h3l1-4h-4V8Z"/>',
    "ig": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
    "upload": '<path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"/>',
    "ext": '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
    "layers": '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/>',
    "euro": '<path d="M17 6a7 7 0 1 0 0 12M4 10h9M4 14h9"/>',
}


def icon(name, cls="ico"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_I[name]}</svg>')


def img(name):
    return IMG + name


def btn(label, href, kind="primary", ico="arrow", extra=""):
    i = icon(ico) if ico else ""
    return f'<a class="btn btn-{kind}" href="{href}"{extra}><span>{e(label)}</span>{i}</a>'




# --------------------------------------------------------------------------- layout
def header(active):
    links = "".join(
        f'<li><a href="{h}"{" aria-current=page" if h == active else ""}>{e(t)}</a></li>' for t, h in NAV)
    return f'''
<a class="skip" href="#main">Vai al contenuto</a>
<div class="topbar">
  <div class="wrap topbar-in">
    <span class="topbar-claim"><span class="dot-live"></span>Formazione • Sicurezza sul lavoro • Medicina del lavoro</span>
    <span class="topbar-links">
      <span>{icon("pin")}Grado (GO)</span>
      <a href="/contatti/">Richiedi informazioni</a>
      <a href="tel:{COMPANY['phones'][0][1]}">{COMPANY['phones'][0][0]}</a>
    </span>
  </div>
</div>
<header class="site-header" data-header>
  <div class="wrap header-in">
    <a class="brand" href="/" aria-label="Medicare Italia – Home">
      <img src="{img('logo-mark.webp')}" alt="" width="44" height="43">
      <span class="brand-txt"><strong>MEDICARE ITALIA</strong><small>Sicurezza e formazione</small></span>
    </a>
    <nav class="main-nav" aria-label="Menu principale" data-nav>
      <ul>{links}</ul>
      <div class="nav-mobile-extra">
        {btn("Richiedi consulenza", "/contatti/")}
        <div class="nav-mobile-contacts">
          <a href="tel:{COMPANY['phones'][0][1]}">{icon("phone")}{COMPANY['phones'][0][0]}</a>
          <a href="mailto:{COMPANY['emails'][1][1]}">{icon("mail")}{COMPANY['emails'][1][1]}</a>
        </div>
      </div>
    </nav>
    <div class="header-actions">
      <button class="icon-btn" type="button" data-search-open aria-label="Cerca nel sito">{icon("search")}</button>
      <a class="icon-btn" href="/cart/" aria-label="Carrello">{icon("cart")}<span class="badge" data-cart-count hidden>0</span></a>
      <a class="btn btn-primary btn-sm hide-md" href="/contatti/"><span>Preventivo</span>{icon("arrow")}</a>
      <button class="icon-btn burger" type="button" data-menu aria-label="Apri menu" aria-expanded="false">{icon("menu")}</button>
    </div>
  </div>
</header>
<div class="search-layer" data-search hidden>
  <div class="search-box" role="dialog" aria-modal="true" aria-labelledby="search-title">
    <div class="search-head">
      <div>
        <h2 id="search-title">Cerca nel sito Medicare Italia</h2>
        <p>Trova corsi, prodotti, servizi, pagine e articoli.</p>
      </div>
      <button class="icon-btn" type="button" data-search-close aria-label="Chiudi ricerca">{icon("close")}</button>
    </div>
    <label class="search-field">{icon("search")}<input type="search" placeholder="Es. primo soccorso, DVR, HACCP…" data-search-input aria-label="Cerca nel sito"></label>
    <ul class="search-results" data-search-results></ul>
  </div>
</div>'''


def footer():
    ph = "".join(
        f'<li><a href="tel:{n}">{icon("phone")}{t}</a><a class="wa-link" href="https://wa.me/{n[1:]}" target="_blank" rel="noopener">{icon("wa")}WhatsApp</a></li>'
        for t, n in COMPANY["phones"])
    em = "".join(f'<li><small>{e(l)}</small><a href="mailto:{m}">{icon("mail")}{m}</a></li>' for l, m in COMPANY["emails"])
    ex = "".join(f'<li><a href="{h}">{e(t)}</a></li>' for t, h in FOOTER_EXPLORE)
    return f'''
<footer class="site-footer">
  <div class="footer-glow" aria-hidden="true"></div>
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <a class="brand brand-light" href="/">
        <img src="{img('logo-mark.webp')}" alt="" width="52" height="51">
        <span class="brand-txt"><strong>MEDICARE ITALIA</strong><small>Sicurezza e formazione</small></span>
      </a>
      <p>Il partner professionale per formazione, salute, sicurezza e organizzazione aziendale.</p>
      <div class="socials">
        <span>Seguici</span>
        <a href="{COMPANY['facebook']}" target="_blank" rel="noopener" aria-label="Facebook – Medicare Italia Sicurezza sul Lavoro">{icon("fb")}</a>
        <a href="{COMPANY['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">{icon("ig")}</a>
      </div>
    </div>
    <div><h3>Esplora</h3><ul class="f-links">{ex}</ul></div>
    <div><h3>Contatti</h3><ul class="f-contacts">{ph}{em}</ul></div>
    <div>
      <h3>{COMPANY['name']}</h3>
      <address>{COMPANY['address']}<br>{COMPANY['city']}<br>P. IVA/C.F. {COMPANY['piva']}</address>
      <a class="map-link" href="{COMPANY['maps']}" target="_blank" rel="noopener">{icon("pin")}Apri in Google Maps</a>
    </div>
  </div>
  <div class="wrap footer-legal">
    <span>© 2026 {COMPANY['name']} · {COMPANY['capitale']} · {COMPANY['rea']}</span>
    <span>
      <a href="/privacy-policy/">Informativa sulla privacy</a>
      <a href="/cookie-policy-ue/">Cookie policy</a>
      <a href="/termini-condizioni/">Termini e condizioni</a>
      <a href="/modulo-recesso/">Modulo di recesso</a>
    </span>
  </div>
</footer>
<div class="wa-float" data-wa>
  <div class="wa-pop" data-wa-pop hidden>
    <p>Scrivici su WhatsApp</p>
    {"".join(f'<a href="https://wa.me/{n[1:]}" target="_blank" rel="noopener">{icon("wa")}{t}</a>' for t, n in COMPANY["phones"])}
  </div>
  <button type="button" class="wa-btn" data-wa-toggle aria-label="Contattaci su WhatsApp" aria-expanded="false">{icon("wa")}</button>
</div>'''


def page(path, title, desc, body, active=None, og_image=None, head_extra="", filename=None):
    canonical = f'<link rel="canonical" href="{ORIGIN + path}">' if not filename else '<meta name="robots" content="noindex">'
    html = f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{canonical}
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{ORIGIN}{og_image or img('foto-homepage-aula-v433.webp')}">
<meta name="theme-color" content="#0a2540">
<script>document.documentElement.classList.add("js")</script>
<link rel="icon" href="{img('medicare-italia-favicon-512-300x300.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css?v={VERSION}">
<script src="/assets/js/main.js?v={VERSION}" defer></script>
{head_extra}
</head>
<body>
{header(active or path)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
'''
    if filename:
        out = os.path.join(OUT, filename)
    else:
        out = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" else os.path.join(OUT, "index.html")
        GENERATED.append(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("  ", path)


def page_hero(eyebrow, h1, lead="", crumbs=None, extra="", tone=""):
    cr = ""
    if crumbs:
        items = '<a href="/">Home</a>' + "".join(
            f'<span>/</span>{"<a href=" + chr(34) + h + chr(34) + ">" + e(t) + "</a>" if h else "<span aria-current=page>" + e(t) + "</span>"}'
            for t, h in crumbs)
        cr = f'<nav class="crumbs" aria-label="Percorso">{items}</nav>'
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    return f'''
<section class="page-hero {tone}">
  <div class="aurora" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="grid-bg" aria-hidden="true"></div>
  <div class="wrap page-hero-in">
    {cr}
    <span class="eyebrow eyebrow-light">{e(eyebrow)}</span>
    <h1 class="reveal">{h1}</h1>
    {lead_html}
    {extra}
  </div>
</section>'''


def checklist(items, cls=""):
    return f'<ul class="checklist {cls}">' + "".join(f'<li>{icon("check")}<span>{e(i)}</span></li>' for i in items) + "</ul>"


def chips(links):
    return '<div class="chips">' + "".join(f'<a class="chip" href="{h}">{e(t)}{icon("arrow")}</a>' for t, h in links) + "</div>"


def cta_band(title="Hai bisogno di un piano completo?",
             text="Raccontaci la tua realtà aziendale: prepareremo una proposta su misura.",
             label="Richiedi un preventivo", href="/contatti/"):
    return f'''
<section class="section">
  <div class="wrap">
    <div class="cta-band reveal">
      <div class="cta-rings" aria-hidden="true"><i></i><i></i><i></i></div>
      <div>
        <h2>{e(title)}</h2>
        <p>{e(text)}</p>
      </div>
      <div class="cta-actions">
        {btn(label, href, "light")}
        <a class="cta-phone" href="tel:{COMPANY['phones'][0][1]}">{icon("phone")}<span><small>Oppure chiamaci</small>{COMPANY['phones'][0][0]}</span></a>
      </div>
    </div>
  </div>
</section>'''


def territory_marquee():
    row = "".join(f'<span>{icon("pin")}{e(t)}</span>' for t in TOWNS)
    return f'<div class="marquee" aria-label="Territori serviti"><div class="marquee-track">{row}{row}</div></div>'


# --------------------------------------------------------------------------- componenti corsi
def cat_by_key(k):
    return next(c for c in COURSE_CATS if c[0] == k)


MONTHS = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
MODE_ICO = {"presenza": "users", "videoconferenza": "video", "elearning": "monitor"}


def price_num(p):
    return float(p.replace(".", "").replace(",", ".")) if p else 0.0


def ship_num(s):
    m = re.search(r"([\d.,]+)\s*€", s or "")
    return price_num(m.group(1)) if m else 0.0


def item_url(c):
    return f"/product/{c['slug']}/"


def cart_payload(c, kind):
    meta = MODES.get(c.get("mode"), "") if kind == "course" else ""
    if c.get("days"):
        meta = c["days"][0][0] + (" · " + MODES[c["mode"]] if c.get("mode") else "")
    data = {"id": c["id"], "slug": c["slug"], "title": c["title"], "price": price_num(c["price"]), "kind": kind,
            "img": c["img"], "url": item_url(c), "meta": meta, "max": c.get("seats") or 99,
            "ship": ship_num(c.get("shipping"))}
    return e(json.dumps(data, ensure_ascii=False), quote=True)


def add_button(c, kind, cls="icon-btn add-btn", label=""):
    if not c.get("in_stock", True):
        return '<span class="tag">Esaurito</span>'
    inner = f'{icon("cart")}<span>{e(label)}</span>' if label else icon("cart")
    aria = "" if label else f' aria-label="Aggiungi al carrello: {e(c["title"])}"'
    return f'<button type="button" class="{cls}" data-add="{cart_payload(c, kind)}"{aria}>{inner}</button>'


def linkrow(h):
    """Paragrafi fatti solo di link → riga di chip; link a prodotti inesistenti → calendario corsi."""
    h = re.sub(r'href="/product/([^/"]+)/"', lambda m: m.group(0) if m.group(1) in ALL_SLUGS else 'href="/corsi/"', h)
    def sub(m):
        links = re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', m.group(1))
        if len(links) < 2:
            return m.group(0)
        return chips([(html_lib.unescape(t), html_lib.unescape(u)) for u, t in links])
    return re.sub(r"<p>((?:\s*(?:·\s*)?<a [^>]*>[^<]*</a>\s*)+)</p>", sub, h)


def course_card(c):
    cat = cat_by_key(c["primary"]) if c["primary"] in {k[0] for k in COURSE_CATS} else COURSE_CATS[2]
    color = cat[4]
    if c["days"]:
        d0 = c["days"][0][0].split("/")
        date_badge = f'<div class="date-badge"><b>{d0[0]}</b><span>{MONTHS[int(d0[1]) - 1]}</span><small>{d0[2]}</small></div>'
        status = "Edizione disponibile"
        sched = "".join(
            f'<li><span class="day-n">{i + 1}ª giornata</span>{icon("cal")}{d}'
            f'{(" " + icon("clock") + e(t)) if t else ""}</li>'
            for i, (d, t) in enumerate(c["days"]))
        if c["note"]:
            sched += f'<li class="muted">{icon("clock")}{e(c["note"])}</li>'
        sched = f'<ul class="sched">{sched}</ul>'
    else:
        date_badge = f'<div class="date-badge online">{icon("monitor")}<small>online</small></div>'
        status = "Disponibile online"
        sched = '<ul class="sched"><li>' + icon("monitor") + 'Corso interamente online</li><li>' + icon("layers") + \
                'Da computer, tablet o smartphone</li><li>' + icon("clock") + 'Senza date e orari prestabiliti</li></ul>'
    meta = [f'<span class="tag">{icon(MODE_ICO[c["mode"]])}{MODES[c["mode"]]}</span>']
    if c["validity"]:
        meta.append(f'<span class="tag">{icon("award")}Validità attestato {c["validity"]}</span>')
    place = ""
    if c["place"]:
        place = (f'<a class="place" href="{COMPANY["maps"]}" target="_blank" rel="noopener">{icon("pin")}'
                 f'<span>{e(c["place"])}</span><em>Apri in Google Maps</em></a>')
    seats = ""
    if c["seats"]:
        low = " low" if c["seats"] <= 7 else ""
        seats = f'<span class="seats{low}"><i></i>{c["seats"]} posti disponibili</span>'
    elif c["mode"] == "elearning":
        seats = '<span class="seats online"><i></i>Accesso online</span>'
    cats = set(c["cats"]) | {c["primary"]}
    search = " ".join([c["title"], MODES[c["mode"]]] + [cat_by_key(k)[1] for k in cats if k in {x[0] for x in COURSE_CATS}]).lower()
    url = item_url(c)
    return f'''
<article class="course reveal" style="--c:{color}" data-cats="{" ".join(sorted(cats))}" data-mode="{c["mode"]}" data-q="{e(search)}">
  <a class="course-media" href="{url}" tabindex="-1" aria-hidden="true">
    <img src="{c['img']}" alt="" loading="lazy" width="768" height="512">
    {date_badge}
    <span class="course-cat">{e(cat[1])}</span>
  </a>
  <div class="course-body">
    <span class="status"><i></i>{status}</span>
    <h3><a href="{url}">{e(c['title'])}</a></h3>
    {sched}
    <div class="tags">{"".join(meta)}</div>
    {place}
    <div class="course-foot">
      <div class="price"><b>{c['price']} €</b><small>IVA inc.</small>{seats}</div>
      <div class="foot-actions">
        {add_button(c, "course")}
        <a class="btn btn-primary btn-sm" href="{url}"><span>Scheda corso</span>{icon("arrow")}</a>
      </div>
    </div>
  </div>
</article>'''


def product_card(p, i=0):
    cat = next((c for c in SHOP_CATS if c[0] == p["primary"]), SHOP_CATS[-1])
    url = item_url(p)
    return f'''
<article class="product reveal" data-cat="{p['primary']}" style="--d:{(i % 4) * 70}ms">
  <a class="product-media" href="{url}"><img src="{p['img']}" alt="{e(p['title'])}" loading="lazy" width="300" height="300"></a>
  <div class="product-body">
    <span class="product-cat">{e(cat[1])}</span>
    <h2><a href="{url}">{e(p['title'])}</a></h2>
    <div class="product-foot">
      <span class="price"><b>{p['price']} €</b><small>IVA inc.</small></span>
      {add_button(p, "product", "btn btn-primary btn-sm add-btn", "Aggiungi al carrello")}
    </div>
  </div>
</article>'''


def cat_card(k, title, text, image, color, i):
    return f'''
<a class="cat-card reveal" href="/product-category/{k}/" style="--c:{color};--d:{i * 60}ms">
  <div class="cat-media"><img src="{img(image)}" alt="" loading="lazy"></div>
  <div class="cat-body">
    <h3>{e(title)}</h3>
    <p>{e(text)}</p>
    <span class="link-arrow">Sfoglia i nostri corsi{icon("arrow")}</span>
  </div>
</a>'''


def newsletter():
    return f'''
<section class="section" id="newsletter">
  <div class="wrap news-grid">
    <div class="reveal">
      <span class="eyebrow">Newsletter</span>
      <h2>Aggiornamenti normativi utili, <span class="hl">solo quando servono</span></h2>
      <p class="lead-dark">Iscriviti per ricevere esclusivamente aggiornamenti normativi rilevanti, chiarimenti operativi e comunicazioni utili per chi utilizza il sito.</p>
      {checklist(["Novità su sicurezza sul lavoro, HACCP, antincendio, primo soccorso e medicina del lavoro.",
                  "Comunicazioni di servizio realmente utili per clienti, aziende e professionisti.",
                  "Nessun invio superfluo: solo contenuti pratici e pertinenti."])}
    </div>
    <form class="card form-card reveal" data-form="newsletter" data-to="{COMPANY['emails'][1][1]}" novalidate>
      <span class="pill">{icon("mail")}Solo comunicazioni utili</span>
      <h3>Resta aggiornato</h3>
      <p>Lascia il tuo indirizzo e-mail per ricevere gli aggiornamenti direttamente nella tua casella di posta.</p>
      <label class="field"><span>E-mail *</span><input type="email" name="email" required autocomplete="email" placeholder="nome@azienda.it"></label>
      <label class="hp" aria-hidden="true">Sito web<input type="text" name="website" tabindex="-1" autocomplete="off"></label>
      <label class="consent"><input type="checkbox" name="privacy" required><span>Ho letto e accetto l’<a href="/privacy-policy/">Informativa sulla privacy</a>.</span></label>
      <button class="btn btn-primary btn-block" type="submit"><span>Iscriviti agli aggiornamenti</span>{icon("arrow")}</button>
      <small class="form-note">Riceverai solo aggiornamenti normativi utili o comunicazioni di servizio per chi utilizza il sito.</small>
      <div class="form-msg" data-form-msg hidden></div>
    </form>
  </div>
</section>'''


# =========================================================================== PAGINE
def home():
    points = [
        ("01", "Un solo partner", "Formazione, HSE e medicina del lavoro", "target"),
        ("02", "Più competenze, più sicurezza", "Corsi in presenza a Grado o presso la tua sede.", "shield"),
        ("03", "Acquisto online", "Corsi e prodotti in pochi passaggi", "cart"),
        ("04", "Supporto reale", "Persone, risposte e soluzioni concrete", "users"),
    ]
    services = [
        ("/consulenza-hse/", "Consulenza HSE", "Supporto continuativo per salute, sicurezza e ambiente.", "shield"),
        ("/sicurezza-sul-lavoro/", "DVR e RSPP esterno", "Redazione e aggiornamento DVR, incarico RSPP esterno e supporto alla tua azienda.", "doc"),
        ("/medicina-del-lavoro/", "Medicina del lavoro", "Medico competente, visite e sorveglianza sanitaria.", "steth"),
        ("/haccp-autocontrollo/", "Piani di autocontrollo HACCP", "Formazione, redazione e aggiornamento dei piani di autocontrollo.", "food"),
    ]
    svc = "".join(f'''
<a class="svc-card reveal" href="{h}" style="--d:{i * 70}ms">
  <span class="svc-ico">{icon(ic)}</span>
  <h3>{e(t)}</h3>
  <p>{e(p)}</p>
  <span class="svc-go">{icon("arrow")}</span>
</a>''' for i, (h, t, p, ic) in enumerate(services))
    pts = "".join(f'<li class="reveal" style="--d:{i * 80}ms"><span class="pt-n">{n}</span><span class="pt-ico">{icon(ic)}</span><b>{e(t)}</b><span>{e(s)}</span></li>'
                  for i, (n, t, s, ic) in enumerate(points))
    cats = "".join(cat_card(*c, i) for i, c in enumerate(COURSE_CATS))
    shop = "".join(f'''
<a class="shop-card reveal" href="/product-category/{k}/" style="--d:{i * 70}ms">
  <span class="shop-ico">{icon(ic)}</span>
  <h3>{e(t)}</h3><p>{e(p)}</p>
  <span class="link-arrow">Scopri i prodotti{icon("arrow")}</span>
</a>''' for i, (k, t, p, ic) in enumerate(SHOP_CATS))
    svc_list = ["Consulenza HSE e incarico RSPP esterno", "DVR, DUVRI, POS e procedure operative",
                "Piani di emergenza, evacuazione e formazione", "Medico Competente e sorveglianza sanitaria",
                "Formazione HACCP e redazione dei piani di autocontrollo", "PES, PAV, PEI e formazione specialistica"]
    svc_ul = "".join(f'<li class="reveal" style="--d:{i * 60}ms"><span>{i + 1:02d}</span>{e(s)}</li>' for i, s in enumerate(svc_list))
    orbit = ["Formazione", "RSPP", "Consulenza HSE", "Medicina del lavoro"]
    orbit_html = "".join(f'<span class="orb" style="--i:{i}">{e(o)}</span>' for i, o in enumerate(orbit))

    body = f'''
<section class="hero">
  <div class="aurora" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="grid-bg" aria-hidden="true"></div>
  <div class="wrap hero-in">
    <div class="hero-copy">
      <span class="eyebrow eyebrow-light reveal">Formazione e consulenza per le aziende</span>
      <h1 class="reveal">Formazione e sicurezza, <span class="grad">in un unico partner</span></h1>
      <p class="lead reveal">Corsi di aggiornamento professionale, primo soccorso, sicurezza sul lavoro, antincendio e HACCP. Consulenza HSE, DVR, piani di autocontrollo e medicina del lavoro con un servizio coordinato e concreto.</p>
      <div class="hero-ctas reveal">
        {btn("Sfoglia i nostri corsi", "/corsi/", "primary")}
        {btn("Richiedi consulenza", "/contatti/", "ghost", None)}
      </div>
      <ul class="hero-chips reveal">
        <li>{icon("check")}Formazione in presenza e online</li>
        <li>{icon("check")}Consulenza coordinata</li>
        <li>{icon("check")}Shop professionale</li>
      </ul>
    </div>
    <div class="hero-visual reveal" data-tilt>
      <div class="hero-photo">
        <img src="{img('foto-homepage-aula-v433.webp')}" alt="L’aula corsi di Medicare Italia a Grado" width="1200" height="833" fetchpriority="high">
      </div>
      <div class="float-card fc-1">{icon("cal")}<span><b>Calendario corsi</b><small>Prossime date disponibili</small></span></div>
      <div class="float-card fc-2">{icon("pin")}<span><b>Grado (GO)</b><small>Aula corsi e sede</small></span></div>
      <div class="float-card fc-3"><span class="pulse"></span><span><b>E-learning</b><small>Da telefono, PC o tablet</small></span></div>
    </div>
  </div>
  <div class="wrap">
    <ul class="points">{pts}</ul>
  </div>
</section>

<section class="section svc-section">
  <div class="wrap">
    <div class="svc-grid">{svc}</div>
  </div>
</section>

<section class="section" id="formazione">
  <div class="wrap">
    <div class="sec-head reveal">
      <div>
        <span class="eyebrow">Formazione</span>
        <h2>Primo soccorso, antincendio e <span class="hl">sicurezza dei lavoratori</span></h2>
      </div>
      <div class="sec-head-side">
        <p>Consulta date, programmi e prezzi oppure richiedi un corso per la tua azienda.</p>
        {btn("Calendario corsi", "/corsi/", "outline")}
      </div>
    </div>
    <div class="cat-grid">{cats}</div>
  </div>
</section>

<section class="section territory">
  <div class="wrap terr-grid">
    <div class="reveal">
      <span class="eyebrow">Corsi e servizi per le aziende del territorio</span>
      <h2>Da Grado, per le imprese del <span class="hl">Friuli Venezia Giulia</span></h2>
      <p class="lead-dark">Lavoriamo con le aziende di Grado e dei comuni limitrofi come Aquileia, Cervignano del Friuli, Monfalcone e Ronchi dei Legionari, e nelle province di Gorizia, Trieste, Udine e Pordenone.</p>
      <p>Le edizioni in calendario riportano sede e modalità di svolgimento. Per i corsi presso la tua azienda e per DVR, RSPP esterno e HACCP, concordiamo attività, sopralluoghi e organizzazione in base alle tue esigenze.</p>
      {btn("Chiedi un preventivo per la tua azienda", "/contatti/")}
    </div>
    <div class="radar reveal" aria-hidden="true">
      <div class="radar-ring r1"></div><div class="radar-ring r2"></div><div class="radar-ring r3"></div>
      <div class="radar-sweep"></div>
      <div class="radar-core"><img src="{img('logo-mark.webp')}" alt=""><b>Grado</b></div>
      <span class="rp" style="--x:58%;--y:36%">Aquileia</span>
      <span class="rp" style="--x:30%;--y:30%">Cervignano</span>
      <span class="rp" style="--x:72%;--y:58%">Monfalcone</span>
      <span class="rp" style="--x:66%;--y:22%">Ronchi dei Legionari</span>
      <span class="rp far" style="--x:80%;--y:17%">Gorizia</span>
      <span class="rp far" style="--x:84%;--y:80%">Trieste</span>
      <span class="rp far" style="--x:24%;--y:13%">Udine</span>
      <span class="rp far" style="--x:12%;--y:56%">Pordenone</span>
    </div>
  </div>
  {territory_marquee()}
</section>

<section class="section" id="shop">
  <div class="wrap">
    <div class="sec-head reveal">
      <div>
        <span class="eyebrow">E-commerce</span>
        <h2>Shop online <span class="hl">per la sicurezza</span></h2>
      </div>
      <div class="sec-head-side">
        <p>Attrezzature, dispositivi e materiali selezionati per aziende, professionisti ed enti.</p>
        {btn("Visita tutto lo shop", "/shop/", "outline")}
      </div>
    </div>
    <div class="shop-grid">{shop}</div>
  </div>
</section>

<section class="section dark-band">
  <div class="aurora" aria-hidden="true"><i></i><i></i></div>
  <div class="wrap integ-grid">
    <div class="orbit reveal" aria-hidden="true">
      <div class="orbit-ring"></div>
      <div class="orbit-core"><img src="{img('logo-mark.webp')}" alt=""></div>
      <div class="orbit-spin">{orbit_html}</div>
    </div>
    <div class="reveal">
      <span class="eyebrow eyebrow-light">Soluzione integrata</span>
      <p class="integ-line">Formazione · RSPP · Consulenza HSE · Medicina del lavoro</p>
      <h2>Una regia unica per la tua azienda</h2>
      <p class="lead">Formazione, documentazione, scadenze e sorveglianza sanitaria coordinate.</p>
      <div class="values"><span>{icon("shield")}Prevenzione</span><span>{icon("doc")}Conformità</span><span>{icon("users")}Assistenza</span></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap compl-grid">
    <div class="reveal sticky-col">
      <span class="eyebrow">Servizi aziendali</span>
      <h2>Dalla conformità alla <span class="hl">prevenzione reale</span></h2>
      <p class="lead-dark">Analizziamo l’organizzazione e costruiamo un servizio commisurato ai rischi, alle persone e alle attività svolte.</p>
      {btn("Richiedi consulenza", "/contatti/")}
    </div>
    <ol class="num-list">{svc_ul}</ol>
  </div>
</section>

{newsletter()}
{cta_band()}
'''
    page("/", "Medicare Italia – Formazione, sicurezza sul lavoro e medicina del lavoro a Grado (GO)",
         "Corsi di primo soccorso, antincendio, sicurezza sul lavoro, HACCP e BLSD. Consulenza HSE, DVR, RSPP esterno e medicina del lavoro in Friuli Venezia Giulia.",
         body)


def corsi():
    order = [("aggiornamento-professionale", "Calendario corsi", "Aggiornamento professionale"),
             ("primo-soccorso", "Calendario corsi", "Primo soccorso aziendale"),
             ("sicurezza-sul-lavoro", "Calendario corsi", "Sicurezza sul lavoro"),
             ("corsi-blsd", "Calendario corsi", "Corsi BLSD"),
             ("corsi-elearning", "Formazione online", "Corsi e-learning")]
    n_pres = sum(1 for c in COURSES if c["mode"] == "presenza")
    n_vid = sum(1 for c in COURSES if c["mode"] == "videoconferenza")
    n_el = sum(1 for c in COURSES if c["mode"] == "elearning")
    filters = '<button class="fchip is-on" type="button" data-filter="all">Tutti <b>' + str(len(COURSES)) + "</b></button>"
    for k, t, _, _, col in COURSE_CATS:
        n = sum(1 for c in COURSES if k in c["cats"] or c["primary"] == k)
        filters += f'<button class="fchip" type="button" data-filter="{k}" style="--c:{col}">{e(t)} <b>{n}</b></button>'
    modes = '<div class="seg" role="group" aria-label="Modalità">' + \
            '<button type="button" class="is-on" data-mode="all">Tutte</button>' + \
            "".join(f'<button type="button" data-mode="{k}">{icon({"presenza": "users", "videoconferenza": "video", "elearning": "monitor"}[k])}{v}</button>'
                    for k, v in MODES.items()) + "</div>"

    groups = ""
    for k, eb, title in order:
        items = [c for c in COURSES if c["primary"] == k]
        sub = "Corsi disponibili online, senza date e orari prestabiliti." if k == "corsi-elearning" \
            else "Le edizioni sono ordinate dalla data disponibile più vicina alla più lontana."
        groups += f'''
<div class="cgroup" data-group="{k}">
  <div class="cgroup-head"><span class="eyebrow">{e(eb)}</span><h2>{e(title)}</h2><p>{sub}</p></div>
  <div class="course-grid">{"".join(course_card(c) for c in items)}</div>
</div>'''
    anti = cat_by_key("antincendio")
    empty_anti = f'''
<div class="cgroup cgroup-info" data-group="antincendio" hidden>
  <div class="info-card reveal" style="--c:{anti[4]}">
    <span class="svc-ico">{icon("fire")}</span>
    <div>
      <span class="eyebrow">Corsi Antincendio in Friuli Venezia Giulia</span>
      <h2>Antincendio</h2>
      <p class="lead-dark">{e(anti[2])}</p>
      <div class="prose">{linkrow(CATEGORIES["antincendio"]["html"])}</div>
      <p class="muted">Al momento non ci sono edizioni pubblicate in calendario.</p>
      <div class="btn-row">{btn("Richiedi un corso antincendio per la tua azienda", "/contatti/")}{btn("Corsi di primo soccorso", "/product-category/primo-soccorso/", "outline")}</div>
    </div>
  </div>
</div>'''

    body = page_hero("Calendario corsi", 'Prossime <span class="grad">date disponibili</span>',
                     'Scegli tra i corsi di primo soccorso, i corsi antincendio e la formazione sulla sicurezza per i lavoratori. Ogni edizione indica date, orari, sede, prezzo e disponibilità: apri la scheda per iscriverti online.',
                     [("Corsi", None)],
                     f'''<div class="hero-stats">
  <a href="#catalogo" data-quick-mode="presenza"><b>{n_pres}</b><span>Corsi in presenza<small>Date, orari e formazione nella nostra aula</small></span>{icon("arrow")}</a>
  <a href="#catalogo" data-quick-mode="videoconferenza"><b>{n_vid}</b><span>In videoconferenza<small>Lezioni in diretta con il docente</small></span>{icon("arrow")}</a>
  <a href="#catalogo" data-quick-mode="elearning"><b>{n_el}</b><span>Corsi e-learning<small>Formazione online disponibile quando vuoi</small></span>{icon("arrow")}</a>
</div>''')
    body += f'''
<section class="section catalog" id="catalogo">
  <div class="wrap">
    <p class="note-box reveal">{icon("pin")}<span>La sede è a Grado (GO). Ci rivolgiamo alle aziende di Grado e dei comuni limitrofi, oltre che alle imprese delle province di Gorizia, Trieste, Udine e Pordenone. Verifica sempre il luogo effettivo e la modalità di svolgimento nella scheda del corso scelto.</span></p>
    <div class="filterbar" data-filterbar>
      <div class="filter-top">
        <label class="search-inline">{icon("search")}<input type="search" placeholder="Cerca un corso…" data-course-search aria-label="Cerca un corso"></label>
        {modes}
      </div>
      <div class="fchips">{filters}</div>
    </div>
    <p class="result-count" data-count aria-live="polite"></p>
    {groups}
    {empty_anti}
    <div class="empty" data-empty hidden>{icon("search")}<p>Nessun corso corrisponde ai filtri selezionati.</p><button class="btn btn-outline btn-sm" type="button" data-reset><span>Mostra tutti i corsi</span></button></div>
  </div>
</section>

<section class="section">
  <div class="wrap split-card reveal">
    <div>
      <span class="eyebrow">Formazione aziendale</span>
      <h2>Organizza la formazione per la tua azienda</h2>
      <p class="lead-dark">Se devi formare più persone o non trovi un’edizione adatta, richiedi una proposta aziendale. Possiamo valutare corsi presso la tua sede, concordando partecipanti, spazi necessari, programma e modalità di svolgimento. Indicaci il comune, il corso richiesto, il numero dei lavoratori e le eventuali scadenze.</p>
      {btn("Richiedi un preventivo per un corso aziendale", "/contatti/")}
      <p class="small">Per coordinare formazione e documentazione scopri i servizi di <a href="/sicurezza-sul-lavoro/">DVR e RSPP esterno</a> e i <a href="/haccp-autocontrollo/">piani di autocontrollo HACCP</a>.</p>
    </div>
    <div class="split-media"><img src="{img('foto-homepage-aula-v433.webp')}" alt="Aula corsi Medicare Italia" loading="lazy"></div>
  </div>
</section>

<section class="section territory slim">
  <div class="wrap narrow center reveal">
    <span class="eyebrow">Servizi nel territorio</span>
    <h2>Corsi professionali a Grado, Gorizia e in Friuli Venezia Giulia</h2>
    <p class="lead-dark">Medicare Italia organizza corsi in presenza e percorsi aziendali dedicati per imprese e professionisti di Grado, Monfalcone, Gorizia, Trieste, Udine e dell’intero Friuli Venezia Giulia. Consulta il calendario per trovare le prossime edizioni di primo soccorso, antincendio, sicurezza sul lavoro, HACCP e aggiornamento professionale.</p>
    {chips([("Primo soccorso aziendale", "/product-category/primo-soccorso/"), ("Antincendio", "/product-category/antincendio/"), ("Sicurezza sul lavoro", "/product-category/sicurezza-sul-lavoro/"), ("Formazione HACCP", "/product-category/haccp/")])}
  </div>
  {territory_marquee()}
</section>
'''
    page("/corsi/", "Calendario corsi – Medicare Italia",
         "Corsi di primo soccorso, antincendio, sicurezza sul lavoro, BLSD, HACCP ed e-learning a Grado (GO) e in Friuli Venezia Giulia: date, orari, sede e prezzi.", body)


def service_page(path, eyebrow, h1, h2, paras, items, links, title, desc, extra_sections="", side_title="Il servizio comprende",
                 hero_ico="shield", related_title=None, related_text=None, related_links=None, crumb=""):
    ps = "".join(f'<p>{p}</p>' for p in paras)
    rel = ""
    if related_title:
        rel = f'''
<section class="section soft">
  <div class="wrap narrow center reveal">
    <h2>{e(related_title)}</h2>
    <p class="lead-dark">{e(related_text)}</p>
    {chips(related_links)}
  </div>
</section>'''
    body = page_hero(eyebrow, h1, "", [(crumb, None)],
                     f'<div class="hero-ico">{icon(hero_ico)}</div>')
    body += f'''
<section class="section">
  <div class="wrap svc-layout">
    <article class="prose reveal">
      <h2>{h2}</h2>
      {ps}
      <div class="btn-row">{"".join(btn(t, h, "primary" if i == len(links) - 1 else "outline") for i, (t, h) in enumerate(links))}</div>
    </article>
    <aside class="side-card reveal">
      <div class="side-card-in">
        <span class="pill">{icon("check")}{e(side_title)}</span>
        {checklist(items)}
        {btn("Richiedi un preventivo", "/contatti/", "primary")}
        <div class="side-contacts">
          <a href="tel:{COMPANY['phones'][0][1]}">{icon("phone")}{COMPANY['phones'][0][0]}</a>
          <a href="mailto:{COMPANY['emails'][0][1]}">{icon("mail")}{COMPANY['emails'][0][1]}</a>
        </div>
      </div>
    </aside>
  </div>
</section>
{extra_sections}
{rel}
{cta_band()}
'''
    page(path, title, desc, body)


def sicurezza():
    paras = [
        "Medicare Italia offre il servizio di RSPP esterno e il supporto per la redazione e l’aggiornamento del DVR. La consulenza sulla sicurezza sul lavoro parte dalle attività, dagli ambienti e dalle mansioni della tua azienda.",
        "La sede è a Grado (GO). Seguiamo le imprese dei comuni del territorio circostante, tra cui Aquileia, Cervignano del Friuli, Monfalcone e Ronchi dei Legionari, e delle province di Gorizia, Trieste, Udine e Pordenone. Sopralluoghi e organizzazione del servizio vengono concordati in base alla sede operativa e alle esigenze dell’impresa.",
        "Per il Documento di Valutazione dei Rischi affianchiamo l’azienda nella raccolta delle informazioni, nell’analisi delle lavorazioni e dei rischi presenti e nella predisposizione o revisione del documento. Colleghiamo le misure di prevenzione alle procedure e alla formazione dei lavoratori.",
        "L’incarico di Responsabile del Servizio di Prevenzione e Protezione viene definito considerando l’organizzazione e le attività aziendali. Il servizio RSPP esterno può comprendere sopralluoghi, supporto alla valutazione dei rischi, consulenza continuativa, documentazione e pianificazione delle attività di prevenzione.",
        "Supportiamo anche la predisposizione di DUVRI, POS, procedure operative e piani di emergenza ed evacuazione. Organizziamo corsi di primo soccorso, antincendio e sicurezza per i lavoratori: puoi consultare le categorie qui sotto per scegliere il percorso e verificare le edizioni disponibili. Per le attività alimentari offriamo inoltre piani di autocontrollo e consulenza HACCP.",
        "<strong>Per richiedere un preventivo</strong>, indicaci il comune della sede operativa, il settore di attività, il numero dei lavoratori e se ti occorrono un nuovo DVR, un aggiornamento o l’incarico di RSPP esterno. Queste informazioni ci aiutano a definire una proposta pertinente.",
    ]
    items = ["Valutazione dei rischi e redazione DVR", "DUVRI", "POS", "Procedure operative", "Incarico RSPP esterno",
             "Consulenza continuativa", "Piani di emergenza ed evacuazione", "Formazione ai sensi del D.Lgs. 81/2008"]
    links = [("Corsi di primo soccorso", "/product-category/primo-soccorso/"), ("Corsi antincendio", "/product-category/antincendio/"),
             ("Formazione per i lavoratori", "/product-category/sicurezza-sul-lavoro/"),
             ("Richiedi un preventivo per DVR e RSPP esterno", "/contatti/")]
    extra = f'''
<section class="section soft">
  <div class="wrap">
    <div class="duo">
      <article class="feature-card reveal" id="mi-rspp-esterno">
        <span class="svc-ico">{icon("shield")}</span>
        <h2>RSPP esterno per la tua azienda</h2>
        <p>L’incarico di RSPP esterno si inserisce nella gestione della prevenzione aziendale. Medicare Italia offre un riferimento per sopralluoghi, valutazione dei rischi, documentazione e coordinamento degli adempimenti, con un servizio definito in base all’attività e all’organizzazione dell’impresa.</p>
      </article>
      <article class="feature-card reveal" id="mi-dvr" style="--d:80ms">
        <span class="svc-ico">{icon("doc")}</span>
        <h2>DVR e valutazione dei rischi</h2>
        <p>La redazione e l’aggiornamento del DVR partono dalle lavorazioni, dagli ambienti e dalle mansioni effettive. Il servizio comprende l’analisi dei rischi e il supporto nella predisposizione della documentazione, collegando le misure di prevenzione alla formazione e alla medicina del lavoro.</p>
        <p class="muted">Per le richieste da Cervignano del Friuli e dagli altri comuni della regione, indicaci sedi operative, attività svolte e numero dei lavoratori: sono gli elementi da cui partire per definire il servizio.</p>
      </article>
    </div>
    <div class="center reveal" style="margin-top:2rem">
      {chips([("Piani di autocontrollo HACCP", "/haccp-autocontrollo/"), ("Consulenza HSE", "/consulenza-hse/"), ("Medicina del lavoro", "/medicina-del-lavoro/"), ("Corsi sicurezza sul lavoro", "/product-category/sicurezza-sul-lavoro/")])}
    </div>
  </div>
</section>'''
    service_page("/sicurezza-sul-lavoro/", "Servizi in Friuli Venezia Giulia",
                 'Sicurezza sul lavoro e <span class="grad">RSPP</span> in Friuli Venezia Giulia',
                 "DVR e RSPP esterno per le aziende del Friuli Venezia Giulia", paras, items, links,
                 "Sicurezza sul lavoro, DVR e RSPP esterno in Friuli Venezia Giulia – Medicare Italia",
                 "RSPP esterno, redazione e aggiornamento DVR, DUVRI, POS, piani di emergenza e formazione D.Lgs. 81/2008 per aziende di Grado, Gorizia e FVG.",
                 extra, hero_ico="shield", crumb="Sicurezza sul lavoro")


def medicina():
    paras = [
        "Medicare Italia organizza servizi di medicina del lavoro e sorveglianza sanitaria per aziende, imprese e professionisti, con sede a Grado e attività in tutta la provincia di Gorizia e nel Friuli Venezia Giulia.",
        "Il servizio comprende la nomina del Medico Competente, l’organizzazione delle visite mediche preventive e periodiche, la definizione del protocollo sanitario in relazione ai rischi lavorativi e la gestione delle scadenze previste dalla normativa.",
        "Operiamo direttamente presso le aziende a Grado, Gorizia, Monfalcone, Ronchi dei Legionari, Staranzano, Gradisca d’Isonzo e Cormons, con possibilità di organizzare il servizio anche negli altri comuni del Friuli Venezia Giulia.",
        "La sorveglianza sanitaria viene organizzata in funzione dell’attività svolta e dei rischi presenti nell’ambiente di lavoro, coordinando gli accertamenti sanitari e gli adempimenti previsti dal D.Lgs. 81/2008.",
    ]
    items = ["Nomina del Medico Competente", "Sorveglianza sanitaria dei lavoratori", "Visite mediche preventive e periodiche",
             "Definizione del protocollo sanitario", "Accertamenti sanitari previsti in relazione ai rischi lavorativi",
             "Giudizi di idoneità alla mansione", "Programmazione delle visite e delle scadenze",
             "Sopralluoghi negli ambienti di lavoro", "Collaborazione alla valutazione dei rischi",
             "Gestione della documentazione sanitaria"]
    links = [("Sicurezza sul lavoro", "/sicurezza-sul-lavoro/"), ("Consulenza HSE", "/consulenza-hse/"),
             ("Consulta i corsi disponibili", "/corsi/"), ("Richiedi un preventivo", "/contatti/")]
    service_page("/medicina-del-lavoro/", "Servizi in Friuli Venezia Giulia", 'Medicina <span class="grad">del lavoro</span>',
                 "Medicina del lavoro e Medico Competente a Grado, Gorizia e in Friuli Venezia Giulia", paras, items, links,
                 "Medicina del lavoro e Medico Competente a Grado e Gorizia – Medicare Italia",
                 "Nomina del Medico Competente, sorveglianza sanitaria, visite preventive e periodiche e protocollo sanitario per aziende in Friuli Venezia Giulia.",
                 hero_ico="steth", crumb="Medicina del lavoro")


def consulenza():
    paras = [
        "Medicare Italia offre servizi di consulenza HSE per aziende, imprese e organizzazioni che necessitano di un supporto integrato nella gestione della salute, della sicurezza sul lavoro e degli aspetti ambientali.",
        "Dalla sede di Grado affianchiamo aziende di Gorizia, Monfalcone, Ronchi dei Legionari, Staranzano, Gradisca d’Isonzo e Cormons, con possibilità di intervento anche negli altri territori del Friuli Venezia Giulia.",
        "La consulenza HSE comprende l’analisi dell’organizzazione aziendale, il supporto nella verifica della conformità normativa, l’individuazione delle criticità, la pianificazione degli interventi e il coordinamento degli adempimenti in materia di salute, sicurezza e ambiente.",
        "L’attività può comprendere audit HSE, supporto documentale, procedure operative, gestione delle scadenze, coordinamento della formazione, supporto alla valutazione dei rischi e assistenza nella gestione dei sistemi organizzativi interni.",
        "L’obiettivo è fornire all’azienda un unico riferimento operativo per organizzare in modo strutturato e continuativo gli adempimenti HSE, con interventi calibrati sulle caratteristiche dell’attività e sui rischi effettivamente presenti.",
    ]
    items = ["Consulenza HSE continuativa", "Audit HSE e verifica della conformità normativa",
             "Supporto alla gestione salute, sicurezza e ambiente", "Analisi dell’organizzazione aziendale",
             "Supporto documentale HSE", "Procedure operative", "Coordinamento degli adempimenti",
             "Gestione delle scadenze", "Supporto alla valutazione dei rischi", "Coordinamento della formazione",
             "Supporto ai sistemi organizzativi interni"]
    links = [("Sicurezza sul lavoro", "/sicurezza-sul-lavoro/"), ("Medicina del lavoro", "/medicina-del-lavoro/"),
             ("Consulta i corsi disponibili", "/corsi/"), ("Richiedi un preventivo", "/contatti/")]
    service_page("/consulenza-hse/", "Consulenza HSE in Friuli Venezia Giulia",
                 'Consulenza HSE e <span class="grad">RSPP esterno</span> in Friuli Venezia Giulia',
                 "Consulenza HSE per aziende a Grado, Gorizia e in Friuli Venezia Giulia", paras, items, links,
                 "Consulenza HSE e RSPP esterno in Friuli Venezia Giulia – Medicare Italia",
                 "Consulenza HSE continuativa, audit, procedure operative, gestione delle scadenze e coordinamento degli adempimenti per aziende di Grado, Gorizia e FVG.",
                 hero_ico="target", crumb="Servizi HSE",
                 related_title="Consulenza HSE e servizi collegati",
                 related_text="Il supporto HSE può essere coordinato con l’incarico di RSPP esterno, la valutazione dei rischi e la formazione. Consulta i servizi collegati per individuare le attività da includere nella richiesta per la tua azienda.",
                 related_links=[("RSPP esterno", "/sicurezza-sul-lavoro/#mi-rspp-esterno"),
                                ("DVR e valutazione dei rischi", "/sicurezza-sul-lavoro/#mi-dvr"),
                                ("Corsi per lavoratori e figure aziendali", "/product-category/sicurezza-sul-lavoro/"),
                                ("Medico Competente e sorveglianza sanitaria", "/medicina-del-lavoro/")])


def haccp():
    paras = [
        "Medicare Italia affianca ristoranti, bar, imprese alimentari, strutture ricettive e attività di somministrazione con redazione e aggiornamento dei piani di autocontrollo HACCP, consulenza e formazione del personale.",
        "La sede è a Grado (GO). Il servizio è rivolto alle attività dei comuni vicini, tra cui Aquileia, Cervignano del Friuli e Monfalcone, e delle province di Gorizia, Trieste, Udine e Pordenone. Modalità del sopralluogo e interventi vengono concordati in base alla sede e alle lavorazioni dell’impresa.",
        "<strong>Un piano di autocontrollo costruito sulla tua attività.</strong> Partiamo dall’analisi delle attività svolte, dei locali e della gestione degli alimenti. Il piano viene predisposto o aggiornato considerando le lavorazioni effettive, le procedure adottate e le esigenze dell’azienda.",
    ]
    items = ["Sopralluogo e analisi dell’attività", "Redazione personalizzata del piano di autocontrollo HACCP",
             "Procedure di igiene, sanificazione e gestione degli alimenti",
             "Analisi dei pericoli e individuazione dei punti critici",
             "Revisione e aggiornamento periodico della documentazione",
             "Supporto nella gestione di registri, controlli e non conformità"]
    links = [("Consulta i corsi HACCP", "/product-category/haccp/"), ("Scopri tutti i corsi", "/corsi/"),
             ("Richiedi un preventivo per il piano HACCP", "/contatti/")]
    haccp_courses = [c for c in COURSES if "haccp" in c["cats"]]
    extra = f'''
<section class="section soft">
  <div class="wrap">
    <div class="duo">
      <article class="feature-card reveal">
        <span class="svc-ico">{icon("award")}</span>
        <h2>Corsi HACCP per alimentaristi e responsabili</h2>
        <p>Organizziamo corsi iniziali e aggiornamenti per alimentaristi, addetti e responsabili, con programmi adeguati alla mansione e alla normativa applicabile. Consulta i <a href="/product-category/haccp/">corsi HACCP disponibili</a> per conoscere durata, modalità e condizioni di iscrizione.</p>
      </article>
      <article class="feature-card reveal" style="--d:80ms">
        <span class="svc-ico">{icon("doc")}</span>
        <h2>Richiedi un preventivo HACCP</h2>
        <p>Indicaci il comune della sede, il tipo di attività, le lavorazioni principali e se possiedi già un piano di autocontrollo da aggiornare. Segnala anche l’eventuale necessità di formare il personale: potremo valutare insieme documentazione, consulenza e corsi.</p>
        <p class="muted">Per gli altri adempimenti aziendali scopri anche i servizi di <a href="/sicurezza-sul-lavoro/">DVR e RSPP esterno</a> e il <a href="/corsi/">calendario dei corsi di sicurezza</a>.</p>
      </article>
    </div>
    <div class="course-grid two" style="margin-top:2rem">{"".join(course_card(c) for c in haccp_courses)}</div>
  </div>
</section>'''
    service_page("/haccp-autocontrollo/", "HACCP", 'HACCP e piani di <span class="grad">autocontrollo</span>',
                 "Piani di autocontrollo HACCP a Grado e in Friuli Venezia Giulia", paras, items, links,
                 "HACCP e piani di autocontrollo a Grado e in FVG – Medicare Italia",
                 "Redazione e aggiornamento dei piani di autocontrollo HACCP, consulenza e corsi per alimentaristi e responsabili a Grado e in Friuli Venezia Giulia.",
                 extra, side_title="Il supporto può comprendere", hero_ico="food", crumb="HACCP e autocontrollo",
                 related_title="HACCP e piani di autocontrollo in Friuli Venezia Giulia",
                 related_text="Supportiamo ristoranti, bar, strutture ricettive e imprese alimentari di Grado, Gorizia e del Friuli Venezia Giulia con formazione HACCP, redazione personalizzata e aggiornamento dei piani di autocontrollo, procedure e gestione documentale.",
                 related_links=[("Consulta i corsi HACCP", "/product-category/haccp/"), ("Scopri tutti i corsi", "/corsi/"),
                                ("Richiedi un preventivo HACCP", "/contatti/")])




def chi_siamo():
    body = page_hero("Medicare Italia", 'Chi <span class="grad">siamo</span>', "", [("Chi siamo", None)])
    body += f'''
<section class="section">
  <div class="wrap about-grid">
    <div class="reveal">
      <span class="eyebrow">La nostra missione</span>
      <h2 class="display">Proteggiamo le persone. <span class="hl">Valorizziamo le aziende.</span></h2>
      <p class="lead-dark">{COMPANY['name']} è il partner professionale per formazione, sicurezza sul lavoro, medicina del lavoro e consulenza aziendale. Un unico interlocutore per trasformare gli obblighi in processi chiari e gestibili.</p>
      <div class="values dark"><span>{icon("shield")}Prevenzione</span><span>{icon("doc")}Conformità</span><span>{icon("users")}Assistenza</span></div>
      <div class="btn-row">{btn("Scopri i corsi", "/corsi/")}{btn("Contattaci", "/contatti/", "outline")}</div>
    </div>
    <div class="about-media reveal" data-tilt>
      <img src="{img('foto-homepage-aula-v433.webp')}" alt="L’aula corsi di Medicare Italia a Grado" loading="lazy">
      <div class="float-card fc-2">{icon("pin")}<span><b>{COMPANY['address']}</b><small>{COMPANY['city']}</small></span></div>
    </div>
  </div>
</section>
{cta_band()}
'''
    page("/chi-siamo/", "Chi siamo – Medicare Italia",
         "Medicare Italia S.r.l. è il partner professionale per formazione, sicurezza sul lavoro, medicina del lavoro e consulenza aziendale.", body)


def contatti():
    opts = ["Corso di formazione", "Formazione HACCP", "Redazione o aggiornamento piano di autocontrollo",
            "Consulenza HSE", "DVR e sicurezza sul lavoro", "Medicina del lavoro", "Altro"]
    hse = {"Consulenza HSE", "DVR e sicurezza sul lavoro", "Medicina del lavoro", "Redazione o aggiornamento piano di autocontrollo"}
    o = "".join(f'<option data-to="{COMPANY["emails"][0][1] if x in hse else COMPANY["emails"][1][1]}">{e(x)}</option>' for x in opts)
    cards = "".join(f'''
<div class="contact-card"><span class="svc-ico">{icon("phone")}</span><div><small>Telefono</small><a href="tel:{n}">{t}</a>
<a class="wa-link" href="https://wa.me/{n[1:]}" target="_blank" rel="noopener">{icon("wa")}WhatsApp</a></div></div>''' for t, n in COMPANY["phones"])
    cards += "".join(f'''
<div class="contact-card"><span class="svc-ico">{icon("mail")}</span><div><small>{e(l)}</small><a href="mailto:{m}">{m}</a></div></div>''' for l, m in COMPANY["emails"])
    cards += f'''
<div class="contact-card"><span class="svc-ico">{icon("pin")}</span><div><small>Sede</small><span>{COMPANY['address']}, {COMPANY['city']}</span>
<a class="wa-link" href="{COMPANY['maps']}" target="_blank" rel="noopener">{icon("ext")}Apri in Google Maps</a></div></div>'''
    body = page_hero("Preventivi", 'Parliamo delle esigenze <span class="grad">della tua azienda</span>',
                     "Descrivi il servizio o il corso di cui hai bisogno. Ti ricontatteremo con una proposta dedicata.", [("Contatti", None)])
    body += f'''
<section class="section">
  <div class="wrap contact-grid">
    <form class="card form-card big reveal" data-form="contatti" data-to="{COMPANY['emails'][1][1]}" novalidate>
      <h2>Richiedi un preventivo</h2>
      <div class="f-row">
        <label class="field"><span>Nome e cognome *</span><input name="nome" required autocomplete="name"></label>
        <label class="field"><span>Azienda</span><input name="azienda" autocomplete="organization"></label>
      </div>
      <div class="f-row">
        <label class="field"><span>Email *</span><input type="email" name="email" required autocomplete="email"></label>
        <label class="field"><span>Telefono</span><input type="tel" name="telefono" autocomplete="tel"></label>
      </div>
      <fieldset class="field">
        <legend>Servizio richiesto</legend>
        <div class="radio-pills">{"".join(f'<label><input type="radio" name="servizio" value="{e(x)}" data-to="{COMPANY["emails"][0][1] if x in hse else COMPANY["emails"][1][1]}"{" checked" if i == 0 else ""}><span>{e(x)}</span></label>' for i, x in enumerate(opts))}</div>
      </fieldset>
      <label class="field"><span>Messaggio *</span><textarea name="messaggio" rows="5" required placeholder="Comune della sede, settore, numero dei lavoratori, corso o servizio richiesto…"></textarea></label>
      <label class="hp" aria-hidden="true">Sito web<input type="text" name="website" tabindex="-1" autocomplete="off"></label>
      <label class="consent"><input type="checkbox" name="privacy" required><span>Dichiaro di aver letto l’<a href="/privacy-policy/">informativa sulla privacy</a>.</span></label>
      <button class="btn btn-primary btn-block" type="submit"><span>Invia richiesta</span>{icon("arrow")}</button>
      <div class="form-msg" data-form-msg hidden></div>
    </form>
    <aside class="contact-side reveal">
      {cards}
    </aside>
  </div>
</section>
<section class="section territory slim">
  <div class="wrap narrow center reveal">
    <span class="eyebrow">Servizi nel territorio</span>
    <h2>Un referente locale per formazione e sicurezza aziendale</h2>
    <p class="lead-dark">La sede di Medicare Italia è a Grado, in provincia di Gorizia. Contattaci per corsi, consulenza HSE, incarico RSPP, DVR, medicina del lavoro, HACCP e piani di autocontrollo destinati alle aziende del Friuli Venezia Giulia.</p>
    {chips([("Vedi i corsi", "/corsi/"), ("Consulenza HSE", "/consulenza-hse/"), ("Medicina del lavoro", "/medicina-del-lavoro/")])}
  </div>
  {territory_marquee()}
</section>
'''
    page("/contatti/", "Contatti e preventivi – Medicare Italia",
         "Richiedi un preventivo per corsi, consulenza HSE, RSPP, DVR, medicina del lavoro e HACCP. Sede a Grado (GO).", body)


def lavora():
    body = page_hero("Lavora con noi", 'Entra nel team di <span class="grad">Medicare Italia</span>',
                     "Siamo interessati a conoscere professionisti e collaboratori nei settori della formazione, sicurezza sul lavoro, medicina del lavoro e assistenza sanitaria. Inviaci la tua candidatura spontanea e il curriculum: valuteremo il profilo per le opportunità presenti e future.",
                     [("Lavora con noi", None)])
    areas = [("award", "Formazione"), ("shield", "Sicurezza sul lavoro"), ("steth", "Medicina del lavoro"), ("heart", "Assistenza sanitaria")]
    body += f'''
<section class="section">
  <div class="wrap contact-grid">
    <form class="card form-card big reveal" data-form="candidatura" data-to="{COMPANY['emails'][1][1]}" novalidate>
      <h2>Candidatura spontanea</h2>
      <div class="f-row">
        <label class="field"><span>Nome e cognome *</span><input name="nome" required autocomplete="name"></label>
        <label class="field"><span>Email *</span><input type="email" name="email" required autocomplete="email"></label>
      </div>
      <div class="f-row">
        <label class="field"><span>Telefono *</span><input type="tel" name="telefono" required autocomplete="tel"></label>
        <label class="field"><span>Profilo professionale *</span><input name="profilo" required placeholder="Es. formatore, infermiere, tecnico HSE…"></label>
      </div>
      <label class="field"><span>Presentazione</span><textarea name="presentazione" rows="4"></textarea></label>
      <label class="dropzone" data-drop>
        <input type="file" name="cv" accept=".pdf,.doc,.docx" required>
        <span class="svc-ico">{icon("upload")}</span>
        <b data-drop-label>Curriculum vitae *</b>
        <small>Trascina qui il file o clicca per selezionarlo. Formati accettati: PDF, DOC o DOCX. Dimensione massima: 5 MB.</small>
      </label>
      <label class="hp" aria-hidden="true">Sito web<input type="text" name="website" tabindex="-1" autocomplete="off"></label>
      <label class="consent"><input type="checkbox" name="privacy" required><span>Dichiaro di aver letto l’<a href="/privacy-policy/">informativa sulla privacy</a> e acconsento al trattamento dei dati per la valutazione della candidatura.</span></label>
      <button class="btn btn-primary btn-block" type="submit"><span>Invia candidatura</span>{icon("arrow")}</button>
      <div class="form-msg" data-form-msg hidden></div>
    </form>
    <aside class="contact-side reveal">
      <div class="side-card-in plain">
        <span class="pill">{icon("users")}Settori</span>
        <ul class="area-list">{"".join(f"<li><span class='svc-ico'>{icon(i)}</span>{t}</li>" for i, t in areas)}</ul>
      </div>
      <div class="about-media small"><img src="{img('foto-homepage-aula-v433.webp')}" alt="Aula corsi Medicare Italia" loading="lazy"></div>
    </aside>
  </div>
</section>
'''
    page("/lavora-con-noi/", "Lavora con noi – Medicare Italia",
         "Invia la tua candidatura spontanea: cerchiamo professionisti della formazione, sicurezza sul lavoro, medicina del lavoro e assistenza sanitaria.", body)


def trasparenza():
    cols = ["Anno", "Soggetto erogante", "Codice fiscale / identificativo ente", "Importo percepito",
            "Data di incasso / fruizione", "Causale / descrizione del beneficio", "Riferimento normativo / bando", "Note"]
    body = page_hero("Obblighi informativi", "Trasparenza", "", [("Trasparenza", None)], tone="compact")
    body += f'''
<section class="section">
  <div class="wrap narrow prose reveal">
    <p class="lead-dark">{COMPANY['name']} pubblica nella presente sezione le informazioni relative a sovvenzioni, sussidi, vantaggi, contributi o aiuti, in denaro o in natura, ricevuti da pubbliche amministrazioni e dagli altri soggetti previsti dalla normativa, nei casi in cui sussista l’obbligo di pubblicazione.</p>
    <p>La presente sezione è predisposta ai fini degli obblighi informativi previsti dall’art. 1, commi 125 e seguenti, della Legge 4 agosto 2017, n. 124 e successive modificazioni e integrazioni.</p>

    <h2>Soggetto beneficiario</h2>
    <div class="id-card">
      <span class="svc-ico">{icon("doc")}</span>
      <dl>
        <div><dt>Ragione sociale</dt><dd>{COMPANY['name']}</dd></div>
        <div><dt>Sede</dt><dd>Viale Argine dei Moreri 8, {COMPANY['city']}</dd></div>
        <div><dt>P. IVA / C.F.</dt><dd>{COMPANY['piva']}</dd></div>
        <div><dt>REA</dt><dd>GO-214174</dd></div>
      </dl>
    </div>

    <h2>Contributi, sovvenzioni e vantaggi economici ricevuti</h2>
    <p>In questa sezione vengono riportate, per ciascun esercizio di riferimento, le erogazioni pubbliche soggette a obbligo informativo, sulla base dei dati effettivamente percepiti e comunicati dalla società.</p>
    <div class="table-wrap"><table><thead><tr>{"".join(f'<th scope="col">{c}</th>' for c in cols)}</tr></thead><tbody></tbody></table></div>

    <h2>Aiuti di Stato e aiuti “de minimis”</h2>
    <p>Gli aiuti di Stato e gli aiuti “de minimis” soggetti a registrazione sono consultabili nel Registro Nazionale degli Aiuti di Stato (RNA), istituito ai sensi dell’art. 52 della Legge 24 dicembre 2012, n. 234.</p>
    <p>Per consultare gli aiuti registrati a favore di {COMPANY['name']} è possibile accedere alla sezione Trasparenza del Registro Nazionale degli Aiuti di Stato e utilizzare come chiave di ricerca il codice fiscale della società:</p>
    <div class="cf-box"><code data-copy>{COMPANY['piva']}</code><button type="button" class="btn btn-outline btn-sm" data-copy-btn><span>Copia</span></button></div>
    <div class="btn-row">{btn("Consulta il Registro Nazionale degli Aiuti di Stato", "https://www.rna.gov.it/", "primary", "ext", ' target="_blank" rel="noopener"')}</div>
    <p class="muted small">Ultimo aggiornamento della sezione: 2 Settembre 2026<br>Le informazioni vengono aggiornate sulla base dei dati amministrativi e contabili disponibili e degli obblighi di pubblicazione applicabili.</p>
  </div>
</section>
'''
    page("/trasparenza/", "Trasparenza – Medicare Italia",
         "Obblighi informativi ai sensi della Legge 124/2017: contributi, sovvenzioni e aiuti di Stato ricevuti da Medicare Italia S.r.l.", body)




def shop():
    cats = '<button class="fchip is-on" type="button" data-shop-filter="all">Tutti i prodotti</button>' + "".join(
        f'<button class="fchip" type="button" data-shop-filter="{k}">{icon(ic)}{e(t)}</button>' for k, t, _, ic in SHOP_CATS)
    prods = "".join(product_card(p, i) for i, p in enumerate(PRODUCTS))
    cat_cards = "".join(f'''
<a class="shop-card reveal" href="/product-category/{k}/" style="--d:{i * 70}ms">
  <span class="shop-ico">{icon(ic)}</span><h3>{e(t)}</h3><p>{e(p)}</p>
  <span class="link-arrow">Scopri i prodotti{icon("arrow")}</span>
</a>''' for i, (k, t, p, ic) in enumerate(SHOP_CATS))
    body = page_hero("E-commerce", 'Shop online <span class="grad">per la sicurezza</span>',
                     "Attrezzature, dispositivi e materiali selezionati per aziende, professionisti ed enti.", [("Shop", None)])
    body += f'''
<section class="section">
  <div class="wrap">
    <div class="shop-grid compact">{cat_cards}</div>
    <div class="shop-toolbar">
      <div class="fchips">{cats}</div>
      <p class="result-count" data-shop-count>Visualizzazione di {len(PRODUCTS)} risultati</p>
    </div>
    <div class="product-grid" data-products>{prods}</div>
    <div class="empty" data-shop-empty hidden>{icon("box")}<p>Nessun prodotto disponibile in questa categoria.</p><a class="btn btn-outline btn-sm" href="/contatti/"><span>Richiedi informazioni</span></a></div>
  </div>
</section>
{cta_band("Ti serve una fornitura per la tua azienda?", "Cassette di pronto soccorso, defibrillatori e cartellonistica: contattaci per informazioni.", "Richiedi informazioni")}
'''
    page("/shop/", "Shop – Medicare Italia",
         "Cassette di pronto soccorso, defibrillatori, cartellonistica e prodotti per la sicurezza sul lavoro.", body)


def post_card(n, i=0):
    url = f"/news-e-aggiornamenti/{n['slug']}/"
    return f'''
<article class="post reveal" style="--d:{(i % 3) * 70}ms">
  <a class="post-media" href="{url}"><img src="{n['image']}" alt="" loading="lazy"></a>
  <div class="post-body">
    <time>{icon("cal")}{n['date']}</time>
    <h2><a href="{url}">{e(n['title'])}</a></h2>
    {f"<p>{e(n['excerpt'])}</p>" if n['excerpt'] else ""}
    <span class="link-arrow">Apri il contenuto{icon("arrow")}</span>
  </div>
</article>'''


def news():
    first, rest = NEWS[0], NEWS[1:]
    url = f"/news-e-aggiornamenti/{first['slug']}/"
    body = page_hero("Blog", 'News e <span class="grad">aggiornamenti</span>',
                     "Aggiornamenti normativi, documenti utili, immagini e comunicazioni operative pubblicate da Medicare Italia.",
                     [("News", None)])
    body += f'''
<section class="section">
  <div class="wrap">
    <article class="post-featured reveal">
      <a class="post-media" href="{url}"><img src="{first['image']}" alt=""></a>
      <div class="post-body">
        <span class="pill">{icon("spark")}Ultimo articolo</span>
        <time>{icon("cal")}{first['date']}</time>
        <h2><a href="{url}">{e(first['title'])}</a></h2>
        <p>{e(first['excerpt'])}</p>
        {btn("Apri il contenuto", url)}
      </div>
    </article>
    <div class="post-grid">{"".join(post_card(n, i) for i, n in enumerate(rest))}</div>
  </div>
</section>
{newsletter()}
'''
    page("/news-e-aggiornamenti/", "News e aggiornamenti – Medicare Italia",
         "Aggiornamenti normativi, documenti utili e comunicazioni operative su sicurezza sul lavoro, formazione, HACCP e medicina del lavoro.", body)
    redirect("/news-e-aggiornamenti/page/2/", "/news-e-aggiornamenti/")


def news_article(n):
    url = f"/news-e-aggiornamenti/{n['slug']}/"
    others = [x for x in NEWS if x is not n][:3]
    files = "".join(
        f'<a class="file-card" href="{f}" download>{icon("doc")}<span><b>{e(os.path.basename(f))}</b><small>Documento PDF · scarica</small></span>{icon("upload", "ico dl")}</a>'
        for f in n["files"])
    body = page_hero("News e aggiornamenti", e(n["title"]), "", [("News", "/news-e-aggiornamenti/"), (n["title"][:48] + ("…" if len(n["title"]) > 48 else ""), None)],
                     f'<p class="hero-meta">{icon("cal")}Pubblicato il {n["date"]}</p>', tone="article")
    body += f'''
<section class="section article-section">
  <div class="wrap article-wrap">
    <figure class="article-cover reveal"><img src="{n['image']}" alt="" width="1400" height="933"></figure>
    <div class="article-grid">
      <article class="prose article-body">
        {files}
        {linkrow(n['html'])}
        <p class="back-link"><a href="/news-e-aggiornamenti/">← Torna a news e aggiornamenti</a></p>
      </article>
      <aside class="article-side">
        <div class="side-card-in">
          <span class="pill">{icon("shield")}Hai bisogno di supporto?</span>
          <p>Formazione, DVR, RSPP esterno, medicina del lavoro e HACCP: un unico partner a Grado (GO).</p>
          {btn("Richiedi consulenza", "/contatti/")}
          <div class="side-contacts">
            <a href="tel:{COMPANY['phones'][0][1]}">{icon("phone")}{COMPANY['phones'][0][0]}</a>
            <a href="mailto:{COMPANY['emails'][1][1]}">{icon("mail")}{COMPANY['emails'][1][1]}</a>
          </div>
        </div>
      </aside>
    </div>
  </div>
</section>
<section class="section soft">
  <div class="wrap">
    <div class="sec-head reveal"><div><span class="eyebrow">Continua a leggere</span><h2>Altri aggiornamenti</h2></div>
    <div class="sec-head-side">{btn("Tutte le news", "/news-e-aggiornamenti/", "outline")}</div></div>
    <div class="post-grid">{"".join(post_card(x, i) for i, x in enumerate(others))}</div>
  </div>
</section>
{newsletter()}
'''
    page(url, f"{n['title']} – Medicare Italia", n["excerpt"] or n["title"], body, active="/news-e-aggiornamenti/",
         og_image=n["image"])


def detail_rows(c):
    rows = ""
    for i, (d, t) in enumerate(c["days"]):
        dd, mm, yy = d.split("/")
        rows += f'''<li class="session"><span class="mini-date"><b>{dd}</b>{MONTHS[int(mm) - 1]}</span>
<span><small>{i + 1}ª giornata · {yy}</small><b>{d}</b>{f"<em>{e(t)}</em>" if t else ""}</span></li>'''
    if c.get("note"):
        rows += f'<li class="info-row">{icon("clock")}<span>{e(c["note"])}</span></li>'
    if c.get("mode"):
        rows += f'<li class="info-row">{icon(MODE_ICO[c["mode"]])}<span><small>Modalità</small>{MODES[c["mode"]] if c["mode"] != "elearning" else "Corso interamente online"}</span></li>'
    if c.get("mode") == "elearning":
        rows += f'<li class="info-row">{icon("layers")}<span><small>Accesso</small>Da computer, tablet o smartphone</span></li>'
        rows += f'<li class="info-row">{icon("clock")}<span><small>Disponibilità</small>Senza date e orari prestabiliti</span></li>'
    if c.get("place"):
        rows += (f'<li class="info-row">{icon("pin")}<span><small>Indirizzo</small>{e(c["place"])}'
                 f'<a href="{COMPANY["maps"]}" target="_blank" rel="noopener">Apri in Google Maps</a></span></li>')
    if c.get("validity"):
        rows += f'<li class="info-row">{icon("award")}<span><small>Validità attestato</small>{e(c["validity"])}</span></li>'
    return f'<ul class="detail-list">{rows}</ul>' if rows else ""


def tabs_html(tabs):
    tabs = [t for t in tabs if t["html"]]
    if not tabs:
        return ""
    if len(tabs) == 1:
        return f'<div class="pdp-desc reveal"><h2 class="pdp-desc-title">{e(tabs[0]["title"])}</h2><div class="prose">{linkrow(tabs[0]["html"])}</div></div>'
    heads = "".join(f'<button type="button" role="tab" data-tab="{i}"{" aria-selected=true" if i == 0 else ""}>{e(t["title"])}</button>' for i, t in enumerate(tabs))
    panels = "".join(f'<div class="prose" role="tabpanel" data-panel="{i}"{"" if i == 0 else " hidden"}>{linkrow(t["html"])}</div>' for i, t in enumerate(tabs))
    return f'<div class="pdp-desc reveal" data-tabs><div class="tabbar" role="tablist">{heads}</div>{panels}</div>'


def jsonld_product(c, kind):
    data = {"@context": "https://schema.org", "@type": "Product", "name": c["title_full"], "image": ORIGIN + c["img"],
            "sku": str(c["id"]), "brand": {"@type": "Organization", "name": "Medicare Italia"},
            "offers": {"@type": "Offer", "price": f"{price_num(c['price']):.2f}", "priceCurrency": "EUR",
                       "availability": "https://schema.org/" + ("InStock" if c.get("in_stock", True) else "OutOfStock"),
                       "url": ORIGIN + item_url(c)}}
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def course_page(c):
    cat = cat_by_key(c["primary"])
    related = [x for x in COURSES if x is not c and x["primary"] == c["primary"] and x["title"] != c["title"]][:3]
    if len(related) < 3:
        related += [x for x in COURSES if x is not c and x not in related and x["primary"] == c["primary"]][:3 - len(related)]
    others = [x for x in COURSES if x is not c and x["slug"] != c["slug"] and x["title"] == c["title"]]
    other_ed = ""
    if others:
        other_ed = '<div class="other-ed"><small>Altre edizioni</small>' + "".join(
            f'<a href="{item_url(o)}">{icon("cal")}{o["days"][0][0] if o["days"] else "Online"}{icon("arrow")}</a>' for o in others) + "</div>"
    seats = ""
    if c["seats"]:
        low = " low" if c["seats"] <= 7 else ""
        seats = f'<span class="seats{low}"><i></i>{c["seats"]} posti disponibili</span>'
    elif c["mode"] == "elearning":
        seats = '<span class="seats online"><i></i>Accesso online</span>'
    status = "Edizione disponibile" if c["days"] else "Disponibile online"
    if c["past"]:
        status = "Edizione conclusa"
        seats = ""
    qty_max = c["seats"] or 99
    buy_row = f'''<div class="buy-row">
          <div class="qty" data-qty><button type="button" data-step="-1" aria-label="Diminuisci">−</button><input type="number" value="1" min="1" max="{qty_max}" inputmode="numeric" aria-label="Numero di partecipanti"><button type="button" data-step="1" aria-label="Aumenta">+</button></div>
          {add_button(c, "course", "btn btn-primary add-btn grow", "Aggiungi al carrello")}
        </div>
        <p class="buy-note">Indica il numero di partecipanti. Potrai inserire i loro nominativi nella richiesta di iscrizione.</p>'''
    if c["past"]:
        buy_row = f'''<div class="past-box">{icon("cal")}<span><b>Questa edizione è conclusa.</b> Consulta il calendario per le prossime date o richiedi un corso per la tua azienda.</span></div>
        {btn("Vai al calendario corsi", "/corsi/")}'''
    hero_extra = f'''<div class="hero-tags">
  <span>{icon(MODE_ICO[c["mode"]])}{MODES[c["mode"]]}</span>
  {f'<span>{icon("cal")}Dal {c["days"][0][0]}</span>' if c["days"] else ""}
  {f'<span>{icon("award")}Validità attestato {e(c["validity"])}</span>' if c["validity"] else ""}
  <span class="{'past' if c['past'] else 'ok'}">{icon("check")}{status}</span>
</div>'''
    body = page_hero(cat[1], e(c["title"]), "", [("Corsi", "/corsi/"), (cat[1], f"/product-category/{cat[0]}/"), (c["title"][:40] + ("…" if len(c["title"]) > 40 else ""), None)],
                     hero_extra, tone="pdp-hero")
    body += f'''
<section class="section pdp-section">
  <div class="wrap pdp" style="--c:{cat[4]}">
    <div class="pdp-main">
      <figure class="pdp-media reveal"><img src="{c['img']}" alt="{e(c['title'])}" width="1200" height="800"></figure>
      {f'<div class="pdp-short prose reveal">{c["short"]}</div>' if c["short"] else ""}
      {tabs_html(c["tabs"])}
    </div>
    <aside class="buy-card" aria-label="Acquisto">
      <div class="buy-in">
        <div class="buy-price"><b>{c['price']} €</b><small>IVA inclusa</small></div>
        {seats}
        {detail_rows(c)}
        {other_ed}
        {buy_row}
        <a class="link-arrow" href="/contatti/">Vuoi organizzare il corso presso la tua azienda?{icon("arrow")}</a>
      </div>
    </aside>
  </div>
</section>
{f"""<section class="section soft"><div class="wrap">
  <div class="sec-head reveal"><div><span class="eyebrow">{e(cat[1])}</span><h2>Altri corsi della categoria</h2></div>
  <div class="sec-head-side">{btn("Tutti i corsi " + cat[1], "/product-category/" + cat[0] + "/", "outline")}</div></div>
  <div class="course-grid">{"".join(course_card(x) for x in related)}</div>
</div></section>""" if related else ""}
{cta_band("Devi formare più persone?", "Possiamo valutare corsi presso la tua sede, concordando partecipanti, spazi, programma e modalità.", "Richiedi un preventivo")}
'''
    page(item_url(c), f"{c['title']} – Medicare Italia", re.sub(r"<[^>]+>", "", c["short"])[:155] or c["title"], body,
         active="/corsi/", og_image=c["img"], head_extra=jsonld_product(c, "course"))


def shop_product_page(p):
    cat = next((x for x in SHOP_CATS if x[0] == p["primary"]), SHOP_CATS[-1])
    others = [x for x in PRODUCTS if x is not p][:3]
    benefits = [("check", "Prodotto selezionato", "Per uso professionale e aziendale"),
                ("box", "Spedizione tracciata", "Tempi indicati durante l’ordine"),
                ("users", "Assistenza alla scelta", "Supporto Medicare Italia")]
    ben = "".join(f'<li>{icon(i)}<span><b>{t}</b><small>{s}</small></span></li>' for i, t, s in benefits)
    body = page_hero(cat[1], e(p["title"]), "", [("Shop", "/shop/"), (cat[1], f"/product-category/{cat[0]}/"), (p["title"][:40], None)], tone="pdp-hero")
    body += f'''
<section class="section pdp-section">
  <div class="wrap pdp">
    <div class="pdp-main">
      <figure class="pdp-media product-shot reveal"><img src="{p['img']}" alt="{e(p['title'])}"></figure>
      {f'<div class="pdp-short prose reveal">{p["short"]}</div>' if p["short"] else ""}
      {tabs_html(p["tabs"])}
    </div>
    <aside class="buy-card" aria-label="Acquisto">
      <div class="buy-in">
        <div class="buy-price"><b>{p['price']} €</b><small>IVA inclusa</small></div>
        {f'<p class="ship">{icon("box")}<span><b>Spese di spedizione:</b> {e(p["shipping"])}</span></p>' if p["shipping"] else ""}
        <ul class="benefits">{ben}</ul>
        <div class="buy-row">
          <div class="qty" data-qty><button type="button" data-step="-1" aria-label="Diminuisci">−</button><input type="number" value="1" min="1" max="99" inputmode="numeric" aria-label="Quantità"><button type="button" data-step="1" aria-label="Aumenta">+</button></div>
          {add_button(p, "product", "btn btn-primary add-btn grow", "Aggiungi al carrello")}
        </div>
        <div class="help-box"><b>Hai dubbi sul prodotto corretto?</b><p>Contattaci indicando settore, numero di lavoratori ed esigenze aziendali. Ti aiutiamo a scegliere la soluzione adatta.</p><a class="link-arrow" href="/contatti/">Richiedi assistenza{icon("arrow")}</a></div>
      </div>
    </aside>
  </div>
</section>
{f"""<section class="section soft"><div class="wrap">
  <div class="sec-head reveal"><div><span class="eyebrow">Shop</span><h2>Altri prodotti</h2></div>
  <div class="sec-head-side">{btn("Visita tutto lo shop", "/shop/", "outline")}</div></div>
  <div class="product-grid">{"".join(product_card(x, i) for i, x in enumerate(others))}</div>
</div></section>""" if others else ""}
'''
    page(item_url(p), f"{p['title']} – Shop Medicare Italia", re.sub(r"<[^>]+>", "", p["short"])[:155] or p["title"], body,
         active="/shop/", og_image=p["img"], head_extra=jsonld_product(p, "product"))


def category_page(k):
    data = CATEGORIES[k]
    is_course = k in {c[0] for c in COURSE_CATS}
    if is_course:
        meta = cat_by_key(k)
        items = [COURSE_BY_SLUG[s] for s in data["products"] if s in COURSE_BY_SLUG]
        items.sort(key=lambda c: COURSES.index(c))
        grid = f'<div class="course-grid">{"".join(course_card(c) for c in items)}</div>'
        crumbs = [("Corsi", "/corsi/"), (meta[1], None)]
        others = [(c[1], f"/product-category/{c[0]}/") for c in COURSE_CATS if c[0] != k]
        lead = meta[2]
        color = meta[4]
        empty_txt = "Al momento non ci sono edizioni pubblicate per questa categoria."
        extra_btn = btn("Consulta il calendario corsi", "/corsi/", "outline")
    else:
        meta = next(c for c in SHOP_CATS if c[0] == k)
        items = [PRODUCT_BY_SLUG[s] for s in data["products"] if s in PRODUCT_BY_SLUG]
        grid = f'<div class="product-grid">{"".join(product_card(p, i) for i, p in enumerate(items))}</div>'
        crumbs = [("Shop", "/shop/"), (meta[1], None)]
        others = [(c[1], f"/product-category/{c[0]}/") for c in SHOP_CATS if c[0] != k]
        lead = meta[2]
        color = "#007aa1"
        empty_txt = "Non è stato trovato nessun prodotto che corrisponde alla tua selezione."
        extra_btn = btn("Visita tutto lo shop", "/shop/", "outline")
    n = len(items)
    count = "Visualizzazione del risultato" if n == 1 else f"Visualizzazione di {n} risultati"
    chtml = data["html"]
    first = re.match(r"<p>(.*?)</p>", chtml)
    if first and re.sub(r"<[^>]+>", "", first.group(1)).strip() == lead.strip():
        chtml = chtml[first.end():]  # già mostrato nella hero
    intro = f'<div class="wrap narrow"><div class="cat-intro prose reveal" style="--c:{color}">{linkrow(chtml)}</div></div>' if chtml.strip() else ""
    if items:
        listing = f'<p class="result-count">{count}</p>{grid}'
    else:
        listing = f'''<div class="empty big">{icon("cal")}<p>{empty_txt}</p>
<div class="btn-row">{btn("Richiedi informazioni", "/contatti/")}{extra_btn}</div></div>'''
    body = page_hero("Shop" if not is_course else "Formazione", e(data["title"]), e(lead), crumbs,
                     f'<div class="hero-count"><b>{n}</b><span>{"corsi" if is_course else "prodotti"}<br>disponibili</span></div>')
    body += f'''
<section class="section">
  {intro}
  <div class="wrap" style="margin-top:{'2.4rem' if intro else '0'}">
    {listing}
    <div class="center" style="margin-top:2.6rem"><span class="eyebrow">Altre categorie</span>{chips(others)}</div>
  </div>
</section>
{cta_band()}
'''
    page(f"/product-category/{k}/", f"{data['title']} – Medicare Italia", lead, body, active="/corsi/" if is_course else "/shop/")


def legal_page(slug):
    data = LEGAL[slug]
    h = linkrow(re.sub(r"^<h2>" + re.escape(data["title"]) + r"</h2>", "", data["html"]))
    toc = []

    def anchor(m):
        t = re.sub(r"<[^>]+>", "", m.group(1))
        a = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60]
        toc.append((t, a))
        return f'<h3 id="{a}">{m.group(1)}</h3>'
    h = re.sub(r"<h3>(.*?)</h3>", anchor, h)
    toc_html = "".join(f'<li><a href="#{a}">{e(html_lib.unescape(t))}</a></li>' for t, a in toc)
    body = page_hero("Medicare Italia", e(data["title"]), "", [(data["title"], None)], tone="compact")
    body += f'''
<section class="section">
  <div class="wrap legal-grid">
    {f'<nav class="toc" aria-label="Indice"><span class="pill">{icon("layers")}Indice</span><ol>{toc_html}</ol></nav>' if toc else ""}
    <article class="prose legal reveal">{h}</article>
  </div>
</section>'''
    page(f"/{slug}/", f"{data['title']} – Medicare Italia", f"{data['title']} di Medicare Italia S.r.l.", body)


def cart_page():
    body = page_hero("Medicare Italia", 'Il tuo <span class="grad">carrello</span>', "Controlla corsi e prodotti selezionati e invia la richiesta di iscrizione o d’ordine.",
                     [("Carrello", None)], tone="compact")
    body += f'''
<section class="section">
  <div class="wrap cart-layout" data-cart-page>
    <div class="cart-main">
      <div class="card cart-card">
        <div class="cart-head"><h2>Riepilogo</h2><button type="button" class="link-btn" data-cart-clear hidden>Svuota carrello</button></div>
        <ul class="cart-list" data-cart-list></ul>
        <div class="empty" data-cart-empty hidden>{icon("cart")}<p>Il tuo carrello è vuoto.</p>
          <div class="btn-row">{btn("Calendario corsi", "/corsi/")}{btn("Ritorna al negozio", "/shop/", "outline")}</div></div>
      </div>
      <form class="card form-card big" id="checkout" data-form="ordine" data-to="{COMPANY['emails'][1][1]}" novalidate hidden>
        <h2>Dati per l’iscrizione e la fatturazione</h2>
        <p class="muted">Compila i dati: la richiesta arriverà a Medicare Italia, che ti ricontatterà per confermare iscrizione, disponibilità e modalità di pagamento.</p>
        <div class="f-row">
          <label class="field"><span>Nome e cognome *</span><input name="nome" required autocomplete="name"></label>
          <label class="field"><span>Azienda / Ragione sociale</span><input name="azienda" autocomplete="organization"></label>
        </div>
        <div class="f-row">
          <label class="field"><span>Email *</span><input type="email" name="email" required autocomplete="email"></label>
          <label class="field"><span>Telefono *</span><input type="tel" name="telefono" required autocomplete="tel"></label>
        </div>
        <div class="f-row">
          <label class="field"><span>Codice fiscale / Partita IVA</span><input name="fiscale"></label>
          <label class="field"><span>Codice destinatario / PEC</span><input name="sdi"></label>
        </div>
        <label class="field"><span>Indirizzo di fatturazione<span data-ship-req hidden> e spedizione *</span></span><input name="indirizzo" autocomplete="street-address" data-ship-field></label>
        <label class="field" data-course-only><span>Nominativi dei partecipanti</span><textarea name="partecipanti" rows="3" placeholder="Nome e cognome di ogni partecipante, uno per riga"></textarea></label>
        <label class="field"><span>Note</span><textarea name="note" rows="3"></textarea></label>
        <label class="hp" aria-hidden="true">Sito web<input type="text" name="website" tabindex="-1" autocomplete="off"></label>
        <label class="consent"><input type="checkbox" name="privacy" required><span>Dichiaro di aver letto l’<a href="/privacy-policy/">informativa sulla privacy</a>.</span></label>
        <label class="consent"><input type="checkbox" name="termini" required><span>Ho letto e accetto i <a href="/termini-condizioni/">termini e condizioni</a>.</span></label>
        <button class="btn btn-primary btn-block" type="submit"><span>Invia richiesta</span>{icon("arrow")}</button>
        <div class="form-msg" data-form-msg hidden></div>
      </form>
    </div>
    <aside class="buy-card" data-cart-summary hidden>
      <div class="buy-in">
        <h3>Totale</h3>
        <dl class="totals">
          <div><dt>Subtotale</dt><dd data-sub>0,00 €</dd></div>
          <div data-ship-row hidden><dt>Spedizione</dt><dd data-ship>0,00 €</dd></div>
          <div class="grand"><dt>Totale <small>IVA inclusa</small></dt><dd data-total>0,00 €</dd></div>
        </dl>
        <a class="btn btn-primary btn-block" href="#checkout"><span>Procedi con la richiesta</span>{icon("arrow")}</a>
        <div class="side-contacts">
          <a href="tel:{COMPANY['phones'][0][1]}">{icon("phone")}{COMPANY['phones'][0][0]}</a>
          <a href="mailto:{COMPANY['emails'][1][1]}">{icon("mail")}{COMPANY['emails'][1][1]}</a>
        </div>
      </div>
    </aside>
  </div>
</section>'''
    page("/cart/", "Carrello – Medicare Italia", "Il tuo carrello Medicare Italia.", body)
    redirect("/checkout/", "/cart/#checkout")
    redirect("/my-account/", "/cart/")


def redirect(path, to):
    out = os.path.join(OUT, path.strip("/"), "index.html")
    GENERATED.append(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(f'<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Reindirizzamento…</title>'
                f'<meta name="robots" content="noindex"><link rel="canonical" href="{ORIGIN}{to}">'
                f'<meta http-equiv="refresh" content="0;url={to}"></head><body><a href="{to}">Continua</a></body></html>\n')
    print("  ", path, "->", to)


def search_index():
    idx = [
        {"t": "Calendario corsi", "u": "/corsi/", "k": "Pagina"},
        {"t": "Sicurezza sul lavoro, DVR e RSPP esterno", "u": "/sicurezza-sul-lavoro/", "k": "Servizio"},
        {"t": "Medicina del lavoro e Medico Competente", "u": "/medicina-del-lavoro/", "k": "Servizio"},
        {"t": "Consulenza HSE", "u": "/consulenza-hse/", "k": "Servizio"},
        {"t": "HACCP e piani di autocontrollo", "u": "/haccp-autocontrollo/", "k": "Servizio"},
        {"t": "Shop online", "u": "/shop/", "k": "Pagina"},
        {"t": "News e aggiornamenti", "u": "/news-e-aggiornamenti/", "k": "Pagina"},
        {"t": "Chi siamo", "u": "/chi-siamo/", "k": "Pagina"},
        {"t": "Contatti e preventivi", "u": "/contatti/", "k": "Pagina"},
        {"t": "Lavora con noi", "u": "/lavora-con-noi/", "k": "Pagina"},
        {"t": "Trasparenza", "u": "/trasparenza/", "k": "Pagina"},
        {"t": "Carrello", "u": "/cart/", "k": "Pagina"},
    ]
    idx += [{"t": CATEGORIES[c[0]]["title"], "u": f"/product-category/{c[0]}/", "k": "Categoria corsi"} for c in COURSE_CATS]
    idx += [{"t": c[1], "u": f"/product-category/{c[0]}/", "k": "Categoria shop"} for c in SHOP_CATS]
    idx += [{"t": c["title"], "u": item_url(c), "k": "Corso · " + (c["days"][0][0] if c["days"] else "e-learning") + " · " + c["price"] + " €"} for c in COURSES]
    idx += [{"t": p["title"], "u": item_url(p), "k": "Prodotto · " + p["price"] + " €"} for p in PRODUCTS]
    idx += [{"t": n["title"], "u": f"/news-e-aggiornamenti/{n['slug']}/", "k": "Articolo · " + n["date"]} for n in NEWS]
    idx += [{"t": l["title"], "u": f"/{k}/", "k": "Pagina legale"} for k, l in LEGAL.items()]
    os.makedirs(os.path.join(OUT, "assets", "js"), exist_ok=True)
    with open(os.path.join(OUT, "assets", "js", "search-index.json"), "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False)


def sitemap():
    urls = []
    for dirpath, dirs, files in os.walk(OUT):
        if dirpath == OUT:
            dirs[:] = [d for d in dirs if d not in SOURCE_DIRS]
        if "index.html" in files:
            with open(os.path.join(dirpath, "index.html"), encoding="utf-8") as f:
                if 'http-equiv="refresh"' in f.read(600):
                    continue
            rel = os.path.relpath(dirpath, OUT).replace("\\", "/")
            urls.append("/" if rel == "." else f"/{rel}/")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
          "".join(f"  <url><loc>{ORIGIN}{u}</loc></url>\n" for u in sorted(urls)) + "</urlset>\n"
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {ORIGIN}/sitemap.xml\n")
    print(f"   sitemap.xml ({len(urls)} URL)")


def not_found():
    links = [("cal", "Calendario corsi", "Prossime date in presenza, videoconferenza ed e-learning", "/corsi/"),
             ("shield", "Servizi HSE", "DVR, RSPP esterno, medicina del lavoro e HACCP", "/consulenza-hse/"),
             ("cart", "Shop", "Cassette di pronto soccorso e defibrillatori", "/shop/"),
             ("phone", "Contatti", "Parla con noi o richiedi un preventivo", "/contatti/")]
    cards = "".join(f'''
<a class="nf-card reveal" href="{h}" style="--d:{i * 70}ms">
  <span class="svc-ico">{icon(ic)}</span>
  <span><b>{e(t)}</b><small>{e(d)}</small></span>
  {icon("arrow")}
</a>''' for i, (ic, t, d, h) in enumerate(links))
    upcoming = [c for c in COURSES if c["days"]][:3]
    body = f'''
<section class="hero nf-hero">
  <div class="aurora" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="grid-bg" aria-hidden="true"></div>
  <div class="wrap nf-in">
    <div class="nf-code" aria-hidden="true"><span>4</span><img src="{img('logo-mark.webp')}" alt=""><span>4</span></div>
    <span class="eyebrow eyebrow-light">Errore 404</span>
    <h1>Questa pagina <span class="grad">non esiste</span></h1>
    <p class="lead">Il link potrebbe essere vecchio o contenere un errore: abbiamo rinnovato il sito e alcuni indirizzi sono cambiati.
    <span class="nf-path" data-nf-path hidden>Indirizzo richiesto: <code></code></span></p>
    <div class="hero-ctas">
      <button class="btn btn-primary" type="button" data-search-open><span>Cerca nel sito</span>{icon("search")}</button>
      {btn("Torna alla home", "/", "ghost", None)}
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="sec-head reveal"><div><span class="eyebrow">Ripartiamo da qui</span><h2>Cosa stavi cercando?</h2></div></div>
    <div class="nf-grid">{cards}</div>
  </div>
</section>
{f'''<section class="section soft"><div class="wrap">
  <div class="sec-head reveal"><div><span class="eyebrow">Calendario</span><h2>Prossimi corsi</h2></div>
  <div class="sec-head-side">{btn("Tutti i corsi", "/corsi/", "outline")}</div></div>
  <div class="course-grid">{"".join(course_card(c) for c in upcoming)}</div>
</div></section>''' if upcoming else ""}
<script>
  (function () {{
    var box = document.querySelector("[data-nf-path]");
    if (box && location.pathname !== "/404.html") {{ box.querySelector("code").textContent = location.pathname; box.hidden = false; }}
  }})();
</script>
'''
    page("/404.html", "Pagina non trovata – Medicare Italia", "La pagina richiesta non esiste.", body, active="", filename="404.html")


def prepare_out():
    """File di servizio per la pubblicazione (GitHub Pages)."""
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    # il dominio si imposta su GitHub (Settings → Pages); il file CNAME, se c'è, non viene toccato
    if not os.path.exists(os.path.join(OUT, "CNAME")):
        with open(os.path.join(OUT, "CNAME"), "w") as f:
            f.write(ORIGIN.split("//")[1] + "\n")


def clean_stale():
    """Elimina solo le pagine create da una build precedente che ora non esistono più
    (es. un corso cancellato dall'admin). Non tocca nient'altro."""
    new = {os.path.relpath(p, ROOT).replace("\\", "/") for p in GENERATED}
    old = set()
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            old = {l.strip() for l in f if l.strip()}
    for rel in sorted(old - new):
        path = os.path.join(ROOT, rel)
        if rel.endswith("index.html") and rel.split("/")[0] not in SOURCE_DIRS and os.path.isfile(path):
            os.remove(path)
            d = os.path.dirname(path)
            while d != ROOT and os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
                d = os.path.dirname(d)
            print("   rimossa pagina non più esistente:", rel)
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(sorted(new)) + "\n")


if __name__ == "__main__":
    prepare_out()
    print("Generazione pagine:")
    for fn in (home, corsi, sicurezza, medicina, consulenza, haccp, shop, news, chi_siamo, contatti, lavora, trasparenza, cart_page):
        fn()
    for c in ALL_COURSES:
        course_page(c)
    for p in PRODUCTS:
        shop_product_page(p)
    for k in CATEGORIES:
        category_page(k)
    for n in NEWS:
        news_article(n)
    for k in LEGAL:
        legal_page(k)
    not_found()
    clean_stale()
    search_index()
    sitemap()
    print("Fatto.")
