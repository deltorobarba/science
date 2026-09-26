(() => {
  const main = document.getElementById("main");
  const q = document.getElementById("q");
  const result = document.getElementById("result");
  const empty = document.getElementById("empty");
  const units = [...document.querySelectorAll("[data-unit]")];
  const papers = units.filter((u) => u.classList.contains("paper"));
  const parts = [...document.querySelectorAll("details.part")];
  let task = "";
  let status = "";

  /* ---------- formulas: rendered when they become visible ---------- */
  const queue = new Set();
  let scheduled = false;

  function shown(el) {
    for (let d = el.parentElement.closest("details"); d; d = d.parentElement.closest("details")) {
      if (!d.open && !d.querySelector(":scope > summary").contains(el)) return false;
    }
    return true;
  }
  function renderMath(root) {
    root.querySelectorAll(".math:not(.done)").forEach((el) => { if (shown(el)) queue.add(el); });
    if (!scheduled && queue.size) { scheduled = true; requestAnimationFrame(drain); }
  }
  function drain() {
    scheduled = false;
    if (!window.katex) return;
    let n = 0;
    for (const el of queue) {
      queue.delete(el);
      if (!el.classList.contains("done")) {
        try {
          katex.render(el.dataset.tex, el, {
            displayMode: el.classList.contains("display"), throwOnError: false, strict: "ignore",
          });
        } catch (e) { /* the TeX source stays visible */ }
        el.classList.add("done");
      }
      if (++n >= 160) break;
    }
    if (queue.size) { scheduled = true; requestAnimationFrame(drain); }
  }
  document.addEventListener("toggle", (e) => { if (e.target.open) { renderMath(e.target); renderDiagrams(e.target); } }, true);

  /* ---------- diagrams: Mermaid is loaded only when a diagram becomes visible ---------- */
  const MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  let mermaidReady = null;
  function loadMermaid() {
    if (!mermaidReady) {
      mermaidReady = import(MERMAID).then(({ default: mermaid }) => mermaid).catch(() => null);
    }
    return mermaidReady;
  }
  function themeMermaid(mermaid) {
    const css = getComputedStyle(document.documentElement);
    const v = (name) => css.getPropertyValue(name).trim();
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      theme: "base",
      fontFamily: v("--font-ui"),
      themeVariables: {
        fontSize: "13px",
        background: v("--surface"),
        primaryColor: v("--accent-weak"),
        primaryBorderColor: v("--accent"),
        primaryTextColor: v("--ink"),
        lineColor: v("--ink-2"),
        textColor: v("--ink"),
      },
      block: { useMaxWidth: true },
      flowchart: { useMaxWidth: true },
    });
  }
  const MIN_DIAGRAM_WIDTH = 900; // below this, wide diagrams scroll instead of shrinking
  function sizeDiagram(el) {
    const svg = el.querySelector("svg");
    if (svg && svg.viewBox.baseVal && svg.viewBox.baseVal.width > MIN_DIAGRAM_WIDTH) {
      svg.style.minWidth = MIN_DIAGRAM_WIDTH + "px";
    }
  }
  async function renderDiagrams(root) {
    const nodes = [...root.querySelectorAll("pre.mermaid:not([data-processed]):not([data-pending])")].filter(shown);
    if (!nodes.length) return;
    nodes.forEach((el) => {
      el.dataset.pending = "1";
      if (!el.dataset.src) el.dataset.src = el.textContent;
    });
    const mermaid = await loadMermaid();
    if (mermaid) {
      themeMermaid(mermaid);
      try { await mermaid.run({ nodes }); } catch (e) { console.warn("diagram:", e); }
    }
    nodes.forEach((el) => { delete el.dataset.pending; sizeDiagram(el); });
  }
  const scheme = window.matchMedia("(prefers-color-scheme: dark)");
  scheme.addEventListener("change", () => {
    main.querySelectorAll("pre.mermaid[data-processed]").forEach((el) => {
      el.removeAttribute("data-processed");
      el.textContent = el.dataset.src;
    });
    renderDiagrams(main);
  });

  /* ---------- navigation ---------- */
  function reveal(el) {
    if (el.hidden || el.closest("[hidden]")) resetFilters();
    if (el.classList.contains("paper")) el.querySelector(".paper-d").open = true;
    if (el.tagName === "DETAILS") el.open = true;
    for (let d = el.parentElement.closest("details"); d; d = d.parentElement.closest("details")) d.open = true;
  }
  function go(id, smooth) {
    const el = document.getElementById(id);
    if (!el) return false;
    reveal(el);
    requestAnimationFrame(() => el.scrollIntoView({ behavior: smooth ? "smooth" : "auto", block: "start" }));
    return true;
  }
  document.addEventListener("click", (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    const id = decodeURIComponent(a.getAttribute("href").slice(1));
    if (!document.getElementById(id)) return;
    e.preventDefault();
    try { history.pushState(null, "", "#" + id); } catch (err) { /* not allowed in every frame */ }
    go(id, true);
    document.body.classList.remove("toc-open");
    tocBtn.setAttribute("aria-expanded", "false");
  });
  window.addEventListener("hashchange", () => go(decodeURIComponent(location.hash.slice(1)), true));

  /* ---------- sidebar on small screens ---------- */
  const tocBtn = document.getElementById("toc-btn");
  tocBtn.addEventListener("click", () => {
    const open = document.body.classList.toggle("toc-open");
    tocBtn.setAttribute("aria-expanded", String(open));
  });
  main.addEventListener("click", (e) => {
    if (document.body.classList.contains("toc-open") && !e.target.closest("#toc-btn")) {
      document.body.classList.remove("toc-open");
      tocBtn.setAttribute("aria-expanded", "false");
    }
  });

  /* ---------- expand and collapse ---------- */
  document.getElementById("expand").addEventListener("click", () => {
    main.querySelectorAll("details").forEach((d) => { if (!d.closest("[hidden]")) d.open = true; });
    renderMath(main);
    renderDiagrams(main);
  });
  document.getElementById("collapse").addEventListener("click", () => {
    main.querySelectorAll("details.sec, details.paper-d").forEach((d) => { d.open = false; });
  });

  /* ---------- search and filters ---------- */
  const texts = new Map();
  const textOf = (u) => {
    if (!texts.has(u)) texts.set(u, u.textContent.toLowerCase());
    return texts.get(u);
  };
  let saved = null;

  function paperPasses(u) {
    if (task && u.dataset.task !== task) return false;
    if (status === "ggg" && !(u.dataset.c === "g" && u.dataset.t === "g" && u.dataset.m === "g")) return false;
    if (status === "t-r" && u.dataset.t !== "r") return false;
    if (status === "c-r" && u.dataset.c !== "r") return false;
    return true;
  }

  function apply() {
    const raw = q.value.trim().toLowerCase();
    const terms = raw.length >= 2 ? raw.split(/\s+/) : [];
    const searching = terms.length > 0;
    const filtering = Boolean(task || status);
    if ((searching || filtering) && !saved) saved = [...main.querySelectorAll("details")].map((d) => [d, d.open]);
    if (!searching && !filtering && saved) { saved.forEach(([d, o]) => { d.open = o; }); saved = null; }
    document.body.classList.toggle("narrowed", searching || filtering);

    let nPapers = 0;
    let nSecs = 0;
    for (const u of units) {
      const isPaper = u.classList.contains("paper");
      let ok = isPaper ? paperPasses(u) : !filtering;
      if (ok && searching) ok = terms.every((t) => textOf(u).includes(t));
      u.hidden = !ok;
      if (!ok) continue;
      if (isPaper) nPapers += 1; else nSecs += 1;
      if (searching) {
        if (isPaper) u.querySelector(".paper-d").open = true; else u.open = true;
      }
    }
    for (const p of parts) {
      p.hidden = (searching || filtering) && !p.querySelector("[data-unit]:not([hidden])");
      if (!p.hidden) p.open = true;
    }
    empty.hidden = !(searching || filtering) || nPapers + nSecs > 0;
    if (searching) result.textContent = `${nPapers} papers, ${nSecs} sections`;
    else if (filtering) result.textContent = `${nPapers} of ${papers.length} papers`;
    else result.textContent = `${papers.length} papers`;
    highlight(searching ? terms : []);
    renderMath(main);
  }

  function highlight(terms) {
    if (!window.CSS || !CSS.highlights) return;
    CSS.highlights.delete("hit");
    if (!terms.length) return;
    const ranges = [];
    for (const u of units) {
      if (u.hidden) continue;
      const walker = document.createTreeWalker(u, NodeFilter.SHOW_TEXT);
      for (let node = walker.nextNode(); node && ranges.length < 600; node = walker.nextNode()) {
        if (node.parentElement.closest(".katex, .math")) continue;
        const text = node.data.toLowerCase();
        for (const t of terms) {
          for (let i = text.indexOf(t); i !== -1 && ranges.length < 600; i = text.indexOf(t, i + t.length)) {
            const r = new Range();
            r.setStart(node, i);
            r.setEnd(node, i + t.length);
            ranges.push(r);
          }
        }
      }
    }
    CSS.highlights.set("hit", new Highlight(...ranges));
  }

  function setChips(group, attr, value) {
    group.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset[attr] === value)));
  }
  function resetFilters() {
    task = "";
    status = "";
    q.value = "";
    setChips(taskChips, "task", "");
    setChips(statusChips, "status", "");
    apply();
  }
  const taskChips = document.getElementById("task-chips");
  const statusChips = document.getElementById("status-chips");
  taskChips.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    task = b.dataset.task;
    setChips(taskChips, "task", task);
    apply();
  });
  statusChips.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    status = b.dataset.status;
    setChips(statusChips, "status", status);
    apply();
  });
  let timer = 0;
  q.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(apply, 180); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== q && !e.target.closest("input, textarea")) {
      e.preventDefault();
      q.focus();
    }
    if (e.key === "Escape" && document.activeElement === q && q.value) { q.value = ""; apply(); }
  });

  /* ---------- current position in the sidebar ---------- */
  const tocLinks = new Map([...document.querySelectorAll(".toc-part li a")].map((a) => [a.getAttribute("href").slice(1), a]));
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      for (const en of entries) {
        if (!en.isIntersecting) continue;
        const a = tocLinks.get(en.target.id);
        if (!a) continue;
        document.querySelectorAll(".toc-part li a.here").forEach((x) => x.classList.remove("here"));
        a.classList.add("here");
      }
    }, { rootMargin: "-20% 0px -70% 0px" });
    units.forEach((u) => io.observe(u));
  }

  /* ---------- start ---------- */
  result.textContent = `${papers.length} papers`;
  renderMath(main);
  renderDiagrams(main);
  if (location.hash.length > 1) go(decodeURIComponent(location.hash.slice(1)), false);
})();
