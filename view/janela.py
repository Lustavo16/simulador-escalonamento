import copy
import tkinter as tk
import csv
from tkinter import filedialog, messagebox, ttk

from control import simular_escalonamento
from model import Processo
from model.prioridade import Prioridade
from view import grafico_processos
from control.gerador_cenarios.gerador_cenarios import gerar_cenario
from view.simulacao_lotes import configurar_tela_lotes

processos = []


def adicionar_processo():
    try:
        chegada = int(entrada_chegada.get().strip())
        duracao = int(entrada_duracao.get().strip())
        prioridade_num = int(entrada_prioridade.get().strip())

        # Leitura dos campos opcionais de Seção Crítica
        sc_inicio_str = entrada_sc_inicio.get().strip()
        sc_duracao_str = entrada_sc_duracao.get().strip()

        sc_inicio = None
        sc_duracao = None

        if sc_inicio_str or sc_duracao_str:
            if not (sc_inicio_str and sc_duracao_str):
                messagebox.showerror(
                    "Erro",
                    "Para definir seção crítica, informe início e duração."
                )
                return

            sc_inicio = int(sc_inicio_str)
            sc_duracao = int(sc_duracao_str)

            # Validação R2: Seção crítica deve estar contida na duração da tarefa
            if (
                sc_inicio < 0
                or sc_duracao <= 0
                or (sc_inicio + sc_duracao) > duracao
            ):
                messagebox.showerror(
                    "Erro",
                    "A seção crítica deve ser válida e estar contida na duração da tarefa."
                )
                return

        novo_id = (
            max(processo.id for processo in processos) + 1
            if processos else 1
        )

        processo = Processo(
            novo_id,
            chegada,
            duracao,
            Prioridade(prioridade_num),
            sc_inicio=sc_inicio,
            sc_duracao=sc_duracao
        )

        processos.append(processo)

        sc_texto = (
            f", SC: [{sc_inicio}, {sc_inicio + sc_duracao})"
            if sc_inicio is not None
            else ""
        )

        lista_processos.insert(
            tk.END,
            f"ID: {novo_id}, Chegada: {chegada}, "
            f"Duração: {duracao}, Prioridade: {prioridade_num}{sc_texto}"
        )

        # Limpar campos de entrada
        entrada_chegada.delete(0, tk.END)
        entrada_duracao.delete(0, tk.END)
        entrada_prioridade.delete(0, tk.END)
        entrada_sc_inicio.delete(0, tk.END)
        entrada_sc_duracao.delete(0, tk.END)

    except ValueError:
        messagebox.showerror(
            "Erro",
            "Valores inválidos. Use apenas números inteiros."
        )


def remover_processo():
    if len(lista_processos.curselection()):
        index_selecionado = lista_processos.curselection()[0]
        lista_processos.delete(index_selecionado)
        processos.pop(index_selecionado)

    elif processos:
        processos.pop()
        lista_processos.delete(lista_processos.size() - 1)


def editar_processo():
    if len(lista_processos.curselection()):
        index_selecionado = lista_processos.curselection()[0]
        processo_selecionado = processos[index_selecionado]

        entrada_chegada.delete(0, tk.END)
        entrada_chegada.insert(0, processo_selecionado.chegada)

        entrada_duracao.delete(0, tk.END)
        entrada_duracao.insert(0, processo_selecionado.duracao)

        entrada_prioridade.delete(0, tk.END)

        p_val = (
            processo_selecionado.prioridade.numero
            if hasattr(processo_selecionado.prioridade, 'numero')
            else processo_selecionado.prioridade
        )

        entrada_prioridade.insert(0, p_val)

        entrada_sc_inicio.delete(0, tk.END)
        if getattr(processo_selecionado, 'sc_inicio', None) is not None:
            entrada_sc_inicio.insert(0, processo_selecionado.sc_inicio)

        entrada_sc_duracao.delete(0, tk.END)
        if getattr(processo_selecionado, 'sc_duracao', None) is not None:
            entrada_sc_duracao.insert(0, processo_selecionado.sc_duracao)

        lista_processos.delete(index_selecionado)
        processos.pop(index_selecionado)

def exportar_processos():
    if not processos:
        messagebox.showwarning(
            "Aviso",
            "Não há processos para exportar."
        )
        return

    caminho = filedialog.asksaveasfilename(
        title="Exportar tarefas",
        defaultextension=".csv",
        filetypes=[
            ("Arquivo CSV", "*.csv"),
            ("Todos os arquivos", "*.*")
        ]
    )

    if not caminho:
        return

    try:
        with open(
            caminho,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as arquivo:
            escritor = csv.writer(arquivo)

            escritor.writerow([
                "id",
                "chegada",
                "duracao",
                "prioridade",
                "sc_inicio",
                "sc_duracao"
            ])

            for processo in processos:
                prioridade_num = (
                    processo.prioridade.numero
                    if hasattr(processo.prioridade, "numero")
                    else processo.prioridade
                )

                escritor.writerow([
                    processo.id,
                    processo.chegada,
                    processo.duracao,
                    prioridade_num,
                    getattr(processo, "sc_inicio", None)
                    if getattr(processo, "sc_inicio", None) is not None
                    else "",
                    getattr(processo, "sc_duracao", None)
                    if getattr(processo, "sc_duracao", None) is not None
                    else ""
                ])

        messagebox.showinfo(
            "Exportação concluída",
            "A lista de tarefas foi exportada com sucesso."
        )

    except Exception as e:
        messagebox.showerror(
            "Erro",
            f"Não foi possível exportar as tarefas.\n\n{e}"
        )


def importar_processos():
    caminho = filedialog.askopenfilename(
        title="Importar tarefas",
        filetypes=[
            ("Arquivo CSV", "*.csv"),
            ("Todos os arquivos", "*.*")
        ]
    )

    if not caminho:
        return

    try:
        novos_processos = []

        with open(
            caminho,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as arquivo:
            leitor = csv.DictReader(arquivo)

            campos_obrigatorios = {
                "id",
                "chegada",
                "duracao",
                "prioridade",
                "sc_inicio",
                "sc_duracao"
            }

            if not campos_obrigatorios.issubset(
                set(leitor.fieldnames or [])
            ):
                raise ValueError(
                    "O arquivo CSV não possui o formato esperado."
                )

            for linha_numero, linha in enumerate(leitor, start=2):
                try:
                    processo_id = int(linha["id"])
                    chegada = int(linha["chegada"])
                    duracao = int(linha["duracao"])
                    prioridade_num = int(linha["prioridade"])

                    sc_inicio_str = linha["sc_inicio"].strip()
                    sc_duracao_str = linha["sc_duracao"].strip()

                    sc_inicio = None
                    sc_duracao = None

                    if sc_inicio_str or sc_duracao_str:
                        if not (
                            sc_inicio_str
                            and sc_duracao_str
                        ):
                            raise ValueError(
                                "Início e duração da SC devem "
                                "ser informados juntos."
                            )

                        sc_inicio = int(sc_inicio_str)
                        sc_duracao = int(sc_duracao_str)

                        if (
                            sc_inicio < 0
                            or sc_duracao <= 0
                            or sc_inicio + sc_duracao > duracao
                        ):
                            raise ValueError(
                                "A seção crítica é inválida "
                                "ou ultrapassa a duração."
                            )

                    if processo_id <= 0:
                        raise ValueError(
                            "O ID deve ser maior que zero."
                        )

                    if chegada < 0:
                        raise ValueError(
                            "A chegada não pode ser negativa."
                        )

                    if duracao <= 0:
                        raise ValueError(
                            "A duração deve ser maior que zero."
                        )

                    novos_processos.append(
                        Processo(
                            processo_id,
                            chegada,
                            duracao,
                            Prioridade(prioridade_num),
                            sc_inicio=sc_inicio,
                            sc_duracao=sc_duracao
                        )
                    )

                except (ValueError, TypeError) as e:
                    raise ValueError(
                        f"Erro na linha {linha_numero}: {e}"
                    )

        if not novos_processos:
            messagebox.showwarning(
                "Aviso",
                "O arquivo não possui tarefas."
            )
            return

        if processos:
            confirmar = messagebox.askyesno(
                "Importar tarefas",
                "Os processos atuais serão substituídos. "
                "Deseja continuar?"
            )

            if not confirmar:
                return

        processos.clear()
        processos.extend(novos_processos)

        lista_processos.delete(
            0,
            tk.END
        )

        for processo in processos:
            prioridade_num = (
                processo.prioridade.numero
                if hasattr(processo.prioridade, "numero")
                else processo.prioridade
            )

            sc_texto = (
                f", SC: [{processo.sc_inicio}, "
                f"{processo.sc_inicio + processo.sc_duracao})"
                if getattr(processo, "sc_inicio", None) is not None
                else ""
            )

            lista_processos.insert(
                tk.END,
                f"ID: {processo.id}, "
                f"Chegada: {processo.chegada}, "
                f"Duração: {processo.duracao}, "
                f"Prioridade: {prioridade_num}"
                f"{sc_texto}"
            )

        messagebox.showinfo(
            "Importação concluída",
            f"{len(novos_processos)} tarefa(s) importada(s) com sucesso."
        )

    except Exception as e:
        messagebox.showerror(
            "Erro",
            f"Não foi possível importar as tarefas.\n\n{e}"
        )

def gerar_cenario_interface():
    try:
        quantidade = int(
            quantidade_cenario_entry.get().strip()
        )

        chegada_max = int(
            chegada_max_entry.get().strip()
        )

        duracao_max = int(
            duracao_max_entry.get().strip()
        )

        prioridade_max = int(
            prioridade_max_entry.get().strip()
        )

        if quantidade <= 0:
            messagebox.showerror(
                "Erro",
                "A quantidade de tarefas deve ser maior que zero."
            )
            return

        if chegada_max < 0:
            messagebox.showerror(
                "Erro",
                "A chegada máxima não pode ser negativa."
            )
            return

        if duracao_max <= 0:
            messagebox.showerror(
                "Erro",
                "A duração máxima deve ser maior que zero."
            )
            return

        if prioridade_max <= 0:
            messagebox.showerror(
                "Erro",
                "A prioridade máxima deve ser maior que zero."
            )
            return

        if processos:
            confirmar = messagebox.askyesno(
                "Gerar cenário",
                "Os processos atuais serão substituídos. Deseja continuar?"
            )

            if not confirmar:
                return

        novo_cenario = gerar_cenario(
            quantidade,
            chegada_max,
            duracao_max,
            prioridade_max
        )

        processos.clear()
        processos.extend(novo_cenario)

        lista_processos.delete(
            0,
            tk.END
        )

        for processo in processos:
            prioridade_num = (
                processo.prioridade.numero
                if hasattr(processo.prioridade, "numero")
                else processo.prioridade
            )

            sc_texto = (
                f", SC: [{processo.sc_inicio}, "
                f"{processo.sc_inicio + processo.sc_duracao})"
                if getattr(processo, "sc_inicio", None) is not None
                else ""
            )

            lista_processos.insert(
                tk.END,
                f"ID: {processo.id}, "
                f"Chegada: {processo.chegada}, "
                f"Duração: {processo.duracao}, "
                f"Prioridade: {prioridade_num}"
                f"{sc_texto}"
            )

    except ValueError:
        messagebox.showerror(
            "Erro",
            "Informe valores inteiros válidos para os parâmetros."
        )

    except Exception as e:
        messagebox.showerror(
            "Erro",
            str(e)
        )

def form_submit():
    try:
        if not processos:
            messagebox.showwarning(
                "Aviso",
                "Adicione ao menos um processo antes de simular."
            )
            return

        processos_submit = copy.deepcopy(processos)

        algoritmo = algoritmo_var.get()

        quantum = (
            int(quantum_entry.get().strip())
            if quantum_entry.get().strip()
            else 2
        )

        ctx_time = (
            float(ctx_entry.get().strip())
            if ctx_entry.get().strip()
            else 0.0
        )

        # Lê o valor do Alpha do Aging
        alpha = (
            float(alpha_entry.get().strip())
            if alpha_entry.get().strip()
            else 0.0
        )

        if alpha < 0:
            messagebox.showerror(
                "Erro",
                "O Alpha do Aging não pode ser negativo."
            )
            return

        if algoritmo == 3 and quantum <= ctx_time:
            messagebox.showerror(
                "Erro",
                "Sob Round-Robin, o quantum deve ser maior que a troca de contexto."
            )
            return

        resultado = simular_escalonamento(
            processos_submit,
            algoritmo,
            quantum,
            ctx_time,
            alpha
        )
        
        media_execucao, media_espera, media_primeira_execucao, nome_processo = resultado

        grafico_processos(
            processos_submit,
            media_execucao,
            media_espera,
            media_primeira_execucao,
            nome_processo
        )

    except Exception as e:
        messagebox.showerror("Erro", str(e))


def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    pos_x = (largura_tela // 2) - (largura // 2)
    pos_y = (altura_tela // 2) - (altura // 2)

    janela.geometry(
        f'{largura}x{altura}+{pos_x}+{pos_y}'
    )


def habilitar_quantum():
    if algoritmo_var.get() == 3:
        quantum_label.pack(padx=20, pady=2)
        quantum_entry.pack(padx=20, pady=2)
    else:
        quantum_label.pack_forget()
        quantum_entry.pack_forget()

    if algoritmo_var.get() in (5, 6):
        alpha_label.pack(pady=2)
        alpha_entry.pack(pady=2)
    else:
        alpha_label.pack_forget()
        alpha_entry.pack_forget()


def criar_janela():
    global entrada_chegada, entrada_duracao, entrada_prioridade
    global entrada_sc_inicio, entrada_sc_duracao
    global lista_processos, algoritmo_var
    global quantum_label, quantum_entry
    global ctx_label, ctx_entry
    global alpha_label, alpha_entry
    global gerador_label, gerador_frame
    global quantidade_cenario_entry
    global chegada_max_entry
    global duracao_max_entry
    global prioridade_max_entry

    janela = tk.Tk()
    janela.title("Simulador de Escalonamento")
    janela.configure(bg="#FFFFFF")
    janela.resizable(False, False)

    centralizar_janela(janela, 900, 900)

    algoritmo_var = tk.IntVar(value=1)

    processos_label = tk.Label(
        janela,
        text="Defina os processos",
        font=("Calibri", 18, "bold"),
        fg="#0D0D0D",
        bg="#FFFFFF"
    )
    processos_label.pack(pady=5)

    input_form_frame = tk.Frame(
        janela,
        bg="#FFFFFF"
    )
    input_form_frame.pack(pady=5)

    # Campos Básicos
    tk.Label(
        input_form_frame,
        text="Chegada:",
        font=("Calibri", 11),
        bg="#FFFFFF"
    ).grid(row=0, column=0, padx=4)

    entrada_chegada = tk.Entry(
        input_form_frame,
        width=8,
        bd=2,
        font=("Calibri", 11),
        justify="center"
    )
    entrada_chegada.grid(row=1, column=0, padx=4, pady=3)

    tk.Label(
        input_form_frame,
        text="Duração:",
        font=("Calibri", 11),
        bg="#FFFFFF"
    ).grid(row=0, column=1, padx=4)

    entrada_duracao = tk.Entry(
        input_form_frame,
        width=8,
        bd=2,
        font=("Calibri", 11),
        justify="center"
    )
    entrada_duracao.grid(row=1, column=1, padx=4, pady=3)

    tk.Label(
        input_form_frame,
        text="Prioridade:",
        font=("Calibri", 11),
        bg="#FFFFFF"
    ).grid(row=0, column=2, padx=4)

    entrada_prioridade = tk.Entry(
        input_form_frame,
        width=8,
        bd=2,
        font=("Calibri", 11),
        justify="center"
    )
    entrada_prioridade.grid(row=1, column=2, padx=4, pady=3)

    # Campos Opcionais de Seção Crítica
    tk.Label(
        input_form_frame,
        text="Início SC:",
        font=("Calibri", 11),
        bg="#FFFFFF"
    ).grid(row=0, column=3, padx=4)

    entrada_sc_inicio = tk.Entry(
        input_form_frame,
        width=8,
        bd=2,
        font=("Calibri", 11),
        justify="center"
    )
    entrada_sc_inicio.grid(row=1, column=3, padx=4, pady=3)

    tk.Label(
        input_form_frame,
        text="Duração SC:",
        font=("Calibri", 11),
        bg="#FFFFFF"
    ).grid(row=0, column=4, padx=4)

    entrada_sc_duracao = tk.Entry(
        input_form_frame,
        width=8,
        bd=2,
        font=("Calibri", 11),
        justify="center"
    )
    entrada_sc_duracao.grid(row=1, column=4, padx=4, pady=3)

    buttons_form_frame = tk.Frame(
        janela,
        bg="#FFFFFF"
    )
    buttons_form_frame.pack(pady=6)

    tk.Button(
        buttons_form_frame,
        text="Adicionar Processo",
        command=adicionar_processo,
        font=("Calibri", 11),
        fg="#FFFFFF",
        bg="#4682B4"
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        buttons_form_frame,
        text="Remover Processo",
        command=remover_processo,
        font=("Calibri", 11),
        fg="#FFFFFF",
        bg="#B74343"
    ).grid(row=0, column=1, padx=5)

    tk.Button(
        buttons_form_frame,
        text="Editar Processo",
        command=editar_processo,
        font=("Calibri", 11),
        fg="#FFFFFF",
        bg="#44B649"
    ).grid(row=0, column=2, padx=5)

    container_tabela = tk.Frame(janela, bg="white")
    container_tabela.pack(padx=10, pady=6)

    lista_processos = tk.Listbox(
        container_tabela,
        width=70,
        height=5,
        bd=2,
        font=("Calibri", 11),
        justify="center"
    )
    lista_processos.pack(side="left", padx=(0, 10))

    botoes_csv_frame = tk.Frame(container_tabela, bg="white")
    botoes_csv_frame.pack(side="left", fill="y", pady=(10, 0))

    tk.Button(
        botoes_csv_frame,
        text="Importar CSV",
        command=importar_processos,
        font=("Calibri", 11),
        fg="#FFFFFF",
        bg="#6A5ACD",
        width=12
    ).pack(pady=(0, 5), fill="x")

    tk.Button(
        botoes_csv_frame,
        text="Exportar CSV",
        command=exportar_processos,
        font=("Calibri", 11),
        fg="#FFFFFF",
        bg="#4682B4",
        width=12
    ).pack(pady=(5, 0), fill="x")

    gerador_label = tk.Label(
        janela,
        text="Gerador de cenários",
        font=("Calibri", 16, "bold"),
        fg="#0D0D0D",
        bg="#FFFFFF"
    )
    gerador_label.pack(pady=5)

    gerador_frame = tk.Frame(
        janela,
        bg="#FFFFFF"
    )
    gerador_frame.pack(pady=2)

    tk.Label(
        gerador_frame,
        text="Número de tarefas:",
        font=("Calibri", 11),
        bg="#FFFFFF"
    ).grid(row=0, column=0, padx=5)

    quantidade_cenario_entry = tk.Entry(
        gerador_frame,
        width=8,
        bd=2,
        font=("Calibri", 11),
        justify="center"
    )
    quantidade_cenario_entry.grid(
        row=1,
        column=0,
        padx=5,
        pady=3
    )

    quantidade_cenario_entry.insert(0, "10")

    tk.Label(
        gerador_frame,
        text="Chegada máxima:",
        font=("Calibri", 11),
        bg="#FFFFFF"
    ).grid(row=0, column=1, padx=5)

    chegada_max_entry = tk.Entry(
        gerador_frame,
        width=8,
        bd=2,
        font=("Calibri", 11),
        justify="center"
    )
    chegada_max_entry.grid(
        row=1,
        column=1,
        padx=5,
        pady=3
    )

    chegada_max_entry.insert(0, "8")

    tk.Label(
        gerador_frame,
        text="Duração máxima:",
        font=("Calibri", 11),
        bg="#FFFFFF"
    ).grid(row=0, column=2, padx=5)

    duracao_max_entry = tk.Entry(
        gerador_frame,
        width=8,
        bd=2,
        font=("Calibri", 11),
        justify="center"
    )
    duracao_max_entry.grid(
        row=1,
        column=2,
        padx=5,
        pady=3
    )

    duracao_max_entry.insert(0, "6")

    tk.Label(
        gerador_frame,
        text="Prioridade máxima:",
        font=("Calibri", 11),
        bg="#FFFFFF"
    ).grid(row=0, column=3, padx=5)

    prioridade_max_entry = tk.Entry(
        gerador_frame,
        width=8,
        bd=2,
        font=("Calibri", 11),
        justify="center"
    )
    prioridade_max_entry.grid(
        row=1,
        column=3,
        padx=5,
        pady=3
    )

    prioridade_max_entry.insert(0, "5")

    tk.Button(
        gerador_frame,
        text="Gerar cenário",
        command=gerar_cenario_interface,
        font=("Calibri", 11),
        fg="#FFFFFF",
        bg="#6A5ACD"
    ).grid(
        row=1,
        column=4,
        padx=10
    )

    algoritmo_label = tk.Label(
        janela,
        text="Escolha o algoritmo de escalonamento",
        font=("Calibri", 16, "bold"),
        fg="#0D0D0D",
        bg="#FFFFFF"
    )
    algoritmo_label.pack(pady=5)

    radio_frame = tk.Frame(
        janela,
        bg="#FFFFFF"
    )
    radio_frame.pack(pady=5)

    tk.Radiobutton(
        radio_frame,
        text="1. FCFS",
        variable=algoritmo_var,
        value=1,
        command=habilitar_quantum,
        font=("Calibri", 12),
        bg="#FFFFFF"
    ).grid(row=0, column=0, sticky="w", padx=25)

    tk.Radiobutton(
        radio_frame,
        text="2. SJF",
        variable=algoritmo_var,
        value=2,
        command=habilitar_quantum,
        font=("Calibri", 12),
        bg="#FFFFFF"
    ).grid(row=1, column=0, sticky="w", padx=25)

    tk.Radiobutton(
        radio_frame,
        text="3. Round Robin",
        variable=algoritmo_var,
        value=3,
        command=habilitar_quantum,
        font=("Calibri", 12),
        bg="#FFFFFF"
    ).grid(row=2, column=0, sticky="w", padx=25)

    tk.Radiobutton(
        radio_frame,
        text="4. SRTF",
        variable=algoritmo_var,
        value=4,
        command=habilitar_quantum,
        font=("Calibri", 12),
        bg="#FFFFFF"
    ).grid(row=3, column=0, sticky="w", padx=25)

    tk.Radiobutton(
        radio_frame,
        text="5. Prioridade cooperativo",
        variable=algoritmo_var,
        value=5,
        command=habilitar_quantum,
        font=("Calibri", 12),
        bg="#FFFFFF"
    ).grid(row=0, column=1, sticky="w", padx=25)

    tk.Radiobutton(
        radio_frame,
        text="6. Prioridade preemptivo",
        variable=algoritmo_var,
        value=6,
        command=habilitar_quantum,
        font=("Calibri", 12),
        bg="#FFFFFF"
    ).grid(row=1, column=1, sticky="w", padx=25)

    tk.Radiobutton(
        radio_frame,
        text="7. Inversão de prioridade",
        variable=algoritmo_var,
        value=7,
        command=habilitar_quantum,
        font=("Calibri", 12),
        bg="#FFFFFF"
    ).grid(row=2, column=1, sticky="w", padx=25)

    tk.Radiobutton(
        radio_frame,
        text="8. Herança de prioridade",
        variable=algoritmo_var,
        value=8,
        command=habilitar_quantum,
        font=("Calibri", 12),
        bg="#FFFFFF"
    ).grid(row=3, column=1, sticky="w", padx=25)

    tk.Radiobutton(
        radio_frame,
        text="9. Teto de prioridade",
        variable=algoritmo_var,
        value=9,
        command=habilitar_quantum,
        font=("Calibri", 12),
        bg="#FFFFFF"
    ).grid(row=4, column=1, sticky="w", padx=25)

    alpha_label = tk.Label(
        janela,
        text="Alpha do Aging:",
        font=("Calibri", 12),
        bg="#FFFFFF"
    )

    alpha_entry = tk.Entry(
        janela,
        bd=2,
        font=("Calibri", 12),
        justify="center",
        width=10
    )

    alpha_entry.insert(0, "0")

    quantum_label = tk.Label(
        janela,
        text="Quantum para Round Robin:",
        font=("Calibri", 12),
        bg="#FFFFFF"
    )

    quantum_entry = tk.Entry(
        janela,
        bd=2,
        font=("Calibri", 12),
        justify="center",
        width=10
    )

    quantum_entry.insert(0, "2")

    ctx_label = tk.Label(
        janela,
        text="Tempo de troca de contexto (s):",
        font=("Calibri", 12),
        bg="#FFFFFF"
    )

    ctx_entry = tk.Entry(
        janela,
        bd=2,
        font=("Calibri", 12),
        justify="center",
        width=10
    )

    ctx_entry.insert(0, "0")

    ctx_label.pack(pady=2)
    ctx_entry.pack(pady=2)

    tk.Button(
        janela,
        text="Simular",
        command=form_submit,
        font=("Calibri", 15, "bold"),
        fg="#FFFFFF",
        bg="#FFA500",
        activeforeground="#FFFFFF",
        activebackground="#CC8400",
        width=14
    ).pack(pady=15)

    botao_lotes = tk.Button(
        janela,
        text="Simular em lotes",
        command=lambda: abrir_simulacao_lotes(janela),
        font=("Calibri", 15, "bold"),
        fg="#FFFFFF",
        bg="#FFA500",
        activeforeground="#FFFFFF",
        activebackground="#CC8400",
        width=14
    )
    botao_lotes.pack(pady=10)

    janela.mainloop()

def abrir_simulacao_lotes(janela):
    janela_lotes = tk.Toplevel(janela)
    janela_lotes.title("Simulação em Lotes")
    janela_lotes.geometry("500x450")
    janela_lotes.resizable(False, False)

    centralizar_janela(janela_lotes, 400, 450)

    configurar_tela_lotes(janela_lotes)
