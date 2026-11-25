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

## Correções do público

O botão "Reportar correção" abre um formulário (issue) no GitHub. As sugestões aparecem na aba **Issues** do repositório.

## Hospedagem, domínio e backup

- **Custo:** GitHub Pages é gratuito para repositórios públicos.
- **Domínio próprio (opcional):** compre um domínio num registrador, crie um registro CNAME apontando para `pablojacinto.github.io` e informe o domínio em **Settings → Pages → Custom domain**. Nada disso foi feito ainda.
- **Backup:** todo o histórico fica no Git. Para guardar uma cópia, use **Code → Download ZIP**.
- **Quem edita:** só quem tiver acesso de escrita ao repositório (hoje, apenas o dono). Colaboradores podem ser convidados em **Settings → Collaborators**.
