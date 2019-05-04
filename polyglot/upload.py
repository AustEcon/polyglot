import bitsv

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


