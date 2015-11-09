
import timeit
r = 1000


case1 = timeit.timeit('sg.render()', setup='from strgen import StringGenerator as SG;sg=SG("[\d]{100}")', number=r)
print("StringGenerator: %s seconds" % round(case1, 2))
case2 = timeit.timeit('["".join(choice(string.digits) for i in xrange(100))]',
                      setup='import string;import random;choice = random.SystemRandom().choice;', number=r)
print("Standard method: %s seconds" % round(case2, 2))
print("Standard method - StringGenerator: %s (%s%%)" %
      (str((case1 - case2)), str(round(100 * (case1 - case2) / case1, 2))))


case1 = timeit.timeit(
    'sg.render()',
    setup='from strgen import StringGenerator as SG;sg=SG("[\l]{10}&[\d]{2}")',
    number=r)
print("StringGenerator: %s seconds" % round(case1, 2))
case2 = timeit.timeit(
    'shuffle(["".join(choice(string.letters) for i in xrange(10))]+["".join(choice(string.digits) for i in xrange(2))])',
    setup='import string;import random;choice = random.SystemRandom().choice;shuffle = random.SystemRandom().shuffle',
    number=r)
print("Standard method (complex): %s seconds" % round(case2, 2))
print("Standard method - StringGenerator (complex): %s (%s%%)" %
      (str((case1 - case2)), str(round(100 * (case1 - case2) / case1, 2))))


from strgen import StringGenerator as SGPIP
import time
import imp
strgen = imp.load_source('strgen', 'strgen/__init__.py')

sg1 = strgen.StringGenerator('[\d]{100}')
sg2 = SGPIP('[\d]{100}')

s = time.time()
for i in xrange(10000):
    sg1.render()
c1 = time.time() - s

print("StringGenerator: %s seconds" % round(c1, 2))

s = time.time()
for i in xrange(10000):
    sg2.render()
c2 = time.time() - s

print("StringGenerator PIP: %s seconds" % round(c2, 2))


"""
from strgen import StringGenerator as SG
import dis
SG('[\d]')
dis.dis(SG.render)
"""
