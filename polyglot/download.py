from bitsv.network import NetworkAPI

from .bitcom import B, C, BCAT, BCATPART, D, AIP, MAP

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
        return lst

    @staticmethod
    def binary_to_bsv_string(binary):
        string = binary.decode('utf-8')
        if string in ('\0','\t','\n','\x0B','\r',' ',''):
            string = None
        return string

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
            fields['encoding'] = self.binary_to_bsv_string(data[offset + 3].decode('utf-8'))
        if len(data) > offset + 4:
            fields['name'] = self.binary_to_bsv_string(data[offset + 4].decode('utf-8'))
        if len(data) > offset + 5:
            fields['extra'] = data[offset + 5:]
        return fields

    def b_binary_from_pushdata(self, data):
        fields = self.b_fields_from_pushdata
        if len(fields):
            return fields['data']
        else:
            return None

    def b_fields_from_txid(self, txid):
        fields = {}
        for script in self.scripts_from_txid(txid):
            data = self.pushdata_from_script(script)
            newfields = self.b_fields_from_pushdata(data)
            if len(fields):
                if 'extra' not in fields:
                    fields['extra'] = newfields
                else:
                    fields['extra'].extend(newfields)
            elif len(newfields):
                fields = newfields
        return fields

    def b_file_from_txid(self, txid, file):
        fields = self.b_fields_from_txid(txid)
        if not fields:
            raise ValueError('b tx not found')
        self.binary_to_file(fields['data'], file)
        return fields

    # alias
    download_b = b_file_from_txid

    # BCAT
    
    def bcat_part_detect_from_pushdata(self, data):
        return len(data) >= 2 and (data[0].decode('utf-8') == BCATPART or data[1].decode('utf-8') == BCATPART)

    def bcat_part_detect_fromtxid(self, txid):
        for script in self.scripts_from_txid(txid):
            data = self.pushdata_from_script(script)
            if self.bcat_part_detect_from_pushdata(data):
                return True
        return False
   
    def bcat_part_binary_from_pushdata(self, data):
        if not self.bcat_part_detect_from_pushdata(data):
            return self.b_binary_from_pushdata(data)
        offset = 0
        if len(data[0]) == 0:
            offset = 1
        return b''.join(data[offset:]))))

    def bcat_part_binary_from_txid(self, txid):
        binary = b''
        for script in self.scripts_from_txid(txid):
            data = self.pushdata_from_script(script)
            newbinary = self.bcat_part_binary_from_pushdata(data)
            if newbinary is not None:
                binary += newbinary
        return binary

    def bcat_linker_detect_from_pushdata(self, data):
        return len(data) >= 8 and (data[0].decode('utf-8') == BCAT or data[1].decode('utf-8') == BCAT)

    def bcat_linker_detect_from_txid(self, txid):
        for script in self.scripts_from_txid(txid):
            data = self.pushdata_from_script(script)
            if self.bcat_linker_detect_from_pushdata(data):
                return True
        return False

    def bcat_linker_fields_from_pushdata(self, data):
        fields = {}
        if not self.bcat_linker_detect_from_pushdata(data):
            return fields
        offset = 0
        if len(data[0]) == 0:
            offset = 1
        fields['info'] = self.binary_to_bsv_string(data[offset + 1])
        fields['mediatype'] = self.binary_to_bsv_string(data[offset + 2])
        fields['encoding'] = self.binary_to_bsv_string(data[offset + 3])
        fields['name'] = self.binary_to_bsv_string(data[offset + 4])
        fields['flag'] = self.binary_to_bsv_string(data[offset + 5])
        parts = []
        for link in data[offset + 6:]:
            parts.append(link.hex())
        fields['parts'] = parts

        return fields

    def bcat_linker_fields_from_txid(self, txid):
        fields = {}
        for script in self.scripts_from_txid(txid):
            data = self.pushdata_from_script(script)
            fields = self.bcat_linker_fields_from_pushdata(data)
            if fields:
                break
        return fields

    def bcat_fields_from_txid(self, txid):
        fields = self.bcat_linker_fields_from_txid(txid)
        if not fields:
            return fields
        data = bytes()
        for txid in fields['parts']:
            data += self.bcat_part_binary_from_txid(txid)
        fields['data'] = data
        return fields

    def download_bcat(self, txid, file):
        fields = self.bcat_linker_fields_from_txid(txid)
        if not fields:
            raise ValueError('bcat tx not found')
        with open(file, 'wb') as f:
            for txid in fields['parts']:
                f.write(self.bcat_part_binary_from_txid(txid))
        return fields

