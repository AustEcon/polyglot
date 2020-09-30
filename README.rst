Polyglot: Bitcoin protocols made easy
=====================================
Documentation: https://austecon.github.io/polyglot/
Powered by BitSV: https://github.com/AustEcon/bitsv

Powered by BitSV: https://github.com/AustEcon/bitsv

.. image:: https://img.shields.io/travis/AustEcon/polyglot.svg?branch=master&style=flat-square
    :target: https://travis-ci.org/AustEcon/polyglot

.. image:: https://img.shields.io/pypi/pyversions/bitsv.svg?style=flat-square
    :target: https://pypi.org/project/bitsv

.. image:: https://img.shields.io/badge/license-MIT-orange.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License


------

Polyglot is  `designed to be <https://austecon.github.io/polyglot/guide/intro.html>`_
Bitcoin SV's most intuitive way to interact with a myriad of metanet protocols through *python* -
a match made in heaven.

The style of this library is inspired by ofek's library `bit <https://github.com/ofek/bit>`_
(`bitsv's <https://github.com/AustEcon/bitsv>`_ predecessor)

**Here are some examples:**

Polyglot extends bitsv with the **polyglot.Upload** class, which inherits all of the properties of
the **bitsv.PrivateKey** class such as checking balance, unspends, sending payments etc.


1. Upload an image < 100kb with b:// protocol (https://github.com/unwriter/B):

.. code-block:: python

    >>> import polyglot
    >>> uploader = polyglot.Upload('your private key goes here in WIF format')
    >>> # Optional parameters shown for completeness are populated from the file path by default
    >>> uploader.upload_b(file, media_type=None, encoding=None, file_name=None)

See image here: https://bico.media/252ea6d5a4a4bfc956518403f6e5aa2ced1c2590d1120cd75341e0233d1b06e3

This works for a wide range of media types.

2. Upload large multimedia > 100kb with bcat:// protocol (https://bcat.bico.media/):

.. code-block:: python

    >>> file = "C:/Users/username/Pictures/BSV_banner.jpg""
    >>> uploader.upload_bcat(file)

See image here: https://bico.media/be8b6a79e66934d3419265fbf3295d03e331a4c08098ae7f817a7592ffaedd2b

Please note: For BCAT protocol, it is very important to have an adequate number of "fresh" utxos with 1 confirmation to generate the parts. To do this see #3 Utilities (next).

3. Basic Utilities

Some basic utilities are included for working with utxo splitting and extracting the media type / handling of the file based on the file path (with extension and content) - to cover some potentially more advanced useage patterns of the B and BCAT protocols.

.. code-block:: python

    >>> uploader.get_media_type_for_file_name(file) #--> media_type
    >>> uploader.get_encoding_for_file_name(file) #--> encoding,
    >>> uploader.get_filename(path) #--> file_name.ext)

But additionally:

.. code-block:: python

    >>> uploader.get_largest_utxo(self) #--> largest utxo (for splitting)
    >>> uploader.split_biggest_utxo(self) #--> splits utxo into 100000 satoshi amounts
    >>> uploader.filter_utxos_for_bcat(self) #-- > filters utxos with 0 conf or too low amount to handle a 100kb tx
    >>> get_file_ext(file) #--> .ext
    >>> calculate_txid(rawtx) #--> txid



Features
--------

Currently Working:
~~~~~~~~~~~~~~~~~~

1. Uploading
~~~~~~~~~~~~
- B:// (for multimedia up to 100kb) - https://github.com/unwriter/B
- BCAT:// (for multimedia up to 310mb uncompressed, 110GB with nested gzip) - https://bcat.bico.media/

2. UTXO management
~~~~~~~~~~~~~~~~~~
- Utilities for splitting / selecting UTXOs for a single private key - especially for use in BCAT protocol.
- Bip32 level UTXO management is also planned

Planned:
~~~~~~~~

1. HTML reference converter
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A Class that will allow for easy conversion of metanet style referencing:

- B:// (ref. by txid)
- C:// (ref. by sha256 hash of content)
- D:// (ref. by dynamic state - linked to identity system)

To localhost paths or mainstream internet urls as well as toggling it all back and forth.

This will allow quick iteration of building a web application on the local machine but also rapid conversion to b://, c:// d:// etc. referencing styles for deployment to the blockchain.

Would just need a dictionary of {path : B:// reference} pairs for example to be swapped back and forth. Many other features in mind (possibly for another repository).

2. Downloading
~~~~~~~~~~~~~~
Should be able to specify content by:

- B:// (ref. by txid)
- C:// (ref. by sha256 hash of content)
- D:// (ref. by dynamic state - linked to identity system)
- Should work for content uploaded via BCAT

And have it be downloaded.

If it is a static html page then should optionally allow retreival of all referenced content to reconstruct the entire webpage on the local machine.

3. Identity protocols (Money Button, AIP etc.):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
I would like to add a very simple interface for interacting with
- AIP (https://github.com/BitcoinFiles/AUTHOR_IDENTITY_PROTOCOL)
- other ID protocols (e.g. Ryan X. Charles of Money Button has been working hard on this area)

4. "Linking / mapping / database functions":
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- MAP protocol for linking all kinds of different protocols together (powerful)
- (maybe) A.N.N.E. protocol by Mr Scatmann - https://medium.com/@bsmith12251960/a-n-n-e-the-alpha-testing-begins-545f809c6129

Installation
------------

Polyglot is distributed on `PyPI` as a universal wheel and is available on Linux/macOS
and Windows and supports Python 3.6+. ``pip`` >= 8.1.2 is required.

.. code-block:: bash

    $ pip install polyglot-bitcoin # pip3 if pip is Python 2 on your system.


Credits
-------
- CoinGeek / nChain / Bitcoin Association for putting on an amazing hackathon from which this project was born!

Donate
--------
- Made by $AustEcon (Handcash handle)
