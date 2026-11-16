import struct

ECHO = 1
SUM = 2
UPPERCASE = 3


def echo(arguments: bytes) -> bytes:
    return arguments


def sum_(arguments: bytes) -> bytes:
    a, b = struct.unpack("!ii", arguments)
    return struct.pack("!i", a + b)


def uppercase(arguments: bytes) -> bytes:
    return arguments.decode("utf-8").upper().encode("utf-8")


def registerAll(server) -> None:
    server.registerOperation(ECHO, echo)
    server.registerOperation(SUM, sum_)
    server.registerOperation(UPPERCASE, uppercase)


def packSum(a: int, b: int) -> bytes:
    return struct.pack("!ii", a, b)


def unpackInt(data: bytes) -> int:
    return struct.unpack("!i", data)[0]
