import tkinter as tk
from tkinter import messagebox

from control.gerador_cenarios.gerador_lotes import executar_lote

def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    pos_x = (largura_tela // 2) - (largura // 2)
    pos_y = (altura_tela // 2) - (altura // 2)

    janela.geometry(
        f'{largura}x{altura}+{pos_x}+{pos_y}'
    )

def abrir_resultados(janela_lotes, resultados):

    janela_resultados = tk.Toplevel(janela_lotes)

    janela_resultados.title("Resultados da Simulação em Lotes")
    janela_resultados.geometry("750x400")
    janela_resultados.resizable(False, False)

    centralizar_janela(janela_resultados, 1200, 350)

    titulo = tk.Label(
        janela_resultados,
        text="Resultados da Simulação em Lotes",
        font=("Arial", 16, "bold")
    )
    titulo.pack(pady=15)

    frame_tabela = tk.Frame(janela_resultados)
    frame_tabela.pack(pady=10)

    cabecalho = [
        "Algoritmo",
        "Turnaround médio",
        "Espera média",
        "Primeira Execução"
    ]

    for coluna, texto in enumerate(cabecalho):
        label = tk.Label(
            frame_tabela,
            text=texto,
            font=("Arial", 12, "bold"),
            relief="solid",
            borderwidth=1,
            width=20
        )

        label.grid(
            row=0,
            column=coluna,
            padx=1,
            pady=1
        )

    linha = 1

    resultados_ordenados = sorted(
        resultados.items(),
        key=lambda item: (
            item[1]["turnaround_medio"],
            item[1]["espera_media"],
            item[1]["media_primeira_execucao"]
        )
    )

    for algoritmo, dados in resultados_ordenados:

        nome = dados["nome"]
        turnaround = dados["turnaround_medio"]
        espera = dados["espera_media"]
        primeira_execucao = dados["media_primeira_execucao"]

        valores = [
            nome,
            f"{turnaround:.2f}",
            f"{espera:.2f}",
            f"{primeira_execucao:.2f}"
        ]

        for coluna, valor in enumerate(valores):

            label = tk.Label(
                frame_tabela,
                text=valor,
                relief="solid",
                borderwidth=1,
                width=25
            )

            label.grid(
                row=linha,
                column=coluna,
                padx=1,
                pady=1
            )

        linha += 1

    botao_fechar = tk.Button(
        janela_resultados,
        text="Fechar",
        command=janela_resultados.destroy,
        width=20
    )

    botao_fechar.pack(pady=20)

    janela_resultados.transient(janela_lotes)
    janela_resultados.grab_set()

def configurar_tela_lotes(janela):

    titulo = tk.Label(
        janela,
        text="Simulação em Lotes",
        font=("Arial", 16, "bold")
    )
    titulo.pack(pady=15)

    frame_parametros = tk.Frame(janela)
    frame_parametros.pack(pady=10)

    # Quantidade de cenários
    tk.Label(
        frame_parametros,
        text="Quantidade de cenários:"
    ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

    entrada_cenarios = tk.Entry(frame_parametros, width=10)
    entrada_cenarios.insert(0, "50")
    entrada_cenarios.grid(row=0, column=1, padx=10, pady=8)

    # Quantidade de tarefas
    tk.Label(
        frame_parametros,
        text="Tarefas por cenário:"
    ).grid(row=1, column=0, padx=10, pady=8, sticky="w")

    entrada_tarefas = tk.Entry(frame_parametros, width=10)
    entrada_tarefas.insert(0, "5")
    entrada_tarefas.grid(row=1, column=1, padx=10, pady=8)

    # Quantum
    tk.Label(
        frame_parametros,
        text="Quantum:"
    ).grid(row=2, column=0, padx=10, pady=8, sticky="w")

    entrada_quantum = tk.Entry(frame_parametros, width=10)
    entrada_quantum.insert(0, "2")
    entrada_quantum.grid(row=2, column=1, padx=10, pady=8)

    # Chegada máxima
    tk.Label(
        frame_parametros,
        text="Chegada máxima:"
    ).grid(row=3, column=0, padx=10, pady=8, sticky="w")

    entrada_chegada_max = tk.Entry(frame_parametros, width=10)
    entrada_chegada_max.insert(0, "8")
    entrada_chegada_max.grid(row=3, column=1, padx=10, pady=8)

    # Duração máxima
    tk.Label(
        frame_parametros,
        text="Duração máxima:"
    ).grid(row=4, column=0, padx=10, pady=8, sticky="w")

    entrada_duracao_max = tk.Entry(frame_parametros, width=10)
    entrada_duracao_max.insert(0, "6")
    entrada_duracao_max.grid(row=4, column=1, padx=10, pady=8)

    # Prioridade máxima
    tk.Label(
        frame_parametros,
        text="Prioridade máxima:"
    ).grid(row=5, column=0, padx=10, pady=8, sticky="w")

    entrada_prioridade_max = tk.Entry(frame_parametros, width=10)
    entrada_prioridade_max.insert(0, "5")
    entrada_prioridade_max.grid(row=5, column=1, padx=10, pady=8)

    # Tempo de troca de contexto
    tk.Label(
        frame_parametros,
        text="Tempo de troca de contexto:"
    ).grid(row=6, column=0, padx=10, pady=8, sticky="w")

    entrada_troca_contexto = tk.Entry(frame_parametros, width=10)
    entrada_troca_contexto.insert(0, "0")
    entrada_troca_contexto.grid(row=6, column=1, padx=10, pady=8)

    # Alpha do Aging
    tk.Label(
        frame_parametros,
        text="Alpha do Aging:"
    ).grid(row=7, column=0, padx=10, pady=8, sticky="w")

    entrada_alpha = tk.Entry(frame_parametros, width=10)
    entrada_alpha.insert(0, "0")
    entrada_alpha.grid(row=7, column=1, padx=10, pady=8)

    def executar():
        try:
            quantidade_cenarios = int(entrada_cenarios.get())
            quantidade_tarefas = int(entrada_tarefas.get())
            quantum = int(entrada_quantum.get())
            chegada_max = int(entrada_chegada_max.get())
            duracao_max = int(entrada_duracao_max.get())
            prioridade_max = int(entrada_prioridade_max.get())
            troca_contexto = int(entrada_troca_contexto.get())
            alpha = int(entrada_alpha.get())

            if quantidade_cenarios <= 0:
                raise ValueError(
                    "A quantidade de cenários deve ser maior que zero."
                )

            if quantidade_tarefas <= 0:
                raise ValueError(
                    "A quantidade de tarefas deve ser maior que zero."
                )

            if quantum <= 0:
                raise ValueError(
                    "O quantum deve ser maior que zero."
                )

            if chegada_max < 0:
                raise ValueError(
                    "A chegada máxima não pode ser negativa."
                )

            if duracao_max <= 0:
                raise ValueError(
                    "A duração máxima deve ser maior que zero."
                )

            if prioridade_max <= 0:
                raise ValueError(
                    "A prioridade máxima deve ser maior que zero."
                )

            if troca_contexto < 0:
                raise ValueError(
                    "O tempo da troca de contexo deve maior ou igual a zero."
                )
            
            if alpha < 0:
                raise ValueError(
                    "O alpha do Aging deve ser maior ou igual a zero."
                )

            resultados = executar_lote(
                quantidade_cenarios,
                quantidade_tarefas,
                quantum,
                chegada_max,
                duracao_max,
                prioridade_max,
                troca_contexto,
                alpha
            )

            abrir_resultados(
                janela,
                resultados
            )

        except ValueError as erro:
            messagebox.showerror(
                "Erro",
                str(erro)
            )

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                str(erro)
            )

    botao_executar = tk.Button(
        janela,
        text="Executar lote",
        command=executar,
        width=20
    )
    botao_executar.pack(pady=20)