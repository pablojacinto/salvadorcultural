// Coleta de candidatos a evento (roda no GitHub Actions, Node 20+, sem dependências).
// Lê páginas públicas das fontes do catálogo e guarda um retrato em coleta/ (branch "coleta").
// Nada daqui vai direto para o site: os candidatos são conferidos antes de entrar em data/eventos.json.
// Não faz login, respeita bloqueios (não tenta contornar 403/429) e espera entre as requisições.
import { mkdir, writeFile } from "node:fs/promises";

const UA = "salvadorcultural-coletor/1.0 (+https://pablojacinto.github.io/salvadorcultural/)";
const PAUSA = 700;
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
const log = [];

async function baixar(url) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 25000);
  try {
    const r = await fetch(url, { redirect: "follow", signal: ctrl.signal, headers: { "user-agent": UA, "accept-language": "pt-BR,pt;q=0.9" } });
    const txt = await r.text();
    log.push({ url, status: r.status });
    await dormir(PAUSA);
    return r.ok ? { html: txt, final: r.url } : null;
  } catch (e) {
    log.push({ url, status: e.name === "AbortError" ? "timeout" : "erro" });
    return null;
  } finally { clearTimeout(t); }
}

const semTags = (h) => h
  .replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ")
  .replace(/<br\s*\/?>|<\/(p|div|li|h\d|tr|section|article)>/gi, "\n")
  .replace(/<[^>]+>/g, " ").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#0?39;/g, "'")
  .replace(/[ \t]+/g, " ").replace(/\n\s*\n+/g, "\n").trim();

const links = (h, base) => {
  const out = [];
  for (const m of h.matchAll(/<a\b[^>]*href="([^"#]+)"[^>]*>([\s\S]*?)<\/a>/gi)) {
    try { out.push({ href: new URL(m[1], base).href.split("#")[0], txt: semTags(m[2]).slice(0, 140) }); } catch {}
  }
  return out;
};
const jsonld = (h) => [...h.matchAll(/<script[^>]*application\/ld\+json[^>]*>([\s\S]*?)<\/script>/gi)].map((m) => m[1].trim()).slice(0, 20);

// ---------- 1. Sympla: listagem de Salvador + dados estruturados de cada evento ----------
async function sympla() {
  const evs = new Map(), bileto = new Map();
  for (let p = 1; p <= 60; p++) {
    const r = await baixar(`https://www.sympla.com.br/eventos/salvador-ba?page=${p}`);
    if (!r) break;
    let novos = 0;
    for (const l of links(r.html, r.final)) {
      const k = l.href.split("?")[0];
      if (/sympla\.com\.br\/evento\//.test(k) && !evs.has(k)) { evs.set(k, l.txt); novos++; }
      if (/bileto\.sympla\.com\.br\/event\/\d+/.test(k) && !bileto.has(k)) { bileto.set(k, l.txt); novos++; }
    }
    if (!novos) break;
  }
  const out = [];
  for (const [url, txt] of evs) {
    const r = await baixar(url);
    if (!r) { out.push({ url, erro: true, txt }); continue; }
    const m = r.html.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/);
    try {
      const e = JSON.parse(m[1]).props.pageProps.hydrationData.eventHydration.event;
      const a = e.eventsAddress || {};
      out.push({
        url, nome: e.name, inicio: e.startDate, fim: e.endDate, local: a.name, complemento: a.addressAlt,
        endereco: [a.address, a.addressNum].filter(Boolean).join(", "), bairro: a.neighborhood, cidade: a.city, uf: a.state,
        categoria: e.eventsCategory, tipo: e.eventType, online: e.onlineInfo, cancelado: e.cancelled, imagem: e.logoUrl,
        descricao: (e.strippedDetail || "").replace(/\s+/g, " ").slice(0, 1200),
      });
    } catch { out.push({ url, erro: "sem dados estruturados", txt }); }
  }
  await writeFile("coleta/sympla.json", JSON.stringify({ eventos: out, bileto: [...bileto].map(([url, txt]) => ({ url, txt })) }, null, 1));
}

// ---------- 2. Páginas de agendas, bilheterias e equipamentos (texto + links + JSON-LD) ----------
const PAGINAS = [
  // agenda oficial
  ["pms-agenda", "https://www.salvadordabahia.com/agenda/", /salvadordabahia\.com\/eventos\//],
  ["pms-shows", "https://www.salvadordabahia.com/categoria-agenda/shows-e-festas/", /salvadordabahia\.com\/eventos\//],
  ["pms-exposicoes", "https://www.salvadordabahia.com/categoria-agenda/exposicoes/", /salvadordabahia\.com\/eventos\//],
  ["pms-teatro", "https://www.salvadordabahia.com/categoria-agenda/teatro/", /salvadordabahia\.com\/eventos\//],
  ["pms-gratuitos", "https://www.salvadordabahia.com/categoria-agenda/gratuitos/", /salvadordabahia\.com\/eventos\//],
  ["pms-danca", "https://www.salvadordabahia.com/categoria-agenda/danca/", /salvadordabahia\.com\/eventos\//],
  // bilheterias
  ["bilheteriadigital", "https://www.bilheteriadigital.com/busca/salvador", /bilheteriadigital\.com\/(?!busca)[^/]+/],
  ["ticketmaker", "https://vendas.ticketmaker.com.br/Eventos", /ticketmaker\.com\.br\/.+/],
  ["boratickets", "https://vendas.boratickets.com.br/", /boratickets\.com\.br\/.+/],
  ["pida", "https://www.pida.com.br/eventos", /pida\.com\.br\/evento/],
  ["nokta", "https://www.noktatickets.com.br/eventos/em/salvador", /noktatickets\.com\.br\/(evento|e\/)/],
  ["eventim", "https://www.eventim.com.br/city/salvador-1143/", /eventim\.com\.br\/(event|artist)\//],
  ["ingresse", "https://www.ingresse.com/", null],
  ["casarosa-bileto", "https://site.bileto.sympla.com.br/casarosa/", null],
  // agendas independentes
  ["agendasalvador-musica", "https://agendasalvador.com.br/salvador/musica", /agendasalvador\.com\.br\/evento/],
  ["agendasalvador-teatro", "https://agendasalvador.com.br/salvador/teatro", /agendasalvador\.com\.br\/evento/],
  ["agendasalvador-exposicoes", "https://agendasalvador.com.br/salvador/exposicoes", /agendasalvador\.com\.br\/evento/],
  ["agendasalvador-centro", "https://agendasalvador.com.br/salvador/centro", /agendasalvador\.com\.br\/evento/],
  ["agendasalvador-rv", "https://agendasalvador.com.br/salvador/rio-vermelho", /agendasalvador\.com\.br\/evento/],
  ["rapana", "https://rapana.com.br/salvador/eventos", /rapana\.com\.br\/.+\/evento/],
  ["agendartecultura", "https://www.agendartecultura.com.br/", /agendartecultura\.com\.br\/.+/],
  ["agendaculturalsalvador", "https://www.agendaculturalsalvador.com.br/categoria/teatro-salvador", /agendaculturalsalvador\.com\.br\/(?!categoria).+/],
  ["elcabong", "https://elcabong.com.br/", null],
  ["soteroteatro", "https://soteroteatro.com.br/", /soteroteatro\.com\.br\/.+/],
  ["simbora", "https://simbora.net/", null],
  ["batekoo", "https://batekoo.com/eventos/", null],
  ["guiagay", "https://www.guiagaysalvador.com.br/roteiro/", null],
  ["bocadebrasa", "https://www.movimentobocadebrasa.com.br/", null],
  // governo
  ["secult-eventos", "https://www.ba.gov.br/cultura/eventos", /ba\.gov\.br\/cultura\/eventos\/.+/],
  ["funceb-agenda", "https://www.ba.gov.br/fundacaocultural/5524/agenda-cultural-bahia", null],
  ["ipac-noticias", "https://www.ba.gov.br/ipac/noticias", /ba\.gov\.br\/ipac\/noticias\/2026-1[12]\//],
  ["ipac-museus", "https://www.ba.gov.br/ipac/museus-0", null],
  ["tca", "https://www.ba.gov.br/tca/eventos", /ba\.gov\.br\/tca\/eventos?\/.+/],
  ["cms-agenda", "https://www.cms.ba.gov.br/CMS/public/agenda", null],
  // equipamentos
  ["caixa", "https://www.caixacultural.gov.br/Paginas/Salvador.aspx", /caixacultural\.gov\.br\/.+/],
  ["ccbb", "https://ccbb.com.br/salvador/programacao/", /ccbb\.com\.br\/salvador\/.+/],
  ["vilavelha", "https://teatrovilavelha.com.br/tempo/", /teatrovilavelha\.com\.br\/.+/],
  ["gamboa", "https://teatrogamboa.com.br/agenda/", /teatrogamboa\.com\.br\/.+/],
  ["modulo", "https://teatromodulo.com.br/programacao", /teatromodulo\.com\.br\/.+/],
  ["sesc", "https://www.sescbahia.com.br/programacao", /sescbahia\.com\.br\/.+/],
  ["martim", "https://teatro.ufba.br/agenda/", /teatro\.ufba\.br\/.+/],
  ["casarosa", "https://casarosasalvador.com.br/programacao/mes/", /casarosasalvador\.com\.br\/.+/],
  ["jorgeamado-fund", "https://jorgeamado.org.br/", null],
  ["nautico", "https://www.museunauticodabahia.org.br/eventos/", null],
  ["muncab", "https://muncab.com.br/", null],
  ["goethe", "https://www.goethe.de/ins/br/pt/sta/sal/ver.cfm", null],
  ["saladearte", "https://www.saladearte.art.br/", null],
  ["teatrojorgeamado", "https://www.teatrojorgeamado.com.br/", null],
  ["pierreverger", "https://www.pierreverger.org/", null],
  ["mafro", "https://mafro.ceao.ufba.br/", null],
  ["galatea", "https://galatea.art/", null],
  ["alianca", "https://www.afsalvador.org.br/", null],
  ["icba", "https://www.icba.com.br/", null],
  ["museucostapinto", "https://www.museucostapinto.com.br/", null],
];

async function paginas() {
  const resumo = [];
  for (const [id, url, seguir] of PAGINAS) {
    const r = await baixar(url);
    if (!r) { resumo.push({ id, url, ok: false }); continue; }
    const ls = links(r.html, r.final);
    const filhos = [];
    if (seguir) {
      const alvo = [...new Set(ls.map((l) => l.href).filter((h) => seguir.test(h) && h !== url))].slice(0, 60);
      for (const u of alvo) {
        const f = await baixar(u);
        if (f) filhos.push({ url: u, texto: semTags(f.html).slice(0, 8000), jsonld: jsonld(f.html) });
      }
    }
    await writeFile(`coleta/paginas/${id}.json`, JSON.stringify({ id, url, final: r.final, texto: semTags(r.html).slice(0, 60000), jsonld: jsonld(r.html), links: ls.slice(0, 600), filhos }, null, 1));
    resumo.push({ id, url, ok: true, filhos: filhos.length });
  }
  return resumo;
}

await mkdir("coleta/paginas", { recursive: true });
await sympla();
const resumo = await paginas();
await writeFile("coleta/resumo.json", JSON.stringify({ em: new Date().toISOString(), resumo, requisicoes: log }, null, 1));
console.log(`Coleta concluída: ${log.length} requisições.`);
