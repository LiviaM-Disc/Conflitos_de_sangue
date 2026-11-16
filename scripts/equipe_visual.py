"""Short, playable investigations for the Naturals; plain Pygame cards."""
import pygame

from scripts.interfaces import TEXT, MUTED, GOOD
from scripts.personagens import CHARACTERS
from scripts.roteiro_expandido import TEAM_PROFILES


def task(actor, title, prompt, kind, references, cards, answer, hint):
    return dict(actor=actor, title=title, prompt=prompt, kind=kind,
                references=references, cards=cards, answer=answer, hint=hint)


# Every answer is supported by the records displayed on the same screen.
TEAM_TASKS = {
    1: [task("cassie", "Reconstruir os registros da gaveta", "Coloque os acontecimentos do primeiro ao ultimo.", "order",
             [("paper", "Agenda de Celine", "Saida marcada: 20:30"), ("phone", "Registro do celular", "Desligado: 20:42"), ("new_envelope", "Inspecao de Cassie", "Envelope achado: 21:16")],
             [("new_envelope", "Envelope", "Encontrado por Cassie"), ("key417", "Saida marcada", "Anotada na agenda"), ("phone", "Celular desligado", "Registrado no aparelho")],
             [1, 2, 0], "Use agenda, celular e horario da descoberta. As cameras ainda estao sem energia.")],
    2: [task("lia", "Conferir o relato do porteiro", "Qual fala do porteiro contradiz o historico do celular?", "choose",
             [("phone", "Celular da gaveta", "Sem chamadas apos 20:42")],
             [("phone", "Ligacao as 21h", "Ela me ligou as nove."), ("key417", "Saida as 20:30", "Eu a vi sair."), ("camera", "Visita as 21:09", "Alguem entrou depois.")],
             [0], "O historico nao tem chamadas depois das 20:42; a ligacao das 21h nao consta."),
        task("lia", "Checar a segunda versao", "Qual fala nao combina com a camera?", "choose",
             [("camera", "Entrega no escritorio", "Envelope deixado: 21:09"), ("clock", "Saida no video", "Mensageiro: 21:14"), ("key417", "Celine no video", "Saida confirmada: 20:30")],
             [("clock", "Cinco minutos", "A visita durou 5 min."), ("camera", "Antes das 21h", "Ninguem entrou apos 21h."), ("key417", "Depois de Celine", "Ela ja tinha saido.")],
             [1], "A camera registrou uma entrada depois das 21h.")],
    3: [task("dean", "Entender o convite", "Marque DUAS pistas de que querem levar Cassie a essa casa.", "select",
             [("new_envelope", "Destinataria", "O envelope diz CASSIE"), ("photo", "Fotografia", "Mercer House marcada")],
             [("new_envelope", "Nome de Cassie", "Mensagem pessoal"), ("dust", "Poeira", "Casa antiga"), ("photo", "Destino marcado", "Foto da propriedade"), ("lamp", "Luz acesa", "Comodo iluminado")],
             [0, 2], "Procure a destinataria e o local escolhido; poeira nao indica intencao.")],
    4: [task("michael", "Conversar com a zeladora", "A zeladora treme ao ouvir o audio. Como abrir a conversa?", "choose",
             [("witness", "Zeladora da casa", "Recua ao ouvir o audio")],
             [("lock_a", "Pressionar", "Exigir uma confissao"), ("phone", "Dar espaco", "Oferecer uma pausa"), ("new_envelope", "Acusar", "Medo significa culpa")],
             [1], "O medo pede cuidado. Uma reacao nao demonstra culpa."),
        task("michael", "Localizar o relogio citado", "Ela se acalma. Que pergunta ajuda a seguir a pista do audio?", "choose",
             [("recorder", "Trecho recuperado", "Lorelai / relogio / porao")],
             [("new_envelope", "Quem e culpado?", "Exigir um nome"), ("clock", "Encerrar", "Ignorar a gravacao"), ("clock", "Qual relogio?", "Pedir que mostre o local")],
             [2], "A zeladora conhece a casa. Pergunte onde fica o relogio citado.")],
    5: [task("sloane", "Abrir o fecho do porao", "Complete a primeira metade do codigo da porta.", "choose",
             [("lock_a", "Cartao do relogio / faixa 1", "3  /  6  /  9  /  ?")],
             [("paper", "10", ""), ("paper", "12", ""), ("paper", "18", "")], [1], "Cada numero aumenta em 3."),
        task("sloane", "Completar o codigo da porta", "O primeiro valor e 12. Encontre o segundo para abrir o porao.", "choose",
             [("lock_b", "Cartao do relogio / faixa 2", "2  /  4  /  8  /  ?")],
             [("paper", "10", ""), ("paper", "12", ""), ("paper", "16", "")], [2], "Cada numero e o dobro do anterior.")],
    6: [task("dean", "O que o sistema protege?", "Marque DUAS pistas de planejamento contra a equipe.", "select",
             [("recordings", "Arquivo protegido", "Perfis + testes feitos sob medida")],
             [("recordings", "Perfis dos cinco", "Habilidades registradas"), ("lamp", "Lampada antiga", "Objeto comum"), ("lock_a", "Testes pessoais", "Usam essas habilidades"), ("dust", "Poeira no porao", "Sem relacao com a equipe")],
             [0, 2], "Relacione os perfis guardados com os desafios preparados."),
        task("sloane", "Preparar a fila de copia", "O indice pede o menor lote primeiro. Ordene a transferencia.", "order",
             [("recordings", "Indice de exportacao", "Comecar pelo menor lote")],
             [("recordings", "Lote C", "32 registros"), ("recordings", "Lote A", "8 registros"), ("recordings", "Lote B", "16 registros")],
             [1, 2, 0], "Comece com 8 registros e dobre duas vezes.")],
    7: [task("lia", "Conferir o recado no servidor", "Qual frase do recado e desmentida pela copia dos arquivos?", "choose",
             [("new_envelope", "Envelope recuperado", "Nome de Cassie"), ("recordings", "Lotes copiados", "Perfis de toda a equipe")],
             [("new_envelope", "Mensagem pessoal", "Cassie e citada."), ("recordings", "So Celine", "Nao ha nada sobre voces."), ("recordings", "Cinco perfis", "A equipe foi estudada.")],
             [1], "Os arquivos guardam os perfis dos Naturais."),
        task("lia", "Limitar a conclusao", "Qual afirmacao vai alem do que a imagem mostra?", "choose",
             [("camera", "Imagem recuperada", "Rosto do mensageiro oculto"), ("clock", "Horario legivel", "Entrada as 21:09")],
             [("camera", "Era Lorelai", "Reconheci quem entrou."), ("clock", "As 21:09", "O horario esta visivel."), ("camera", "Sem rosto", "A pessoa nao foi identificada.")],
             [0], "O horario aparece, mas o rosto nao. Nao invente uma identidade.")],
    8: [task("michael", "Conferir o relato pelo radio", "A zeladora pede tempo para explicar seu relato. Como ouvir?", "choose",
             [("phone", "Contato com a zeladora", "Pede tempo para responder")],
             [("clock", "Dar tempo", "Ouvir sem pressionar"), ("lock_a", "Ameacar", "Acelerar a resposta"), ("new_envelope", "Sugerir um nome", "Escolher por ela")],
             [0], "Acolha a reacao sem colocar palavras na boca da pessoa."),
        task("sloane", "Conferir a cronologia", "Organize os registros por horario.", "order",
             [("clock", "Relogios conferidos", "Os registros usam a mesma hora")],
             [("camera", "Visita", "21:09"), ("new_envelope", "Envelope", "21:16"), ("key417", "Saida de Celine", "20:30")],
             [2, 0, 1], "20:30 vem antes de 21:09; a descoberta e as 21:16."),
        task("lia", "Revisar a acusacao", "Qual frase NAO pode entrar como fato comprovado?", "choose",
             [("camera", "Camera", "Rosto oculto"), ("recorder", "Audio", "Cita o nome Lorelai")],
             [("recorder", "Lorelai foi citada", "O nome aparece no audio"), ("camera", "Lorelai enviou", "Autoria confirmada"), ("camera", "Autoria incerta", "A imagem nao identifica")],
             [1], "Um nome citado nao confirma quem enviou a mensagem."),
        task("dean", "Ligar intencao e evidencias", "Marque DUAS provas de que conheciam a equipe.", "select",
             [("recordings", "Arquivo", "Perfis individuais"), ("new_envelope", "Convite", "Dirigido a Cassie")],
             [("lamp", "Luz da casa", "Ambiente iluminado"), ("recordings", "Perfis pessoais", "Habilidades registradas"), ("clock", "Relogio parado", "Sem autoria"), ("new_envelope", "Nome de Cassie", "Destinataria escolhida")],
             [1, 3], "A destinataria e os perfis sustentam o planejamento."),
        task("cassie", "Fechar o relatorio da equipe", "Marque TRES conclusoes sustentadas pela investigacao.", "select",
             [("new_envelope", "Mensagem", "Cassie era o alvo"), ("camera", "Mensageiro", "Identidade desconhecida"), ("key417", "Celine", "Ainda desaparecida")],
             [("new_envelope", "Alvo: Cassie", "A mensagem a escolheu"), ("camera", "Autor conhecido", "O rosto foi identificado"), ("key417", "Celine desaparecida", "O destino segue incerto"), ("recordings", "Equipe estudada", "Perfis recuperados")],
             [0, 2, 3], "Use o que foi demonstrado. A identidade do mensageiro continua incerta.")],
}

SOURCES = {
    1: "FONTE: agenda, celular e envelope encontrados na gaveta",
    2: "FONTE: relato do porteiro, celular e video recuperado",
    3: "FONTE: envelope e fotografia que voce remontou",
    4: "FONTE: gravador entregue pela zeladora de Mercer House",
    5: "FONTE: cartao encontrado no compartimento do relogio",
    6: "FONTE: perfis e indice do arquivo que voce destravou",
    7: "FONTE: lotes copiados do servidor e recado anexado",
    8: "FONTE: provas reunidas e contato com a zeladora pelo radio",
}
RESULTS = {
    1: ("Os registros estao em ordem. Falta identificar quem deixou o envelope.",),
    2: ("A ligacao nao consta. Lia passa a conferir o relato com o video.",
        "A camera confirma a entrega depois da saida filmada de Celine."),
    3: ("Nome e fotografia indicam um convite pessoal. A equipe segue para Mercer House.",),
    4: ("A zeladora se acalma e aceita explicar o que reconheceu no audio.",
        "Ela mostra o relogio numa foto de manutencao: 03:21."),
    5: ("Primeira metade do fecho encontrada: 12. Falta o segundo valor.",
        "O fecho aceita 12-16. A porta do porao foi aberta."),
    6: ("Os testes usam as habilidades dos cinco. Sloane organiza a exportacao.",
        "Fila de copia preparada: lotes A, B e C."),
    7: ("O recado e falso: os lotes tambem guardam os perfis dos Naturais.",
        "O horario e conhecido; o rosto nao. Essa limitacao entra no relatorio."),
    8: ("O relato foi conferido com a zeladora, sem sugerir uma resposta.",
        "A cronologia foi conferida. Lia revisa o que pode ser afirmado.",
        "A autoria continua incerta. Dean separa as provas de planejamento.",
        "As evidencias sustentam a intencao. Cassie fecha as conclusoes.",
        "Relatorio revisado pelos cinco. Agora envie as quatro partes."),
}


class TeamInvestigation:
    def __init__(self, campaign):
        self.c = campaign
        self.roster_open = False
        self.roster_page = 0
        self.faces = {key: pygame.transform.smoothscale(portrait, (130, 195))
                      for key, portrait in campaign.game.stage_portraits.items()}

    def current(self):
        d = self.c.data
        rounds = TEAM_TASKS[d["chapter"]]
        return rounds[min(d["team_round"], len(rounds) - 1)]

    def actor(self):
        return self.current()["actor"]

    def open(self):
        self.c.data["view"] = "team_task"
        self.c.feedback_time = 0

    def select(self, index):
        d, task = self.c.data, self.current()
        if d["view"] != "team_task" or not d["team_ready"] or not 0 <= index < len(task["cards"]):
            return
        chosen = d["team_selection"]
        if index in chosen:
            chosen.remove(index)
        elif task["kind"] == "choose":
            chosen[:] = [index]
        elif len(chosen) < len(task["answer"]):
            chosen.append(index)
        else:
            self.c.notice("Desmarque uma escolha para trocar.")

    def confirm(self):
        d, task = self.c.data, self.current()
        if d["view"] != "team_task" or not d["team_ready"] or d["chapter"] in d["team_done"]:
            return
        chosen = d["team_selection"]
        if len(chosen) != len(task["answer"]):
            self.c.notice("Complete a selecao antes de confirmar.")
            return
        correct = chosen == task["answer"] if task["kind"] == "order" else set(chosen) == set(task["answer"])
        if not correct:
            self.c.mistake("As pistas nao sustentam essa resposta.")
            return
        inv = self.c.game.investigation
        result = RESULTS[d["chapter"]][d["team_round"]]
        ability = f"visual8_{d['chapter']}_{d['team_round']}_{task['actor']}"
        if inv.use_ability(ability):
            inv.correct_connections += 1
            if task["actor"] == "lia" and (d["chapter"] == 2 or (d["chapter"] == 7 and d["team_round"] == 0)):
                inv.lies_found += 1
        d["team_round"] += 1
        d["team_selection"] = []
        self.c.notice(result + "  |  +10")
        self.c.feedback_time = 3.5
        if d["team_round"] == len(TEAM_TASKS[d["chapter"]]):
            d["team_done"].append(d["chapter"])
            d["team_ready"] = False
            if d["chapter"] == 8 and d["hits"] < 4:
                self.c.open_puzzle("timing")
            else:
                self.c.complete()

    def buttons(self):
        c, d, task = self.c, self.c.data, self.current()
        count = len(task["cards"])
        width = (790 - (count - 1) * 12) // count
        buttons = [c.button((290 + i * (width + 12), 365, width, 165), card[1], ("team_card", i),
                            selected=i in d["team_selection"]) for i, card in enumerate(task["cards"])]
        buttons += [c.button((710, 545, 150, 44), "Limpar", "team_clear", bool(d["team_selection"])),
                    c.button((880, 540, 200, 54), "Confirmar", "team_confirm", len(d["team_selection"]) == len(task["answer"]))]
        return buttons

    def draw_task(self):
        c, g, d, task = self.c, self.c.game, self.c.data, self.current()
        actor = task["actor"]
        g.screen.blit(self.faces[actor], (80, 210))
        c.text(CHARACTERS[actor]["name"], (30, 425, 230, 38), g.fonts.h2, align="center")
        role = next(p[2] for p in TEAM_PROFILES if p[0] == actor)
        c.text(role, (30, 469, 230, 30), g.fonts.body, GOOD, align="center")
        c.text(f"Analise {d['team_round'] + 1} / {len(TEAM_TASKS[d['chapter']])}", (30, 519, 230, 28), g.fonts.small, MUTED, "center")
        c.text(task["title"], (290, 175, 800, 40), g.fonts.h2)
        c.text(SOURCES[d["chapter"]], (290, 210, 800, 23), g.fonts.small, MUTED)
        refs = task["references"]
        width = (790 - (len(refs) - 1) * 14) // len(refs)
        for i, (icon, label, detail) in enumerate(refs):
            rect = pygame.Rect(290 + i * (width + 14), 237, width, 104)
            pygame.draw.rect(g.screen, (38, 52, 51), rect, border_radius=4)
            c.draw_item(icon, pygame.Rect(rect.x + 10, rect.y + 12, 35, 32))
            c.text(label, (rect.x + 55, rect.y + 13, width - 65, 30), g.fonts.small, GOOD)
            pattern = task["actor"] == "sloane" and " / " in detail
            c.text(detail, (rect.x + 12, rect.y + 54, width - 24, 46),
                   g.fonts.h2 if pattern else g.fonts.body, align="center" if pattern else "left")
        for button in self.buttons():
            if not isinstance(button.value, tuple):
                continue
            index = button.value[1]
            icon, label, detail = task["cards"][index]
            rect = button.rect
            pygame.draw.rect(g.screen, (44, 77, 68) if button.selected else (39, 49, 48), rect, border_radius=5)
            border = (225, 190, 91) if button.selected else TEXT if rect.collidepoint(pygame.mouse.get_pos()) else MUTED
            pygame.draw.rect(g.screen, border, rect, 2, border_radius=5)
            c.draw_item(icon, pygame.Rect(rect.centerx - 26, rect.y + 12, 52, 44))
            c.text(label, (rect.x + 8, rect.y + 62, rect.w - 16, 50),
                   g.fonts.h1 if label.isdigit() else g.fonts.button, align="center", line_spacing=0)
            c.text(detail, (rect.x + 8, rect.y + 112, rect.w - 16, 42), g.fonts.small, MUTED, "center", line_spacing=0)
            if button.selected:
                number = str(d["team_selection"].index(index) + 1) if task["kind"] == "order" else "+"
                pygame.draw.circle(g.screen, GOOD, (rect.x + 20, rect.y + 20), 13)
                c.text(number, (rect.x + 8, rect.y + 6, 24, 28), g.fonts.button, (18, 26, 27), "center")
        c.text(f"{len(d['team_selection'])} / {len(task['answer'])} selecionados", (290, 550, 380, 30), g.fonts.small, MUTED)
        if d["chapter"] == 5:
            c.text("Fecho: " + ("12 - ?" if d["team_round"] else "? - ?"), (30, 559, 230, 30), g.fonts.body, GOOD, "center")

    def roster_buttons(self):
        return [self.c.button((30, 145, 170, 42), "Os Naturais", "naturals", selected=self.roster_page == 0),
                self.c.button((215, 145, 190, 42), "Pessoas do caso", "case", selected=self.roster_page == 1),
                self.c.button((895, 633, 185, 48), "Voltar ao jogo", "close")]

    def handle_roster_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.roster_open = False
        for button in self.roster_buttons():
            if button.hit(event):
                if button.value == "close":
                    self.roster_open = False
                else:
                    self.roster_page = 0 if button.value == "naturals" else 1

    def draw_roster(self):
        c, g = self.c, self.c.game
        g.screen.fill((18, 26, 27))
        c.text("Quem faz o que", (30, 65, 1000, 55), g.fonts.h1)
        profiles = TEAM_PROFILES if self.roster_page == 0 else [
            ("celine", "Celine", "Desaparecida", "Seus ultimos passos iniciam a investigacao."),
            ("daniel", "Daniel Redding", "O aviso", "Alerta Cassie sobre os padroes dos Masters."),
            ("lorelai", "Lorelai", "Passado de Cassie", "Seu nome aparece; sua participacao e incerta."),
            ("masters", "Masters", "Grupo investigado", "Ligado aos testes que cercam a equipe."),
        ]
        for i, (key, name, role, description) in enumerate(profiles):
            x = 35 + i * 215
            g.screen.blit(self.faces[key], (x + 32, 222))
            c.text(name, (x, 430, 200, 40), g.fonts.h2, align="center")
            c.text(role, (x, 478, 200, 30), g.fonts.small, GOOD, "center")
            c.text(description, (x + 2, 519, 196, 80), g.fonts.small, MUTED, "center")
        for button in self.roster_buttons():
            button.draw(g.screen, g.fonts, pygame.mouse.get_pos())

    def draw_intro(self):
        c, g = self.c, self.c.game
        g.screen.blit(self.faces["celine"], (70, 175))
        g.screen.blit(self.faces["daniel"], (230, 175))
        c.text("Celine", (65, 375, 145, 28), g.fonts.small, align="center")
        c.text("Daniel Redding", (225, 375, 150, 28), g.fonts.small, align="center")
        c.text("Celine desapareceu.", (410, 185, 660, 55), g.fonts.h1)
        c.text("Voce e Cassie. Procure os registros de Celine com a ajuda dos Naturais.", (410, 252, 640, 80))
        c.text('Redding: "Eles procuram padroes, Cassie."', (410, 342, 660, 42), g.fonts.body, (225, 190, 91))
        for i, (key, name, role, _) in enumerate(TEAM_PROFILES):
            x = 95 + i * 202
            g.screen.blit(pygame.transform.smoothscale(self.faces[key], (70, 105)), (x + 38, 422))
            c.text(name, (x, 534, 150, 30), g.fonts.button, align="center")
            c.text(role, (x - 15, 569, 180, 25), g.fonts.small, GOOD, "center")

    def draw_ending(self):
        c, g = self.c, self.c.game
        for i, (key, name, _, _) in enumerate(TEAM_PROFILES):
            x = 385 + i * 140
            g.screen.blit(pygame.transform.smoothscale(self.faces[key], (70, 105)), (x + 20, 425))
            c.text(name, (x, 545, 110, 30), g.fonts.button, align="center")
