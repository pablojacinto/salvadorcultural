// Compara a coleta (coleta/) com a agenda publicada (data/eventos.json) e escreve
// coleta/candidatos.md: a lista de eventos novos para conferir. Nada é publicado no site.
import { readFile, readdir, writeFile } from "node:fs/promises";

const hoje = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Bahia" }).format(new Date());
const agenda = JSON.parse(await readFile("data/eventos.json", "utf8")).eventos;
const norm = (u) => String(u || "").split(/[?#]/)[0].replace(/\/+$/, "").replace(/^https?:\/\/(www\.)?/, "").toLowerCase();
const jaTem = new Set(agenda.flatMap((e) => [norm(e.url), norm(e.fonte_url)]));
const titulos = new Set(agenda.map((e) => e.titulo.toLowerCase().normalize("NFD").replace(/[^a-z0-9]/g, "")));
const linhas = [];

// Sympla: dados estruturados, filtra Salvador, presencial, futuro, não cancelado
try {
  const s = JSON.parse(await readFile("coleta/sympla.json", "utf8"));
  const ok = s.eventos.filter((e) => !e.erro && !e.cancelado && !e.online && /salvador/i.test(e.cidade || "")
    && (e.fim || e.inicio || "").slice(0, 10) >= hoje && !jaTem.has(norm(e.url))
    && !titulos.has(String(e.nome).toLowerCase().normalize("NFD").replace(/[^a-z0-9]/g, "")));
  ok.sort((a, b) => a.inicio.localeCompare(b.inicio));
  linhas.push(`## Sympla (${ok.length} candidatos)\n`);
  for (const e of ok) linhas.push(`- [ ] ${e.inicio.slice(0, 16).replace("T", " ")} · **${e.nome}** · ${e.local || "?"}${e.bairro ? ", " + e.bairro : ""} · ${e.url}`);
  const bi = s.bileto.filter((b) => !jaTem.has(norm(b.url)));
  if (bi.length) { linhas.push(`\n## Sympla Bileto (${bi.length} links sem dados estruturados)\n`); for (const b of bi) linhas.push(`- [ ] ${b.txt || "(sem título)"} · ${b.url}`); }
} catch (e) { linhas.push(`Sympla: sem dados (${e.message})`); }

// Demais fontes: páginas filhas (links de evento) que ainda não estão na agenda
const pags = await readdir("coleta/paginas").catch(() => []);
for (const f of pags.sort()) {
  const p = JSON.parse(await readFile(`coleta/paginas/${f}`, "utf8"));
  const novos = (p.filhos || []).filter((c) => !jaTem.has(norm(c.url)));
  if (!novos.length) continue;
  linhas.push(`\n## ${p.id} (${novos.length} páginas novas)\n`);
  for (const c of novos.slice(0, 40)) {
    const t = (c.texto || "").split("\n").map((x) => x.trim()).find((x) => x.length > 8) || "";
    linhas.push(`- [ ] ${t.slice(0, 90)} · ${c.url}`);
  }
}
let fora = [];
try { fora = JSON.parse(await readFile("coleta/resumo.json", "utf8")).resumo.filter((r) => !r.ok).map((r) => r.id); } catch {}

const corpo = `Coleta automática de ${hoje}. Estes são **candidatos**: só entram no site depois de conferidos na página oficial do evento (data, local, preço e link).\n\n`
  + (fora.length ? `Fontes que não responderam ao robô: ${fora.join(", ")}.\n\n` : "")
  + linhas.join("\n");
await writeFile("coleta/candidatos.md", corpo.slice(0, 64000));
console.log(corpo.slice(0, 400));
