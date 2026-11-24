from __future__ import annotations

from datetime import date

from excecoes import QuartoIndisponivelError, QuartoNaoEncontradoError
from pessoas import Funcionario, Hospede
from quartos import Quarto, QuartoLuxo, QuartoSimples, Suite
from reservas import Periodo, Reserva


class Hotel:
    _TIPOS_QUARTO = {"simples": QuartoSimples, "luxo": QuartoLuxo, "suite": Suite}

    def __init__(self, nome: str):
        if not nome or not nome.strip():
            raise ValueError("O nome do hotel não pode ser vazio.")
        self._nome = nome.strip()
        self._quartos: dict[int, Quarto] = {}  # composição: o hotel cria os quartos
        self._reservas: list[Reserva] = []  # composição: o hotel cria as reservas
        self._funcionarios: list[Funcionario] = []  # associação

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def quartos(self) -> list[Quarto]:
        return list(self._quartos.values())

    @property
    def reservas(self) -> list[Reserva]:
        return list(self._reservas)

    @property
    def funcionarios(self) -> list[Funcionario]:
        return list(self._funcionarios)

    def adicionar_quarto(self, numero: int, tipo: str, diaria_base: float) -> Quarto:
        classe = self._TIPOS_QUARTO.get(tipo.lower())
        if classe is None:
            raise ValueError(f"Tipo de quarto inválido: {tipo}.")
        if numero in self._quartos:
            raise ValueError(f"O quarto {numero} já existe.")
        quarto = classe(numero, diaria_base)
        self._quartos[numero] = quarto
        return quarto

    def buscar_quarto(self, numero: int) -> Quarto:
        try:
            return self._quartos[numero]
        except KeyError:
            raise QuartoNaoEncontradoError(f"O quarto {numero} não existe.") from None

    def contratar(self, funcionario: Funcionario) -> None:
        if not isinstance(funcionario, Funcionario):
            raise TypeError("Só é possível contratar um Funcionario.")
        self._funcionarios.append(funcionario)

    def quarto_disponivel(self, numero: int, entrada: date, saida: date) -> bool:
        self.buscar_quarto(numero)
        periodo = Periodo(entrada, saida)  # dependência: uso local de Periodo
        return not any(
            r.quarto.numero == numero
            and r.ocupa_quarto
            and r.periodo.conflita_com(periodo)
            for r in self._reservas
        )

    def quartos_disponiveis(self, entrada: date, saida: date) -> list[Quarto]:
        return [
            q for q in self._quartos.values()
            if self.quarto_disponivel(q.numero, entrada, saida)
        ]

    def reservar(self, hospede: Hospede, numero: int, entrada: date, saida: date) -> Reserva:
        quarto = self.buscar_quarto(numero)
        if not self.quarto_disponivel(numero, entrada, saida):
            raise QuartoIndisponivelError(
                f"O quarto {numero} está ocupado no período solicitado."
            )
        reserva = Reserva(hospede, quarto, entrada, saida)
        self._reservas.append(reserva)
        return reserva

    def taxa_ocupacao(self, dia: date) -> float:
        if not self._quartos:
            return 0.0
        ocupados = {
            r.quarto.numero
            for r in self._reservas
            if r.ocupa_quarto and r.periodo.contem(dia)
        }
        return len(ocupados) / len(self._quartos)

    def folha_salarial(self) -> float:
        return round(sum(f.calcular_salario() for f in self._funcionarios), 2)