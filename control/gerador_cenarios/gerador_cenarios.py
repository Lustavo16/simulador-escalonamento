import random

from model.processo import Processo
from model.prioridade import Prioridade


def gerar_cenario(quantidade, chegada_max, duracao_max, prioridade_max):
    processos = []

    for i in range(1, quantidade + 1):
        chegada = random.randint(0, chegada_max)
        duracao = random.randint(1, duracao_max)
        prioridade = random.randint(1, prioridade_max)

        processo = Processo(
            i,
            chegada,
            duracao,
            Prioridade(prioridade)
        )

        processos.append(processo)

    processos.sort(key=lambda p: p.id)

    return processos