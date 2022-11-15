import struct

# Constants 
SYN_FLAG = 0b00000010
ACK_FLAG = 0b00001000
FIN_FLAG = 0b00000001

class SegmentFlag:
    def __init__(self, flag : bytes):
        # Init flag variable from flag byte
        self.syn = bool(SYN_FLAG & flag)
        self.ack = bool(ACK_FLAG & flag)
        self.fin = bool(FIN_FLAG & flag)

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        flag_result  = 0b0
        if (self.syn):
            flag_result |= SYN_FLAG
            if (self.ack):
                flag_result |= ACK_FLAG 
                if (self.fin):
                    flag_result |= FIN_FLAG
            else:
                if (self.fin):
                    flag_result |= FIN_FLAG
        else:
            if (self.ack):
                flag_result |= ACK_FLAG
                if (self.fin):
                    flag_result |= FIN_FLAG
            else:
                if (self.fin):
                    flag_result |= FIN_FLAG
        return struct.pack("<B", flag_result)




class Segment:
    # -- Internal Function --
    def __init__(self):
        # Initalize segment
        self.header = {}
        self.flag = SegmentFlag(0b0)
        self.checksum = 0
        self.payload = b""

    def __str__(self):
        # Optional, override this method for easier print(segmentA)
        output = ""
        seq_num = self.header["seq_num"]
        ack_num = self.header["ack_num"]
        output += f"{'Sequence number':24} | {seq_num}\n"
        output += f"{'Acknowledge number':24} | {ack_num}\n"
        output += f"{'SYN Flag':24} | {self.flag.syn}\n"
        output += f"{'ACK Flag':24} | {self.flag.ack}\n"
        output += f"{'FIN Flag':24} | {self.flag.fin}\n"
        output += f"{'Checksum':24} | {self.checksum}\n"
        output += f"{'Payload':24} | {self.payload}\n"
        return output

    def __calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        # using 16 bits datasum
        seq_num = struct.pack("<I", self.header["seq_num"])
        ack_num = struct.pack("<I", self.header["ack_num"])
        flag = self.flag.get_flag_bytes()
        empty_padding = struct.pack("x")
        payload = self.payload
        # sum all except self.checksum
        datasum = seq_num + ack_num + flag + empty_padding + payload
        data = datasum.hex()
        # split data into 2 bytes
        data = [data[i : i + 2] for i in range(0, len(data), 2)]
        # sum all data in 16 bits
        checksum = 0
        for i in data:
            checksum += int(i, 16)
        # get last 16 bits checksum
        return checksum & 0xFFFF


    # -- Setter --
    def set_header(self, header : dict):
        self.header["seq_num"] = header["seq_num"]
        self.header["ack_num"] = header["ack_num"]

    def set_payload(self, payload : bytes):
        self.payload = payload

    def set_flag(self, flag_list : list):
        flag_result = 0b0
        for flag in flag_list:
            flag_result |= flag
        self.flag = SegmentFlag(flag_result)


    # -- Getter --
    def get_flag(self) -> SegmentFlag:
        return self.flag

    def get_header(self) -> dict:
        return self.header

    def get_payload(self) -> bytes:
        return self.payload


    # -- Marshalling --
    def set_from_bytes(self, src : bytes):
        # From pure bytes, unpack() and set into python variable
        self.header["seq_num"] = struct.unpack("<I", src[0:4])
        self.header["ack_num"] = struct.unpack("<I", src[4:8])
        self.flag = SegmentFlag(struct.unpack("<B", src[8:9]))
        self.checksum = struct.unpack("<H", src[10:12])
        self.payload = src[12:]

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        self.checksum = self.__calculate_checksum()

        bytes_result = b""
        bytes_result += struct.pack("<I", self.header["seq_num"])
        bytes_result += struct.pack("<I", self.header["ack_num"])
        bytes_result += self.flag.get_flag_bytes()
        bytes_result += struct.pack("x")
        bytes_result += struct.pack("<H", self.checksum)
        bytes_result += self.payload
        return bytes_result


    # -- Checksum --
    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        return self.__calculate_checksum() == 0x0000 # 16 bits
