PROLOGUE_LINES = [
    (
        "Daniel Redding",
        "Voce acha que esta olhando para uma pessoa, Cassie. Os Masters querem que voce olhe para um padrao.",
    ),
    (
        "Cassie",
        "Padroes deixam rastros. Pessoas tambem.",
    ),
    (
        "Daniel Redding",
        "Entao observe o que eles escolhem esconder. E, principalmente, quem eles escolhem manter por perto.",
    ),
]

PROLOGUE_CHOICES = [
    (
        "Pressionar Redding sobre os Masters",
        "redding_warning",
        "Redding sorri pouco. O aviso fica registrado como evidencia.",
    ),
    (
        "Encerrar a conversa sem insistir",
        None,
        "A conversa termina, mas Cassie sente que deixou uma pista escapar.",
    ),
]

INTERROGATION_ROUNDS = [
    {
        "title": "A ultima ligacao",
        "statement": "Depoente: Celine me ligou do celular dela as 21h. Parecia tranquila.",
        "lia": "Lia: ele hesita antes de dizer o horario, mas repete o resto sem dificuldade.",
        "michael": "Michael: a pergunta sobre o telefone provoca receio, nao surpresa.",
        "choices": [
            ("A ligacao contradiz o registro: o celular foi desligado as 20h42.", True),
            ("Dizer que ela estava tranquila prova que ele planejou o desaparecimento.", False),
            ("A pulseira confirma que Celine fez essa ligacao.", False),
        ],
        "evidence": "lia_lie",
        "uses": ("broken_phone",),
        "feedback": "O registro do aparelho contradiz o relato. Ele admite ter inventado a ligacao para evitar perguntas.",
    },
    {
        "title": "O convite",
        "statement": "Depoente: Eu so ouvi falar desse convite depois que voces chegaram.",
        "lia": "Lia: ele evita a palavra 'receber'. Ha algo omitido sobre o convite.",
        "michael": "Michael: quando voce mostra o papel, a tensao diminui. Ele ja conhecia o objeto.",
        "choices": [
            ("Um convite sem remetente prova que Celine fugiu por vontade propria.", False),
            ("A ausencia de remetente torna o papel irrelevante para o caso.", False),
            ("Pedir que explique como o convite chegou, sem acusa-lo do desaparecimento.", True),
        ],
        "evidence": "invitation_delivery",
        "uses": ("coded_invitation",),
        "feedback": "Ele admite que entregou o envelope a pedido de um desconhecido. A entrega foi dirigida, nao casual.",
    },
    {
        "title": "O nome que assusta",
        "statement": "Depoente: Nao tenho medo dos Masters. So quero ir embora.",
        "lia": "Lia: a negacao do medo nao combina com o restante da fala.",
        "michael": "Michael: ha medo real quando o nome aparece. Medo nao identifica um culpado.",
        "choices": [
            ("Se ele sente medo, entao e o responsavel por tudo.", False),
            ("Investigar a pressao que sofreu e registrar a ligacao com o envelope.", True),
            ("Descartar tudo o que disse, inclusive os fatos que podemos verificar.", False),
        ],
        "evidence": "witness_pressure",
        "uses": ("coded_invitation",),
        "feedback": "O depoente relata uma ameaca depois da entrega. A mentira encobria medo; a autoria ainda exige provas.",
    },
]

PUZZLE_ROUNDS = [
    {"title": "O numero ausente", "values": ("3", "5", "8", "13", "?", "34"),
     "prompt": "Que numero completa a sequencia?", "choices": (18, 21, 26), "answer": 21,
     "hint": "Sloane: compare cada termo com os dois imediatamente anteriores."},
    {"title": "A quebra do padrao", "values": ("8", "13", "21", "30", "34", "55"),
     "prompt": "Qual numero nao pertence a esta sequencia?", "choices": (21, 30, 55), "answer": 30,
     "hint": "Sloane: uma intrusao pode ser retirada sem quebrar a regra dos demais termos."},
    {"title": "A chave do envelope", "values": ("3", "5", "8", "13", "21", "34"),
     "prompt": "No verso: 'Terceiro + quinto'. Qual e a chave numerica?", "choices": (26, 24, 29), "answer": 29,
     "hint": "Sloane: terceiro e quinto indicam posicoes na sequencia, nao os numeros 3 e 5."},
]

FINAL_CHOICES = [
    (
        "Celine foi usada como isca para aproximar Cassie dos Masters e de Lorelai.",
        True,
    ),
    (
        "O caso nao tem relacao com Cassie; os Masters queriam apenas assustar Celine.",
        False,
    ),
    (
        "Daniel Redding manipulou todas as pistas para esconder Sloane.",
        False,
    ),
]

FINAL_ROUNDS = [
    {
        "title": "Uma saida livre?",
        "prompt": "O bilhete promete uma saida livre. A porta foi trancada por fora. Qual leitura resiste as pistas?",
        "hint": "Cassie: uma promessa pode ser parte da isca. Preciso compara-la ao que encontrei.",
        "choices": [
            ("O bilhete basta para provar que Celine veio por vontade propria.", False),
            ("A porta contradiz o bilhete: a aparencia de escolha faz parte da armadilha.", True),
            ("A tranca prova que Daniel esteve pessoalmente neste salao.", False),
        ],
        "uses": ("locked_exit", "lorelai_note"),
        "feedback": "A promessa de liberdade nao combina com a saida bloqueada. O ambiente foi preparado para conduzir alguem.",
    },
    {
        "title": "O alvo da mensagem",
        "prompt": "O mesmo padrao do convite reaparece no salao. O bilhete cita Lorelai e se dirige a Cassie. Quem era o alvo?",
        "hint": "Cassie: a sequencia liga os lugares; o nome no bilhete liga o caso ao meu passado.",
        "choices": FINAL_CHOICES,
        "uses": ("hall_pattern", "lorelai_note", "fibonacci_key"),
        "feedback": "Celine foi usada como isca. Os Masters conduziram Cassie a uma investigacao ligada a Lorelai e ao seu passado.",
    },
]

PROFILE_EVIDENCES = ("broken_phone", "coded_invitation", "celine_bracelet", "fibonacci_key")
PROFILE_PAIR = frozenset(("coded_invitation", "fibonacci_key"))

PROFILE_EVENTS = [
    "Celine recebe um convite sem remetente.",
    "O celular perde sinal antes da ultima mensagem.",
    "A equipe percebe que tambem esta sendo observada.",
    "A investigacao leva Cassie para uma armadilha.",
]

PROFILE_CORRECT_ORDER = [0, 1, 2, 3]
