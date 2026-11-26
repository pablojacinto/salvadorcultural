// Conferência de datas: abre a página oficial de cada evento da agenda e compara com data/eventos.json.
// Roda no GitHub Actions (Node 20+, sem dependências). Não altera a agenda: escreve um relatório
// (conferencia/relatorio.md e conferencia/resultado.json) que vira uma issue para revisão.
// Respeita bloqueios (não tenta contornar 403/429) e espera entre as requisições.
import { mkdir, readFile, writeFile } from "node:fs/promises";

const UA = "salvadorcultural-conferencia/1.0 (+https://pablojacinto.github.io/salvadorcultural/)";
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
const hoje = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Bahia" }).format(new Date());
const MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
const br = (iso) => iso ? iso.slice(8, 10) + "/" + iso.slice(5, 7) : "?";

async function baixar(url) {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), 25000);
  try {
    const r = await fetch(url, { redirect: "follow", signal: c.signal, headers: { "user-agent": UA, "accept-language": "pt-BR,pt;q=0.9" } });
    return { status: r.status, html: r.ok ? await r.text() : "", final: r.url };
  } catch (e) {
    return { status: e.name === "AbortError" ? "tempo esgotado" : "erro de conexão", html: "" };
  } finally { clearTimeout(t); await dormir(700); }
}

const texto = (h) => h
  .replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ")
  .replace(/<br\s*\/?>|<\/(p|div|li|h\d|tr|section|article)>/gi, "\n").replace(/<[^>]+>/g, " ")
  .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&#0?39;/g, "'").replace(/&quot;/g, '"').replace(/[ \t]+/g, " ");

// ano provável de uma data sem ano: a agenda olha para a frente (até ~10 meses)
const comAno = (d, m, a) => {
  if (a) return `${a < 100 ? 2000 + +a : a}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
  const [ya, ma] = hoje.split("-").map(Number);
  const y = m < ma - 2 ? ya + 1 : ya;
  return `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
};

// datas escritas no texto: 27/11, 27/11/2026, "27 de novembro", "14 (sábado) e 27 (sexta) de novembro", "5 a 9 de dezembro"
function datasNoTexto(t) {
  const out = new Set();
  for (const m of t.matchAll(/\b(\d{1,2})\/(\d{1,2})(?:\/(\d{2,4}))?\b/g)) {
    const d = +m[1], mm = +m[2];
    if (d >= 1 && d <= 31 && mm >= 1 && mm <= 12) out.add(comAno(d, mm, m[3]));
  }
  const re = new RegExp(`((?:\\d{1,2}º?(?:\\s*\\([^)]{0,20}\\))?\\s*(?:,|e|a|à|até|-|–)?\\s*){1,12})de\\s+(${MESES.join("|")})(?:\\s+de\\s+(\\d{4}))?`, "gi");
  for (const m of t.matchAll(re)) {
    const mm = MESES.indexOf(m[2].toLowerCase()) + 1;
    const dias = [...m[1].matchAll(/\d{1,2}/g)].map((x) => +x[0]).filter((d) => d >= 1 && d <= 31);
    const faixa = /\d\s*(?:\([^)]*\)\s*)?(?:a|à|até|-|–)\s*\d/.test(m[1]) && dias.length === 2;
    if (faixa) for (let d = dias[0]; d <= dias[1]; d++) out.add(comAno(d, mm, m[3]));
    else for (const d of dias) out.add(comAno(d, mm, m[3]));
  }
  return [...out].sort();
}

// datas de JSON-LD (Event.startDate/endDate), em qualquer nível
function datasJsonLd(h) {
  const ini = [], fim = [];
  for (const m of h.matchAll(/<script[^>]*application\/ld\+json[^>]*>([\s\S]*?)<\/script>/gi)) {
    for (const x of m[1].matchAll(/"startDate"\s*:\s*"(\d{4}-\d{2}-\d{2})/g)) ini.push(x[1]);
    for (const x of m[1].matchAll(/"endDate"\s*:\s*"(\d{4}-\d{2}-\d{2})/g)) fim.push(x[1]);
  }
  return { ini: [...new Set(ini)].sort(), fim: [...new Set(fim)].sort() };
}

function sympla(h) {
  const m = h.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/);
  if (!m) return null;
  try {
    const e = JSON.parse(m[1]).props.pageProps.hydrationData.eventHydration.event;
    return { ini: (e.startDate || "").slice(0, 10), fim: (e.endDate || "").slice(0, 10), cancelado: !!e.cancelled, desc: e.strippedDetail || "" };
  } catch { return null; }
}

const dados = JSON.parse(await readFile("data/eventos.json", "utf8"));
const porUrl = {};
for (const e of dados.eventos) porUrl[e.url] = (porUrl[e.url] || 0) + 1;
const ativos = dados.eventos.filter((e) => (e.data_fim || e.data) >= hoje);
const passados = dados.eventos.filter((e) => (e.data_fim || e.data) < hoje);
const res = [];
const cache = {};

for (const e of ativos) {
  const r = cache[e.url] || (cache[e.url] = await baixar(e.url));
  const item = { id: e.id, titulo: e.titulo, url: e.url, agenda: { data: e.data, data_fim: e.data_fim || null }, problemas: [], aviso: [] };
  res.push(item);
  if (!r.html) { item.problemas.push(`a página não abriu (${r.status})`); continue; }
  const inicio = e.data, fim = e.data_fim || e.data;
  const sp = /sympla\.com\.br\/evento\//.test(e.url) ? sympla(r.html) : null;
  const ld = datasJsonLd(r.html);
  const txt = datasNoTexto(texto(r.html) + "\n" + (sp ? sp.desc : ""));
  item.fonte = { sympla: sp && { ini: sp.ini, fim: sp.fim, cancelado: sp.cancelado }, jsonld: ld, texto: txt.filter((d) => d >= somaMeses(-1) && d <= somaMeses(14)) };

  if (sp) {
    if (sp.cancelado) item.problemas.push("a Sympla marca o evento como cancelado");
    if (sp.ini && sp.ini !== inicio) item.problemas.push(`a página diz que começa em ${br(sp.ini)}; a agenda diz ${br(inicio)}`);
    if (sp.fim && sp.fim !== fim && sp.fim !== sp.ini) item.problemas.push(`a página diz que termina em ${br(sp.fim)}; a agenda diz ${br(fim)}`);
    if (!sp.fim || sp.fim === sp.ini) { if (e.data_fim && e.data_fim !== e.data) item.problemas.push(`a página indica um só dia (${br(sp.ini)}), mas a agenda mostra um período`); }
  } else if (ld.ini.length && porUrl[e.url] === 1) {
    const dentro = ld.ini.includes(inicio) || ld.ini.some((d, i) => d <= inicio && (ld.fim[i] || d) >= inicio);
    if (!dentro) item.problemas.push(`os dados da página indicam ${ld.ini.map(br).join(", ")}; a agenda diz ${br(inicio)}`);
  }

  // período contínuo na agenda, mas o texto da página fala em dias separados dentro dele
  if (e.data_fim && e.data_fim !== e.data) {
    const dentro = txt.filter((d) => d >= inicio && d <= fim);
    const dias = (Date.parse(fim) - Date.parse(inicio)) / 864e5 + 1;
    if (dentro.length >= 2 && dentro.length <= 6 && dias > dentro.length + 2) {
      item.problemas.push(`a página cita só os dias ${dentro.map(br).join(", ")}; a agenda mostra de ${br(inicio)} a ${br(fim)} sem interrupção`);
    }
  }
  // a data da agenda aparece em algum lugar da página?
  const ref = inicio < hoje ? null : inicio;
  if (ref && !txt.includes(ref) && !(sp && sp.ini === ref) && !ld.ini.includes(ref)) {
    item.aviso.push(`a data ${br(ref)} não aparece escrita na página`);
  }
}

function somaMeses(n) { const d = new Date(hoje + "T12:00:00Z"); d.setUTCMonth(d.getUTCMonth() + n); return d.toISOString().slice(0, 10); }

const comProblema = res.filter((x) => x.problemas.length);
const soAviso = res.filter((x) => !x.problemas.length && x.aviso.length);
const linha = (x) => `- [ ] **${x.titulo}** (agenda: ${br(x.agenda.data)}${x.agenda.data_fim ? " a " + br(x.agenda.data_fim) : ""}): ${[...x.problemas, ...x.aviso].join("; ")}. ${x.url}`;
const md = `Conferência automática de ${br(hoje)}/${hoje.slice(0, 4)}: ${ativos.length} eventos em cartaz conferidos na página oficial de cada um.\n\n`
  + `Nada foi mudado no site. Corrija em data/eventos.json o que estiver errado (ou remova o evento) e feche os itens.\n\n`
  + `## Divergências (${comProblema.length})\n\n` + (comProblema.map(linha).join("\n") || "Nenhuma.") + "\n\n"
  + `## Data não encontrada no texto da página (${soAviso.length})\n\nPode ser só o jeito como a página escreve a data, ou uma página de programação geral. Vale uma olhada rápida.\n\n`
  + (soAviso.map(linha).join("\n") || "Nenhum.") + "\n\n"
  + `## Já terminaram (${passados.length})\n\nSaem da lista do site sozinhos; podem ser apagados de data/eventos.json quando for conveniente.\n`;

await mkdir("conferencia", { recursive: true });
await writeFile("conferencia/relatorio.md", md.slice(0, 64000));
await writeFile("conferencia/resultado.json", JSON.stringify({ data: hoje, resultado: res }, null, 1));
await writeFile("conferencia/contagem.txt", String(comProblema.length));
console.log(`Conferidos: ${ativos.length}. Divergências: ${comProblema.length}. Avisos: ${soAviso.length}. Passados: ${passados.length}.`);
