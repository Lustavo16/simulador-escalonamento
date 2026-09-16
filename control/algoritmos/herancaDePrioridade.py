from model.prioridade import Prioridade


def heranca_prioridade(processos, ctx_time=0, aging_habilitado=False):
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
        p.bonus_aging = 0

        if hasattr(p.prioridade, "numero"):
            p.prioridade_base = int(p.prioridade.numero)
        else:
            p.prioridade_base = int(p.prioridade)

        p.prioridade_efetiva = p.prioridade_base
        p.tempo_espera_aging = 0

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
                raise RuntimeError("Não foi possível encontrar próximo evento.")
            tempo_atual = min(proximas_chegadas)
            continue

        # Herança de prioridade e identificação de bloqueios
        bloqueados_ids = set()
        for p in processos:
            p.prioridade_efetiva = p.prioridade_base + p.bonus_aging
            p.bloqueado = False

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
                        if p.prioridade_base > dono.prioridade_efetiva:
                            dono.prioridade_efetiva = p.prioridade_base

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
                    "Deadlock na simulação de herança de prioridade.\n"
                    f"Tempo atual: {tempo_atual}\n"
                    f"Processos pendentes: {[p.id for p in pendentes]}\n"
                    f"Processos chegados: {[p.id for p in chegados]}\n"
                    f"Bloqueados: {list(bloqueados_ids)}\n"
                    f"Dono do recurso: {dono_id}"
                )

        # Escolha do processo
        escolhido = max(aptos, key=lambda p: (p.prioridade_efetiva, -p.chegada, -p.id))

        # Entrada na seção crítica
        if escolhido.precisa_recurso():
            dono_id = escolhido.id

        # Troca de Contexto na tarefa que está ENTRANDO
        if escolhido.id != ultimo_processo_id and ctx_time > 0:
            escolhido.adicionar_troca_contexto(tempo_atual, tempo_atual + ctx_time)
            tempo_atual += ctx_time

        # Executa exatamente 1 unidade discreta de tempo
        inicio_execucao = tempo_atual
        fim_execucao = tempo_atual + 1
        duracao_executada = escolhido.adicionar_processamento(inicio_execucao, fim_execucao)
        tempo_atual += duracao_executada

        ultimo_processo_id = escolhido.id

        # Liberação do recurso ao fim da seção crítica
        if dono_id == escolhido.id:
            if escolhido.sc_fim is not None and escolhido.tempo_executado >= escolhido.sc_fim:
                dono_id = None

        # Conclusão do processo
        if escolhido.terminou():
            if dono_id == escolhido.id:
                dono_id = None
            escolhido.bloqueado = False
            pendentes.remove(escolhido)

    # Restauração das prioridades originais
    for p in processos:
        p.prioridade_efetiva = p.prioridade_base
        if hasattr(p.prioridade, "numero"):
            p.prioridade.numero = p.prioridade_base
        else:
            p.prioridade = p.prioridade_base
        p.bloqueado = False

    # Métricas
    if not processos:
        return 0, 0, "Herança de Prioridade"

    media_execucao = sum(p.get_turnaround() for p in processos) / len(processos)
    media_espera = sum(p.get_espera() for p in processos) / len(processos)
    media_primeria_execucao = sum(p.get_tempo_primeira_execucao() for p in processos) / len(processos)

    # Ordem padronizada com a interface: (Tt, Tw, Nome)
    return media_execucao, media_espera, media_primeria_execucao, "Herança de Prioridade"