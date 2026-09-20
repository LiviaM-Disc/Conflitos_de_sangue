from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json

from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(r'C:\Users\lb119\Downloads\GDD.docx')
OUTPUT = ROOT / 'docs' / 'Historia_do_jogo_Conflitos_de_Sangue.docx'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}

CONTENT = [
('title', 'História do jogo Conflitos de Sangue'),
('p', 'Roteiro narrativo da versão implementada em 19 de setembro de 2026. Este documento reúne os acontecimentos do prólogo, das cinco fases e do epílogo, com as descobertas e consequências das escolhas do jogador. Contém as respostas dos enigmas e as revelações do capítulo.'),
('p', 'A narrativa abaixo descreve o protótipo atual, e não uma reprodução integral de Bad Blood, quarto livro da série Os Naturais. As falas, os horários e os códigos específicos foram desenvolvidos para o jogo. O capítulo termina com a compreensão da armadilha dos Masters; o destino definitivo de Celine e as respostas completas sobre Lorelai ainda não são revelados.'),
('h', 'Sinopse'),
('p', 'Cassie participa de uma conversa tensa com Daniel Redding e ouve um aviso sobre os métodos dos Masters. Pouco depois, o desaparecimento de Celine leva os Naturais a investigar um escritório, um depoimento contraditório e um convite cifrado. O que começa como a busca por outra pessoa se torna uma investigação sobre a própria Cassie e sobre os vínculos que podem ser usados para conduzi-la.'),
('p', 'Ao confrontar registros, emoções e padrões, a equipe descobre que as pistas não apontam apenas para um acontecimento passado: elas também orientam o próximo passo dos investigadores. Separada dos demais, Cassie chega a um salão onde uma promessa de liberdade contradiz a porta trancada. Para concluir o caso apresentado no capítulo, ela precisa reconhecer a armadilha sem confundir seu desejo de saber mais sobre Lorelai com uma prova confiável.'),
('h', 'Personagens e funções na história'),
('p', 'Cassie conduz a investigação e reconstrói os acontecimentos. Dean ajuda a testar a intenção por trás das pistas. Lia identifica sinais de mentira, enquanto Michael observa as emoções; suas leituras oferecem contexto, mas não determinam a culpa. Sloane auxilia na análise dos números e do código do convite.'),
('p', 'Celine é a pessoa desaparecida cuja ausência inicia o caso. Daniel Redding introduz a suspeita sobre os Masters, a ameaça central do capítulo. Lorelai representa a ligação pessoal explorada para atrair Cassie. O depoente da segunda fase não recebe um nome na versão atual do jogo.'),
('h', 'Prólogo'),
('sub', 'Uma conversa sob suspeita'),
('p', 'Na sala de visitas, Cassie se senta diante de Daniel Redding. A sensação é de estar sendo avaliada antes mesmo de fazer a primeira pergunta. Ela quer falar dos Masters, mas não se satisfaz com histórias vagas: procura os rastros que eles deixam.'),
('p', 'Redding desloca a conversa das pessoas para os padrões. Diz que Cassie acredita estar olhando para uma pessoa, enquanto os Masters querem que ela observe outra coisa. Cassie responde que padrões deixam rastros, mas pessoas também. Ele então chama atenção para aquilo que seus adversários escondem e para quem escolhem manter por perto.'),
('p', 'Cassie percebe a maneira como Redding trata pessoas como peças e pergunta quem decide onde cada uma fica. Ele responde com a imagem de duas escolhas aparentemente livres: alguém recebe um convite e outra pessoa recebe uma pergunta. Ambas acreditam controlar o que farão em seguida. Cassie sai desse raciocínio sem um nome concreto, mas com uma direção e uma dúvida: ouviu um aviso ou já começou a ser conduzida?'),
('sub', 'A escolha e o chamado'),
('p', 'O jogador pode pressionar Redding sobre os Masters ou encerrar a conversa. A insistência registra o Aviso de Redding, segundo o qual os Masters testam padrões, vínculos e medo. Encerrar o assunto deixa essa informação de fora do dossiê e reduz a pontuação, mas não impede o início da investigação.'),
('p', 'Na transição com a equipe, Dean anuncia que Celine desapareceu e que seu escritório ainda não foi revirado. Cassie lembra a conversa com Redding, mas reconhece que uma advertência vaga não comprova o envolvimento dos Masters. Lia distingue o que as pessoas dizem daquilo que Michael percebe em suas reações. Sloane pede atenção aos números, inclusive aos que parecem deslocados.'),
('p', 'Cassie estabelece a prioridade: primeiro Celine, depois as suspeitas da equipe. Sua decisão é registrar o que existe, não apenas procurar aquilo que espera encontrar.'),
('h', 'Fase 1 O desaparecimento de Celine'),
('p', 'Cassie explora o escritório de Celine. A ausência da desaparecida se torna concreta nos objetos que permaneceram no ambiente. Perto da saída, uma pulseira foi deixada sem sinais de luta ao redor. O registro da pista sugere uma possível mensagem, mas não transforma essa impressão em certeza sobre o que aconteceu.'),
('p', 'O celular fornece um dado verificável: foi desligado às 20h42 e não originou chamadas depois disso. Um convite sem remetente apresenta a sequência 3, 5, 8, 13, ?, 34, separada por manchas de tinta. A pulseira, o celular e o convite são os três registros essenciais para a equipe seguir adiante.'),
('p', 'Há também objetos que exigem cautela. Um livro foi movido, mas esconde apenas poeira e um marcador antigo, sem utilidade demonstrada para a solução. Já uma marca fina na janela é interpretada no registro como indício de observação externa, não de entrada forçada. O ambiente não oferece uma explicação pronta: detalhes relevantes convivem com informações que podem distrair.'),
('p', 'Ao deixar o escritório, Cassie dispõe de um horário para confrontar futuros relatos e de um código ainda sem solução. A investigação passa dos objetos para as pessoas que afirmam saber algo sobre Celine.'),
('h', 'Fase 2 Mentiras e emoções'),
('sub', 'A última ligação'),
('p', 'O depoente afirma que Celine ligou do próprio celular às 21h e parecia tranquila. Lia percebe uma hesitação antes do horário; Michael observa receio quando o assunto é o telefone. Essas reações não bastam para concluir nada, mas o registro do aparelho oferece a contradição objetiva: ele já estava desligado às 20h42.'),
('p', 'A interpretação sustentada pela pista é que a ligação descrita não corresponde ao registro do celular. Confrontado com essa diferença, o depoente admite ter inventado o contato para evitar perguntas. A mentira é descoberta, mas ainda não prova que ele provocou o desaparecimento.'),
('sub', 'A entrega do convite'),
('p', 'Em seguida, ele diz que só ouviu falar do convite depois da chegada dos investigadores. Lia nota que evita falar em recebê-lo. Michael percebe que mostrar o papel reduz sua tensão, em vez de causar surpresa. Cassie pode pedir que explique como o convite chegou, sem acusá-lo de ser responsável por todo o caso.'),
('p', 'O depoente admite ter entregue o envelope a pedido de um desconhecido. A informação liga uma pessoa ao percurso do objeto e mostra que a entrega foi dirigida, não casual. O convite passa a representar uma ação planejada, embora a identidade de quem a ordenou permaneça desconhecida.'),
('sub', 'O nome que assusta'),
('p', 'Ao ouvir o nome dos Masters, o depoente nega sentir medo e insiste que quer ir embora. Lia identifica uma incompatibilidade entre a negativa e o restante da fala. Michael reconhece medo real, mas ressalta que medo não identifica um culpado. A pergunta relevante é sobre a pressão que ele sofreu e sua relação com o envelope.'),
('p', 'Ele relata uma ameaça posterior à entrega. A equipe compreende que a mentira encobria medo, sem obter prova de autoria do desaparecimento. Nos três assuntos, o jogador precisa apresentar uma hipótese e uma prova. Se errar, perde desempenho; a revisão da equipe ainda comunica a descoberta e permite que o capítulo prossiga.'),
('h', 'Fase 3 O padrão dos Masters'),
('p', 'O convite volta ao centro da investigação. Com o apoio de Sloane, Cassie enfrenta três camadas de análise. Não basta escolher entre respostas prontas: o jogador digita os números e pode consultar uma observação parcial de Sloane quando necessário.'),
('p', 'A primeira sequência é 3, 5, 8, 13, ?, 34. O termo ausente é 21, pois cada novo número resulta da soma dos dois anteriores. Na segunda sequência, 8, 13, 21, 30, 34, 55, o intruso é 30. Retirá-lo restabelece a progressão dos demais termos.'),
('p', 'A terceira camada usa a sequência completa 3, 5, 8, 13, 21, 34. No verso do convite aparece a instrução “Quinto - terceiro + quarto + primeiro”. As palavras indicam posições, não os números cinco, três, quatro e um. A substituição resulta em 21 - 8 + 13 + 3 = 29.'),
('p', 'A chave 29 abre o envelope interno e revela uma mensagem pedindo que Cassie venha sozinha. O código deixa de ser apenas um desafio numérico: seu resultado é uma orientação dirigida à protagonista. A evidência Chave Fibonacci registra a progressão e o conteúdo do chamado.'),
('h', 'Fase 4 Dentro da mente'),
('sub', 'A reconstrução dos acontecimentos'),
('p', 'Cassie e Dean reorganizam as descobertas para compreender a intenção por trás do caso. Primeiro, o jogador relaciona o Convite cifrado à Chave Fibonacci. Esse par sustenta a existência de um código planejado; não é uma associação baseada apenas na proximidade dos objetos no escritório.'),
('p', 'Depois, a reconstrução apresentada no jogo estabelece esta ordem: Celine recebe um convite sem remetente; o celular perde sinal antes da última mensagem; a equipe percebe que também está sendo observada; a investigação conduz Cassie a uma armadilha. O momento da “última mensagem” não ganha um horário específico na versão atual, além do registro de desligamento do celular às 20h42.'),
('p', 'A ordem muda a leitura do caso. A equipe não está apenas perseguindo rastros deixados por outra pessoa: seu próprio movimento faz parte do plano. Hipóteses incoerentes precisam ser revistas antes de avançar. Quando a sequência é aceita, o jogo registra a reconstrução e anuncia que a pista era uma armadilha.'),
('p', 'A transição coloca Cassie separada dos demais, no salão dos Masters. O protótipo comunica essa separação por uma mensagem e pela mudança de cenário; não apresenta uma cena adicional de captura, confronto físico ou fuga.'),
('h', 'Fase 5 Cassie e os Masters'),
('sub', 'O salão e suas promessas'),
('p', 'Sem apoio direto da equipe, Cassie investiga o retrato, a porta e o mosaico do salão. Atrás do retrato encontra o bilhete: “Cassie, as respostas sobre Lorelai estão aqui. A saída está livre.” O nome de Lorelai torna o chamado pessoal, mas não identifica quem escreveu a mensagem.'),
('p', 'A porta contradiz a promessa: está trancada por fora. No mosaico, Cassie encontra as marcas 3, 5, 8, 13, 21 e 34, repetindo o padrão do convite. As três pistas conectam o espaço atual ao percurso iniciado no escritório. A presença visual de Lorelai na etapa de dedução é uma lembrança, não uma aparição física nem ajuda disponível à protagonista.'),
('sub', 'A primeira dedução'),
('p', 'Cassie precisa avaliar se a saída é realmente livre. A conclusão sustentada é que a porta contradiz o bilhete e que a aparência de escolha faz parte da armadilha. As provas são Saída bloqueada e Bilhete no retrato. A promessa escrita não apaga a condição observada da porta, nem a tranca identifica automaticamente uma pessoa que esteve no salão.'),
('sub', 'O alvo da mensagem'),
('p', 'Na segunda dedução, a pergunta deixa de ser como o ambiente funciona e passa a ser quem ele procura atingir. Cassie relaciona Marcas no mosaico, Bilhete no retrato e Chave Fibonacci. O padrão liga o salão ao convite; a mensagem cifrada pede sua presença; o bilhete usa Lorelai para aproximar o caso do seu passado.'),
('p', 'A conclusão do capítulo é que Celine foi usada como isca para aproximar Cassie dos Masters e de respostas sobre Lorelai. Se o jogador apresenta uma hipótese errada ou um conjunto inadequado de provas, perde pontos e precisa revisar o argumento. O jogo só libera o encerramento quando as duas deduções estão sustentadas.'),
('h', 'Epílogo O que fica'),
('p', 'Cassie reconhece que, enquanto procurava o caminho de Celine, cada pista também desenhava o seu. No salão, tornou-se clara a diferença entre investigar uma situação e ser conduzida por ela. O nome de Lorelai no bilhete mostra que alguém sabia onde atingi-la, mas não prova quem escreveu a mensagem.'),
('p', 'Dean retoma o relato de Cassie e identifica uma linha comum entre convite, código e salão. Lia resume a mudança de perspectiva: uma mentira escondia medo e uma promessa escondia uma porta fechada. As versões só puderam ser compreendidas quando comparadas aos registros.'),
('p', 'O encerramento reconhece seu próprio limite: a armadilha foi compreendida, mas as respostas completas sobre Celine e Lorelai não chegaram. Aquilo que não foi demonstrado permanece no dossiê como pergunta. Cassie não escolhe as respostas que gostaria de ouvir; decide sustentar apenas o que pode demonstrar.'),
('p', 'A última reflexão varia conforme o desempenho. Se houve erros, Cassie admite que existem lacunas a reconhecer antes de seguir. Sem erros, afirma que os registros sustentam os passos da conclusão. A história-base não muda: a variação expressa a qualidade da investigação, não um destino alternativo para os personagens.'),
('p', 'Depois das seis falas do epílogo, aparece o relatório com pontuação total, pistas encontradas, enigmas resolvidos, mentiras identificadas, conexões corretas e erros investigativos. O desempenho recebe uma classificação, de Muitas pontas soltas a Investigação exemplar.'),
('h', 'Escolhas e limites do capítulo'),
('p', 'As escolhas alteram as informações registradas, a pontuação e a necessidade de rever conclusões. Pressionar Redding acrescenta uma pista; explorar objetos opcionais amplia o contexto; consultar os Naturais oferece informações parciais. Errar um código ou uma reconstrução exige nova tentativa. No interrogatório, a equipe revisa os resultados; na fase final, Cassie precisa corrigir o próprio argumento.'),
('p', 'Não há uma escolha que transforme o depoente em autor comprovado do desaparecimento ou confirme Lorelai como autora do bilhete. Também não há, nesta versão, resgate de Celine, prisão dos Masters, solução definitiva sobre Lorelai ou cena de saída física do salão. Esses acontecimentos não devem ser acrescentados ao relato como se já estivessem implementados.'),
('p', 'O fechamento atual é investigativo: Cassie identifica o propósito da armadilha e reconhece os limites das provas. O fio condutor é a busca pela verdade em um ambiente em que mentiras, medo e vínculos pessoais podem ser usados para induzir decisões.'),
('h', 'Base deste documento'),
('p', 'História e falas: scripts/dialogos.py. Objetos e registros do dossiê: scripts/pistas.py. Transições, consequências e encerramento: scripts/cenas.py. Desempenho e classificação: scripts/investigacao.py. Escopo do protótipo: README.md. O GDD fornecido serviu de referência visual e de organização. Acentos e pontuação foram normalizados para leitura, sem alterar o sentido das falas selecionadas.'),
]

from story_script import CONTENT

with ZipFile(SOURCE) as archive:
    original = {name: archive.read(name) for name in archive.namelist()}
tree = etree.fromstring(original['word/document.xml'])
body = tree.find('w:body', NS)
paragraphs = body.findall('w:p', NS)
patterns = {'title': paragraphs[0], 'p': paragraphs[1], 'h': paragraphs[13], 'sub': paragraphs[26]}
section = deepcopy(body.find('w:sectPr', NS))
for child in list(body):
    body.remove(child)

for kind, text in CONTENT:
    template = patterns[kind]
    paragraph = etree.SubElement(body, f'{{{W}}}p')
    props = deepcopy(template.find('w:pPr', NS))
    if props is None:
        props = etree.Element(f'{{{W}}}pPr')
    for obsolete in props.findall('w:numPr', NS):
        props.remove(obsolete)
    if kind in ('h', 'title', 'sub'):
        etree.SubElement(props, f'{{{W}}}keepNext')
    spacing = props.find('w:spacing', NS)
    if spacing is None:
        spacing = etree.SubElement(props, f'{{{W}}}spacing')
    spacing.set(f'{{{W}}}after', '120')
    if kind == 'h':
        spacing.set(f'{{{W}}}before', '240')
    paragraph.append(props)
    run = etree.SubElement(paragraph, f'{{{W}}}r')
    runprops = template.find('w:r/w:rPr', NS)
    if runprops is not None:
        run.append(deepcopy(runprops))
    node = etree.SubElement(run, f'{{{W}}}t')
    node.text = text
body.append(section)
result = dict(original)
result['word/document.xml'] = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(OUTPUT, 'w') as archive:
    for name, data in result.items():
        archive.writestr(name, data)
audit = {'source_sha256': sha256(SOURCE.read_bytes()).hexdigest(),
         'output': str(OUTPUT), 'paragraphs': len(CONTENT),
         'parts': {name: {'sha256': sha256(data).hexdigest(), 'bytes': len(data),
                          'preserved': result[name] == data} for name, data in original.items()}}
assert all(item['preserved'] for name, item in audit['parts'].items() if name != 'word/document.xml')
assert etree.tostring(section) == etree.tostring(etree.fromstring(original['word/document.xml']).find('w:body/w:sectPr', NS))
(Path(__file__).parent / 'audit.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
print(OUTPUT)
