## 1. Estrutura do Projeto

* `mensagem.py` — Define as classes `RemoteRef` e `Message`, além do empacotamento e desempacotamento binário (`pack` / `unpack`).
* `cliente.py` — Implementa o lado cliente com a primitiva `doOperation()`, controle de timeout e retransmissão.
* `servidor.py` — Implementa o lado servidor com as primitivas `getRequest()` e `sendReply()`, além do histórico para evitar reexecução de requisições duplicadas.
* `operacoes.py` — Operações remotas cadastradas para teste (`ECHO`, `SUM` e `UPPERCASE`).
* `demo_servidor.py` e `demo_cliente.py` — Scripts executáveis para demonstração via terminal.
* `teste_protocolo.py` — Testes unitários automatizados (incluindo simulação de perda de pacotes).

---

## 2. Formato da Mensagem (Interoperabilidade)

Para permitir a comunicação entre diferentes máquinas e linguagens, o cabeçalho da mensagem foi padronizado em **24 bytes** utilizando ordenação de rede (*Big-Endian*):

| Campo | Tipo | Tamanho | Descrição |
| :--- | :--- | :--- | :--- |
| `messageType` | `int32` | 4 bytes | `0` = Request, `1` = Reply |
| `requestId` | `int32` | 4 bytes | Identificador sequencial da requisição |
| `remoteReference` (IP) | `bytes` | 4 bytes | Endereço IPv4 de destino |
| `remoteReference` (Porta) | `int32` | 4 bytes | Porta UDP de destino |
| `operationId` | `int32` | 4 bytes | Código da operação (`-1` indica erro no Reply) |
| `argumentsLength` | `int32` | 4 bytes | Tamanho (`N`) do vetor de argumentos |
| `arguments` | `byte[]` | `N` bytes | Dados empacotados da requisição ou resposta |

---

## 3. Como Executar

### Pré-requisitos
* **Python 3.10** ou superior instalado.

### Execução
Abra dois terminais na pasta raiz do projeto:

Terminal 1 — Iniciar o servidor:
```bash
python demo_servidor.py 5000
```

Terminal 2 — Executar o cliente de demonstração:
```bash
python demo_cliente.py 127.0.0.1 5000
```
Para testar em rede com outra máquina, basta substituir 127.0.0.1 pelo IPv4 do servidor.

### Comandos Disponíveis no Cliente
Com o cliente em execução (`>`), digite um dos comandos abaixo para invocar as operações remotamente no servidor:

* **`echo <texto>`** — Envia uma mensagem de texto para o servidor e recebe exatamente o mesmo conteúdo de volta (operação `ECHO`, ID `1`). Exemplo: digitar `echo ola` retorna `ola`.
* **`sum <num1> <num2>`** — Empacota dois números inteiros em binário, realiza a soma no servidor e devolve o resultado (operação `SUM`, ID `2`). Exemplo: digitar `sum 40 2` retorna `42`.
* **`upper <texto>`** — Envia uma frase ou palavra para o servidor e recebe o texto convertido para letras maiúsculas (operação `UPPERCASE`, ID `3`). Exemplo: digitar `upper ola` retorna `OLA`.
* **`exit`** — Fecha o socket UDP e encerra o terminal interativo do cliente (também aceita `sair`, `quit` ou `Ctrl+C`).

### Testes
```bash
python -m unittest -v teste_protocolo.py
```