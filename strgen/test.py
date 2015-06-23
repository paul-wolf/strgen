# -*- coding: utf-8 -*-
import unittest
from strgen import StringGenerator

class TestStringGenerator(unittest.TestCase):

    def test_string_generator(self):
        test_list = [
            u"[a-z][\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)",
            u"[a-z\d\d\d\d]{8}",
            u"[\l]{6:10}&[\d]{2}",
            u"([a-z]{4}|[0-9]{9})",
            u"[\d]&[\c]&[\w\p]{6}",
        ]

        for t in test_list:
            result = StringGenerator(t).render()
            print(u"%s == %s"%(t,result))
            self.assertTrue(not result == None)

    def test_unicode(self):
        test_list = [
            u'idzie wąż wąską dróżką',
            u'[ą-ż]{8}',
            u'\xe6\xbf\xe5, \xe9\xe5\xa9\xe5\xe5\xad\xe6\xaf\xe7\xe9\xba\xbc\xe6\xe6',
        ]

        for t in test_list:
            result = StringGenerator(t).render()
            print(u"%s == %s"%(t,result))
            self.assertTrue(not result == None)

    def test_list(self):
        test_list = [
            u"[a-z][\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)",
            u"[a-z\d\d\d\d]{8}",
            u"[\l]{6:10}&[\d]{2}",
            u"([a-z]{4}|[0-9]{9})",
            u"[\d]&[\c]&[\w\p]{6}",
        ]

        for t in test_list:
            result = StringGenerator(t).render_list(10)
            print(u"%s == %s"%(t,result))
            self.assertTrue(type(result)==list)
        

if __name__ == '__main__':
    unittest.main()
