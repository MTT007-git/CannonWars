import socket
import struct
import threading

PORT = 5000
BROADCAST_PORT = 5001
BROADCAST_MSG = b"SEARCH_FOR_SERVER"
BROADCAST_REPLY = b"THIS_IS_SERVER"
IS_SERVER = False
LOG = True


def listen_for_broadcast(ips: list[str], max_players: int = -1, msg: bytes = BROADCAST_MSG, port: int = BROADCAST_PORT,
                         reply: bytes = BROADCAST_REPLY) -> None:
    global IS_SERVER
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", port))
    players_count = 0
    while players_count < max_players or max_players < 0:
        data, addr = sock.recvfrom(1024)
        if data == msg and IS_SERVER:
            sock.sendto(reply, addr)
            ips.append(addr[0])
            players_count += 1


def broadcast(timeout: float = 3, msg: bytes = BROADCAST_MSG, port: int = BROADCAST_PORT,
              reply: bytes = BROADCAST_REPLY) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    sock.sendto(msg, ("255.255.255.255", port))
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if data == reply:
                return addr[0]
    except socket.timeout:
        return None


def server(port: int = PORT, log: bool = LOG) -> socket.socket:
    if log:
        print("[SERVER] Starting")
    sock = socket.socket()
    sock.bind(("", port))
    sock.listen(1)
    conn, addr = sock.accept()
    if log:
        print(f"[SERVER] Connected to {addr[0]}:{addr[1]}")
    return conn


def client(server_ip: str, port: int = PORT, log: bool = LOG) -> socket.socket:
    if log:
        print(f"[CLIENT] Trying to connect to {server_ip}:{port}")
    sock = socket.socket()
    try:
        sock.connect((server_ip, port))
    except ConnectionRefusedError:
        if log:
            print("[CLIENT] Failed to connect")
        return None
    if log:
        print(f"[CLIENT] Connected to {server_ip}:{port}")
    return sock


def get_sock(log: bool = LOG, timeout: float = 3, max_players: int = -1, msg: bytes = BROADCAST_MSG,
             port: int = BROADCAST_PORT, reply: bytes = BROADCAST_REPLY, ips: list[int] = ()) -> socket.socket:
    global IS_SERVER
    threading.Thread(target=listen_for_broadcast, args=(ips, max_players, msg, port, reply), daemon=True).start()
    if log:
        print("[BROADCAST] Searching for an existing server")
    server_ip = broadcast(timeout, msg, port, reply)
    if server_ip:
        if log:
            print(f"[BROADCAST] Found server at {server_ip}:{port}")
        sock = client(server_ip, port, log)
    else:
        if log:
            print("[BROADCAST] Could not find an existing server")
        IS_SERVER = True
        sock = server(port, log)
    return sock


def send(sock: socket.socket, data: bytes) -> None:
    sock.send(struct.pack("<I", len(data)))
    sock.send(data)


def recv(sock: socket.socket) -> bytes:
    size_bytes = sock.recv(4)
    if len(size_bytes) != 4:
        raise ConnectionResetError("Couldn't read size")
    size = struct.unpack("<I", size_bytes)[0]
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionResetError("Couldn't read data")
        data += chunk
    return data


def send_str(sock: socket.socket, string: str) -> None:
    send(sock, string.encode("utf-8"))


def recv_str(sock: socket.socket) -> str:
    return recv(sock).decode("utf-8")


class Network:
    def __init__(self, max_players: int = 1, port: int = PORT, broadcast_port: int = BROADCAST_PORT,
                 broadcast_msg: bytes = BROADCAST_MSG, broadcast_reply: bytes = BROADCAST_REPLY, log: bool = LOG,
                 timeout: float = 3) -> None:
        self.sock: socket.socket | None = None
        self.max_players = max_players
        self.port: int = port
        self.broadcast_port: int = broadcast_port
        self.broadcast_msg: bytes = broadcast_msg
        self.broadcast_reply: bytes = broadcast_reply
        self.log: bool = log
        self.timeout: float = timeout
        self.ips = []

    def connect(self) -> None:
        self.sock = get_sock(self.log, self.timeout, self.max_players, self.broadcast_msg, self.broadcast_port,
                             self.broadcast_reply, self.ips)

    def send(self, data: bytes) -> None:
        send(self.sock, data)

    def recv(self) -> bytes:
        return recv(self.sock)

    def send_str(self, string: str) -> None:
        send_str(self.sock, string)

    def recv_str(self) -> str:
        return recv_str(self.sock)


def test_listen_for_updates(sock: socket.socket):
    try:
        while True:
            text = recv_str(sock)
            if text:
                print(text)
    except ConnectionResetError:
        pass


def test():
    sock = get_sock()
    threading.Thread(target=test_listen_for_updates, args=(sock,), daemon=True).start()
    try:
        while True:
            send_str(sock, input())
    except ConnectionResetError:
        sock.close()


if __name__ == "__main__":
    test()
