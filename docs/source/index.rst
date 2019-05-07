Polyglot: Bitcoin protocols made easy.
======================================

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

This library is heavily inspired by ofek's library `bit <https://github.com/ofek/bit>`_
(`bitsv's <https://github.com/AustEcon/bitsv>`_ predecessor)

**Here are some examples:**

Polyglot extends bitsv with the **polyglot.Upload** class, which inherits all of the properties of
the **bitsv.PrivateKey** class such as checking balance, unspends, sending payments etc.


1. Upload an image < 100kb with b:// protocol (https://github.com/unwriter/B):

.. code-block:: python

    >>> import polyglot
    >>> uploader = polyglot.Upload('your private key goes here in WIF format')
    >>> file = "C:/Users/username/Pictures/Ludwig_von_Mises.jpg"
    >>> media_type = uploader.get_media_type_for_file_name(file)  # 'image/jpeg'
    >>> encoding = uploader.get_encoding_for_file_name(file)  # 'binary'
    >>> file_name = uploader.get_filename(file)
    >>>
    >>> uploader.b_send_from_file(file, media_type, encoding, file_name=file_name)

See image here: https://bico.media/252ea6d5a4a4bfc956518403f6e5aa2ced1c2590d1120cd75341e0233d1b06e3

This works for a wide range of media types.

In the next release, this will be done simply with:

.. code-block:: python

    >>> file = "C:/Users/username/Pictures/BSV_banner.jpg""
    >>> uploader.upload_b(file)


2. Upload large multimedia > 100kb with bcat:// protocol (https://bcat.bico.media/):

.. code-block:: python

    >>> file = "C:/Users/username/Pictures/BSV_banner.jpg""
    >>> file_name = uploader.get_filename(file)
    >>>
    >>> txids = uploader.bcat_parts_send_from_file(file)
    >>> txid = uploader.bcat_linker_send_from_txids(
                    txids=txids,
                    media_type=uploader.get_media_type_for_file_name(file),
                    encoding=uploader.get_encoding_for_file_name(file),
                    file_name=file
                    )

See image here: https://bico.media/be8b6a79e66934d3419265fbf3295d03e331a4c08098ae7f817a7592ffaedd2b

In the next release, this will be done simply with:

.. code-block:: python

    >>> uploader.upload_bcat(file)

3. Basic Utilities

Some basic utilities are included for working with utxo splitting and predicting the media type / handling of the file based on the filename.

Already shown:

.. code-block:: python

    >>> get_media_type_for_file_name(file) #--> media_type
    >>> get_encoding_for_file_name(file) #--> encoding,
    >>> get_filename(path) #--> file_name.ext)

But additionally:

.. code-block:: python

    >>> Upload.get_largest_utxo(self) #--> largest utxo (for splitting)
    >>> Upload.split_biggest_utxo(self) #--> splits utxo into 100000 satoshi amounts
    >>> Upload.filter_utxos_for_bcat(self) #-- > filters utxos with 0 conf or too low amount to handle a 100kb tx
    >>> get_file_ext(file) #--> .ext
    >>> calculate_txid(rawtx) #--> txid


Features (Planned)
------------------

Operational:
~~~~~~~~~~~~

- B:// (for multimedia up to 100kb) - https://github.com/unwriter/B
- BCAT:// (for multimedia up to 310mb uncompressed, 110GB with nested gzip) - https://bcat.bico.media/

Bottle (metanet native browser) related:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bottle (https://bottle.bitdb.network/) (native metanet) refs and mainstream urls for:

- B:// (ref. by txid)
- C:// (ref. by sha256 hash of content)
- D:// (ref. by dynamic state - linked to identity system)

Would like to make scripts for re-translating html document links to any of these three bitcoin resource links, so that one can quickly iterate building a web application on the local machine (and swap back and forth between local paths versus b://, c:// d:// etc. referencing style for deployment to the blockchain. (would just need a dictionary of {path : txid} pairs to be swapped back and forth. Many other features in mind (possibly for another repository).

Identity protocols (Money Button, AIP etc.):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
I would like to add a very simple interface for interacting with
- AIP (https://github.com/BitcoinFiles/AUTHOR_IDENTITY_PROTOCOL)
- other ID protocols (e.g. Ryan X. Charles of Money Button has been working hard on this area)

"Linking / mapping / database functions":
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- MAP protocol for linking all kinds of different protocols together (powerful)
- A.N.N.E. protocol by Mr Scatmann - https://medium.com/@bsmith12251960/a-n-n-e-the-alpha-testing-begins-545f809c6129

Installation
------------

Polyglot *will be* distributed on `PyPI` as a universal wheel and is available on Linux/macOS
and Windows and supports Python 3.5+. ``pip`` >= 8.1.2 is required.

.. code-block:: bash

    $ pip install polyglot # pip3 if pip is Python 2 on your system.

In the meantime - you can simply clone the repository and run:

.. code-block:: bash

    $ python setup.py install


User Guide
----------

This section will tell you a little about the project, show how to install it,
and will then walk you through how to use BitSV with many examples and explanations
of best practices.

.. toctree::
    :maxdepth: 2

    guide/intro

Credits
-------
- CoinGeek for putting on an amazing hackathon from which this project was born!

Donate
--------
- Made by $AustEcon (Handcash handle)
