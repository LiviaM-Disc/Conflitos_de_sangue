# Artes preparadas

Geradas com a ferramenta integrada image_gen em 18/09/2026. Os PNGs nas pastas
individuais dos personagens sao os originais e foram preservados. As edicoes
com IA podem alterar pequenos detalhes; nao sao recortes pixel a pixel.

## Arquivos usados pelo jogo

- cassie.png: tres celulas horizontais, idle, walk, action.
- equipe.png: grade 2x2, Dean, Michael, Lia, Sloane, por linha.
- caso.png: grade 2x2, Celine, Daniel, Lorelai, Masters, por linha.
- ../../cenarios/escritorio.png: cenario da exploracao e fundo do menu.

As celulas sao selecionadas em memoria pelo Pygame. Nao substitua uma grade
por uma imagem individual sem atualizar prepared_portrait em personagens.py.

## Prompts usados

### Cassie

Edit target: supplied Cassie sprite sheet. Produce a production game sprite sheet PNG with genuinely transparent alpha background, NO white background, no checkerboard baked in, NO text, titles, captions, borders, floor or shadows. Preserve this exact red-haired chibi pixel-art character, cream jacket, blue jeans, sneakers, face and style. Exactly three equal-width cells in a single horizontal row: idle standing, walking pose, investigating with magnifying glass. Each full character contained within its cell with generous transparent gutters, feet aligned at 90% canvas height, same scale. Landscape 1536x1024 if possible. Remove all existing lettering and background. Output file to use in local Pygame project.

### Equipe

Edit these 4 supplied character images into one production transparent PNG sprite atlas. Exact 2 columns by 2 rows equal-sized cells. Top left Dean (brown-haired man black jacket), top right Michael (blond man blue shirt), bottom left Lia (black hair black outfit), bottom right Sloane (blond ponytail girl with tablet). Preserve each supplied character's face, hair, clothes and chibi pixel style. Full body visible, centered in each cell with generous transparent gutters. Remove all white paper backgrounds, all text and captions, shadows and borders. Actual transparent alpha background, no colored background or checkerboard drawn in. No text. Square canvas. Each character wholly inside its own quadrant.

### Caso

Edit these 4 supplied character images into one production transparent PNG sprite atlas. Exact 2 columns by 2 rows equal-sized cells. Top left Celine (long blond hair cream outfit), top right Daniel (short black hair orange prison uniform), bottom left Lorelai (red hair black long coat brown pants), bottom right Masters (faceless black hooded cloak). Preserve each supplied character's face, hair, clothes and chibi pixel style. Full body visible, centered in each cell with generous transparent gutters. Remove all white paper backgrounds, all text and captions, shadows and borders. Actual transparent alpha background, no colored background or checkerboard drawn in. No text. Square canvas. Each character wholly inside its own quadrant.

### Cenario

Create a polished 2D pixel art adventure game background for a chibi mystery investigation game. ONLY environment, no characters, no text, no UI, no captions. Landscape 1536x1024. Orthographic front-facing slightly elevated RPG room interior (not isometric), entire room visible edge to edge. A missing young woman's study at dusk. Sage green wallpaper, muted wine-red curtain accents, cool gray oak floorboards, ivory trim, restrained golden lamplight and silver moonlight. Clean crisp pixel-art details, readable and inviting mysterious atmosphere, not excessively dark. Layout for gameplay: back wall takes upper 38 percent, floor lower 62 percent. Bookshelf against upper left wall with one red book at reachable lower shelf; writing desk against back wall center with envelope on desktop; tall window with curtains on upper right; low small side table near right wall at 65% height with black cellphone; small gold bracelet on open floor near left at 70% height. Most of central and lower floor is empty walkable space with a subtle faded woven rug. Furniture must remain at perimeter, no foreground occluding furniture. Include tasteful personal touches papers and framed botanical picture. Consistent perspective and pixel-art scale for a character about 15% image height. This will be the playable full screen background, not a mockup or framed illustration.
