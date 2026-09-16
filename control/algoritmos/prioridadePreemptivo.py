from model.prioridade import Prioridade

def prioridade_preemptivo(processos, ctx_time=0, alpha=0):
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
        p.bloqueado = False

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
        chegados = [
            p for p in pendentes
            if p.chegada <= tempo_atual
        ]

        if not chegados:
            proximas_chegadas = [
                p.chegada
                for p in pendentes
                if p.chegada > tempo_atual
            ]

            if not proximas_chegadas:
                raise RuntimeError(
                    "Não foi possível encontrar uma próxima tarefa para executar."
                )

            tempo_atual = min(proximas_chegadas)
            continue

        if dono_recurso is not None:
            if dono_recurso.tempo_restante <= 0:
                dono_recurso = None

            elif (
                dono_recurso.sc_fim is not None
                and dono_recurso.tempo_executado >= dono_recurso.sc_fim
            ):
                dono_recurso = None

        for p in pendentes:
            p.bloqueado = False

            if (
                dono_recurso is not None
                and p.id != dono_recurso.id
                and p.sc_inicio is not None
                and p.tempo_executado >= p.sc_inicio
                and p.sc_fim is not None
                and p.tempo_executado < p.sc_fim
            ):
                p.bloqueado = True

        aptos = [
            p for p in chegados
            if not p.bloqueado and p.tempo_restante > 0
        ]

        if not aptos:
            if (
                dono_recurso is not None
                and dono_recurso in chegados
                and dono_recurso.tempo_restante > 0
            ):
                aptos = [dono_recurso]

            if not aptos:
                proximas_chegadas = [
                    p.chegada
                    for p in pendentes
                    if p.chegada > tempo_atual
                ]

                if proximas_chegadas:
                    tempo_atual = min(proximas_chegadas)
                    continue

                raise RuntimeError(
                    "Não foi possível encontrar uma tarefa apta para executar."
                )

        for p in aptos:
            tempo_espera = tempo_atual - p.inicio_espera
            p.prioridade_efetiva = (
                p.prioridade_base + (tempo_espera * alpha)
            )

        escolhido = max(
            aptos,
            key=lambda p: (
                p.prioridade_efetiva,
                -p.chegada,
                -p.id
            )
        )

        vai_entrar_na_sc = (
            escolhido.sc_inicio is not None
            and escolhido.sc_fim is not None
            and escolhido.tempo_executado >= escolhido.sc_inicio
            and escolhido.tempo_executado < escolhido.sc_fim
        )

        if vai_entrar_na_sc and dono_recurso is None:
            dono_recurso = escolhido

        if (
            vai_entrar_na_sc
            and dono_recurso is not None
            and dono_recurso.id != escolhido.id
        ):
            escolhido.bloqueado = True
            continue

        if escolhido.id != ultimo_processo_id and ctx_time > 0:
            escolhido.adicionar_troca_contexto(
                tempo_atual,
                tempo_atual + ctx_time
            )

            tempo_atual += ctx_time

            # Novas tarefas podem chegar durante a troca de contexto.
            for p in pendentes:
                if p.chegada <= tempo_atual:
                    p.bloqueado = False

        escolhido.prioridade_efetiva = escolhido.prioridade_base
        escolhido.inicio_espera = tempo_atual

        inicio_execucao = tempo_atual
        fim_execucao = tempo_atual + 1

        duracao_executada = escolhido.adicionar_processamento(
            inicio_execucao,
            fim_execucao
        )

        tempo_atual += duracao_executada
        ultimo_processo_id = escolhido.id

        if dono_recurso is not None and dono_recurso.id == escolhido.id:
            if (
                escolhido.sc_fim is not None
                and escolhido.tempo_executado >= escolhido.sc_fim
            ):
                dono_recurso = None

        if escolhido.tempo_restante > 0:
            escolhido.inicio_espera = tempo_atual

        if escolhido.tempo_restante <= 0:
            if (
                dono_recurso is not None
                and dono_recurso.id == escolhido.id
            ):
                dono_recurso = None

            escolhido.bloqueado = False
            pendentes.remove(escolhido)

    for p in processos:
        p.prioridade_efetiva = p.prioridade_base

        if hasattr(p.prioridade, "numero"):
            p.prioridade.numero = p.prioridade_base
        else:
            p.prioridade = p.prioridade_base

        p.bloqueado = False

    if not processos:
        return 0, 0, 0, "Prioridade Preemptivo"

    media_execucao = (
        sum(p.get_turnaround() for p in processos)
        / len(processos)
    )

    media_espera = (
        sum(p.get_espera() for p in processos)
        / len(processos)
    )

    media_primeria_execucao = (
        sum(p.get_tempo_primeira_execucao() for p in processos)
        / len(processos)
    )

    return (
        media_execucao,
        media_espera,
        media_primeria_execucao,
        "Prioridade Preemptivo"
    )