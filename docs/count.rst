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

``count()`` will not know how to produce a result if you use a source variable
that could be a callable or list. That's when using the ``${somevariable}``
syntax.

It will very specifically not work correct if you use the shuffle operator ``&``
on a complex template expression. 

