Debugging
=========

Call the dump() method on the class instance to get useful information:

-  Version of strgen module
-  Version of Python
-  The class name used for random methods
-  The parse tree
-  The output from one invocation of the render() method

The output looks something like the following:

.. code:: python

     In [106]: SG('[\w]{8}&xyz|(zzz&yyy)').dump()
     StringGenerator version: 0.4.0
     Python version: 3.8.7 (default, Feb  3 2021, 06:31:03)
     [Clang 12.0.0 (clang-1200.0.32.29)]
     Random method provider class: SystemRandom
     sequence:
     OR
     AND
          -1:8:_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
          xyz
     sequence:
          AND
               zzz
               yyy
     Out[106]: 'ybYxak7JRzN'
                                                                       

