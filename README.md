# Simulador de Escalonamento de Tarefas

Projeto prático da disciplina de **Sistemas Operacionais**, ministrado pelo Prof. **Vinicius S. Borges**. 8.º semestre do curso de Engenharia da Computação na FESA.

---

## Autoria

| Nome | RA |
|------|----|
| Aline Cristina R. de Barros | 081230021 |
| Gustavo A. Zaccheu | 081230023 |
| Luis Gustavo de O. Caneiro | 081230029 |
| Vitor Barbosa Carlos | 081230037 |

---

## Descrição

Simulador de escalonamento de tarefas em um processador, desenvolvido em Python com interface gráfica. O simulador implementa seis algoritmos de escalonamento — FCFS, SJF, SRTF, Round-Robin, Prioridade Cooperativa e Prioridade Preemptiva — e reproduz o fenômeno da inversão de prioridades, com os mecanismos de correção por herança de prioridade e teto de prioridade. Inclui também envelhecimento (*aging*) para eliminação de inanição e geração aleatória de cenários.

---

## Como executar
> **No GitHub ou em seu clone local (direto na pasta, não em uma IDE), clique duas vezes em `dist/SimuladorEscalonamento.exe`.**
>
> Nenhuma instalação, ambiente virtual ou linha de comando é necessária.

---

## Estrutura do repositório

```
simulador-escalonamento/
├── dist/
│   └── SimuladorEscalonamento.exe   → Executável (duplo clique para abrir)
├── main.py                          → Ponto de entrada do código-fonte
├── model/
│   ├── processo.py                  → Modelo de tarefa (Processo) e período
│   └── prioridade.py                → Classe Prioridade
├── control/
│   ├── simular_escalonamento.py     → Controlador principal (roteador de algoritmos)
│   └── algoritmos/
│       ├── fcfs.py                  → Algoritmo FCFS
│       ├── sjf.py                   → Algoritmo SJF
│       ├── srtf.py                  → Algoritmo SRTF
│       ├── roundRobin.py            → Algoritmo Round-Robin
│       ├── prioridadeCooperativo.py → Prioridade cooperativa (com aging)
│       ├── prioridadePreemptivo.py  → Prioridade preemptiva (com aging)
│       ├── inversaoDePrioridade.py  → Inversão de prioridade (cenário sem correção)
│       ├── herancaDePrioridade.py   → Herança de prioridade (R6)
│       └── tetoDePrioridade.py      → Teto de prioridade (R7)
├── control/gerador_cenarios/
│   └── gerador_cenarios.py          → Geração aleatória de cenários (R9)
├── view/
│   ├── janela.py                    → Janela principal da interface (Tkinter)
│   ├── graficoProcessos.py          → Diagrama de tempo e tabela de métricas
│   └── simulacao_lotes.py           → Tela de simulação em lotes
├── assets/                          → Recursos visuais da interface
├── cenarios/                        → Conjuntos de tarefas exportados (CSV)
├── requirements.txt                 → Dependências do código-fonte
└── docs/
    ├── tutorial_execucao.pdf       → Tutorial de execução
    ├── tutorial_uso.pdf            → Tutorial de uso
    └── documentacao_projeto.pdf    → Documentação técnica
```

---

## Arquivos de código

| Arquivo | O que faz |
|---------|-----------|
| `main.py` | Ponto de entrada: chama `criar_janela()` do módulo `view` |
| `model/processo.py` | Define as classes `Processo` e `Periodo`; calcula turnaround, espera e tempo até 1.ª execução |
| `model/prioridade.py` | Encapsula o valor numérico de prioridade de uma tarefa |
| `control/simular_escalonamento.py` | Recebe os parâmetros da interface e despacha para o algoritmo correto |
| `control/algoritmos/fcfs.py` | First-Come, First-Served |
| `control/algoritmos/sjf.py` | Shortest Job First |
| `control/algoritmos/srtf.py` | Shortest Remaining Time First |
| `control/algoritmos/roundRobin.py` | Round-Robin com quantum configurável |
| `control/algoritmos/prioridadeCooperativo.py` | Prioridade cooperativa com envelhecimento |
| `control/algoritmos/prioridadePreemptivo.py` | Prioridade preemptiva com envelhecimento |
| `control/algoritmos/inversaoDePrioridade.py` | Cenário de inversão de prioridades (sem correção) |
| `control/algoritmos/herancaDePrioridade.py` | Correção por herança de prioridade (R6) |
| `control/algoritmos/tetoDePrioridade.py` | Correção por teto de prioridade (R7) |
| `control/gerador_cenarios/gerador_cenarios.py` | Gera conjuntos aleatórios de tarefas (R9) |
| `view/janela.py` | Interface gráfica principal: entrada de tarefas, parâmetros e seleção de algoritmo |
| `view/graficoProcessos.py` | Exibe diagrama de tempo (Gantt) e tabela de métricas |
| `view/simulacao_lotes.py` | Tela de simulação em lotes para comparação entre algoritmos |

---

## Funcionalidades

| O que faz | Arquivo onde está implementado |
|-----------|-------------------------------|
| Seis algoritmos de escalonamento (R1) | `control/algoritmos/` |
| Entrada manual e sorteio de tarefas (R2) | `view/janela.py`, `control/gerador_cenarios/gerador_cenarios.py` |
| Exportar e importar conjuntos de tarefas em CSV (R2) | `view/janela.py` |
| Métricas por tarefa e em média — T_t, T_p, T_w, 1.ª exec. (R3) | `model/processo.py`, `view/graficoProcessos.py` |
| Quantum e custo de troca de contexto configuráveis (R4) | `view/janela.py`, `control/algoritmos/roundRobin.py` |
| Eficiência do escalonador (R4) | `view/graficoProcessos.py` |
| Recursos de uso exclusivo e inversão de prioridades (R5) | `control/algoritmos/inversaoDePrioridade.py` |
| Herança de prioridade (R6) | `control/algoritmos/herancaDePrioridade.py` |
| Teto de prioridade (R7) | `control/algoritmos/tetoDePrioridade.py` |
| Envelhecimento / aging (R8) | `control/algoritmos/prioridadeCooperativo.py`, `prioridadePreemptivo.py` |
| Geração aleatória de cenários e simulação em lotes (R9) | `control/gerador_cenarios/gerador_cenarios.py`, `view/simulacao_lotes.py` |
| Diagrama de tempo (Gantt) (R9) | `view/graficoProcessos.py` |
| Execução por duplo clique sem montagem de ambiente (R10) | `dist/SimuladorEscalonamento.exe` |

---

## Requisitos de ambiente (apenas para executar via código-fonte)

- Python 3.10 ou superior
- Tkinter (incluído na instalação padrão do Python)
- Matplotlib (para diagramas de tempo)

Instalar dependências:

```bash
pip install -r requirements.txt
```

> **Atenção:** o executável `dist/SimuladorEscalonamento.exe` **não exige** nenhuma dessas instalações.

---

## Documentação

- [Tutorial de execução](./docs/tutorial_execucao.pdf) — Como abrir e confirmar que o programa funciona
- [Tutorial de uso](./docs/tutorial_uso.pdf) — Como operar todas as funcionalidades do simulador
- [Documentação técnica](./docs/documentacao_projeto.pdf) — Funcionamento interno, módulos e convenções

## Por onde começar

1. Abra `dist/SimuladorEscalonamento.exe` com dois cliques
2. Siga o **Tutorial de execução** para confirmar que o programa funciona
3. Siga o **Tutorial de uso** para reproduzir um cenário conhecido
4. Consulte a **Documentação técnica** para entender o funcionamento interno
