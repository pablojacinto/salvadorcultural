# Salvador Cultural

Guia e agenda cultural independente de Salvador (BA), publicado no GitHub Pages:
**https://pablojacinto.github.io/salvadorcultural/**

## Como o site funciona

É um site estático: três páginas de código (`index.html`, `sobre.html`, `assets/`) que leem arquivos de dados em `data/`.
Não há banco de dados, servidor nem login, e a hospedagem no GitHub Pages é gratuita.

| Arquivo | O que guarda |
|---|---|
| `data/eventos.json` | Os eventos da agenda. Cada um tem data, horário, local, bairro, preço, link oficial, fonte e data da verificação. |
| `data/fontes.json` | O catálogo persistente de fontes (bilheterias, agendas, espaços, produtores e redes sociais), com status de acesso e data da última consulta. |
| `data/espacos.json` | O guia de espaços e as casas da noite. |
| `data/prompt.txt` | O texto que aparece em "Leve a ideia". |

O site esconde sozinho os eventos que já terminaram (pela data de Salvador), então a agenda não fica com coisas vencidas.

## Como atualizar a agenda

**Pelo navegador, sem programar:** abra `data/eventos.json` no GitHub, clique no lápis (Edit), copie um bloco de evento, altere os campos e clique em "Commit changes". O site atualiza em um ou dois minutos.

Regras de cada registro:
- só eventos presenciais em Salvador, com data confirmada na página do evento, da bilheteria oficial ou do espaço;
- `preco` só com valor publicado na fonte; se não houver, use "Consulte a fonte";
- `url` aponta para a página individual do evento ou de compra oficial; `fonte_nome` e `fonte_url` dizem quem confirmou;
- `verificado_em` recebe a data e a hora da conferência;
- temporadas usam `data` e `data_fim`; se a fonte listar as sessões, grave cada data separadamente.

**Com ajuda de IA:** peça a uma sessão do Claude para "fazer a varredura da agenda do salvadorcultural". O ideal é que ela consulte as fontes de `data/fontes.json`, confira cada evento na página individual, atualize `eventos.json` e `fontes.json` e entregue o resumo da varredura (fontes consultadas e inacessíveis, eventos novos, atualizados e descartados).

## Rotina automática que existe hoje

- **Checagem semanal das fontes** (`.github/workflows/verificar-fontes.yml`): toda segunda às 8h de Salvador, o GitHub testa se cada fonte responde e grava o resultado em `data/fontes.json`. Ela **não** descobre nem grava eventos.
- Pode ser rodada à mão na aba **Actions → Checar fontes da agenda → Run workflow**.
- **Coleta de candidatos** (`.github/workflows/coletar.yml`): segundas e quintas às 7h de Salvador, o GitHub lê as bilheterias, agendas e espaços do catálogo e abre uma issue "Candidatos a evento" na aba **Issues** com o que ainda não está na agenda. Nada entra no site sem conferência: abra a página oficial de cada candidato e, se estiver tudo certo, acrescente o evento em `data/eventos.json`.
- **Banners dos eventos** (`.github/workflows/imagens.yml`): sempre que `data/eventos.json` muda (e toda segunda), busca a imagem de divulgação na página oficial de cada evento novo e grava o campo `imagem`. Sem imagem, o card usa a arte padrão.
- **Conferência de datas** (`.github/workflows/conferir.yml`): todo dia às 6h de Salvador (e sempre que `data/eventos.json` muda), o GitHub abre a página oficial de cada evento em cartaz e compara data, período e cancelamento. As divergências ficam numa única issue "Conferência de datas" (etiqueta `conferencia`), que se fecha sozinha quando tudo confere. O robô não altera o site. Bileto, Balcão de Ingressos e Ingresse só mostram a data no navegador: aparecem na seção "Conferir no navegador".
- **Evento em dias separados** (ex.: sábados de uma temporada): use `"datas": ["2026-11-28", "2026-12-05"]` em vez de `data_fim`. O card mostra o próximo dia e cita os seguintes. `data_fim` é só para período contínuo (exposição, festival em dias seguidos).
- A data de "Agenda atualizada em" no topo do site vem do campo `atualizado_em` de `data/eventos.json`: atualize-o a cada revisão.

## Correções do público

O botão "Reportar correção" abre um formulário (issue) no GitHub. As sugestões aparecem na aba **Issues** do repositório.

## Hospedagem, domínio e backup

- **Custo:** GitHub Pages é gratuito para repositórios públicos.
- **Domínio próprio (opcional):** compre um domínio num registrador, crie um registro CNAME apontando para `pablojacinto.github.io` e informe o domínio em **Settings → Pages → Custom domain**. Nada disso foi feito ainda.
- **Backup:** todo o histórico fica no Git. Para guardar uma cópia, use **Code → Download ZIP**.
- **Quem edita:** só quem tiver acesso de escrita ao repositório (hoje, apenas o dono). Colaboradores podem ser convidados em **Settings → Collaborators**.
