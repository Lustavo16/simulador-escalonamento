def sjf(processos, ctx_time=0):
    tempo_atual = 0
    ultimo_processo_id = None  # None garante que o primeiro despacho pague a troca

    processos_pendentes = list(processos)

    for p in processos:
        p.tempo_restante = int(p.duracao)
        p.tempo_executado = 0
        p.processamentos = []

    while processos_pendentes:
        # Filtra quem já chegou na fila de prontos
        chegados = [p for p in processos_pendentes if p.chegada <= tempo_atual]

        # Se ninguém chegou ainda, salta o relógio para a próxima chegada (C10)
        if not chegados:
            tempo_atual = min(p.chegada for p in processos_pendentes)
            chegados = [p for p in processos_pendentes if p.chegada <= tempo_atual]

        # Seleção SJF com desempate oficial (C3: menor duração, menor chegada, menor id)
        processo_atual = min(
            chegados,
            key=lambda p: (p.duracao, p.chegada, p.id)
        )

        # Troca de Contexto (C4: inclusive no 1º despacho)
        if processo_atual.id != ultimo_processo_id and ctx_time > 0:
            processo_atual.adicionar_troca_contexto(tempo_atual, tempo_atual + ctx_time)
            tempo_atual += ctx_time

        # Execução não-preemptiva (cooperativa) até o fim
        duracao_executada = processo_atual.adicionar_processamento(
            tempo_atual,
            tempo_atual + processo_atual.tempo_restante
        )

        tempo_atual += duracao_executada

        ultimo_processo_id = processo_atual.id
        processos_pendentes.remove(processo_atual)

    # Métricas
    media_espera = sum(p.get_espera() for p in processos) / len(processos)
    media_execucao = sum(p.get_turnaround() for p in processos) / len(processos)
    media_primeria_execucao = sum(p.get_tempo_primeira_execucao() for p in processos) / len(processos)

    return media_execucao, media_espera, media_primeria_execucao, "SJF"