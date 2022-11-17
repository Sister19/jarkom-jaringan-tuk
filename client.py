from lib.connection import Connection
from lib.segment import Segment
import lib.segment as segment
import socket


IP = "127.0.0.1"
PORT = 1234
BROADCAST_PORT = 3000
N = 4
FILE = "output.py"

class Client:
    def __init__(self):
        # Init client
        self.conn = Connection(IP, PORT)
        print(f"Client started at {IP}:{PORT}")

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        print("[!] Starting three way handshake...")
        print(f"[!] Sending SYN segment request to port {BROADCAST_PORT}")
        message_SYN = Segment()
        message_SYN.set_header({
            "seq_num": 0,
            "ack_num": 0
        })
        message_SYN.set_flag([segment.SYN_FLAG])
        self.conn.send_data(message_SYN, (IP, BROADCAST_PORT))
    
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
        print("Receiving file...")

        request_number = 0

        bytes_array = bytes()
        with open(FILE, "wb") as file:
            file.write(bytes_array)
        
        with open(FILE, "ab") as file:
            while True:
                self.conn.set_timeout(3)
                try:
                    addr, segment_response = self.conn.listen_single_segment()

                    if addr == (IP, BROADCAST_PORT) and segment_response.flag.fin:
                        print(f"[!] [Server] Segment FIN received")
                        message_ACK_FIN = Segment()
                        message_ACK_FIN.set_header({
                            "seq_num": 0,
                            "ack_num": 0
                        })
                        message_ACK_FIN.set_flag([segment.ACK_FLAG, segment.FIN_FLAG])
                        self.conn.send_data(message_ACK_FIN, addr)

                        print(f"[!] [Server] Sending segment FIN acknowledgement")
                        print("\nFile received")
                        print(f"Closing connection...")
                        self.conn.close_socket()
                        print(f"Connection closed")

                        break
                    
                    if addr == (IP, BROADCAST_PORT) and not segment_response.flag.ack and not segment_response.flag.fin and not segment_response.flag.syn:
                        print(f"[!] [Server] Segment {segment_response.header['seq_num']} received")
                        if segment_response.header["seq_num"] == request_number:
                            message_ACK = Segment()
                            message_ACK.set_header({
                                "seq_num": 0,
                                "ack_num": segment_response.header['seq_num']
                            })
                            message_ACK.set_flag([segment.ACK_FLAG])
                            self.conn.send_data(message_ACK, addr)
                            print(f"[!] [Server] Sending segment {segment_response.header['seq_num']} acknowledgement")

                            file.write(segment_response.get_payload())

                            print(f"[!] Segment {segment_response.header['seq_num']} written to file {FILE}")
                            
                            request_number += 1
                        else:
                            print(f"[!] [Server] Segment {segment_response.header['seq_num']} is not acknowleged")
                            raise socket.timeout
                    else:
                        print(f"[!] [Server] Segment received")
                        print(f"[!] [Server] Segment is not acknowleged")
                        raise socket.timeout

                        
                except socket.timeout:
                    print(f"\n[!] [Server] [Num={request_number}] [Timeout] segment num={request_number} timeout, resending previous ACK..")
                    message_ACK = Segment()
                    message_ACK.set_header({
                        "seq_num": 0,
                        "ack_num": request_number - 1
                    })
                    message_ACK.set_flag([segment.ACK_FLAG])
                    self.conn.send_data(message_ACK, addr)
                    print(f"[!] [Server] Sending segment {request_number - 1} acknowledgement")
        


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
