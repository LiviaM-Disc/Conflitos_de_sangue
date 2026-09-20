"""Conteudo da campanha expandida; estados e interacoes ficam em campanha.py."""

PROLOGUE = [
    ("Cassie", "Quero saber como eles escolhem as pessoas."),
    ("Daniel Redding", "Voce ainda esta pensando em pessoas. Eles pensam em padroes."),
    ("Cassie", "Padroes deixam rastros."),
    ("Daniel Redding", "Sim. Mas os melhores rastros sao aqueles que parecem pertencer a outra historia."),
    ("Cassie", "Voce esta dizendo que eles escondem uma investigacao dentro de outra?"),
    ("Daniel Redding", "Estou dizendo que, quando voce perceber qual historia esta seguindo, talvez alguem ja tenha escolhido o caminho por voce."),
    ("Cassie", "Meu nome e Cassie. Tento reconstruir o que as pessoas pensam a partir do que deixam para tras. Foi por isso que vim ouvir Daniel Redding falar sobre os Masters."),
    ("Cassie", "Os Masters sao o grupo que estamos investigando. Ainda sabemos pouco sobre seus planos. O aviso de Redding nao e uma prova, mas torna cada escolha mais inquietante."),
    ("Cassie", "Lorelai faz parte do meu passado. Ha perguntas sobre ela que ainda me acompanham. Preciso tomar cuidado para nao confundir o que desejo descobrir com o que consigo provar."),
    ("Dean", "Antes de chegarmos aqui, recebemos a noticia do desaparecimento de Celine. Nossa proxima parada e o escritorio dela. Ainda nao sabemos por que ela sumiu."),
    ("Cassie", "Celine e a pessoa que precisamos encontrar. Nao sabemos se saiu por vontade propria, se estava em perigo ou se o caso tem alguma ligacao com os Masters."),
    ("Dean", "Sou Dean. Trabalho com perfis e motivacoes. Vou ajudar Cassie a reconstruir as decisoes de Celine, mas uma explicacao convincente ainda precisa de provas."),
    ("Michael", "Eu sou Michael. Observo emocoes e reacoes que as pessoas tentam esconder. Medo pode indicar que algo importa, mas nao explica sozinho o que aconteceu."),
    ("Lia", "Sou Lia. Minha especialidade e perceber mentiras e contradicoes. Alguem pode mentir para se proteger ou para proteger outra pessoa. Vamos precisar descobrir a diferenca."),
    ("Sloane", "Eu sou Sloane. Trabalho com numeros, horarios e padroes. Se os registros nao combinarem, vou ajudar a encontrar onde a historia deixou de fazer sentido."),
    ("Cassie", "Nao trabalho sozinha. Dean, Michael, Lia e Sloane enxergam coisas diferentes. Juntos, podemos testar uma suspeita antes de transforma-la numa acusacao."),
    ("Dean", "No escritorio, comecamos pelo que podemos observar: os objetos, os registros e o que ficou fora do lugar. Primeiro entendemos a ausencia de Celine."),
    ("Lia", "E nao vamos chamar tudo de pista so porque parece estranho. O que importa e o que cada descoberta realmente permite afirmar."),
    ("Cassie", "Antes de partir, quero registrar o aviso de Redding e observar esta sala. Depois reunimos a equipe. A investigacao de Celine comeca agora."),
]
# The previous dialogue remains available only for existing saves.
BRIEFING = [
    ("Antes de comecar", "Esta historia aborda desaparecimento, manipulacao psicologica e lembrancas dolorosas. Este jogo apresenta um capitulo de uma investigacao maior; nem todas as perguntas serao respondidas aqui."),
    ("O desaparecimento de Celine", "Celine desapareceu. A equipe foi chamada para investigar os vestigios deixados em seu escritorio. Ainda nao ha elementos suficientes para afirmar como ou por que ela partiu. Cassie tambem busca respostas sobre os Masters, um grupo cujas intencoes permanecem incertas."),
    ("A equipe", "Cinco perspectivas sobre o mesmo caso. Suas especialidades ajudam a interpretar os registros, mas nenhuma impressao substitui uma prova."),
    ("A primeira tarefa", "Reconstruir os ultimos acontecimentos conhecidos e investigar o desaparecimento de Celine. Antes de visitar o escritorio, Cassie procura Daniel Redding para ouvi-lo sobre os Masters. As perguntas sobre Lorelai, ligadas ao passado de Cassie, ainda permanecem abertas."),
]
TEAM_PROFILES = [
    ("cassie", "Cassie", "Perfilacao", "Reconstroi comportamentos e motivacoes."),
    ("dean", "Dean", "Perfil criminal", "Analisa intencoes e escolhas."),
    ("michael", "Michael", "Emocoes", "Interpreta reacoes e sentimentos."),
    ("lia", "Lia", "Contradicoes", "Confronta falas e identifica mentiras."),
    ("sloane", "Sloane", "Padroes", "Compara numeros, horarios e probabilidades."),
]
OPENING = BRIEFING + PROLOGUE[:6]
EPILOGUE = [
    ("Dean", "Eles queriam que voce confundisse uma coincidencia com uma causa."),
    ("Cassie", "E queriam que eu escolhesse a resposta mais pessoal antes de escolher a mais provavel."),
    ("Lia", "Mentiras funcionam melhor quando carregam uma parte verdadeira."),
    ("Michael", "E medo funciona melhor quando a pessoa ja sabe onde doi."),
    ("Sloane", "Os numeros eram consistentes. A historia construida em volta deles, nem sempre."),
    ("Cassie", "Celine nao foi a chave. O caso dela foi a porta que alguem aproveitou para deixar aberta. O alvo era eu."),
    ("Cassie", "O nome de Lorelai continua aqui. Mas um nome nao e uma resposta. Ainda nao."),
    ("Continua", "A equipe encerra esta etapa com uma conclusao, nao com todas as respostas. O destino de Celine, a autoria da mensagem e o papel de Lorelai permanecem em aberto. A investigacao continua."),
]
DIALOGUES = {"opening": OPENING, "prologue": PROLOGUE, "epilogue": EPILOGUE}
CHAPTERS = ["O aviso de Redding", "O escritorio de Celine", "A testemunha e as cameras",
            "O codigo que escolhe Cassie", "Mercer House", "O jogo dos Masters", "O nome de Lorelai"]

# Prefixos evitam mudar evidencias dos salvamentos da campanha anterior.
EVIDENCE_DATA = {
    "x_warning": ("Aviso de Redding", "Os Masters escondem uma investigacao dentro de outra. Convites e escolhas podem ser formas de manipulacao."),
    "x_reflection": ("Reflexo no vidro", "No vidro, a mesma pessoa observa a porta durante toda a conversa. Observacao nao prova participacao nos Masters."),
    "x_watch": ("Relogio parado", "O relogio da sala esta parado; seu horario nao pode datar a conversa. E um objeto sem valor cronologico."),
    "x_bracelet": ("Pulseira sobre a mesa", "A pulseira esta sobre a mesa, nao no chao. Nao ha marcas de luta proximas. A posicao parece deliberada."),
    "x_phone": ("Celular desligado", "Desligamento registrado as 20h42. O historico posterior esta vazio; nao houve chamada as 21h."),
    "x_chair": ("Cadeira afastada", "Sem marcas de impacto. A cadeira e compativel com alguem que se levantou normalmente."),
    "x_glass": ("Copo com gelo derretido", "O copo ja estava parcialmente derretido na primeira inspecao. Sua mudanca posterior e compativel com uma ausencia curta, mas o gelo sozinho nao fornece um horario exato."),
    "x_interval": ("Fotos da inspecao", "Foto inicial: mesa sem envelope as 21h03. Foto do retorno: envelope CASSIE as 21h16. Treze minutos, coerentes com a observacao do copo."),
    "x_writing": ("Marcas de escrita", "20:30 - saida pelos fundos. Nao ligar. Deixar o que eles esperam ver."),
    "x_plan": ("Planejamento de saida", "O registro indica intencao de sair discretamente, sem comunicacao. Nao prova coacao; doze minutos ate o desligamento nao anulam o planejamento."),
    "x_agenda": ("Agenda de Celine", "Os compromissos terminam antes das 20h30. Nao ha reuniao posterior. O arquivo tem patrimonio 417."),
    "x_batch": ("Lote de papelaria", "O involucro de manutencao e o envelope usam o lote P17, comprado pelo predio. Papel comum nao identifica autoria."),
    "x_envelope": ("Envelope para Cassie", "O envelope CASSIE apareceu durante a investigacao. Contem 3, 5, 8, 13, ?, 34 e: 'Voce reconhece padroes. Reconhece a propria historia?'"),
    "x_departure": ("Registro da portaria", "Celine saiu pelos fundos as 20h30. O depoente foi registrado no hall as 21h03. Cassie entrou no corredor as 21h16."),
    "x_testimony": ("Alegacao de ligacao", "O depoente afirmou: Celine me ligou as nove. Disse que estava bem."),
    "x_protective": ("Mentira protetora", "O depoente inventou a ligacao porque Celine pediu que nao revelasse sua saida. Nao ha prova de que ele participe dos Masters."),
    "x_backup": ("Copias locais", "As copias sao gravadas em blocos de 21 minutos: 20:21, 20:42, 21:03, 21:24. Cada bloco cobre ate o inicio do seguinte."),
    "x_window": ("Janela de insercao", "Video: pessoa de bone e uniforme entra as 21h09 e sai as 21h14. O envelope foi inserido nessa janela, depois da saida de Celine."),
    "x_pattern": ("Padrao Fibonacci", "3, 5, 8, 13, 21, 34. Cada termo soma os dois anteriores. Quinto - terceiro + quarto + primeiro = 29."),
    "x_address": ("Mercer House", "A transparencia sobre a fotografia revela MERCER HOUSE. O arquivo digital associa Mercer House, 23, a uma investigacao dos Masters."),
    "x_target": ("Mensagem dirigida a Cassie", "O envelope nomeia CASSIE. O compartimento menciona Lorelai e seu passado: 'Ha uma historia sua nesta casa. Lorelai e um nome que voce reconhece.'"),
    "x_team": ("Teste de composicao", "As habilidades de Dean, Michael, Lia e Sloane cercam Cassie, o ALVO. 'Toda equipe tem um ponto que pode ser puxado.'"),
    "x_photo": ("Memoria adulterada", "A fotografia que mostra o celular desligando as 21h00 foi adulterada. O registro original comprova 20h42."),
    "x_below": ("Mensagem por ausencia", "ABAIXO DA CASA, A PRIMEIRA RESPOSTA E SEMPRE A ERRADA. A porta enumera a ordem: A padrao, B cronologia, C deducao."),
    "x_recording": ("Gravacao sem contradicao", "O envelope foi inserido apos a saida de Celine e dirigido a Cassie. A identidade do mensageiro nao esta comprovada."),
    "x_grid": ("Cronologia independente", "Celine sai 20h30; depoente no hall 21h03; mensageiro entra 21h09 e sai 21h14; Cassie entra no corredor 21h16. O rosto do mensageiro permanece desconhecido."),
    "x_verified": ("Fotografias verificadas", "Sao autenticas as fotos do celular as 20h42, da sequencia recuperada com 21 e do corredor as 21h09. No verso: 5, 13, 21. Os versos identificam as fotos, nao sao a referencia de consulta do arquivo."),
    "x_final": ("Deducao final", "Os Masters aproveitaram a investigacao de Celine para alcancar Cassie. Padrao, cronologia e mensagem demonstram planejamento e conhecimento de seu passado, mas nao comprovam quem escreveu a mensagem nem o papel atual de Lorelai."),
}
ITEMS = {
    "clip": ("Clipe metalico", "Solta uma lingueta; nao substitui uma chave."),
    "carbon": ("Folha de carbono", "Pode revelar marcas sob uma pagina iluminada."),
    "key417": ("Chave 417", "Copia da chave de um movel com patrimonio 417."),
    "key471": ("Chave 471", "Copia da chave de um movel com patrimonio 471."),
    "key714": ("Chave 714", "Copia da chave de um movel com patrimonio 714."),
    "badge": ("Cracha antigo", "A tarja magnetica ainda funciona nas fechaduras antigas."),
    "folded_photo": ("Fotografia dobrada", "Placa ao fundo: M A E R C S E R H O U S E. Marcas circulares cercam as letras da placa."),
    "overlay": ("Transparencia", "Janelas circulares numeradas 1, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13. Encaixa nas marcas da fotografia dobrada."),
    "partial_photo": ("Metade de fotografia", "Mostra parte de Mercer House e um relogio marcando 3h21. No verso: 'o horario da fotografia, nao o da chegada'."),
    "magnet": ("Pequeno ima", "Retirado do fecho de uma caixa. Sozinho, nao alcanca a grelha."),
    "strip": ("Tira metalica", "Longa e flexivel; pode sustentar um ima."),
    "magnetic_tool": ("Ferramenta magnetica", "Ima preso a tira metalica. Alcanca objetos em frestas."),
    "hand": ("Ponteiro dos minutos", "Peca recuperada da grelha da cozinha."),
    "brass_key": ("Chave L", "Chave de latao da galeria."),
    "small_key": ("Chave pequena", "Abre o quarto no corredor superior."),
    "punched": ("Cartao perfurado", "Encaixe retangular. Letras so aparecem com luz atraves dos furos."),
}

OBJECTS = {}


def obj(key, label, text, *, items=(), evidence=(), needs=(), use=(), puzzle="", phase=None):
    OBJECTS[key] = dict(label=label, text=text, items=list(items), evidence=list(evidence),
                        needs=list(needs), use=list(use), puzzle=puzzle, phase=phase)
    return key


obj("redding_notes", "Bloco de Redding", "No bloco: duas historias, um mesmo padrao. Redding observa Cassie, nao a porta.", evidence=("x_warning",))
obj("reflection", "Reflexo no vidro", "Uma figura observa o corredor. Nao e possivel identifica-la.", evidence=("x_reflection",))
obj("stopped_watch", "Relogio parado", "Os ponteiros nao se movem. Nao use este horario como registro da conversa.", evidence=("x_watch",))
obj("leave_intro", "Reunir a equipe", "Dean: Celine desapareceu. Vamos registrar o que existe, antes de escolher uma explicacao.", needs=("x_warning", "x_reflection", "stopped_watch"), phase=(1, "reception"))
obj("card_holder", "Porta-cartoes", "Um clipe esta preso sob o porta-cartoes.", items=("clip",))
obj("guest_book", "Livro de visitas", "A equipe registra entrada no escritorio as 21h03. O recepcionista pede que portas de servico permanecam fechadas.")
obj("plant", "Vaso", "Poeira e folhas secas. Nao ha mensagem escondida.")
obj("desk", "Mesa de Celine", "A pulseira esta sobre a mesa. Na primeira foto, nenhum envelope. O bloco parece em branco.", evidence=("x_bracelet",))
obj("phone", "Celular", "O registro do aparelho pode datar uma alegacao de ligacao.", evidence=("x_phone",))
obj("chair", "Cadeira", "A cadeira foi afastada normalmente.", evidence=("x_chair",))
obj("glass", "Copo e fotos de inspecao", "A comparacao do copo ajuda a conferir o intervalo; os horarios exatos vem das fotos, nao do derretimento sozinho.", evidence=("x_glass",))
obj("bin", "Lixeira", "Uma folha de carbono amassada ainda pode ser usada.", items=("carbon",))
obj("lamp", "Luminaria e bloco", "A base inclina. Carbono sob a pagina e luz lateral revelam: 20:30 - saida pelos fundos. Nao ligar. Deixar o que eles esperam ver.", use=("carbon",), evidence=("x_writing",), puzzle="writing")
obj("drawer_cover", "Tampa lateral", "A lingueta cede. Etiqueta: PATRIMONIO 417. Copia da chave - copa.", use=("clip",))
obj("drawer", "Gaveta inferior", "A chave 417 abre sem forcar. Dentro: agenda, cracha e fotografia dobrada.", needs=("drawer_cover",), use=("key417",), items=("badge",), evidence=("x_agenda",))
obj("folded_photo", "Fotografia dobrada", "Uma placa com letras ao fundo pode ser lida com um gabarito. Guarde a fotografia.", needs=("drawer",), items=("folded_photo",))
obj("key_board", "Quadro de chaves", "Tres copias: 417, 471, 714. A etiqueta lateral do arquivo identifica a correta.", items=("key417", "key471", "key714"))
obj("coffee", "Cafeteira", "Cafe frio, sem marcas novas. Um objeto cotidiano, nao uma prova de autoria.")
obj("maintenance_door", "Porta de manutencao", "A tarja do cracha aciona a fechadura antiga.", use=("badge",))
obj("supply", "Carrinho e achados", "No fundo da caixa, um involucro rasgado do lote P17. A marca pode ser comparada ao papel do escritorio.", needs=("maintenance_door",), evidence=("x_batch",))
obj("new_envelope", "Envelope CASSIE", "O envelope nao estava na mesa antes. Agora traz seu nome: 'Voce reconhece padroes. Reconhece a propria historia?'", needs=("supply", "desk"), evidence=("x_envelope", "x_interval"), puzzle="office_conclusion")
obj("witness", "Depoente", "Celine me ligou as nove. Disse que estava bem.", evidence=("x_testimony",), puzzle="witness")
obj("hall_log", "Registro da portaria", "Horarios assinados e sincronizados com as cameras. Nao sao estimativas.", evidence=("x_departure",))
obj("guard", "Seguranca", "O arquivo das 20h as 22h esta corrompido. As copias locais ficam no deposito tecnico; o terminal pode reconstruir um bloco.")
obj("backup_labels", "Etiquetas de manutencao", "O cracha ainda funciona na tarja antiga. Uma etiqueta descreve as copias de 21 minutos.", evidence=("x_backup",))
obj("router", "Roteador e nobreak", "Relogios sincronizados com a portaria. Intervalo fotografado: 21h03 a 21h16. O nobreak preservou a copia local.")
obj("camera", "Terminal de video", "Localize o bloco que cobre toda a ausencia de Cassie. Compare as fotos do copo com os intervalos da copia.", needs=("x_backup", "x_glass", "x_interval", "x_protective", "x_departure"), puzzle="camera")
obj("sequence", "Envelope cifrado", "Tres camadas: sequencia, intruso e chave posicional.", puzzle="sequence")
obj("intruder", "Segunda camada", "Uma intrusao interrompe a progressao.", needs=("sequence",), puzzle="intruder")
obj("positional", "Compartimento lacrado", "No verso: quinto - terceiro + quarto + primeiro.", needs=("intruder",), puzzle="positional")
obj("photo_table", "Mesa de luz", "A fotografia dobrada do arquivo tem marcas compativeis com a transparencia. Ambas precisam estar no inventario.", needs=("overlay", "folded_photo"), use=("overlay", "folded_photo"), puzzle="overlay")
obj("digital", "Arquivo de imoveis", "Resultados: Mercer House, 23; Miller House, 23; Mercer Hall, 13; Meyer House, 21. So Mercer House consta do processo dos Masters. O fragmento informa ...ER HOUSE / 23.", needs=("positional",))
obj("target_board", "Quadro de conexoes", "O envelope explica a saida de Celine ou escolhe uma nova pessoa?", needs=("x_address", "digital"), puzzle="target")
obj("front_garden", "Placa da propriedade", "MERCER HOUSE, 23. A porta principal esta destrancada. O caminho de volta nao parece vigiado, mas a casa espera por alguem.")
obj("box", "Caixa decorativa", "O fecho quebrado contem um pequeno ima.", items=("magnet",))
obj("clock", "Relogio e aparador", "Relogio sem ponteiro dos minutos. A legenda fixa indica 8h13; quatro discos no aparador nao sao um teclado. Uma inscricao pede o horario da fotografia.", use=("hand",), needs=("partial_photo",), puzzle="clock")
obj("shelves", "Lombadas da biblioteca", "A lanterna revela pontos: 3, 5, 8 e 13. Na lateral: 'conte da esquerda; a soma dos dois anteriores indica a proxima posicao'.", puzzle="books")
obj("false_index", "Indice alfabetico", "Um indice falso organiza titulos, mas nenhuma marca coincide com as letras. As posicoes das lombadas, nao os nomes, acionam a estante.")
obj("grate", "Grelha da cozinha", "Um ponteiro caiu alem do alcance. Uma haste magnetica consegue recupera-lo.", use=("magnetic_tool",), items=("hand",))
obj("portraits", "Cinco retratos", "Cartoes: PERFILADOR, EMOCOES, ALVO, MENTIRAS, ESTATISTICA. A legenda permanente liga os retratos a Dean, Michael, Cassie, Lia e Sloane; cartoes soltos contraditorios nao sao registros.", puzzle="gallery")
obj("portrait_notes", "Anotacoes nos retratos", "Gravuras fixas: 1 Dean reconstrui intencoes; 2 Michael observa reacoes; 3 Cassie no centro; 4 Lia confronta falas; 5 Sloane trabalha com numeros. Cartoes soltos dizem: 1 Estatistica, 2 Perfilador, 5 Mentiras. Eles contradizem as gravuras permanentes; nao sao registros confiaveis.")
obj("upper_log", "Corredor superior", "Uma moldura traz a inscricao: 'A memoria tambem pode ser editada. Confie no registro original, nao na imagem mais familiar.'")
obj("altered", "Seis fotografias", "Uma fotografia mudou um horario. Compare as seis legendas com o dossie.", puzzle="altered")
obj("office_light", "Luminaria com encaixe", "O cartao projeta letras dispersas: ABAIXO DA CASA, A PRIMEIRA RESPOSTA E SEMPRE A ERRADA.", use=("punched",), evidence=("x_below",))
obj("lock_a", "Fechadura A", "PAINEL A / PADRAO. Selecione os termos na ordem da sequencia. A placa manda comecar por A.", puzzle="lock_a")
obj("lock_b", "Fechadura B", "PAINEL B / CRONOLOGIA. Saida, desligamento, entrada e saida do mensageiro.", needs=("lock_a",), puzzle="lock_b")
obj("lock_c", "Fechadura C", "PAINEL C / DEDUCAO. Marque a afirmacao falsa, depois dos mecanismos A e B.", needs=("lock_b",), puzzle="lock_c")
obj("hidden_symbol", "Simbolo e gravacoes", "O simbolo dos Masters identifica a sala como um teste preparado. Seis gravacoes aguardam no painel.", needs=("lock_c",), phase=(5, "hidden"))
obj("recordings", "Seis gravacoes", "Regra: A gravacao certa nao mente sobre tempo nem sobre alvo. Confira cada afirmacao nos registros.", needs=("hidden_symbol",), puzzle="recordings")
obj("logic_grid", "Quadro de restricoes", "Nao atribua um rosto ao mensageiro. Portaria e video permitem reconstruir a janela sem identificar a pessoa.", needs=("x_recording",), puzzle="grid")
obj("restrictions", "Restricoes do quadro", "Quem entrou 21h09 nao era Celine. O mensageiro ficou cinco minutos e nao saiu 21h03. O depoente estava no hall antes de 21h09. Cassie entrou depois da entrega. Portaria: Celine 20h30, depoente 21h03, Cassie 21h16.")
obj("terminals", "Terminais da equipe", "Lia, Michael e Sloane deixaram analises. O circuito permite apenas duas consultas diferentes.")
obj("manual", "Manual do painel", "Ordenacao final: o registro do desligamento perde o separador; o termo recuperado permanece; o minuto de entrada conserva dois digitos. Fotografias datadas confirmam os tres dados.")
obj("continue_final", "Camara final", "Cassie segue sem atribuir aos registros uma identidade que eles nao mostram.", needs=("x_grid",), phase=(6, "final_chamber"))
obj("nine_photos", "Nove fotografias", "Escolha somente as imagens verificaveis. Originais do dossie: aparelho 20h42, sequencia com 21, entrada 21h09. Nao use apelo emocional como verificacao.", puzzle="photos")
obj("final_panel", "Catalogo de registros", "Consulte os documentos cruzando o que mudou, o que permaneceu e o que foi acrescentado. Tres campos: horario sem separador, termo, minuto com dois digitos.", needs=("x_verified",), puzzle="final_code")
obj("recovery_one", "Circuito de observacao", "Rota alternativa de manutencao. Primeiro reconstitua os quatro horarios comprovados.", needs=("panel_locked",), puzzle="recovery_one")
obj("recovery_two", "Rele de isolamento", "Depois da cronologia, reproduza os seis termos do padrao para isolar o bloqueio.", needs=("recovery_one",), puzzle="recovery_two")
obj("transmission", "Terminal de transmissao", "Envie a equipe uma conclusao sustentada por tres provas. O nome de Lorelai nao demonstra autoria nem presenca fisica.", needs=("final_code",), puzzle="final_deduction")


def puzzle(title, prompt, kind, answer, *, options=(), needs=(), evidence=(), items=(), phase=None, proofs=(), hint=""):
    return dict(title=title, prompt=prompt, kind=kind, answer=answer, options=list(options),
                needs=list(needs), evidence=list(evidence), items=list(items), phase=phase,
                proofs=list(proofs), hint=hint)


PUZZLES = {
    "writing": puzzle("As marcas de escrita", "20:30 - saida pelos fundos. Nao ligar. Deixar o que eles esperam ver.", "choice", "plan",
        options=[("plan", "Celine planejava sair discretamente."), ("forced", "Celine foi obrigada a escrever."), ("ignore", "Doze minutos de diferenca invalidam o registro.")], evidence=("x_plan",)),
    "office_conclusion": puzzle("Duas historias", "O envelope nao estava na primeira foto. A escrita e anterior a sua chegada. O que pode ser afirmado?", "proof", "later",
        options=[("kidnap", "Celine foi sequestrada; o envelope prova isso."), ("later", "A saida pode ser voluntaria; o envelope e uma intervencao posterior dirigida a Cassie."), ("same", "Celine deixou o envelope durante nossa inspecao.")],
        needs=("x_plan", "x_phone", "x_chair", "x_glass", "x_agenda", "x_batch"), proofs=("x_plan", "x_envelope"), phase=(2, "interview")),
    "witness": puzzle("A primeira mentira", "Depoente: Celine me ligou as nove. Disse que estava bem.", "proof", "contradiction",
        options=[("guilty", "A mentira comprova que ele participa dos Masters."), ("contradiction", "O horario da ligacao contradiz o registro do celular."), ("fear", "O medo confirma um sequestro.")],
        proofs=("x_phone", "x_testimony"), evidence=("x_protective",)),
    "camera": puzzle("Reconstruir a copia", "Qual bloco cobre a ausencia fotografada de 21h03 a 21h16? Blocos de 21 minutos: 20:21, 20:42, 21:03, 21:24. Digite HHMM.", "code", "2103",
        evidence=("x_window",), phase=(3, "lab")),
    "sequence": puzzle("Sequencia incompleta", "3, 5, 8, 13, ?, 34. Cada termo depende dos dois anteriores.", "code", "21", hint="Sloane: Cada numero conversa com os dois anteriores."),
    "intruder": puzzle("Termo intruso", "8, 13, 21, 30, 34, 55. Qual termo interrompe a soma dos dois anteriores?", "code", "30"),
    "positional": puzzle("Chave posicional", "3, 5, 8, 13, 21, 34. Quinto - terceiro + quarto + primeiro.", "code", "29", evidence=("x_pattern", "x_target"), items=("overlay", "partial_photo")),
    "overlay": puzzle("Letras na transparencia", "Placa: M A E R C S E R H O U S E. Janelas: 1,3,4,5,7,8,9,10,11,12,13. O fragmento diz ...ER HOUSE / 23. Qual propriedade?", "choice", "mercer",
        options=[("miller", "Miller House"), ("meyer", "Meyer House"), ("mercer", "Mercer House"), ("hall", "Mercer Hall")], evidence=("x_address",)),
    "target": puzzle("O codigo escolhe alguem", "Cruze a mensagem nominal e o endereco confirmado, sem supor onde Celine esta.", "proof", "cassie",
        options=[("celine", "Mercer House comprova o paradeiro de Celine."), ("cassie", "A investigacao paralela conduz Cassie ao proprio passado."), ("lorelai", "Lorelai escreveu pessoalmente o convite.")],
        proofs=("x_address", "x_target"), phase=(4, "garden")),
    "books": puzzle("O indice falso", "As marcas indicam posicoes a partir da esquerda: 3, 5, 8, 13. Puxe nessa ordem.", "order", ["3", "5", "8", "13"],
        options=[(str(n), f"Livro {n}") for n in (13, 4, 8, 3, 5, 12)], items=("strip",)),
    "clock": puzzle("Memoria do relogio", "O mecanismo pede o horario preservado na fotografia parcial, nao a legenda fixa do vestibulo. Formato HHMM.", "code", "0321", items=("brass_key",)),
    "gallery": puzzle("Verdade mentira e ordem", "Atribua os cartoes aos retratos da esquerda para a direita. Legendas fixas: Dean, Michael, Cassie, Lia, Sloane. O ALVO fica no centro.", "grid", ["perfil", "emocao", "alvo", "mentira", "estatistica"],
        options=[("alvo", "ALVO"), ("estatistica", "ESTATISTICA"), ("mentira", "MENTIRAS"), ("perfil", "PERFILADOR"), ("emocao", "EMOCOES")], items=("small_key",), evidence=("x_team",)),
    "altered": puzzle("Memoria imperfeita", "Qual foto contradiz os registros originais? Identifique a adulteracao.", "choice", "phone",
        options=[("bracelet", "Pulseira sobre a mesa"), ("phone", "Celular desligado as 21h00"), ("chair", "Cadeira afastada sem impacto"), ("plate", "Placa Mercer House 23"), ("video", "Mensageiro entrando 21h09"), ("pattern", "Sequencia com termo 21")],
        items=("punched",), evidence=("x_photo",)),
    "lock_a": puzzle("Fechadura A", "Selecione a sequencia crescente de soma dos dois anteriores, comecando em 3 e 5.", "order", ["3", "5", "8", "13", "21", "34"], options=[(str(n), str(n)) for n in (34, 8, 30, 5, 13, 3, 21, 18)]),
    "lock_b": puzzle("Fechadura B", "Ordene: saida de Celine, desligamento, entrada e saida do mensageiro.", "order", ["2030", "2042", "2109", "2114"], options=[("2114", "21h14"), ("2042", "20h42"), ("2109", "21h09"), ("2030", "20h30")]),
    "lock_c": puzzle("Fechadura C", "Qual afirmacao e falsa diante dos registros?", "choice", "author",
        options=[("before", "Celine saiu antes do envelope."), ("during", "O envelope surgiu durante a investigacao."), ("author", "Celine deixou o codigo para Cassie.")]),
    "recordings": puzzle("Seis gravacoes", "A gravacao certa nao mente sobre tempo nem sobre alvo. Selecione a unica dupla sustentada pelo dossie.", "choice", "4",
        options=[("1", "1 | Celine saiu 20h30; o envelope estava na mesa 20h42."), ("2", "2 | O envelope nomeia Cassie; Celine estava no predio 21h09."), ("3", "3 | O mensageiro saiu 21h14; o envelope nomeia apenas Celine."), ("4", "4 | O envelope e posterior a saida de Celine; sua destinataria e Cassie."), ("5", "5 | O celular desligou 20h42; o mensageiro saiu 21h03."), ("6", "6 | O padrao repete Fibonacci; o envelope foi encontrado antes de 20h30.")], evidence=("x_recording",)),
    "grid": puzzle("Quadro de restricoes", "Associe os quatro registros: Celine / saida; depoente / hall; mensageiro / entrada; Cassie / corredor. O mensageiro saiu cinco minutos depois de entrar. Seu rosto e desconhecido.", "grid", ["2030", "2103", "2109", "2116"],
        options=[("2116", "21h16"), ("2109", "21h09"), ("2030", "20h30"), ("2103", "21h03")], evidence=("x_grid",)),
    "photos": puzzle("Nove fotografias", "Selecione as tres imagens verificaveis pelo dossie. As restantes sao alteradas ou alheias ao caso.", "set", ["phone", "sequence", "corridor"],
        options=[("phone", "Celular / 20h42 / escritorio"), ("fake_phone", "Celular / 21h00 / escritorio"), ("holiday", "Praia sem data"), ("sequence", "Convite / termo recuperado 21"), ("fake_seq", "Convite / termo recuperado 30"), ("garden", "Jardim de outra propriedade"), ("corridor", "Corredor / entrada 21h09"), ("fake_video", "Corredor / entrada 20h09"), ("portrait", "Retrato sem local ou data")], evidence=("x_verified",)),
    "final_code": puzzle("Consulta cruzada", "Localize o registro: horario do desligamento, termo recuperado e minuto de entrada do mensageiro.", "code", "2042 21 09"),
    "recovery_one": puzzle("Circuito de observacao", "Reconstrua a cronologia para desviar o circuito bloqueado.", "order", ["2030", "2042", "2109", "2114"], options=[("2109", "21h09"), ("2030", "20h30"), ("2114", "21h14"), ("2042", "20h42")]),
    "recovery_two": puzzle("Rele de isolamento", "O circuito reserva pede a sequencia completa em ordem.", "order", ["3", "5", "8", "13", "21", "34"], options=[(str(n), str(n)) for n in (21, 5, 34, 8, 3, 13)]),
    "final_deduction": puzzle("A deducao decisiva", "Selecione a conclusao sustentada e anexe as tres provas minimas. Saber sobre Lorelai nao prova autoria.", "proof", "parallel",
        options=[("lorelai", "Lorelai escreveu o envelope e conduz os Masters."), ("kidnap", "Celine foi sequestrada pelos Masters para atrair Cassie."), ("parallel", "Os Masters usaram a investigacao de Celine e informacoes sobre Lorelai para conduzir Cassie a Mercer House.")],
        proofs=("x_window", "x_pattern", "x_target"), evidence=("x_final",), phase=(7, "final_chamber")),
}
GRID_ROWS = {"gallery": ["Dean", "Michael", "Cassie", "Lia", "Sloane"],
             "grid": ["Celine / saida", "Depoente / hall", "Mensageiro / entrada", "Cassie / corredor"]}

ROOMS = {}


def room(key, title, phase, background, objects, needs=()):
    ROOMS[key] = dict(title=title, phase=phase, background=background, objects=objects.split(), needs=list(needs))


room("intro", "Sala de entrevistas", 0, "entrevista", "redding_notes reflection stopped_watch leave_intro")
room("reception", "Recepcao", 1, "escritorio", "card_holder guest_book plant")
room("office", "Escritorio principal", 1, "escritorio", "desk phone chair glass bin lamp new_envelope")
room("archive", "Arquivo lateral", 1, "arquivo", "drawer_cover drawer folded_photo")
room("service", "Corredor de servico", 1, "arquivo", "maintenance_door supply")
room("pantry", "Copa", 1, "escritorio", "key_board coffee")
room("interview", "Sala de entrevistas", 2, "entrevista", "witness")
room("hall", "Hall do edificio", 2, "escritorio", "hall_log")
room("security", "Sala de seguranca", 2, "analise", "guard camera")
room("technical", "Deposito tecnico", 2, "arquivo", "backup_labels router", ("badge",))
room("lab", "Laboratorio de Sloane", 3, "analise", "sequence intruder positional")
room("digital", "Arquivo digital", 3, "analise", "digital")
room("evidence", "Sala de evidencias", 3, "arquivo", "photo_table")
room("connections", "Quadro de conexoes", 3, "arquivo", "target_board")
room("garden", "Jardim frontal", 4, "masters", "front_garden")
room("vestibule", "Vestibulo", 4, "masters", "box clock")
room("library", "Biblioteca", 4, "arquivo", "shelves false_index")
room("kitchen", "Cozinha", 4, "escritorio", "grate")
room("gallery", "Galeria", 4, "masters", "portraits portrait_notes", ("brass_key",))
room("upper", "Corredor superior", 4, "masters", "upper_log")
room("bedroom", "Quarto fechado", 4, "masters", "altered", ("small_key",))
room("house_office", "Escritorio terreo", 4, "escritorio", "office_light")
room("basement", "Porao", 4, "masters", "lock_a lock_b lock_c", ("x_below",))
room("hidden", "Sala oculta", 4, "masters", "hidden_symbol recordings", ("lock_c",))
room("observation", "Corredor de observacao", 5, "masters", "restrictions manual recovery_one recovery_two")
room("recording", "Camara de gravacao", 5, "analise", "logic_grid terminals continue_final")
room("final_chamber", "Camara final", 6, "masters", "manual")
room("photo_archive", "Arquivo de fotografias", 6, "arquivo", "nine_photos")
room("exit", "Catalogo documental", 6, "analise", "final_panel")
room("transmission", "Terminal de transmissao", 6, "analise", "transmission")

OBJECTIVES = [
    "Examinar a sala e registrar o aviso antes de reunir a equipe.",
    "Reconstituir a saida de Celine e investigar o envelope que apareceu depois.",
    "Confrontar a testemunha e recuperar a janela de insercao nas cameras.",
    "Abrir o envelope, combinar as fotografias e confirmar o destino.",
    "Explorar Mercer House e abrir os tres mecanismos do porao.",
    "Verificar as gravacoes e reconstruir a cronologia sem inventar identidades.",
    "Validar fotografias, consultar os documentos e sustentar a deducao final.",
]

HOTSPOT_POSITIONS = {
    "desk": (553, 311), "phone": (1040, 393), "chair": (554, 416),
    "glass": (685, 307), "bin": (399, 399), "lamp": (478, 224), "new_envelope": (610, 305),
    "redding_notes": (554, 327), "reflection": (710, 170), "stopped_watch": (979, 145),
    "leave_intro": (254, 385), "shelves": (207, 259), "false_index": (497, 311),
}

# Each entry is a place to visit and an object to investigate, never an answer.
GUIDED_STEPS = [
    [("intro", key) for key in ("redding_notes", "reflection", "stopped_watch", "leave_intro")],
    [("reception", "card_holder"), ("reception", "guest_book"),
     *[("office", key) for key in ("desk", "phone", "chair", "glass", "bin", "lamp")],
     ("archive", "drawer_cover"), ("pantry", "key_board"), ("archive", "drawer"),
     ("archive", "folded_photo"), ("service", "maintenance_door"), ("service", "supply"),
     ("office", "new_envelope")],
    [("interview", "witness"), ("hall", "hall_log"), ("security", "guard"),
     ("technical", "backup_labels"), ("technical", "router"), ("security", "camera")],
    [("lab", "sequence"), ("lab", "intruder"), ("lab", "positional"),
     ("archive", "folded_photo"), ("evidence", "photo_table"),
     ("digital", "digital"), ("connections", "target_board")],
    [("garden", "front_garden"), ("vestibule", "box"), ("library", "shelves"),
     ("kitchen", "magnetic_tool"), ("kitchen", "grate"), ("vestibule", "clock"),
     ("gallery", "portrait_notes"), ("gallery", "portraits"), ("upper", "upper_log"),
     ("bedroom", "altered"), ("house_office", "office_light"),
     ("basement", "lock_a"), ("basement", "lock_b"), ("basement", "lock_c"),
     ("hidden", "hidden_symbol")],
    [("hidden", "recordings"), ("observation", "restrictions"),
     ("recording", "logic_grid"), ("recording", "continue_final")],
    [("final_chamber", "manual"), ("photo_archive", "nine_photos"),
     ("exit", "final_panel"), ("transmission", "transmission")],
]

PROOF_OPTIONS = {
    "office_conclusion": ["x_plan", "x_phone", "x_chair", "x_envelope"],
    "witness": ["x_phone", "x_testimony", "x_chair", "x_glass"],
    "target": ["x_address", "x_phone", "x_target", "x_agenda"],
    "final_deduction": ["x_window", "x_pattern", "x_target", "x_phone", "x_chair", "x_agenda"],
}

PUZZLE_HINTS = {
    "writing": ("Observe os verbos do bilhete: sair, nao ligar e deixar.", "O bilhete descreve preparativos. Nao ha nele uma ordem de um agressor."),
    "office_conclusion": ("Separe duas perguntas: como Celine saiu e quando o envelope apareceu.", "Compare o plano escrito com o envelope ausente da primeira foto. Sao duas provas diferentes."),
    "witness": ("Compare o horario da ligacao com o estado do celular.", "Um aparelho desligado as 20h42 nao sustenta a ligacao alegada para as 21h. Anexe os dois registros."),
    "camera": ("Procure um bloco que comece antes ou junto da primeira foto e termine depois da segunda.", "A ausencia vai de 21h03 a 21h16. Some 21 minutos a cada inicio de bloco e confira qual cobre todo o intervalo."),
    "sequence": ("O numero seguinte vem da soma dos dois anteriores.", "Para preencher o espaco depois de 13, some 8 e 13."),
    "intruder": ("Confira cada termo somando os dois numeros anteriores.", "Depois de 13 e 21 deveria vir 34. Procure o numero que foi inserido entre 21 e 34."),
    "positional": ("Quinto, terceiro, quarto e primeiro indicam posicoes, nao os numeros 5, 3, 4 e 1.", "Substitua as posicoes pelos valores: 21 - 8 + 13 + 3."),
    "overlay": ("Conte as letras da placa a partir de 1. Leia somente as janelas indicadas.", "As janelas descartam a segunda e a sexta letras. Junte as demais e compare com as propriedades."),
    "target": ("A mensagem nomeia uma pessoa. O endereco revela para onde essa pessoa esta sendo conduzida.", "Nao ha prova do paradeiro de Celine nem da autoria de Lorelai. Compare o endereco com a mensagem dirigida a Cassie."),
    "books": ("Os numeros indicam posicoes dos livros, nao a ordem alfabetica dos titulos.", "Reproduza as quatro posicoes marcadas, da menor para a maior. Ignore os livros 4 e 12."),
    "clock": ("A legenda fixa do relogio e uma distracao. O horario confiavel esta na fotografia parcial.", "A fotografia mostra 3h21. O campo pede quatro algarismos, incluindo o zero inicial."),
    "gallery": ("Use as especialidades da equipe e as legendas permanentes. Os cartoes soltos sao falsos.", "Dean analisa perfis; Michael, emocoes; Lia, mentiras; Sloane, numeros. Cassie ocupa o centro do teste."),
    "altered": ("Compare os horarios das fotos com os registros que voce ja recolheu.", "O celular foi desligado as 20h42. Uma legenda mostra um horario diferente para esse mesmo fato."),
    "lock_a": ("Comece pelos dois termos dados: 3 e 5.", "Some os dois ultimos termos a cada passo. A sequencia tem seis numeros; 18 e 30 nao pertencem a ela."),
    "lock_b": ("Organize os acontecimentos do mais antigo ao mais recente.", "Primeiro Celine sai, depois o celular desliga. So depois o mensageiro entra e sai."),
    "lock_c": ("Desta vez, procure a frase falsa, nao a verdadeira.", "O envelope surgiu depois da saida de Celine. Isso nao permite atribuir o codigo a ela."),
    "recordings": ("Cada gravacao contem duas afirmacoes. As duas precisam estar corretas.", "O envelope apareceu depois da saida de Celine e traz o nome de Cassie. Procure a dupla que respeita esses dois fatos."),
    "grid": ("Use a portaria para Celine, o depoente e Cassie. Use o video para o mensageiro.", "Portaria: Celine 20h30, depoente 21h03, Cassie 21h16. O mensageiro entrou cinco minutos antes de sair as 21h14."),
    "photos": ("Escolha tres fotos ligadas aos registros originais, nao as imagens sem data ou local.", "Compare o horario do celular, o termo recuperado do convite e o horario de entrada no corredor."),
    "final_code": ("Os tres campos usam dados ja confirmados: celular, sequencia e entrada do mensageiro.", "Retire o separador de 20h42; mantenha o termo recuperado 21; de 21h09 use apenas o minuto, com dois digitos."),
    "recovery_one": ("A rota alternativa usa os mesmos quatro acontecimentos comprovados.", "Coloque a saida de Celine antes do desligamento, seguido da entrada e da saida do mensageiro."),
    "recovery_two": ("O circuito reserva repete o padrao de soma dos dois anteriores.", "Comece com 3 e 5. Continue somando ate usar os seis termos."),
    "final_deduction": ("Separe o que os registros mostram daquilo que voce apenas suspeita sobre Lorelai.", "A entrega ocorreu durante a investigacao. O padrao e a mensagem ligam o teste a Cassie. Use essas tres provas, sem atribuir autoria a Lorelai."),
}
