==============
ixc-imagetools
==============

Doing cool things to images since 2016.

3rd-party C libraries
=====================
You need to install lcms (once per machine) for color management, before installing pillow.

$ brew install lcms

or

$ sudo apt-get install liblcms2-dev

To install

    pip install imagetools

If you still get a Color Management related error, pip uninstall pillow, then pip install pillow.

Includes:
=========

Zoom tiles generator
--------------------

Converter to sRGB
-----------------

To come:
========

Color extraction, face recognition, etc.

