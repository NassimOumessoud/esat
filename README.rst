Embryonic Structural Analysis Tool
==================================

Installing
----------

.. code-block:: shell

    $ git clone https://github.com/NassimOumessoud/esat.git
    $ cd esat
    $ pip install -r requirements.txt OR py setup.py install

Usage
-----

.. code-block:: shell

    $ py -m esat --help
    usage: Esat [-h] [-o OUTFOLDER] [embryos ...]

    positional arguments:
      embryos               Folders containing embryo images
    
    optional arguments:
      -h, --help            show this help message and exit
      -o OUTFOLDER, --outfolder OUTFOLDER

Improvements
------------
- peak valley detection
- web-app
- Folder selection error handling
- icon
- deep learning?
- extra- and interpolation to create 3d images
