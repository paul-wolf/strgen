Syntactical Details
===================

The grammar for strgen is quite tolerant. We try to produce something
unless there is confusion about the count of potential outcomes.

The shuffle operator `&` causes its operands to produce permutations
without replacement.

While the shuffle operator is most useful as a binary operator, it can
be used as a unary operator. These all do the same thing:

.. code:: python

    SG('123456789&').render()
    SG('&123456789').render()
    SG('&123456789&').render()

Likewise, the binary operator, `|`, no longer raises an exception if there is only one operand:

.. code:: python

    SG("1|")

as well as an extra operator:

.. code:: python

    SG("1|2|3|")


The associative properties should be observed. The following produces 2-character elements as output:

.. code:: python

    In [13]: SG("1|2|3[abc]").render_list(10)
    Out[13]: ['1a', '3c', '3c', '1c', '2a', '3c', '3b', '3a', '1b', '2b']

This produces either one of : `1, 2, 3, a, b, c`.

.. code:: python

    In [14]: SG("1|2|3|[abc]").render_list(10)
    Out[14]: ['1', '2', '1', 'a', 'a', '1', '2', '2', '1', '1']

and without square brackets:

.. code:: python

    In [138]: SG("1|2|3|abc").render_list(10)
    Out[138]: ['1', '2', '3', 'abc', '1', '1', '2', 'abc', 'abc', '1']
