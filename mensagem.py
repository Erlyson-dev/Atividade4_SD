import socket
import struct
from dataclasses import dataclass

REQUEST = 0
REPLY = 1
ERROR_OPERATION_ID = -1

_HEADER_FORMAT = "!ii4siii"
HEADER_SIZE = struct.calcsize(_HEADER_FORMAT)
MAX_DATAGRAM_SIZE = 65507


@dataclass(frozen=True)
class RemoteRef:
    host: str
    port: int


@dataclass
class Message:
    messageType: int
    requestId: int
    remoteReference: RemoteRef
    operationId: int
    arguments: bytes = b""


def pack(message: Message) -> bytes:
    ip = socket.inet_aton(socket.gethostbyname(message.remoteReference.host))
    header = struct.pack(
        _HEADER_FORMAT,
        message.messageType,
        message.requestId,
        ip,
        message.remoteReference.port,
        message.operationId,
        len(message.arguments),
    )
    data = header + message.arguments
    if len(data) > MAX_DATAGRAM_SIZE:
        raise ValueError("mensagem maior que o tamanho máximo de um datagrama UDP")
    return data


def unpack(data: bytes) -> Message:
    if len(data) < HEADER_SIZE:
        raise ValueError("datagrama menor que o cabeçalho")
    messageType, requestId, ip, port, operationId, length = struct.unpack(
        _HEADER_FORMAT, data[:HEADER_SIZE]
    )
    arguments = data[HEADER_SIZE:]
    if messageType not in (REQUEST, REPLY):
        raise ValueError(f"messageType inválido: {messageType}")
    if length != len(arguments):
        raise ValueError("tamanho dos arguments não confere")
    return Message(messageType, requestId, RemoteRef(socket.inet_ntoa(ip), port),
                   operationId, arguments)
