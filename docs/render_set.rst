`render_set()` vs. `render_list()`
==================================

`render_set(<set_size>)` was introduced in StringGenerator 0.4.2. It is an alternative to `render_list()`. 

`render_list()` takes an argument for a progress callback function and can
generate a unique list if `unique=True`. It also throws an exception
if you provide a pattern and result size that are not compatible, like: 

.. code:: python

    SG("[123456789]{3}").render_list(800, unique=True)

The maximum number of unique results for this pattern is 729. An exception will
be raised:

::

    UniquenessError: couldn't satisfy uniqueness

In contrast, `render_set()` returns a `set` so it does not need a `unique=True`
parameter. It is optimised to be fast and therefore does not support either a
progress callback nor will it check if the request is feasible. 

But it's much faster than `render_list(count, unique=True)`

On a reasonably fast host, you can generate 100,000 unique 20 character
strings in under five seconds:

.. code:: python

    In [5]: %time tokens = SG("[\w]{20}").render_set(100000)
    CPU times: user 3.84 s, sys: 598 ms, total: 4.44 s
    Wall time: 4.44 s


`render_list(100000, unique=True)` would accomplish the same thing but take well
over 10x as long. 

The `seed` parameter has the same effect with `render_set()`:

.. code:: python

    In [23]: SG(r"[\u\d]{46}", seed=100).render_set(10)
    Out[23]:
    {'1A2SM257I4JNSYABZHPJP4L0TS7YYY4H9IC6DB61YYOBHE',
    '6SKXTOZ1CARF8GR148R9C5TLFF5N7FVJZ6CZV0L1PF2XAS',
    '9DP6SV7V8X4ZDGT1QP165QJDUKDRHDOT7NWV3AH4M7HNCY',
    'GZJ48C2KD4DMPKGCINFHQEZC8142V37MQ0JN0ERZQGMODY',
    'H2BN7K4C82WAF5D1YJM1LNRQNSZZQVBRP7LD0FWHK4XN7P',
    'HTIHODZ31WFEC20BJ4GFSG9JI9JKWYG5UH4SOWOCAO6H9F',
    'I4D4W64N5D6QB77GLCO3AHOXUHTGTT2MUFKVJM1FFUNURJ',
    'J33LZW16H8HF3QDNVOTNLJMWX0NZ39RYKHLAZJKMKBP2YI',
    'RARTCB9SOZAFOTBFWU2CLFBW9JKAAU6ZLYY2MNK9RE3I16',
    'ZB3VCQ5DEWCQ3S8ZXUKILV5Z0P5G7NLEPFBR4OV0CR4WVE'}

    In [24]: SG(r"[\u\d]{46}", seed=100).render_set(10)
    Out[24]:
    {'1A2SM257I4JNSYABZHPJP4L0TS7YYY4H9IC6DB61YYOBHE',
    '6SKXTOZ1CARF8GR148R9C5TLFF5N7FVJZ6CZV0L1PF2XAS',
    '9DP6SV7V8X4ZDGT1QP165QJDUKDRHDOT7NWV3AH4M7HNCY',
    'GZJ48C2KD4DMPKGCINFHQEZC8142V37MQ0JN0ERZQGMODY',
    'H2BN7K4C82WAF5D1YJM1LNRQNSZZQVBRP7LD0FWHK4XN7P',
    'HTIHODZ31WFEC20BJ4GFSG9JI9JKWYG5UH4SOWOCAO6H9F',
    'I4D4W64N5D6QB77GLCO3AHOXUHTGTT2MUFKVJM1FFUNURJ',
    'J33LZW16H8HF3QDNVOTNLJMWX0NZ39RYKHLAZJKMKBP2YI',
    'RARTCB9SOZAFOTBFWU2CLFBW9JKAAU6ZLYY2MNK9RE3I16',
    'ZB3VCQ5DEWCQ3S8ZXUKILV5Z0P5G7NLEPFBR4OV0CR4WVE'}