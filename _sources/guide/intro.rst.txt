.. _intro:

Intro
=====

Polyglot is designed to be a fast and simple way to interface with the myriad of growing protocols being build on bitcoin SV.

Polyglot Mission
----------------

Lower barriers to entry for novice programmers and make metanet FUN!

* So why python and why polyglot?

    - Python is one of the main languages taught at 1st year university level and is arguably the most used language in the scientific disciplines where programming is seen as an adjunct to their core business.
    - Python is also the language often taught to 1st, 2nd year CompSci / Software Engineering students to teach some basic principles of programming because the syntax is incredibly easy to understand and productivity is incredible.
    - Bitcoin is difficult enough for people to wrap their heads around and *truly* understand as it is. Python, an interpreted language, is the perfect medium through which people can learn by doing and experimenting; running lines of code in real time and seeing what happened.
    - Building webpages for 5 cents per megabyte is a huge breakthrough for ushering in a new wave of innovation on the metanet. Until now a cheap digital ocean cloud server at $5/month was your best bet - which isn't that bad - but then there's the steep learning curve of setting up an apache server and setting up your SFTP and SSH shells etc.
    - I want to make the process so easy that it is basically three lines of code... and you spend the rest of your time learning html, css (which can be mostly learned in one or two weekends) and then adding in some js.
    - Give the path to your files and simply upload to metanet! DONE!

* Is it just for uploading files?

    - No I have much bigger plans for this.
    - This library is designed to be the easiest way for pythonistas to interface with all of the various, growing bitcoin metanet protocols.

    Data Carriage:

    - B:// (for multimedia up to 100kb) - https://github.com/unwriter/B
    - BCAT:// (for multimedia up to 310mb uncompressed, 110GB with nested gzip) - https://bcat.bico.media/

    Endpoints:

    - bottle browser (https://bottle.bitdb.network/) (native metanet) browser and urls for mainstream browsers / 3rd party servers:

        - B:// (ref. by txid)
        - C:// (ref. by sha256 hash of content)
        - D:// (ref. by dynamic state - linked to identity system)

    Identity Systems:

    - AIP (https://github.com/BitcoinFiles/AUTHOR_IDENTITY_PROTOCOL)
    - other identity protocols (e.g. Ryan X. Charles of Money Button will be announcing one at CoinGeek)

    Other protocols

    - MAP protocol for linking all kinds of different protocols together (powerful)
    - A.N.N.E. protocol by Mr Scatmann - https://medium.com/@bsmith12251960/a-n-n-e-the-alpha-testing-begins-545f809c6129 (eagerly awaited)


* A PyQt5 GUI will accompany this library to lower barriers to entry even further to non-technical folk https://github.com/AustEcon/polyglotGUI

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


License
-------

Polyglot is licensed under terms of the `MIT License`_.

Credits
-------
- CoinGeek / nChain / Bitcoin Association for putting on an amazing hackathon from which this project was born!

Donate
--------
- Made by $AustEcon (Handcash handle)

.. _MIT License: https://en.wikipedia.org/wiki/MIT_License