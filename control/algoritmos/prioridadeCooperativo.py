from model.prioridade import Prioridade


def prioridade_cooperativo(processos, ctx_time=0, alpha=0):
    tempo_atual = 0
    ultimo_processo_id = None
    dono_recurso = None
    ctx_time = float(ctx_time)
    alpha = float(alpha)

    # Inicialização dos processos
    for p in processos:
        p.tempo_restante = int(p.duracao)
        p.tempo_executado = 0
        p.processamentos = []

        if hasattr(p.prioridade, "numero"):
            p.prioridade_base = int(p.prioridade.numero)
        else:
            p.prioridade_base = int(p.prioridade)

        p.prioridade_efetiva = p.prioridade_base
        p.inicio_espera = p.chegada

        sc_inicio = getattr(p, "sc_inicio", None)
        sc_duracao = getattr(p, "sc_duracao", None)
        if (
            sc_inicio is not None
            and sc_duracao is not None
            and str(sc_inicio).strip() != ""
            and str(sc_duracao).strip() != ""
        ):
            p.sc_inicio = int(sc_inicio)
            p.sc_duracao = int(sc_duracao)
            p.sc_fim = p.sc_inicio + p.sc_duracao
        else:
            p.sc_inicio = None
            p.sc_duracao = None
            p.sc_fim = None

    pendentes = [p for p in processos if p.tempo_restante > 0]

    while pendentes:
        # Processos que já chegaram
        chegados = [p for p in pendentes if p.chegada <= tempo_atual]

        # CPU ociosa: avança direto para a próxima chegada
        if not chegados:
            proximas_chegadas = [p.chegada for p in pendentes if p.chegada > tempo_atual]
            if not proximas_chegadas:
                raise RuntimeError("Não foi possível encontrar próximo evento.")
            tempo_atual = min(proximas_chegadas)
            continue

        # Calcula a prioridade efetiva usando Aging
        for p in chegados:
            tempo_espera = tempo_atual - p.inicio_espera
            p.prioridade_efetiva = (
                p.prioridade_base
                + (tempo_espera * alpha)
            )

        # Escolha por prioridade efetiva 
        escolhido = max(
            chegados,
            key=lambda p: (
                p.prioridade_efetiva,
                -p.chegada,
                -p.id
            )
        )

        # Troca de Contexto
        if escolhido.id != ultimo_processo_id and ctx_time > 0:
            escolhido.adicionar_troca_contexto(
                tempo_atual,
                tempo_atual + ctx_time
            )
            tempo_atual += ctx_time

        # Ao receber o processador, o Aging é resetado
        escolhido.prioridade_efetiva = escolhido.prioridade_base
        escolhido.inicio_espera = tempo_atual

        # Execução cooperativa
        while escolhido.tempo_restante > 0:
            vai_entrar_na_sc = (
                escolhido.sc_inicio is not None
                and escolhido.sc_fim is not None
                and escolhido.tempo_executado >= escolhido.sc_inicio
                and escolhido.tempo_executado < escolhido.sc_fim
            )

            if vai_entrar_na_sc and dono_recurso is None:
                dono_recurso = escolhido

            # Executa 1 unidade de CPU
            duracao_executada = escolhido.adicionar_processamento(
                tempo_atual,
                tempo_atual + 1
            )
            tempo_atual += duracao_executada

            # Libera o recurso
            if (
                dono_recurso == escolhido
                and escolhido.sc_fim is not None
                and escolhido.tempo_executado >= escolhido.sc_fim
            ):
                dono_recurso = None

        ultimo_processo_id = escolhido.id

        # Processo concluiu a execução
        if escolhido.tempo_restante <= 0:
            if dono_recurso == escolhido:
                dono_recurso = None
            pendentes.remove(escolhido)

    # Restaura as prioridades base
    for p in processos:
        p.prioridade_efetiva = p.prioridade_base
        if hasattr(p.prioridade, "numero"):
            p.prioridade.numero = p.prioridade_base
        else:
            p.prioridade = p.prioridade_base

    # Métricas
    if not processos:
        return 0, 0, "Prioridade Cooperativo"

    media_execucao = sum(p.get_turnaround() for p in processos) / len(processos)
    media_espera = sum(p.get_espera() for p in processos) / len(processos)
    media_primeria_execucao = sum(p.get_tempo_primeira_execucao() for p in processos) / len(processos)

    return media_execucao, media_espera, media_primeria_execucao, "Prioridade Cooperativo"