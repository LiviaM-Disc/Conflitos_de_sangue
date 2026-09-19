# Conflitos de Sangue

Primeira versao jogavel em Python + Pygame baseada no GDD 

## Como rodar

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Controles

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

## Conteudo jogavel

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
Salvamentos anteriores sao convertidos automaticamente para o formato 3,
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
```

## Estrutura

- `main.py`: inicializacao do Pygame e loop principal
- `scripts/cenas.py`: estados de jogo, fases e transicoes
- `scripts/personagens.py`: jogador e retratos dos personagens
- `scripts/interfaces.py`: botoes, paineis, texto e HUD
- `scripts/investigacao.py`: pontuacao, pistas, deducoes e progresso
- `scripts/dialogos.py`: falas e escolhas narrativas
- `scripts/pistas.py`: base de evidencias investigaveis
- `scripts/salvamento.py`: formato, validacao e gravacao do progresso
