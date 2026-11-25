"""Segunda varredura (25/11/2026): correções e eventos novos conferidos na página oficial.
Uso: python3 scripts/lote2.py  (altera data/eventos.json no lugar; não apaga nada além do indicado)."""
import json, re, unicodedata, sys

ARQ = "data/eventos.json"
VERIF = "2026-11-25T08:40:00-03:00"

def slug(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:70]

def ev(titulo, cat, data, data_fim, horario, local, bairro, desc, preco, gratuito, noite, url, fonte_nome, fonte_url=None):
    return {"id": f"{data}-{slug(titulo)}", "titulo": titulo, "categoria": cat, "data": data, "data_fim": data_fim,
            "horario": horario, "local": local, "bairro": bairro, "cidade": "Salvador", "descricao": desc,
            "preco": preco, "gratuito": gratuito, "noite": noite, "url": url, "fonte_nome": fonte_nome,
            "fonte_url": fonte_url or url, "verificado_em": VERIF}

MUS, TEA, EXP, FES, CRI, LIT, CIN = ("Música e cultura popular", "Teatro, dança e humor", "Exposições e museus",
    "Festas populares e festivais", "Crianças e famílias", "Literatura e formação", "Cinema e audiovisual")
ING = lambda s: f"https://www.ingresse.com/{s}/"
IPAC = "https://www.ba.gov.br/ipac/noticias/2026-11/10135/museus-do-ipac-inauguram-tres-novas-exposicoes-neste-fim-de-semana"
MUNCAB_POST = "https://www.muncab.com.br/"

NOVOS = [
    ev("As Maiores de 2026", MUS, "2026-11-27", None, "22h", "SAN Boate", "Rio Vermelho", "Festa com as músicas mais tocadas do ano.", "Consulte a fonte", False, True, ING("asmaiores2026"), "Ingresse"),
    ev("Turnê Dominguinho", MUS, "2026-11-28", None, "19h", "Arena Fonte Nova", "Nazaré", "Show da turnê Dominguinho em Salvador.", "Consulte a fonte", False, False, ING("turne-dominguinho-salvador"), "Ingresse"),
    ev("Blessed: Nina Sabbah", MUS, "2026-11-28", None, "22h", "SAN Boate", "Rio Vermelho", "Noite com a DJ Nina Sabbah.", "Consulte a fonte", False, True, ING("blessed-nina"), "Ingresse"),
    ev("ARCA", MUS, "2026-12-04", None, "22h", "SAN Boate", "Rio Vermelho", "Festa ARCA.", "Consulte a fonte", False, True, ING("arca-408548"), "Ingresse"),
    ev("Mega Bailão — Red Party", MUS, "2026-12-05", None, "22h", "Amsterdam (R. João Gomes, 249)", "Rio Vermelho", "Festa Mega Bailão, edição Red Party.", "Consulte a fonte", False, True, ING("megared"), "Ingresse"),
    ev("Fervo + Trima's Night", MUS, "2026-12-11", None, "22h", "Amsterdam", "Rio Vermelho", "Festa Fervo com a noite Trima's.", "Consulte a fonte", False, True, ING("fervo-trimas"), "Ingresse"),
    ev("Réveillon da Pirâmide 2027", FES, "2026-12-31", None, "21h", "Pirâmide Salvador", "", "Festa de Réveillon.", "Consulte a fonte", False, True, ING("reveillondapiramide2027"), "Ingresse"),
    ev("Colado — Terceira Edição", MUS, "2026-12-05", None, "18h às 2h", "Casa da Felicidade (Rua da Paciência)", "Rio Vermelho", "Festa Colado, terceira edição.", "A partir de R$ 20", False, True, "https://shotgun.live/pt-br/events/colado-terceira-edicao", "Shotgun — Salvador", "https://shotgun.live/pt-br/cities/salvador"),
    ev("Traços do Tempo — Ivana Panizzi", EXP, "2026-11-07", "2026-12-18", "Consulte os horários na fonte", "Galeria do Goethe-Institut/ICBA", "Corredor da Vitória", "Retrospectiva da artista visual, com a instalação In Vitro exibida pela primeira vez no Brasil.", "Entrada gratuita", True, False, "https://www.goethe.de/ins/br/pt/sta/sal/ver.cfm?event_id=27378918", "Goethe-Institut Salvador-Bahia", "https://www.goethe.de/ins/br/pt/sta/sal/ver.cfm"),
    ev("O mundo, de outro modo — imagens em movimento de Índia e Brasil", CIN, "2026-11-26", None, "17h30", "Goethe-Institut Salvador-Bahia", "Corredor da Vitória", "Mostra de filmes experimentais, vídeos e instalações.", "Entrada gratuita", True, False, "https://www.goethe.de/ins/br/pt/sta/sal/ver.cfm?event_id=27390496", "Goethe-Institut Salvador-Bahia", "https://www.goethe.de/ins/br/pt/sta/sal/ver.cfm"),
    ev("Construtores — #Deuinsight, por Rafael Bittencourt", EXP, "2026-11-07", "2026-12-13", "Sábados, 10h às 16h; domingos, 10h às 13h", "MAM-BA — Galpão das Oficinas", "Solar do Unhão", "Fotografias, obras e instalações em homenagem aos trabalhadores da construção.", "Consulte a fonte", False, False, IPAC, "IPAC — notícias"),
    ev("As Pedras que Falam (Saxa Loquuntur)", EXP, "2026-11-07", "2026-12-13", "Sábados, 10h às 16h; domingos, 10h às 13h", "MAM-BA — Galpão das Oficinas", "Solar do Unhão", "Projeto de Roberto Uribe-Castro sobre a memória da Oficina de Litografia do MAM.", "Consulte a fonte", False, False, IPAC, "IPAC — notícias"),
    ev("Ocupação Ferrovias", EXP, "2026-11-06", "2026-11-26", "Terça a domingo, 10h às 18h", "MAC_Bahia — Sala Multiuso", "", "Fotografias, pesquisa, projeções e instalação interativa sobre o Subúrbio Ferroviário.", "Consulte a fonte", False, False, IPAC, "IPAC — notícias"),
]

CORRECOES = {
    # MUNCAB fecha a partir de 30/11 para desmontagem e montagem de novas exposições (post oficial na home do museu)
    "2026-04-30-pade-ona-encontrar-caminhos": {"data_fim": "2026-11-29", "descricao": "Exposição do artista visual Sandro Aiyê, com curadoria de Jamile Coelho e Jil Soares. O MUNCAB fecha a partir de 30/11 para montagem de novas exposições.", "fonte_nome": "MUNCAB (site oficial)", "fonte_url": MUNCAB_POST, "verificado_em": VERIF},
    "2026-09-05-nem-todo-viandante-anda-estradas-da-humanidade-como-pratica": {"preco": "R$ 20 (inteira), R$ 10 (meia); grátis às quartas e domingos", "horario": "Terça a domingo, 10h às 17h (acesso até 16h30)", "url": "https://www.muncab.com.br/36a-bienal-de-sao-paulo-itinerancia-salvador/", "fonte_nome": "MUNCAB (site oficial)", "fonte_url": MUNCAB_POST, "verificado_em": VERIF},
}

def aplicar(extra=()):
    d = json.load(open(ARQ, encoding="utf-8"))
    ids = {e["id"] for e in d["eventos"]}
    urls = {e["url"] for e in d["eventos"]}
    for e in d["eventos"]:
        if e["id"] in CORRECOES: e.update(CORRECOES[e["id"]])
    n = 0
    for e in list(NOVOS) + list(extra):
        if e["id"] in ids or e["url"] in urls and "event_id" not in e["url"] and e["url"] != IPAC: continue
        d["eventos"].append(e); ids.add(e["id"]); urls.add(e["url"]); n += 1
    d["atualizado_em"] = VERIF
    json.dump(d, open(ARQ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(ARQ, "a").write("\n")
    print(f"{n} eventos novos; total {len(d['eventos'])}")

if __name__ == "__main__":
    aplicar()
