from abc import ABC, abstractmethod


class Quarto(ABC):
    """Superclasse abstrata dos quartos do hotel."""

    def __init__(self, numero: int, diaria_base: float):
        if numero <= 0:
            raise ValueError("O número do quarto deve ser positivo.")
        if diaria_base <= 0:
            raise ValueError("A diária base deve ser positiva.")
        self._numero = numero
        self._diaria_base = diaria_base

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def diaria_base(self) -> float:
        return self._diaria_base

    @abstractmethod
    def calcular_diaria(self) -> float:
        """Valor da diária (polimórfico: cada tipo de quarto calcula o seu)."""

    def descricao(self) -> str:
        return f"{type(self).__name__} {self._numero} - R$ {self.calcular_diaria():.2f}/noite"


class QuartoSimples(Quarto):
    def calcular_diaria(self) -> float:
        return round(self._diaria_base, 2)


class QuartoLuxo(Quarto):
    ADICIONAL = 1.8

    def calcular_diaria(self) -> float:
        return round(self._diaria_base * self.ADICIONAL, 2)


class Suite(Quarto):
    ADICIONAL = 2.5
    TAXA_CAFE_DA_MANHA = 45.0

    def calcular_diaria(self) -> float:
        return round(self._diaria_base * self.ADICIONAL + self.TAXA_CAFE_DA_MANHA, 2)