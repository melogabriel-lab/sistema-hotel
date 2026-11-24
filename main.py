from datetime import date

from excecoes import HotelError
from hotel import Hotel
from pagamentos import PagamentoCartao, PagamentoDinheiro, PagamentoPix
from pessoas import Gerente, Hospede, Recepcionista


def ler_data(rotulo):
    try:
        dia, mes, ano = input(f"{rotulo} (dd/mm/aaaa): ").split("/")
        return date(int(ano), int(mes), int(dia))
    except ValueError:
        raise ValueError("Data inválida. Use o formato dd/mm/aaaa.") from None


def ler_numero(rotulo):
    return float(input(f"{rotulo}: ").replace(",", "."))


def escolher(itens, rotulo, descrever=str):
    if not itens:
        print(f"Nenhum(a) {rotulo} disponível.")
        return None
    for i, item in enumerate(itens, 1):
        print(f"{i}) {descrever(item)}")
    n = int(input(f"Escolha o número do(a) {rotulo}: "))
    if not 1 <= n <= len(itens):
        raise ValueError("Opção inválida.")
    return itens[n - 1]


def descrever_reserva(r):
    return (
        f"{r.hospede.nome} | quarto {r.quarto.numero} | "
        f"{r.periodo.entrada:%d/%m/%Y} a {r.periodo.saida:%d/%m/%Y} | "
        f"R$ {r.valor_total:.2f} | {r.status.value} | "
        f"{'paga' if r.paga else 'não paga'}"
    )


def adicionar_quarto(hotel):
    numero = int(input("Número do quarto: "))
    tipo = input("Tipo (simples, luxo ou suite): ")
    diaria = ler_numero("Diária base")
    quarto = hotel.adicionar_quarto(numero, tipo, diaria)
    print(f"Quarto criado: {quarto.descricao()}")


def contratar(hotel):
    cargo = input("Cargo (1-Recepcionista, 2-Gerente): ")
    if cargo not in ("1", "2"):
        raise ValueError("Cargo inválido.")
    nome = input("Nome: ")
    cpf = input("CPF: ")
    salario = ler_numero("Salário base")
    classe = Recepcionista if cargo == "1" else Gerente
    funcionario = classe(nome, cpf, salario)
    hotel.contratar(funcionario)
    print(f"Contratado: {funcionario.descricao()} (salário R$ {funcionario.calcular_salario():.2f})")


def ver_disponiveis(hotel):
    entrada = ler_data("Entrada")
    saida = ler_data("Saída")
    quartos = hotel.quartos_disponiveis(entrada, saida)
    if not quartos:
        print("Nenhum quarto disponível nesse período.")
    for quarto in quartos:
        print(quarto.descricao())


def reservar(hotel):
    nome = input("Nome do hóspede: ")
    cpf = input("CPF: ")
    telefone = input("Telefone: ")
    hospede = Hospede(nome, cpf, telefone)
    numero = int(input("Número do quarto: "))
    entrada = ler_data("Entrada")
    saida = ler_data("Saída")
    reserva = hotel.reservar(hospede, numero, entrada, saida)
    print(f"Reserva criada. Valor total: R$ {reserva.valor_total:.2f}")


def listar_reservas(hotel):
    if not hotel.reservas:
        print("Nenhuma reserva.")
    for i, reserva in enumerate(hotel.reservas, 1):
        print(f"{i}) {descrever_reserva(reserva)}")


def pagar(hotel):
    reserva = escolher(hotel.reservas, "reserva", descrever_reserva)
    if reserva is None:
        return
    valor = reserva.valor_total
    print(f"Valor a pagar: R$ {valor:.2f}")
    forma = input("Forma (1-Dinheiro, 2-Cartão, 3-Pix): ")
    if forma == "1":
        pagamento = PagamentoDinheiro(valor, ler_numero("Valor entregue"))
    elif forma == "2":
        numero = input("Número do cartão: ")
        parcelas = int(input("Parcelas: "))
        pagamento = PagamentoCartao(valor, numero, parcelas)
    elif forma == "3":
        pagamento = PagamentoPix(valor, input("Chave Pix: "))
    else:
        raise ValueError("Forma de pagamento inválida.")
    print(reserva.pagar(pagamento))


def checkin(hotel):
    reserva = escolher(hotel.reservas, "reserva", descrever_reserva)
    if reserva is None:
        return
    recepcionistas = [f for f in hotel.funcionarios if isinstance(f, Recepcionista)]
    recepcionista = escolher(recepcionistas, "recepcionista")
    if recepcionista is None:
        return
    recepcionista.realizar_checkin(reserva)
    print("Check-in realizado.")


def checkout(hotel):
    reserva = escolher(hotel.reservas, "reserva", descrever_reserva)
    if reserva is None:
        return
    recepcionistas = [f for f in hotel.funcionarios if isinstance(f, Recepcionista)]
    recepcionista = escolher(recepcionistas, "recepcionista")
    if recepcionista is None:
        return
    recepcionista.realizar_checkout(reserva)
    print("Check-out realizado.")


def cancelar(hotel):
    reserva = escolher(hotel.reservas, "reserva", descrever_reserva)
    if reserva is None:
        return
    reserva.cancelar()
    print("Reserva cancelada.")


def relatorio(hotel):
    gerentes = [f for f in hotel.funcionarios if isinstance(f, Gerente)]
    gerente = escolher(gerentes, "gerente")
    if gerente is None:
        return
    print(gerente.gerar_relatorio(hotel, ler_data("Data")))


OPCOES = {
    "1": ("Adicionar quarto", adicionar_quarto),
    "2": ("Contratar funcionário", contratar),
    "3": ("Ver quartos disponíveis", ver_disponiveis),
    "4": ("Fazer reserva", reservar),
    "5": ("Listar reservas", listar_reservas),
    "6": ("Pagar reserva", pagar),
    "7": ("Fazer check-in", checkin),
    "8": ("Fazer check-out", checkout),
    "9": ("Cancelar reserva", cancelar),
    "10": ("Relatório do gerente", relatorio),
}


def main():
    while True:
        try:
            hotel = Hotel(input("Nome do hotel: "))
            break
        except ValueError as erro:
            print(f"Erro: {erro}")

    while True:
        print(f"\n=== {hotel.nome} ===")
        for chave, (titulo, _) in OPCOES.items():
            print(f"{chave}) {titulo}")
        print("0) Sair")
        escolha = input("Opção: ").strip()
        if escolha == "0":
            break
        if escolha not in OPCOES:
            print("Opção inválida.")
            continue
        try:
            OPCOES[escolha][1](hotel)
        except (HotelError, ValueError) as erro:
            print(f"Erro: {erro}")


if __name__ == "__main__":
    main()