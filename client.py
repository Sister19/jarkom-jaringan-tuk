from lib.connection import Connection
from lib.segment import Segment
import lib.segment as segment
import socket
import sys
import os
from dotenv import load_dotenv

load_dotenv()
IP = os.getenv("IP")
N = int(os.getenv("N"))

class Client:
    def __init__(self):
        # Init client
        self.port = int(sys.argv[1])
        self.conn = Connection(IP, self.port)
        self.broadcast_port = int(sys.argv[2])
        self.file = sys.argv[3]
        self.retry_three_way_handshake = False
        self.three_way_handshake_tries = 0
        print(f"Client started at {IP}:{self.port}")

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        self.three_way_handshake_tries += 1
        if not self.retry_three_way_handshake:
            print("[!] Starting three way handshake...")
        message_SYN = Segment()
        message_SYN.set_header({
            "seq_num": 0,
            "ack_num": 0
        })
        message_SYN.set_flag([segment.SYN_FLAG])
        self.conn.send_data(message_SYN, (IP, self.broadcast_port))
        print(f"[!] Sending SYN segment request to port {self.broadcast_port}")
        self.three_way_handshake_response()

    def three_way_handshake_response(self):
        self.conn.set_timeout(5)
        try:
            addr, segment_response = self.conn.listen_single_segment()

            if (
                segment_response.flag.ack  # 
                and segment_response.flag.syn
                and not segment_response.flag.fin
                and segment_response.valid_checksum()  # check if the request contains no error when transmitting with checksum
                and addr == (IP, self.broadcast_port)
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
                self.retry_three_way_handshake = False

        except socket.timeout:
            print(f"\n[!] [Client] [SYN, ACK] [Timeout] SYN, ACK response timeout, resending SYN segment..")
            if self.three_way_handshake_tries >= 5:
                print(f"[!] Handshake failed")
                exit()
            self.retry_three_way_handshake = True
            self.three_way_handshake()


    def listen_file_transfer(self):
        sequence_number_list = []

        # File transfer, client-side
        print("Receiving file...")

        request_number = 0
        
        with open(self.file, "bw") as file:
            while True:
                try:
                    addr, segment_response = self.conn.listen_single_segment()

                    if addr == (IP, self.broadcast_port) and segment_response.flag.fin and not segment_response.flag.syn and not segment_response.flag.ack:
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
                        
                    if addr == (IP, self.broadcast_port) and not segment_response.flag.ack and not segment_response.flag.fin and not segment_response.flag.syn:
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
                            sequence_number_list.append(int(segment_response.header['seq_num']))

                            print(f"[!] Segment {segment_response.header['seq_num']} written to file {self.file}")
                            
                            request_number += 1
                        elif int(segment_response.header['seq_num']) in sequence_number_list:
                            print(f"[!] [Server] Segment {segment_response.header['seq_num']} is already accepted")
                            message_ACK = Segment()
                            message_ACK.set_header({
                                "seq_num": 0,
                                "ack_num": segment_response.header['seq_num']
                            })
                            message_ACK.set_flag([segment.ACK_FLAG])
                            self.conn.send_data(message_ACK, addr)
                            print(f"[!] [Server] Sending segment {segment_response.header['seq_num']} acknowledgement")
                        else:
                            print(f"[!] [Server] Segment {segment_response.header['seq_num']} is not acknowleged")
                    
                    
                    else:
                        print(f"[!] [Server] Segment received")
                        print(f"[!] [Server] Segment is not acknowleged")
                except socket.timeout:
                    print(f"[!] [Server] Connection failed")
                    break
                    
        


if __name__ == '__main__':
    main = Client()
    main.three_way_handshake()
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
