import os
from io import BytesIO

import bitsv
from bitsv import crypto
from bitsv import utils

# [BITCOM PREFIXES]
B = '19HxigV4QyBv3tHpQVcUEQyq1pzZVdoAut'  # https://b.bitdb.network/
C = '19HxigV4QyBv3tHpQVcUEQyq1pzZVdoAut'  # https://c.bitdb.network/ --> writing to blockchain is same as B://
BCAT = '15DHFxWZJT58f9nhyGnsRBqrgwK4W6h4Up'  # https://bcat.bico.media/
BCATPART = '1ChDHzdd1H4wSjgGMHyndZm6qxEDGjqpJL'  # https://bcat.bico.media/ (raw data only after prefix)
D = '19iG3WTYSsbyos3uJ733yK4zEioi1FesNU'  # Dynamic - ownership over state of address
AIP = '15PciHG22SNLQJXMoSUaWVi7WSqc7hCfva'  # https://github.com/BitcoinFiles/AUTHOR_IDENTITY_PROTOCOL
MAP = '1PuQa7K62MiKCtssSLKy1kh56WWU7MtUR5'  # MAP protocol.

MEDIA_TYPE = {
# Images
'png' : 'image/png',
'jpg' : 'image/jpeg',

# Documents
'html': 'text/html',
'css' : 'text/css',
'js' : 'text/javascript',

# Audio
'mp3' : 'audio/mp3',
}

ENCODINGS = {
# Images
'png' : 'binary',
'jpg' : 'binary',

# Documents
'html': 'utf-8',
'css' : 'utf-8',
'js' : 'utf-8',

# Audio
'mp3' : 'binary',
}


class Upload(bitsv.PrivateKey):
    """
    A simple interface to a multitude of bitcoin protocols
    """

    # UTILITIES
    @staticmethod
    def file_to_binary(file):
        """Give the pathname to a png, jpg, gif, tiff, bmp
        returns binary

        Example path (for newer users): "C://Users/username/Pictures/my_picture.jpg etc."
        """
        with open(file, 'rb') as f:
            return f.read()

    @staticmethod
    def binary_to_hex(binary):
        # FIXME - may not just work for any file
        return binary.hex()

    @staticmethod
    def get_filename(path):
        if "\\" in path:
            lst = path.split(os.sep)
            return lst[len(lst)-1]
        else:
            lst = path.split("/")
            return lst[len(lst)-1]

    @staticmethod
    def get_file_ext(file):
        ext = file.split(r".")[1].strip(r"'")
        return ext

    @staticmethod
    def get_media_type_for_extension(ext):
        return MEDIA_TYPE[str(ext)]

    @staticmethod
    def get_encoding_type_for_extension(ext):
        return ENCODINGS[str(ext)]

    def get_media_type_for_file_name(self, file):
        return self.get_media_type_for_extension(self.get_file_ext(file))

    def get_encoding_for_file_name(self, file):
        return self.get_encoding_type_for_extension(self.get_file_ext(file))

    @staticmethod
    def send_rawtx(rawtx):
        return bitsv.network.services.BitIndex.broadcast_rawtx(rawtx)

    @staticmethod
    def send_lst_of_rawtxs(lst_of_tx):
        """Takes in list of rawtxs - returns txids of sent transactions if successful"""
        txs = []
        for tx in lst_of_tx:
            txs.append(bitsv.network.services.BitIndex.broadcast_rawtx(tx))
        return txs

    @staticmethod
    def calculate_txid(rawtx):
        rawtx = crypto.double_sha256(bitsv.utils.hex_to_bytes(rawtx))[::-1]
        return rawtx.hex()

    # B
    def b_create_rawtx_from_binary(self, binary, media_type, encoding=' ', file_name=' '):
        """Creates rawtx for sending data (<100kb) to the blockchain via the B:// protocol
        see: https://github.com/unwriter/B or https://b.bitdb.network/ for details"""

        hex_data = binary.hex()
        lst_of_pushdata = [(B, "utf-8"),  # B:// protocol prefix
                           (hex_data, 'hex'),
                           (media_type, "utf-8"),
                           (encoding, "utf-8"),  # Optional if no filename
                           (file_name, "utf-8")]  # Optional
        return self.create_op_return_rawtx(lst_of_pushdata)

    def b_create_rawtx_from_file(self, file, media_type, encoding=' ', file_name=' '):
        # FIXME - add checks for file extension type --> enforce correct parameters for protocol
        binary = self.file_to_binary(file)
        return self.b_create_rawtx_from_binary(binary, media_type, encoding=encoding, file_name=file_name)

    def b_create_rawtx_from_file_ezmode(self, file):
        """This function predicts the media_type, encoding and b:// filename from 'file' name and extension"""
        media_type = self.get_media_type_for_file_name(file)
        encoding = self.get_encoding_for_file_name(file)
        file_name = self.get_filename(file)
        binary = self.file_to_binary(file)
        return self.b_create_rawtx_from_binary(binary, media_type, encoding=encoding, file_name=file_name)

    def b_send_from_binary(self, binary, media_type, encoding=' ', file_name=' '):
        rawtx = self.b_create_rawtx_from_binary(binary, media_type, encoding=encoding, file_name=file_name)
        return self.send_rawtx(rawtx)

    def b_send_from_file(self, file, media_type, encoding=' ', file_name=' '):
        rawtx = self.b_create_rawtx_from_file(file, media_type, encoding=encoding, file_name=file_name)
        return self.send_rawtx(rawtx)

    # BCAT
    def bcat_parts_create_from_binary(self, binary):
        """Takes in binary data for upload - returns list of rawtx"""
        # Get full binary
        stream = BytesIO(binary)

        # FIXME I have just subtracted 10000 bytes instead of going through the logic of making everything perfectly
        #  end up with a finalised rawtx of exactly <= 100kb every time (Must include bytes taken up by UTXOs that
        #  will be used to cover the fees - which also needs to be calculated upfront based on what the transaction
        #  sizes will be - which depends on UTXOs you end up with a simultaneous equations problem - I'll fix it later.

        # Available space per tx = 100kb - BCATPART - "safety margin of 10,000 bytes for utxos etc"
        space_available_per_tx = 100000 - len(BCATPART.encode('utf-8')) - 10000  # temporary hack (-) 10,000 bytes

        txs = []  # to store hashes

        num_of_tx_required = (len(binary) // space_available_per_tx) + 1
        for _ in range(num_of_tx_required):
            lst_of_pushdata = [(BCATPART, 'utf-8'),
                               (stream.read(space_available_per_tx).hex(), 'hex')]
            txs.append(self.create_op_return_rawtx(lst_of_pushdata))
        return txs

    def bcat_parts_create_from_file(self, file):
        # FIXME - check if this will work for plain text / html etc.
        with open(file, 'rb') as f:
            binary = f.read()
        return self.bcat_parts_create_from_binary(binary)

    def bcat_parts_send_from_binary(self, binary):
        """returns txids of sent transactions if successful"""
        lst_of_tx = self.bcat_parts_create_from_binary(binary)
        return self.send_lst_of_rawtxs(lst_of_tx)

    def bcat_parts_send_from_file(self, file):
        """returns txids of sent transactions if successful"""
        # Get full binary
        with open(file, 'rb') as f:
            binary = f.read()
        binary = Upload.file_to_binary(binary)
        lst_of_tx = self.bcat_parts_create_from_binary(binary)
        return self.send_lst_of_rawtxs(lst_of_tx)

    def bcat_linker_create_from_txids(self, lst_of_txids, media_type, encoding, file_name, info=' ', flags=' '):
        """Creates bcat transaction to link up "bcat parts" (with the stored data).
        This BCAT:// protocol allows for concatenating data > 100kb (up to 310MB uncompressed) to the blockchain.
        see: https://bcat.bico.media/

        returns rawtx"""

        # FIXME - add checks
        lst_of_pushdata = [(BCAT, 'utf-8'),
                           (info, "utf-8"),  # B:// protocol prefix
                           (media_type, 'utf-8'),
                           (encoding, "utf-8"),
                           (file_name, "utf-8"),  # Optional if no filename
                           (flags, "utf-8")]  # Optional

        lst_of_pushdata.extend([(tx, 'hex') for tx in lst_of_txids])
        return self.create_op_return_rawtx(lst_of_pushdata)

    def bcat_linker_send_from_txids(self, lst_of_txids, media_type, encoding, file_name=' ', info=' ', flags=' '):
        """Creates and sends bcat transaction to link up "bcat parts" (with the stored data).
        This BCAT:// protocol allows for concatenating data > 100kb (up to 310MB uncompressed) to the blockchain.
        see: https://bcat.bico.media/"""

        rawtx = self.bcat_linker_create_from_txids(lst_of_txids, media_type, encoding, file_name, info=info,
                                                   flags=flags)
        return self.send_rawtx(rawtx)
