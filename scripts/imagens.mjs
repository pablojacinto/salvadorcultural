// Busca a imagem oficial (banner/flyer) de cada evento na própria página do evento.
// Roda no GitHub Actions (Node 20+, sem dependências) e grava o campo "imagem" em data/eventos.json.
// Usa só o que a página publica para divulgação (og:image, JSON-LD ou dados da Sympla).
// Imagens repetidas em vários eventos (logotipo do site) são descartadas: o card mantém a arte padrão.
import { readFile, writeFile } from "node:fs/promises";

const ARQ = "data/eventos.json";
const UA = "salvadorcultural-imagens/1.0 (+https://pablojacinto.github.io/salvadorcultural/)";
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
const refazer = process.argv.includes("--todas");

const html = async (url) => {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), 20000);
  try {
    const r = await fetch(url, { redirect: "follow", signal: c.signal, headers: { "user-agent": UA, "accept-language": "pt-BR,pt;q=0.9" } });
    return r.ok ? { txt: await r.text(), final: r.url } : null;
  } catch { return null; } finally { clearTimeout(t); await dormir(600); }
};

const decod = (s) => s.replace(/&amp;/g, "&").replace(/&#0?38;/g, "&").replace(/\\u002F/gi, "/").replace(/\\\//g, "/");

const achar = (h, base) => {
  const cand = [];
  const meta = (p) => { const m = h.match(new RegExp(`<meta[^>]+(?:property|name)=["']${p}["'][^>]*>`, "i")); return m && (m[0].match(/content=["']([^"']+)["']/i) || [])[1]; };
  // 1) Sympla (Next.js): imagem do evento
  const nx = h.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/);
  if (nx) { try { const e = JSON.parse(nx[1]).props.pageProps.hydrationData.eventHydration.event; if (e.logoUrl) cand.push(e.logoUrl); } catch {} }
  // 2) og:image / twitter:image
  cand.push(meta("og:image:secure_url"), meta("og:image"), meta("twitter:image"));
  // 3) JSON-LD "image"
  for (const m of h.matchAll(/<script[^>]*application\/ld\+json[^>]*>([\s\S]*?)<\/script>/gi)) {
    const i = m[1].match(/"image"\s*:\s*(?:\[\s*)?(?:\{[^}]*"url"\s*:\s*)?"([^"]+)"/);
    if (i) cand.push(i[1]);
  }
  for (const c of cand.filter(Boolean)) {
    try {
      const u = new URL(decod(c.trim()), base);
      if (!/^https:$/.test(u.protocol)) continue;
      if (/logo|favicon|sprite|placeholder|default/i.test(u.pathname)) continue;
      return u.href;
    } catch {}
  }
  return null;
};

const dados = JSON.parse(await readFile(ARQ, "utf8"));
let novas = 0;
// páginas que listam vários eventos (calendários, programação do mês) não dizem qual imagem é de qual evento
const porUrl = {};
for (const e of dados.eventos) porUrl[e.url] = (porUrl[e.url] || 0) + 1;
for (const e of dados.eventos) {
  if (porUrl[e.url] > 1) { if (refazer) delete e.imagem; continue; }
  if (e.imagem && !refazer) continue;
  const p = await html(e.url);
  const img = p && achar(p.txt, p.final);
  if (img) { e.imagem = img; novas++; }
}
// descarta imagem genérica (a mesma em 3+ eventos de páginas diferentes)
const conta = {};
for (const e of dados.eventos) if (e.imagem) conta[e.imagem] = (conta[e.imagem] || 0) + 1;
for (const e of dados.eventos) if (e.imagem && conta[e.imagem] >= 3) delete e.imagem;

await writeFile(ARQ, JSON.stringify(dados, null, 1) + "\n");
console.log(`Imagens novas: ${novas}. Eventos com imagem: ${dados.eventos.filter((e) => e.imagem).length}/${dados.eventos.length}.`);
