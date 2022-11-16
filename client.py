from lib.connection import Connection
from lib.segment import Segment
import lib.segment as segment

IP = "127.0.0.1"
PORT = 1234
BROADCAST_PORT = 3000
N = 4

class Client:
    def __init__(self):
        # Init client
        # self.conn = Connection("localhost", 3120)
        self.conn = Connection(IP, PORT)
        print(f"Client started at {IP}:{PORT}")

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        print("[!] Starting three way handshake...")
        print(f"[!] Sending SYN segment request to port {BROADCAST_PORT}")
        message_SYN = Segment()
        message_SYN.set_header({
            "seq_num": 0,
            "ack_num":0
        })
        message_SYN.set_flag([segment.SYN_FLAG])
        self.conn.send_data(message_SYN, (IP, BROADCAST_PORT))
        # pass
    
    def three_way_handshake_response(self):
        addr, segment_response = self.conn.listen_single_segment()

        if (
            segment_response.flag.ack  # 
            and segment_response.flag.syn
            and segment_response.valid_checksum()  # check if the request contains no error when transmitting with checksum
            and addr == (IP, BROADCAST_PORT)
        ):
            print(f"[!] Received SYN, ACK response from {addr}")
            message_ACK = Segment()
            message_ACK.set_header({
                "seq_num": 0,
                "ack_num":0
            })
            message_ACK.set_flag([segment.ACK_FLAG])
            self.conn.send_data(message_ACK, addr)
            print(f"[!] Sending ACK segment response to port {addr[1]}")
            print(f"[!] [Handshake] Handshake to server {addr} success")


    def listen_file_transfer(self):
        # File transfer, client-side
        segment_list = []
        sequence_base = 0
        sequence_add = 0
        print("Receiving file...")
        while True:
            addr, segment_response = self.conn.listen_single_segment()
            print(segment_response.valid_checksum())
            # if addr == (IP, BROADCAST_PORT) and segment_response.flag.fin:
            #     self.conn.close_socket()
            #     break

            # if addr == (IP, BROADCAST_PORT) and not segment_response.flag.ack and not segment_response.flag.fin and segment_response.flag.syn:
            #     segment_list.append(segment_response)
            #     sequence_base += 1
                
            # if sequence_base - sequence_add == N:
            #     message_ACK = Segment()
            #     message_ACK.set_header({
            #         "seq_num": 0,
            #         "ack_num":0
            #     })
            #     message_ACK.set_flag([segment.ACK_FLAG])
            #     self.conn.send_data(message_ACK, addr)

        
        print("File received")


if __name__ == '__main__':
    main = Client()
    main.three_way_handshake()
    main.three_way_handshake_response()
    main.listen_file_transfer()

    # while True:
    #     payload = input("Input message: ")
    #     msg = Segment()
    #     msg.set_header({
    #         "seq_num": 0,
    #         "ack_num":0
    #     })
    #     msg.set_payload(bytes(payload, "utf8"))
    #     main.conn.send_data(msg, ("localhost", 3121))
