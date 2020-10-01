from bitsv.network import NetworkAPI

# [BITCOM PREFIXES]
B = '19HxigV4QyBv3tHpQVcUEQyq1pzZVdoAut'  # https://b.bitdb.network/
C = '19HxigV4QyBv3tHpQVcUEQyq1pzZVdoAut'  # https://c.bitdb.network/ --> writing to blockchain is same as B://
BCAT = '15DHFxWZJT58f9nhyGnsRBqrgwK4W6h4Up'  # https://bcat.bico.media/
BCATPART = '1ChDHzdd1H4wSjgGMHyndZm6qxEDGjqpJL'  # https://bcat.bico.media/ (raw data only after prefix)
D = '19iG3WTYSsbyos3uJ733yK4zEioi1FesNU'  # Dynamic - ownership over state of address
AIP = '15PciHG22SNLQJXMoSUaWVi7WSqc7hCfva'  # https://github.com/BitcoinFiles/AUTHOR_IDENTITY_PROTOCOL
MAP = '1PuQa7K62MiKCtssSLKy1kh56WWU7MtUR5'  # MAP protocol.

class Download(NetworkAPI):
    def __init__(self, network='main'):
        super().__init__(network=network)

    # UTILITIES
    @staticmethod
    def binary_to_file(binary, file):
        """Give the pathname to a png, jpg, gif, tiff, bmp
        writes binary to it

        Example path (for newer users): "C://Users/username/Pictures/my_picture.jpg etc."
        """
        with open(file, 'wb') as f:
            f.write(binary)

    @staticmethod
    def hex_to_binary(hex):
        # FIXME - may not just work for any file
        return bytes.fromhex(hex)

    def scripts_from_txid(self, txid):
        lst = []
        tx = self.get_transaction(txid)
        for output in tx.outputs:
            lst.append(output.scriptpubkey)

    @staticmethod
    def pushdata_from_script(script):
        script = Download.hex_to_binary(script)
        offset = 0
        data = []
        while offset < len(script):
            opcode = script[offset]
            offset += 1
            if opcode == 0x00: # OP_0, OP_FALSE
                data.append(bytes(0))
            elif opcode <= 0x4b: # short data
                data.append(script[offset : offset + opcode])
                offset += opcode
            elif opcode == 0x4c: # OP_PUSHDATA1
                length = script[offset]
                data.append(script[offset + 1 : offset + 1 + length])
                offset += 1 + length
            elif opcode == 0x4d: # OP_PUSHDATA2
                length = script[offset] + script[offset + 1] * 0x100
                data.append(script[offset + 2 : offset + 2 + length])
                offset += 2 + length
            elif opcode == 0x4e: # OP_PUSHDATA4
                length = script[offset] + script[offset + 1] * 0x100 + script[offset + 2] * 0x10000 + script[offset + 3] * 0x1000000
                data.append(script[offset + 4 : offset + 4 + length])
                offset += 4 + length
            elif opcode == 0x4f: # OP_1NEGATE
                data.append(bytes([0xff])) # -1 is 0xff in twos complement
            elif opcode == 0x51: # OP_1, OP_TRUE
                data.append(bytes([0x01]))
            elif opcode > 0x50 and opcode <= 0x60: # OP_#
                data.append(bytes([opcode - 0x50]))
            elif opcode == 0x61: # OP_NOP
                pass
            elif opcode == 0x6a: # OP_RETURN
                pass
            elif opcode == 0x80: # OP_RESERVED
                pass
            elif opcode == 0xb0 or (opcode >= 0xb3 and opcode <= 0xb9): # OP_NOP#
                pass
            else:
                # not data-only
                return []
        return data

    # B

    def b_detect_from_pushdata(self, data):
        return len(data) >= 3 and (data[0].decode('utf-8') == B or data[1].decode('utf-8') == B)

    def b_detect_from_txid(self, txid):
        for script in self.scripts_from_txid(txid):
            data = self.pushdata_from_script(script)
            if self.b_detect_from_pushdata(data):
                return True
        return False

    def b_fields_from_pushdata(self, data):
        fields = {}
        if not self.b_detect_from_pushdata(data):
            return fields
        offset = 0
        if len(data[0]) == 0:
            offset = 1
        fields['data'] = data[offset + 1]
        fields['mediatype'] = data[offset + 2].decode('utf-8')
        if len(data) > offset + 3:
            fields['encoding'] = data[offset + 3].decode('utf-8')
        if len(data) > offset + 4:
            fields['filename'] = data[offset + 4].decode('utf-8')
        if len(data) > offset + 5:
            fields['extra'] = data[offset + 5:]
        return fields

    def b_fields_from_txid(self, txid):
        fields = {}
        for script in self.scripts_from_txid(txid):
            data = self.pushdata_from_script(script)
            newfields = self.b_fields_from_pushdata(data)
            if len(fields):
                fields['extra'].extend(newfields)
            elif len(newfields):
                fields = newfields
        return fields

    def b_file_from_txid(self, txid, file):
        fields = self.b_fields_from_txid(txid)
        if not len(fields):
            raise ValueError('b tx not found')
        binary_to_file(fields['data'], file)

    # alias
    download_b = b_file_from_txid

    # BCAT
        # todo
