# -*- coding: utf-8 -*-
import random
import collections

from hypothesis import given
import hypothesis.strategies as st
from hypothesis import find, settings, Verbosity
from hypothesis.strategies import lists, integers

import unittest
from strgen import StringGenerator

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


class TestStringGenerator(unittest.TestCase):
    @given(st.text(min_size=2, max_size=100), st.integers(min_value=10, max_value=1000))
    @settings(verbosity=Verbosity.verbose)
    def test_unicode_strings(self, s, i):
        s = remove_special(s)
        if s:
            p = f"[{s}]{{10}}"
            print(p)
            r = StringGenerator(p).render()
            # print(r)
            assert r

    @given(st.characters(blacklist_characters=SPECIAL_CHARACTERS), st.integers())
    @settings(verbosity=Verbosity.verbose)
    def test_single_characters(self, s, i):
        p = f"[{s}]{{10}}"
        r = StringGenerator(p).render()
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
            result = StringGenerator(t).render()
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
            result = StringGenerator(t).render()
            # TODO: must be a better test than testing for None
            self.assertIsNotNone(result)

    def test_list(self):
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
            result = StringGenerator(t).render_list(list_length)
            self.assertTrue(isinstance(result, list))
            self.assertTrue(len(result) == list_length)

    def test_list_progress(self):
        """Check if the progress indicator actually works"""

        list_length = 10

        progress_states = []

        def progress_callback(current, total):
            progress_state = "{current}/{total}".format(**locals())
            progress_states.append(progress_state)

        StringGenerator(r"[a-z\d\d\d\d]{8}").render_list(
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
            r"foo&",  # binary operator error
            r"|foo",  # binary operator error
            r"[\w]{10:}",  # cannot have open range in quantifier
        ]
        for t in test_list:
            # using 2.7 specific context manager here
            # so, test won't work on < 2.7 but everything else should do
            # with self.assertRaises(StringGenerator.SyntaxError) as context:
            #    StringGenerator(t).render()
            self.assertRaises(
                StringGenerator.SyntaxError, lambda: StringGenerator(t).render()
            )

    def test_uniqueness_error(self):
        """Make sure we throw an exception if we can't generate list."""
        t = "[123]"
        self.assertRaises(
            StringGenerator.UniquenessError,
            lambda: StringGenerator(t).render_list(100, unique=True),
        )

    def test_escaping(self):
        test_list = [
            r"[\[\]]",
            r"\{\}",
            r"[\[\]\(\)\{\}\&\|\-\$_+=;'\"<>,.?:!#%^`~*@]{10}",
        ]

        for t in test_list:
            result = StringGenerator(t).render()
            self.assertIsNotNone(result)

    def test_literals(self):
        """Test various literals."""
        test_list = [r"hel-lo[\w]{8}", r"hello:[\w]{8}", r"-hello-[\w]{8}"]

        for t in test_list:
            result = StringGenerator(t).render()
            self.assertIsNotNone(result)

    def test_forward_slash(self):
        result = StringGenerator(r"[\\]").render()
        self.assertEqual(result, "\\")

    def test_capital_u(self):
        result = StringGenerator(r"[\U]{10}").render()
        assert len(result) == 10
        assert result.isupper()

    def test_source(self):

        # you can pass a function
        StringGenerator("blah${names}").render(
            names=lambda: random.choice(["1", "2", "3"])
        )

        # you can pass a generator
        StringGenerator("generator: ${names}").render(
            names=(lambda: (yield "somestring"))()
        )

        # range to list
        StringGenerator("generator: ${names}").render(names=list(range(10)))

    def test_unseeded_randomizer(self):
        # provide a seed to get consistent results
        pattern = r"[\w]{10}&([\d]{10}|M3W9MF_lH3906I14O50)"

        sg = StringGenerator(pattern)
        s1 = sg.render()
        sg = StringGenerator(pattern)
        s2 = sg.render()
        assert s1 != s2

        sg = StringGenerator(pattern)
        list1 = sg.render_list(100)
        sg = StringGenerator(pattern)
        list2 = sg.render_list(100)
        assert collections.Counter(list1) != collections.Counter(list2)

    def test_seeded_randomizer(self):
        # provide a seed to get consistent results
        pattern = r"[\w]{10}&([\d]{10}|M3W9MF_lH3906I14O50)"

        for seed in [random.randint(1, 100000000) for _ in range(100)]:
            sg = StringGenerator(pattern, seed=seed)
            s1 = sg.render()
            sg = StringGenerator(pattern, seed=seed)
            s2 = sg.render()
            assert s1 == s2

            sg = StringGenerator(pattern, seed=seed)
            list1 = sg.render_list(100)
            sg = StringGenerator(pattern, seed=seed)
            list2 = sg.render_list(100)
            assert collections.Counter(list1) == collections.Counter(list2)

    def test_custom_bad_randomizer(self):
        pattern = r"[\w]{10}&([\d]{10}|M3W9MF_lH3906I14O50)"
        sg = StringGenerator(pattern, randomizer=CustomBadRandomizer())
        self.assertRaises(Exception, lambda: sg.render())

    def test_custom_randomizer(self):
        pattern = r"[\w]{10}&([\d]{10}|M3W9MF_lH3906I14O50)"
        sg = StringGenerator(pattern, randomizer=CustomRandomizer())
        assert len(sg.render())

    def test_dump(self):
        """make sure dump method works."""
        StringGenerator(r"[\w]{8}").dump()


if __name__ == "__main__":
    unittest.main()
