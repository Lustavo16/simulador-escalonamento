from model.prioridade import Prioridade


class Periodo:
    def __init__(self, inicio, fim, tipo="Execução"):
        self.inicio = inicio
        self.fim = fim
        self.tipo = tipo  # "Execução" ou "CTX"

    def get_duracao(self):
        return self.fim - self.inicio

    def contem_instante(self, instante, epsilon=0.0001):
        return self.inicio - epsilon <= instante < self.fim + epsilon


class Processo:
    def __init__(
        self,
        id,
        chegada,
        duracao,
        prioridade: Prioridade,
        sc_inicio=None,
        sc_duracao=None
    ):
        self.id = id
        self.chegada = chegada
        self.duracao = duracao
        self.prioridade = prioridade

        # Controle da execução
        self.tempo_restante = duracao
        self.tempo_executado = 0
        self.processamentos = []
        self.ultimo_contexto = None

        # Prioridade
        self.prioridade_base = (
            int(prioridade.numero)
            if hasattr(prioridade, "numero")
            else int(prioridade)
        )

        self.prioridade_efetiva = self.prioridade_base

        # Controle do Aging
        self.inicio_espera = chegada

        # Parâmetros da Seção Crítica
        self.sc_inicio = sc_inicio
        self.sc_duracao = sc_duracao

        if sc_inicio is not None and sc_duracao is not None:
            self.sc_inicio = int(sc_inicio)
            self.sc_duracao = int(sc_duracao)
            self.sc_fim = self.sc_inicio + self.sc_duracao
        else:
            self.sc_inicio = None
            self.sc_duracao = None
            self.sc_fim = None

        # Estado
        self.bloqueado = False

    def precisa_recurso(self):
        """
        Retorna True quando o processo está dentro da sua
        janela de seção crítica, considerando o tempo de CPU
        que ele já executou.
        """

        if self.sc_inicio is None or self.sc_fim is None:
            return False

        return (
            self.sc_inicio
            <= self.tempo_executado
            < self.sc_fim
        )

    def adicionar_processamento(self, inicio, fim):
        if self.tempo_restante - (fim - inicio) < 0:
            fim = inicio + self.tempo_restante

        duracao = fim - inicio

        self.processamentos.append(
            Periodo(inicio, fim)
        )

        self.tempo_restante -= duracao
        self.tempo_executado += duracao

        return duracao

    def adicionar_troca_contexto(self, inicio, fim):
        """
        Adiciona um período de troca de contexto.

        Troca de contexto NÃO consome tempo de CPU do processo.
        """

        if fim <= inicio:
            return 0

        periodo = Periodo(
            inicio,
            fim,
            "CTX"
        )

        self.processamentos.append(periodo)

        return fim - inicio

    def terminou(self):
        """
        Indica se o processo terminou sua execução.
        """

        return self.tempo_restante <= 0

    def get_turnaround(self):
        """
        Turnaround = momento do término - momento da chegada.
        """

        if not self.processamentos:
            return 0

        return self.processamentos[-1].fim - self.chegada

    def get_espera(self):
        """
        Tempo de espera = turnaround - tempo total de execução.
        """

        return self.get_turnaround() - self.duracao

    def get_tempo_primeira_execucao(self):
        """
        Retorna o tempo entre a chegada e a primeira execução.
        """

        periodos = [
            p for p in self.processamentos
            if p.tipo == "Execução"
        ]

        if not periodos:
            return 0

        return periodos[0].inicio - self.chegada

    def verificar_estado(self, instante, epsilon=0.0001):
        """
        Retorna o estado do processo no instante informado.
        """

        if instante < self.chegada - epsilon:
            return "Antes da chegada"

        if not self.processamentos:
            return "Espera"

        for periodo in self.processamentos:
            if periodo.contem_instante(instante, epsilon):
                return periodo.tipo

        # Se o instante estiver depois do último processamento
        if instante >= self.processamentos[-1].fim - epsilon:
            return "Após a chegada"

        return "Espera"

    def __str__(self):
        return f"Processo(id={self.id})"