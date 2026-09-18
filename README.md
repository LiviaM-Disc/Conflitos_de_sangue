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

## Imagens dos personagens

Coloque as artes em `assets/personagens/`. O jogo procura automaticamente por arquivos
`.png`, `.jpg`, `.jpeg`, `.webp` ou `.bmp` com estes nomes:

- `cassie`
- `dean`
- `michael`
- `lia`
- `sloane`
- `celine`
- `daniel`
- `lorelai`

Exemplo: `assets/personagens/cassie.png`.

Se alguma imagem nao existir, o jogo usa um placeholder gerado em tempo de execucao.

## Estrutura

- `main.py`: inicializacao do Pygame e loop principal
- `scripts/cenas.py`: estados de jogo, fases e transicoes
- `scripts/personagens.py`: jogador e retratos dos personagens
- `scripts/interfaces.py`: botoes, paineis, texto e HUD
- `scripts/investigacao.py`: pontuacao, pistas, deducoes e progresso
- `scripts/dialogos.py`: falas e escolhas narrativas
- `scripts/pistas.py`: base de evidencias investigaveis
