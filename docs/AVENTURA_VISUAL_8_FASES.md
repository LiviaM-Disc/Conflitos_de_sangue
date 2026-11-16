# Conflitos de Sangue: aventura visual

Novas partidas usam oito fases. O motor continua Python/Pygame, sem servidor
web. As artes dos cenarios e personagens existentes foram reaproveitadas.
Salvamentos anteriores continuam no roteiro antigo e nao sao convertidos
em fases que o jogador ainda nao concluiu.

## Proposta

Inspiracao de interacao: Garfield's Scary Scavenger Hunt. Objetivo visivel,
poucos pontos de interacao grandes, inventario pequeno, resposta imediata e
obstaculos visuais. Nao foram copiados personagens, mapas ou assets do jogo.
Referencia: https://www.numuki.com/game/garfield-s-scary-scavenger-hunt/

A historia continua investigativa: Celine desapareceu e uma mensagem leva
Cassie a Mercer House. A equipe recupera provas; o desaparecimento ainda
nao e resolvido. Abertura e fechamento sao curtos; O caso e opcional.

## Oito fases

| Fase | Desafio | Progressao |
| --- | --- | --- |
| 1. O escritorio | Recolher a chave e abrir a gaveta | Aprender causa e efeito com dois alvos |
| 2. Sem sinal | Instalar fusivel e girar circuito | Caminho de seis pecas, entrada e saida visiveis |
| 3. A fotografia | Trocar seis fragmentos de imagem | Reconstrucao espacial com referencia visual |
| 4. O eco da casa | Repetir quatro sinais | Memoria visual, cores e formas redundantes |
| 5. Fora de alcance | Combinar ima e tira, recuperar ponteiro, ajustar relogio | Cadeia de objetos e comparacao com fotografia |
| 6. Dois bloqueios | Circuito de 12 pecas e cinco sinais | Duas etapas, seis simbolos e exibicao mais rapida |
| 7. Sob observacao | Capturar tres sinais na faixa segura | Precisao e ritmo, erro reinicia a sequencia local |
| 8. Antes que apaguem | Circuito de 16 pecas, sete sinais e quatro capturas | Sintese; faixa segura menor, sem apagar fases anteriores |

## Ligacao entre as descobertas

1. No escritorio, Cassie abre a gaveta e compara agenda, celular e envelope.
   Ainda nao ha acesso ao video; a agenda registra uma saida prevista.
2. Na central de cameras, a equipe restaura a energia e confere o porteiro.
   O video confirma a saida de Celine e a entrega posterior do envelope.
3. A foto rasgada veio dentro do envelope. Remonta-la revela Mercer House,
   onde a zeladora recebe a equipe.
4. A zeladora fornece um gravador com trava luminosa. O audio cita Lorelai,
   um relogio e o porao. Michael consegue uma foto de manutencao do relogio.
5. O jogador recoloca o ponteiro e reproduz 03:21, o horario dessa foto.
   O compartimento revela o cartao com duas sequencias: 12 e 16 formam o
   codigo da porta do porao. Sloane abre o acesso ao concluir as duas partes.
6. No porao, os bloqueios protegem perfis da equipe. Dean relaciona os
   arquivos aos testes; Sloane prepara a fila de copia dos lotes A, B e C.
7. A faixa verde indica conexao estavel. Cada acerto copia um desses lotes.
   Lia compara o recado anexado com o conteudo efetivamente recuperado.
8. O circuito e os sinais habilitam o terminal. Os cinco revisam o relatorio
   ANTES da transmissao. Depois, quatro acertos enviam cronologia, relato
   da zeladora, perfis e conclusoes. Somente entao a fase termina.

O local aparece no cabecalho. As analises identificam a fonte dos registros
na propria tela. As transicoes mostram o que foi descoberto e por que
seguir ao proximo ambiente, sem exigir uma tela extra de leitura.

## Controles

- Mouse: objetos, ferramentas, pecas e sinais.
- Fotografia: selecionar dois fragmentos para troca-los.
- Circuito: cada clique gira uma peca; a energia aparece em verde.
- Gravacao: observar o sinal e repetir. O botao Rever mostra os sinais restantes;
  voltar a cena ou retomar a partida preserva os sinais ja acertados.
  Errar reinicia a sequencia do desafio atual.
- Relogio: ajustar hora e minutos com + e - para corresponder a foto ao lado.
- Terminal: Copiar lote (fase 7) ou Enviar provas (fase 8) na faixa verde.
  O nome do lote ou da parte do relatorio identifica o que esta sendo transferido.
- ?: ajuda visual opcional, sem desconto direto de pontos.
- Pistas ou Tab: consultar somente as descobertas ja recuperadas; a consulta
  pausa os desafios. Esc fecha o dossie.
- Equipe: retratos e funcoes dos Naturais e das pessoas ligadas ao caso.
  A consulta pausa os desafios; Esc ou Voltar ao jogo fecha a tela.
- Analises: selecione os cartoes e clique em Confirmar. Em ordens, os numeros
  mostram a sequencia escolhida. Clique novamente para desmarcar ou use Limpar.
- Esc: pausa; o tempo dos desafios fica congelado.
- Fechar a janela: encerra a tentativa e registra os pontos no ranking.

Nao e necessario caminhar ate os objetos. Itens compativeis sao usados
diretamente quando estao no inventario; a selecao manual e opcional.
Na fase 5, ima e tira podem ser recolhidos em qualquer ordem. Depois,
Combinar + monta a ferramenta. Nas fases 6 e 8, o indicador Etapas mostra
os desafios concluidos, o atual e os seguintes; voltar a cena nao apaga
os bloqueios ja resolvidos.

A faixa Agora resume a acao atual em uma linha. Cliques em objetos ainda
bloqueados indicam o proximo passo e nao retiram pontos. A coleta tem uma
animacao curta ate o inventario, mas o item pode ser usado imediatamente.
Na memoria, Observe e Sua vez separam demonstracao e resposta. No desafio
de captura, o botao ganha destaque enquanto o marcador esta na faixa segura.

Ao concluir uma fase, a tela apresenta a pista recuperada, uma frase da
historia, o bonus da fase e o proximo objetivo. O dossie desta edicao usa
essas descobertas, sem os enigmas exclusivos da campanha anterior.

## Investigacao com a equipe

As fases 1 a 7 incluem uma analise jogavel depois do mecanismo principal.
Na fase 8, a equipe revisa o relatorio entre destravar o terminal e enviar as provas.
As 17 etapas usam registros curtos, ilustracoes e selecoes pelo mouse.
O retrato e a especialidade mostram quem esta conduzindo a tarefa. Na ultima
fase, todos participam da revisao do relatorio.

| Fase | Personagem | Tarefa adicional |
| --- | --- | --- |
| 1 | Cassie | Ordenar a saida prevista na agenda, o desligamento do celular e a descoberta do envelope |
| 2 | Lia | Confrontar duas falas com o celular e os horarios da camera |
| 3 | Dean | Selecionar duas pistas que indicam um convite dirigido a Cassie |
| 4 | Michael | Conversar com a zeladora e localizar o relogio citado no audio |
| 5 | Sloane | Completar as duas metades do codigo que abre a porta do porao |
| 6 | Dean e Sloane | Relacionar os perfis aos testes e preparar os tres lotes que serao copiados |
| 7 | Lia | Identificar uma contradicao e uma afirmacao sem prova |
| 8 | Todos os cinco | Preservar o relato, ordenar horarios, revisar a acusacao, selecionar provas e fechar as conclusoes |

Michael usa as reacoes para orientar a conversa, sem tratar medo como prova
de culpa. Lia distingue falas desmentidas de afirmacoes ainda nao comprovadas.
O destino de Celine e a autoria da mensagem continuam em aberto.

A abertura apresenta Celine, o aviso de Daniel Redding e os cinco Naturais.
O botao Equipe tambem apresenta Lorelai e os Masters em Pessoas do caso.
O epilogo mostra a equipe reunida e preserva a continuacao da historia.

## Pontuacao e resultados

Coleta: 10 pontos. Mecanismo concluido: 25. Cada analise correta: 10 pontos,
uma unica vez. Fase concluida: 50 mais 10 por
marca de desempenho (uma a tres). Erros de sinal/captura retiram 5 pontos,
com piso zero. Respostas incorretas nas analises tambem retiram 5 pontos.
Selecoes incompletas, limpar, desmarcar e consultar Equipe nao descontam pontos.
Girar pecas e trocar fotografias nao penaliza experimentacao.
Ajuda nao retira pontos existentes, mas limita a duas marcas o bonus da fase.
Repetir uma fase concluida nao concede pontos novamente.

O ranking Django/SQLite tem duas abas: Oito fases e Campanha anterior.
Resultados antigos sao mantidos. O esquema do save visual e a versao 7.
Saves visuais da versao 6 sao atualizados ao carregar: fases ja concluidas
permanecem concluidas, sem pontos adicionais. As analises entram nas fases
ainda em andamento ou futuras. Salvar no meio da analise preserva o
personagem, a etapa e a selecao; voltar a cena nao repete o mecanismo resolvido.
Fechar a janela durante a analise encerra e registra a pontuacao atual.
Partidas antigas que chegaram ao envio final antes da revisao agora abrem
a revisao pendente, preservando pontos e partes ja enviadas. Quando as quatro
partes ja haviam sido transmitidas, concluir a revisao nao exige reenvio.
Oito fases nao significa uma duracao garantida; tempo e dificuldade devem
ser avaliados com jogadores reais. O teste automatizado cobre o percurso
completo pelo mouse, regras, pausas, retomada e registro final.
