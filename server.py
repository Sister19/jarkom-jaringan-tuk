from lib.connection import Connection
from lib.segment import Segment
import lib.segment as segment
import socket

import sys
import os

IP = "127.0.0.1"
N = 3
MAX_SEGMENT_PAYLOAD = 32756
# MAX_SEGMENT_PAYLOAD = 1000

class Server:
    def __init__(self):
        # Init server
        # self.conn = Connection("localhost", 3121)
        self.port = int(sys.argv[1])
        self.file = sys.argv[2]
        self.conn = Connection(IP, self.port)
        print(f"[!] Server started at localhost:{self.port}")
        print(f"[!] Source file | README.md | 1012 bytes")
        print(f"[!] Listening to broadcast address for clients.\n")
        self.clients = []


    def listen_for_clients(self):
        # Waiting client for connect
        while True:
            addr, segment = self.conn.listen_single_segment()
            print(segment)
            print(f"[!] Received request from {addr}")

            if (
                segment.flag.syn  # Check if request if from client that wants to establish connection
                and segment.valid_checksum()  # check if the request contains no error when transmitting with checksum
                and addr not in self.clients  # check if client is already in client list
            ):
                self.clients.append(addr)
                print(f"[!] Client added to list")
                listen_more = input("[?] Listen more? (y) ")
                if listen_more == "y":
                    continue
                else:
                    break
            else:
                print(f"[!] Client cannot be added to list")


    def start_file_transfer(self):
        print(f"\nClient list:")
        i = 0
        for client in self.clients:
            print(f"{i + 1}. {IP}:{client}")
            i += 1
        
        # Handshake & file transfer for all client
        print(f"\n[!] Commencing file transfer...")

        i = 0
        for client in self.clients:
            print(f"\n[!] [Handshake] Handshake to client {i + 1}... {client}")
            handshake_success = self.three_way_handshake(client)
            
            if handshake_success:
                print(f"[!] [Handshake] Handshake to client {i + 1} success")
                print(f"[!] [Client {i + 1}] Initiating file transfer...")
                self.file_transfer(client)
            else:
                print(f"[!] [Handshake] Handshake to client {i + 1} failed")
            i += 1
        
        print(f"\nClosing connection...")
        self.conn.close_socket()
        print(f"Connection closed")

    def file_transfer(self, client_addr : ("ip", "port")):
        sequence_base = 0
        sequence_max = N
        with open(self.file, "rb") as file:
            file_size = os.path.getsize(self.file)
            total_segment_number = file_size // MAX_SEGMENT_PAYLOAD if file_size % MAX_SEGMENT_PAYLOAD == 0  else (file_size // MAX_SEGMENT_PAYLOAD) + 1
            sequence_max = min(total_segment_number, sequence_max)

            repeat = True
            while True:
                if sequence_base == sequence_max:
                    break
                
                # print(repeat)
                if repeat:
                    for sequence_number in range(sequence_base, sequence_max):
                        file.seek(MAX_SEGMENT_PAYLOAD * sequence_number)
                        file_bytes = file.read(MAX_SEGMENT_PAYLOAD)

                        file_segment = Segment()
                        file_segment.set_header({
                            "seq_num": sequence_number,
                            "ack_num":0
                        })

                        file_segment.set_payload(file_bytes)
                        self.conn.send_data(file_segment, client_addr)
                        print(f"[!] [Client] [Num={sequence_number}] Sending segment to client...")
                        # break
                else:
                    file.seek(MAX_SEGMENT_PAYLOAD * (sequence_max - 1))
                    file_bytes = file.read(MAX_SEGMENT_PAYLOAD)

                    file_segment = Segment()
                    file_segment.set_header({
                        "seq_num": sequence_max - 1,
                        "ack_num":0
                    })

                    file_segment.set_payload(file_bytes)
                    self.conn.send_data(file_segment, client_addr)
                    print(f"[!] [Client] [Num={sequence_max - 1}] Sending segment to client...")
            
                while sequence_base < sequence_max:
                    self.conn.set_timeout(3)
                    try:
                        addr, segment_response = self.conn.listen_single_segment()
                        if addr == client_addr and segment_response.flag.ack and segment_response.header["ack_num"] == sequence_base:
                            sequence_base = sequence_base + 1
                            sequence_max = min(total_segment_number, sequence_max + 1)

                            print(f"[!] [Client] [Num={segment_response.header['ack_num']}] [ACK] ACK received, new sequence base = {sequence_base}")
                            repeat = False
 
                            if sequence_max - sequence_base == N:
                                break

                    except socket.timeout:
                        print(f"\n[!] [Client] [Num={sequence_base}] [Timeout] ACK response timeout, resending segment num..")
                        repeat = True
                        break

            send_fin = True
            while send_fin:
                message_FIN = Segment()
                message_FIN.set_header({
                    "seq_num": 0,
                    "ack_num": 0
                })

                message_FIN.set_flag([segment.FIN_FLAG])
                print(f"[!] [FIN] Sending FIN..")
                self.conn.send_data(message_FIN, client_addr)

                self.conn.set_timeout(3)
                try:
                    addr, segment_response = self.conn.listen_single_segment()
                    if addr == client_addr and segment_response.flag.ack and segment_response.flag.fin and not segment_response.flag.syn:
                        print(f"[!] [Client] [FIN] [ACK] ACK received")
                        send_fin = False

                except socket.timeout:
                    print(f"\n[!] [Client] [FIN] [Timeout] ACK response timeout, resending FIN segment..")

    def three_way_handshake(self, client_addr: ("ip", "port")) -> bool:
       # Three way handshake, server-side, 1 client
        message_SYN_ACK = Segment()
        message_SYN_ACK.set_header({
            "seq_num": 0,
            "ack_num":0
        })
        message_SYN_ACK.set_flag([segment.SYN_FLAG, segment.ACK_FLAG])
        self.conn.send_data(message_SYN_ACK, client_addr)
        print(f"[!] Sending SYNC, ACK segment response to port {client_addr[1]}")
        return self.three_way_handshake_response(client_addr)

        
    
    def three_way_handshake_response(self, client_addr: ("ip", "port")):
        self.conn.set_timeout(200)
        try:
            addr, segment_response = self.conn.listen_single_segment()

            if (
                segment_response.flag.ack  # Check if request if from client that wants to establish connection
                and segment_response.valid_checksum()  # check if the request contains no error when transmitting with checksum
                and addr == client_addr # check if client is already in client list
            ):
                print(f"[!] Received ACK response from client {addr}")
                return True
            else:
                return False
        except socket.timeout:
            print("Lewat timeout")
            return False



if __name__ == '__main__':
    main = Server()
    main.listen_for_clients()
    main.start_file_transfer()
    # while True:
    #     print(main.conn.listen_single_segment().get_payload().decode("utf8"))
