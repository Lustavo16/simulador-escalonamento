from model.prioridade import Prioridade


def fcfs(processos, ctx_time=0):
    tempo_atual = 0
    ultimo_processo_id = None
    ctx_time = float(ctx_time)

    # Inicialização dos processos
    for p in processos:
        p.tempo_restante = int(p.duracao)
        p.tempo_executado = 0
        p.processamentos = []

    # Desempate por chegada e depois por ID
    processos_ordenados = sorted(processos, key=lambda p: (p.chegada, p.id))

    for escolhido in processos_ordenados:
        # Se a CPU ficou ociosa, avança até o ingresso do processo
        if escolhido.chegada > tempo_atual:
            tempo_atual = escolhido.chegada

        # Troca de contexto
        if escolhido.id != ultimo_processo_id and ctx_time > 0:
            escolhido.adicionar_troca_contexto(
                tempo_atual,
                tempo_atual + ctx_time
            )
            tempo_atual += ctx_time

        # Executa o processo
        duracao_executada = escolhido.adicionar_processamento(
            tempo_atual,
            tempo_atual + escolhido.tempo_restante
        )
        tempo_atual += duracao_executada

        ultimo_processo_id = escolhido.id

    if not processos:
        return 0, 0, "FCFS"

    # Métricas
    media_execucao = sum(p.get_turnaround() for p in processos) / len(processos)
    media_espera = sum(p.get_espera() for p in processos) / len(processos)
    media_primeria_execucao = sum(p.get_tempo_primeira_execucao() for p in processos) / len(processos)

    return media_execucao, media_espera, media_primeria_execucao, "FCFS"