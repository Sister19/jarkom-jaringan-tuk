from lib.connection import Connection
from lib.segment import Segment
import lib.segment as segment

class Client:
    def __init__(self):
        # Init client
        self.conn = Connection("localhost", 3120)

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        pass

    def listen_file_transfer(self):
        # File transfer, client-side
        pass


if __name__ == '__main__':
    main = Client()
    main.three_way_handshake()
    main.listen_file_transfer()

    while True:
        payload = input("Input message: ")
        msg = Segment()
        msg.set_header({
            "seq_num": 0,
            "ack_num":0
        })
        msg.set_payload(bytes(payload, "utf8"))
        main.conn.send_data(msg, ("localhost", 3121))
