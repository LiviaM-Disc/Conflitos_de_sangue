import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.dialogos import (PROLOGUE_LINES, PROLOGUE_CHOICES, PROLOGUE_OUTRO,
                              INTERROGATION_ROUNDS, PUZZLE_ROUNDS, PROFILE_EVENTS,
                              FINAL_ROUNDS, EPILOGUE_LINES)
from scripts.pistas import EVIDENCES

CONTENT = []


def add(kind, text):
    CONTENT.append((kind, text))


def line(speaker, text):
    add('p', f'{speaker}: {text}')


def evidence(key):
    item = EVIDENCES[key]
    line(f'Registro do dossiê | {item.name}', item.description)


add('title', 'Conflitos de Sangue Roteiro completo do jogo')
add('p', 'Prólogo, cinco fases e epílogo da versão atual. As falas estão reproduzidas como aparecem no jogo. As indicações entre colchetes situam a cena ou identificam trechos opcionais e respostas às escolhas; não são falas adicionais dos personagens.')

add('h', 'Prólogo Uma conversa sob suspeita')
add('p', '[Sala de entrevistas. Cassie participa de uma conversa com Daniel Redding.]')
for speaker, text in PROLOGUE_LINES:
    line(speaker, text)
line('Cassie', 'Redding deixou uma abertura. Como voce conduz a conversa?')
add('sub', 'Escolha do jogador')
for number, (text, key, feedback) in enumerate(PROLOGUE_CHOICES, 1):
    line(f'Opção {number}', text)
    line('Resposta da cena', feedback)
    if key:
        evidence(key)
    else:
        add('p', '[A conversa termina sem registrar o Aviso de Redding. A investigação segue, com perda de pontuação.]')
add('sub', 'O chamado')
add('p', '[As duas escolhas conduzem à preparação da equipe. O desaparecimento de Celine passa a ser o foco da investigação.]')
for speaker, text in PROLOGUE_OUTRO:
    line(speaker, text)

add('h', 'Fase 1 O escritório de Celine')
add('p', '[Cassie entra no escritório. O jogador pode examinar os objetos em ordens diferentes. Os textos abaixo são os registros encontrados, não declarações de um suspeito.]')
for key in ('celine_bracelet', 'broken_phone', 'coded_invitation', 'dusty_book', 'window_mark'):
    add('sub', EVIDENCES[key].name)
    evidence(key)
add('sub', 'Observação de Cassie')
line('Mensagem ao usar a habilidade', 'Cassie reconstruiu a cena: nada aqui parece aleatorio.')
line('Mensagem ao repetir a habilidade', 'Cassie ja registrou o padrao principal desta sala.')
add('p', '[A pulseira, o celular e o convite permitem avançar. O livro e a marca na janela são descobertas opcionais. O jogador segue para o depoimento.]')

add('h', 'Fase 2 Mentiras e emoções')
add('p', '[Sala de entrevistas. Um depoente, sem nome apresentado nesta versão, responde sobre Celine. Lia e Michael podem ser consultados em cada assunto. Antes da consulta, a cena informa: “Lia e Michael aguardam a proxima pergunta.”]')
for number, topic in enumerate(INTERROGATION_ROUNDS, 1):
    add('sub', f'Assunto {number} {topic["title"]}')
    add('p', topic['statement'])
    add('p', '[Ao consultar Lia]')
    add('p', topic['lia'])
    add('p', '[Ao consultar Michael]')
    add('p', topic['michael'])
    if number == 3:
        evidence('michael_emotion')
    add('p', '[O jogador escolhe uma interpretação e apresenta evidências.]')
    for index, (text, correct) in enumerate(topic['choices'], 1):
        line(f'Opção {index}', text)
    line('Interpretação sustentada', next(text for text, correct in topic['choices'] if correct))
    line('Prova correspondente', ', '.join(EVIDENCES[k].name for k in topic['uses']))
    line('Resposta ao argumento correto', 'Argumento sustentado pelas provas. ' + topic['feedback'])
    line('Resposta à hipótese correta com provas inadequadas', 'Hipotese correta, mas as provas apresentadas nao a sustentam. ' + topic['feedback'])
    line('Resposta à hipótese incorreta', 'A hipotese nao resiste ao confronto com os registros. ' + topic['feedback'])
    add('p', '[Quando a interpretação é sustentada, o dossiê recebe este registro.]')
    evidence(topic['evidence'])
add('p', '[A revisão do depoimento permite seguir mesmo após um erro. Ao terminar os três assuntos, a equipe analisa o convite.]')

add('h', 'Fase 3 O convite cifrado')
add('p', '[Laboratório de análise. Sloane acompanha a investigação do código. O jogador digita uma resposta numérica para cada etapa.]')
for index, topic in enumerate(PUZZLE_ROUNDS, 1):
    add('sub', f'Análise {index} {topic["title"]}')
    line('Sequência exibida', ', '.join(topic['values']))
    line('Enigma', topic['prompt'])
    add('p', '[Ao consultar Sloane]')
    add('p', topic['hint'])
    line('Resposta', str(topic['answer']))
    if index == 3:
        add('p', '[A operação é 21 - 8 + 13 + 3 = 29. Os termos são escolhidos pelas posições indicadas no verso.]')
        line('Resposta da cena', 'A chave 29 abre o envelope interno. A mensagem pede que Cassie venha sozinha.')
    else:
        line('Resposta ao acerto', 'A regra confere. Ainda ha outra camada no convite.')
    line('Resposta ao erro', 'A resposta nao encaixa. Revise a sequencia ou consulte Sloane.')
evidence('fibonacci_key')
add('p', '[O conteúdo descoberto não é uma orientação genérica: pede a presença de Cassie sozinha. A equipe passa a relacionar o código aos demais acontecimentos.]')

add('h', 'Fase 4 A linha do tempo')
add('p', '[Arquivo da investigação. Cassie e Dean confrontam as pistas. Primeiro, é necessário relacionar duas evidências; depois, ordenar os acontecimentos.]')
line('Pergunta da cena', 'Quais duas pistas mostram que o convite tem um codigo planejado?')
line('Evidências apresentadas como opções', 'Celular sem sinal; Convite cifrado; Pulseira de Celine; Chave Fibonacci.')
line('Relação sustentada', 'Convite cifrado e Chave Fibonacci.')
line('Dean', 'o codigo confirma que o convite foi planejado. Agora precisamos ordenar os fatos.')
line('Dean', 'o que aconteceu primeiro muda toda a leitura do caso.')
add('sub', 'Reconstrução correta')
for index, event in enumerate(PROFILE_EVENTS, 1):
    line(f'Acontecimento {index}', event)
line('Resposta a uma relação ou ordem incorreta', 'A hipotese deixa uma lacuna. Revise as evidencias e tente novamente.')
evidence('profile_sequence')
line('Transição para a próxima cena', 'A pista era uma armadilha. Separada da equipe, Cassie precisa investigar o salao sozinha.')
add('p', '[A separação é comunicada por essa mensagem e pela mudança de cenário. Não há uma cena adicional de captura na versão atual.]')

add('h', 'Fase 5 O outro lado da armadilha')
add('p', '[Salão dos Masters. Cassie está sem o apoio direto da equipe. Ela investiga três pontos: retrato, porta e mosaico.]')
for key in ('lorelai_note', 'locked_exit', 'hall_pattern'):
    add('sub', EVIDENCES[key].name)
    evidence(key)
line('Cassie ao observar o ambiente', 'o retrato, a porta e o mosaico contam versoes diferentes deste lugar.')
add('p', '[Depois de reunir as três pistas, Cassie passa às deduções. Lorelai aparece como lembrança, não como presença física ou personagem que fornece ajuda.]')
for index, topic in enumerate(FINAL_ROUNDS, 1):
    add('sub', f'Dedução {index} {topic["title"]}')
    line('Questão da cena', topic['prompt'])
    add('p', '[Reflexão opcional de Cassie. Só uma ajuda pode ser usada durante as deduções finais; a fala depende da dedução em que ela é solicitada.]')
    add('p', topic['hint'])
    for number, (text, correct) in enumerate(topic['choices'], 1):
        line(f'Opção {number}', text)
    line('Hipótese sustentada', next(text for text, correct in topic['choices'] if correct))
    line('Provas correspondentes', '; '.join(EVIDENCES[k].name for k in topic['uses']))
    line('Resposta ao argumento correto', 'Argumento sustentado pelas provas. ' + topic['feedback'])
    line('Resposta ao argumento incorreto', 'O argumento tem uma lacuna. Reavalie a hipotese e a relevancia de cada prova antes de concluir.')
    add('p', '[Um erro exige rever a hipótese e as provas. A próxima etapa só é liberada após uma conclusão sustentada.]')
line('Mensagem ao pedir outra ajuda', 'Agora Cassie precisa concluir sem novas ajudas.')
evidence('final_deduction')

add('h', 'Epílogo O que fica')
add('p', '[Depois da armadilha. As duas primeiras reflexões de Cassie aparecem sobre o cenário do salão; as seguintes são apresentadas no arquivo da investigação.]')
for speaker, text in EPILOGUE_LINES:
    line(speaker, text)
add('p', '[A última fala de Cassie recebe um complemento conforme o desempenho.]')
line('Cassie se houve erros', 'Ha lacunas que precisamos reconhecer antes de seguir.')
line('Cassie se não houve erros', 'Os registros sustentam cada passo desta conclusao.')
add('sub', 'Relatório da investigação')
add('p', '[Após o diálogo, o relatório apresenta a pontuação total, as pistas encontradas, os enigmas resolvidos, as mentiras identificadas, as conexões corretas e os erros investigativos. A classificação pode ser Investigacao exemplar, Investigacao solida, Investigacao incompleta ou Muitas pontas soltas.]')
line('Conclusão registrada no relatório', FINAL_ROUNDS[-1]['feedback'])
add('p', '[Fim do capítulo implementado. O jogador pode voltar ao menu. O destino definitivo de Celine e as respostas completas sobre Lorelai permanecem em aberto, conforme as próprias falas do epílogo.]')

# Verify coverage of the story data, including every optional line and choice.
full_text = '\n'.join(text for _, text in CONTENT)
for speaker, text in PROLOGUE_LINES + PROLOGUE_OUTRO + EPILOGUE_LINES:
    assert text in full_text
for topic in INTERROGATION_ROUNDS + FINAL_ROUNDS:
    assert topic['feedback'] in full_text
    for text, _ in topic['choices']:
        assert text in full_text
for item in EVIDENCES.values():
    assert item.description in full_text
