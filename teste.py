import unittest
from datetime import date

from excecoes import (
    HotelError,
    PagamentoRecusadoError,
    QuartoIndisponivelError,
    QuartoNaoEncontradoError,
    ReservaInvalidaError,
)
from hotel import Hotel
from pagamentos import Pagamento, PagamentoCartao, PagamentoDinheiro, PagamentoPix
from pessoas import Funcionario, Gerente, Hospede, Pessoa, Recepcionista
from quartos import Quarto, QuartoLuxo, QuartoSimples, Suite
from reservas import Periodo, Reserva, StatusReserva

CPF = "123.456.789-09"
CARTAO = "1234 5678 9012 3456"
D1, D2, D3, D4 = date(2026, 12, 1), date(2026, 12, 2), date(2026, 12, 3), date(2026, 12, 4)


def novo_hospede():
    return Hospede("Maria Silva", CPF, "62 99999-0000")


class TestExcecoes(unittest.TestCase):
    def test_todas_herdam_de_hotel_error(self):
        for erro in (
            QuartoNaoEncontradoError,
            QuartoIndisponivelError,
            ReservaInvalidaError,
            PagamentoRecusadoError,
        ):
            self.assertTrue(issubclass(erro, HotelError))


class TestPessoas(unittest.TestCase):
    def test_classes_abstratas_nao_instanciam(self):
        with self.assertRaises(TypeError):
            Pessoa("Ana", CPF)
        with self.assertRaises(TypeError):
            Funcionario("Ana", CPF, 2000)

    def test_hospede_valido(self):
        h = novo_hospede()
        self.assertEqual(h.nome, "Maria Silva")
        self.assertEqual(h.cpf, "12345678909")
        self.assertEqual(h.telefone, "62 99999-0000")
        self.assertIsInstance(h, Pessoa)

    def test_nome_vazio_e_cpf_invalido(self):
        with self.assertRaises(ValueError):
            Hospede("  ", CPF, "1")
        with self.assertRaises(ValueError):
            Hospede("Ana", "123", "1")

    def test_descricao_e_str(self):
        h = novo_hospede()
        self.assertEqual(h.descricao(), "Hóspede Maria Silva (tel. 62 99999-0000)")
        self.assertEqual(str(h), h.descricao())
        self.assertEqual(Gerente("Carlos", CPF, 5000).descricao(), "Gerente Carlos")

    def test_salario_base_invalido(self):
        with self.assertRaises(ValueError):
            Recepcionista("Ana", CPF, 0)

    def test_salario_polimorfico(self):
        recep = Recepcionista("Ana", CPF, 2000)
        gerente = Gerente("Carlos", CPF, 5000)
        self.assertEqual(recep.calcular_salario(), 2000)
        self.assertEqual(gerente.calcular_salario(), 7500)
        for f in (recep, gerente):
            self.assertIsInstance(f, Funcionario)
            self.assertGreater(f.calcular_salario(), f.salario_base - 1)

    def test_recepcionista_checkin_e_bonus(self):
        recep = Recepcionista("Ana", CPF, 2000)
        reserva = Reserva(novo_hospede(), QuartoSimples(1, 100), D1, D2)
        recep.realizar_checkin(reserva)
        self.assertEqual(reserva.status, StatusReserva.CHECKIN)
        self.assertEqual(recep.checkins_realizados, 1)
        self.assertEqual(recep.calcular_salario(), 2020)

    def test_recepcionista_checkout(self):
        recep = Recepcionista("Ana", CPF, 2000)
        reserva = Reserva(novo_hospede(), QuartoSimples(1, 100), D1, D2)
        reserva.pagar(PagamentoPix(100, "chave"))
        recep.realizar_checkin(reserva)
        recep.realizar_checkout(reserva)
        self.assertEqual(reserva.status, StatusReserva.CHECKOUT)

    def test_checkin_invalido_nao_conta_bonus(self):
        recep = Recepcionista("Ana", CPF, 2000)
        reserva = Reserva(novo_hospede(), QuartoSimples(1, 100), D1, D2)
        reserva.cancelar()
        with self.assertRaises(ReservaInvalidaError):
            recep.realizar_checkin(reserva)
        self.assertEqual(recep.checkins_realizados, 0)

    def test_gerente_gera_relatorio(self):
        hotel = Hotel("Hotel Central")
        hotel.adicionar_quarto(1, "simples", 100)
        hotel.adicionar_quarto(2, "luxo", 200)
        hotel.contratar(Gerente("Carlos", CPF, 4000))
        hotel.reservar(novo_hospede(), 1, D1, D3)
        relatorio = hotel.funcionarios[0].gerar_relatorio(hotel, D1)
        self.assertEqual(
            relatorio,
            "Relatório de Hotel Central em 01/12/2026: ocupação 50%, folha salarial R$ 6000.00",
        )


class TestQuartos(unittest.TestCase):
    def test_quarto_abstrato(self):
        with self.assertRaises(TypeError):
            Quarto(1, 100)

    def test_diarias_polimorficas(self):
        self.assertEqual(QuartoSimples(1, 200).calcular_diaria(), 200)
        self.assertEqual(QuartoLuxo(2, 200).calcular_diaria(), 360)
        self.assertEqual(Suite(3, 200).calcular_diaria(), 545)
        for q in (QuartoSimples(1, 100), QuartoLuxo(2, 100), Suite(3, 100)):
            self.assertIsInstance(q, Quarto)

    def test_descricao(self):
        self.assertEqual(Suite(3, 200).descricao(), "Suite 3 - R$ 545.00/noite")

    def test_propriedades(self):
        q = QuartoSimples(7, 150)
        self.assertEqual(q.numero, 7)
        self.assertEqual(q.diaria_base, 150)

    def test_dados_invalidos(self):
        with self.assertRaises(ValueError):
            QuartoSimples(0, 100)
        with self.assertRaises(ValueError):
            QuartoSimples(1, 0)


class TestPagamentos(unittest.TestCase):
    def test_pagamento_abstrato(self):
        with self.assertRaises(TypeError):
            Pagamento(10)

    def test_valor_invalido(self):
        with self.assertRaises(ValueError):
            PagamentoPix(0, "chave")

    def test_dinheiro_com_troco(self):
        p = PagamentoDinheiro(100, 150)
        self.assertEqual(p.valor, 100)
        self.assertEqual(p.processar(), "Dinheiro: R$ 100.00 recebido, troco R$ 50.00")

    def test_dinheiro_insuficiente(self):
        with self.assertRaises(PagamentoRecusadoError):
            PagamentoDinheiro(100, 50).processar()

    def test_cartao(self):
        p = PagamentoCartao(300, CARTAO, parcelas=3)
        self.assertEqual(p.processar(), "Cartão final 3456: 3x de R$ 100.00")

    def test_cartao_padrao_a_vista(self):
        self.assertEqual(
            PagamentoCartao(300, CARTAO).processar(), "Cartão final 3456: 1x de R$ 300.00"
        )

    def test_cartao_invalido(self):
        with self.assertRaises(ValueError):
            PagamentoCartao(100, "1234")
        with self.assertRaises(ValueError):
            PagamentoCartao(100, CARTAO, parcelas=0)
        with self.assertRaises(ValueError):
            PagamentoCartao(100, CARTAO, parcelas=13)

    def test_pix(self):
        self.assertEqual(
            PagamentoPix(100, " a@b.com ").processar(), "Pix: R$ 100.00 para a chave a@b.com"
        )

    def test_pix_chave_vazia(self):
        with self.assertRaises(ValueError):
            PagamentoPix(100, "  ")

    def test_processar_polimorfico(self):
        pagamentos = [
            PagamentoDinheiro(100, 100),
            PagamentoCartao(100, CARTAO),
            PagamentoPix(100, "chave"),
        ]
        for p in pagamentos:
            self.assertIsInstance(p, Pagamento)
            self.assertIsInstance(p.processar(), str)


class TestPeriodo(unittest.TestCase):
    def test_noites_e_propriedades(self):
        p = Periodo(D1, D4)
        self.assertEqual(p.noites, 3)
        self.assertEqual(p.entrada, D1)
        self.assertEqual(p.saida, D4)

    def test_saida_invalida(self):
        with self.assertRaises(ReservaInvalidaError):
            Periodo(D2, D1)
        with self.assertRaises(ReservaInvalidaError):
            Periodo(D1, D1)

    def test_conflito(self):
        self.assertTrue(Periodo(D1, D3).conflita_com(Periodo(D2, D4)))
        self.assertTrue(Periodo(D2, D4).conflita_com(Periodo(D1, D3)))
        self.assertTrue(Periodo(D1, D4).conflita_com(Periodo(D2, D3)))

    def test_periodos_adjacentes_nao_conflitam(self):
        self.assertFalse(Periodo(D1, D2).conflita_com(Periodo(D2, D3)))

    def test_contem(self):
        p = Periodo(D1, D3)
        self.assertTrue(p.contem(D1))
        self.assertTrue(p.contem(D2))
        self.assertFalse(p.contem(D3))


class TestReserva(unittest.TestCase):
    def setUp(self):
        self.hospede = novo_hospede()
        self.quarto = QuartoSimples(1, 100)
        self.reserva = Reserva(self.hospede, self.quarto, D1, D4)

    def test_estado_inicial(self):
        r = self.reserva
        self.assertIs(r.hospede, self.hospede)
        self.assertIs(r.quarto, self.quarto)
        self.assertEqual(r.periodo.noites, 3)
        self.assertEqual(r.status, StatusReserva.ATIVA)
        self.assertIsNone(r.pagamento)
        self.assertFalse(r.paga)
        self.assertTrue(r.ocupa_quarto)

    def test_valor_total_usa_diaria_do_tipo(self):
        self.assertEqual(self.reserva.valor_total, 300)
        suite = Reserva(self.hospede, Suite(2, 200), D1, D3)
        self.assertEqual(suite.valor_total, 1090)

    def test_periodo_invalido(self):
        with self.assertRaises(ReservaInvalidaError):
            Reserva(self.hospede, self.quarto, D2, D1)

    def test_pagar(self):
        comprovante = self.reserva.pagar(PagamentoPix(300, "chave"))
        self.assertEqual(comprovante, "Pix: R$ 300.00 para a chave chave")
        self.assertTrue(self.reserva.paga)
        self.assertIsInstance(self.reserva.pagamento, PagamentoPix)

    def test_pagar_valor_errado(self):
        with self.assertRaises(PagamentoRecusadoError):
            self.reserva.pagar(PagamentoPix(100, "chave"))
        self.assertFalse(self.reserva.paga)

    def test_pagar_recusado_nao_marca_como_paga(self):
        with self.assertRaises(PagamentoRecusadoError):
            self.reserva.pagar(PagamentoDinheiro(300, 100))
        self.assertFalse(self.reserva.paga)

    def test_pagar_duas_vezes(self):
        self.reserva.pagar(PagamentoPix(300, "chave"))
        with self.assertRaises(ReservaInvalidaError):
            self.reserva.pagar(PagamentoPix(300, "chave"))

    def test_pagar_reserva_cancelada(self):
        self.reserva.cancelar()
        with self.assertRaises(ReservaInvalidaError):
            self.reserva.pagar(PagamentoPix(300, "chave"))

    def test_fluxo_completo(self):
        self.reserva.pagar(PagamentoCartao(300, CARTAO))
        self.reserva.fazer_checkin()
        self.assertEqual(self.reserva.status, StatusReserva.CHECKIN)
        self.assertTrue(self.reserva.ocupa_quarto)
        self.reserva.fazer_checkout()
        self.assertEqual(self.reserva.status, StatusReserva.CHECKOUT)
        self.assertFalse(self.reserva.ocupa_quarto)

    def test_checkin_so_para_reserva_ativa(self):
        self.reserva.fazer_checkin()
        with self.assertRaises(ReservaInvalidaError):
            self.reserva.fazer_checkin()

    def test_checkout_exige_checkin(self):
        self.reserva.pagar(PagamentoPix(300, "chave"))
        with self.assertRaises(ReservaInvalidaError):
            self.reserva.fazer_checkout()

    def test_checkout_exige_pagamento(self):
        self.reserva.fazer_checkin()
        with self.assertRaises(PagamentoRecusadoError):
            self.reserva.fazer_checkout()
        self.assertEqual(self.reserva.status, StatusReserva.CHECKIN)

    def test_cancelar(self):
        self.reserva.cancelar()
        self.assertEqual(self.reserva.status, StatusReserva.CANCELADA)
        self.assertFalse(self.reserva.ocupa_quarto)

    def test_cancelar_so_reserva_ativa(self):
        self.reserva.fazer_checkin()
        with self.assertRaises(ReservaInvalidaError):
            self.reserva.cancelar()

    def test_checkin_em_reserva_cancelada(self):
        self.reserva.cancelar()
        with self.assertRaises(ReservaInvalidaError):
            self.reserva.fazer_checkin()


class TestHotel(unittest.TestCase):
    def setUp(self):
        self.hotel = Hotel("Hotel Central")
        self.hotel.adicionar_quarto(1, "simples", 100)
        self.hotel.adicionar_quarto(2, "luxo", 200)
        self.hotel.adicionar_quarto(3, "suite", 300)
        self.hospede = novo_hospede()

    def test_nome(self):
        self.assertEqual(self.hotel.nome, "Hotel Central")
        with self.assertRaises(ValueError):
            Hotel("  ")

    def test_adicionar_quarto_cria_o_tipo_certo(self):
        tipos = [type(q) for q in self.hotel.quartos]
        self.assertEqual(tipos, [QuartoSimples, QuartoLuxo, Suite])

    def test_adicionar_quarto_duplicado_ou_tipo_invalido(self):
        with self.assertRaises(ValueError):
            self.hotel.adicionar_quarto(1, "simples", 100)
        with self.assertRaises(ValueError):
            self.hotel.adicionar_quarto(9, "cobertura", 100)

    def test_buscar_quarto(self):
        self.assertEqual(self.hotel.buscar_quarto(2).numero, 2)
        with self.assertRaises(QuartoNaoEncontradoError):
            self.hotel.buscar_quarto(99)

    def test_contratar(self):
        recep = Recepcionista("Ana", CPF, 2000)
        self.hotel.contratar(recep)
        self.assertEqual(self.hotel.funcionarios, [recep])

    def test_contratar_apenas_funcionario(self):
        with self.assertRaises(TypeError):
            self.hotel.contratar(self.hospede)

    def test_folha_salarial_polimorfica(self):
        self.hotel.contratar(Recepcionista("Ana", CPF, 2000))
        self.hotel.contratar(Gerente("Carlos", CPF, 4000))
        self.assertEqual(self.hotel.folha_salarial(), 8000)

    def test_folha_salarial_vazia(self):
        self.assertEqual(self.hotel.folha_salarial(), 0)

    def test_reservar(self):
        reserva = self.hotel.reservar(self.hospede, 1, D1, D3)
        self.assertIsInstance(reserva, Reserva)
        self.assertEqual(self.hotel.reservas, [reserva])

    def test_reservar_quarto_inexistente(self):
        with self.assertRaises(QuartoNaoEncontradoError):
            self.hotel.reservar(self.hospede, 99, D1, D3)

    def test_reservar_periodo_invalido(self):
        with self.assertRaises(ReservaInvalidaError):
            self.hotel.reservar(self.hospede, 1, D3, D1)

    def test_conflito_de_reserva(self):
        self.hotel.reservar(self.hospede, 1, D1, D3)
        with self.assertRaises(QuartoIndisponivelError):
            self.hotel.reservar(self.hospede, 1, D2, D4)
        self.assertEqual(len(self.hotel.reservas), 1)

    def test_mesmo_periodo_em_outro_quarto(self):
        self.hotel.reservar(self.hospede, 1, D1, D3)
        self.hotel.reservar(self.hospede, 2, D1, D3)
        self.assertEqual(len(self.hotel.reservas), 2)

    def test_reservas_em_sequencia_no_mesmo_quarto(self):
        self.hotel.reservar(self.hospede, 1, D1, D2)
        self.hotel.reservar(self.hospede, 1, D2, D3)
        self.assertEqual(len(self.hotel.reservas), 2)

    def test_cancelamento_libera_o_quarto(self):
        reserva = self.hotel.reservar(self.hospede, 1, D1, D3)
        self.assertFalse(self.hotel.quarto_disponivel(1, D1, D3))
        reserva.cancelar()
        self.assertTrue(self.hotel.quarto_disponivel(1, D1, D3))

    def test_checkout_libera_o_quarto(self):
        reserva = self.hotel.reservar(self.hospede, 1, D1, D3)
        reserva.pagar(PagamentoPix(reserva.valor_total, "chave"))
        reserva.fazer_checkin()
        self.assertFalse(self.hotel.quarto_disponivel(1, D1, D3))
        reserva.fazer_checkout()
        self.assertTrue(self.hotel.quarto_disponivel(1, D1, D3))

    def test_quarto_disponivel_valida_quarto_e_periodo(self):
        with self.assertRaises(QuartoNaoEncontradoError):
            self.hotel.quarto_disponivel(99, D1, D2)
        with self.assertRaises(ReservaInvalidaError):
            self.hotel.quarto_disponivel(1, D2, D1)

    def test_quartos_disponiveis(self):
        self.hotel.reservar(self.hospede, 1, D1, D3)
        numeros = [q.numero for q in self.hotel.quartos_disponiveis(D1, D3)]
        self.assertEqual(numeros, [2, 3])

    def test_taxa_ocupacao(self):
        self.assertEqual(self.hotel.taxa_ocupacao(D1), 0)
        self.hotel.reservar(self.hospede, 1, D1, D3)
        self.assertAlmostEqual(self.hotel.taxa_ocupacao(D1), 1 / 3)
        self.hotel.reservar(self.hospede, 2, D1, D2)
        self.assertAlmostEqual(self.hotel.taxa_ocupacao(D1), 2 / 3)
        self.assertAlmostEqual(self.hotel.taxa_ocupacao(D2), 1 / 3)
        self.assertEqual(self.hotel.taxa_ocupacao(D3), 0)

    def test_taxa_ocupacao_sem_quartos(self):
        self.assertEqual(Hotel("Vazio").taxa_ocupacao(D1), 0.0)

    def test_taxa_ocupacao_ignora_reserva_cancelada(self):
        reserva = self.hotel.reservar(self.hospede, 1, D1, D3)
        reserva.cancelar()
        self.assertEqual(self.hotel.taxa_ocupacao(D1), 0)

    def test_listas_retornadas_sao_copias(self):
        self.hotel.quartos.clear()
        self.hotel.reservas.clear()
        self.hotel.funcionarios.clear()
        self.assertEqual(len(self.hotel.quartos), 3)


if __name__ == "__main__":
    unittest.main()