# Conflitos de Sangue

Primeira versao jogavel em Python + Pygame baseada no GDD 

## Campanha expandida

### Jogadores e ranking Django

No menu, Iniciar/Nova investigacao pede um apelido de 2 a 24 caracteres.
O mesmo apelido (ignorando maiusculas) identifica o mesmo jogador; nao ha
login nem senha. Use apelidos diferentes para pessoas diferentes.

O Django armazena jogadores e todas as partidas concluidas em
`saves/ranking.sqlite3`. O Pygame usa o ORM diretamente, sem servidor HTTP
ou internet. As migrations sao aplicadas automaticamente no primeiro acesso.
O ranking mostra a melhor partida por jogador. Empates: menos erros, depois
o resultado registrado primeiro. Ao terminar o epilogo, o resultado e
registrado; reabrir o relatorio nao duplica a partida. Falhas de banco permitem
tentar novamente em Ranking, sem fingir que o resultado foi salvo.

Cada evidencia nova vale 10 pontos; enigmas e deducoes corretos valem 20,
alem das novas evidencias concedidas. Cada erro penalizado custa 5 pontos,
com piso zero. Dicas sao gratuitas; reexaminar pistas nao rende pontos extras.
Nao ha bloqueio por erros. Os descontos valem para a campanha expandida.

Partidas anteriores ao formato 5 preservam seu progresso e podem ser
concluidas; sao guardadas no historico, mas nao entram no ranking competitivo,
pois comecaram sem as mesmas penalidades. Uma nova partida usa as novas regras.
O teste separado do escritorio e a campanha antiga nao participam do ranking.

Este ranking e local ao computador, sem autenticacao nem protecao contra
edicao manual de arquivos. Nao e um servico de competicao online.

### Investigacao interativa: escritorio

O teste do escritorio foi retirado do menu. Seu codigo e salvamento separado
permanecem apenas como referencia historica. A campanha completa e a opcao jogavel.
No antigo prototipo, era possivel clicar nos objetos do cenario
para examina-los. O inventario permanece visivel; selecione a chave ou o
cracha e clique no destino. O bilhete e a fotografia podem ser relidos ali.

Nao ha fuga, porta trancada ou codigo de saida. Cassie pode ir e voltar entre
o escritorio e a sala da equipe desde o inicio. A chave abre a gaveta; o cracha
permite consultar os acessos no computador. Apos essa consulta, um envelope
aparece na mesa. A fotografia anterior e o celular ajudam a sustentar a conversa
com Dean. O trecho termina com uma descoberta sobre a interferencia no caso,
nao com uma fuga. A analise posterior da mensagem faz parte da campanha completa.
Ha dicas graduais, pontuacao e interacoes visuais. Tudo funciona com mouse;
ESC pausa. As salas reutilizam as artes existentes.

O progresso deste teste fica em `saves/escritorio_escape.json`, separado de
`saves/progresso.json`. Esse arquivo antigo foi preservado, mas nao ha mais
botao para abrir o teste no menu. A campanha principal nao foi alterada.
O nome antigo do arquivo foi mantido para compatibilidade. Saves do prototipo
de fuga preservam os objetos, mas retomam a investigacao sem inventar as novas
descobertas; o teclado e a conclusao de fuga sao removidos na migracao.
Implementacao em `scripts/escritorio_escape.py`, apenas Pygame e biblioteca
padrao: imagens existentes, retangulos, classes, eventos e estados de cena.

### Roteiro completo

Novas partidas usam `Conflitos_de_Sangue_Roteiro_Expandido_Jogo.docx`: prologo,
seis fases e epilogo. Ha mapa de ambientes, inventario separado do dossie,
combinacao de objetos, retorno a salas anteriores e enigmas encadeados.

Novas partidas comecam com quatro telas de abertura: aviso de conteudo,
contexto do caso, retratos e especialidades da equipe e objetivo inicial.
Depois vem a entrevista original de seis falas com Daniel Redding.
O epilogo termina com a indicacao de que a investigacao continua, sem resolver
os misterios restantes. O texto de abertura e adaptacao narrativa para o jogo.
Saves anteriores preservam sua sequencia de dialogo; partidas avancadas nao
repetem a abertura nem perdem progresso.

O estilo de investigacao por cliques abrange o prologo, as seis fases e o
epilogo. Botoes de passagem conectam os ambientes; objetos e personagens
podem ser examinados no cenario. O inventario fica visivel, com seis itens
por pagina: selecione um objeto e clique no destino, ou selecione dois e
use Combinar. Os itens nao sao aplicados automaticamente.

O objetivo do capitulo permanece visivel. Dica explica o proximo passo
somente quando solicitada, sem executar a acao. Mapa e inventario completo
sao consultas opcionais; a campanha pode ser concluida com o mouse e a
barra de itens. Os paineis numericos possuem teclado na tela. O catalogo
final cruza referencias documentais, nao destranca uma saida.

- I: inventario. Selecione ate dois objetos para usar ou combinar.
- M: mapa. Escolha uma fase ja alcancada e depois o ambiente.
- Q: consultas limitadas; TAB: dossie; ESC: pausa e salvamento.
- Mouse: examinar objetos, escolher destinos e responder aos enigmas.
- Numeros: codigos; Enter: confirmar; Backspace: corrigir.
- WASD/setas e E continuam disponiveis na exploracao.

Todo enigma tem duas dicas progressivas e uma opcao explicita de ver a
resposta. Consultar dicas nao resolve o enigma automaticamente nem apaga a
resposta em andamento. As dicas sao gratuitas e ficam registradas no save.
Erros descontam 5 pontos, sem saldo negativo, perda de itens ou bloqueio dos paineis.
Os terminais narrativos da quinta fase continuam permitindo duas consultas
diferentes; esse limite nao se aplica ao botao Dica.

**Nova investigacao** inicia o roteiro expandido. **Continuar** preserva a
historia da partida salva: saves antigos seguem na campanha anterior, sem
misturar tramas. Confirmar nova partida substitui o unico slot. O formato atual
de save e 5, incluindo identificacao da partida, jogador, inventario e consultas.

As artes existentes foram reutilizadas nos novos ambientes; os comodos ainda
nao possuem todos fundos exclusivos. A duracao de 4 a 6 horas do documento e
uma meta, nao um tempo validado desta implementacao. Detalhes e decisoes de
adaptacao estao em `docs/IMPLEMENTACAO_ROTEIRO_EXPANDIDO.md`.

## Relacao com o estudo dirigido

A base continua em Pygame, com a organizacao ensinada no material:

- Paginas 5-7: pastas `assets` e `scripts`, janela e repeticao principal em `main.py`.
- Paginas 9-10: classe do jogador, movimento, desenho e caixa de colisao em `scripts/personagens.py` (equivalente ao `jogador.py` do estudo).
- Paginas 13-15: troca de cenas por estado em `scripts/cenas.py`.
- Paginas 16-20: textos e botoes em `scripts/interfaces.py`.
- Paginas 20-22: verificacoes de colisao e contadores de pontuacao.

O roteiro usa essa mesma sequencia: receber eventos, atualizar e desenhar.
As falas e os desafios ficam em listas e dicionarios de
`scripts/roteiro_expandido.py`; a classe de `scripts/campanha.py` consulta esses
dados com condicoes para liberar salas e conferir respostas.

Inventario, deducoes e salvamento sao extensoes: nao estao ensinados passo a
passo no PDF. Para limitar a complexidade, o deslocamento entre salas usa
botoes, gravacoes e videos usam texto, e os mecanismos usam selecoes e codigos.
O motor continua sendo Pygame; nao ha sintese de audio. Django e SQLite
foram acrescentados apenas para atender ao requisito de jogadores e ranking.

## Como rodar

Neste computador, abra `Jogar.cmd`. Na primeira preparacao de outro computador:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe main.py
```

## Controles

O botao **Como jogar**, no menu e na campanha, abre um guia sem spoilers.
F1 tambem abre a ajuda; ESC fecha sem alterar a resposta ou o progresso.
Novos jogadores veem o guia apos informar o apelido e podem fecha-lo a
qualquer momento para iniciar a abertura. Partidas ja salvas tambem tem acesso
ao guia. Enigmas exibem lembretes de selecao e confirmacao quando nao ha
uma mensagem de resultado. Nenhuma regra, resposta ou pontuacao foi alterada.

- WASD ou setas: movimentar Cassie na exploracao
- E: investigar objeto proximo
- Q: usar habilidade quando a fase permitir
- TAB: abrir ou fechar painel de pistas
- ESC: pausar
- Mouse: escolher respostas, botoes e deducoes
- Numeros e Backspace: preencher e corrigir codigos; Enter: confirmar
- Enter ou Espaco: avancar falas do prologo e do epilogo
- Roda do mouse ou setas do dossie: navegar pelas paginas de pistas

## Imagens dos personagens

As 36 artes recebidas foram organizadas em subpastas de `assets/personagens/`:

- `cassie`
- `dean`
- `michael`
- `lia`
- `sloane`
- `celine`
- `daniel`
- `lorelai`
- `masters`

Cada pasta contem `idle.png` (parado), `walk.png` (andando), `action.png`
(investigando) e `sprite_sheet.png` (folha de referencia preservada).

Exemplo: `assets/personagens/cassie/idle.png`.

Os dialogos e as telas de investigacao usam retratos transparentes em pe.
Na exploracao, Cassie alterna entre parada, andando e investigando.
Estas sao poses estaticas, nao uma animacao quadro a quadro. As folhas completas
nao sao recortadas automaticamente. Masters esta cadastrado, mas ainda nao tem
uma aparicao visual nas cenas atuais; Celine tambem permanece sem retrato em cena.

As imagens originais mantem fundo e legendas e continuam preservadas.
O jogo prioriza os atlas transparentes em `assets/personagens/preparados/`.
Essas versoes foram editadas com IA a partir dos originais e podem apresentar
pequenas diferencas. Cassie possui tres poses; os demais usam o retrato preparado
tambem nas telas de investigacao. A caminhada tem oscilacao leve e orientacao
horizontal, mas ainda nao possui um ciclo de quadros completo.
O novo escritorio ilustrado fica em `assets/cenarios/escritorio.png`, com areas
de interacao alinhadas aos objetos e bloqueio da mesa central e mesa lateral.
O carregador tambem aceita JPG, JPEG, WEBP e BMP e preserva o suporte ao formato
anterior, como `assets/personagens/cassie.png`. Uma pose ausente usa `idle`.

Se alguma imagem nao existir, o jogo usa um placeholder gerado em tempo de execucao.

## Cenarios e interface

- Prologo e fase 2: sala de entrevistas (`entrevista.png`).
- Fase 1: escritorio de Celine (`escritorio.png`).
- Fase 3: laboratorio de analise (`analise.png`).
- Fase 4 e epilogo: arquivo da investigacao (`arquivo.png`).
- Fase 5: salao dos Masters (`masters.png`).

Os cenarios estao em `assets/cenarios/`; os prompts de geracao estao em
`assets/cenarios/PROMPTS.md`. O prologo pode ser avancado pelo mouse ou teclado.
O interrogatorio mostra o resultado antes de seguir. O dossie exibe todas as
evidencias em paginas de quatro registros. Pausar ou consultar pistas congela
o tempo das mensagens.

## Conteudo da campanha anterior

- Prologo: conversa de oito falas com Redding, escolha investigativa e cinco
  falas de preparacao com a equipe antes de entrar no escritorio.
- Fase 1: exploracao do escritorio e cinco objetos investigaveis.
- Fase 2: tres assuntos no interrogatorio, com consultas opcionais a Lia e
  Michael. A interpretacao precisa ser acompanhada por uma prova coletada.
  Hipoteses alternativas exigem distinguir suspeitas de fatos confirmados.
- Fase 3: tres enigmas (termo ausente, intruso e chave por posicao), com dicas
  opcionais de Sloane. Respostas numericas digitadas, sem alternativas;
  a chave final combina quatro termos por posicao. Erros permitem nova tentativa.
- Fase 4: selecao de duas evidencias que se sustentam e reconstrucao de quatro
  acontecimentos apresentados fora de ordem. Hipoteses incoerentes podem ser revistas.
- Fase 5: exploracao do salao sem a equipe, tres novas pistas obrigatorias e
  duas deducoes, sustentadas por duas e tres provas, respectivamente.
  Lorelai aparece como lembranca, nao como apoio na exploracao.
- Epilogo: seis falas de fechamento do capitulo, com reflexao de Cassie e da
  equipe, seguidas pelo relatorio de desempenho. Erros nao criam finais alternativos.

O dossie marca evidencias utilizadas em deducoes corretas, sem classificar
automaticamente os objetos como relevantes ou irrelevantes. Habilidades repetidas
na mesma etapa nao geram novos pontos. Uma nova partida reinicia todas as etapas.

Nos confrontos, o jogador pode consultar o dossie, selecionar provas em paginas
e rever a hipotese antes de apresentar o argumento. Apenas pistas coletadas
ficam disponiveis. A avaliacao exige a hipotese correta e o conjunto completo
de provas relevantes; acertar apenas uma parte perde pontos. Ha ate tres espacos
em qualquer argumento, sem revelar quantas provas sao necessarias. No interrogatorio,
a equipe revisa o resultado. No final, erros bloqueiam a conclusao ate o jogador
rever o argumento; o aviso nao revela qual parte estava correta.

As falas do depoente, o horario 20h42, a chave 29 e as pistas do salao sao
conteudo original de adaptacao para exercitar as mecanicas do GDD, nao citacoes
nem acontecimentos confirmados do livro. Prologo e epilogo tambem usam falas
originais do prototipo: fecham este capitulo, sem inventar o destino definitivo
de Celine ou Lorelai. Ainda faltam roteiro narrativo completo,
audio e animacoes de caminhada quadro a quadro.

## Salvamento

O jogo possui um slot local em `saves/progresso.json`. O progresso e gravado
automaticamente apos acoes, a cada cinco segundos quando ha alteracoes e ao
fechar normalmente a janela. O menu mostra **Continuar** quando existe uma
partida valida. Enter no menu retoma essa partida.

O salvamento inclui fase e subetapa, posicao, pistas utilizadas, pontuacao,
habilidades ja consultadas e selecoes parciais da reconstrucao e dos confrontos.
Salvamentos anteriores sao convertidos automaticamente para o formato 5,
preservando o progresso e as conclusoes ja avaliadas. Pausa e dossie
fecham ao retomar; mensagens temporarias reaparecem por alguns segundos.
Falas da abertura e do encerramento e codigos parcialmente digitados tambem
sao preservados. Continuar retoma a fase salva; Nova investigacao inicia o prologo.

Na pausa, **Salvar partida** grava manualmente e **Salvar e voltar ao menu**
retorna ao menu. **Nova investigacao** pede confirmacao antes de substituir
uma partida valida. Um arquivo ilegivel nao e alterado ao abrir o jogo; iniciar
uma partida nova o substitui. Falhas ao gravar geram aviso, preservam o ultimo
arquivo valido e impedem sair normalmente ate salvar ou escolher **Sair sem salvar**.

Os testes usam pastas temporarias e nao alteram o progresso real do jogador.

## Verificacao

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe manage.py test ranking_app
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py ranking
```

## Estrutura

- `main.py`: inicializacao do Pygame e loop principal
- `scripts/cenas.py`: estados de jogo, fases e transicoes
- `scripts/campanha.py`: regras da campanha expandida
- `scripts/campanha_visual.py`: passagens, objetos visuais e inventario na tela
- `scripts/roteiro_expandido.py`: salas, falas, itens e enigmas da campanha
- `scripts/personagens.py`: jogador e retratos dos personagens
- `scripts/interfaces.py`: botoes, paineis, texto e HUD
- `scripts/investigacao.py`: pontuacao, pistas, deducoes e progresso
- `scripts/dialogos.py`: falas e escolhas narrativas
- `scripts/pistas.py`: base de evidencias investigaveis
- `scripts/salvamento.py`: formato, validacao e gravacao do progresso
- `scripts/jogadores.py`: nome do jogador e tela de ranking
- `scripts/ranking.py`: integracao do Pygame com o ORM do Django
- `ranking_app/models.py`: jogadores e resultados persistidos
- `ranking_project/settings.py`: banco SQLite e configuracao local do Django

Manuais: `docs/Manual_do_Jogador.docx` e `docs/Guia_de_Respostas.docx`.
As versoes em Markdown ficam na mesma pasta. O ORM em um programa Python
independente segue a [documentacao oficial do Django](https://docs.djangoproject.com/en/5.2/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage).
