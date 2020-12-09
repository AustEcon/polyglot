import gzip
import os
from urllib.parse import urlparse

from bitsv.network import NetworkAPI

from .bitcom import B, C, BCAT, BCATPART, D, AIP, MAP

class Download(NetworkAPI):
    def __init__(self, network='main'):
        super().__init__(network=network)

    # UTILITIES
    @staticmethod
    def binary_to_file(binary, file):
        """Give the pathname to a file
        makes needed subdirectories and writes binary to it

        Example path (for newer users): "C://Users/username/Pictures/my_picture.jpg etc."
        """
        subdirs = os.path.dirname(file)
        if subdirs:
            os.makedirs(subdirs, exist_ok=True)
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
            fields['encoding'] = self.binary_to_bsv_string(data[offset + 3])
        if len(data) > offset + 4:
            fields['name'] = self.binary_to_bsv_string(data[offset + 4])
        if len(data) > offset + 5:
            fields['extra'] = data[offset + 5:]
        return fields

    def b_binary_from_pushdata(self, data):
        fields = self.b_fields_from_pushdata(data)
        if len(fields):
            return fields['data']
        else:
            return None

    def b_fields_from_txid(self, txid):
        fields = {}
        for script in self.scripts_from_txid(txid):
            data = self.pushdata_from_script(script)
            if len(fields):
                if 'extra' not in fields:
                    fields['extra'] = data
                else:
                    fields['extra'].extend(data)
            else:
                fields = self.b_fields_from_pushdata(data)
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
   
    def bcat_part_binary_from_pushdata(self, data, gunzip = False):
        if not self.bcat_part_detect_from_pushdata(data):
            subfields = self.bcat_linker_fields_from_pushdata(data)
            if subfields:
                gunzip = gunzip and subfields['flag'] in ('gzip', 'nested-gzip')
                return self.bcat_binary_from_txids(subfields['parts'], gunzip)
            else:
                return self.b_binary_from_pushdata(data)
        offset = 0
        if len(data[0]) == 0:
            offset = 1
        return b''.join(data[offset + 1:])

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

    def bcat_binary_from_txids(self, txids, gunzip = False):
        data = bytes()
        for txid in txids:
            data += self.bcat_part_binary_from_txid(txid)
        if gunzip:
            data = gzip.decompress(data)
        return data

    def bcat_fields_from_linker_fields(self, fields, gunzip = True):
        fields = fields.copy()
        gunzip = gunzip and fields['flag'] in ('gzip', 'nested-gzip')
        fields['data'] = self.bcat_binary_from_txids(fields['parts'], gunzip)
        if gunzip:
            # change 'flag' to reflect that we mutated the data
            fields['flag'] = fields['flag'].replace('zip','unzipped')
        return fields

    def bcat_fields_from_pushdata(self, data, gunzip = True):
        fields = self.bcat_linker_fields_from_pushdata(data)
        return self.bcat_fields_from_linker_fields(fields, gunzip)

    def bcat_fields_from_txid(self, txid, gunzip = True):
        for script in self.scripts_from_txid(txid):
            data = self.pushdata_from_script(script)
            fields = self.bcat_linker_fields_from_pushdata(data)
            if fields:
                return self.bcat_fields_from_linker_fields(fields, gunzip)

    def download_bcat(self, txid, file, gunzip = True):
        fields = self.bcat_linker_fields_from_txid(txid)
        if not fields:
            raise ValueError('bcat tx not found')
        if gunzip and fields['flag'] in ('gzip', 'nested-gzip'):
            # change 'flag' to reflect that we mutated the data
            fields['flag'] = fields['flag'].replace('zip','unzipped')
        else:
            gunzip = False
        with open(file, 'wb') as f:
            for txid in fields['parts']:
                data = self.bcat_part_binary_from_txid(txid)
                if gunzip:
                    data = gzip.decompress(data)
                f.write(data)
        return fields

    # D

    def d_detect_from_pushdata(self, data):
        return len(data) >= 3 and (data[0].decode('utf-8') == D or data[1].decode('utf-8') == D)

    def d_detect_from_txid(self, txid):
        for script in self.scripts_from_txid(txid):
            data = self.pushdata_from_script(script)
            if self.d_detect_from_pushdata(data):
                return True
        return False

    def d_linker_fields_from_pushdata(self, data):
        fields = {}
        if not self.d_detect_from_pushdata(data):
            return fields
        offset = 0
        if len(data[0]) == 0:
            offset = 1
        fields['key'] = self.binary_to_bsv_string(data[offset + 1])
        fields['value'] = self.binary_to_bsv_string(data[offset + 2])
        fields['type'] = self.binary_to_bsv_string(data[offset + 3])
        fields['sequence'] = int(data[offset + 4])
        if len(data) > offset + 5:
            fields['extra'] = data[offset + 5:]
        return fields

    def d_linker_fields_from_txid(self, txid):
        fields = {}
        for script in self.scripts_from_txid(txid):
            data = self.pushdata_from_script(script)
            if len(fields):
                if 'extra' not in fields:
                    fields['extra'] = data
                else:
                    fields['extra'].extend(data)
            else:
                fields = self.d_linker_fields_from_pushdata(data)
                if fields:
                    fields['txid'] = txid
        return fields

    def d_linker_fields_from_address(self, address):
        for txid in self.get_transactions(address):
            fields = self.d_linker_fields_from_txid(txid)
            if fields:
                yield fields

    def d_fields_from_linker_fields(self, fields):
        fields = fields.copy()
        if not len(fields):
            fields['data'] = None
        elif fields['value'] is None:
            fields['data'] = None
        elif fields['type'] == 'txt':
            fields['data'] = bytes(fields['value'], 'utf-8')
        elif fields['type'] == 'tx' or fields['type'] == 'b' or fields['type'] == 'bcat':
            fields['data'] = None
            for script in self.scripts_from_txid(fields['value']):
                data = self.pushdata_from_script(script)
                if self.b_detect_from_pushdata(data):
                    newbinary = self.b_binary_from_pushdata(data)
                elif self.bcat_linker_detect_from_pushdata(data):
                    newbinary = self.bcat_fields_from_pushdata(data)['data']
                else:
                    raise ValueError('unrecognised tx type id {}'.format(fields['value']))
                if newbinary is not None:
                    if fields['data'] is not None:
                        fields['data'] += newbinary
                    else:
                        fields['data'] = newbinary
        else:
            raise ValueError('unhandled d type "{}"'.format(fields['type']))
        return fields

    def d_fields_from_address(self, address):
        for fields in self.d_linker_fields_from_address(address):
            yield self.d_fields_from_linker_fields(fields)

    def download_d_linker_fields(self, fields, file):
        if fields['type'] == 'txt':
            data = bytes(fields['value'], 'utf-8')
            self.binary_to_file(data, file)
        elif fields['type'] == 'tx' or fields['type'] == 'b' or fields['type'] == 'bcat':
            try:
                self.download_bcat(fields['value'], file)
            except ValueError:
                self.download_b(fields['value'], file)
        else:
            raise ValueError('unrecognised d value')

    def download_d(self, address, key, file):
        for linker_fields in self.d_linker_fields_from_address(address):
            if linker_fields['key'] == key:
                self.download_d_linker_fields(linker_fields, file)
        raise ValueError('d tx not found')

    # urls

    def download_url(self, url, file):
        url = urlparse(url)
        if url.scheme == 'b':
            return self.download_b(url.netloc, file)
        elif url.scheme == 'bcat':
            return self.download_bcat(url.netloc, file)
        elif url.scheme == 'd':
            urlpath = url.path
            if len(urlpath) and urlpath[0] == '/':
                urlpath = urlpath[1:]
            return self.download_d(url.netloc, urlpath, file)
        elif url.scheme == 'bit':
            if url.netloc == D:
                return self.download_url('D:/{}'.format(url.path), file)
            elif url.netloc == B:
                return self.download_url('B:/{}'.format(url.path), file)
            elif url.netloc == BCAT:
                return self.download_url('BCAT:/{}'.format(url.path), file)
        raise ValueError('unrecognised url scheme')
