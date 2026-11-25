"""Gera data/eventos.json com a primeira varredura verificada (25/11/2026).

Cada linha abaixo foi conferida na página individual do evento (Sympla, Bileto,
Shotgun) ou no calendário oficial da Prefeitura (salvadordabahia.com).
Uso: python3 scripts/dados_iniciais.py
"""
import json, re, unicodedata, pathlib

VERIF = "2026-11-25T07:30:00-03:00"
MUS, TEA, EXP, FES, INF, FOR = (
    "Música e cultura popular", "Teatro, dança e humor", "Exposições e museus",
    "Festas populares e festivais", "Crianças e famílias", "Literatura e formação")

SY = ("Sympla", "https://www.sympla.com.br/eventos/salvador-ba")
BI = ("Sympla Bileto", "https://www.sympla.com.br/eventos/salvador-ba")
SH = ("Shotgun — Salvador", "https://shotgun.live/pt-br/cities/salvador")
PMS_CAL = "https://www.salvadordabahia.com/eventos/calendario-do-verao-de-salvador-2026-2027-programacao-completa/"
PMS = ("Salvador da Bahia — calendário oficial do verão", PMS_CAL)

def sy(slug): return f"https://www.sympla.com.br/evento/{slug}"
def bi(n): return f"https://bileto.sympla.com.br/event/{n}"
def sh(slug): return f"https://shotgun.live/pt-br/events/{slug}"
def pms(slug): return f"https://www.salvadordabahia.com/eventos/{slug}/"

# (titulo, categoria, data, data_fim, horario, local, bairro, descricao, preco, gratuito, noite, url, fonte)
E = [
 # ---- Exposições (agenda oficial da Prefeitura, página individual) ----
 ("Padê Onã — Encontrar Caminhos", EXP, "2026-04-30", "2027-01-13", "Terça a domingo", "MUNCAB — Museu Nacional da Cultura Afro-Brasileira (Rua das Vassouras, 25)", "Centro Histórico",
  "Exposição do artista visual Sandro Aiyê, com curadoria de Jamile Coelho e Jil Soares.", "Consulte a fonte", False, False, pms("exposicao-pade-ona-encontrar-caminhos"), ("Salvador da Bahia — agenda oficial", pms("exposicao-pade-ona-encontrar-caminhos"))),
 ("Nem todo viandante anda estradas — Da humanidade como prática", EXP, "2026-09-05", "2026-11-29", "Terça a domingo, 10h às 17h", "MUNCAB (Rua das Vassouras, 25)", "Centro Histórico",
  "Itinerância da 36ª Bienal de São Paulo, com obras sobre território e experiências da diáspora africana.", "Ingresso pago; gratuita às quartas e domingos", False, False, pms("exposicao-nem-todo-viandante-anda-estradas-da-humanidade-como-pratica"), ("Salvador da Bahia — agenda oficial", pms("exposicao-nem-todo-viandante-anda-estradas-da-humanidade-como-pratica"))),
 ("3 Obás de Xangô", EXP, "2026-08-06", "2026-12-06", "Terça a domingo e feriados, 9h às 18h", "CAIXA Cultural Salvador — Unidade Pelourinho (Rua do Saldanha, 14)", "Pelourinho",
  "Mostra inspirada no documentário homônimo de Sérgio Machado.", "Gratuita", True, False, pms("exposicao-3-obas-de-xango"), ("Salvador da Bahia — agenda oficial", pms("exposicao-3-obas-de-xango"))),
 ("Atlântico Sertão", EXP, "2026-09-29", "2027-01-29", "Terça a domingo, 10h às 18h", "Museu de Arte da Bahia (MAB)", "Corredor da Vitória",
  "Obras de mais de 80 artistas, em sua maioria do Norte e Nordeste; realização do CCBB.", "Gratuita", True, False, pms("exposicao-atlantico-sertao"), ("Salvador da Bahia — agenda oficial", pms("exposicao-atlantico-sertao"))),
 ("Narrativas da Beleza — Acervo da Laje", EXP, "2026-11-05", "2027-01-17", "Terça a domingo, 9h às 18h", "CAIXA Cultural Salvador — Unidade Carlos Gomes", "Centro",
  "Exposição do Acervo da Laje, museu-casa-escola do Subúrbio Ferroviário.", "Gratuita", True, False, pms("exposicao-narrativas-da-beleza"), ("Salvador da Bahia — agenda oficial", pms("exposicao-narrativas-da-beleza"))),
 ("O Reinado do Riso", EXP, "2026-11-04", "2027-01-17", "Terça a domingo, 9h às 18h", "CAIXA Cultural Salvador — Unidade Carlos Gomes", "Centro",
  "Fantasias, mamulengos, fantoches e outras obras sobre o humor na cultura popular brasileira.", "Gratuita", True, False, pms("exposicao-o-reinado-do-riso"), ("Salvador da Bahia — agenda oficial", pms("exposicao-o-reinado-do-riso"))),

 # ---- Sympla (páginas individuais) ----
 ("Quarta-Jazz — Matilde Charles", MUS, "2026-11-25", None, "17h30", "Casa da Mãe", "Rio Vermelho", "Show da cantora baiana Matilde Charles.", "Consulte a fonte", False, False, sy("quarta-jazz-matilde-charles/3644441"), SY),
 ("Brega a Dois", MUS, "2026-11-28", None, "20h às 3h", "A Marujada (Rua dos Marchantes, 81)", "Santo Antônio Além do Carmo", "Festa com Ian Fraguas e Spadina Banks.", "R$ 25 a R$ 30 + taxa", False, True, sy("brega-a-dois-28-11/3656564"), SY),
 ("Morango canta Ludmilla e Alcione", MUS, "2026-11-29", None, "15h", "Baía Sunset", "Dois de Julho", "Show em homenagem a Ludmilla e Alcione.", "Consulte a fonte", False, False, sy("morango-canta-ludmila-e-alcione-baia-sunset/3650935"), SY),
 ("Giuliano Eriston — show Politonia", MUS, "2026-11-29", None, "18h", "Casa da Mãe", "Rio Vermelho", "Canções do segundo álbum do artista, Politonia.", "Consulte a fonte", False, False, sy("giuliano-eriston-show-politonia/3661770"), SY),
 ("Harry's Club — Forever Young Party", MUS, "2026-12-05", None, "19h às 23h30", "Casa da Felicidade Barra", "Barra", "Festa com repertório de One Direction e Harry Styles.", "Consulte a fonte", False, True, sy("harry-s-club-2a-ed-forever-young-party/3569998"), SY),
 ("Patrícia Gomes em Som dos Tribais", MUS, "2026-12-05", None, "15h às 19h", "Restaurante D'Madda", "Candeal", "Patrícia Gomes volta ao Candeal com o show Som dos Tribais.", "Consulte a fonte", False, False, sy("patricia-gomes-em-som-dos-tribais/3649524"), SY),
 ("Samba do Carangondé", MUS, "2026-12-05", None, "11h às 21h", "Casa 09", "Jardim Apipema", "Primeira edição do encontro de samba do Recôncavo.", "Consulte a fonte", False, False, sy("samba-do-carongonde/3654247"), SY),
 ("Colado — terceira edição", MUS, "2026-12-05", None, "18h às 2h", "Casa da Felicidade Arte & Música & Gastronomia", "", "Noite de música e dança.", "A partir de R$ 30", False, True, sy("colado-terceira-edicao/3642584"), SY),
 ("Guga canta Gil", MUS, "2026-12-05", None, "18h às 22h", "Hotel Villa da Praia", "Itapuã", "O ator e cantor Guga interpreta canções de Gilberto Gil à beira-mar.", "Consulte a fonte", False, False, sy("guga-canta-gil-vila-da-praia-hotel/3654583"), SY),
 ("1798 — Lucas Dantas: Um Herói de Búzios", TEA, "2026-12-05", None, "20h", "Casa Preta Espaço de Cultura", "Dois de Julho", "Solo teatral sobre Lucas Dantas, líder da Revolta dos Búzios.", "Consulte a fonte", False, False, sy("1798-lucas-dantas-um-heroi-de-buzios-05-12/3663589"), SY),
 ("1º Aniversário do Samba Mussurunga", MUS, "2026-12-06", None, "13h às 22h", "Quadra de Mussurunga", "Mussurunga", "Tarde de samba e pagode.", "Consulte a fonte", False, False, sy("1-aniversario-samba-mussurunga/3614299"), SY),
 ("SUBH com Mano Parras e convidados", MUS, "2026-12-12", None, "20h às 3h", "A Marujada (Rua dos Marchantes, 81)", "Santo Antônio Além do Carmo", "Noite com Mano Parras e convidados.", "R$ 15 a R$ 25 + taxa", False, True, sy("subh-com-mano-parras-e-convidados/3652582"), SY),
 ("Astoria — Pink Floyd Cover", MUS, "2026-12-12", None, "21h", "Teatro SESI Rio Vermelho", "Rio Vermelho", "Tributo à obra do Pink Floyd.", "Consulte a fonte", False, False, sy("astoria-pink-floyd-cover-a-essencia-do-pink-floyd-ao-vivo/3644665"), SY),
 ("Salceruh", MUS, "2026-12-19", None, "19h às 0h30", "Largo Tereza Batista", "Pelourinho", "Festa ao ar livre no Centro Histórico.", "Consulte a fonte", False, True, sy("salceruh/3659735"), SY),
 ("Réveillon da Baía 2027", FES, "2026-12-31", None, "22h às 6h", "Área da Igreja de Santo Antônio da Barra", "Barra", "26ª edição da festa de virada do ano.", "Consulte a fonte", False, True, sy("reveillon-da-baia-2027/3521775"), SY),
 ("Réveillon Alerta Praia 2027", FES, "2026-12-31", None, "21h às 4h", "Alerta Praia Bar", "Itapuã", "Festa de virada com camarote e open bar.", "Consulte a fonte", False, True, sy("reveillon-alerta-praia-2027/3599370"), SY),
 ("Réveillon Villa Bahiana 2027", FES, "2026-12-31", None, "21h às 4h", "Villa Bahiana", "Itapuã", "Festa de virada do ano.", "Consulte a fonte", False, True, sy("reveillon-villa-bahiana-2027/3595207"), SY),
 ("Rodrigo Barba — 25 anos do Bloco do Eu Sozinho", MUS, "2027-01-16", None, "19h", "Largo Quincas Berro D'Água", "Pelourinho", "O baterista do Los Hermanos celebra os 25 anos do disco.", "Consulte a fonte", False, False, sy("baterista-da-los-hermanos-em-salvador-ba-rodrigo-barba-apresenta-25-anos-do-bloco-do-eu-sozinho/3663429"), SY),

 # ---- Sympla Bileto (páginas individuais; preço = menor valor publicado) ----
 ("Ensaio aberto — Tarsila, a Brasileira", TEA, "2026-11-25", None, "19h", "Teatro Castro Alves", "Campo Grande", "Ensaio aberto do musical Tarsila, a Brasileira.", "Gratuito (retirada de ingresso)", True, False, bi(130685), BI),
 ("Pedro Iaco apresenta Sangria", MUS, "2026-11-26", None, "19h", "Teatro Gamboa", "Gamboa de Cima", "Show do cantor, violonista e compositor Pedro Iaco.", "A partir de R$ 15", False, False, bi(128802), BI),
 ("Carol Delgado — Energia Feminina", TEA, "2026-11-26", None, "20h", "Teatro Faresi", "Ondina", "Show de stand-up comedy.", "A partir de R$ 50", False, False, bi(128195), BI),
 ("Celo Dut apresenta: Rei das Ruas", MUS, "2026-11-27", None, "22h", "Casa Rosa — Pátio Viração", "Rio Vermelho", "Show de Celo Dut no Pátio Viração.", "A partir de R$ 20", False, True, bi(129428), BI),
 ("Como Sobreviver à Própria Família?", TEA, "2026-11-27", None, "21h", "Teatro Jorge Amado", "Pituba", "Espetáculo de humor.", "A partir de R$ 60", False, False, bi(123270), BI),
 ("maresia ~ a ondulação constante da maré", MUS, "2026-11-27", "2026-11-28", "Duas noites; horários na bilheteria", "Teatro Gamboa", "Gamboa de Cima", "Paulo Pitta apresenta ao vivo o trabalho Maresia.", "A partir de R$ 25", False, False, bi(129725), BI),
 ("Roda de Samba Reggae com Marcia Castro", MUS, "2026-11-28", None, "21h", "Casa Rosa — Pátio Viração", "Rio Vermelho", "Edição Festa da Democracia.", "A partir de R$ 30", False, True, bi(129713), BI),
 ("David Coelho — Tudo Vira MPB", MUS, "2026-11-28", None, "20h", "Teatro Jorge Amado", "Pituba", "Show de David Coelho.", "A partir de R$ 50", False, False, bi(123722), BI),
 ("QR Corpo — Anti Status Quo Companhia de Dança", TEA, "2026-11-28", "2026-11-29", "Horários na bilheteria", "Teatro Vila Velha", "Campo Grande", "Dança contemporânea da companhia de Brasília (DF).", "Gratuito (retirada de ingresso)", True, False, bi(129849), BI),
 ("Lazzo Matumbi no 24º Festival Educadora FM", MUS, "2026-11-29", None, "18h30", "Concha Acústica do TCA", "Campo Grande", "Show de Lazzo Matumbi no festival da Rádio Educadora.", "A partir de R$ 25", False, False, bi(126563), BI),
 ("Musical Arrocha — Aceita esse musical que dói menos", TEA, "2026-12-03", "2026-12-12", "Temporada; sessões na bilheteria", "Teatro Gregório de Mattos (Praça Castro Alves)", "Centro", "Temporada curta que celebra a reabertura do teatro.", "A partir de R$ 40", False, False, bi(129783), BI),
 ("Matita Perê apresenta Andarilho", MUS, "2026-12-05", None, "17h", "Teatro Gamboa", "Gamboa de Cima", "Show do grupo baiano Matita Perê.", "A partir de R$ 25", False, False, bi(130178), BI),
 ("Brava Gente — o Brasil não é lugar, é gente", MUS, "2026-12-05", None, "19h", "Concha Acústica do TCA", "Campo Grande", "Espetáculo de celebração da cultura brasileira.", "A partir de R$ 50", False, False, bi(129983), BI),
 ("Rapunzel — Ballet Helena Palma", INF, "2026-12-05", "2026-12-06", "Sessões nos dois dias; horários na bilheteria", "Teatro Sesc Casa do Comércio", "Caminho das Árvores", "Espetáculo de dança inspirado na história de Rapunzel.", "A partir de R$ 50", False, False, bi(129436), BI),
 ("Maria Rita — Redescobrir Vol. 2", MUS, "2026-12-11", None, "19h", "Concha Acústica do TCA", "Campo Grande", "Turnê em que Maria Rita revisita canções de sua formação.", "R$ 140 a R$ 240", False, False, bi(126867), BI),
 ("Aniversário da Sambaiana — 7 anos", MUS, "2026-12-12", None, "22h", "Casa Rosa — Pátio Viração", "Rio Vermelho", "A Sambaiana comemora sete anos no Rio Vermelho.", "A partir de R$ 30", False, True, bi(130339), BI),
 ("Natal das Estrelas — Ivete Sangalo, Zeca Baleiro e OSBA", MUS, "2026-12-19", "2026-12-20", "Duas noites; horários na bilheteria", "Teatro Castro Alves", "Campo Grande", "Concertos com a Orquestra Sinfônica da Bahia.", "A partir de R$ 60", False, False, bi(130445), BI),
 ("Rodrigo Marques — stand-up", TEA, "2026-12-20", None, "17h", "Teatro Faresi", "Ondina", "Show de stand-up comedy.", "A partir de R$ 25", False, False, bi(127100), BI),
 ("O Sítio do Picapau Amarelo", INF, "2027-01-09", "2027-01-10", "Sessões nos dois dias; horários na bilheteria", "Teatro Faresi", "Ondina", "Espetáculo infantil.", "A partir de R$ 50", False, False, bi(129378), BI),
 ("João Bosco 80 Anos", MUS, "2027-01-15", None, "20h", "Teatro Castro Alves", "Campo Grande", "Show comemorativo dos 80 anos do cantor e violonista.", "A partir de R$ 110", False, False, bi(128755), BI),
 ("Chame Gente — Um Carnaval em Cada Esquina", TEA, "2027-01-15", "2027-01-23", "Temporada; sessões na bilheteria", "Teatro Jorge Amado", "Pituba", "Espetáculo sobre o Carnaval.", "A partir de R$ 40", False, False, bi(128658), BI),
 ("O Céu da Língua — Gregorio Duvivier", TEA, "2027-01-22", "2027-01-23", "Sessões nos dois dias; horários na bilheteria", "Concha Acústica do TCA", "Campo Grande", "Espetáculo dirigido por Luciana Paes.", "A partir de R$ 50", False, False, bi(130559), BI),
 ("Festival de Verão Salvador 2027", FES, "2027-01-23", "2027-01-24", "Dois dias; horários na bilheteria", "WET Eventos (Av. Luís Viana Filho)", "Paralela", "26ª edição do festival.", "A partir de R$ 90", False, False, bi(128831), BI),
 ("Chico Chico — Let It Burn", MUS, "2027-01-24", None, "19h", "Teatro Castro Alves", "Campo Grande", "Turnê Let It Burn – Deixa Arder.", "A partir de R$ 100", False, False, bi(129188), BI),

 # ---- Shotgun (páginas individuais; preço = menor valor publicado) ----
 ("Nightmare Day", MUS, "2026-11-27", None, "18h", "Av. Sete de Setembro, 3713", "Barra", "Festa de R&B, afrobeat e baile funk.", "A partir de R$ 15", False, True, sh("nightmareday2026"), SH),
 ("Âmbar Session 01", MUS, "2026-11-28", None, "22h30", "Casa da Nigéria", "Pelourinho", "Festa de R&B, afrobeat e dancehall.", "A partir de R$ 30", False, True, sh("ambar-session"), SH),
 ("O Natal Mora Aqui — Drag Show", TEA, "2026-12-05", None, "18h", "Saladearte CineMAM (Solar do Unhão)", "", "Show de drag com repertório natalino e pop.", "A partir de R$ 25", False, True, sh("o-natal-mora-aqui-drag-show"), SH),
 ("Virou", MUS, "2026-12-05", None, "22h", "Doca 1 (Av. da França)", "Comércio", "Festa de hip hop, house e dancehall.", "A partir de R$ 55", False, True, sh("vi-rou"), SH),
 ("Espaço Dona Neuza: O Lugar da Música", MUS, "2026-12-05", None, "17h", "Espaço Cultural Dona Neuza", "", "Encontro musical com dub e MPB.", "A partir de R$ 20", False, False, sh("espaco-dona-neuza-o-lugar-da-musica-05-12-2026"), SH),
 ("Bereguede & Afins: Felipe Cordeiro + Feito no Brasil", MUS, "2026-12-12", None, "18h", "Gabinete Português de Leitura", "Dois de Julho", "Show de Felipe Cordeiro com Feito no Brasil.", "Consulte a fonte", False, False, sh("bereguede-afins-apresenta-felipe-cordeiro-feito-no-brasil"), SH),
 ("Matriz Cyber Edition", MUS, "2026-12-18", None, "22h", "Teatro Solar Boa Vista", "Brotas", "Festa de pop e eletrônica.", "A partir de R$ 40", False, True, sh("matriz-cyber-edition"), SH),
 ("Iorigun + Cajupitanga + Colibri", MUS, "2026-12-18", None, "19h", "Casa 141", "", "Shows de rock e indie.", "A partir de R$ 25", False, True, sh("iorigun-cajupitanga-colibri"), SH),
 ("NHL apresenta: Tangolo Mangos + Noite Suite", MUS, "2026-12-19", None, "21h", "Café Teatro Nilda Spencer", "", "Shows de indie rock.", "A partir de R$ 40", False, True, sh("nhl-apresenta-tangolo-mangos-noite-suite"), SH),

 # ---- Calendário oficial do verão (Prefeitura de Salvador) ----
 ("Festa de Santa Bárbara", FES, "2026-12-01", "2026-12-04", "Programação ao longo do dia", "Centro Histórico", "Centro Histórico", "Alvorada, missa, procissão e caruru.", "Aberto ao público", True, False, pms("festa-de-santa-barbara"), PMS),
 ("Ensaio do Pagod'art", MUS, "2026-12-05", None, "A partir das 14h", "Alto do Andu", "Pituaçu", "Ensaio de verão.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Samba do Lôro", MUS, "2026-12-05", None, "17h", "Barraca do Lôro — Pedra do Sal", "", "Roda de samba.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Festival Hit Salvador 2026", FES, "2026-12-05", None, "18h", "WET Eventos (Av. Luís Viana Filho)", "Paralela", "Festival com Matuê, Duquesa e outras atrações.", "Consulte a fonte", False, True, PMS_CAL, PMS),
 ("Ensaio de verão da Timbalada", MUS, "2026-12-06", None, "16h", "Candyall Guetho Square", "Candeal", "Tradicional ensaio de verão da Timbalada.", "Consulte a fonte", False, False, pms("ensaios-de-verao-da-timbalada-2027-confira-programacao"), PMS),
 ("Jau na Concha — 40 anos de carreira", MUS, "2026-12-06", None, "17h", "Concha Acústica do TCA", "Campo Grande", "Show comemorativo de Jau.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Festa de Nossa Senhora da Conceição da Praia", FES, "2026-12-08", None, "Programação ao longo do dia", "Basílica de N. Sra. da Conceição da Praia", "Comércio", "Festa religiosa e popular.", "Aberto ao público", True, False, PMS_CAL, PMS),
 ("Festa Alô Saudade — É o Tchan, Cheiro de Amor e Tatau", MUS, "2026-12-08", None, "14h", "Chácara Baluarte", "Santo Antônio Além do Carmo", "Festa com sucessos do axé.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Festinha Massa", MUS, "2026-12-08", None, "16h", "Clube Espanhol", "Ondina", "Festa.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Nattan em Salvador", MUS, "2026-12-12", None, "21h", "WET Eventos (Av. Luís Viana Filho)", "Paralela", "Show de Nattan.", "Consulte a fonte", False, True, PMS_CAL, PMS),
 ("Márcia Freire apresenta Minha História", MUS, "2026-12-13", None, "15h", "Pátio da Ordem Terceira", "Pelourinho", "Show de Márcia Freire.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Sarau do Brown", MUS, "2026-12-13", None, "16h", "Candyall Guetho Square", "Candeal", "Sarau de Carlinhos Brown.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Ensaio de Narcizinho", MUS, "2026-12-13", None, "17h", "Espaço Cultural Barroquinha", "Centro", "Ensaio de verão.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Ensaio de Verão Raízes — Alex Maxx, Patrulha do Samba e Lu Costa", MUS, "2026-12-18", None, "A partir das 18h", "Praça das Artes Mestre Neguinho do Samba", "Pelourinho", "Ensaio de verão gratuito no Pelourinho.", "Gratuito", True, False, PMS_CAL, PMS),
 ("Liniker — Bye Bye Caju", MUS, "2026-12-18", None, "20h", "Arena Fonte Nova", "Nazaré", "Show da turnê Bye Bye Caju.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Pagodiggo", MUS, "2026-12-19", None, "16h", "Candyall Guetho Square", "Candeal", "Festa de pagode.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("O Maior Encontro do Samba — Zeca, Alcione e Aragão", MUS, "2026-12-19", None, "20h", "Arena Fonte Nova", "Nazaré", "Encontro de grandes nomes do samba.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("É a Bahia, Vida! — Baco Exu do Blues e O Kannalha", MUS, "2026-12-19", None, "21h", "Alto do Andu", "Pituaçu", "Show de Baco Exu do Blues e O Kannalha.", "Consulte a fonte", False, True, PMS_CAL, PMS),
 ("Ensaio de verão da Timbalada", MUS, "2026-12-20", None, "16h", "Candyall Guetho Square", "Candeal", "Tradicional ensaio de verão da Timbalada.", "Consulte a fonte", False, False, pms("ensaios-de-verao-da-timbalada-2027-confira-programacao"), PMS),
 ("Som de Jorge", MUS, "2026-12-25", None, "15h", "Chácara Baluarte", "Santo Antônio Além do Carmo", "Festa com repertório de Jorge Ben Jor.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Festival Virada Salvador 2027", FES, "2026-12-30", "2027-01-03", "Programação diária", "Arena O Canto da Cidade", "Boca do Rio", "Festival de Réveillon da Prefeitura.", "Gratuito", True, True, PMS_CAL, PMS),
 ("Festa de Bom Jesus dos Navegantes", FES, "2026-12-31", "2027-01-01", "Programação ao longo do dia", "Boa Viagem", "Cidade Baixa", "Procissão marítima e festa popular.", "Aberto ao público", True, False, PMS_CAL, PMS),
 ("Ensaio de verão da Timbalada", MUS, "2027-01-03", None, "16h", "Candyall Guetho Square", "Candeal", "Tradicional ensaio de verão da Timbalada.", "Consulte a fonte", False, False, pms("ensaios-de-verao-da-timbalada-2027-confira-programacao"), PMS),
 ("Bênção do Olodum 2027", MUS, "2027-01-05", None, "20h", "Praça das Artes Neguinho do Samba", "Pelourinho", "Ensaio de verão do Olodum.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Shakira — Las Mujeres Ya No Lloran", MUS, "2027-01-06", None, "Horário na bilheteria", "Arena Fonte Nova", "Nazaré", "Show da turnê mundial.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Baile da Santinha", MUS, "2027-01-08", None, "A partir das 19h", "WET Eventos (Av. Luís Viana Filho)", "Paralela", "Festa.", "Consulte a fonte", False, True, PMS_CAL, PMS),
 ("Churrasquinho Menos é Mais", MUS, "2027-01-09", None, "A partir das 14h", "Parque de Exposições", "Paralela", "Festa de pagode com o grupo Menos é Mais.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Pôr do Jau — Jau e Nando Reis", MUS, "2027-01-09", None, "15h", "Shopping da Bahia", "Caminho das Árvores", "Show ao pôr do sol.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Canto da Sereiona", MUS, "2027-01-09", None, "17h", "Porto Salvador", "Comércio", "Show.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Sarau du Brown", MUS, "2027-01-10", None, "16h", "Candyall Guetho Square", "Candeal", "Sarau de Carlinhos Brown.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("A Melhor Segunda — Xanddy Harmonia e Tony Salles", MUS, "2027-01-11", None, "A partir das 20h", "Centro de Convenções Salvador (Av. Octávio Mangabeira)", "", "Festa de pagode.", "Consulte a fonte", False, True, PMS_CAL, PMS),
 ("Bênção do Olodum 2027", MUS, "2027-01-12", None, "20h", "Praça das Artes Neguinho do Samba", "Pelourinho", "Ensaio de verão do Olodum.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Lavagem do Bonfim", FES, "2027-01-14", None, "Programação ao longo do dia", "Da Conceição da Praia à Basílica do Senhor do Bonfim", "Comércio / Bonfim", "Cortejo de 8 km e lavagem das escadarias do Bonfim.", "Aberto ao público", True, False, pms("lavagem-do-bonfim"), PMS),
 ("Ensaio de Verão Raízes — Alex Maxx, Patrulha do Samba e Lu Costa", MUS, "2027-01-14", None, "A partir das 18h", "Praça das Artes Mestre Neguinho do Samba", "Pelourinho", "Ensaio de verão gratuito no Pelourinho.", "Gratuito", True, False, PMS_CAL, PMS),
 ("Ensaio de verão da Timbalada", MUS, "2027-01-17", None, "16h", "Candyall Guetho Square", "Candeal", "Tradicional ensaio de verão da Timbalada.", "Consulte a fonte", False, False, pms("ensaios-de-verao-da-timbalada-2027-confira-programacao"), PMS),
 ("Bênção do Olodum 2027", MUS, "2027-01-19", None, "20h", "Praça das Artes Neguinho do Samba", "Pelourinho", "Ensaio de verão do Olodum.", "Consulte a fonte", False, False, PMS_CAL, PMS),
 ("Ensaio de Verão Raízes — Alex Maxx, Patrulha do Samba e Lu Costa", MUS, "2027-01-22", None, "A partir das 18h", "Praça das Artes Mestre Neguinho do Samba", "Pelourinho", "Ensaio de verão gratuito no Pelourinho.", "Gratuito", True, False, PMS_CAL, PMS),
 ("Xande & Jau", MUS, "2027-01-23", None, "14h", "Porto Salvador", "Comércio", "Show de Xande de Pilares e Jau.", "Consulte a fonte", False, False, PMS_CAL, PMS),
]

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]

out = []
for t, cat, d, df, hr, loc, bairro, desc, preco, grat, noite, url, (fn, fu) in E:
    out.append({
        "id": f"{d}-{slug(t)}", "titulo": t, "categoria": cat, "data": d, "data_fim": df,
        "horario": hr, "local": loc, "bairro": bairro, "cidade": "Salvador",
        "descricao": desc, "preco": preco, "gratuito": grat, "noite": noite,
        "url": url, "fonte_nome": fn, "fonte_url": fu, "verificado_em": VERIF,
    })
ids = [e["id"] for e in out]
assert len(ids) == len(set(ids)), "ids duplicados"
out.sort(key=lambda e: (e["data"], e["titulo"]))
p = pathlib.Path(__file__).resolve().parent.parent / "data" / "eventos.json"
p.write_text(json.dumps({"atualizado_em": VERIF, "cidade": "Salvador, BA", "eventos": out}, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out), "eventos")
