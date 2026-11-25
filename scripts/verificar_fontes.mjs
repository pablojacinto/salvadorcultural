// Checagem semanal do catálogo de fontes (roda no GitHub Actions, Node 20+, sem dependências).
// Para cada fonte de data/fontes.json, faz uma requisição pública e registra o resultado em
// "consulta_automatica". Não faz login, não contorna bloqueios e não altera eventos.
import { readFile, writeFile } from "node:fs/promises";

const ARQ = new URL("../data/fontes.json", import.meta.url);
const dados = JSON.parse(await readFile(ARQ, "utf8"));
const agora = new Date().toISOString();

async function testar(url) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 20000);
  try {
    const r = await fetch(url, {
      redirect: "follow", signal: ctrl.signal,
      headers: { "user-agent": "salvadorcultural-verificador/1.0 (+https://pablojacinto.github.io/salvadorcultural/)" },
    });
    if (r.ok) return "respondeu";
    if (r.status === 401 || r.status === 403 || r.status === 429) return `bloqueou acesso automático (HTTP ${r.status})`;
    return `erro HTTP ${r.status}`;
  } catch (e) {
    return e.name === "AbortError" ? "sem resposta em 20s" : "falha de conexão";
  } finally {
    clearTimeout(t);
  }
}

let ok = 0;
for (const f of dados.fontes) {
  // Redes sociais exigem login para listar publicações: só registramos a limitação.
  const resultado = f.tipo === "rede social" ? "não verificada automaticamente (exige login)" : await testar(f.source_url);
  if (resultado === "respondeu") ok++;
  f.consulta_automatica = { em: agora, resultado };
}
dados.ultima_checagem_automatica = agora;
await writeFile(ARQ, JSON.stringify(dados, null, 1) + "\n", "utf8");
console.log(`${ok} de ${dados.fontes.length} fontes responderam.`);
