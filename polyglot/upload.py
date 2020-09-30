import os
import sys
import time
from io import BytesIO
from pathlib import Path
import bitsv
from bitsv import op_return
from bitsv import crypto
from bitsv import utils
from .bitcom import B, C, BCAT, BCATPART, D, AIP, MAP

# Temp hack to allow space for funding inputs (10,000 bytes allocated)
MAX_DATA_CARRIER_SIZE = 100_000  # bytes
SPACE_AVAILABLE_PER_TX_BCAT_PART = MAX_DATA_CARRIER_SIZE - \
    len(BCATPART.encode('utf-8')) - 10000  # temporary hack (-) 10,000 bytes


class Upload(bitsv.PrivateKey):
    """
    A simple interface to a multitude of bitcoin protocols
    """
    def __init__(self, wif=None, network='main', fee=1, utxo_min_confirmations=1):
        super().__init__(wif=wif, network=network)
        self.woc = bitsv.network.services.WhatsonchainNormalised(api_key=None, network=network)
        self.fee = fee
        self.utxo_min_confirmations = utxo_min_confirmations

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
        return Path(path).name

    @staticmethod
    def get_file_ext(file):
        ext = Path(file).suffix
        if ext and ext[0] == '.':
            ext = ext[1:]
        return ext

    def get_media_type_for_file_name(self, file):
        import magic
        return magic.from_file(file, mime=True)

    def get_encoding_for_file_name(self, file):
        import magic
        return magic.Magic(mime_encoding=True).from_file(file)

    def send_rawtx(self, rawtx):
        return self.woc.send_transaction(rawtx)

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
            if utxo.confirmations >= self.utxo_min_confirmations and utxo.amount >= self.fee * MAX_DATA_CARRIER_SIZE:
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

    def get_nonbcatpart_utxos(self):
        lst = []
        utxos = self.get_unspents()
        for utxo in utxos:
            if utxo.amount != MAX_DATA_CARRIER_SIZE:
                lst.append(utxo)
        return lst

    def get_split_outputs(self, utxos):
        """(crudely) splits utxos into 0.001 amounts with some remainder for fees"""
        sum = 0
        for utxo in utxos:
            sum += utxo.amount
        num_splits = int(sum // (self.fee * MAX_DATA_CARRIER_SIZE)) - 1
        my_addr = self.address
        outputs = []
        for i in range(num_splits):
            outputs.append((my_addr, self.fee * 0.001, 'bsv'))
        return outputs

    def combine_and_split_utxos(self, utxos):
        outputs = self.get_split_outputs(utxos)
        return self.send(outputs, unspents=utxos, fee=self.fee)

    def split_biggest_utxo(self):
        biggest_unspent = self.get_largest_utxo()
        return self.combine_and_split_utxos([biggest_unspent])

    def split_all_utxos(self):
        lst = self.get_nonbcatpart_utxos()
        return self.combine_and_split_utxos(lst)

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
        return self.create_transaction(outputs=[], message=lst_of_pushdata, combine=False,
            custom_pushdata=True, unspents=self.filter_utxos_for_bcat(), fee=self.fee)

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
                             "BCAT upload (" + str(len(utxos)) + " < " + str(number_bcat_parts) + "). "
                             "Please generate more 'Fresh' utxos and try again")

        for i in range(number_bcat_parts):
            data = stream.read(SPACE_AVAILABLE_PER_TX_BCAT_PART)
            lst_of_pushdata = [(BCATPART, 'utf-8'),
                               (data.hex(), 'hex')]

            lst_of_pushdata = op_return.create_pushdata(lst_of_pushdata)
            # bitsv sorts utxos by amount and then selects first the ones of *lowest* amount
            # so here we will manually select "Fresh" utxos (with 100,000 satoshis, 1 conf) one at a time
            fresh_utxo = utxos[i:i+1]
            txid = self.send(outputs=[], message=lst_of_pushdata, fee=self.fee, combine=False,
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
        return self.create_transaction(outputs=[], message=lst_of_pushdata, combine=False, custom_pushdata=True, unspents=utxos[-1:], fee=self.fee)

    def bcat_linker_send_from_txids(self, lst_of_txids, media_type, encoding, file_name=' ', info=' ', flags=' ', utxos=None):
        """Creates and sends bcat transaction to link up "bcat parts" (with the stored data).
        This BCAT:// protocol allows for concatenating data > 100kb (up to 310MB uncompressed) to the blockchain.
        see: https://bcat.bico.media/"""
        if utxos is None:
            utxos = self.filter_utxos_for_bcat()
        rawtx = self.bcat_linker_create_from_txids(lst_of_txids, media_type, encoding, file_name, info=info,
                                                   flags=flags, utxos=utxos[-1:])
        return self.send_rawtx(rawtx)

    def upload_bcat(self, file, media_type=None, encoding=None, file_name=None, utxos=None, txids=None):
        """broadcasts bcat parts and then bcat linker tx. Returns txid of linker.
        Extracts defaults for the media_type, encoding and filename from the file path
        Alternatively these parameters can be overridden as required"""
        if media_type is None:
            media_type = self.get_media_type_for_file_name(file)
        if encoding is None:
            encoding = self.get_encoding_for_file_name(file)
        if file_name is None:
            file_name = self.get_filename(file)
        if utxos is None:
            utxos = self.filter_utxos_for_bcat()
        if txids is None:
            txids = self.bcat_parts_send_from_file(file, utxos)
        txid = self.bcat_linker_send_from_txids(lst_of_txids=txids,
                                                media_type=media_type,
                                                file_name=file_name,
                                                encoding=encoding,
                                                utxos=utxos[-1:])
        return txid

    def confirmations(self, txids):
        """return an array of the number of confirmations the passed pending txids have
	todo: use bitsv to support checking any transactions"""
        dct = {}
        utxos = self.get_unspents()
        for utxo in utxos:
            dct[utxo.txid] = utxo.confirmations
        lst = []
        for txid in txids:
            if txid not in dct:
                lst.append(None)
            else:
                lst.append(dct[txid])
        return lst

    def upload_easy(self, file):
        """Convenience function to upload any file to the blockchain.
        Picks BCAT:// or B:// depending on filesize.
        Extracts the media_type, encoding and filename from the file path. Returns txid of
        result."""
        size = os.path.getsize(file)
        num_bcat_parts = self.get_number_bcat_parts(size)
        if sum([utxo.amount//MAX_DATA_CARRIER_SIZE for utxo in self.get_unspents()]) < num_bcat_parts:
            if (self.balance < size + 200000):
                raise ValueError("Not enough funds: send " + str(size + 200000 - self.balance) +
                                 " to " + self.address)
            else:
                # coins need consolidation
                self.send([])
        if sum([utxo.amount//MAX_DATA_CARRIER_SIZE for
                utxo in self.filter_utxos_for_bcat()]) < num_bcat_parts:
            # funds present but not ready
            self.split_all_utxos()
            print("Funds present but waiting network confirmation ...", file=sys.stderr)
            while sum([utxo.amount//MAX_DATA_CARRIER_SIZE for
                       utxo in self.filter_utxos_for_bcat()]) < num_bcat_parts:
                time.sleep(60)
            print("Got network confirmation", file=sys.stderr)
        if size < MAX_DATA_CARRIER_SIZE:
            return self.upload_b(file)
        else:
            return self.upload_bcat(file)
