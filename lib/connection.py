import socket

from .segment import Segment


DEFAULT_TIMEOUT = 10000

class Connection:
    def __init__(self, ip : str, port : int):
        # Init UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, port))

        # set timeout
        self.socket.settimeout(DEFAULT_TIMEOUT)


    def send_data(self, msg : Segment, dest : tuple[str, int]):
        # Send single segment into destination
        self.socket.sendto(msg.get_bytes(), dest)

    def listen_single_segment(self) -> Segment:
        # Listen single UDP datagram within timeout and convert into segment
        response, address = self.socket.recvfrom(1024)
        data = Segment()
        data.set_from_bytes(response)
        return data

    def set_timeout(self, timeout):
        self.socket.settimeout(timeout)

    def close_socket(self):
        # Release UDP socket
        self.socket.close()
