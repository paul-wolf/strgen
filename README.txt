strgen
======

|Python package|

Generate test data, unique ids, passwords, vouchers or other randomized
textual data very quickly using a template language. The template
language is superficially similar to regular expressions but instead of
defining how to match or capture strings, it defines how to generate
randomized strings. A very simple invocation to produce a random string
with word characters and digits of 10 characters length:

.. code:: python

   >>> from strgen import StringGenerator as SG
   >>> SG("[\d\w]{10}").render()
   'sj5ic8vebF'

`Full documentation <https://strgen.readthedocs.io>`__

The purpose of this module is to save the Python developer from having
to write verbose code around the same pattern every time to generate
passwords, keys, tokens, test data, etc. of this sort:

.. code:: python

   my_secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(30))

that is:

1. Hard to read even at this simplistic level.

2. Hard to safely change quickly. Even modest additions to the
   requirements need unreasonably verbose solutions.

3. Doesn’t use safe encryption standards.

4. Doesn’t provide the implied minimal guarantees of character
   occurance.

5. Hard to track back to requirements (“must be between x and y in
   length and have characters from sets Q, R and S”).

The template uses short forms similar to those of regular expressions.
An example template for generating a strong password:

::

    [\w\p\d]{20}

will generate something like the following:

::

    P{:45Ec5$3)2!I68x`{6

Guarantee at least two “special” characters in a string:

::

    [\w\p]{10}&[\p]{2}

You can also generate useful test data, like fake emails with plenty of
variation:

::

    [\c]{10}.[\c]{5:10}@[\c]{3:12}.(com|net|org)

Requirements
------------

From version 0.4.0, support for 2.x is dropped. If you still need
support for Python 2, use version 0.3.4.

There are no dependencies beyond the Python Standard Library.

Installation
------------

Install as standard for Python packages from PyPi:

.. code:: shell

   pip install StringGenerator

License
-------

Released under the BSD license.

Acknowledgements
----------------

Thanks to Robert LeBlanc who caught some important errors in escaping
special characters. Thanks to Andreas Motl for the progress counter.

Original Author: paul.wolf@yewleaf.com

.. |Python package| image:: https://github.com/paul-wolf/strgen/actions/workflows/main.yml/badge.svg
   :target: https://github.com/paul-wolf/strgen/actions/workflows/main.yml
