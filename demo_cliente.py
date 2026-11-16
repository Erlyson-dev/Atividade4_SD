import sys

import operacoes
from cliente import Client, RemoteError
from mensagem import RemoteRef


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

    servidor = RemoteRef(host, port)
    client = Client()

    print("Conectado! Comandos disponíveis:")
    print("  echo <texto>        -> repete o texto enviado")
    print("  sum <num1> <num2>   -> soma dois números inteiros")
    print("  upper <texto>       -> converte o texto para maiúsculas")
    print("  exit               -> encerra o cliente\n")

    try:
        while True:
            try:
                entrada = input("> ").strip()
            except EOFError:
                break

            if not entrada:
                continue

            partes = entrada.split(maxsplit=1)
            comando = partes[0].lower()
            argumento = partes[1] if len(partes) > 1 else ""

            if comando in ("sair", "exit", "quit"):
                break

            try:
                if comando == "echo":
                    resposta = client.doOperation(servidor, operacoes.ECHO, argumento.encode("utf-8"))
                    print(resposta.decode("utf-8"))

                elif comando == "upper":
                    resposta = client.doOperation(servidor, operacoes.UPPERCASE, argumento.encode("utf-8"))
                    print(resposta.decode("utf-8"))

                elif comando == "sum":
                    nums = argumento.split()
                    if len(nums) != 2:
                        print("Uso correto: sum <num1> <num2>")
                        continue
                    payload = operacoes.packSum(int(nums[0]), int(nums[1]))
                    resposta = client.doOperation(servidor, operacoes.SUM, payload)
                    print(operacoes.unpackInt(resposta))

                else:
                    print(f"Comando desconhecido: '{comando}'. Use echo, sum, upper ou sair.")

            except ValueError:
                print("Erro: 'sum' exige dois números inteiros válidos.")
            except RemoteError as error:
                print(f"Erro remoto: {error}")
            except TimeoutError as error:
                print(f"Timeout: {error}")

    except KeyboardInterrupt:
        print("\nEncerrando cliente...")
    finally:
        client.close()


if __name__ == "__main__":
    main()