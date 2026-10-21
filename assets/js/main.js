/* Medicare Italia – HSE · interazioni */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.documentElement.classList.add("js");

  /* ---------------------------------------------------------------- header */
  const header = $("[data-header]");
  const onScroll = () => header && header.classList.toggle("is-scrolled", scrollY > 10);
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  const burger = $("[data-menu]");
  const setMenu = (open) => {
    if (open && header) document.documentElement.style.setProperty("--nav-top", header.getBoundingClientRect().bottom + "px");
    document.body.classList.toggle("menu-open", open);
    if (burger) {
      burger.setAttribute("aria-expanded", String(open));
      burger.setAttribute("aria-label", open ? "Chiudi menu" : "Apri menu");
    }
  };
  burger && burger.addEventListener("click", () => setMenu(!document.body.classList.contains("menu-open")));
  $$("[data-nav] a").forEach((a) => a.addEventListener("click", () => setMenu(false)));

  /* ---------------------------------------------------------------- reveal */
  const io = "IntersectionObserver" in window && !reduce
    ? new IntersectionObserver((entries) => entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      }), { rootMargin: "0px 0px -8% 0px", threshold: 0.08 })
    : null;
  const watch = (el) => (io ? io.observe(el) : el.classList.add("is-in"));
  $$(".reveal, .radar").forEach(watch);

  /* ---------------------------------------------------------------- tilt + glow */
  if (!reduce && matchMedia("(hover: hover)").matches) {
    $$("[data-tilt]").forEach((el) => {
      const target = el.querySelector(".hero-photo") || el.querySelector("img");
      el.addEventListener("pointermove", (ev) => {
        const r = el.getBoundingClientRect();
        const x = (ev.clientX - r.left) / r.width - 0.5;
        const y = (ev.clientY - r.top) / r.height - 0.5;
        target.style.transform = `rotateY(${x * 10}deg) rotateX(${-y * 8}deg)`;
      });
      el.addEventListener("pointerleave", () => (target.style.transform = ""));
    });
    $$(".svc-card").forEach((el) => el.addEventListener("pointermove", (ev) => {
      const r = el.getBoundingClientRect();
      el.style.setProperty("--mx", `${ev.clientX - r.left}px`);
      el.style.setProperty("--my", `${ev.clientY - r.top}px`);
    }));
  }

  /* ---------------------------------------------------------------- search */
  const layer = $("[data-search]");
  const input = $("[data-search-input]");
  const results = $("[data-search-results]");
  let index = null;
  let active = -1;
  const norm = (s) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const loadIndex = () => index || fetch("/assets/js/search-index.json").then((r) => r.json()).then((d) => (index = d)).catch(() => (index = []));
  const render = () => {
    if (!Array.isArray(index)) return;
    const q = norm(input.value.trim());
    const words = q.split(/\s+/).filter(Boolean);
    const list = words.length
      ? index.filter((it) => words.every((w) => norm(it.t + " " + it.k).includes(w))).slice(0, 12)
      : index.slice(0, 7);
    active = -1;
    results.innerHTML = list.length
      ? list.map((it) => {
          let t = esc(it.t);
          words.forEach((w) => {
            const i = norm(it.t).indexOf(w);
            if (i > -1 && w.length > 1) t = esc(it.t.slice(0, i)) + "<mark>" + esc(it.t.slice(i, i + w.length)) + "</mark>" + esc(it.t.slice(i + w.length));
          });
          return `<li><a href="${esc(it.u)}"><span>${t}</span><small>${esc(it.k)}</small></a></li>`;
        }).join("")
      : '<li class="none">Nessun risultato. Prova con “primo soccorso”, “DVR”, “HACCP”…</li>';
  };
  const openSearch = async () => {
    layer.hidden = false;
    document.body.style.overflow = "hidden";
    input.focus();
    await loadIndex();
    render();
  };
  const closeSearch = () => { layer.hidden = true; document.body.style.overflow = ""; };
  $$("[data-search-open]").forEach((b) => b.addEventListener("click", openSearch));
  $("[data-search-close]") && $("[data-search-close]").addEventListener("click", closeSearch);
  layer && layer.addEventListener("click", (ev) => ev.target === layer && closeSearch());
  input && input.addEventListener("input", render);
  input && input.addEventListener("keydown", (ev) => {
    const links = $$("a", results);
    if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
      ev.preventDefault();
      active = (active + (ev.key === "ArrowDown" ? 1 : -1) + links.length) % links.length;
      links.forEach((l, i) => l.classList.toggle("is-active", i === active));
      links[active] && links[active].scrollIntoView({ block: "nearest" });
    } else if (ev.key === "Enter" && links.length) {
      (links[active] || links[0]).click();
    }
  });
  addEventListener("keydown", (ev) => {
    if (ev.key === "Escape") { closeSearch(); setMenu(false); }
    if ((ev.key === "k" && (ev.metaKey || ev.ctrlKey)) || (ev.key === "/" && !/input|textarea/i.test(document.activeElement.tagName))) {
      ev.preventDefault(); openSearch();
    }
  });

  /* ---------------------------------------------------------------- course catalog */
  const catalog = $(".catalog");
  if (catalog) {
    const cards = $$(".course", catalog);
    const groups = $$(".cgroup", catalog);
    const chipsEl = $$("[data-filter]", catalog);
    const modeEl = $$(".seg [data-mode]", catalog);
    const qEl = $("[data-course-search]", catalog);
    const count = $("[data-count]", catalog);
    const empty = $("[data-empty]", catalog);
    const state = { cat: "all", mode: "all", q: "" };

    const apply = () => {
      const q = norm(state.q.trim());
      let shown = 0;
      cards.forEach((c) => {
        const ok = (state.cat === "all" || c.dataset.cats.split(" ").includes(state.cat)) &&
          (state.mode === "all" || c.dataset.mode === state.mode) &&
          (!q || norm(c.dataset.q).includes(q));
        c.hidden = !ok;
        if (ok) shown++;
      });
      groups.forEach((g) => {
        if (g.dataset.group === "antincendio") { g.hidden = state.cat !== "antincendio"; return; }
        g.hidden = !$$(".course", g).some((c) => !c.hidden);
      });
      chipsEl.forEach((b) => b.classList.toggle("is-on", b.dataset.filter === state.cat));
      modeEl.forEach((b) => b.classList.toggle("is-on", b.dataset.mode === state.mode));
      const anti = state.cat === "antincendio";
      empty.hidden = shown > 0 || anti;
      count.textContent = anti ? "" : `${shown} ${shown === 1 ? "corso trovato" : "corsi trovati"}`;
    };
    const fromHash = () => {
      const h = decodeURIComponent(location.hash.slice(1));
      if (chipsEl.some((b) => b.dataset.filter === h)) { state.cat = h; apply(); }
    };
    chipsEl.forEach((b) => b.addEventListener("click", () => {
      state.cat = b.dataset.filter;
      history.replaceState(null, "", state.cat === "all" ? location.pathname : "#" + state.cat);
      apply();
    }));
    modeEl.forEach((b) => b.addEventListener("click", () => { state.mode = b.dataset.mode; apply(); }));
    qEl.addEventListener("input", () => { state.q = qEl.value; apply(); });
    $("[data-reset]", catalog).addEventListener("click", () => {
      Object.assign(state, { cat: "all", mode: "all", q: "" }); qEl.value = ""; apply();
    });
    $$("[data-quick-mode]").forEach((a) => a.addEventListener("click", () => {
      Object.assign(state, { cat: "all", mode: a.dataset.quickMode }); apply();
    }));
    addEventListener("hashchange", () => {
      fromHash();
      if (location.hash) $(".filterbar").scrollIntoView({ behavior: reduce ? "auto" : "smooth" });
    });
    fromHash();
    apply();
    if (location.hash && state.cat !== "all") setTimeout(() => $(".filterbar").scrollIntoView(), 50);
  }

  /* ---------------------------------------------------------------- shop filter */
  const products = $("[data-products]");
  if (products) {
    const items = $$(".product", products);
    const btns = $$("[data-shop-filter]");
    const cnt = $("[data-shop-count]");
    const emptyShop = $("[data-shop-empty]");
    const set = (cat) => {
      let n = 0;
      items.forEach((p) => { const ok = cat === "all" || p.dataset.cat === cat; p.hidden = !ok; if (ok) n++; });
      btns.forEach((b) => b.classList.toggle("is-on", b.dataset.shopFilter === cat && (cat !== "all" || b.classList.contains("fchip"))));
      cnt.textContent = n === 1 ? "Visualizzazione di 1 risultato" : `Visualizzazione di ${n} risultati`;
      emptyShop.hidden = n > 0;
    };
    btns.forEach((b) => b.addEventListener("click", () => {
      const c = b.dataset.shopFilter;
      history.replaceState(null, "", c === "all" ? location.pathname : "#" + c);
      set(c);
    }));
    const h = location.hash.slice(1);
    set(btns.some((b) => b.dataset.shopFilter === h) ? h : "all");
  }

  /* ---------------------------------------------------------------- carrello
     Il carrello vive nel browser (localStorage); la pagina /cart/ invia la richiesta d'iscrizione/ordine. */
  const CART_KEY = "mi-cart-v1";
  const fmt = (n) => n.toLocaleString("it-IT", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
  const readCart = () => { try { const c = JSON.parse(localStorage.getItem(CART_KEY)); return Array.isArray(c) ? c : []; } catch { return []; } };
  let cart = readCart();
  const badge = $("[data-cart-count]");
  const updateBadge = (bump) => {
    if (!badge) return;
    const n = cart.reduce((a, i) => a + i.qty, 0);
    badge.textContent = n;
    badge.hidden = n === 0;
    if (bump) { badge.classList.remove("bump"); void badge.offsetWidth; badge.classList.add("bump"); }
  };
  const saveCart = (bump) => {
    try { localStorage.setItem(CART_KEY, JSON.stringify(cart)); } catch { /* storage non disponibile */ }
    updateBadge(bump);
    renderCart();
  };
  let toastEl, toastT;
  const toast = (text) => {
    if (!toastEl) {
      toastEl = document.createElement("div");
      toastEl.className = "toast";
      toastEl.setAttribute("role", "status");
      document.body.append(toastEl);
    }
    toastEl.innerHTML = '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 4.5 4.5L19 7"/></svg>' +
      `<span>${esc(text)}</span><a href="/cart/">Vai al carrello</a>`;
    toastEl.classList.add("is-on");
    clearTimeout(toastT);
    toastT = setTimeout(() => toastEl.classList.remove("is-on"), 3800);
  };
  const addToCart = (data, qty) => {
    const found = cart.find((i) => i.id === data.id);
    const max = data.max || 99;
    if (found) found.qty = Math.min(max, found.qty + qty);
    else cart.push({ ...data, qty: Math.min(max, qty) });
    saveCart(true);
  };
  document.addEventListener("click", (ev) => {
    const add = ev.target.closest("[data-add]");
    if (add) {
      const data = JSON.parse(add.dataset.add);
      const box = add.closest(".buy-in");
      const qIn = box && box.querySelector("[data-qty] input");
      const qty = Math.max(1, parseInt(qIn ? qIn.value : 1, 10) || 1);
      addToCart(data, qty);
      add.classList.add("is-added");
      setTimeout(() => add.classList.remove("is-added"), 1200);
      toast(`${qty > 1 ? qty + " × " : ""}${data.title} aggiunto al carrello`);
      return;
    }
    const step = ev.target.closest("[data-qty] [data-step]");
    if (step) {
      const inp = step.parentElement.querySelector("input");
      const v = (parseInt(inp.value, 10) || 1) + parseInt(step.dataset.step, 10);
      inp.value = Math.min(parseInt(inp.max, 10) || 99, Math.max(1, v));
      inp.dispatchEvent(new Event("change", { bubbles: true }));
    }
  });
  addEventListener("storage", (ev) => { if (ev.key === CART_KEY) { cart = readCart(); updateBadge(); renderCart(); } });

  const cartPage = $("[data-cart-page]");
  function renderCart() {
    if (!cartPage) return;
    const list = $("[data-cart-list]", cartPage);
    const empty = !cart.length;
    $("[data-cart-empty]", cartPage).hidden = !empty;
    $("[data-cart-clear]", cartPage).hidden = empty;
    $("#checkout").hidden = empty;
    $("[data-cart-summary]").hidden = empty;
    list.innerHTML = cart.map((i, n) => `
      <li class="cart-item">
        <a href="${esc(i.url)}" tabindex="-1"><img src="${esc(i.img)}" alt="" loading="lazy"></a>
        <div><h3><a href="${esc(i.url)}">${esc(i.title)}</a></h3><small>${esc(i.meta || "")}${i.kind === "course" ? " · " + i.qty + (i.qty === 1 ? " partecipante" : " partecipanti") : ""} · ${fmt(i.price)} cad.</small></div>
        <div class="cart-ctrl">
          <b>${fmt(i.price * i.qty)}</b>
          <div class="qty" data-qty><button type="button" data-step="-1" aria-label="Diminuisci">−</button><input type="number" value="${i.qty}" min="1" max="${i.max || 99}" data-cart-qty="${n}" aria-label="Quantità"><button type="button" data-step="1" aria-label="Aumenta">+</button></div>
          <button type="button" class="cart-remove" data-cart-remove="${n}">Rimuovi</button>
        </div>
      </li>`).join("");
    const sub = cart.reduce((a, i) => a + i.price * i.qty, 0);
    const ship = cart.reduce((a, i) => a + (i.ship || 0) * i.qty, 0);
    $("[data-sub]").textContent = fmt(sub);
    $("[data-ship]").textContent = fmt(ship);
    $("[data-ship-row]").hidden = !ship;
    $("[data-total]").textContent = fmt(sub + ship);
    const physical = cart.some((i) => i.kind === "product");
    $("[data-ship-field]").required = physical;
    $("[data-ship-req]").hidden = !physical;
    $("[data-course-only]").hidden = !cart.some((i) => i.kind === "course");
  }
  if (cartPage) {
    cartPage.addEventListener("change", (ev) => {
      const n = ev.target.dataset.cartQty;
      if (n === undefined) return;
      const it = cart[+n];
      it.qty = Math.min(it.max || 99, Math.max(1, parseInt(ev.target.value, 10) || 1));
      saveCart();
    });
    cartPage.addEventListener("click", (ev) => {
      const r = ev.target.closest("[data-cart-remove]");
      if (r) { cart.splice(+r.dataset.cartRemove, 1); saveCart(); }
      if (ev.target.closest("[data-cart-clear]")) { cart = []; saveCart(); }
    });
  }
  updateBadge();
  renderCart();

  /* ---------------------------------------------------------------- schede (tab) */
  $$("[data-tabs]").forEach((box) => {
    const btns = $$("[data-tab]", box);
    btns.forEach((b) => b.addEventListener("click", () => {
      btns.forEach((x) => x.setAttribute("aria-selected", String(x === b)));
      $$("[data-panel]", box).forEach((p) => (p.hidden = p.dataset.panel !== b.dataset.tab));
    }));
  });

  /* ---------------------------------------------------------------- forms
     Il sito è statico: in assenza di un endpoint (attributo data-endpoint) la richiesta
     viene preparata come e-mail verso l'indirizzo corretto. */
  $$("form[data-form]").forEach((form) => {
    const msg = $("[data-form-msg]", form);
    const show = (text, err) => { msg.hidden = false; msg.textContent = text; msg.classList.toggle("err", !!err); };
    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      if (form.website && form.website.value) return; // honeypot
      let bad = null;
      $$("[required]", form).forEach((f) => {
        const invalid = f.type === "checkbox" ? !f.checked : !f.value.trim() || (f.type === "email" && !/^\S+@\S+\.\S+$/.test(f.value));
        f.classList.toggle("is-bad", invalid);
        (f.closest(".dropzone") || f).classList.toggle("is-bad", invalid);
        if (invalid && !bad) bad = f;
      });
      if (bad) {
        show(bad.type === "checkbox" ? "Per proseguire è necessario accettare l’informativa sulla privacy." : "Compila i campi obbligatori contrassegnati da *.", true);
        bad.focus();
        return;
      }
      const cv = form.cv && form.cv.files[0];
      if (cv && cv.size > 5 * 1024 * 1024) { show("Il curriculum supera la dimensione massima di 5 MB.", true); return; }

      const data = new FormData(form);
      const endpoint = form.dataset.endpoint;
      if (endpoint) {
        if (form.dataset.form === "ordine") data.append("carrello", JSON.stringify(cart));
        try {
          const r = await fetch(endpoint, { method: "POST", body: data });
          if (!r.ok) throw new Error();
          form.reset();
          show("Grazie! La tua richiesta è stata inviata: ti ricontatteremo al più presto.");
        } catch { show("Si è verificato un errore durante l’invio. Riprova o contattaci telefonicamente.", true); }
        return;
      }
      const kind = form.dataset.form;
      const sel = form.querySelector('input[name="servizio"]:checked');
      const to = (sel && sel.dataset.to) || form.dataset.to;
      const subject = {
        contatti: "Richiesta preventivo" + (sel ? " – " + sel.value : ""),
        candidatura: "Candidatura spontanea – " + (data.get("profilo") || ""),
        newsletter: "Iscrizione agli aggiornamenti normativi",
        ordine: "Richiesta di iscrizione / ordine dal sito",
      }[kind];
      const labels = { nome: "Nome e cognome", azienda: "Azienda", email: "Email", telefono: "Telefono", fiscale: "Codice fiscale / P. IVA", sdi: "Codice destinatario / PEC", indirizzo: "Indirizzo", servizio: "Servizio richiesto", messaggio: "Messaggio", profilo: "Profilo professionale", presentazione: "Presentazione", partecipanti: "Partecipanti", note: "Note" };
      const lines = Object.entries(labels).filter(([k]) => data.get(k)).map(([k, l]) => `${l}: ${data.get(k)}`);
      if (kind === "ordine") {
        const sub = cart.reduce((t, i) => t + i.price * i.qty, 0);
        const ship = cart.reduce((t, i) => t + (i.ship || 0) * i.qty, 0);
        lines.unshift("RIEPILOGO", ...cart.map((i) => `- ${i.qty} × ${i.title}${i.meta ? " (" + i.meta + ")" : ""} – ${fmt(i.price * i.qty)} [cod. ${i.id}]`),
          ship ? `Spedizione: ${fmt(ship)}` : "", `Totale (IVA inclusa): ${fmt(sub + ship)}`, "", "DATI");
      }
      if (kind === "candidatura") lines.push("", "(Allego il curriculum vitae)");
      if (kind === "newsletter") lines.unshift("Desidero ricevere gli aggiornamenti normativi di Medicare Italia.");
      location.href = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join("\n"))}`;
      show(kind === "candidatura"
        ? "Abbiamo preparato l’e-mail nel tuo programma di posta: ricordati di allegare il curriculum prima di inviarla."
        : "Abbiamo preparato l’e-mail nel tuo programma di posta: controlla e premi Invia.");
    });
    $$("input, textarea", form).forEach((f) => f.addEventListener("input", () => f.classList.remove("is-bad")));
  });

  $$("[data-drop]").forEach((dz) => {
    const fi = $("input[type=file]", dz);
    const label = $("[data-drop-label]", dz);
    const orig = label.textContent;
    ["dragenter", "dragover"].forEach((t) => dz.addEventListener(t, (e) => { e.preventDefault(); dz.classList.add("is-over"); }));
    ["dragleave", "drop"].forEach((t) => dz.addEventListener(t, () => dz.classList.remove("is-over")));
    dz.addEventListener("drop", (e) => { e.preventDefault(); if (e.dataTransfer.files.length) { fi.files = e.dataTransfer.files; fi.dispatchEvent(new Event("change")); } });
    fi.addEventListener("change", () => {
      const f = fi.files[0];
      dz.classList.toggle("has-file", !!f);
      dz.classList.remove("is-bad");
      label.textContent = f ? `${f.name} · ${(f.size / 1024 / 1024).toFixed(2)} MB` : orig;
    });
  });

  /* ---------------------------------------------------------------- whatsapp + copy */
  const waT = $("[data-wa-toggle]");
  const waP = $("[data-wa-pop]");
  waT && waT.addEventListener("click", (ev) => {
    ev.stopPropagation();
    waP.hidden = !waP.hidden;
    waT.setAttribute("aria-expanded", String(!waP.hidden));
  });
  document.addEventListener("click", (ev) => { if (waP && !waP.hidden && !ev.target.closest("[data-wa]")) { waP.hidden = true; waT.setAttribute("aria-expanded", "false"); } });

  $$("[data-copy-btn]").forEach((b) => b.addEventListener("click", async () => {
    const code = b.parentElement.querySelector("[data-copy]");
    try { await navigator.clipboard.writeText(code.textContent.trim()); b.querySelector("span").textContent = "Copiato!"; }
    catch { b.querySelector("span").textContent = "Seleziona e copia"; }
    setTimeout(() => (b.querySelector("span").textContent = "Copia"), 2000);
  }));
})();
