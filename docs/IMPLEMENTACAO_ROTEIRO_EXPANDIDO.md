# Implementacao do roteiro expandido

## Estrutura preservada

Python, Pygame, Game, Player, Button, FontBook e InvestigationState permanecem
como base do jogo. Django foi acrescentado somente para armazenar jogadores
e resultados com seu ORM em SQLite, sem substituir o loop do Pygame. O controlador
`scripts/campanha.py` recebe eventos, atualiza estados e desenha as cenas;
`scripts/roteiro_expandido.py` guarda falas, salas, objetos, dependencias,
enigmas, itens e provas. `scripts/cenas.py` encaminha a nova campanha ao
controlador, mantendo os caminhos antigos para retomar partidas antigas.

`scripts/campanha_visual.py` concentra conexoes entre salas, objetos desenhados
com Pygame, conversas contextuais e a barra de inventario. Todas as fases usam
essa exploracao por cliques. O teste independente do escritorio foi retirado
do menu; seu codigo historico e salvamento separado foram preservados.

## Percurso implementado

- Abertura: aviso, contexto, retratos com especialidades e objetivo inicial.
  Em seguida, entrevista de seis falas com Redding e tres objetos investigaveis.
  O dialogo antigo de 19 falas permanece disponivel para saves anteriores;
  novas partidas usam a sequencia independente `opening`.
- Fase 1: cinco ambientes, carbono/luminaria, clipe/tampa, chaves por patrimonio,
  cracha, fotografia opcional, manutencao, envelope posterior e deducao com provas.
- Fase 2: mentira protetora, portaria, deposito por cracha, copias de 21 minutos,
  recuperacao do bloco 21h03 e registro 21h09-21h14. Consultas limitadas.
- Fase 3: tres enigmas numericos, compartimento, transparencia/fotografia,
  retorno ao arquivo se necessario, consulta digital e deducao sobre o alvo.
- Fase 4: dez ambientes de Mercer House; livros, ima/tira, grelha, ponteiro,
  relogio, galeria, quarto, cartao/luz e tres fechaduras em ordem.
- Fase 5: seis gravacoes completas, grade de quatro registros, escolha de dois
  terminais e penalidade especifica por atribuir um rosto nao comprovado.
- Fase 6: nove fotografias, selecao verificavel, tres referencias no catalogo documental.
  A via direta nao bloqueia por erros. Saves com bloqueio antigo tambem podem usa-la.
  Deducao final exige Janela de insercao, Padrao Fibonacci e Mensagem dirigida a Cassie.
- Epilogo: sete falas do documento, aviso de continuidade e relatorio.

## Detalhes preenchidos para tornar o roteiro executavel

O documento descreve alguns desafios sem listar todas as alternativas ou
todos os dados. Foram definidos dados locais, sem acrescentar autoria a Lorelai:

- Patrimonio 417 e chaves distratoras 471/714.
- Fotos da mesa sem/com envelope as 21h03/21h16. O gelo confirma um intervalo
  curto, mas nao e tratado como um cronometro preciso.
- Registro da portaria confirma a saida de Celine as 20h30, depoente no hall
  as 21h03 e Cassie no corredor as 21h16. Esses dados tornam a grade determinada.
- Todas as seis gravacoes e nove legendas fotograficas estao explicitadas.
- A transparencia deixa ver MERCER HOUSE, por indices de letras verificaveis.
- As legendas fixas dos retratos prevalecem sobre tres cartoes soltos conflitantes.
- A rota alternativa usa cronologia e padrao em dois mecanismos sucessivos.
- O manual no corredor explica a transformacao do codigo final, permitindo
  resolver o painel mesmo sem consultar o terminal de Sloane.
- Cada enigma resolvido registra um checkpoint para compatibilidade. Erros
  nao provocam retorno nem tempo de espera. Cada erro penalizado desconta
  5 pontos, com pontuacao minima zero.
- Todos os enigmas possuem duas dicas graduais e uma revelacao opcional da
  resposta. A consulta preserva selecoes e nao conclui o enigma automaticamente.
- A melhor classificacao exige poucos erros, nenhuma identidade atribuida sem
  prova e leitura dos registros opcionais de recepcao, roteador e galeria.

## Escopo visual e balanceamento

Os ambientes sao estados distintos com destinos e requisitos proprios.
Passagens conectam salas vizinhas; o mapa oferece deslocamento direto como
alternativa. Nao existe premissa de Cassie estar presa para fugir da casa.
Chaves abrem compartimentos e documentos fazem a investigacao avancar.
O inventario mostra seis itens por pagina e exige selecao antes do uso;
enigmas numericos aceitam mouse ou teclado. Dicas nao executam a proxima acao.
Os fundos ilustrados existentes sao reutilizados; nao se
afirma que todos os novos comodos ja tenham arte exclusiva. A fotografia, o
video, as gravacoes e os mecanismos sao representados por registros e paineis
interativos, nao por novos filmes ou vozes gravadas. Uma escolha errada de
gravacao mostra uma mensagem e desconta 5 pontos, sem sintese de audio.

A meta de duracao de 30-50 minutos por fase precisa de teste com jogadores.
Os testes automatizados verificam progressao, dependencias e recuperacao,
nao garantem esse tempo de jogo nem o nivel subjetivo de dificuldade.

## Compatibilidade e verificacao

Save 5 inclui identificacao do jogador e da partida, alem da campanha, e migra os formatos 1-4 sem trocar a
historia de uma partida iniciada. Novas partidas usam a campanha expandida.
Os testes usam SDL dummy e arquivos temporarios; nao alteram saves do usuario.

Comando: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`.

Banco Django: `.\.venv\Scripts\python.exe manage.py test ranking_app`.
Partidas antigas ficam fora do ranking competitivo para nao misturar regras.
