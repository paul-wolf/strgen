Recipes
=======


Produce Collisions
------------------

Quick check if two random sets might overlap:

.. code:: python

          In [121]: SG(r'[\u\d]{5}').render_set(10000) & SG(r'[\u\d]{5}').render_set(10000)
          Out[121]: {'PH8AX'}

In this case, we had a single overlap. Easy to make that more
overlapping by increasing set size with the same pattern:


.. code:: python
          
    In [59]: len(SG(r'[\u\d]{5}').render_set(100000) & SG(r'[\u\d]{5}').render_set(100000))
    Out[58]: 150

150 overlaps. 

Or make it very unlikely that an overlap will exist by making the
results more characters:

.. code:: python

          In [35]: len(SG(r'[\u\d]{50}').render_set(100000) & SG(r'[\u\d]{50}').render_set(100000))
          Out[35]: 0

It would be nice to know what the count of the sets of potential results are:

.. code:: python
          
          In [19]: SG(r'[\u\d]{5}').count()
          Out[19]: 60466176

          In [18]: SG(r'[\u\d]{50}').count()
          Out[18]: 653318623500070906096690267158057820537143710472954871543071966369497141477376

The set ``\u\d``: 

::

   ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789

is 36 characters, so ``36^5 = 60466176``, permutation with replacement. And likewise ``36^50 = a big number``. 

Coin Flip
---------

Flip a coin 10000 times and count heads and tails:

.. code:: python

   import collections
   In [64]: collections.Counter(SG("heads|tails").render_list(10000))
   Out[64]: Counter({'tails': 5046, 'heads': 4954})


Flip two coins and check how the combinations were distributed:

.. code:: python

   In [81]: collections.Counter(list(zip(SG("heads|tails").render_list(100), SG("heads|tails").render_list(100))))
   Out[81]:
   Counter({('heads', 'heads'): 20,
   ('tails', 'heads'): 21,
   ('heads', 'tails'): 25,
   ('tails', 'tails'): 34})

Roll two die 1000 times:

.. code:: python

   In [7]: d = list(zip(SG(r'[123456]').render_list(1000), SG(r'[123456]').render_list(1000)))

   In [8]: Counter(d)
   Out[8]:
   Counter({('2', '2'): 28,
            ('3', '1'): 28,
            ('4', '1'): 27,
            ('5', '2'): 32,
            ('1', '5'): 28,
            ('6', '2'): 42,
            ('4', '3'): 19,
            ('1', '4'): 40,
            ...

We counted where order matters, 36 potential outcomes. 

Pick a card from a deck
-----------------------

First setup some definitions:

.. code:: python

    SPADE = "♠"
    HEART = "♥"
    DIAMOND = "♦"
    CLUB = "♣"

    def is_face_card(s):
       return s[0] in "JQK"

    def is_black_suit(s):
       return s[-1] in (SPADE, CLUB)

    def is_red_suit(s):
       return s[-1] in (DIAMOND, HEART)
   

Now let's randomly pick a card 1000 times:

.. code:: python

   In [208]: d = SG(f"J|Q|K|A|2|3|4|5|6|7|8|9|10[{HEART}{SPADE}{DIAMOND}{CLUB}]").render_list(1000)

   collections.Counter([is_face_card(x) & is_black_suit(x) for x in d])

   In [209]: collections.Counter([is_face_card(x) & is_black_suit(x) for x in d])
   Out[209]: Counter({False: 887, True: 113})

We expect the probability of getting a black face card to be 11.5%:

.. code:: python

   In [210]: 113/1000
   Out[210]: 0.113

Close enough

Normal Distribution
-------------------

We expect the distribution of picking one of 0 - 9 digits to be normally distributed if we try 100 times over 1000 times. 

.. code:: python

   In [11]: import statistics

   In [12]: d = [statistics.mean([int(SG("0|1|2|3|4|5|6|7|8|9").render()) for _ in range(100)]) for _ in range(1000)]
      ...: nd = statistics.NormalDist.from_samples(d)
      ...: nd.stdev
   Out[12]: 0.29718859089567784

   In [13]: nd.mean
   Out[13]: 4.51675

4.5 is the mean for 0 - 9. 



