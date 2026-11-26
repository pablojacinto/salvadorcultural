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
  const re = new RegExp(`((?:\\d{1,2}º?(?:\\s*\\([^)]{0,20}\\))?\\s*(?:,|e|a|à|até|-|–)?\\s*){1,12})(?:de\\s+)?(${MESES.join("|")})(?:\\s+de\\s+(\\d{4}))?`, "gi");
  for (const m of t.matchAll(re)) {
    const mm = MESES.indexOf(m[2].toLowerCase()) + 1;
    const dias = [...m[1].matchAll(/\d{1,2}/g)].map((x) => +x[0]).filter((d) => d >= 1 && d <= 31);
    const faixa = /\d\s*(?:\([^)]*\)\s*)?(?:a|à|até|-|–)\s*\d/.test(m[1]) && dias.length === 2;
    if (faixa) for (let d = dias[0]; d <= dias[1]; d++) out.add(comAno(d, mm, m[3]));
    else for (const d of dias) out.add(comAno(d, mm, m[3]));
  }
  return [...out].sort();
}

// dia no fuso de Salvador: "2026-11-29T01:30:00Z" (UTC) é 28/11 às 22h30 aqui
const diaBahia = (s) => /T\d\d:\d\d.*(Z|[+-]\d\d:?\d\d)$/.test(s)
  ? new Intl.DateTimeFormat("en-CA", { timeZone: "America/Bahia" }).format(new Date(s)) : s.slice(0, 10);

// datas de JSON-LD (Event.startDate/endDate), em qualquer nível
function datasJsonLd(h) {
  const ini = [], fim = [];
  for (const m of h.matchAll(/<script[^>]*application\/ld\+json[^>]*>([\s\S]*?)<\/script>/gi)) {
    for (const x of m[1].matchAll(/"startDate"\s*:\s*"(\d{4}-\d{2}-\d{2}[^"]*)"/g)) ini.push(diaBahia(x[1]));
    for (const x of m[1].matchAll(/"endDate"\s*:\s*"(\d{4}-\d{2}-\d{2}[^"]*)"/g)) fim.push(diaBahia(x[1]));
  }
  return { ini: [...new Set(ini)].sort(), fim: [...new Set(fim)].sort() };
}

function sympla(h) {
  const m = h.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/);
  if (!m) return null;
  try {
    const e = JSON.parse(m[1]).props.pageProps.hydrationData.eventHydration.event;
    return { ini: e.startDate ? diaBahia(e.startDate.replace(" ", "T")) : "", fim: e.endDate ? diaBahia(e.endDate.replace(" ", "T")) : "", cancelado: !!e.cancelled, desc: e.strippedDetail || "" };
  } catch { return null; }
}

const dados = JSON.parse(await readFile("data/eventos.json", "utf8"));
const porUrl = {};
for (const e of dados.eventos) porUrl[e.url] = (porUrl[e.url] || 0) + 1;
const ultimo = (e) => e.datas?.length ? [...e.datas].sort().at(-1) : (e.data_fim || e.data);
const ativos = dados.eventos.filter((e) => ultimo(e) >= hoje);
const passados = dados.eventos.filter((e) => ultimo(e) < hoje);
// sites que montam a página no navegador (a data não vem no HTML): ficam para conferência manual
const SO_NAVEGADOR = /bileto\.sympla\.com\.br|balcaodeingressos\.com|ingresse\.com|ticketmaker|uhuu\.com/;
const res = [];
const cache = {};
const ultimaVez = {};
const abrir = async (url) => {
  if (cache[url]) return cache[url];
  const host = new URL(url).host;
  const espera = /shotgun/.test(host) ? 3000 : 0;   // a Shotgun limita requisições seguidas
  if (espera && ultimaVez[host]) await dormir(Math.max(0, espera - (Date.now() - ultimaVez[host])));
  let r = await baixar(url);
  if (r.status === 429) { await dormir(20000); r = await baixar(url); }   // uma nova tentativa, com calma
  ultimaVez[host] = Date.now();
  return (cache[url] = r);
};
const diasEntre = (a, b) => (Date.parse(b) - Date.parse(a)) / 864e5;

for (const e of ativos) {
  const item = { id: e.id, titulo: e.titulo, url: e.url, agenda: { data: e.data, data_fim: e.data_fim || null, datas: e.datas || null }, problemas: [], aviso: [] };
  res.push(item);
  if (SO_NAVEGADOR.test(e.url)) { item.manual = true; continue; }
  const r = await abrir(e.url);
  if (!r.html) {
    if (r.status === 403 || r.status === 429) item.bloqueado = `o site recusou o robô (${r.status})`;
    else item.problemas.push(`a página não abriu (${r.status}); o link pode ter saído do ar`);
    continue;
  }
  const inicio = e.data, fim = e.data_fim || e.data;
  const sp = /sympla\.com\.br\/evento\//.test(e.url) ? sympla(r.html) : null;
  const ld = porUrl[e.url] === 1 ? datasJsonLd(r.html) : { ini: [], fim: [] };
  let txt = datasNoTexto(texto(r.html) + "\n" + (sp ? sp.desc : ""));
  const descSp = sp ? datasNoTexto(sp.desc) : [];
  item.fonte = { sympla: sp && { ini: sp.ini, fim: sp.fim, cancelado: sp.cancelado }, jsonld: ld };

  if (sp?.cancelado) item.problemas.push("a Sympla marca o evento como cancelado");
  if (/"eventStatus"\s*:\s*"[^"]*Cancel/i.test(r.html)) item.problemas.push("a página marca o evento como cancelado");

  if (e.datas?.length) {
    // dias separados: cada dia que ainda vai acontecer precisa aparecer na página
    const vem = e.datas.filter((d) => d >= hoje);
    const faltam = vem.filter((d) => !txt.includes(d) && !ld.ini.includes(d) && sp?.ini !== d && sp?.fim !== d);
    if (faltam.length) item.aviso.push(`os dias ${faltam.map(br).join(", ")} não aparecem escritos na página`);
  } else if (sp && sp.ini) {
    const umDia = !sp.fim || sp.fim === sp.ini || (diasEntre(sp.ini, sp.fim) === 1 && !e.data_fim); // festa que vira a noite
    if (sp.ini !== inicio) item.problemas.push(`a página diz que começa em ${br(sp.ini)}; a agenda diz ${br(inicio)}`);
    else if (!umDia && sp.fim !== fim) item.problemas.push(`a página diz que vai até ${br(sp.fim)}; a agenda diz ${br(fim)}`);
    else if (umDia && e.data_fim && e.data_fim !== e.data) item.problemas.push(`a página indica um só dia (${br(sp.ini)}), mas a agenda mostra um período`);
    // período na agenda, mas a descrição da Sympla fala em dias separados
    if (e.data_fim && e.data_fim !== e.data) {
      const dentro = descSp.filter((d) => d >= inicio && d <= fim);
      if (dentro.length >= 2 && diasEntre(inicio, fim) + 1 > dentro.length + 1) {
        item.problemas.push(`a descrição cita só os dias ${dentro.map(br).join(", ")}; a agenda mostra de ${br(inicio)} a ${br(fim)} sem interrupção (use o campo "datas")`);
      }
    }
  } else if (ld.ini.length) {
    const ok = ld.ini.includes(inicio) || ld.ini.some((d, i) => d <= inicio && (ld.fim[i] || d) >= inicio) || (inicio < hoje && ld.ini.some((d) => d <= fim));
    if (!ok) item.problemas.push(`os dados da página indicam ${ld.ini.map(br).join(", ")}; a agenda diz ${br(inicio)}`);
  }

  // a data da agenda aparece escrita em algum lugar? (se não, tenta a página da fonte, ex. calendário oficial)
  if (!e.datas?.length && inicio >= hoje && !txt.includes(inicio) && sp?.ini !== inicio && !ld.ini.includes(inicio)) {
    let achou = false;
    if (e.fonte_url && e.fonte_url !== e.url) {
      const f = await abrir(e.fonte_url);
      if (f.html) achou = datasNoTexto(texto(f.html)).includes(inicio);
    }
    if (!achou) item.aviso.push(`a data ${br(inicio)} não aparece escrita na página do evento nem na da fonte`);
  }
}

function somaMeses(n) { const d = new Date(hoje + "T12:00:00Z"); d.setUTCMonth(d.getUTCMonth() + n); return d.toISOString().slice(0, 10); }

const quando = (x) => x.agenda.datas ? x.agenda.datas.map(br).join(", ") : br(x.agenda.data) + (x.agenda.data_fim ? " a " + br(x.agenda.data_fim) : "");
const comProblema = res.filter((x) => x.problemas.length);
const soAviso = res.filter((x) => !x.problemas.length && x.aviso.length);
const bloqueados = res.filter((x) => x.bloqueado);
const manuais = res.filter((x) => x.manual);
const ok = res.length - comProblema.length - soAviso.length - bloqueados.length - manuais.length;
const linha = (x) => `- [ ] **${x.titulo}** (agenda: ${quando(x)}): ${[...x.problemas, ...x.aviso, x.bloqueado].filter(Boolean).join("; ")}. ${x.url}`;
const curta = (x) => `- [ ] ${x.titulo} (agenda: ${quando(x)}) · ${x.url}`;
const md = `Conferência automática de ${br(hoje)}/${hoje.slice(0, 4)}: ${ativos.length} eventos em cartaz. **${ok} conferem com a página oficial**, ${comProblema.length} têm divergência e ${soAviso.length} pedem uma olhada.\n\n`
  + `Nada foi mudado no site. Corrija em data/eventos.json o que estiver errado (ou remova o evento). Evento em dias separados usa o campo "datas": ["AAAA-MM-DD", ...].\n\n`
  + `## Divergências (${comProblema.length})\n\n` + (comProblema.map(linha).join("\n") || "Nenhuma.") + "\n\n"
  + `## Data não encontrada na página (${soAviso.length})\n\nPode ser só o jeito como a página escreve a data. Vale uma olhada rápida.\n\n` + (soAviso.map(linha).join("\n") || "Nenhum.") + "\n\n"
  + `## Conferir no navegador (${manuais.length + bloqueados.length})\n\nEstes sites montam a página só no navegador ou recusam robôs; o robô não consegue ler a data. Confira de vez em quando, principalmente os mais próximos.\n\n`
  + [...bloqueados, ...manuais].sort((a, b) => a.agenda.data.localeCompare(b.agenda.data)).map(curta).join("\n") + "\n\n"
  + `## Já terminaram (${passados.length})\n\nSaem da lista do site sozinhos; podem ser apagados de data/eventos.json quando for conveniente.\n`;

await mkdir("conferencia", { recursive: true });
await writeFile("conferencia/relatorio.md", md.slice(0, 64000));
await writeFile("conferencia/resultado.json", JSON.stringify({ data: hoje, resultado: res }, null, 1));
await writeFile("conferencia/contagem.txt", String(comProblema.length + soAviso.length));
console.log(`Em cartaz: ${ativos.length}. Conferem: ${ok}. Divergências: ${comProblema.length}. Avisos: ${soAviso.length}. No navegador: ${manuais.length + bloqueados.length}. Passados: ${passados.length}.`);
