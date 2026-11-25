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
        if e["id"] in ids: continue
        d["eventos"].append(e); ids.add(e["id"]); urls.add(e["url"]); n += 1
    d["atualizado_em"] = VERIF
    json.dump(d, open(ARQ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(ARQ, "a").write("\n")
    print(f"{n} eventos novos; total {len(d['eventos'])}")

if __name__ == "__main__" and len(sys.argv) == 1:
    aplicar()

# ---------- Segunda parte: bilheterias e agendas oficiais (coleta + navegador, 25/11/2026) ----------
BAL = lambda u: f"https://www.balcaodeingressos.com/evento/{u}"
INGRA = lambda s: f"https://ingratickets.com.br/evento/{s}"
PMS = lambda s: f"https://www.salvadordabahia.com/eventos/{s}/"
PIDA = lambda s: f"https://www.pida.com.br/evento/{s}"
C = "Consulte a fonte"
EXTRA = [
    # Balcão de Ingressos (comissário oficial)
    ev("República do Reggae 2026", FES, "2026-11-28", None, "18h", "WET Eventos (Av. Luís Viana Filho)", "Paralela", "Festival de reggae com Alpha Blondy, Ponto de Equilíbrio, Edson Gomes, Groundation e outros.", C, False, True, "https://vendas.boratickets.com.br/evento/392/republica-do-reggae-2026", "Salvador da Bahia — agenda oficial", PMS("republica-do-reggae-2026-edson-gomes-adao-negro-e-muito-mais")),
    ev("Réveillon 7 Mares 2027", FES, "2026-12-31", None, "22h", "Jardim dos Namorados", "Pituba", "Festa de Réveillon.", C, False, True, BAL("462a97e8-a8f2-44c8-8ada-d520bf3d13f1"), "Balcão de Ingressos"),
    ev("Ensaio do Pai", MUS, "2027-01-09", None, "16h", "Candyall Guetho Square", "Candeal", "Ensaio de verão.", C, False, False, BAL("aeff864d-9fe9-48d5-b1e3-b7cf5ab9760f"), "Balcão de Ingressos"),
    ev("Ensaios do Pagodart", MUS, "2026-12-05", None, "15h", "Alto do Andu", "", "Ensaio do Pagodart.", C, False, False, BAL("d0004c3f-ff64-4f13-8ffa-468efaec1ae6"), "Balcão de Ingressos"),
    ev("Encontrin com Di Propósito", MUS, "2026-12-06", None, C, "Império do Samba", "", "Encontro de samba com o grupo Di Propósito.", C, False, False, BAL("989dd1cf-a813-44ea-8736-ce5b2609e88f"), "Balcão de Ingressos"),
    ev("Sambadurras", MUS, "2026-12-06", None, C, "Pátio Ordem Terceira (POT)", "Pelourinho", "Roda de samba.", C, False, False, BAL("3bafa000-1a6a-4a5e-9779-33f6c92fc993"), "Balcão de Ingressos"),
    ev("Pagode dos Desejos", MUS, "2026-12-12", None, "15h", "Mali", "", "Festa de pagode.", C, False, False, BAL("1cd917c1-189e-4e96-bda6-e399c689f3da"), "Balcão de Ingressos"),
    ev("É a Bahia, Vida! — Baco Exu do Blues e O Kannalha", MUS, "2026-12-19", None, "21h", "Alto do Andu", "", "Show de Baco Exu do Blues e O Kannalha.", C, False, True, BAL("98a7b99e-1514-4648-a700-acc9f16257a5"), "Balcão de Ingressos"),
    ev("Samba Saboeiro de Verão", MUS, "2026-12-20", None, C, "Arena Parque Santiago", "", "Roda de samba de verão.", C, False, False, BAL("32684b92-e15e-4b8f-9ea1-f87ca906c383"), "Balcão de Ingressos"),
    ev("Pra Encher & Derramar", MUS, "2027-01-17", None, C, "Porto Salvador", "Comércio", "Festa de verão.", C, False, False, BAL("c2890973-b409-4f19-9561-ec417f2b23cc"), "Balcão de Ingressos"),
    ev("Samba Saboeiro no Yemanjá", FES, "2027-02-02", None, C, "Pátio 071", "Rio Vermelho", "Samba no dia da Festa de Iemanjá.", C, False, False, BAL("03dcc781-df8e-4042-b0ae-35c1db48f404"), "Balcão de Ingressos"),
    ev("Réveillon Ayó", FES, "2026-12-31", None, "21h", "MAM-BA", "Solar do Unhão", "Festa de Réveillon no Museu de Arte Moderna.", C, False, True, BAL("ed0b2b96-25e5-4639-9360-ee754d07b774"), "Balcão de Ingressos"),
    ev("Guilherme Arantes — 50 Anos-Luz", MUS, "2026-11-27", None, "19h (portões às 17h)", "Concha Acústica do TCA", "Campo Grande", "Turnê comemorativa dos 50 anos de carreira.", C, False, False, PMS("guilherme-arantes-apresenta-50-anos-luz"), "Salvador da Bahia — agenda oficial", BAL("5b682c5b-8c6a-474d-a092-5c6cc23e2627")),
    # Ingra Tickets
    ev("Momento Salvador", MUS, "2026-11-28", None, "14h", "Baía Sunset Bar", "", "Festa de fim de tarde.", "A partir de R$ 30", False, False, INGRA("momento-salvador/884"), "Ingra Tickets"),
    ev("Só Toca Funk — Retrô", MUS, "2026-12-11", None, "21h", "Point do Japa Bar", "", "Noite de funk retrô.", "A partir de R$ 25", False, True, INGRA("so-toca-funk-retro/880"), "Ingra Tickets"),
    ev("Pedro Qualy no Horto", MUS, "2026-12-11", None, "21h", "Horto Lounge", "", "Show de Pedro Qualy.", "A partir de R$ 30", False, True, INGRA("pedro-qualy-no-horto/758"), "Ingra Tickets"),
    ev("Baile de Favela", MUS, "2026-12-12", None, "20h", "Space Lounge Bar", "", "Baile funk.", "A partir de R$ 60", False, True, INGRA("baile-de-favela/877"), "Ingra Tickets"),
    ev("Réveillon das Patroas", FES, "2026-12-31", None, "19h", "Boteco das Patroas", "", "Festa de Réveillon.", "A partir de R$ 100", False, True, INGRA("reveillon-das-patroas/786"), "Ingra Tickets"),
    ev("Réveillon do Sotero 2027", FES, "2026-12-31", None, "21h", "Sotero Beach Bar", "", "Festa de Réveillon.", "A partir de R$ 249,90", False, True, INGRA("reveillon-do-sotero-2027/886"), "Ingra Tickets"),
    ev("Meu Samba", MUS, "2026-11-27", None, "18h", "Sotero Beach Bar", "", "Roda de samba.", "A partir de R$ 20", False, False, INGRA("meu-samba-27-11/941"), "Ingra Tickets"),
    ev("As BB Quer Funk", MUS, "2026-11-27", None, "22h", "Space Lounge Bar", "", "Noite de funk.", "A partir de R$ 30", False, True, INGRA("as-bb-quer-funk/940"), "Ingra Tickets"),
    ev("After da Rino Demolidor", MUS, "2026-11-28", None, "21h", "Horto Lounge", "", "Festa.", "A partir de R$ 40", False, True, INGRA("after-da-rino-demolidor/859"), "Ingra Tickets"),
    ev("Segue o Baile", MUS, "2026-11-28", None, "21h", "Lounge do Japa", "", "Baile funk.", "R$ 25", False, True, INGRA("bailim-anjinhas-diabinhas/939"), "Ingra Tickets"),
    ev("Fica, Vai Ter Funk na ECO!", MUS, "2026-12-10", None, "20h", "ECO", "", "Noite de funk.", "R$ 15", False, True, INGRA("fica-vai-ter-funk-na-eco/937"), "Ingra Tickets"),
    ev("Escuna Rave", FES, "2026-12-13", None, "8h", "Píer da Ribeira", "Ribeira", "Festa a bordo de escuna.", "R$ 500", False, False, INGRA("escuna-rave/804"), "Ingra Tickets"),
    ev("Pré-Carna da Carisma", MUS, "2027-01-30", None, "21h", "Horto Lounge", "", "Festa de pré-carnaval.", "A partir de R$ 30", False, True, INGRA("pre-carna-da-carisma/928"), "Ingra Tickets"),
    # Uhuu, Guichê Web, Zig, Bilheteria Digital
    ev("CPM 22 — 30 anos", MUS, "2026-12-19", None, "21h30 (abertura 19h)", "Arena A TARDE", "", "Show da turnê de 30 anos da banda de hardcore.", "A partir de R$ 60", False, True, "https://uhuu.com/evento/ba/salvador/cpm-22-16918", "Uhuu"),
    ev("Circo Portugal", CRI, "2026-11-26", None, "20h", "Av. Paralela, ao lado da Villa Global", "Paralela", "Espetáculo circense; outras sessões na bilheteria.", "A partir de R$ 30 + taxas", False, False, "https://www.guicheweb.com.br/circo-portugal--quinta-26nov-as-20h_57033", "Guichê Web"),
    ev("Samba do Piramba", MUS, "2026-12-07", None, "16h", "Pirambeira", "", "Roda de samba.", C, False, False, "https://zig.tickets/evento/samba-do-piramba", "Zig Tickets"),
    ev("Bailaum Black Bang", MUS, "2026-12-04", None, "20h às 3h", "Largo da Tieta", "Pelourinho", "Festa no Pelourinho.", "A partir de R$ 70", False, True, "https://www.bilheteriadigital.com/bailaum-black-bang-04-de-dezembro", "Bilheteria Digital"),
    # Agenda oficial da Prefeitura (salvadordabahia.com)
    ev("Pagode do Compadre — 2ª edição", MUS, "2026-11-25", None, "18h", "Pátio Ordem Terceira (POT)", "Pelourinho", "Compadre Washington recebe Raça Negra e Léo Santana.", C, False, False, PMS("pagode-do-compadre-2a-edicao"), "Salvador da Bahia — agenda oficial"),
    ev("XV Festival Internacional de Percussão 2 de Julho", MUS, "2026-11-24", "2026-11-25", "Programação na fonte", "Teatro Sesc Pelourinho", "Pelourinho", "Oficinas, recitais e apresentações de percussão.", C, False, False, PMS("xv-festival-internacional-de-percussao-2-de-julho"), "Salvador da Bahia — agenda oficial"),
    ev("Concerto Literomusical Afro-Brasileiro — Coral Ecumênico da Bahia", MUS, "2026-11-25", None, "19h15", "Terreiro Ilê Axé Opô Afonjá", "São Gonçalo do Retiro", "Primeiro concerto literomusical afro-brasileiro do coral.", "Entrada gratuita", True, False, PMS("concerto-afro-brasileiro-do-coral-ecumenico-da-bahia"), "Salvador da Bahia — agenda oficial"),
    ev("Sankara Radio Show", MUS, "2026-11-27", None, "21h (show às 22h40)", "30 Segundos Bar", "Rio Vermelho", "Estreia do espetáculo da banda Sankara, com abertura da DJ Sister Morphine.", C, False, True, PMS("sankara-radio-show"), "Salvador da Bahia — agenda oficial"),
    ev("Pagogin", MUS, "2026-11-28", None, "17h", "Pátio Ordem Terceira (POT)", "Pelourinho", "Festa que mistura funk e pagode.", C, False, False, PMS("pagogin-so-na-paquera-guga-meyra-e-mais"), "Salvador da Bahia — agenda oficial"),
    ev("19ª Caminhada Nacional do Samba", FES, "2026-11-29", None, "13h", "Circuito Campo Grande (Osmar)", "Campo Grande", "Nove blocos tradicionais de samba com trios elétricos.", "Aberto ao público", True, False, PMS("19a-caminhada-nacional-do-samba"), "Salvador da Bahia — agenda oficial"),
    ev("Encontro com o Tempo — Augusto Leal", EXP, "2026-11-13", "2027-01-17", "Terça a domingo, 9h às 17h", "Museu Solar Ferrão", "Pelourinho", "Obras feitas a partir de árvores, galhos e troncos.", "Entrada gratuita", True, False, PMS("exposicao-encontro-com-o-tempo"), "Salvador da Bahia — agenda oficial"),
    # Espaços (sites oficiais)
    ev("Planeta VerDE Perto", MUS, "2026-11-25", None, "19h", "Teatro Gamboa", "Gamboa de Cima", "Apresentação da Banda Terráquea.", C, False, False, "https://teatrogamboa.com.br/evento/planeta-verde-perto/2026-11-25/", "Teatro Gamboa"),
    ev("Festa de Iansã na Casa Rosa", FES, "2026-12-04", None, "17h", "Casa Rosa — Pátio Viração", "Rio Vermelho", "Festa em homenagem a Iansã.", "R$ 100 a R$ 200", False, False, "https://casarosasalvador.com.br/evento/festa-de-iansa-na-casa-rosa-2/", "Casa Rosa"),
    ev("Paulinho Boca & convidados — 80 anos", MUS, "2026-12-11", None, "21h", "Casa Rosa — Pátio Viração", "Rio Vermelho", "Show em comemoração aos 80 anos de Paulinho Boca de Cantor.", C, False, True, "https://casarosasalvador.com.br/programacao/lista/", "Casa Rosa"),
    ev("Quinta da Casa — Sete Dias, de Monique Nascimento", TEA, "2026-12-17", None, "20h", "Teatro Cambará (Casa Rosa)", "Rio Vermelho", "Espetáculo da programação Quinta da Casa.", C, False, False, "https://casarosasalvador.com.br/programacao/lista/", "Casa Rosa"),
    ev("Nação Ilê", EXP, "2026-11-21", "2027-03-29", "Consulte os horários na fonte", "CCBB Salvador", "", "Exposição sobre o Ilê Aiyê.", C, False, False, "https://ccbb.com.br/salvador/programacao/nacao-ile/", "CCBB Salvador"),
    ev("CONFUZO (está escurecendo dentro de mim)", TEA, "2026-12-04", "2026-12-21", "Sessões na fonte", "CCBB Salvador", "", "Espetáculo de artes cênicas.", C, False, False, "https://ccbb.com.br/salvador/programacao/confuzo-esta-escurecendo-dentro-de-mim/", "CCBB Salvador"),
    # Pida (agenda de shows de Salvador)
    ev("Alexandre Pires — Pagonejo Bão", MUS, "2026-12-05", None, "20h", "Arena A TARDE", "", "Show de Alexandre Pires.", C, False, False, PIDA("alexandre-pires-pagonejo-bao"), "Pida (agenda)"),
    ev("Silvanno das Antigas", MUS, "2026-12-12", None, "18h", "Ária Hall", "", "Show de Silvanno Salles.", C, False, False, PIDA("silvanno-das-antigas"), "Pida (agenda)"),
    ev("DVD Intensidade no Resenha do Boca", MUS, "2026-12-13", None, "15h", "WET Eventos", "Paralela", "Gravação de DVD.", C, False, False, PIDA("dvd-intensidade-no-resenha-do-boca"), "Pida (agenda)"),
]

# eventos já publicados que ganharam link individual de compra (a fonte de confirmação continua a mesma)
LINKS = {
    "Nattan em Salvador": BAL("17149080-3f43-42e3-a960-0677e6d071fd"),
    "Baile da Santinha": BAL("61c9b5d4-2ed8-4fb2-8de1-16eee94bd370"),
    "Churrasquinho Menos é Mais": BAL("d57209a5-0729-4f7c-a8f4-84512de11220"),
    "Som de Jorge": "https://www.bilheteriadigital.com/som-de-jorge-25-de-dezembro",
}
PRECOS = {"Som de Jorge": "A partir de R$ 70"}

def sympla():
    out = []
    for s in json.load(open("scripts/lote2_sympla.json", encoding="utf-8")):
        e = ev(s["titulo"], s["categoria"], s["data"], s["data_fim"], s["horario"], s["local"], s["bairro"], s["descricao"],
               s["preco"], s["gratuito"], s["noite"], s["url"], "Sympla", "https://www.sympla.com.br/eventos/salvador-ba")
        if s.get("imagem"): e["imagem"] = s["imagem"]
        out.append(e)
    return out

def aplicar2():
    d = json.load(open(ARQ, encoding="utf-8"))
    for e in d["eventos"]:
        if e["titulo"] in LINKS and "salvadordabahia.com/eventos/calendario" in e["url"]:
            e["url"] = LINKS[e["titulo"]]
            if e["titulo"] in PRECOS: e["preco"] = PRECOS[e["titulo"]]
    json.dump(d, open(ARQ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(ARQ, "a").write("\n")
    aplicar(EXTRA + sympla())

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "2":
    aplicar2()
