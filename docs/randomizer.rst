Seeding and Custom Randomization
================================

Seeding
-------

If you want to test and produce consistent results, you can use the ``seed`` option:

.. code:: python

    In [79]: SG("[\w]{10}&[\d]{10}", seed=4318).render_list(10)
    Out[79]:
    ['42U1uqGt5qG0519J6562',
     'q5d68X3n66r5h81pdz59',
     '1u307GH7Ad9Xmd1Zg119',
     'I7R224u5efft78A6986h',
     '3TP43404okw7Q5R019l4',
     '0D3952i05QYe1C935y36',
     '219W9iw9924XYy368E4B',
     '5F74c59Sy947LNw28p86',
     'W3ocGxWw675166352862',
     '35A6G69rEjh4U58t9X5E']
    
    In [80]: SG("[\w]{10}&[\d]{10}", seed=4318).render_list(10)
    Out[80]:
    ['42U1uqGt5qG0519J6562',
     'q5d68X3n66r5h81pdz59',
     '1u307GH7Ad9Xmd1Zg119',
     'I7R224u5efft78A6986h',
     '3TP43404okw7Q5R019l4',
     '0D3952i05QYe1C935y36',
     '219W9iw9924XYy368E4B',
     '5F74c59Sy947LNw28p86',
     'W3ocGxWw675166352862',
     '35A6G69rEjh4U58t9X5E']

Notice these two lists are exactly the same. 

Normally, when the StringGenerator is initialised, it will try to use
``random.SystemRandom`` as the random method provider. It falls back gracefully
to ``random.Random`` if that is not available.

When you use the ``seed`` option, it will force use of ``random.Random`` and use
the provided seed value, which can be any integer. This will cause the results
to be the same each time you initialise the StringGenerator.

Fast, secure generation
------------------------

By default StringGenerator uses ``random.SystemRandom``, which is
cryptographically secure but reads from the operating system entropy pool on
every draw -- one syscall per random value. For large batches (for example
``render_set(1000000)``) that syscall overhead dominates.

``BufferedSecureRandom`` solves this. It draws the same ``os.urandom`` entropy
as ``SystemRandom`` -- each byte used once and never expanded by a userspace
PRNG -- but reads it in bulk so the syscall is amortized across many values. It
is therefore as secure as ``SystemRandom`` while being many times faster for
bulk generation. It is reachable without an extra import as
``StringGenerator.BufferedSecureRandom``:

.. code:: python

    from strgen import StringGenerator as SG

    sg = SG(r"[\w\p]{32}", randomizer=SG.BufferedSecureRandom())
    tokens = sg.render_set(50000)

Being entropy-based, it ignores any seed.

If you do not need cryptographic randomness at all (for example, generating
test data), seeding -- or passing a plain ``random.Random`` -- uses the much
faster Mersenne Twister. Choose based on your needs:

=================================  ==============  ========================
Randomizer                         Relative speed  Cryptographically secure
=================================  ==============  ========================
``seed=`` / ``random.Random``      fastest         no
``SG.BufferedSecureRandom()``      fast            yes
``random.SystemRandom`` (default)  slowest         yes
=================================  ==============  ========================

Custom Random Class
-------------------

You can also provide your own Random class. Currently we use these methods:

* ``choice()``
* ``choices()``
* ``randint()``
* ``shuffle()``

So, you'd need to provide at least these with the same arguments and
return types as ``Random`` and ``SystemRandom``.

See documentation for the `Python Standard Library random package <https://docs.python.org/3/library/random.html>`__

    BEWARE: you should provide all the methods of ```Random()``` in
    your custom class because we might change the implementation of
    StringGenerator to use different methods.  

    
