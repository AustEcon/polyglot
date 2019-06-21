import os
from io import BytesIO
import bitsv
from bitsv import op_return
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

# Temp hack to allow space for funding inputs (10,000 bytes allocated)
SPACE_AVAILABLE_PER_TX_BCAT_PART = 100000 - len(BCATPART.encode('utf-8')) - 10000  # temporary hack (-) 10,000 bytes


MEDIA_TYPE = {
    # Images
    'png': 'image/png',
    'jpg': 'image/jpeg',

    # Documents
    'html': 'text/html',
    'css': 'text/css',
    'js': 'text/javascript',

    # Audio
    'mp3': 'audio/mp3',
}

ENCODINGS = {
    # Images
    'png': 'binary',
    'jpg': 'binary',

    # Documents
    'html': 'utf-8',
    'css': 'utf-8',
    'js': 'utf-8',

    # Audio
    'mp3': 'binary',
}


class Upload(bitsv.PrivateKey):
    """
    A simple interface to a multitude of bitcoin protocols
    """
    def __init__(self, wif=None):
        super().__init__(wif=wif)

        self.bix3 = bitsv.network.services.BitIndex3(api_key=None, network='main')

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
            return lst[len(lst) - 1]
        else:
            lst = path.split("/")
            return lst[len(lst) - 1]

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

    def send_rawtx(self, rawtx):
        return self.bix3.send_transaction(rawtx)['txid']

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

    @staticmethod
    def extract_txids(txids):
        ids = []
        for i in txids:
            ids.append(i['data']['txid'])
        return ids

    def filter_utxos_for_bcat(self):
        """filters out all utxos with 0 conf or too low amount for use in a BCAT part transaction"""
        filtered_utxos = []
        for utxo in self.get_unspents():
            if utxo.confirmations != 0 and utxo.amount >= 100000:
                filtered_utxos.append(utxo)
        return filtered_utxos

    def get_largest_utxo(self):
        lst = []
        utxos = self.get_unspents()
        for utxo in utxos:
            lst.append(utxo.amount)
        max_utxo_amount = max(lst)
        for utxo in utxos:
            if utxo.amount == max_utxo_amount and utxo.amount >= 0.02:
                return utxo

        # if nothing returned
        raise ValueError(
            'Error: It is likely that the utxo has an amount that is too little or you have no utxos for this key')

    def get_split_outputs(self, utxo):
        """(crudely) splits a utxo into 0.001 amounts with some remainder for fees"""
        num_splits = utxo.amount // 100000 - 1
        my_addr = self.address
        outputs = []
        for i in range(num_splits):
            outputs.append((my_addr, 0.001, 'bsv'))
        return outputs

    def split_biggest_utxo(self):
        biggest_unspent = self.get_largest_utxo()
        outputs = self.get_split_outputs(biggest_unspent)
        return self.send(outputs, unspents=[biggest_unspent], combine=False)

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
        lst_of_pushdata = op_return.create_pushdata(lst_of_pushdata)
        return self.create_transaction(outputs=[], message=lst_of_pushdata, combine=False, custom_pushdata=True, unspents=self.filter_utxos_for_bcat())

    def b_create_rawtx_from_file(self, file, media_type=None, encoding=None, file_name=None):
        # FIXME - add checks
        if media_type is None:
            media_type = self.get_media_type_for_file_name(file)
        if encoding is None:
            encoding = self.get_encoding_for_file_name(file)
        if file_name is None:
            file_name = self.get_filename(file)
        binary = self.file_to_binary(file)
        return self.b_create_rawtx_from_binary(binary, media_type, encoding=encoding, file_name=file_name)

    def b_send_from_file(self, file, media_type=None, encoding=None, file_name=None):
        """Convenience function to upload any file to the blockchain via the B:// protocol
        Extracts defaults for the media_type, encoding and filename from the file path
        Alternatively these parameters can be overridden as required

        A whitespace string can be used for encoding and filename if preferred"""
        if media_type is None:
            media_type = self.get_media_type_for_file_name(file)
        if encoding is None:
            encoding = self.get_encoding_for_file_name(file)
        if file_name is None:
            file_name = self.get_filename(file)
        rawtx = self.b_create_rawtx_from_file(file, media_type, encoding=encoding, file_name=file_name)
        return self.send_rawtx(rawtx)

    def b_send_from_binary(self, binary, media_type, encoding=' ', file_name=' '):
        rawtx = self.b_create_rawtx_from_binary(binary, media_type, encoding=encoding, file_name=file_name)
        return self.send_rawtx(rawtx)

    # alias
    upload_b = b_send_from_file

    # BCAT

    @staticmethod
    def get_number_bcat_parts(length_binary):
        num_parts = (length_binary // SPACE_AVAILABLE_PER_TX_BCAT_PART) + 1
        return num_parts

    def bcat_parts_send_from_binary(self, binary, utxos=None):
        """Takes in binary data for upload - returns list of rawtx"""

        # Get full binary
        stream = BytesIO(binary)
        if utxos is None:
            utxos = self.filter_utxos_for_bcat()

        txs = []
        number_bcat_parts = self.get_number_bcat_parts(len(binary))

        if len(utxos) - 1 >= number_bcat_parts:  # Leaves one Fresh utxo leftover for linker.
            pass
        else:
            raise ValueError("insufficient 'Fresh' unspent transaction outputs (utxos) to complete the "
                             "BCAT upload. Please generate more 'Fresh' utxos and try again")

        for i in range(number_bcat_parts):
            data = stream.read(SPACE_AVAILABLE_PER_TX_BCAT_PART)
            lst_of_pushdata = [(BCATPART, 'utf-8'),
                               (data.hex(), 'hex')]

            lst_of_pushdata = op_return.create_pushdata(lst_of_pushdata)
            # bitsv sorts utxos by amount and then selects first the ones of *lowest* amount
            # so here we will manually select "Fresh" utxos (with 100,000 satoshis, 1 conf) one at a time
            fresh_utxo = utxos[i:i+1]
            txid = self.send(outputs=[], message=lst_of_pushdata, fee=1, combine=False,
                             custom_pushdata=True, unspents=fresh_utxo)
            txs.append(txid)
        return txs

    def bcat_parts_send_from_file(self, file, utxos=None):
        if utxos is None:
            utxos = self.filter_utxos_for_bcat()
        binary = self.file_to_binary(file)
        return self.bcat_parts_send_from_binary(binary, utxos=utxos)

    def bcat_linker_create_from_txids(self, lst_of_txids, media_type, encoding, file_name, info=' ', flags=' ', utxos=None):
        """Creates bcat transaction to link up "bcat parts" (with the stored data).
        This BCAT:// protocol allows for concatenating data > 100kb (up to 310MB uncompressed) to the blockchain.
        see: https://bcat.bico.media/

        returns rawtx"""
        if utxos is None:
            utxos = self.filter_utxos_for_bcat()
        # FIXME - add checks
        lst_of_pushdata = [(BCAT, 'utf-8'),
                           (info, "utf-8"),  # B:// protocol prefix
                           (media_type, 'utf-8'),
                           (encoding, "utf-8"),
                           (file_name, "utf-8"),  # Optional if no filename
                           (flags, "utf-8")]  # Optional

        lst_of_pushdata.extend([(tx, 'hex') for tx in lst_of_txids])
        lst_of_pushdata = op_return.create_pushdata(lst_of_pushdata)
        return self.create_transaction(outputs=[], message=lst_of_pushdata, combine=False, custom_pushdata=True, unspents=utxos[-1:])

    def bcat_linker_send_from_txids(self, lst_of_txids, media_type, encoding, file_name=' ', info=' ', flags=' ', utxos=None):
        """Creates and sends bcat transaction to link up "bcat parts" (with the stored data).
        This BCAT:// protocol allows for concatenating data > 100kb (up to 310MB uncompressed) to the blockchain.
        see: https://bcat.bico.media/"""
        if utxos is None:
            utxos = self.filter_utxos_for_bcat()
        rawtx = self.bcat_linker_create_from_txids(lst_of_txids, media_type, encoding, file_name, info=info,
                                                   flags=flags, utxos=utxos[-1:])
        return self.send_rawtx(rawtx)

    def upload_bcat(self, file):
        """broadcasts bcat parts and then bcat linker tx. Returns txid of linker."""
        utxos = self.filter_utxos_for_bcat()
        txids = self.bcat_parts_send_from_file(file, utxos)
        txid = self.bcat_linker_send_from_txids(lst_of_txids=txids,
                                                media_type=self.get_media_type_for_file_name(file),
                                                file_name=file,
                                                encoding=self.get_encoding_for_file_name(file),
                                                utxos=utxos[-1:])
        return txid
