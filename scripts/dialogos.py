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

INTERROGATION_STATEMENTS = [
    "Suspeito: Eu vi Celine sair as 21h. Estava tudo normal.",
    "Lia: Essa frase esta limpa demais. Ele treinou a resposta.",
    "Michael: Quando voce menciona Masters, o medo aparece antes da culpa.",
]

INTERROGATION_CHOICES = [
    (
        "A mentira esta no horario. O celular ja estava sem sinal antes disso.",
        True,
    ),
    (
        "A mentira prova que ele sequestrou Celine sozinho.",
        False,
    ),
    (
        "Nao ha contradicao suficiente para confrontar.",
        False,
    ),
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

PROFILE_EVENTS = [
    "Celine recebe um convite sem remetente.",
    "O celular perde sinal antes da ultima mensagem.",
    "A equipe percebe que tambem esta sendo observada.",
    "A investigacao leva Cassie para uma armadilha.",
]

PROFILE_CORRECT_ORDER = [0, 1, 2, 3]
