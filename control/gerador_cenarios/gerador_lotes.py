import copy

from .gerador_cenarios import gerar_cenario
from control import simular_escalonamento


def executar_lote(
    quantidade_cenarios,
    quantidade_tarefas,
    quantum,
    chegada_max,
    duracao_max,
    prioridade_max,
    ctx_time=0,
    alpha=0
):
    resultados = {
        1: {"nome": "FCFS", "turnaround": [], "espera": [], "primeira_execucao": []},
        2: {"nome": "SJF", "turnaround": [], "espera": [], "primeira_execucao": []},
        3: {"nome": "Round Robin", "turnaround": [], "espera": [], "primeira_execucao": []},
        4: {"nome": "SRTF", "turnaround": [], "espera": [], "primeira_execucao": []},
        5: {"nome": "Prioridade Cooperativa", "turnaround": [], "espera": [], "primeira_execucao": []},
        6: {"nome": "Prioridade Preemptiva", "turnaround": [], "espera": [], "primeira_execucao": []}
    }

    for numero_cenario in range(quantidade_cenarios):

        cenario = gerar_cenario(
            quantidade_tarefas,
            chegada_max,
            duracao_max,
            prioridade_max
        )

        for algoritmo in range(1, 7):

            processos = copy.deepcopy(cenario)

            resultado = simular_escalonamento(
                processos,
                algoritmo,
                quantum,
                ctx_time,
                alpha
            )

            media_execucao, media_espera, media_primeira_execucao, nome_processo = resultado

            resultados[algoritmo]["turnaround"].append(media_execucao)
            resultados[algoritmo]["espera"].append(media_espera)
            resultados[algoritmo]["primeira_execucao"].append(media_primeira_execucao)

            """
            print(
                resultados[algoritmo]["nome"],
                "T1 média:",
                media_primeira_execucao
            )
            """

    for algoritmo in resultados:

        resultados[algoritmo]["turnaround_medio"] = (
            sum(resultados[algoritmo]["turnaround"])
            / len(resultados[algoritmo]["turnaround"])
        )

        resultados[algoritmo]["espera_media"] = (
            sum(resultados[algoritmo]["espera"])
            / len(resultados[algoritmo]["espera"])
        )

        resultados[algoritmo]["media_primeira_execucao"] = (
            sum(resultados[algoritmo]["primeira_execucao"])
            / len(resultados[algoritmo]["primeira_execucao"])
        )

    return resultados