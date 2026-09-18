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

Os dialogos do prologo usam a pose parada. As telas de investigacao usam a pose
de acao. Na exploracao, Cassie alterna entre parada, andando e investigando.
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

## Estrutura

- `main.py`: inicializacao do Pygame e loop principal
- `scripts/cenas.py`: estados de jogo, fases e transicoes
- `scripts/personagens.py`: jogador e retratos dos personagens
- `scripts/interfaces.py`: botoes, paineis, texto e HUD
- `scripts/investigacao.py`: pontuacao, pistas, deducoes e progresso
- `scripts/dialogos.py`: falas e escolhas narrativas
- `scripts/pistas.py`: base de evidencias investigaveis
