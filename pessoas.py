from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hotel import Hotel
    from reservas import Reserva


class Pessoa(ABC):
    """Superclasse abstrata de todas as pessoas do sistema."""

    def __init__(self, nome: str, cpf: str):
        if not nome or not nome.strip():
            raise ValueError("O nome não pode ser vazio.")
        digitos = "".join(c for c in cpf if c.isdigit())
        if len(digitos) != 11:
            raise ValueError("O CPF deve ter 11 dígitos.")
        self._nome = nome.strip()
        self._cpf = digitos

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def cpf(self) -> str:
        return self._cpf

    @abstractmethod
    def descricao(self) -> str:
        """Texto descritivo (polimórfico)."""

    def __str__(self) -> str:
        return self.descricao()


class Hospede(Pessoa):
    def __init__(self, nome: str, cpf: str, telefone: str):
        super().__init__(nome, cpf)
        self._telefone = telefone

    @property
    def telefone(self) -> str:
        return self._telefone

    def descricao(self) -> str:
        return f"Hóspede {self.nome} (tel. {self._telefone})"


class Funcionario(Pessoa):
    """Superclasse abstrata dos funcionários."""

    def __init__(self, nome: str, cpf: str, salario_base: float):
        super().__init__(nome, cpf)
        if salario_base <= 0:
            raise ValueError("O salário base deve ser positivo.")
        self._salario_base = salario_base

    @property
    def salario_base(self) -> float:
        return self._salario_base

    @abstractmethod
    def calcular_salario(self) -> float:
        """Salário final (polimórfico: cada cargo calcula o seu)."""

    def descricao(self) -> str:
        return f"{type(self).__name__} {self.nome}"


class Recepcionista(Funcionario):
    BONUS_POR_CHECKIN = 20.0

    def __init__(self, nome: str, cpf: str, salario_base: float):
        super().__init__(nome, cpf, salario_base)
        self._checkins_realizados = 0

    @property
    def checkins_realizados(self) -> int:
        return self._checkins_realizados

    def calcular_salario(self) -> float:
        return self._salario_base + self.BONUS_POR_CHECKIN * self._checkins_realizados

    # Dependência: Reserva aparece só como parâmetro, não é atributo.
    def realizar_checkin(self, reserva: Reserva) -> None:
        reserva.fazer_checkin()
        self._checkins_realizados += 1

    def realizar_checkout(self, reserva: Reserva) -> None:
        reserva.fazer_checkout()


class Gerente(Funcionario):
    ADICIONAL = 1.5

    def calcular_salario(self) -> float:
        return round(self._salario_base * self.ADICIONAL, 2)

    # Dependência: Hotel aparece só como parâmetro, não é atributo.
    def gerar_relatorio(self, hotel: Hotel, dia: date) -> str:
        return (
            f"Relatório de {hotel.nome} em {dia:%d/%m/%Y}: "
            f"ocupação {hotel.taxa_ocupacao(dia):.0%}, "
            f"folha salarial R$ {hotel.folha_salarial():.2f}"
        )