from abc import ABC, abstractmethod

from excecoes import PagamentoRecusadoError


class Pagamento(ABC):
    """Superclasse abstrata das formas de pagamento."""

    def __init__(self, valor: float):
        if valor <= 0:
            raise ValueError("O valor do pagamento deve ser positivo.")
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    @abstractmethod
    def processar(self) -> str:
        """Processa o pagamento e devolve o comprovante (polimórfico)."""


class PagamentoDinheiro(Pagamento):
    def __init__(self, valor: float, valor_entregue: float):
        super().__init__(valor)
        self._valor_entregue = valor_entregue

    def processar(self) -> str:
        if self._valor_entregue < self._valor:
            raise PagamentoRecusadoError("Valor entregue insuficiente.")
        troco = self._valor_entregue - self._valor
        return f"Dinheiro: R$ {self._valor:.2f} recebido, troco R$ {troco:.2f}"


class PagamentoCartao(Pagamento):
    MAX_PARCELAS = 12

    def __init__(self, valor: float, numero: str, parcelas: int = 1):
        super().__init__(valor)
        digitos = "".join(c for c in numero if c.isdigit())
        if len(digitos) != 16:
            raise ValueError("O cartão deve ter 16 dígitos.")
        if not 1 <= parcelas <= self.MAX_PARCELAS:
            raise ValueError(f"Parcelas devem ficar entre 1 e {self.MAX_PARCELAS}.")
        self._final = digitos[-4:]
        self._parcelas = parcelas

    def processar(self) -> str:
        parcela = self._valor / self._parcelas
        return f"Cartão final {self._final}: {self._parcelas}x de R$ {parcela:.2f}"


class PagamentoPix(Pagamento):
    def __init__(self, valor: float, chave: str):
        super().__init__(valor)
        if not chave or not chave.strip():
            raise ValueError("A chave Pix não pode ser vazia.")
        self._chave = chave.strip()

    def processar(self) -> str:
        return f"Pix: R$ {self._valor:.2f} para a chave {self._chave}"