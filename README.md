strgen
======

Generate randomized strings of characters using a template.

This is a Python module that enables a user to generate test data,
unique ids, passwords, vouchers or other randomized data very quickly
using a template language. The template language is superficially
similar to regular expressions but instead of defining how to find or
capture strings, it defines how to generate randomized strings.

An example template for generating a very strong password:

     [\w\p\d]{20}

will generate something like the following: 

     P{:45Ec5$3)2!I68x`{6

Constructor
-----------

    StringGenerator(<template>)

Usage:

    StringGenerator(<template>).render()

or:

    StringGenerator(<template>).render_list(10,unique=True)

The latter produces a list of 10 strings that are unique within the list.

The `template` is a string that is a sequence of one or more of the following: 

* Literal text
* Character class
* Group

In more detail:

Literal: \<any string>
---------------------

Any literal string. 

Example:

    abc

Character class: [\<class specification>]
----------------------------------------

Much like in regular expressions, it uses strings of characters
and hyphen for defining a class of characters.

Example:

    [a-z0-9_]

Randomly choose characters from the set of lower case letters, digits and the underscore.

Character Set Codes
-------------------

* `\W`: whitespace + punctuation
* `\a`: ascii_letters
* `\c`: lowercase
* `\d`: digits
* `\h`: hexdigits
* `\l`: letters
* `\o`: octdigits
* `\p`: punctuation
* `\r`: printable
* `\s`: whitespace
* `\u`: uppercase
* `\w`: `_` + letters + digits


Quantifier: {x:y} 
----------------- 

Where x is lower bound and y is upper bound. This construct must
always follow immediately a class with no intervening
whitespace. It is possible to write {:y} as a shorthand for {0:y}
or {y} to indicate a fixed length.

Example: 

    [a-z]{0:8}

Generates a string from zero to 8 in length composed of lower case
alphabetic characters

    [a-z]{4}|[0-9]{9}

Generates a string with either four lower case alphbetic
characters or a string that is 9 digits in length.

Using a character class and no quantifier will result in a quantifier of 1. Thus:

      [abc]

will result always in either `a`, `b`, or `c`. 

Groups:  (\<group sepcification>)
--------------------------------

A group specification is a collection of literals, character
classes or other groups divided by the OR operator `|` or the
permutation operator `&`.

OR Operator
-----------

The binary `|` operator can be used in a group to cause one of the
operands to be returned and the other to be ignored with an even
chance.

Permutation Operator
--------------------

The binary `&` operator causes its operands to be combined and
permuted.  This addresses the use case for many password requirements,
such as, "at least 6 characters where 2 or more are digits". This can
be done so:

    [\l]{6:10}&[\d]{2}

If a literal or a group is an operand of the permutation operator,
it will have its string value permuted with the other operand.

    foo&bar

will produce strings like: 

    orbfao

Concatenation and Operators
---------------------------

Classes, literals and groups in sequence are concatenated in the order
they occur.  Use of the `|` or `&` operators always bind the operands
immediately to the left and right:

    [\d]{8}xxx&yyy

produces something like: 

     00488926xyyxxy

In otherwords, the digits occur first in sequence as expected. This is
equivalent to this:

    [\d]{8}(xxx&yyy)

Special Characters, Escaping and Errors
---------------------------------------

There are fewer special characters than regular expressions: 

    [](){}|&-

They can be used as literals by escaping with backslash. All other
characters are treated as literals.  The hyphen is only special in a
character class, when it appears within square brackets. The parser
may do unexpected things if errors are made, usually in favour of
laxness, passing over errors silently, like forgetting to close a
group or class with closing brackets, having space between a class and
quantifier.  But the result in the case of such an error is not likely
to be what is expected or wished for, and the quality of the
randomization will likely be impaired.

Character Classes and Quantifiers
---------------------------------

Use a colon in the curly braces to indicate a range. There are
sensible defaults:

    [\w]       # randomly choose a single word character
    [\w]{0:8}  # generate word characters from 0-8 length 
    [\w]{:8}   # a synonym for the above
    [\w]{8}    # generate word characters of exactly 8 in length
    [a-z0-9]   # generate a-z and digits, just one as there is no quantifier
    [a-z0-9_!@]  # you can combine ranges with individual characters

Here's an example of generating a syntactically valid but, hopefully,
spurious email address:

    [\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)

The first name will be from 1 - 10 lower case characters; the last name
will be 5-10 characters of lower case letters, each separated by
either a dot or underscore.  The domain name without domain class will
be 3 - 12 lower case characters and the domain type will be one of
'.com','.net','.org'.

Using multiple character set codes repeatedly will increase the
probability of a character from that set occuring in the result
string:

    [a-z\d\d\d\d]

This will provide a string that is three times more likely to contain
a digit than if this were used:

    [a-z\d]

Uniqueness 
---------- 

When using the `unique=True` flag, it's possible the generator cannot
possibly produce the required number of unique strings. For instance:

	 StringGenerator("[0-1]").render_list(100,unique=True)

This will generate an exception, but not before attempting to generate
the strings.

The number of times the generator needs to render new strings to
satisfy the list length and uniqueness is not determined at parse
time. However, the maximum number of times it will try is by default
n*10 where n is the requested length of the list. Therefore, taking
the above example, the generator will attempt to generate the unique
list of 0's and 1's 100*10 = 1000 times.

Unicode
-------

Unicode is supported for both the template and output. 

Character Sets and Locale 
------------------------- 

Character sets used for backslashed character codes are exactly the
Python character sets from the string package. Some of these are
dependent on the locale settings. 

Randomness Methods
------------------

The generator tries to use `random.SystemRandom()` for `randint`,
`shuffle`, etc. It falls back to `random.randint` and associated
methods if it can't use `SystemRandom`.

Design Goals
------------

The module is designed with the following goals in mind:

* Provide an abstract template language that does not depend on a
  specific language implementation.

* For Python, reduce dependencies on other packages.

* Keep syntax as simple as possible while being pragmatic.

* Provide an implementation design with associated behaviour that
  strikes the right balance of easy-of-implementation with
  ease-of-use.

* Superficially similar to regular expressions to enable
  developers to quickly pickup the template syntax.


License
-------
Released under the BSD license. 


Original Author: paul.wolf@yewleaf.com

