"""Lado cliente: doOperation()."""
import socket
import time

from mensagem import (ERROR_OPERATION_ID, REPLY, REQUEST, Message, RemoteRef,
                      pack, unpack)


class RemoteError(Exception):
    """O servidor respondeu com erro (ex.: operação desconhecida)."""


class Client:
    def __init__(self, timeout: float = 1.0, max_attempts: int = 3):
        self.timeout = timeout
        self.max_attempts = max_attempts
        self._next_request_id = 1
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def doOperation(self, s: RemoteRef, operationId: int, arguments: bytes = b"") -> bytes:
        requestId = self._next_request_id
        self._next_request_id += 1
        datagram = pack(Message(REQUEST, requestId, s, operationId, arguments))

        for _ in range(self.max_attempts):
            self._socket.sendto(datagram, (s.host, s.port))
            deadline = time.monotonic() + self.timeout
            while (remaining := deadline - time.monotonic()) > 0:
                self._socket.settimeout(remaining)
                try:
                    data, _ = self._socket.recvfrom(65535)
                    reply = unpack(data)
                except socket.timeout:
                    break
                except ConnectionResetError:
                    time.sleep(max(0.0, deadline - time.monotonic()))
                    break
                except ValueError:
                    continue 
                if reply.messageType == REPLY and reply.requestId == requestId:
                    if reply.operationId == ERROR_OPERATION_ID:
                        raise RemoteError(reply.arguments.decode("utf-8", "replace"))
                    return reply.arguments
        raise TimeoutError(f"sem resposta de {s.host}:{s.port} após {self.max_attempts} tentativas")

    def close(self) -> None:
        self._socket.close()
