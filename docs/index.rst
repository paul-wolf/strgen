StringGenerator
===============

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

Install:

::

   pip install StringGenerator

The current package requires Python 3.6 or higher. Use version 0.3.4 or 
earlier if you want to use Python 2.7 or an earlier P3 version. 

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
An example template for generating the same secret key as above:

.. code:: python

   SG(r"[\w\p]{30}").render()

will generate something like the following:

::

   "\\/]U.`I$9E[#!'HTT;MSH].-Y};C|Y"

Changing the character specification is a matter of adding two characters.

Guarantee at least two “special” characters in a string:

::

    [\w\p]{10}&[\p]{2}

You can also generate useful test data, like fake emails with plenty of
variation:

::

    [\c]{10}.[\c]{5:10}@[\c]{3:12}.(com|net|org)



Testing
-------

For running the unit tests, you might want to try:

::

   pip install pytest
   pytest

License
-------

Released under the BSD license.

Acknowledgements
----------------

Thanks to Robert LeBlanc who caught some important errors in escaping
special characters. Thanks to Andreas Motl for the progress counter.

Original Author: paul.wolf@yewleaf.com


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   randomizer
   progress
   debugging
   rationale

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
