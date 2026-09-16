import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tkinter as tk


def centralizar_grafico(fig):
    janela = fig.canvas.manager.window

    janela.update_idletasks()

    largura_janela = 1700
    altura_janela = 750

    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    pos_x = (largura_tela - largura_janela) // 2
    pos_y = (altura_tela - altura_janela) // 2

    janela.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")


def grafico_processos(
    processos,
    media_execucao,
    media_espera,
    media_primeira_execucao,
    nome_processo
):
    fig, ax = plt.subplots(figsize=(18, 8))
    plt.subplots_adjust(
        left=0.07,
        right=0.85,
        bottom=0.18,
        top=0.92
    )

    fig.canvas.manager.set_window_title(
        'Gráfico de Escalonamento'
    )

    todos_fins = [
        p.fim
        for proc in processos
        for p in proc.processamentos
    ]

    tempo_maximo = max(todos_fins) if todos_fins else 1

    ax.set_xlim(0, tempo_maximo)

    # Eixo X com marcas inteiras
    ax.set_xticks(
        range(0, int(tempo_maximo) + 1)
    )

    ax.set_yticks(
        range(1, len(processos) + 1)
    )

    ax.set_yticklabels(
        [f"t{p.id}" for p in processos]
    )

    for processo in processos:
        tempo_util_acumulado = 0

        for periodo in processo.processamentos:
            duracao = periodo.fim - periodo.inicio

            if periodo.tipo == "Execução":
                # Bloco de execução normal (Azul)
                ax.barh(
                    processo.id,
                    duracao,
                    left=periodo.inicio,
                    height=0.6,
                    color='#1E90FF',
                    edgecolor='#1E90FF'
                )

                # Marca a seção crítica com barra superior vermelha se estiver na posse do recurso
                if getattr(
                    processo,
                    'sc_inicio',
                    None
                ) is not None:

                    fim_util = (
                        tempo_util_acumulado
                        + duracao
                    )

                    inter_inicio = max(
                        tempo_util_acumulado,
                        processo.sc_inicio
                    )

                    inter_fim = min(
                        fim_util,
                        processo.sc_fim
                    )

                    if inter_inicio < inter_fim:
                        desloc_inicio = (
                            inter_inicio
                            - tempo_util_acumulado
                        )

                        largura_sc = (
                            inter_fim
                            - inter_inicio
                        )

                        # Traço vermelho no topo da barra
                        ax.barh(
                            processo.id + 0.32,
                            largura_sc,
                            left=(
                                periodo.inicio
                                + desloc_inicio
                            ),
                            height=0.06,
                            color='#B22222',
                            edgecolor='#B22222'
                        )

                tempo_util_acumulado += duracao

            elif periodo.tipo == "CTX":
                ax.barh(
                    processo.id,
                    duracao,
                    left=periodo.inicio,
                    height=0.6,
                    color='#FFD700',
                    edgecolor='#DAA520'
                )

                ax.text(
                    periodo.inicio + duracao / 2,
                    processo.id,
                    'CTX',
                    ha='center',
                    va='center',
                    fontsize=8
                )

        # Preenchimento dos intervalos de espera (vermelho suave)
        if processo.processamentos:
            tempo_ponteiro = processo.chegada

            for periodo in processo.processamentos:
                if periodo.inicio > tempo_ponteiro:
                    duracao_espera = (
                        periodo.inicio
                        - tempo_ponteiro
                    )

                    ax.barh(
                        processo.id,
                        duracao_espera,
                        left=tempo_ponteiro,
                        height=0.6,
                        color='#FF6347',
                        alpha=0.35,
                        edgecolor='#FF6347'
                    )

                tempo_ponteiro = periodo.fim

        # Textos informativos à direita
        espera = processo.get_espera()
        turnaround = processo.get_turnaround()
        primeira_execucao = (
            processo.get_tempo_primeira_execucao()
        )

        ax.text(
            tempo_maximo + 0.3,
            processo.id,
            f"Tt: {turnaround:.1f} | "
            f"Tw: {espera:.1f} | "
            f"1ª Exec.: {primeira_execucao:.1f}",
            va='center',
            fontsize=9
        )

    ax.set_xlabel(
        'Tempo (unidades discretas)'
    )

    ax.set_title(
        nome_processo,
        fontsize=14,
        fontweight='bold'
    )

    ax.grid(
        axis='x',
        linestyle='--',
        alpha=0.5
    )

    # Legendas
    p_exec = mpatches.Patch(
        color='#1E90FF',
        label=(
            f'Execução '
            f'(Tt médio = {media_execucao:.2f})'
        )
    )

    p_esp = mpatches.Patch(
        color='#FF6347',
        alpha=0.5,
        label=(
            f'Espera '
            f'(Tw médio = {media_espera:.2f})'
        )
    )

    p_primeira = mpatches.Patch(
        color='white',
        label=(
            f'1ª execução média = '
            f'{media_primeira_execucao:.2f}'
        )
    )

    p_ctx = mpatches.Patch(
        color='#FFD700',
        label='Troca de Contexto'
    )

    p_sc = mpatches.Patch(
        color='#B22222',
        label='Posse de Recurso (Seção Crítica)'
    )

    ax.legend(
        handles=[
            p_exec,
            p_esp,
            p_primeira,
            p_ctx,
            p_sc
        ],
        loc='upper center',
        bbox_to_anchor=(0.5, -0.13),
        ncol=5,
        fontsize=9
    )

    centralizar_grafico(fig)

    plt.show()