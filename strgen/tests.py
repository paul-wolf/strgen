# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import random

import unittest
from __init__ import StringGenerator

class TestStringGenerator(unittest.TestCase):

    def test_string_generator(self):
        '''Test various templates.'''
        test_list = [
            u"[a-z][\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)",
            u"[\[\]\(\)\{\}\&\|\-\$_+=;\'\"<>,.?:!#%^`~*@\\\]OC",
            u"[a-z\d\d\d\d]{8}",
            u"[\l]{6:10}&[\d]{2}",
            u"([a-z]{4}|[0-9]{9})",
            u"[\d]&[\c]&[\w\p]{6}",
        ]

        for t in test_list:
            result = StringGenerator(t).render()
            print(u"{0} == {1}".format(t, result))
            self.assertTrue(not result is None)

    def test_unicode(self):
        test_list = [
            u'idzie wąż wąską dróżką',
            u'༣ཁངཱུངྵ',
            u'ᚠᚳᛦᛰ',
            u'[ą-ż]{8}',
            u'\xe6\xbf\xe5, \xe9\xe5\xa9\xe5\xe5\xad\xe6\xaf\xe7\xe9\xba\xbc\xe6\xe6',
        ]

        for t in test_list:
            result = StringGenerator(t).render()
            print(u"{0} == {1}".format(t, result))
            # TODO: must be a better test than testing for None
            self.assertTrue(not result is None)

    def test_list(self):
        list_length = 10
        test_list = [
            u"[a-z][\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)",
            u"[a-z\d\d\d\d]{8}",
            u"[\l]{6:10}&[\d]{2}",
            u"[\l]{6-10}&[\d]{2}",  # support both hyphen and colon for ranges
            u"([a-z]{4}|[0-9]{9})",
            u"[\d]&[\c]&[\w\p]{6}",
            u"[\w\p]",
            u"[\w\p]{6}",
            u"[\w\p]{-6},"
            u"[\w\p]{:6}",
            u"[\w\p]{0:6}",
        ]

        for t in test_list:
            result = StringGenerator(t).render_list(list_length)
            print("Pattern [{0}] list length == {1}".format(t, len(result)))
            self.assertTrue(isinstance(result, list) and len(result) == list_length)

    def test_list_progress(self):
        """Check if the progress indicator actually works"""

        list_length = 10

        progress_states = []
        def progress_callback(current, total):
            progress_state = u'{current}/{total}'.format(**locals())
            progress_states.append(progress_state)

        StringGenerator(u"[a-z\d\d\d\d]{8}").render_list(list_length, progress_callback=progress_callback)

        # Length of list of progress states should match length of requested strings
        self.assertTrue(len(progress_states) == list_length)

        # Check the first and the last item for the sake of completeness
        self.assertEqual(progress_states[0], u'1/10')
        self.assertEqual(progress_states[-1], u'10/10')

    def test_syntax_exception(self):
        '''Make sure syntax errors in template are caught.'''
        test_list = [
            u"[a-z]{a}",  # not a valid quantifier
            u"[a-]",  # invalid class range
            u"[[1-9]",  # unescaped chars
            u"((foo)(bar)))",  # extra parens
            u"foo&",  # binary operator error
            u"|foo",  # binary operator error
            u"[\w]{10:}",  # cannot have open range in quantifier
        ]
        for t in test_list:
            # using 2.7 specific context manager here
            # so, test won't work on < 2.7 but everything else should do
            #with self.assertRaises(StringGenerator.SyntaxError) as context:
            #    StringGenerator(t).render()
            self.assertRaises(StringGenerator.SyntaxError, lambda: StringGenerator(t).render())
            
            #print("Exception {0}: {1}".format(t, context.exception))

    def test_uniqueness_error(self):
        '''Make sure we throw an exception if we can't generate list.'''
        t = u'[123]'
        self.assertRaises(StringGenerator.UniquenessError, lambda: StringGenerator(t).render_list(100, unique=True))
        
    def test_escaping(self):
        test_list = [
            "[\[\]]",
            "\{\}",
            "[\[\]\(\)\{\}\&\|\-\$_+=;\'\"<>,.?:!#%^`~*@]{10}",
        ]

        for t in test_list:
            result = StringGenerator(t).render()
            self.assertTrue(not result is None)

    def test_literals(self):
        '''Test various literals.'''
        test_list = [
            u"hel-lo[\w]{8}",
            u"hello:[\w]{8}",
            "-hello-[\w]{8}",
        ]

        for t in test_list:
            result = StringGenerator(t).render()
            self.assertTrue(not result is None)

    def test_forward_slash(self):
        result = StringGenerator(r"[\\]").render()
        self.assertEqual(result, "\\")
        
    def test_source(self):
        
        from countries import countries
        print(StringGenerator('blah${countries}').render(countries=countries))
        print(StringGenerator('blah${countries}').render_list(10, countries=countries))
        
        # you can pass a function 
        print(StringGenerator('blah${names}').render(names=lambda: random.choice(['1', '2', '3'])))
        
        # you can pass a generator
        print(StringGenerator('generator: ${names}').render(names=(lambda: (yield 'somestring'))()))

        # range to list
        print(StringGenerator('generator: ${names}').render(names=list(range(10))))
            
    def test_dump(self):
        """make sure dump method works."""
        StringGenerator("[\w]{8}").dump()


                
if __name__ == '__main__':
    unittest.main()
