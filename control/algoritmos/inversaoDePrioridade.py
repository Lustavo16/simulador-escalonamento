from model.prioridade import Prioridade


def inversao_prioridade(processos, ctx_time=0):
    tempo_atual = 0
    ultimo_processo_id = None
    dono_recurso = None
    ctx_time = float(ctx_time)

    # Inicialização dos processos
    for p in processos:
        p.tempo_restante = int(p.duracao)
        p.tempo_executado = 0
        p.processamentos = []
        p.bloqueado = False

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
        chegados = [p for p in pendentes if p.chegada <= tempo_atual]

        # Se a CPU está ociosa, salta direto para a próxima chegada
        if not chegados:
            proximas_chegadas = [p.chegada for p in pendentes if p.chegada > tempo_atual]
            if not proximas_chegadas:
                raise RuntimeError("Não foi possível encontrar o próximo instante de chegada.")
            tempo_atual = min(proximas_chegadas)
            continue

        # Liberação do recurso se o detentor terminou ou completou a SC
        if dono_recurso is not None:
            if dono_recurso.tempo_restante <= 0:
                dono_recurso = None
            elif (
                dono_recurso.sc_fim is not None
                and dono_recurso.tempo_executado >= dono_recurso.sc_fim
            ):
                dono_recurso = None

        # Identificação de processos bloqueados disputando o recurso
        for p in pendentes:
            p.bloqueado = False
            if (
                dono_recurso is not None
                and p != dono_recurso
                and p.tempo_executado >= (p.sc_inicio or float("inf"))
                and p.sc_fim is not None
                and p.tempo_executado < p.sc_fim
            ):
                p.bloqueado = True

        # Filtragem de processos aptos
        aptos = [p for p in chegados if not p.bloqueado and p.tempo_restante > 0]

        if not aptos:
            if dono_recurso is not None:
                if dono_recurso in chegados and dono_recurso.tempo_restante > 0:
                    aptos = [dono_recurso]

            if not aptos:
                proximas_chegadas = [p.chegada for p in pendentes if p.chegada > tempo_atual]
                if proximas_chegadas:
                    tempo_atual = min(proximas_chegadas)
                    continue
                raise RuntimeError(
                    "Deadlock na simulação de inversão de prioridade.\n"
                    f"Tempo atual: {tempo_atual}\n"
                    f"Pendentes: {[p.id for p in pendentes]}\n"
                    f"Bloqueados: {[p.id for p in pendentes if p.bloqueado]}\n"
                    f"Dono do recurso: {dono_recurso.id if dono_recurso else None}"
                )

        # Escolha do processo
        escolhido = max(
            aptos,
            key=lambda p: (
                p.prioridade.numero,
                -p.chegada,
                -p.id
            )
        )

        # Alocação do recurso ao ingressar na seção crítica
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
            and dono_recurso != escolhido
        ):
            escolhido.bloqueado = True
            continue

        # Troca de Contexto na tarefa que está ENTRANDO
        if escolhido.id != ultimo_processo_id and ctx_time > 0:
            escolhido.adicionar_troca_contexto(
                tempo_atual,
                tempo_atual + ctx_time
            )
            tempo_atual += ctx_time

        # Executa exatamente 1 unidade discreta de tempo
        inicio = tempo_atual
        fim = tempo_atual + 1
        duracao_executada = escolhido.adicionar_processamento(inicio, fim)
        tempo_atual += duracao_executada

        ultimo_processo_id = escolhido.id

        # Liberação do recurso se completou a seção crítica
        if dono_recurso == escolhido:
            if (
                escolhido.sc_fim is not None
                and escolhido.tempo_executado >= escolhido.sc_fim
            ):
                dono_recurso = None

        # Conclusão do processo
        if escolhido.tempo_restante <= 0:
            if dono_recurso == escolhido:
                dono_recurso = None
            escolhido.bloqueado = False
            pendentes.remove(escolhido)

    # Métricas
    if not processos:
        return 0, 0, "Inversão de Prioridade"

    media_execucao = sum(p.get_turnaround() for p in processos) / len(processos)
    media_espera = sum(p.get_espera() for p in processos) / len(processos)
    media_primeria_execucao = sum(p.get_tempo_primeira_execucao() for p in processos) / len(processos)

    # Ordem padronizada com a interface: (Tt, Tw, Nome)
    return media_execucao, media_espera, media_primeria_execucao, "Inversão de Prioridade"