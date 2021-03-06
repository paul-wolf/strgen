Usage
=====


Throughout we import the StringGenerator class aliased as SG:

.. code:: python

   from strgen import StringGenerator as SG

Generate a unique string using this syntax:

.. code:: python

   SG(<template>).render()

or to produce a list of unique strings:

::

   SG(<template>).render_set(<length>)

* template: a string that conforms to the StringGenerator pattern
  language as defined in this document

* length: the list of the result set. `render_set()` produces a unique set.
  `render_list()` can be used if uniqueness is not required.

Example:

.. code:: python

   SG('[\l\d]{4:18}&[\d]&[\p]').render()
   'Cde90uC{X6lWbOueT'

The ``template`` is a string that is a sequence of one or more of the
following:

-  *Literal text* (for example: ``UID``)
-  *Character class* (for example: ``[a-z\s]``)
-  *Group*, a combination of literals and character classes, possibly
   separated by operators and using parentheses where appropriate (for
   example: ``(UID[\d]{4}&[\w]{4})``)

A quantifier ``{x-y}`` should be provided normally just after a
character class to determine the size of the resulting string where x
and y are integers and y can be left away for a fixed length. With no
quantifier, a character class assumes a length of 1.

The range operator can be either ``-`` or ``:`` as in ``{10:20}`` or
``{10-20}``.

You can avoid escaping if you use raw strings, like ``r"[\u]{20}"``. You
need to accommodate f-strings by doubling the curly braces for
quantifiers. You can have raw f-strings:

.. code:: python
   
   x = "foo"
   SG(fr"[\d\u]{{1:20}}{x}").render()
   'E3ZG2foo'

If you want consistent results for testing, you can seed the generator:

.. code:: python

   SG("[\w]{20}", seed=1234).render_set(10000)


`seed` is any integer as per `random <https://docs.python.org/3/library/random.html>`__ if you would like to test with reproduceable results.

See :doc:`randomizer`


Literal: <any string>
---------------------

Any literal string.

Example:

::

   orderno

Special characters need to be escaped with backslash ``\``.

Character class: [<class specification>]
----------------------------------------

Much like in regular expressions, it uses strings of characters and
hyphen for defining a class of characters.

Example:

::

   [a-zA-Z0-9_]

The generator will randomly choose characters from the set of lower case
letters, digits and the underscore. The number of characters generated
will be exactly one in this case. For more, use a quantifier:

::

   [a-zA-Z0-9_]{8}

As a shortcut for commonly used character sets, a character set code may
be used. The following will render in exactly the same way:

::

   [\w]{8}

Character Set Codes
-------------------

-  ``\W``: whitespace + punctuation
-  ``\a``: ascii_letters
-  ``\c``: lowercase
-  ``\d``: digits
-  ``\h``: hexdigits
-  ``\l``: letters
-  ``\o``: octdigits
-  ``\p``: punctuation
-  ``\r``: printable
-  ``\s``: whitespace
-  ``\u``: uppercase 
-  ``\U``: uppercase 
-  ``\w``: ``_`` + letters + digits


Escape ``\u`` as ``\\u`` since this is the unicode prefix unless you use a raw string:

::

   r"[\u]{8}"
   
Or use the alias ``\U``.

Quantifier: {x:y}
-----------------

Where x is lower bound and y is upper bound. This construct must always
follow immediately a class with no intervening whitespace. It is
possible to write {:y} as a shorthand for {0:y} or {y} to indicate a
fixed length. ``{x-y}`` and ``{x:y}`` are synonymous. 

Example:

::

   [a-z]{0:8}

Generates a string from zero to 8 in length composed of lower case
alphabetic characters.

::

   [a-z]{4}|[0-9]{4}

Generates a string with either four lower case alphabetic characters or
a string of digits that is four in length.

Using a character class and no quantifier will result in a quantifier of
1. Thus:

::

     [abc]

will result always in either ``a``, ``b``, or ``c``.

Data Sources
------------

We provide the ``${varname}`` syntax to enable any value to be returned.
``varname`` must be provided as a keyword argument to the ``render()``,
``render_set()`` or ``render_list()`` methods. You can use a list, function
(callable) or generator. Here’s an example using a list:

.. code:: python

   SG('William of ${names}').render(names=['Orange', 'Normandy', 'Ockham'])

Or use a range converted to a list:

.. code:: python

   SG('You have ${chances} chances').render(chances=list(range(1000)))

Or using a function:

.. code:: python

   SG('William of ${names}').render(names=lambda: random.choice(['Orange', 'Normandy', 'Ockham']))

You can obviously pass any callable or generator that might, for
instance, randomly choose a value from a database, if that is what you
want.

Note there is a difference in handling between a callable and list type.
If you use a ``list``, StringGenerator picks an item from the list for
you, randomly. If you use a callable, StringGenerator takes and inserts
whatever is returned by the callable. The callable is required to do any
randomization if that is what the user wants. So, if you pass a function
that returns a list, the entire list will be inserted as a string.

As mentioned above, if you use an f-string, double your curly braces
for the data source name.

.. code:: python

   x = "William of "
   SG(f"{x}${{names}}").render(names=['Orange', 'Normandy', 'Ockham'])


Group: (<group specification>)
------------------------------

A group specification is a collection of literals, character classes or
other groups divided by the OR operator ``|`` or the shuffle operator
``&``.

OR Operator
-----------

The binary ``|`` operator can be used in a group to cause one of the
operands to be returned and the other to be ignored with an even chance.

Shuffle Operator
----------------

The binary ``&`` operator causes its operands to be combined and
shuffled. This addresses the use case for many password requirements,
such as, “at least 6 characters where 2 or more are digits”. For
instance:

::

   [\l]{6:10}&[\d]{2}

If a literal or a group is an operand of the shuffle operator, it will
have its character sequence shuffled with the other operand.

::

   foo&bar

will produce strings like:

::

   orbfao

Concatenation and Operators
---------------------------

Classes, literals and groups in sequence are concatenated in the order
they occur. Use of the ``|`` or ``&`` operators always binds the
operands immediately to the left and right:

::

   [\d]{8}xxx&yyy

produces something like:

::

    00488926xyyxxy

In other words, the digits occur first in sequence as expected. This is
equivalent to this:

::

   [\d]{8}(xxx&yyy)

Special Characters, Escaping and Errors
---------------------------------------

There are fewer special characters than regular expressions:

::

   []{}()|&$\-

They can be used as literals by escaping with backslash. All other
characters are treated as literals. The hyphen is only special in a
character class, when it appears within square brackets.

One special case is the escape character itself, backslash ``\``. To escape
this, you will need at least two backslashes. So, three
altogether: one for Python’s string interpretation and one for
StringGenerator’s escaping. If for some exotic reason you want two
literal backslashes in a row, you need a total of eight backslashes. The
foregoing presupposes the template is a string in a file. If you are
using the template in a shell command line or shell script, you’ll need
to make any changes required by your specific shell.

The template parser tries to raise exceptions when syntax errors are
made, but not every error will be caught, like having space between a
class and quantifier.

Spaces
------

Do not use any spaces in the template unless you intend to use them as
characters in the output:

::

   >>> SG('(zzz & yyy)').render()
   u'zzyz y y'

Character Classes and Quantifiers
---------------------------------

Use a colon in the curly braces to indicate a range. There are sensible
defaults:

::

   [\w]       # randomly choose a single word character
   [\w]{0:8}  # generate word characters from 0-8 in length 
   [\w]{:8}   # a synonym for the above
   [\w]{8}    # generate word characters of exactly 8 in length
   [a-z0-9]   # generate a-z and digits, just one as there is no quantifier
   [a-z0-9_!@]  # you can combine ranges with individual characters

As of version 0.1.7, quantifier ranges can alternatively be specified
with a hyphen:

::

   [\w]{4-8}

Here’s an example of generating a syntactically valid but, hopefully,
spurious email address:

::

   [\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)

The first name will be exactly 10 lower case characters; the last name
will be 5-10 characters of lower case letters, each separated by either
a dot or underscore. The domain name without domain class will be 3 - 12
lower case characters and the domain type will be one of
‘.com’,‘.net’,‘.org’.

The following will produce strings that tend to have more letters,
because the set of letters (52) is larger than the set of digits (10):

::

   [\l\d]

Using multiple character set codes repeatedly will increase the
probability of a character from that set occuring in the result string:

::

   [\l\d\d\d\d]

This will provide a string that is three times more likely to contain a
digit than the previous example.

Uniqueness
----------

``render_list()``  and ``render_set()`` both produce unqiue sequences of
strings. In general, you should use ``render_set()`` as it's much faster. See :doc:`render_set`.

When using the ``unique=True`` flag in the ``render_list()`` method,
it’s possible the generator cannot possibly produce the required number
of unique strings. For instance:

::

    SG("[0-1]").render_list(100, unique=True)

This will generate an exception but not before attempting to generate
the strings.

The number of times the generator needs to render new strings to satisfy
the list length and uniqueness is not determined at parse time. The
maximum number of times it will try is by default n x 10 where n is the
requested length of the list. Therefore, taking the above example, the
generator will attempt to generate the unique list of 0’s and 1’s 100 x
10 = 1000 times before giving up.
