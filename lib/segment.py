import struct

# Constants 
SYN_FLAG = 0b00000001
ACK_FLAG = 0b00000100
FIN_FLAG = 0b00000000

class SegmentFlag:
    def __init__(self, flag : bytes):
        # Init flag variable from flag byte
        self.flag = flag
        pass

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        return self.flag




class Segment:
    # -- Internal Function --
    def __init__(self):
        # Initalize segment
        self.header = {}
        self.flag = SegmentFlag(0b0)
        self.checksum = 0
        self.payload = 0b0
        pass

    def __str__(self):
        # Optional, override this method for easier print(segmentA)
        output = ""
        seq_num = self.header["seq_num"]
        ack_num = self.header["ack_num"]
        output += f"{'Sequence number':24} | {seq_num}\n"
        output += f"{'Acknowledge number':24} | {ack_num}\n"
        output += f"{'Flag':24} | {self.flag}\n"
        output += f"{'Checksum':24} | {self.checksum}\n"
        output += f"{'Payload':24} | {self.payload}\n"
        return output

    def __calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        pass


    # -- Setter --
    def set_header(self, header : dict):
        self.header = header
        pass

    def set_payload(self, payload : bytes):
        self.payload = payload
        pass

    def set_flag(self, flag_list : list):
        self.flag = flag_list[0]
        pass


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
        pass

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        pass


    # -- Checksum --
    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        pass
