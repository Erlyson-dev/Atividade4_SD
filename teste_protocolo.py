import unittest

import operacoes
from cliente import Client, RemoteError
from mensagem import REQUEST, HEADER_SIZE, Message, RemoteRef, pack, unpack
from servidor import Server


class LossyServer(Server):
    def __init__(self, drop: int):
        super().__init__(0, "127.0.0.1")
        self.drop = drop

    def _send_datagram(self, datagram, address):
        if self.drop > 0:
            self.drop -= 1
            return
        super()._send_datagram(datagram, address)


class ProtocolTest(unittest.TestCase):
    def start(self, server):
        operacoes.registerAll(server)
        server.startInThread()
        self.addCleanup(server.stop)
        client = Client(timeout=0.3, max_attempts=3)
        self.addCleanup(client.close)
        return client, RemoteRef("127.0.0.1", server.port)

    def test_message_round_trip(self):
        m = Message(REQUEST, 7, RemoteRef("10.0.0.5", 4000), 2, b"abc")
        data = pack(m)
        self.assertEqual(len(data), HEADER_SIZE + 3)
        self.assertEqual(unpack(data), m)

    def test_malformed_message(self):
        with self.assertRaises(ValueError):
            unpack(b"curto")
        with self.assertRaises(ValueError):
            unpack(pack(Message(0, 1, RemoteRef("127.0.0.1", 1), 1, b"x"))[:-1])

    def test_operations(self):
        client, s = self.start(LossyServer(0))
        self.assertEqual(client.doOperation(s, operacoes.ECHO, b"oi"), b"oi")
        r = client.doOperation(s, operacoes.SUM, operacoes.packSum(40, 2))
        self.assertEqual(operacoes.unpackInt(r), 42)
        self.assertEqual(client.doOperation(s, operacoes.UPPERCASE, "ação".encode()),
                         "AÇÃO".encode())

    def test_unknown_operation(self):
        client, s = self.start(LossyServer(0))
        with self.assertRaises(RemoteError):
            client.doOperation(s, 99, b"")

    def test_retransmission_does_not_reexecute(self):
        server = LossyServer(drop=2)
        executions = []
        server.registerOperation(10, lambda a: executions.append(1) or b"ok")
        server.startInThread()
        self.addCleanup(server.stop)
        client = Client(timeout=0.3, max_attempts=3)
        self.addCleanup(client.close)
        r = client.doOperation(RemoteRef("127.0.0.1", server.port), 10, b"")
        self.assertEqual(r, b"ok")
        self.assertEqual(len(executions), 1)

    def test_timeout_without_server(self):
        client = Client(timeout=0.1, max_attempts=2)
        self.addCleanup(client.close)
        with self.assertRaises(TimeoutError):
            client.doOperation(RemoteRef("127.0.0.1", 9), 1, b"")


if __name__ == "__main__":
    unittest.main()
