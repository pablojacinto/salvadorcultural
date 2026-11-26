(() => {
  "use strict";
  const $ = (s, el = document) => el.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const semAcento = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

  // ---------- datas (fuso de Salvador) ----------
  const hojeISO = () => new Intl.DateTimeFormat("en-CA", { timeZone: "America/Bahia" }).format(new Date());
  const paraData = (iso) => { const [y, m, d] = iso.split("-").map(Number); return new Date(Date.UTC(y, m - 1, d)); };
  const isoDe = (dt) => dt.toISOString().slice(0, 10);
  const somaDias = (iso, n) => { const d = paraData(iso); d.setUTCDate(d.getUTCDate() + n); return isoDe(d); };
  const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
  const DIAS = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"];
  const curta = (iso) => { const d = paraData(iso); return `${d.getUTCDate()} ${MESES[d.getUTCMonth()]}`; };
  const fimDe = (e) => e.data_fim || e.data;
  const quandoTexto = (e) => {
    if (!e.data_fim) {
      const d = paraData(e.data);
      const mais = (e._datas || []).slice(1, 4).map(curta);
      return `${DIAS[d.getUTCDay()]}, ${curta(e.data)}${mais.length ? " (também " + mais.join(", ") + ((e._datas.length > 4) ? "…" : "") + ")" : ""}`;
    }
    return `${curta(e.data)} — ${curta(e.data_fim)}`;
  };

  // ---------- visual por categoria ----------
  const CATS = {
    "Música e cultura popular": { cor: "#e3b863", ink: "#1b3f45", ico: "onda" },
    "Teatro, dança e humor": { cor: "#d9775a", ink: "#fff3ea", ico: "meia" },
    "Exposições e museus": { cor: "#a6b09c", ink: "#1b3f45", ico: "estrela" },
    "Festas populares e festivais": { cor: "#c5aecb", ink: "#3b2c45", ico: "sol" },
    "Crianças e famílias": { cor: "#9fc3c0", ink: "#1b3f45", ico: "meia" },
    "Literatura e formação": { cor: "#ebe4d4", ink: "#1b3f45", ico: "estrela" },
    "Cinema e audiovisual": { cor: "#c7b28f", ink: "#1b3f45", ico: "onda" },
  };
  // a cor do cartão varia; o ícone e o rótulo indicam a linguagem
  const PALETA = [
    { cor: "#e3b863", ink: "#1b3f45" }, { cor: "#d9775a", ink: "#2a1712" }, { cor: "#a6b09c", ink: "#1b3f45" },
    { cor: "#c5aecb", ink: "#3b2c45" }, { cor: "#9fc3c0", ink: "#1b3f45" },
  ];
  const icone = (tipo, ink) => {
    const anel = `<circle cx="50" cy="50" r="46" fill="none" stroke="${ink}" stroke-opacity=".35"/><circle cx="50" cy="50" r="30" fill="none" stroke="${ink}" stroke-opacity=".5"/>`;
    const formas = {
      onda: `<path d="M28 56c6-14 12-14 16 0s10 14 16 0 10-14 12-2" fill="none" stroke="${ink}" stroke-width="7" stroke-linecap="round"/>`,
      meia: `<path d="M33 50a17 17 0 0 0 34 0z" fill="${ink}"/><circle cx="50" cy="50" r="17" fill="none" stroke="${ink}" stroke-width="3"/>`,
      estrela: `<g stroke="${ink}" stroke-width="3" stroke-linecap="round"><path d="M50 30v40M30 50h40M36 36l28 28M64 36 36 64"/></g>`,
      sol: `<circle cx="50" cy="50" r="12" fill="${ink}"/><g stroke="${ink}" stroke-width="3" stroke-linecap="round"><path d="M50 26v8M50 66v8M26 50h8M66 50h8M33 33l6 6M61 61l6 6M67 33l-6 6M39 61l-6 6"/></g>`,
    };
    return `<svg class="ico" viewBox="0 0 100 100" aria-hidden="true">${anel}${formas[tipo] || formas.onda}</svg>`;
  };
  const icoLocal = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 21s7-6.5 7-12a7 7 0 1 0-14 0c0 5.5 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>`;
  const icoHora = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>`;
  const icoOk = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="m5 12 5 5 9-10"/></svg>`;

  const dataHora = (s) => { if (!s) return "—"; const d = new Date(s); return d.toLocaleDateString("pt-BR", { day: "numeric", month: "long", year: "numeric", timeZone: "America/Bahia" }) + ", " + d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", timeZone: "America/Bahia" }).replace(":", "h"); };
  const dataVerif = (s) => { if (!s) return ""; const d = new Date(s); return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric", timeZone: "America/Bahia" }); };

  const card = (e, hoje) => {
    const base = CATS[e.categoria] || CATS["Música e cultura popular"];
    const h = [...e.id].reduce((a, ch) => (a * 31 + ch.charCodeAt(0)) >>> 0, 7);
    const c = { ...base, ...PALETA[h % PALETA.length] };
    const ref = e.data < hoje && e.data_fim ? hoje : e.data;
    const d = paraData(ref);
    const selos = [];
    if (e.data_fim) selos.push(e.data <= hoje ? "Em cartaz" : "Temporada");
    if (e.noite) selos.push("Noite");
    return `<article class="card">
      <div class="card-arte${e.imagem ? " com-img" : ""}" style="background:${c.cor};color:${c.ink}">
        ${e.imagem ? `<img src="${esc(e.imagem)}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.parentNode.classList.remove('com-img');this.remove()">` : ""}
        <div class="dia"><b>${d.getUTCDate()}</b><span>${MESES[d.getUTCMonth()]}</span></div>
        ${icone(c.ico, c.ink)}
        ${selos.length ? `<div class="selos">${selos.map((s) => `<span class="selo-mini">${s}</span>`).join("")}</div>` : ""}
        <span class="cat">${esc(e.categoria)}</span>
      </div>
      <div class="card-corpo">
        <p class="meta" style="margin:0">${icoHora}<span><strong>${esc(quandoTexto(e))}</strong>${e.horario ? " · " + esc(e.horario) : ""}</span></p>
        <h3>${esc(e.titulo)}</h3>
        <p class="meta" style="margin:0">${icoLocal}<span>${esc(e.local)}${e.bairro ? " · " + esc(e.bairro) : ""}</span></p>
        ${e.descricao ? `<p class="desc">${esc(e.descricao)}</p>` : ""}
        <div class="card-pe">
          <span class="preco${e.gratuito ? " gratis" : ""}">${esc(e.preco || "Consulte a fonte")}</span>
          <div class="acoes">
            <a class="link-fonte" href="${esc(e.url)}" target="_blank" rel="noopener">Ver na fonte <span aria-hidden="true">↗</span><span class="sr-only"> (abre em nova aba): ${esc(e.titulo)}</span></a>
            <button type="button" class="mini" data-ics="${esc(e.id)}" aria-label="Adicionar ${esc(e.titulo)} ao calendário">+ Calendário</button>
          </div>
          <p class="origem" style="margin:0">${icoOk}<span>Fonte: <a href="${esc(e.fonte_url)}" target="_blank" rel="noopener">${esc(e.fonte_nome)}</a> · verificado em ${esc(dataVerif(e.verificado_em))}</span></p>
        </div>
      </div>
    </article>`;
  };

  // ---------- estado ----------
  let EVENTOS = [];
  const PASSO = 24;
  const st = { busca: "", bairro: "", gratis: false, noite: false, quando: "tudo", cat: "", limite: PASSO };

  const janela = (q, hoje) => {
    if (q === "hoje") return [hoje, hoje];
    if (q === "7") return [hoje, somaDias(hoje, 6)];
    if (q === "30") return [hoje, somaDias(hoje, 29)];
    if (q === "fds") {
      const dow = paraData(hoje).getUTCDay();
      if (dow === 0) return [hoje, hoje];
      const sab = somaDias(hoje, (6 - dow + 7) % 7);
      return [dow === 6 ? hoje : somaDias(sab, -1), somaDias(sab, 1)]; // sexta a domingo
    }
    return null;
  };

  const filtrar = () => {
    const hoje = hojeISO();
    const j = janela(st.quando, hoje);
    const q = semAcento(st.busca).trim();
    return EVENTOS.filter((e) => {
      if (fimDe(e) < hoje) return false;
      if (j && e._datas) { if (!e._datas.some((d) => d >= j[0] && d <= j[1])) return false; }
      else if (j && (e.data > j[1] || fimDe(e) < j[0])) return false;
      if (st.gratis && !e.gratuito) return false;
      if (st.noite && !e.noite) return false;
      if (st.cat && e.categoria !== st.cat) return false;
      if (st.bairro && e.bairro !== st.bairro) return false;
      if (q && !semAcento([e.titulo, e.local, e.bairro, e.descricao, e.categoria].join(" ")).includes(q)) return false;
      return true;
    });
  };

  const render = () => {
    const hoje = hojeISO();
    const res = filtrar();
    const lista = $("#lista");
    lista.innerHTML = res.length
      ? res.slice(0, st.limite).map((e) => card(e, hoje)).join("")
      : `<div class="vazio" style="grid-column:1/-1"><p><strong>Nenhum evento com esses filtros.</strong></p><p>Tente outro período ou limpe os filtros. Faltou algo? <a href="https://github.com/pablojacinto/salvadorcultural/issues/new?template=correcao.md">Sugira um evento</a>.</p></div>`;
    $("#contagem").textContent = res.length === 1 ? "1 evento encontrado" : `${res.length} eventos encontrados`;
    $("#ver-mais").hidden = res.length <= st.limite;
    const filtrado = st.busca || st.bairro || st.gratis || st.noite || st.cat || st.quando !== "tudo";
    $("#limpar").hidden = !filtrado;
  };

  const renderNoite = () => {
    const hoje = hojeISO();
    const n = EVENTOS.filter((e) => e.noite && fimDe(e) >= hoje).slice(0, 9);
    $("#lista-noite").innerHTML = n.length ? n.map((e) => card(e, hoje)).join("") : `<p>Sem eventos noturnos confirmados no momento.</p>`;
  };

  // ---------- calendário (.ics) ----------
  const ics = (e) => {
    const d0 = e.data.replace(/-/g, "");
    const d1 = somaDias(fimDe(e), 1).replace(/-/g, "");
    const t = (s) => String(s || "").replace(/[\\,;]/g, (m) => "\\" + m).replace(/\n/g, " ");
    const stamp = new Date().toISOString().replace(/[-:]/g, "").slice(0, 15) + "Z";
    const txt = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//salvadorcultural//agenda//PT", "BEGIN:VEVENT",
      `UID:${e.id}@salvadorcultural`, `DTSTAMP:${stamp}`, `DTSTART;VALUE=DATE:${d0}`, `DTEND;VALUE=DATE:${d1}`,
      `SUMMARY:${t(e.titulo)}`, `LOCATION:${t(e.local + (e.bairro ? ", " + e.bairro : "") + ", Salvador - BA")}`,
      `DESCRIPTION:${t((e.horario ? "Horário: " + e.horario + ". " : "") + "Confirme na fonte: " + e.url)}`, `URL:${e.url}`,
      "END:VEVENT", "END:VCALENDAR"].join("\r\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([txt], { type: "text/calendar" }));
    a.download = `${e.id}.ics`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
    toast("Arquivo de calendário baixado");
  };
  const toast = (m) => { const t = $("#toast"); t.textContent = m; t.classList.add("on"); setTimeout(() => t.classList.remove("on"), 2200); };

  // ---------- guia, noite, fontes ----------
  const iniciais = (n) => n.replace(/[^\p{L}\s]/gu, "").split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase();
  const CORES = ["#e3b863", "#d9775a", "#a6b09c", "#c5aecb", "#9fc3c0"];
  const renderEspacos = (esp) => {
    $("#lista-guia").innerHTML = esp.guia.map((g, i) => {
      const tag = g.url ? "a" : "div";
      const attrs = g.url ? ` href="${esc(g.url)}" target="_blank" rel="noopener"` : "";
      return `<${tag} class="espaco"${attrs}><span class="n">${String(i + 1).padStart(2, "0")}${g.url ? ' <span aria-hidden="true">↗</span>' : ""}</span><h3>${esc(g.nome)}</h3><p>${esc(g.linguagem)}${g.descricao ? ". " + esc(g.descricao) : ""}</p><span class="bairro">${icoLocal}${esc(g.bairro)}</span></${tag}>`;
    }).join("");
    $("#lista-casas").innerHTML = esp.noite.map((c, i) => {
      const tag = c.url ? "a" : "div";
      const attrs = c.url ? ` href="${esc(c.url)}" target="_blank" rel="noopener"` : "";
      return `<${tag} class="casa"${attrs}><span class="avatar" style="background:${CORES[i % CORES.length]}" aria-hidden="true">${esc(iniciais(c.nome))}</span><span><b>${esc(c.nome)}</b><small>${esc(c.perfil)}${c.bairro ? " · " + esc(c.bairro) : ""}</small></span></${tag}>`;
    }).join("");
  };

  let FONTES = [];
  let tipoFonte = "";
  const renderFontes = () => {
    const tipos = [...new Set(FONTES.map((f) => f.tipo))];
    $("#filtro-fontes").innerHTML = ["", ...tipos].map((t) => `<button type="button" class="chip" data-t="${esc(t)}" aria-pressed="${t === tipoFonte}">${t ? esc(t) : "Todas"}</button>`).join("");
    $("#lista-fontes").innerHTML = FONTES.filter((f) => !tipoFonte || f.tipo === tipoFonte).map((f) => {
      const auto = f.consulta_automatica;
      const status = [f.status_acesso, f.ultima_consulta ? "consulta em " + dataVerif(f.ultima_consulta) : null,
        auto ? `checagem automática: ${auto.resultado} (${dataVerif(auto.em)})` : null].filter(Boolean).join(" · ");
      return `<div class="fonte"><a href="${esc(f.source_url)}" target="_blank" rel="noopener">${esc(f.source_name)}</a><span class="tag">${esc(f.tipo)}</span><small>${esc(status)}</small></div>`;
    }).join("");
  };

  // ---------- eventos de interface ----------
  const ligar = () => {
    $("#f-busca").addEventListener("input", (ev) => { st.busca = ev.target.value; st.limite = PASSO; render(); });
    $("#f-bairro").addEventListener("change", (ev) => { st.bairro = ev.target.value; st.limite = PASSO; render(); });
    $("#f-gratis").addEventListener("change", (ev) => { st.gratis = ev.target.checked; st.limite = PASSO; render(); });
    $("#f-noite").addEventListener("change", (ev) => { st.noite = ev.target.checked; st.limite = PASSO; render(); });
    $("#f-quando").addEventListener("click", (ev) => {
      const b = ev.target.closest("button"); if (!b) return;
      st.quando = b.dataset.v; st.limite = PASSO;
      $("#f-quando").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b));
      render();
    });
    $("#f-cat").addEventListener("click", (ev) => {
      const b = ev.target.closest("button"); if (!b) return;
      st.cat = b.dataset.v; st.limite = PASSO;
      $("#f-cat").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b));
      render();
    });
    $("#ver-mais").addEventListener("click", () => { st.limite += PASSO; render(); });
    $("#limpar").addEventListener("click", () => {
      Object.assign(st, { busca: "", bairro: "", gratis: false, noite: false, quando: "tudo", cat: "", limite: PASSO });
      $("#f-busca").value = ""; $("#f-bairro").value = ""; $("#f-gratis").checked = false; $("#f-noite").checked = false;
      document.querySelectorAll("#f-quando button, #f-cat button").forEach((x) => x.setAttribute("aria-pressed", x.dataset.v === "tudo" || x.dataset.v === ""));
      render();
    });
    document.addEventListener("click", (ev) => {
      const b = ev.target.closest("[data-ics]"); if (!b) return;
      const e = EVENTOS.find((x) => x.id === b.dataset.ics); if (e) ics(e);
    });
    $("#filtro-fontes").addEventListener("click", (ev) => { const b = ev.target.closest("button"); if (!b) return; tipoFonte = b.dataset.t; renderFontes(); });
    $("#btn-hoje").addEventListener("click", (ev) => {
      ev.preventDefault();
      $("#f-quando").querySelector('[data-v="hoje"]').click();
      $("#agenda").scrollIntoView();
    });
    const mb = $(".menu-btn"), menu = $("#menu");
    mb.addEventListener("click", () => { const a = menu.classList.toggle("aberto"); mb.setAttribute("aria-expanded", a); });
    menu.addEventListener("click", (ev) => { if (ev.target.closest("a")) { menu.classList.remove("aberto"); mb.setAttribute("aria-expanded", "false"); } });
  };

  const carregar = async () => {
    ligar();
    try {
      const [ev, es, fo] = await Promise.all(["data/eventos.json", "data/espacos.json", "data/fontes.json"].map((u) => fetch(u, { cache: "no-cache" }).then((r) => { if (!r.ok) throw new Error(u); return r.json(); })));
      const hoje = hojeISO();
      // eventos em dias separados (campo "datas"): o card mostra o próximo dia e cita os seguintes
      for (const e of ev.eventos) {
        if (!Array.isArray(e.datas) || !e.datas.length) continue;
        const prox = e.datas.slice().sort().filter((d) => d >= hoje);
        delete e.data_fim;
        e.data = prox[0] || e.datas[e.datas.length - 1];
        e._datas = prox.length ? prox : null;
      }
      EVENTOS = ev.eventos.slice().sort((a, b) => {
        const ka = a.data < hoje ? hoje : a.data, kb = b.data < hoje ? hoje : b.data;
        return ka.localeCompare(kb) || (a.data_fim ? 1 : 0) - (b.data_fim ? 1 : 0) || a.titulo.localeCompare(b.titulo, "pt");
      });
      const ativos = EVENTOS.filter((e) => fimDe(e) >= hoje);
      $("#n-eventos").textContent = ativos.length;
      $("#n-gratis").textContent = ativos.filter((e) => e.gratuito).length;
      $("#n-fontes").textContent = fo.fontes.length;
      const quandoAtual = dataHora(ev.atualizado_em);
      $("#ultima-atualizacao").innerHTML = `<strong>Última atualização da agenda:</strong> ${esc(quandoAtual)}.`;
      $("#atualizado-topo").textContent = `Agenda atualizada em ${quandoAtual}`;
      const cats = [...new Set(ativos.map((e) => e.categoria))].sort((a, b) => a.localeCompare(b, "pt"));
      $("#f-cat").innerHTML = [`<button type="button" class="chip" data-v="" aria-pressed="true">Todas</button>`, ...cats.map((c) => `<button type="button" class="chip" data-v="${esc(c)}" aria-pressed="false">${esc(c)}</button>`)].join("");
      const bairros = [...new Set(ativos.map((e) => e.bairro).filter(Boolean))].sort((a, b) => a.localeCompare(b, "pt"));
      $("#f-bairro").insertAdjacentHTML("beforeend", bairros.map((b) => `<option>${esc(b)}</option>`).join(""));
      FONTES = fo.fontes;
      render(); renderNoite(); renderEspacos(es); renderFontes();
      if (location.hash === "#hoje") $("#btn-hoje").click();
    } catch (err) {
      $("#contagem").textContent = "Não foi possível carregar a agenda agora. Tente recarregar a página.";
      console.error(err);
    }
  };
  carregar();
})();
