import sys

import operacoes
from servidor import Server

port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
server = Server(port)
operacoes.registerAll(server)
print(f"Servidor escutando em UDP/{server.port} (Ctrl+C para sair)")
try:
    server.serve()
except KeyboardInterrupt:
    print("\nEncerrado.")
