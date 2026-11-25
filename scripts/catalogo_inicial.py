"""Gera data/fontes.json (catálogo persistente de fontes) e data/espacos.json.

Só roda uma vez para criar a base. Depois, data/fontes.json é atualizado pelo
script verificar_fontes.mjs (GitHub Action) e editado à mão quando entrar fonte nova.
"""
import json, pathlib

HOJE = "2026-11-25T07:30:00-03:00"
OK_NAVEGADOR = "acessível (consulta manual pelo navegador)"

# nome, url, tipo, observação de acesso da varredura de 25/11/2026 (None = não consultada)
F = [
 ("Salvador da Bahia — agenda oficial", "https://www.salvadordabahia.com/agenda/", "agenda", OK_NAVEGADOR),
 ("Salvador da Bahia — calendário do verão 2026/2027", "https://www.salvadordabahia.com/eventos/calendario-do-verao-de-salvador-2026-2027-programacao-completa/", "agenda", OK_NAVEGADOR),
 ("Salvador da Bahia — shows e festas", "https://www.salvadordabahia.com/categoria-agenda/shows-e-festas/", "agenda", None),
 ("Salvador da Bahia — roteiro LGBTQIA+", "https://www.salvadordabahia.com/roteiros/um-roteiro-lgbtqia-em-salvador/", "agenda", None),
 ("Shotgun — Salvador", "https://shotgun.live/pt-br/cities/salvador", "bilheteria", OK_NAVEGADOR),
 ("Shotgun — Manifesto", "https://shotgun.live/pt-br/venues/manifesto", "bilheteria", None),
 ("Ingresse", "https://ingresse.com/", "bilheteria", None),
 ("Sympla — Salvador", "https://www.sympla.com.br/eventos/salvador-ba", "bilheteria", OK_NAVEGADOR),
 ("Sympla Bileto — Casa Rosa", "https://site.bileto.sympla.com.br/casarosa/", "bilheteria", None),
 ("Eventim — Salvador", "https://www.eventim.com.br/city/salvador-1143/", "bilheteria", None),
 ("Bilheteria Digital — Salvador", "https://www.bilheteriadigital.com/busca/salvador", "bilheteria", None),
 ("Ticketmaker", "https://www.ticketmaker.com.br/", "bilheteria", None),
 ("Ticketmaker — eventos", "https://vendas.ticketmaker.com.br/Eventos", "bilheteria", None),
 ("Ticketmaster Brasil", "https://www.ticketmaster.com.br/", "bilheteria", None),
 ("Bora Tickets", "https://vendas.boratickets.com.br/", "bilheteria", None),
 ("Pida — eventos", "https://www.pida.com.br/eventos", "bilheteria", None),
 ("Nokta Tickets — Salvador", "https://www.noktatickets.com.br/eventos/em/salvador", "bilheteria", None),
 ("Agenda Salvador — Música", "https://agendasalvador.com.br/salvador/musica", "agenda", None),
 ("Agenda Salvador — Teatro", "https://agendasalvador.com.br/salvador/teatro", "agenda", None),
 ("Agenda Salvador — Rio Vermelho", "https://agendasalvador.com.br/salvador/rio-vermelho", "agenda", None),
 ("Agenda Salvador — Centro", "https://agendasalvador.com.br/salvador/centro", "agenda", None),
 ("Rapana — Salvador", "https://rapana.com.br/salvador/eventos", "agenda", None),
 ("Agenda Arte e Cultura", "https://www.agendartecultura.com.br/", "agenda", None),
 ("Agenda Cultural Salvador — Teatro", "https://www.agendaculturalsalvador.com.br/categoria/teatro-salvador", "agenda", None),
 ("El Cabong", "https://elcabong.com.br/", "agenda", None),
 ("SoteroTeatro", "https://soteroteatro.com.br/", "agenda", None),
 ("Simbora", "https://simbora.net/", "agenda", None),
 ("Guia Gay Salvador", "https://www.guiagaysalvador.com.br/roteiro/", "agenda", None),
 ("BATEKOO — eventos", "https://batekoo.com/eventos/", "produtor", None),
 ("Movimento Boca de Brasa", "https://www.movimentobocadebrasa.com.br/", "produtor", None),
 ("SecultBA — eventos", "https://www.ba.gov.br/cultura/eventos", "agenda", None),
 ("FUNCEB — Agenda Cultural Bahia", "https://www.ba.gov.br/fundacaocultural/5524/agenda-cultural-bahia", "agenda", None),
 ("Teatro Castro Alves", "https://www.ba.gov.br/tca/eventos", "espaço", None),
 ("MUNCAB", "https://muncab.com.br/", "espaço", None),
 ("CAIXA Cultural Salvador", "https://www.caixacultural.gov.br/Paginas/Salvador.aspx", "espaço", None),
 ("CCBB Salvador", "https://ccbb.com.br/salvador/programacao/", "espaço", None),
 ("Teatro Vila Velha", "https://teatrovilavelha.com.br/tempo/", "espaço", None),
 ("Teatro Gamboa", "https://teatrogamboa.com.br/agenda/", "espaço", None),
 ("Teatro Módulo", "https://teatromodulo.com.br/programacao", "espaço", None),
 ("Sesc Bahia", "https://www.sescbahia.com.br/programacao", "espaço", None),
 ("Teatro Martim Gonçalves — UFBA", "https://teatro.ufba.br/agenda/", "espaço", None),
 ("Goethe-Institut Salvador", "https://www.goethe.de/ins/br/pt/sta/sal/ver.cfm", "espaço", None),
 ("Casa Rosa — programação", "https://casarosasalvador.com.br/programacao/mes/", "espaço", None),
 ("Fundação Casa de Jorge Amado", "https://jorgeamado.org.br/", "espaço", None),
 ("Museu Náutico da Bahia", "https://www.museunauticodabahia.org.br/eventos/", "espaço", None),
 ("Câmara Municipal — Centro de Cultura", "https://www.cms.ba.gov.br/CMS/public/agenda", "espaço", None),
 ("Âncora do Marujo — Instagram", "https://www.instagram.com/ancoradomarujo/", "rede social", None),
 ("SAN Boate — Linktree", "https://linktr.ee/SANBOATE", "rede social", None),
 ("Amsterdam Pop Club — Instagram", "https://www.instagram.com/amsterdamrv/", "rede social", None),
 ("Bar da Pri — Instagram", "https://www.instagram.com/bardapri/", "rede social", None),
 ("Show Bar — Instagram", "https://www.instagram.com/showbar.salvador/", "rede social", None),
 ("Manifesto — Instagram", "https://www.instagram.com/manifesto.ssa/", "rede social", None),
 ("Sapaokê — Instagram", "https://www.instagram.com/sapaokessa/", "rede social", None),
 ("Comunidade Cutelo — Instagram", "https://www.instagram.com/cutelo.oficial/", "rede social", None),
 ("Shantay — Instagram", "https://www.instagram.com/shantay.brasil/", "rede social", None),
]

fontes = []
for nome, url, tipo, acesso in F:
    fontes.append({
        "source_name": nome, "source_url": url, "cidade": "Salvador", "tipo": tipo,
        "status_acesso": acesso or "ainda não consultada",
        "ultima_consulta": HOJE if acesso else None,
        "consulta_automatica": None,
    })

# Guia de espaços: nome, bairro, linguagem, url, descrição
G = [
 ("MUNCAB", "Centro Histórico", "Arte e memória afro-brasileira", "https://muncab.com.br/", "Museu Nacional da Cultura Afro-Brasileira, na Rua das Vassouras."),
 ("CAIXA Cultural Salvador", "Pelourinho e Carlos Gomes", "Exposições, teatro e formação", "https://www.caixacultural.gov.br/Paginas/Salvador.aspx", "Duas unidades com exposições gratuitas."),
 ("Teatro Castro Alves", "Campo Grande", "Música, dança e artes cênicas", "https://www.ba.gov.br/tca/eventos", "Principal teatro da Bahia, com a Concha Acústica."),
 ("CCBB Salvador", "Programação itinerante", "Artes visuais, música, teatro e cinema", "https://ccbb.com.br/salvador/programacao/", "Centro Cultural Banco do Brasil."),
 ("Teatro Vila Velha", "Campo Grande", "Teatro, dança e formação", "https://teatrovilavelha.com.br/tempo/", "Teatro histórico no Passeio Público."),
 ("Teatro Gamboa", "Gamboa de Cima", "Teatro, música e produção independente", "https://teatrogamboa.com.br/agenda/", "Palco da cena independente."),
 ("Teatro Módulo", "Pituba", "Teatro e música", "https://teatromodulo.com.br/programacao", ""),
 ("Sesc Bahia", "Pelourinho e Caminho das Árvores", "Teatro, música e ações formativas", "https://www.sescbahia.com.br/programacao", "Inclui o Teatro Sesc Casa do Comércio."),
 ("Teatro Martim Gonçalves", "Canela", "Artes cênicas universitárias", "https://teatro.ufba.br/agenda/", "Teatro da Escola de Teatro da UFBA."),
 ("Museu de Arte Moderna da Bahia", "Solar do Unhão", "Arte moderna e cinema", "https://www.ba.gov.br/ipac/museu-de-arte-moderna-da-bahia-mam-ba", "Inclui a sala de cinema Saladearte CineMAM."),
 ("Museu de Arte da Bahia", "Corredor da Vitória", "Acervo e exposições", "https://www.ba.gov.br/ipac/museu-de-arte-da-bahia-mab", ""),
 ("Museu Náutico da Bahia", "Barra", "História marítima", "https://www.museunauticodabahia.org.br/eventos/", "No Forte de Santo Antônio da Barra."),
 ("Goethe-Institut Salvador", "Corredor da Vitória", "Cinema, artes e encontros", "https://www.goethe.de/ins/br/pt/sta/sal/ver.cfm", ""),
 ("Casa Rosa", "Rio Vermelho", "Música, teatro e encontros", "https://casarosasalvador.com.br/programacao/mes/", "Shows no Pátio Viração."),
 ("Fundação Casa de Jorge Amado", "Pelourinho", "Literatura e memória", "https://jorgeamado.org.br/", ""),
 ("Teatro Jorge Amado", "Pituba", "Teatro, humor e música", "", ""),
 ("Teatro Faresi", "Ondina", "Humor, teatro e infantil", "", ""),
 ("Candyall Guetho Square", "Candeal", "Música e cultura popular", "", "Espaço ligado a Carlinhos Brown e à Timbalada."),
]

# Noite: nome, bairro, perfil, link de agenda
N = [
 ("Âncora do Marujo", "Dois de Julho", "Performances drag e transformistas", "https://www.instagram.com/ancoradomarujo/"),
 ("SAN Boate", "Rio Vermelho", "Boate LGBTQIA+ com festas, DJs e performances", "https://linktr.ee/SANBOATE"),
 ("Amsterdam Pop Club", "Rio Vermelho", "Pista pop e noites queer", "https://www.instagram.com/amsterdamrv/"),
 ("Casa Rosa — Pátio Viração", "Rio Vermelho", "Shows e festas", "https://casarosasalvador.com.br/programacao/mes/"),
 ("A Marujada", "Santo Antônio Além do Carmo", "Festas e música", ""),
 ("Casa da Felicidade", "Rio Vermelho e Barra", "Música ao vivo e festas", ""),
 ("Casa da Nigéria", "Pelourinho", "Festas e música da diáspora africana", ""),
 ("Bar da Pri", "Santo Antônio Além do Carmo", "Bar LGBTQIA+", "https://www.instagram.com/bardapri/"),
 ("Bar do Fua", "Pelourinho", "Bar da diversidade", "https://www.guiagaysalvador.com.br/roteiro/bares/bar-do-fua"),
 ("Show Bar", "Rio Vermelho", "Casa de shows", "https://www.instagram.com/showbar.salvador/"),
 ("Manifesto", "", "Festas e música eletrônica", "https://shotgun.live/pt-br/venues/manifesto"),
 ("Trapiche Barnabé", "Comércio", "Shows e festas", ""),
]

esp = {
 "atualizado_em": HOJE,
 "guia": [{"nome": n, "bairro": b, "linguagem": l, "url": u, "descricao": d} for n, b, l, u, d in G],
 "noite": [{"nome": n, "bairro": b, "perfil": p, "url": u} for n, b, p, u in N],
}
base = pathlib.Path(__file__).resolve().parent.parent / "data"
(base / "fontes.json").write_text(json.dumps({"atualizado_em": HOJE, "fontes": fontes}, ensure_ascii=False, indent=1), encoding="utf-8")
(base / "espacos.json").write_text(json.dumps(esp, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(fontes), "fontes;", len(G), "espaços;", len(N), "casas noturnas")
