from control import fcfs, sjf, round_robin, srtf, prioridade_cooperativo, prioridade_preemptivo
from control.algoritmos import inversaoDePrioridade
from control.algoritmos import herancaDePrioridade
from control.algoritmos import tetoDePrioridade
#import copy


def simular_escalonamento(
    processos,
    algoritmo,
    quantum_entry=0,
    ctx_time=0,
    alpha=0
):
    if not processos:
        raise Exception("Nenhum processo foi adicionado.")

    #processos = copy.deepcopy(processos)
    ctx_time = float(ctx_time)
    alpha = float(alpha)

    if algoritmo == 1:
        media_execucao, media_espera, media_primeira_execucao, nome_processo = fcfs(
            processos, ctx_time
        )

    elif algoritmo == 2:
        media_execucao, media_espera, media_primeira_execucao, nome_processo = sjf(
            processos, ctx_time
        )

    elif algoritmo == 3:
        quantum = int(quantum_entry)

        media_execucao, media_espera, media_primeira_execucao, nome_processo = round_robin(
            processos, quantum, ctx_time
        )

    elif algoritmo == 4:
        media_execucao, media_espera, media_primeira_execucao, nome_processo = srtf(
            processos, ctx_time
        )

    elif algoritmo == 5:
        media_execucao, media_espera, media_primeira_execucao, nome_processo = prioridade_cooperativo(
            processos,
            ctx_time,
            alpha
        )

    elif algoritmo == 6:
        media_execucao, media_espera, media_primeira_execucao, nome_processo = prioridade_preemptivo(
            processos,
            ctx_time,
            alpha
        )

    elif algoritmo == 7:
        media_execucao, media_espera, media_primeira_execucao, nome_processo = inversaoDePrioridade.inversao_prioridade(
            processos,
            ctx_time
        )

    elif algoritmo == 8:
        media_execucao, media_espera, media_primeira_execucao, nome_processo = herancaDePrioridade.heranca_prioridade(
            processos,
            ctx_time
        )

    elif algoritmo == 9:
        media_execucao, media_espera, media_primeira_execucao, nome_processo = tetoDePrioridade.teto_prioridade(
            processos,
            ctx_time
        )

    else:
        raise Exception("Selecione um algoritmo válido.")

    return media_execucao, media_espera, media_primeira_execucao, nome_processo