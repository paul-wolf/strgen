Debugging
=========

Call the dump() method on the class instance to get useful information:

-  Version of strgen module
-  Version of Python
-  The class name used for random methods
-  The parse tree
-  The output from one invocation of the render() method

The output looks something like the following:

::

   >>> SG('[\w]{8}&xyz|(zzz&yyy)').dump()
   StringGenerator version: 1.1.2
   Python version: 2.7.3 |EPD_free 7.3-2 (32-bit)| (default, Apr 12 2012, 11:28:34)
   [GCC 4.0.1 (Apple Inc. build 5493)]
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
   u'zMXGPwyxE9a'
                                                                       

