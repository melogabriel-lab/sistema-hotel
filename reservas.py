from __future__ import annotations

from datetime import date
from enum import Enum

from excecoes import PagamentoRecusadoError, ReservaInvalidaError
from pagamentos import Pagamento
from pessoas import Hospede
from quartos import Quarto


class StatusReserva(Enum):
    ATIVA = "ativa"
    CHECKIN = "check-in realizado"
    CHECKOUT = "check-out realizado"
    CANCELADA = "cancelada"


class Periodo:
    """Intervalo de datas [entrada, saída). Só existe dentro de uma Reserva."""

    def __init__(self, entrada: date, saida: date):
        if saida <= entrada:
            raise ReservaInvalidaError("A saída deve ser posterior à entrada.")
        self._entrada = entrada
        self._saida = saida

    @property
    def entrada(self) -> date:
        return self._entrada

    @property
    def saida(self) -> date:
        return self._saida

    @property
    def noites(self) -> int:
        return (self._saida - self._entrada).days

    def conflita_com(self, outro: Periodo) -> bool:
        return self._entrada < outro._saida and outro._entrada < self._saida

    def contem(self, dia: date) -> bool:
        return self._entrada <= dia < self._saida


class Reserva:
    def __init__(self, hospede: Hospede, quarto: Quarto, entrada: date, saida: date):
        self._hospede = hospede  # associação
        self._quarto = quarto  # associação
        self._periodo = Periodo(entrada, saida)  # composição
        self._status = StatusReserva.ATIVA
        self._pagamento: Pagamento | None = None  # associação

    @property
    def hospede(self) -> Hospede:
        return self._hospede

    @property
    def quarto(self) -> Quarto:
        return self._quarto

    @property
    def periodo(self) -> Periodo:
        return self._periodo

    @property
    def status(self) -> StatusReserva:
        return self._status

    @property
    def pagamento(self) -> Pagamento | None:
        return self._pagamento

    @property
    def valor_total(self) -> float:
        return round(self._quarto.calcular_diaria() * self._periodo.noites, 2)

    @property
    def paga(self) -> bool:
        return self._pagamento is not None

    @property
    def ocupa_quarto(self) -> bool:
        return self._status in (StatusReserva.ATIVA, StatusReserva.CHECKIN)

    def pagar(self, pagamento: Pagamento) -> str:
        if self._status == StatusReserva.CANCELADA:
            raise ReservaInvalidaError("Reserva cancelada não pode ser paga.")
        if self.paga:
            raise ReservaInvalidaError("A reserva já foi paga.")
        if round(pagamento.valor, 2) != self.valor_total:
            raise PagamentoRecusadoError(
                f"O valor do pagamento deve ser R$ {self.valor_total:.2f}."
            )
        comprovante = pagamento.processar()
        self._pagamento = pagamento
        return comprovante

    def fazer_checkin(self) -> None:
        if self._status != StatusReserva.ATIVA:
            raise ReservaInvalidaError("Só reservas ativas permitem check-in.")
        self._status = StatusReserva.CHECKIN

    def fazer_checkout(self) -> None:
        if self._status != StatusReserva.CHECKIN:
            raise ReservaInvalidaError("O check-out exige check-in realizado.")
        if not self.paga:
            raise PagamentoRecusadoError("Pagamento pendente.")
        self._status = StatusReserva.CHECKOUT

    def cancelar(self) -> None:
        if self._status != StatusReserva.ATIVA:
            raise ReservaInvalidaError("Só reservas ativas podem ser canceladas.")
        self._status = StatusReserva.CANCELADA