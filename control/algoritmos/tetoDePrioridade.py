from model.prioridade import Prioridade


def teto_prioridade(processos, ctx_time=0):
    tempo_atual = 0
    ultimo_processo_id = None
    dono_id = None
    ctx_time = float(ctx_time)

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

        sc_inicio = getattr(p, "sc_inicio", None)
        sc_duracao = getattr(p, "sc_duracao", None)
        if (sc_inicio is not None and sc_duracao is not None and
            str(sc_inicio).strip() != "" and str(sc_duracao).strip() != ""):
            p.sc_inicio = int(sc_inicio)
            p.sc_duracao = int(sc_duracao)
            p.sc_fim = p.sc_inicio + p.sc_duracao
        else:
            p.sc_inicio = None
            p.sc_duracao = None
            p.sc_fim = None

    # Cálculo do Teto do Recurso R
    # Maior prioridade base entre todas as tarefas que utilizam o recurso
    tarefas_com_sc = [p for p in processos if p.sc_inicio is not None]
    teto_recurso = max((p.prioridade_base for p in tarefas_com_sc), default=0)

    pendentes = [p for p in processos if p.tempo_restante > 0]

    while pendentes:
        chegados = [p for p in pendentes if p.chegada <= tempo_atual]

        # Se a CPU está ociosa, salta direto para a próxima chegada
        if not chegados:
            proximas_chegadas = [p.chegada for p in pendentes if p.chegada > tempo_atual]
            if not proximas_chegadas:
                raise RuntimeError("Não foi possível encontrar próximo evento.")
            tempo_atual = min(proximas_chegadas)
            continue

        # Reseta o estado de bloqueio e atualiza a prioridade efetiva
        bloqueados_ids = set()
        for p in processos:
            p.bloqueado = False

            # Se o processo detém o recurso, sua prioridade permanece elevada ao teto
            if dono_id is not None and p.id == dono_id:
                p.prioridade_efetiva = max(p.prioridade_base, teto_recurso)
            else:
                p.prioridade_efetiva = p.prioridade_base

        if dono_id is not None:
            dono = next((p for p in processos if p.id == dono_id), None)

            if dono is None or dono.terminou():
                dono_id = None
            else:
                for p in chegados:
                    if p.id == dono_id:
                        continue

                    if p.precisa_recurso():
                        bloqueados_ids.add(p.id)
                        p.bloqueado = True

        # Filtragem de processos aptos
        aptos = [p for p in chegados if p.id not in bloqueados_ids and not p.terminou()]

        if not aptos:
            if dono_id is not None:
                dono = next((p for p in chegados if p.id == dono_id and not p.terminou()), None)

                if dono is not None:
                    aptos = [dono]

            if not aptos:
                proximas_chegadas = [p.chegada for p in pendentes if p.chegada > tempo_atual]

                if proximas_chegadas:
                    tempo_atual = min(proximas_chegadas)
                    continue

                raise RuntimeError(
                    "Deadlock na simulação de teto de prioridade.\n"
                    f"Tempo atual: {tempo_atual}\n"
                    f"Processos pendentes: {[p.id for p in pendentes]}\n"
                    f"Processos chegados: {[p.id for p in chegados]}\n"
                    f"Bloqueados: {list(bloqueados_ids)}\n"
                    f"Dono do recurso: {dono_id}"
                )

        # Escolha do processo
        escolhido = max(aptos, key=lambda p: (p.prioridade_efetiva, -p.chegada, -p.id))

        # Entrada na seção crítica e elevação imediata ao Teto
        if escolhido.precisa_recurso():
            dono_id = escolhido.id
            escolhido.prioridade_efetiva = max(escolhido.prioridade_base, teto_recurso)

        # Troca de Contexto na tarefa que está entrando
        if escolhido.id != ultimo_processo_id and ctx_time > 0:
            escolhido.adicionar_troca_contexto(tempo_atual, tempo_atual + ctx_time)
            tempo_atual += ctx_time

        # Executa exatamente 1 unidade discreta de tempo
        inicio_execucao = tempo_atual
        fim_execucao = tempo_atual + 1
        duracao_executada = escolhido.adicionar_processamento(inicio_execucao, fim_execucao)
        tempo_atual += duracao_executada

        ultimo_processo_id = escolhido.id

        # Liberação do recurso ao fim da seção crítica e restauração de prioridade
        if dono_id == escolhido.id:
            if escolhido.sc_fim is not None and escolhido.tempo_executado >= escolhido.sc_fim:
                escolhido.prioridade_efetiva = escolhido.prioridade_base
                dono_id = None

                for p in processos:
                    if p.bloqueado:
                        p.bloqueado = False

        # 9. Conclusão do processo
        if escolhido.terminou():
            if dono_id == escolhido.id:
                escolhido.prioridade_efetiva = escolhido.prioridade_base
                dono_id = None

            escolhido.bloqueado = False
            pendentes.remove(escolhido)

    # Restauração final das prioridades originais
    for p in processos:
        p.prioridade_efetiva = p.prioridade_base

        if hasattr(p.prioridade, "numero"):
            p.prioridade.numero = p.prioridade_base
        else:
            p.prioridade = p.prioridade_base

        p.bloqueado = False

    # Cálculo das métricas oficiais
    if not processos:
        return 0, 0, "Teto de Prioridade"

    media_execucao = sum(p.get_turnaround() for p in processos) / len(processos)
    media_espera = sum(p.get_espera() for p in processos) / len(processos)
    media_primeria_execucao = sum(p.get_tempo_primeira_execucao() for p in processos) / len(processos)

    return media_espera, media_execucao, media_primeria_execucao, "Teto de Prioridade"