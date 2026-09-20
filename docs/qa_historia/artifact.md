# Contrato do documento narrativo

Referencia: C:/Users/lb119/Downloads/GDD.docx, original imutavel.
Render de referencia: reference/GDD.pdf e page-1.png ate page-9.png, conferidos.
O renderer empacotado falhou por ausencia de LibreOffice; a conversao foi feita
pelo Word instalado, em modo invisivel e somente leitura, seguida de PDFium.

Pagina A4 retrato, 11906 x 16838 twips, uma secao. Margens declaradas
566.9291338582677 twips nos quatro lados (aproximadamente 1 cm).
Distancias de cabecalho e rodape 720 twips; sem partes de cabecalho/rodape.
Arial 11 pt, entrelinha 1.15, texto justificado. Titulos de secao e titulo
principal reutilizam o padrao de 14 pt negrito do documento de origem.
Cor preta. Nao ha figuras, campos, controles de conteudo ou notas.
Tabelas da referencia documentam metadados e mecanicas; nao sao necessarias
para o pedido de narrativa e sao substituidas por prosa organizada.

Slots editaveis: todo o corpo narrativo word/document.xml/w:document/w:body,
exceto sectPr, preservado. Title de p[0] para o titulo, p[13] para headings
sem numeracao automatica, p[1] para texto justificado, p[26] para subtitulos.
Clonar esses padroes para as secoes narrativas; remover bookmarks de origem
ao substituir conteudo. Acrescentar keepNext nos titulos e espacamento de
6 pt entre paragrafos para evitar blocos densos. Corpo sem tabelas, sem capa
isolada, sem alteracao de estilos globais ou identidade visual.

Fluxo: titulo e escopo; sinopse; personagens; prologo; cinco fases; epilogo;
escolhas e limites do capitulo; fontes locais.
Textos em portugues com acentos. Falas selecionadas recebem apenas
normalizacao ortografica; prosa resume a implementacao e nao cria novos fatos.

Todas as partes do pacote e relacionamentos sao preserve-only, exceto
word/document.xml. O script gera inventario SHA256 e confere igualdade dos
demais bytes. Geometria/sectPr imutavel. SHA256 de referencia em audit.json.
Pagina final pode mudar com o conteudo. Conferir todas as paginas finais,
ausencia de cortes, titulos orfaos e espacos vazios excessivos.
