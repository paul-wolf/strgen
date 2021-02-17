Rationale and Design Goals
==========================

In Python, the need to generate random strings comes up frequently and
is accomplished usually (though not always) via something like the
following code snippet:

::

     import random
     import string
     mykey = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))

This generates a string that is 10 characters made of uppercase letters
and digits. Unfortunately, this solution becomes cumbersome when
real-world requirements are added. Take for example, the typical
requirement to generate a password: “a password shall have 6 - 20
characters of which at least one must be a digit and at least one must
be a special character”. The above solution then becomes much more
complicated and changing the requirements is an error-prone and
unnecessarily complex task.

The equivalent using the strgen package:

::

   from strgen import StringGenerator as SG
   SG('[\u\d]{10}').render()

``strgen`` is far more compact, flexible and feature-rich than using the
standard solution:

-  It tries to use a better entropy mechanism and falls back gracefully
   if this is not available on the host OS.

-  The user can easily modify the specification (template) with minimal
   effort without the fear of introducing hard-to-test code paths.

-  It covers a broader set of use cases: unique ids, persistent unique
   filenames, test data, etc.

-  The template syntax is easy to learn for anyone familiar with regular
   expressions while being much simpler.

-  It supports unicode.

-  It works on Python 2.6, 2.7 and 3.x.

-  It proposes a standard way of expressing common requirements, like “a
   password shall have 6 - 20 characters of which at least one must be a
   digit and at least one must be a special character”:

   ::

         [\l\d]{4:18}&[\d]&[\p]

This package is designed with the following goals in mind:

-  Provide an abstract template language that does not depend on a
   specific implementation language.

-  Reduce dependencies on other packages.

-  Keep syntax as simple as possible while being useful.

-  Provide an implementation design with associated behaviour that
   strikes the right balance between ease-of-implementation and
   ease-of-use.

-  Superficially similar to regular expressions to enable developers to
   quickly pick up the template syntax.

-  Support non-ASCII languages (unicode).
