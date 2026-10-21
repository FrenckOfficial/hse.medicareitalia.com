# -*- coding: utf-8 -*-
"""Contenuti del sito, ripresi 1:1 da hse.medicareitalia.com (ottobre 2026)."""

ORIGIN = "https://hse.medicareitalia.com"
IMG = "/assets/img/"

# COMPANY (contatti e dati aziendali) è in content/impostazioni/contatti.json, caricato da contenuti.py

NAV = [
    ("Corsi", "/corsi/"),
    ("Sicurezza sul lavoro", "/sicurezza-sul-lavoro/"),
    ("Medicina del lavoro", "/medicina-del-lavoro/"),
    ("Servizi HSE", "/consulenza-hse/"),
    ("Shop", "/shop/"),
    ("News", "/news-e-aggiornamenti/"),
    ("Lavora con noi", "/lavora-con-noi/"),
]

FOOTER_EXPLORE = [
    ("Calendario corsi", "/corsi/"),
    ("Shop online", "/shop/"),
    ("Consulenza HSE", "/consulenza-hse/"),
    ("Sicurezza sul lavoro", "/sicurezza-sul-lavoro/"),
    ("Medicina del lavoro", "/medicina-del-lavoro/"),
    ("Lavora con noi", "/lavora-con-noi/"),
    ("Chi siamo", "/chi-siamo/"),
    ("Trasparenza", "/trasparenza/"),
]

TOWNS = ["Grado", "Aquileia", "Cervignano del Friuli", "Monfalcone", "Ronchi dei Legionari",
         "Staranzano", "Gradisca d’Isonzo", "Cormons", "Gorizia", "Trieste", "Udine", "Pordenone"]

# --- Categorie corsi --------------------------------------------------------
# key, titolo, testo, immagine, colore
COURSE_CATS = [
    ("primo-soccorso", "Primo Soccorso",
     "Corsi di primo soccorso e aggiornamenti per addetti aziendali, con edizioni a Grado e formazione presso le imprese da concordare.",
     "ChatGPT-Image-12-ago-2026-13_21_51-768x512.webp", "#d12528"),
    ("antincendio", "Antincendio",
     "Corsi antincendio di livello 1 e 2 e aggiornamenti per gli addetti aziendali. Edizioni a Grado e corsi presso le imprese da concordare.",
     "antincendio.webp", "#e0611a"),
    ("sicurezza-sul-lavoro", "Sicurezza sul lavoro",
     "Formazione generale, specifica e aggiornamenti per i lavoratori: consulta i corsi in presenza, in videoconferenza e in e-learning.",
     "sicurezza-lavoro.webp", "#007aa1"),
    ("aggiornamento-professionale", "Aggiornamento professionale",
     "Aggiornamenti obbligatori e formazione continua per lavoratori e figure aziendali.",
     "aggiornamento.webp", "#4656c8"),
    ("corsi-elearning", "Corsi e-learning",
     "Formazione online da svolgere comodamente da telefono, PC o tablet.",
     "elearning.webp", "#6f42c1"),
    ("corsi-blsd", "Corsi BLSD",
     "Percorsi BLSD e BLS con addestramento pratico per l’uso del defibrillatore.",
     "blsd.webp", "#9f1239"),
    ("haccp", "HACCP",
     "Corsi per alimentaristi e responsabili, con percorsi iniziali e aggiornamenti periodici.",
     "haccp.webp", "#1b8d3a"),
]

MODES = {
    "presenza": "In presenza",
    "videoconferenza": "Videoconferenza sincrona",
    "elearning": "E-learning",
}

# --- Shop --------------------------------------------------------------------
SHOP_CATS = [
    ("cassette-pronto-soccorso", "Cassette di pronto soccorso", "Cassette complete, reintegri e materiali per aziende e attività.", "kit"),
    ("defibrillatori", "Defibrillatori", "Defibrillatori, teche, accessori e materiali di consumo.", "heart"),
    ("cartellonistica", "Cartellonistica", "Segnaletica di sicurezza, emergenza, obbligo e divieto.", "sign"),
    ("altri-prodotti", "Altri prodotti", "Ulteriori dispositivi e articoli per salute e sicurezza.", "box"),
]


