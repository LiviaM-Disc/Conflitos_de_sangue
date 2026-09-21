"""Read-only instructions overlay; never changes campaign or ranking data."""
import pygame

from scripts.interfaces import Button, TEXT, MUTED, ACCENT_2, draw_band, draw_text
from scripts.roteiro_expandido import PUZZLES


PAGES = [
    ("Investigar o ambiente", [
        ("Observe e clique", "Passe o mouse sobre os objetos para descobrir seus nomes. Clique para examinar ou conversar. Voce pode investigar com o mouse sem caminhar ate cada objeto."),
        ("Leia o resultado", "As descobertas aparecem em uma tela de leitura. Use as setas se houver mais texto e Continuar para voltar. O ponto verde marca um objeto ou desafio ja concluido."),
        ("Siga o objetivo", "O objetivo do capitulo aparece no alto. Use as passagens com nomes de salas ou Locais para mudar de ambiente. Dica indica onde procurar quando voce nao souber como continuar."),
    ]),
    ("Usar e combinar itens", [
        ("Guardar nao e usar", "Itens coletados ficam na barra inferior. Clique no item para seleciona-lo e depois no objeto do cenario onde deseja usa-lo. Clique no item de novo para desmarcar. Nao precisa arrastar."),
        ("Procurar e combinar", "As setas da barra mostram mais itens; Itens abre a lista completa. Para montar algo, selecione dois objetos e clique em Combinar. As selecoes continuam ativas ao mudar de pagina."),
        ("Entenda o que mudou", "Uma acao pode liberar outro objeto sem mudar de sala. Leia a mensagem, volte com Continuar e observe o ambiente. Se faltar um requisito, consulte as pistas ou visite outro local."),
    ]),
    ("Responder aos enigmas", [
        ("Alternativas e codigos", "Clique na alternativa e depois em Confirmar. Em codigos, use os numeros da tela ou o teclado. Apagar corrige um digito. Preserve zeros iniciais quando o formato pedir."),
        ("Sequencias e selecoes", "Se o desafio pedir uma ordem, clique nos valores nessa ordem. Os numeros pequenos mostram a posicao escolhida. Se pedir um conjunto, marque apenas os elementos desejados. Clique novamente para desmarcar."),
        ("Revisar antes de confirmar", "Limpar apaga a selecao para recomecar. A resposta so e avaliada em Confirmar. Dossie permite consultar registros. Nos paineis de tabela, clique em cada campo para trocar sua opcao."),
    ]),
    ("Construir uma deducao", [
        ("Primeiro a conclusao", "Leia a pergunta e escolha a explicacao que os registros sustentam. Clicar na conclusao abre a selecao de provas; isso ainda nao envia sua resposta."),
        ("Depois as provas", "Marque as evidencias que sustentam a conclusao. O contador informa quantas provas sao esperadas. Apenas pistas ja coletadas ficam disponiveis. Clique de novo para retirar uma prova."),
        ("Confirme o argumento", "Pressione Confirmar depois de escolher a conclusao e todas as provas. Limpar permite trocar a conclusao. Se faltar uma evidencia, volte a explorar e consulte Pistas ou Dica."),
    ]),
    ("Encontrar salas e registros", [
        ("Passagens e mapa", "Os botoes no alto do cenario levam a salas vizinhas. Em Locais, escolha um capitulo ja alcancado e o ambiente. As setas mostram outras salas quando a lista tem mais de uma pagina."),
        ("Itens e pistas sao diferentes", "Itens sao objetos para usar ou combinar. Pistas, ou Dossie, guarda os registros da investigacao. Consulte esses textos para comparar horarios, falas e acontecimentos."),
        ("Quando um acesso esta fechado", "Leia o aviso para saber o que falta. Algumas salas exigem uma chave no inventario; outros objetos exigem que voce selecione o item antes de clicar. Novos capitulos dependem da conclusao da etapa atual."),
    ]),
    ("Dicas e progresso", [
        ("Ajuda sem desconto", "Dica na exploracao indica o proximo passo. Em um enigma, ha duas dicas e depois Ver resposta. Consultar essas dicas nao tira pontos nem responde automaticamente. As consultas aos personagens podem ter limite."),
        ("Pontuacao e ranking", "Novas evidencias, enigmas e deducoes corretas rendem pontos. Erros penalizados custam 5 pontos, sem saldo negativo ou perda de itens. O ranking registra o resultado ao concluir o epilogo, pelo apelido do jogador."),
        ("Pode parar e continuar depois", "ESC abre a pausa; nela, escolha Salvar e voltar ao menu. Continuar investigacao retoma o progresso salvo. O guia Como jogar pode ser reaberto a qualquer momento pelo botao ou por F1, sem mudar sua resposta."),
    ]),
]


PUZZLE_INSTRUCTIONS = {
    "choice": "Selecione uma alternativa e clique em Confirmar. Dica e gratuita.",
    "code": "Digite o codigo e confirme. Use Apagar para corrigir; preserve zeros iniciais.",
    "order": "Clique nos valores na ordem desejada e confirme. Limpar reinicia a selecao.",
    "set": "Marque o conjunto pedido e confirme. Clique novamente para desmarcar.",
    "grid": "Clique em cada campo para trocar a opcao. Preencha todas as linhas e confirme.",
    "proof": "Escolha uma conclusao; depois selecione as provas e clique em Confirmar.",
}


class Instructions:
    def __init__(self, game):
        self.g = game
        self.active = False
        self.page = 0

    def available(self):
        return self.g.state in {"menu", "campaign"} and not (self.g.paused or self.g.show_clues or self.g.confirm_new or self.g.player_screens.active)

    def button(self):
        return Button(pygame.Rect(925, 14, 175, 42), "Como jogar", "instructions")

    def open(self, contextual=True):
        d = self.g.campaign_data
        self.page = 0
        if contextual and self.g.state == "campaign":
            view = d["note_return"] if d["view"] == "note" else d["view"]
            if view == "puzzle" and d["puzzle"]:
                self.page = 3 if PUZZLES[d["puzzle"]]["kind"] == "proof" else 2
            else:
                self.page = {"inventory": 1, "map": 4, "help": 5, "report": 5}.get(view, 0)
        self.active = True

    def buttons(self):
        return [Button(pygame.Rect(60, 635, 220, 48), "Fechar ajuda", "close"),
                Button(pygame.Rect(900, 635, 65, 48), "<", "previous", self.page > 0),
                Button(pygame.Rect(985, 635, 65, 48), ">", "next", self.page < len(PAGES)-1)]

    def handle_event(self, event):
        action = None
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_F1):
                action = "close"
            elif event.key == pygame.K_RIGHT:
                action = "next"
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                action = "next" if self.page < len(PAGES)-1 else "close"
            elif event.key == pygame.K_LEFT:
                action = "previous"
        for button in self.buttons():
            if button.hit(event):
                action = button.value
                break
        if action == "close":
            self.active = False
        elif action == "next":
            self.page = min(len(PAGES)-1, self.page + 1)
        elif action == "previous":
            self.page = max(0, self.page - 1)

    def draw(self):
        g = self.g
        g.screen.blit(g.backgrounds["arquivo"], (0, 0))
        draw_band(g.screen, pygame.Rect(0, 0, 1120, 720), alpha=243)
        title, sections = PAGES[self.page]
        draw_text(g.screen, f"COMO JOGAR / {self.page + 1} DE {len(PAGES)}", g.fonts.small, ACCENT_2, pygame.Rect(60, 42, 1000, 28))
        draw_text(g.screen, title, g.fonts.h1, TEXT, pygame.Rect(60, 88, 1000, 50))
        for i, (heading, body) in enumerate(sections):
            y = 165 + i * 145
            draw_text(g.screen, heading, g.fonts.h2, TEXT, pygame.Rect(60, y, 1000, 34))
            draw_text(g.screen, body, g.fonts.body, MUTED, pygame.Rect(60, y + 40, 1000, 94))
        for button in self.buttons():
            button.draw(g.screen, g.fonts, pygame.mouse.get_pos())
