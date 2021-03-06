Seeding and Custom Randomization
================================

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

You can also provide your own Random class. The only requirement is that it has three methods:

* ``choice()``
* ``randint()``
* ``shuffle()``

With the same arguments and return types as ``Random`` and ``SystemRandom``.

See documentation for the `Python Standard Library random package <https://docs.python.org/3/library/random.html>`__

