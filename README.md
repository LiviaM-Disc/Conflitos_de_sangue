# Conflitos de Sangue

Primeira versao jogavel em Python + Pygame baseada no GDD fornecido.

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

- Fase 1: exploracao do escritorio e cinco objetos investigaveis.
- Fase 2: tres assuntos no interrogatorio, com consultas opcionais a Lia e
  Michael. As observacoes oferecem contexto; o jogador escolhe a interpretacao.
- Fase 3: tres enigmas (termo ausente, intruso e chave por posicao), com dicas
  opcionais de Sloane. Erros permitem nova tentativa.
- Fase 4: selecao de duas evidencias que se sustentam e reconstrucao de quatro
  acontecimentos apresentados fora de ordem. Hipoteses incoerentes podem ser revistas.
- Fase 5: exploracao do salao sem a equipe, tres novas pistas obrigatorias e
  duas deducoes. Lorelai aparece como lembranca, nao como apoio na exploracao.
- Epilogo: mesmo encerramento-base do prototipo, com avaliacao variavel de
  desempenho. Erros nao criam finais alternativos.

O dossie marca evidencias utilizadas em deducoes corretas, sem classificar
automaticamente os objetos como relevantes ou irrelevantes. Habilidades repetidas
na mesma etapa nao geram novos pontos. Uma nova partida reinicia todas as etapas.

As falas do depoente, o horario 20h42, a chave 29 e as pistas do salao sao
conteudo original de adaptacao para exercitar as mecanicas do GDD, nao citacoes
nem acontecimentos confirmados do livro. Ainda faltam roteiro narrativo completo,
audio, salvamento e animacoes de caminhada quadro a quadro.

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
