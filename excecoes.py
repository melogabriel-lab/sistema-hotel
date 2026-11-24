class HotelError(Exception):
    """Erro base do sistema de hotel."""


class QuartoNaoEncontradoError(HotelError):
    """O número de quarto informado não existe no hotel."""


class QuartoIndisponivelError(HotelError):
    """O quarto já está reservado no período solicitado."""


class ReservaInvalidaError(HotelError):
    """Operação ou dados inválidos para uma reserva."""


class PagamentoRecusadoError(HotelError):
    """O pagamento não pôde ser processado."""