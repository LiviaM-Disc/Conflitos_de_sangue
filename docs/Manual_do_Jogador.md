# Manual do jogador de Conflitos de Sangue

Guia rápido para jogar e apresentar o projeto ao professor. O jogo é uma investigação narrativa em Pygame, com seis fases, pontuação e ranking local armazenado pelo Django. Não é necessário descobrir uma saída de cada sala.

## Começar a jogar

1. Feche uma versão antiga do jogo, se estiver aberta. Na pasta Conflitos_de_sangue, abra Jogar.cmd.
2. Escolha Iniciar investigação ou Nova investigação e informe um nome ou apelido. Confirmar uma nova partida substitui o progresso atual, mas não apaga o ranking.
3. Use um apelido diferente para cada pessoa. Reutilizar o mesmo apelido reúne as partidas do mesmo jogador; não há senha.
4. Leia o aviso, o contexto do caso, a apresentação da equipe e o objetivo. Depois vem a entrevista com Daniel Redding.
5. Ao voltar outro dia, escolha Continuar investigação. O jogo retoma a partida salva.

## Comandos essenciais

- Mouse: examine objetos, converse com personagens e clique nas passagens no alto da tela. Passe o mouse sobre um objeto para ver seu nome.
- Continuar: avança falas e fecha a leitura de um registro. Enter ou Espaço também avançam os diálogos.
- Inventário na parte inferior: clique em um item para selecioná-lo; depois clique no objeto do cenário em que deseja usá-lo. Clique no item novamente para desmarcar.
- Setas do inventário: mostram outros itens. A barra exibe seis de cada vez.
- Combinar: selecione dois itens e pressione o botão. Exemplo: ímã e tira metálica.
- Locais: abre o mapa para escolher um ambiente já disponível. Itens abre o inventário completo; Pistas abre o dossiê.
- Dica: na exploração indica o próximo passo. Em um enigma, oferece duas dicas e depois Ver resposta. Nenhuma dica desconta pontos.
- ESC: pausa. Na pausa, é possível salvar e voltar ao menu. Não é necessário encerrar toda a campanha de uma vez.

## Como responder aos desafios

Nos códigos, use os números na tela ou o teclado e pressione Confirmar. Nos desafios de sequência, clique nos valores na ordem correta. Nas tabelas, cada clique no campo troca a alternativa.

Nas deduções, escolha primeiro a conclusão; depois marque as provas que a sustentam e pressione Confirmar. Limpar permite refazer a seleção. Respostas erradas não bloqueiam o avanço: revise e tente novamente.

Se parecer que nada aconteceu, feche a mensagem com Continuar e consulte Dica. Algumas ações liberam outro objeto no mesmo ambiente, sem trocar de sala. Na manutenção, o crachá libera Carrinho e achados; depois, volte ao escritório para encontrar o envelope.

---

# Pontuação e apresentação do projeto

## Regras do ranking

- Evidência nova: 10 pontos. Enigma ou dedução correta: 20 pontos, além das evidências novas que a solução conceder.
- Erro penalizado: menos 5 pontos. A pontuação nunca fica abaixo de zero. Itens e progresso não são removidos.
- Dicas, mapas e leitura do dossiê são gratuitos. Reexaminar uma pista já registrada não gera pontos extras.
- Ao terminar o epílogo, a partida é registrada no banco. Abra Ranking no relatório ou no menu para comparar os resultados.
- O ranking mostra apenas a melhor partida de cada apelido. Todas as partidas concluídas ficam no histórico do banco.
- Em caso de empate em pontos, vence o menor número de erros; persistindo o empate, o resultado registrado primeiro fica à frente.
- Partidas antigas, iniciadas antes destas regras, podem ser concluídas, mas ficam fora do ranking competitivo. Para disputar o ranking, inicie uma nova investigação.

## O que mostrar ao professor

1. Abra o jogo e mostre a identificação por apelido e a apresentação da equipe.
2. Na primeira fase, pegue o clipe na recepção. No escritório, encontre o carbono na lixeira e use-o na luminária. Isso demonstra coleta, uso de item e resolução de um enigma.
3. Mostre a pontuação no alto da tela, o botão Dica, o dossiê e as passagens entre ambientes. Uma resposta errada desconta até 5 pontos, sem impedir nova tentativa.
4. Mostre as seis fases usando o guia de respostas como apoio. O mapa só libera os capítulos alcançados; não existe um botão de pular fases.
5. Depois de concluir a campanha, mostre o relatório e o ranking. Sem partidas concluídas, o ranking fica vazio; resultados de testes não são inseridos no banco real.

## Critérios atendidos

O projeto possui seis fases, sistema de pontuação, ranking, personagens com especialidades, cenários, regras, inventário e desafios. O Pygame cuida da janela, dos eventos e do desenho. O Django armazena jogadores e resultados por meio de modelos, migrations e banco SQLite.

A integração é local: não exige internet nem iniciar um servidor web. O arquivo saves/progresso.json guarda a partida em andamento; saves/ranking.sqlite3 guarda os jogadores e resultados. Não apague esses arquivos antes da apresentação.

## Conferência técnica opcional

Na pasta do projeto, os comandos abaixo verificam a configuração e mostram o ranking armazenado. Eles usam o mesmo ambiente Python do jogo.

`.\.venv\Scripts\python.exe manage.py check`

`.\.venv\Scripts\python.exe manage.py ranking`

Em outro computador, siga a instalação no README.md. Se aparecer resultado pendente, abra Ranking e clique em Atualizar e registrar. Não confirme uma nova partida antes de resolver a pendência.

O sistema identifica jogadores por apelido, sem autenticação. O ranking pertence a este computador e não foi projetado para uma competição online protegida contra alterações manuais.
