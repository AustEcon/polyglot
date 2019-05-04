Polyglot: Bitcoin protocols made easy.
======================================

Powered by BitSV: https://github.com/AustEcon/bitsv

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



Examples
--------

- Code examples...


Features (Planned)
------------------

- B:// (for multimedia up to 100kb) - https://github.com/unwriter/B
- BCAT:// (for multimedia up to 310mb uncompressed, 110GB with nested gzip) - https://bcat.bico.media/
- Bottle (https://bottle.bitdb.network/) (native metanet) refs and mainstream urls for:

    - B:// (ref. by txid)
    - C:// (ref. by sha256 hash of content)
    - D:// (ref. by dynamic state - linked to identity system)
- AIP (https://github.com/BitcoinFiles/AUTHOR_IDENTITY_PROTOCOL)
- other ID protocols (e.g. Ryan X. Charles of Money Button has been working hard on this area)
- MAP protocol for linking all kinds of different protocols together (powerful)
- A.N.N.E. protocol by Mr Scatmann - https://medium.com/@bsmith12251960/a-n-n-e-the-alpha-testing-begins-545f809c6129

Installation
------------

Polyglot is distributed on `PyPI` as a universal wheel and is available on Linux/macOS
and Windows and supports Python 3.5+. ``pip`` >= 8.1.2 is required.

.. code-block:: bash

    $ pip install polyglot # pip3 if pip is Python 2 on your system.

Documentation
-------------
Docs are hosted by Github Pages and are automatically built and published by Travis after every successful commit to Polyglot's master branch.

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


Donate
--------
- Made by $AustEcon (Handcash handle)
