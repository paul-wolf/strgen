# -*- coding: utf-8 -*-
import random
import collections
import statistics

from hypothesis import given
import hypothesis.strategies as st
from hypothesis import find, settings, Verbosity
from hypothesis.strategies import lists, integers

import unittest
from strgen import StringGenerator as SG

SPECIAL_CHARACTERS = "{}[]()|&$-\\"


def remove_special(s) -> str:
    for c in SPECIAL_CHARACTERS:
        s = s.replace(c, "")
    return s


class CustomBadRandomizer:
    pass


class CustomRandomizer(random.Random):
    def choice(self, s):
        return super().choice(s)

    def shuffle(self, s):
        return super().shuffle(s)

    def randint(self, a, b):
        return super().randint(a, b)


class TestSG(unittest.TestCase):
    @given(st.text(min_size=2, max_size=100), st.integers(min_value=10, max_value=1000))
    @settings(verbosity=Verbosity.verbose)
    def test_unicode_strings(self, s, i):
        s = remove_special(s)
        if s:
            p = f"[{s}]{{10}}"
            print(p)
            r = SG(p).render()
            # print(r)
            assert r

    @given(st.characters(blacklist_characters=SPECIAL_CHARACTERS), st.integers())
    @settings(verbosity=Verbosity.verbose)
    def test_single_characters(self, s, i):
        p = f"[{s}]{{10}}"
        r = SG(p).render()
        # print(r)
        assert r

    def test_string_generator(self):
        """Test various templates."""
        test_list = [
            r"[a-z][\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)",
            r"[\[\]\(\)\{\}\&\|\-\$_+=;'\"<>,.?:!#%^`~*@\\\]OC",
            r"[a-z\d\d\d\d]{8}",
            r"[\l]{6:10}&[\d]{2}",
            r"([a-z]{4}|[0-9]{9})",
            r"[\d]&[\c]&[\w\p]{6}",
        ]

        for t in test_list:
            result = SG(t).render()
            self.assertIsNotNone(result)

    def test_unicode(self):
        test_list = [
            r"idzie wąż wąską dróżką",
            r"༣ཁངཱུངྵ",
            r"ᚠᚳᛦᛰ",
            r"[ą-ż]{8}",
            r"\xe6\xbf\xe5, \xe9\xe5\xa9\xe5\xe5\xad\xe6\xaf\xe7\xe9\xba\xbc\xe6\xe6",  # noqa: E501
        ]

        for t in test_list:
            result = SG(t).render()
            # TODO: must be a better test than testing for None
            self.assertIsNotNone(result)

    def test_render_list(self):
        list_length = 10
        test_list = [
            r"[a-z][\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)",
            r"[a-z\d\d\d\d]{8}",
            r"[\l]{6:10}&[\d]{2}",
            r"[\l]{6-10}&[\d]{2}",  # support both hyphen and colon for ranges
            r"([a-z]{4}|[0-9]{9})",
            r"[\d]&[\c]&[\w\p]{6}",
            r"[\w\p]",
            r"[\w\p]{6}",
            r"[\w\p]{-6}" r"[\w\p]{:6}",
            r"[\w\p]{0:6}",
        ]

        for t in test_list:
            result = SG(t).render_list(list_length)
            self.assertTrue(isinstance(result, list))
            self.assertTrue(len(result) == list_length)

    def test_render_set(self):
        set_length = 100
        p = r"[a-z][\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)"
        result = SG(p).render_set(set_length)
        self.assertTrue(isinstance(result, set))
        self.assertTrue(len(result) == set_length)

    def test_list_progress(self):
        """Check if the progress indicator actually works"""

        list_length = 10

        progress_states = []

        def progress_callback(current, total):
            progress_state = "{current}/{total}".format(**locals())
            progress_states.append(progress_state)

        SG(r"[a-z\d\d\d\d]{8}").render_list(
            list_length, progress_callback=progress_callback
        )

        # Length of list of progress states should match length of
        # requested strings
        self.assertTrue(len(progress_states) == list_length)

        # Check the first and the last item for the sake of completeness
        self.assertEqual(progress_states[0], "1/10")
        self.assertEqual(progress_states[-1], "10/10")

    def test_syntax_exception(self):
        """Make sure syntax errors in template are caught."""
        test_list = [
            r"[a-z]{a}",  # not a valid quantifier
            r"[a-]",  # invalid class range
            r"[[1-9]",  # unescaped chars
            r"((foo)(bar)))",  # extra parens
            #  r"foo&",  # binary operator error
            #  r"|foo",  # binary operator error
            r"[\w]{10:}",  # cannot have open range in quantifier
        ]
        for t in test_list:
            # using 2.7 specific context manager here
            # so, test won't work on < 2.7 but everything else should do
            # with self.assertRaises(SG.SyntaxError) as context:
            #    SG(t).render()
            self.assertRaises(SG.SyntaxError, lambda: SG(t).render())

    def test_uniqueness_error(self):
        """Make sure we throw an exception if we can't generate list."""
        t = "[123]"
        self.assertRaises(
            SG.UniquenessError,
            lambda: SG(t).render_list(100, unique=True),
        )

    def test_escaping(self):
        test_list = [
            r"[\[\]]",
            r"\{\}",
            r"[\[\]\(\)\{\}\&\|\-\$_+=;'\"<>,.?:!#%^`~*@]{10}",
        ]

        for t in test_list:
            result = SG(t).render()
            self.assertIsNotNone(result)

    def test_literals(self):
        """Test various literals."""
        test_list = [r"hel-lo[\w]{8}", r"hello:[\w]{8}", r"-hello-[\w]{8}"]

        for t in test_list:
            result = SG(t).render()
            self.assertIsNotNone(result)

    def test_forward_slash(self):
        result = SG(r"[\\]").render()
        self.assertEqual(result, "\\")

    def test_capital_u(self):
        result = SG(r"[\U]{10}").render()
        assert len(result) == 10
        assert result.isupper()

    def test_source(self):

        # you can pass a function
        SG("blah${names}").render(names=lambda: random.choice(["1", "2", "3"]))

        # you can pass a generator
        SG("generator: ${names}").render(names=(lambda: (yield "somestring"))())

        # range to list
        SG("generator: ${names}").render(names=list(range(10)))

    def test_unseeded_randomizer(self):
        # provide a seed to get consistent results
        pattern = r"[\w]{10}&([\d]{10}|M3W9MF_lH3906I14O50)"

        sg = SG(pattern)
        s1 = sg.render()
        sg = SG(pattern)
        s2 = sg.render()
        assert s1 != s2

        sg = SG(pattern)
        list1 = sg.render_list(100)
        sg = SG(pattern)
        list2 = sg.render_list(100)
        assert collections.Counter(list1) != collections.Counter(list2)

    def test_seeded_randomizer(self):
        # provide a seed to get consistent results
        pattern = r"[\w]{10}&([\d]{10}|M3W9MF_lH3906I14O50)"

        for seed in [random.randint(1, 100000000) for _ in range(100)]:
            sg = SG(pattern, seed=seed)
            s1 = sg.render()
            sg = SG(pattern, seed=seed)
            s2 = sg.render()
            assert s1 == s2

            sg = SG(pattern, seed=seed)
            list1 = sg.render_list(100)
            sg = SG(pattern, seed=seed)
            list2 = sg.render_list(100)
            assert collections.Counter(list1) == collections.Counter(list2)

    def test_custom_bad_randomizer(self):
        pattern = r"[\w]{10}&([\d]{10}|M3W9MF_lH3906I14O50)"
        sg = SG(pattern, randomizer=CustomBadRandomizer())
        self.assertRaises(Exception, lambda: sg.render())

    def test_custom_randomizer(self):
        pattern = r"[\w]{10}&([\d]{10}|M3W9MF_lH3906I14O50)"
        sg = SG(pattern, randomizer=CustomRandomizer())
        assert len(sg.render())

    def test_dump(self):
        """make sure dump method works."""
        SG(r"[\w]{8}").dump()

    def test_str(self):
        str(SG(r"[\w]{8}"))

    def test_repr(self):
        repr(SG(r"[\w]{8}"))


    def test_counts(self):
        assert SG(r'1&abc').count() == len(SG(r'1&abc').render_set(24))
        assert SG(r'[\u\d]{2}|[abc]{3}', uaf=100).count() == len(SG(r'[\u\d]{2}|[abc]{3}', uaf=100).render_list(1323, unique=True))
        
    def test_probabilistic_or(self):
        d = SG("0|1|2|3|4|5|6|7|8|9").render_list(10000)
        d = [int(d) for d in d]
        # statistics.mean(d)
        # quantiles are not available in python 3.6, 3.7
        # q = statistics.quantiles(d, n=4)
        # # we expect: [2.0, 4.0, 7.0]
        # assert q[0] == 2.0
        # assert q[2] == 7.0
        # # the middle quantile can be 4.0 or 5.0
        # # because 4.5 is the mean
        # assert q[1] == 4.0 or q[1] == 5.0


        # Correct:
        # SG('1|2|3[abc]{1}'
        # ['1c', '2b', '1b', '2c', '2c', '3c', '3c', '2b', '1c', '1c']

        # NOT Correct:
        # SG('1|2|[abc]{1}'
        # ['1c', '2b', '1b', '2c', '2c', '3c', '3c', '2b', '1c', '1c']

if __name__ == "__main__":
    unittest.main()
