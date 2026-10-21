# Medicare Italia – HSE · sito e area admin

Sito statico di hse.medicareitalia.com con area admin online su `/admin/`.
I contenuti (corsi, prodotti, news, categorie, pagine legali, contatti) si modificano dal
pannello. Ogni salvataggio crea un commit su GitHub e GitHub Actions rigenera e pubblica il sito
in 1–2 minuti.

```
content/            contenuti modificabili dall'admin (un file JSON per voce)
  corsi/ prodotti/ news/ categorie/ legali/ impostazioni/contatti.json
admin/              area admin (Sveltia CMS): index.html + config.yml
assets/             CSS, JS, immagini; assets/uploads/ = immagini e file caricati dall'admin
_build/             generatore: build.py (pagine), contenuti.py (lettura dei contenuti), data.py
.github/workflows/  pubblica.yml: build + pubblicazione su GitHub Pages
index.html, corsi/, product/, …  pagine generate da build.py nella cartella principale
_build/pagine-generate.txt  elenco delle pagine generate (serve a eliminare quelle non più esistenti)
```

## Messa online (una volta sola)

1. **Crea il repository su GitHub** (es. `medicareitalia/sito-hse`) e caricaci questa cartella.
   Con un account GitHub gratuito, GitHub Pages funziona solo con repository pubblici; per un
   repository privato serve un piano a pagamento (Pro/Team).
2. **Indica il repository all'admin**: in `admin/config.yml` sostituisci `repo: OWNER/REPO` con il
   nome reale (es. `repo: medicareitalia/sito-hse`).
3. **Attiva GitHub Pages**: Settings → Pages → Build and deployment → Source: **GitHub Actions**.
   Il primo push avvia il workflow "Pubblica sito".
4. **Dominio**: in Settings → Pages → Custom domain inserisci `hse.medicareitalia.com`, poi nel DNS
   del dominio crea un record `CNAME` da `hse` a `<utente-o-organizzazione>.github.io`.
   Quando il certificato è pronto, attiva "Enforce HTTPS".
5. **Chi può modificare**: aggiungi ogni redattore come collaboratore del repository con ruolo
   *Write* (Settings → Collaborators).

## Accesso all'area admin

Vai su https://hse.medicareitalia.com/admin/ e scegli **Accedi con Token di Accesso**:

1. il pannello apre la pagina GitHub per creare il token con i permessi già selezionati;
2. genera il token, copialo e incollalo nel pannello: resta salvato in quel browser.

Se preferisci un pulsante "Accedi con GitHub", senza token, va configurato un piccolo servizio
OAuth, ad esempio *Sveltia CMS Authenticator* su Cloudflare Workers (gratuito). Poi si aggiunge
`base_url: <indirizzo del servizio>` sotto `backend:` in `admin/config.yml`. Guida:
https://sveltiacms.app/en/docs/backends/github

## Cosa si gestisce dal pannello

| Raccolta | Cosa contiene |
|---|---|
| Corsi | titolo, categorie, modalità, prezzo, posti, giornate e orari, sede, validità, immagine, descrizioni |
| Prodotti shop | nome, categoria, prezzo, spedizione, disponibilità, immagini, descrizioni |
| News e aggiornamenti | articoli con copertina, testo e documenti scaricabili (PDF) |
| Categorie | titolo e testo introduttivo delle pagine categoria |
| Pagine legali | privacy, cookie policy, termini e condizioni, modulo di recesso |
| Impostazioni | contatti e dati aziendali usati in tutto il sito (telefoni, email, indirizzo, social) |

Note utili:

- **Nuova edizione di un corso**: apri il corso → menu ⋮ → *Duplica*, poi cambia le date.
  Le edizioni dello stesso corso si collegano tra loro nella scheda ("Altre edizioni").
- **Edizioni concluse**: escono da sole da calendario e categorie, perché il sito viene rigenerato
  anche ogni notte. La pagina del corso resta, segnata come conclusa.
- **Posti a 0** = iscrizioni chiuse ("Esaurito"). I posti non scalano da soli con le richieste.
- **Pubblicato** spento = la voce resta nel pannello ma sparisce dal sito.
- Le immagini caricate finiscono in `assets/uploads/`: meglio WebP o JPG sotto i 300 KB.
- I testi delle pagine di servizio (Home, Sicurezza sul lavoro, Medicina del lavoro, Consulenza HSE,
  HACCP, Chi siamo…) sono ancora nel codice (`_build/build.py`), non nel pannello.

## Lavorare in locale

```bash
pip install -r requirements.txt
```

```bash
python _build/build.py
```

```bash
python -m http.server 8765
```

Il sito è su http://localhost:8765. Per usare il pannello sui file locali, senza GitHub, avvia
`python -m http.server 8766` nella cartella del progetto, apri http://localhost:8766/admin/ con
Chrome o Edge e scegli **Lavora con Repository Locale**. Serve che la cartella sia un repository
Git.

## Pubblicare sull'hosting attuale invece che su GitHub Pages

Se il sito deve restare sull'hosting attuale, in `.github/workflows/pubblica.yml` sostituisci il job
`deploy` (e lo step `upload-pages-artifact`) con un caricamento FTP della cartella `_site/` (la cartella principale senza `_build`, `content` e file di lavoro, già preparata dal workflow), ad
esempio con `SamKirkland/FTP-Deploy-Action`. Le credenziali FTP vanno messe nei *Secrets* del
repository.

## Carrello e moduli

Senza backend il carrello resta nel browser del visitatore. "Invia richiesta" e i moduli Contatti,
Lavora con noi e Newsletter aprono un'e-mail già compilata verso formazione@ o
rspp@medicareitalia.org. Per riceverli direttamente aggiungi al `<form>` l'attributo
`data-endpoint="https://…"` (Formspree, Netlify Forms o un tuo script).
