from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from copy import deepcopy
from PIL import Image
import hashlib, json

ROOT=Path(__file__).parent
SOURCE=Path(r'C:\Users\lb119\Downloads\GDD (1).docx')
OUT=Path(r'C:\Users\lb119\Conflitos_de_sangue\output\GDD_Conflitos_de_Sangue_Atualizado.docx')
SHOTS=Path(r'C:\Users\lb119\Conflitos_de_sangue\output\visual8-review')
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W,'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main','pic':'http://schemas.openxmlformats.org/drawingml/2006/picture','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
q=lambda x:'{'+W+'}'+x
def node(tag, **attrs):
    e=E.Element(q(tag))
    for k,v in attrs.items(): e.set(q(k),str(v))
    return e
with ZipFile(SOURCE) as z: parts={i.filename:z.read(i.filename) for i in z.infolist()}
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='d6b7eae200b89f1372ec664d9a826fcc4993a7ebf5d87f9093501df8b64283d4'
root=E.fromstring(parts['word/document.xml'])
body=root.find('w:body',NS)
sect=deepcopy(body.find('w:sectPr',NS))
paragraphs=body.findall('w:p',NS)
tables=body.findall('w:tbl',NS)
image_pars=[deepcopy(p) for p in paragraphs if p.find('.//a:blip',NS) is not None]
rels=E.fromstring(parts['word/_rels/document.xml.rels'])
relmap={r.get('Id'):r.get('Target') for r in rels}
for e in list(body): body.remove(e)

def p(text, kind='body', page=False):
    e=deepcopy(paragraphs[2]); e.clear()
    pr=node('pPr')
    if kind=='title': pr.append(node('pStyle',val='Title'))
    elif kind=='h1': pr.append(node('pStyle',val='Heading1'))
    if kind in ('title','h1','h2','caption'): pr.append(node('keepNext',val=1))
    pr.append(node('keepLines',val=1)); pr.append(node('widowControl',val=1))
    if page: pr.append(node('pageBreakBefore',val=1))
    before=200 if kind=='h1' else 140 if kind=='h2' else 0
    after=120 if kind in ('title','h1','h2') else 100
    pr.append(node('spacing',before=before,after=after,line=276,lineRule='auto'))
    pr.append(node('jc',val='center' if kind=='title' else 'both' if kind=='body' else 'left'))
    e.append(pr)
    r=node('r'); rp=node('rPr')
    rp.append(node('color',val='000000'))
    rp.append(node('sz',val=40 if kind=='title' else 28 if kind=='h1' else 24 if kind=='h2' else 22))
    if kind in ('title','h1','h2','caption'): rp.append(node('b'))
    r.append(rp); t=node('t'); t.text=text; r.append(t); e.append(r); body.append(e)
    return e

def table(rows, widths):
    source=tables[0] if len(widths)==2 else tables[1]
    tbl=deepcopy(source)
    for row in list(tbl.findall('w:tr',NS)): tbl.remove(row)
    grid=tbl.find('w:tblGrid',NS)
    for x in list(grid):grid.remove(x)
    for width in widths:grid.append(node('gridCol',w=width))
    total=sum(widths)
    tbl.find('w:tblPr/w:tblW',NS).set(q('w'),str(total))
    for ri,values in enumerate(rows):
        row=deepcopy(source.findall('w:tr',NS)[0 if ri==0 else 1])
        rpr=row.find('w:trPr',NS)
        if rpr is None:rpr=node('trPr');row.insert(0,rpr)
        for x in list(rpr):rpr.remove(x)
        rpr.append(node('cantSplit'))
        if ri==0:rpr.append(node('tblHeader'))
        for ci,(cell,value,width) in enumerate(zip(row.findall('w:tc',NS),values,widths)):
            cp=cell.find('w:tcPr',NS)
            for el in list(cell):
                if el is not cp:cell.remove(el)
            for el in list(cp):
                if E.QName(el).localname in ('tcW','shd','vAlign'):cp.remove(el)
            cp.append(node('tcW',w=width,type='dxa'))
            cp.append(node('shd',fill='000000' if ri==0 else 'FFFFFF',val='clear'))
            cp.append(node('vAlign',val='center'))
            for el in cp.findall('w:tcMar/*',NS):el.set(q('w'),'90')
            para=node('p');pr=node('pPr');pr.append(node('spacing',before=0,after=0,line=240,lineRule='auto'));para.append(pr)
            run=node('r');rp=node('rPr');rp.append(node('sz',val=22));rp.append(node('color',val='FFFFFF' if ri==0 else '000000'))
            if ri==0:rp.append(node('b'))
            run.append(rp);txt=node('t');txt.text=value;run.append(txt);para.append(run);cell.append(para)
        tbl.append(row)
    body.append(tbl)
    e=p('',kind='short');e.find('w:pPr/w:spacing',NS).set(q('after'),'0');e.find('w:r/w:rPr/w:sz',NS).set(q('val'),'4')
    return tbl

def figure(index, filename, caption, page=False):
    p(caption,'caption',page)
    e=deepcopy(image_pars[index])
    pr=e.find('w:pPr',NS)
    if pr is not None:e.remove(pr)
    pr=node('pPr');pr.append(node('jc',val='center'));pr.append(node('spacing',before=0,after=140));pr.append(node('keepLines'));e.insert(0,pr)
    rid=e.find('.//a:blip',NS).get('{'+NS['r']+'}embed')
    target='word/'+relmap[rid]
    path=SHOTS/filename
    parts[target]=path.read_bytes()
    width=6350000
    iw,ih=Image.open(path).size;height=round(width*ih/iw)
    for extent in e.findall('.//wp:extent',NS)+e.findall('.//a:xfrm/a:ext',NS):extent.set('cx',str(width));extent.set('cy',str(height))
    for crop in e.findall('.//a:srcRect',NS):crop.getparent().remove(crop)
    docpr=e.find('.//wp:docPr',NS)
    docpr.set('descr',caption);docpr.set('name',filename)
    body.append(e)

p('Conflitos de Sangue','title')
p('1 Identificação do projeto','h1')
for s in [
'Nome do jogo: Conflitos de Sangue',
'Linha temática: entretenimento e investigação',
'Gênero: aventura investigativa 2D com enigmas e interação por apontar e clicar',
'Modo de jogo: um jogador | Plataforma: computador | Idioma: português brasileiro',
'Tecnologias: Python, Pygame, Django e SQLite',
'Organização: módulos, classes e controle de cenas e estados',
'Autora: Lívia Maria Barros de Sousa',
'Versão documentada: campanha visual de oito fases | Atualização: 16 de novembro de 2026']:
    p(s,'short')
p('Descrição do projeto','h2')
p('Conflitos de Sangue é um jogo acadêmico de mistério desenvolvido em Python com Pygame. O jogador acompanha Cassie e os Naturais na investigação do desaparecimento de Celine. A campanha atual tem oito fases e transforma as descobertas em ações: recuperar registros, usar objetos, resolver mecanismos e comparar evidências com a equipe.')
p('O objetivo desta campanha é reunir, revisar e transmitir provas sobre o caso. O jogador entende o próximo passo por objetivos curtos, alvos visíveis e respostas imediatas às interações. O encerramento preserva as descobertas, mas deixa o desaparecimento de Celine e a autoria da mensagem em aberto para uma continuação.')
table([
['Aspecto','Definição'],
['Base narrativa','Universo de Conflitos de Sangue, da série Os Naturais, adaptado para o projeto acadêmico.'],
['Estrutura','Abertura e prólogo curtos, oito fases, epílogo e resultado.'],
['Experiência desejada','Curiosidade, suspense e satisfação ao compreender a ligação entre as pistas.'],
['Interação','Mouse, inventário pequeno, enigmas visuais e análises com os personagens.'],
['Referência de interação','Garfield’s Scary Scavenger Hunt: exploração intuitiva, objetos úteis e retorno visual.'],
['Público pretendido','Pessoas interessadas em mistério e enigmas, inclusive sem experiência prévia com o jogo.']
],[2800,7974])

p('1.1 Personagens','h1',True)
p('Os cinco Naturais participam de 17 etapas de análise distribuídas pela campanha. Cada tarefa apresenta o retrato, a especialidade e registros curtos. O jogador seleciona ou ordena cartões e confirma sua resposta. A participação da equipe faz parte da progressão das fases.')
table([
['Personagem','Especialidade ou vínculo','Função na campanha atual'],
['Cassie','Perfilação e reconstrução','Ordena os registros iniciais, acompanha a investigação e organiza as conclusões do relatório final.'],
['Dean','Perfil criminal','Relaciona evidências às intenções de quem preparou os testes e aos perfis encontrados sobre a equipe.'],
['Michael','Leitura de emoções','Orienta a conversa com a zeladora de Mercer House e ajuda a preservar seu relato. Medo não é tratado como prova de culpa.'],
['Lia','Análise de contradições','Compara declarações com registros e distingue uma fala desmentida de uma afirmação ainda sem prova.'],
['Sloane','Reconhecimento de padrões','Resolve sequências numéricas, organiza lotes de arquivos e confere a cronologia.'],
['Celine','Pessoa desaparecida','Seu desaparecimento inicia a investigação. A equipe procura registros de sua saída e pistas de seu paradeiro.'],
['Daniel Redding','Figura do prólogo','Apresenta um aviso sobre padrões que estabelece o tom da investigação.'],
['Lorelai','Ligação com o passado de Cassie','Seu nome aparece na gravação. Isso constitui uma pista, sem comprovar que seja responsável pelo caso.'],
['Masters','Ameaça ligada à trama','Grupo associado aos testes e ao conflito investigado; sua responsabilidade específica ainda exige provas.'],
['Zeladora','Testemunha de Mercer House','Recebe a equipe, entrega o gravador e fornece a fotografia de manutenção do relógio.'],
['Porteiro','Testemunha do prédio','Suas declarações são comparadas com os registros do celular e das câmeras.']
],[1800,2800,6174])
p('Regra de design','h2')
p('As habilidades ajudam a interpretar informações, mas exigem uma decisão do jogador. As conclusões precisam respeitar o que já foi descoberto. Os personagens continuam relevantes nas fases avançadas e todos participam da revisão final.')

p('2 História','h1',True)
p('Celine desapareceu. Cassie e sua equipe começam pelo escritório em busca de registros de sua saída. Um envelope anônimo, dirigido a Cassie, contém uma fotografia rasgada. A recuperação das câmeras e a reconstrução da imagem conduzem os Naturais a Mercer House.')
p('Na casa, a zeladora entrega um gravador. A mensagem menciona Lorelai, um relógio e o porão. Uma fotografia de manutenção permite ajustar o relógio e encontrar o código de acesso ao porão. A equipe descobre arquivos sobre os próprios Naturais, indicando que alguém estudou suas habilidades e preparou os testes.')
p('O jogador copia os registros, confronta as declarações e revisa o relatório com os cinco personagens antes de transmitir as provas. A campanha segue uma sequência principal: as decisões alteram o desempenho e a pontuação, enquanto os erros permitem novas tentativas. O epílogo confirma o envio do material e mantém a investigação aberta.')
p('2.1 Tema e apresentação','h2')
p('A busca pela verdade exige distinguir fatos, contradições e suspeitas. O suspense vem da descoberta de que a equipe também é observada. A abertura contextualiza o desaparecimento, apresenta os Naturais e inclui o aviso de Daniel Redding. Informações adicionais ficam disponíveis em O caso, Equipe e Pistas, sem interromper continuamente a ação.')
p('3 Progressão da história','h1')
p('A campanha atual possui oito fases obrigatórias. Cada conclusão revela uma pista e explica o motivo de avançar para o próximo ambiente.')
table([
['Etapa','Local','Ação principal e descoberta'],
['1 O escritório','Escritório de Celine','Abrir a gaveta e ordenar os registros iniciais; encontrar o envelope.'],
['2 Sem sinal','Central de câmeras','Restaurar a energia e confrontar relatos com o vídeo recuperado.'],
['3 A fotografia','Arquivo do prédio','Remontar a fotografia que identifica Mercer House.'],
['4 O eco da casa','Entrada de Mercer House','Abrir o gravador e conversar com a zeladora.'],
['5 Fora de alcance','Sala do relógio','Recuperar o ponteiro, ajustar o relógio e descobrir o código do porão.'],
['6 Dois bloqueios','Porão','Destravar os perfis da equipe e preparar a fila de cópia.'],
['7 Sob observação','Servidor','Copiar três lotes de registros e conferir o recado anexado.'],
['8 Antes que apaguem','Terminal de envio','Liberar o terminal, revisar o relatório e transmitir quatro partes.']
],[2700,2800,5274])

p('3.1 Desenvolvimento das oito fases','h1',True)
stages=[
('Fase 1 O escritório','A chave abre a gaveta, onde estão a agenda, o celular e o envelope dirigido a Cassie. Cassie ordena três registros: saída prevista para 20h30, celular desligado às 20h42 e envelope encontrado às 21h16. A agenda ainda não comprova a saída; essa confirmação depende das câmeras da próxima fase.'),
('Fase 2 Sem sinal','O jogador recolhe o fusível e resolve um circuito de seis peças para recuperar o vídeo. Lia compara o relato do porteiro com o celular e as imagens: Celine saiu às 20h30, o envelope foi entregue às 21h09 e o mensageiro saiu às 21h14. O envelope contém a fotografia da etapa seguinte.'),
('Fase 3 A fotografia','Seis fragmentos são reorganizados por troca de posições, com uma referência visual disponível. A fotografia revela Mercer House. Dean relaciona o destinatário do envelope à casa marcada e identifica um convite dirigido a Cassie. A equipe segue para o endereço, onde é recebida pela zeladora.'),
('Fase 4 O eco da casa','A zeladora entrega um gravador protegido por uma sequência de quatro sinais. Após abrir a trava, o jogador lê a transcrição da mensagem, que menciona Lorelai, um relógio e o porão. Michael conduz a conversa sem confundir medo com culpa e obtém a fotografia do relógio marcando 03h21.'),
('Fase 5 Fora de alcance','Ímã e tira podem ser recolhidos em qualquer ordem e combinados para retirar o ponteiro de uma grelha. Com o ponteiro recolocado, o relógio deve reproduzir 03h21. O compartimento revela duas sequências numéricas; Sloane encontra 12 e 16, que formam o código da porta do porão.'),
('Fase 6 Dois bloqueios','O arquivo do porão possui um circuito de 12 peças e uma trava de cinco sinais. Dean relaciona os perfis dos Naturais ao planejamento dos testes. Sloane organiza os lotes A, B e C, com 8, 16 e 32 registros, preparando a ordem de cópia da próxima fase.'),
('Fase 7 Sob observação','O jogador copia os três lotes quando o marcador está na faixa verde de conexão estável. Lia confronta o recado anexado com o material recuperado e separa uma contradição de uma afirmação sem prova. Os registros apontam Cassie como alvo, mas o rosto do mensageiro permanece oculto.'),
('Fase 8 Antes que apaguem','Um circuito de 16 peças e uma sequência de sete sinais liberam o terminal. Antes do envio, Michael, Sloane, Lia, Dean e Cassie revisam o relato, a cronologia e as conclusões. Quatro acertos na faixa verde transmitem o relatório. Só então a fase termina e o epílogo confirma que Celine ainda não foi encontrada.')]
for title,text in stages:p(title,'h2');p(text)

p('4 Gameplay','h1',True)
p('O ciclo principal é observar o objetivo, interagir com o alvo, recolher ou usar um objeto, resolver o mecanismo, analisar as evidências com a equipe e avançar a partir da descoberta. A dificuldade está na resolução dos desafios e na interpretação, mantendo visível o próximo passo.')
p('4.1 Objetivos e habilidades do jogador','h2')
table([
['Tipo','Objetivo'],
['Campanha','Concluir as oito fases e transmitir um relatório sustentado pelas provas reunidas.'],
['Fase','Resolver o obstáculo atual, compreender a descoberta e liberar a etapa seguinte.'],
['Desempenho','Acumular pontos, reduzir erros e melhorar o próprio resultado no ranking.']
],[2200,8574])
p('A experiência exercita observação, memória visual, reconhecimento de padrões, organização cronológica e comparação entre declarações e evidências. Os desafios de transmissão também exigem precisão no momento do clique.')
p('4.2 Mecânicas de jogo','h2')
table([
['Mecânica','Funcionamento'],
['Exploração e inventário','Clicar em objetos visíveis. Itens compatíveis são usados automaticamente quando disponíveis; a seleção manual é opcional.'],
['Combinação de objetos','Na quinta fase, recolher ímã e tira e usar Combinar + para montar a ferramenta magnética.'],
['Circuitos','Girar peças por clique para formar um caminho entre entrada e saída. A energia indica visualmente o trecho conectado.'],
['Fotografia','Selecionar dois fragmentos para trocar suas posições e reconstruir a imagem de referência.'],
['Memória visual','Observar sinais diferenciados por cor e forma e repetir a sequência. O botão Rever permite consultar novamente.'],
['Relógio','Usar os controles de hora e minutos para reproduzir o horário indicado na fotografia.'],
['Cópia e transmissão','Clicar em Copiar lote ou Enviar provas enquanto o marcador está na faixa verde.'],
['Análises da equipe','Selecionar ou ordenar cartões e clicar em Confirmar. Desmarcar e Limpar permitem revisar a resposta antes da confirmação.']
],[2900,7874])
p('4.3 Pistas e objetos','h2')
p('Os objetos têm uma função concreta na progressão: a chave abre a gaveta, o fusível restaura a energia, a ferramenta magnética recupera o ponteiro e a fotografia fornece o horário do relógio. Os documentos e depoimentos sustentam as análises. O painel Pistas reúne somente as descobertas já recuperadas, sem antecipar a solução das fases seguintes.')

p('4.4 Progressão e dificuldade','h1',True)
p('A dificuldade aumenta ao longo das oito fases por quantidade de etapas, tamanho dos circuitos, extensão e velocidade das sequências e precisão exigida nas transmissões. Os valores abaixo descrevem a progressão da campanha, e não modos selecionáveis pelo jogador.')
table([
['Fase','Exigência crescente','Participação da equipe'],
['1','Relação simples entre chave e gaveta.','1 análise com Cassie.'],
['2','Circuito de 6 peças.','2 análises com Lia.'],
['3','Fotografia com 6 fragmentos.','1 análise com Dean.'],
['4','4 sinais em 4 opções; intervalo de 0,9 s.','2 análises com Michael.'],
['5','Combinar itens, recuperar peça e ajustar relógio.','2 sequências com Sloane.'],
['6','Circuito de 12 peças e 5 sinais em 6 opções; intervalo de 0,7 s.','2 análises com Dean e Sloane.'],
['7','3 cópias no momento correto; faixa verde de 24% do percurso.','2 análises com Lia.'],
['8','Circuito de 16 peças, 7 sinais a cada 0,55 s e 4 envios; faixa verde de 15%.','5 análises, uma por Natural, antes do envio.']
],[1100,5874,3800])
p('4.5 Falha e recuperação','h2')
p('Uma resposta incorreta penalizada retira cinco pontos e permite tentar novamente. Errar uma sequência ou uma captura reinicia o progresso desse desafio, preservando as fases anteriores e os mecanismos já resolvidos. A pontuação nunca fica negativa. Não há limite global de tempo nem perda de vidas.')
p('Girar peças, trocar fragmentos, limpar uma seleção e clicar em um alvo ainda bloqueado não descontam pontos. Pausar ou consultar Pistas e Equipe congela os desafios. Ao voltar à cena ou retomar um salvamento, as etapas já concluídas permanecem registradas.')
p('4.6 Sistema de pontuação','h2')
table([
['Ação','Efeito'],
['Recolher um item pontuado','+10 pontos.'],
['Concluir um mecanismo pontuado','+25 pontos.'],
['Concluir uma análise da equipe','+10 pontos, uma única vez por etapa.'],
['Concluir uma fase','50 pontos + 10 por estrela: bônus de 60, 70 ou 80.'],
['Errar uma resposta confirmada, sinal ou captura','−5 pontos, com pontuação mínima de zero.'],
['Solicitar ajuda pelo botão ?','Sem desconto direto; limita o bônus da fase a duas estrelas.'],
['Consultar O caso, Equipe ou Pistas','Sem desconto de pontos.']
],[6300,4474])
p('Três estrelas exigem zero erros e nenhuma dica; duas estrelas correspondem a menos de quatro erros, quando a condição anterior não é atendida; quatro ou mais erros resultam em uma estrela. A abertura da gaveta na primeira fase não recebe o bônus de mecanismo. Reabrir etapas concluídas não concede recompensas novamente.')

p('5 Interface e controles','h1',True)
p('O mouse é o controle principal da campanha de oito fases. Não é necessário caminhar até os objetos. O teclado complementa a navegação e permite escrever o nome do jogador.')
table([
['Comando ou botão','Função'],
['Clique do mouse','Recolher ou usar objetos, girar peças, trocar fragmentos e escolher respostas.'],
['Confirmar e Limpar','Enviar a análise selecionada ou limpar os cartões para refazê-la.'],
['Rever','Reexibir os sinais do desafio de memória.'],
['Pistas ou Tab','Consultar as evidências já descobertas.'],
['Equipe','Consultar os Naturais, suas funções e as pessoas ligadas ao caso.'],
['O caso ou F1','Rever o contexto e o objetivo da investigação.'],
['?','Pedir orientação visual sobre o desafio atual.'],
['Esc','Abrir a pausa ou fechar uma consulta, conforme a tela atual.'],
['X da janela','Encerrar a tentativa e registrar a pontuação atual no ranking.']
],[3100,7674])
p('5.1 Orientação durante a partida','h2')
p('O cabeçalho informa a fase, o local, o objetivo e a pontuação. A faixa Agora resume a ação atual. Alvos grandes, rótulos e retorno visual ajudam a compreender as interações. Na memória, Observe e Sua vez separam a demonstração da resposta. Nas transmissões, o botão ganha destaque quando o marcador entra na faixa segura.')
p('Ao concluir uma fase, uma tela mostra a pista recuperada, uma frase explicando a descoberta, as estrelas, o bônus e o próximo objetivo. A leitura obrigatória é curta; os detalhes ficam nas consultas opcionais. O painel Etapas, nas fases com vários bloqueios, indica o que foi resolvido e o que ainda falta.')
p('5.2 Telas e estados','h2')
p('A navegação inclui menu inicial, identificação do jogador, abertura, cena investigativa, mecanismo visual, análise da equipe, descoberta ao concluir a fase, pausa, consultas, epílogo, resultado e ranking. A opção de continuar corresponde a uma investigação salva e ainda não encerrada.')
p('6 Direção de arte','h1')
p('A apresentação usa cenários 2D ilustrados e as imagens dos personagens já produzidas para o projeto. A interface mantém tons escuros e discretos, contraste legível e elementos visuais de investigação. Os retratos identificam quem conduz cada análise; os objetos importantes precisam ser reconhecíveis e úteis para o objetivo atual.')
p('Os mesmos cenários podem representar diferentes áreas, identificadas pelo local exibido no cabeçalho. Ícones, cores e formas tornam os mecanismos legíveis. A referência de Garfield orienta a clareza da interação e o ritmo de descoberta, mantendo os personagens, a história e as artes deste projeto. As gravações narrativas são apresentadas por transcrição na interface.')

p('7 Descrição técnica','h1',True)
p('O jogo continua sendo uma aplicação de computador em Python e Pygame, com janela de 1120 × 720 pixels e atualização limitada a 60 quadros por segundo. A base de programação utiliza eventos, laço principal, imagens, textos, retângulos de interação, classes e estados. O estudo dirigido orienta essa base; os enigmas, a persistência e o ranking são implementações adicionais do projeto.')
table([
['Componente','Responsabilidade'],
['main.py','Inicializar o Pygame e controlar a janela, os eventos, a atualização e o desenho.'],
['scripts/cenas.py','Organizar menu, transições, pausa e encaminhamento da campanha.'],
['scripts/aventura_visual.py','Definir e executar as oito fases, objetos, mecanismos, objetivos e telas de descoberta.'],
['scripts/equipe_visual.py','Definir os personagens apresentados e as 17 etapas de análise da equipe.'],
['scripts/investigacao.py','Manter pontuação, erros e registros de desempenho investigativo.'],
['scripts/interfaces.py','Fornecer componentes visuais e elementos de interface.'],
['scripts/salvamento.py','Gravar e restaurar o progresso da investigação em arquivo JSON.'],
['scripts/jogadores.py','Gerenciar identificação do jogador, resultados e interface do ranking.'],
['scripts/ranking.py','Acessar jogadores e resultados por meio do ORM do Django.'],
['ranking_app e ranking_project','Definir modelos, migrações e configurações do banco de dados.'],
['assets','Armazenar imagens de personagens, cenários e demais recursos visuais.']
],[3800,6974])
p('7.1 Integração com Django e ranking','h2')
p('Antes de iniciar a investigação, o jogador informa um nome ou apelido de 2 a 24 caracteres. O Django armazena os jogadores e os resultados em um banco SQLite local. Cada tentativa registra pontuação, erros, fase alcançada, conclusão ou encerramento antecipado, campanha e data de registro.')
p('O ranking mostra o melhor resultado de cada jogador. A ordenação prioriza a maior pontuação; em empate, vence o menor número de erros e, depois, o resultado registrado primeiro. Tentativas encerradas antes da última fase também podem aparecer. As abas Oito fases e Campanha anterior mantêm separados os resultados das duas versões.')
p('O acesso ao banco ocorre diretamente pelo ORM do Django. A partida não depende de servidor HTTP, conexão com a internet, senha ou execução de runserver. O mesmo apelido identifica o mesmo jogador para comparação dos resultados locais.')

p('7.2 Salvamento e encerramento','h1',True)
p('Salvar pelo menu de pausa permite retomar uma investigação ainda em andamento. Fechar a janela pelo X encerra a tentativa e registra a pontuação atual, mesmo que as oito fases não tenham sido concluídas. Essa tentativa encerrada não deve reaparecer como um jogo pendente de continuação.')
p('Caso ocorra uma falha no registro do resultado, a interface apresenta o erro e mantém a janela aberta para uma nova tentativa. O progresso fica em saves/progresso.json, e o ranking em saves/ranking.sqlite3. O sistema mantém compatibilidade com salvamentos anteriores sem misturar suas fases ou resultados com a nova campanha.')
p('7.3 Organização e execução','h2')
p('A pasta principal Conflitos_de_sangue reúne main.py, assets, scripts, ranking_app, ranking_project, saves e tests. A execução normal é feita por python main.py, com as dependências do projeto instaladas. Os arquivos da campanha anterior permanecem para compatibilidade; novas investigações usam o roteiro visual de oito fases.')
p('7.4 Verificação do funcionamento','h2')
p('Os testes automatizados cobrem regras de pontuação, progressão das oito fases, análises com a equipe, pausas, salvamento, retomada e registro de resultados. A avaliação com jogadores também deve observar se o objetivo está claro, se os itens indicam sua função e se a dificuldade cresce sem depender de textos longos ou objetos difíceis de localizar.')
p('7.5 Atendimento aos critérios do projeto','h2')
table([
['Critério','Implementação'],
['Mínimo de cinco fases','Oito fases na campanha atual.'],
['Pontuação','Pontos por coleta, mecanismos, análises e conclusão; penalidades por erros definidos.'],
['Ranking','Classificação local pelo melhor resultado de cada jogador, com critérios de desempate.'],
['Personagens e cenários','Equipe com cinco especialidades, pessoas ligadas ao caso e ambientes identificados.'],
['Regras e dinâmicas','Uso de objetos, enigmas visuais, análise de evidências e progressão descritos neste GDD.'],
['Integração com Django','Modelos de jogadores e resultados persistidos em SQLite por meio do ORM.']
],[3600,7174])

p('8 Telas do jogo','h1',True)
p('As capturas a seguir ilustram a interface da campanha atual e a participação da equipe nas investigações. As situações exibidas são registros de desenvolvimento.')
figure(0,'team-roster-0.png','Figura 1 A equipe e suas especialidades')
figure(1,'story-art-4-explore.png','Figura 2 Objetivo e objetos na chegada a Mercer House')
figure(2,'story-art-4-team_task.png','Figura 3 Análise de Michael durante a conversa com a zeladora',True)
figure(3,'story-clock.png','Figura 4 Relógio e fotografia que orienta o ajuste')
figure(4,'story-copy.png','Figura 5 Cópia dos lotes com indicação de conexão estável',True)
figure(5,'story-send.png','Figura 6 Envio das provas após a revisão do relatório')

body.append(sect)
parts['word/document.xml']=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
OUT.parent.mkdir(exist_ok=True)
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
    for name,data in parts.items():z.writestr(name,data)
with ZipFile(SOURCE) as z:
    changed=[name for name,data in parts.items() if z.read(name)!=data]
(ROOT/'changed-parts.json').write_text(json.dumps(changed,indent=2),encoding='utf-8')
assert all(x=='word/document.xml' or x.startswith('word/media/') for x in changed)
assert E.tostring(sect)==E.tostring(body.find('w:sectPr',NS))
print('OUTPUT',OUT)
print('CHANGED PARTS',changed)
print('WORDS',len(' '.join(root.xpath('//w:t/text()',namespaces=NS)).split()))
