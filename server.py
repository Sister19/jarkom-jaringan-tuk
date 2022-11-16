from lib.connection import Connection
from lib.segment import Segment
import lib.segment as segment

IP = "127.0.0.1"
PORT = 3000
FILE = "README.md"
class Server:
    def __init__(self):
        # Init server
        # self.conn = Connection("localhost", 3121)
        self.conn = Connection(IP, PORT)
        print(f"[!] Server started at localhost:{PORT}")
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

    def file_transfer(self, client_addr : ("ip", "port")):
        # File transfer, server-side, Send file to 1 client
        # Sb := 0
        # Sm := N + 1
        # Repeat the following steps forever:
        #     if you receive an ack number where Rn > Sb then
        #         Sm := (Sm − Sb) + Rn
        #         Sb := Rn
        #     if no segment is in transmission then
        #         Transmit segments where Sb ≤ Sn ≤ Sm.  
        #         segments are transmitted in order.
        print(f"[!] [FIN] Sending FIN..")
        pass

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



if __name__ == '__main__':
    main = Server()
    main.listen_for_clients()
    main.start_file_transfer()
    # while True:
    #     print(main.conn.listen_single_segment().get_payload().decode("utf8"))
