``StringGenerator.count()``
===========================

    Note this feature is experimental and not fully tested at this time. It will
    probably not work for more complicated patterns. 

``count()`` is a somewhat experimental feature that shows the potential unique
outcomes for a template pattern.

How many unique strings can we generate that are five characters long using
upper case ascii and digits:

.. code:: python

    In [18]: SG(r'[\u\d]{5}').count()
    Out[18]: 60466176

Because:

.. code:: python

    In [17]: len("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") ** 5
    Out[17]: 60466176

Another example:

.. code:: python

    In [116]: SG(r'[abc]{1:3}|[\d]{2}|[\l]{3}').count()
    Out[116]: 140747
    
    In [117]: (3**1 + 3**2 + 3**3) + 10**2 + 52**3
    Out[117]: 140747
    
This method calculates the potential unique results mathematically, but we can
count every instance "manually" as well. First count how many we could get:

.. code:: python

    In [19]: SG(r'[abc]{5}').count()
    Out[19]: 243

Produce every potential outcome:

.. code:: python

    In [28]: d = SG(r'[abc]{5}').render_list(243, unique=True)

    In [29]: len(d)
    Out[29]: 243

If we try to get 244 unique results, there will be an error:

.. code:: python

    In [22]: SG(r'[abc]{5}').render_list(244, unique=True)

    ---------------------------------------------------------------------------
    ...
    UniquenessError: couldn't satisfy uniqueness

It does not mathematically calculate and then raise an error. It tries to
produce the results and gives up after trying a certain number of times. You
don't want to use ``render_set()`` here because it doesn't check if the result
is not possible. It will never return. 

One important thing to remember is each specified character is counted,
even if it repeats another character in the sequence:

.. code:: python

    In [71]: SG("[xxxxxxxxxxxx]{10}").count()
    Out[71]: 61917364224

Limitations
-----------

``count()`` returns the size of the *generation sample space*: the number of
ways the template can be filled in. This equals the number of distinct strings
only when the assumptions below hold. Where they do not, ``count()`` overcounts
the distinct results (or, for the shuffle operator, raises).

Duplicate characters in a class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As shown above, every specified character is counted even if it repeats another
character in the class: the alphabet size is ``len(chars)``, not the number of
*distinct* characters.

.. code:: python

    In [1]: SG(r"[0-9\d]{2}").count()
    Out[1]: 400          # 20 ** 2, but only 100 distinct results

This mirrors rendering, where repeated characters are simply more likely to be
chosen, so the number reflects that weighting rather than the distinct results.

Overlapping alternation
~~~~~~~~~~~~~~~~~~~~~~~~~

For alternation (``|``), ``count()`` sums the size of each branch. That equals
the number of distinct results only when the branches cannot produce the same
string. Overlapping branches overcount:

.. code:: python

    In [2]: SG(r"[ab]|[ab]").count()
    Out[2]: 4           # 2 + 2, but only 2 distinct results

The shuffle operator
~~~~~~~~~~~~~~~~~~~~~~

The shuffle operator (``&``) permutes together the characters produced by all of
its operands. ``count()`` can answer this only when every operand is *fixed* --
it has exactly one possible value -- because then the characters being shuffled
are known:

.. code:: python

    In [3]: SG(r"1&abc").count()
    Out[3]: 24         # distinct arrangements of "1abc" = 4!

If any operand can vary, the characters being shuffled change with each random
draw, so there is no single count. In that case ``count()`` raises
``NotImplementedError`` rather than return a draw-dependent number:

.. code:: python

    In [4]: SG(r"[\d]{2}&[\d]{1}").count()
    ---------------------------------------------------------------------------
    NotImplementedError: count() is undefined for '&' over operands that are not fixed; ...

Source variables
~~~~~~~~~~~~~~~~~~

``count()`` cannot count a ``${somevariable}`` source, because the variable may
be a callable or list whose size is unknown. It raises ``NotImplementedError``.

