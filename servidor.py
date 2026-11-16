import socket
import threading
from collections import OrderedDict

from mensagem import (ERROR_OPERATION_ID, REPLY, REQUEST, Message, pack, unpack)

HISTORY_SIZE = 1000


class Server:
    def __init__(self, port: int = 0, host: str = "0.0.0.0"):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((host, port))
        self.port = self._socket.getsockname()[1]
        self._operations = {}
        self._pending = {}  # (clientHost, clientPort) -> Message em atendimento
        # (clientHost, clientPort, requestId) -> datagrama de Reply (evita reexecutar duplicatas)
        self._history = OrderedDict()
        self._stop = threading.Event()
        self.lastClientHost = None
        self.lastClientPort = None

    def registerOperation(self, operationId: int, function) -> None:
        self._operations[operationId] = function

    def getRequest(self) -> bytes:
        while True:
            data, (host, port) = self._socket.recvfrom(65535)
            try:
                message = unpack(data)
            except ValueError:
                continue
            if message.messageType == REQUEST:
                self.lastClientHost, self.lastClientPort = host, port
                return data

    def sendReply(self, reply: bytes, clientHost: str, clientPort: int,
                  operationId: int | None = None) -> None:
        request = self._pending[(clientHost, clientPort)]
        datagram = pack(Message(
            REPLY, request.requestId, request.remoteReference,
            request.operationId if operationId is None else operationId, reply))
        self._history[(clientHost, clientPort, request.requestId)] = datagram
        if len(self._history) > HISTORY_SIZE:
            self._history.popitem(last=False)
        self._send_datagram(datagram, (clientHost, clientPort))

    def _send_datagram(self, datagram: bytes, address) -> None:
        self._socket.sendto(datagram, address)

    def _handle(self, data: bytes, clientHost: str, clientPort: int) -> None:
        request = unpack(data)
        key = (clientHost, clientPort, request.requestId)
        if key in self._history:  # retransmissão do cliente: reenvia sem reexecutar
            self._send_datagram(self._history[key], (clientHost, clientPort))
            return
        self._pending[(clientHost, clientPort)] = request
        function = self._operations.get(request.operationId)
        if function is None:
            self.sendReply(f"operação {request.operationId} desconhecida".encode(),
                           clientHost, clientPort, ERROR_OPERATION_ID)
            return
        try:
            reply = function(request.arguments)
        except Exception as error:  # noqa: BLE001
            self.sendReply(str(error).encode(), clientHost, clientPort, ERROR_OPERATION_ID)
            return
        self.sendReply(reply, clientHost, clientPort)

    def serve(self) -> None:
        self._socket.settimeout(0.2)
        while not self._stop.is_set():
            try:
                data = self.getRequest()
            except socket.timeout:
                continue
            except OSError:
                break
            self._handle(data, self.lastClientHost, self.lastClientPort)
        self._socket.close()

    def startInThread(self) -> threading.Thread:
        thread = threading.Thread(target=self.serve, daemon=True)
        thread.start()
        return thread

    def stop(self) -> None:
        self._stop.set()
