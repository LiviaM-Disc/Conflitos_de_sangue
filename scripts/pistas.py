from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    id: str
    name: str
    description: str
    kind: str
    phase: str
    points: int = 0
    essential: bool = False
    ability: str | None = None


EVIDENCES: dict[str, Evidence] = {
    "redding_warning": Evidence(
        id="redding_warning",
        name="Aviso de Redding",
        description=(
            "Daniel Redding sugere que os Masters nao atacam por acaso. "
            "Eles testam padroes, vinculos e medo."
        ),
        kind="dialogo",
        phase="prologo",
        points=10,
        essential=True,
        ability="Cassie",
    ),
    "celine_bracelet": Evidence(
        id="celine_bracelet",
        name="Pulseira de Celine",
        description=(
            "A pulseira foi deixada perto da saida, mas nao ha sinais de luta. "
            "Parece mais uma mensagem do que uma perda acidental."
        ),
        kind="pista essencial",
        phase="fase1",
        points=10,
        essential=True,
    ),
    "broken_phone": Evidence(
        id="broken_phone",
        name="Celular sem sinal",
        description=(
            "O registro mostra que o celular foi desligado as 20h42. "
            "Depois disso, nao houve chamadas originadas pelo aparelho."
        ),
        kind="pista essencial",
        phase="fase1",
        points=10,
        essential=True,
    ),
    "coded_invitation": Evidence(
        id="coded_invitation",
        name="Convite cifrado",
        description=(
            "Um convite sem remetente traz numeros separados por manchas de tinta: "
            "3, 5, 8, 13, ?, 34."
        ),
        kind="codigo",
        phase="fase1",
        points=10,
        essential=True,
        ability="Sloane",
    ),
    "dusty_book": Evidence(
        id="dusty_book",
        name="Livro deslocado",
        description=(
            "O livro foi movido recentemente, mas so esconde poeira e um marcador antigo. "
            "Pode ser ruido da cena."
        ),
        kind="objeto irrelevante",
        phase="fase1",
        points=0,
    ),
    "window_mark": Evidence(
        id="window_mark",
        name="Marca na janela",
        description=(
            "Ha uma marca fina no vidro. Ela indica observacao externa, nao entrada forcada."
        ),
        kind="pista complementar",
        phase="fase1",
        points=5,
    ),
    "lia_lie": Evidence(
        id="lia_lie",
        name="Mentira sobre o horario",
        description=(
            "O relato de uma ligacao as 21h contradiz o registro do aparelho, desligado as 20h42."
        ),
        kind="contradicao",
        phase="fase2",
        points=15,
        essential=True,
        ability="Lia",
    ),
    "michael_emotion": Evidence(
        id="michael_emotion",
        name="Medo antes da culpa",
        description=(
            "Michael nota medo real quando os Masters sao citados. A mentira protege algo, "
            "mas nao prova autoria."
        ),
        kind="emocao",
        phase="fase2",
        points=10,
        ability="Michael",
    ),
    "fibonacci_key": Evidence(
        id="fibonacci_key",
        name="Chave Fibonacci",
        description=(
            "Sloane reconhece que os numeros obedecem a uma soma progressiva: "
            "3, 5, 8, 13, 21, 34. A chave 29 revela uma mensagem pedindo que Cassie venha sozinha."
        ),
        kind="padrao",
        phase="fase3",
        points=20,
        essential=True,
        ability="Sloane",
    ),
    "profile_sequence": Evidence(
        id="profile_sequence",
        name="Sequencia reconstruida",
        description=(
            "A vitima recebeu a isca, perdeu comunicacao, foi observada e a equipe caiu "
            "em uma armadilha planejada."
        ),
        kind="perfilacao",
        phase="fase4",
        points=20,
        essential=True,
        ability="Cassie e Dean",
    ),
    "final_deduction": Evidence(
        id="final_deduction",
        name="Deducao final",
        description=(
            "Celine foi usada como isca para aproximar Cassie dos Masters e das respostas "
            "sobre Lorelai."
        ),
        kind="deducao",
        phase="fase5",
        points=20,
        essential=True,
        ability="Cassie",
    ),
    "invitation_delivery": Evidence(
        "invitation_delivery", "Entrega do envelope",
        "O depoente admite ter entregado o convite a pedido de um desconhecido.",
        "depoimento", "fase2", 10,
    ),
    "witness_pressure": Evidence(
        "witness_pressure", "Ameaca apos a entrega",
        "O depoente relata uma ameaca posterior a entrega. A mentira nao demonstra autoria do desaparecimento.",
        "depoimento", "fase2", 10,
    ),
    "locked_exit": Evidence(
        "locked_exit", "Saida bloqueada",
        "A porta foi trancada por fora, embora o bilhete prometa que a saida estaria livre.",
        "observacao", "fase5", 10, True,
    ),
    "lorelai_note": Evidence(
        "lorelai_note", "Bilhete no retrato",
        "Atras do retrato: 'Cassie, as respostas sobre Lorelai estao aqui. A saida esta livre.'",
        "mensagem", "fase5", 10, True,
    ),
    "hall_pattern": Evidence(
        "hall_pattern", "Marcas no mosaico",
        "As marcas 3, 5, 8, 13, 21 e 34 repetem o padrao do convite encontrado no escritorio.",
        "padrao", "fase5", 10, True,
    ),
}


PHASE1_REQUIRED = {"celine_bracelet", "broken_phone", "coded_invitation"}
FINAL_REQUIRED = {"locked_exit", "lorelai_note", "hall_pattern"}
