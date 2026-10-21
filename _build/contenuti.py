# -*- coding: utf-8 -*-
"""Carica i contenuti modificabili dall'area admin (cartella content/, un file JSON per voce)."""
import datetime as _dt
import glob as _glob
import json as _json
import os as _os
import re as _re

from markdown_it import MarkdownIt as _MarkdownIt

_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_CONTENT = _os.path.join(_ROOT, "content")
_MD = _MarkdownIt("commonmark", {"html": True}).enable("table")


def md(text):
    """Markdown (anche con HTML) → HTML."""
    return _MD.render(text or "").strip()


def _read(path):
    with open(path, encoding="utf-8") as f:
        return _json.load(f)


def _collection(folder):
    out = {}
    for path in sorted(_glob.glob(_os.path.join(_CONTENT, folder, "*.json"))):
        d = _read(path)
        if d.get("published", True) is False:
            continue
        d["slug"] = _os.path.splitext(_os.path.basename(path))[0]
        out[d["slug"]] = d
    return out


def euro(n):
    """160 → '160,00' · 1250 → '1.250,00'"""
    s = f"{float(n or 0):,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _num(v):
    if v in (None, ""):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _dmy(iso):
    """'2026-11-11' (anche con orario) → '11/11/2026'"""
    y, m, d = str(iso)[:10].split("-")
    return f"{d}/{m}/{y}"


def _dkey(d):
    dd, mm, yy = d.split("/")
    return (int(yy), int(mm), int(dd))


def _primary(cats, mode):
    if mode == "elearning":
        return "corsi-elearning"
    for k in ("primo-soccorso", "corsi-blsd", "antincendio", "haccp", "aggiornamento-professionale", "sicurezza-sul-lavoro"):
        if k in cats:
            return k
    return cats[0] if cats else "sicurezza-sul-lavoro"


# --------------------------------------------------------------------------- contatti
_c = _read(_os.path.join(_CONTENT, "impostazioni", "contatti.json"))
COMPANY = {
    "name": _c["name"], "address": _c["address"], "city": _c["city"], "piva": _c["piva"], "rea": _c["rea"],
    "capitale": _c["capitale"],
    "phones": [(p["label"], p["number"]) for p in _c["phones"]],
    "emails": [(e["label"], e["email"]) for e in _c["emails"]],
    "facebook": _c["facebook"], "instagram": _c["instagram"], "maps": _c["maps"],
}

# --------------------------------------------------------------------------- corsi
TODAY = _dt.date.today()
ALL_COURSES = []
for _s, _d in _collection("corsi").items():
    _days = sorted(((_dmy(x["date"]), (x.get("time") or "").strip()) for x in _d.get("days") or [] if x.get("date")),
                   key=lambda x: _dkey(x[0]))
    _cats = _d.get("categories") or []
    _mode = _d.get("mode") or "presenza"
    _seats = _num(_d.get("seats"))
    ALL_COURSES.append(dict(
        slug=_s, id=_s, title=_d["title"], title_full=_d["title"], img=_d.get("image") or "/assets/img/aggiornamento.webp",
        gallery=[], price=euro(_d.get("price")), cats=_cats, mode=_mode, days=_days,
        place=_d.get("place") or "", validity=_d.get("validity") or "", seats=_seats, note=_d.get("note") or "",
        short=md(_d.get("short")), tabs=[{"title": "Descrizione", "html": md(_d.get("description"))}],
        shipping="", in_stock=_seats != 0, stock="", primary=_primary(_cats, _mode),
    ))
for _c in ALL_COURSES:
    _c["past"] = bool(_c["days"]) and _dt.date(*_dkey(_c["days"][-1][0])) < TODAY
# corsi con date: dal più vicino; e-learning in coda in ordine alfabetico
ALL_COURSES.sort(key=lambda c: (0, _dkey(c["days"][0][0]), c["title"]) if c["days"] else (1, (0, 0, 0), c["title"]))
# come nel tema originale, le edizioni concluse non compaiono negli elenchi (la pagina resta)
COURSES = [c for c in ALL_COURSES if not c["past"]]
COURSE_BY_SLUG = {c["slug"]: c for c in COURSES}

# --------------------------------------------------------------------------- prodotti
PRODUCTS = []
for _s, _d in _collection("prodotti").items():
    _ship = float(_d.get("shipping") or 0)
    PRODUCTS.append(dict(
        slug=_s, id=_s, title=_d["title"], title_full=_d["title"], img=_d.get("image") or "",
        gallery=_d.get("gallery") or [], price=euro(_d.get("price")), cats=[_d.get("category")], mode="",
        days=[], place="", validity="", seats=None, note="", short=md(_d.get("short")),
        tabs=[{"title": "Descrizione e contenuto", "html": md(_d.get("description"))}],
        shipping=f"{euro(_ship)} € per unità" if _ship else "", in_stock=_d.get("in_stock", True) is not False,
        stock="", primary=_d.get("category") or "altri-prodotti",
    ))
PRODUCTS.sort(key=lambda p: p["title"])
PRODUCT_BY_SLUG = {p["slug"]: p for p in PRODUCTS}
ALL_SLUGS = {c["slug"] for c in ALL_COURSES} | set(PRODUCT_BY_SLUG)

# --------------------------------------------------------------------------- categorie
_COURSE_KEYS = ["primo-soccorso", "antincendio", "sicurezza-sul-lavoro", "aggiornamento-professionale",
                "corsi-elearning", "corsi-blsd", "haccp"]
CATEGORIES = {}
for _k, _d in _collection("categorie").items():
    if _k in _COURSE_KEYS:
        _items = [c["slug"] for c in COURSES if _k in c["cats"] or c["primary"] == _k]
    else:
        _items = [p["slug"] for p in PRODUCTS if p["primary"] == _k]
    CATEGORIES[_k] = {"title": _d["title"], "html": md(_d.get("intro")), "products": _items}

# --------------------------------------------------------------------------- news e pagine legali
NEWS = []
for _s, _d in _collection("news").items():
    _html = md(_d.get("body"))
    _txt = _re.sub(r"\s+", " ", _re.sub(r"<[^>]+>", " ", _html)).strip()
    NEWS.append(dict(
        slug=_s, title=_d["title"], date=_dmy(_d["date"]), image=_d.get("image") or "/assets/img/foto-homepage-aula-v433.webp",
        files=[f for f in (_d.get("files") or []) if f], html=_html,
        excerpt=(_txt[:200].rsplit(" ", 1)[0] + "…") if len(_txt) > 200 else _txt,
    ))
NEWS.sort(key=lambda n: (_dkey(n["date"]), n["title"]), reverse=True)

LEGAL = {k: {"title": d["title"], "html": md(d.get("body"))} for k, d in _collection("legali").items()}
