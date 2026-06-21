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

    def test_unicode_literals(self):
        """Test that Unicode literal strings are rendered correctly."""
        unicode_strings = [
            r"idzie wąż wąską dróżką",
            r"༣ཁངཱུངྵ",
            r"ᚠᚳᛦᛰ",
        ]

        for template in unicode_strings:
            result = SG(template).render()
            self.assertEqual(result, template)
            self.assertIsInstance(result, str)

    def test_unicode_character_class(self):
        """Test Unicode character class ranges."""
        template = r"[ą-ż]{8}"
        result = SG(template).render()

        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 8)

        # Verify all characters are in the expected Unicode range
        for char in result:
            self.assertGreaterEqual(ord(char), ord("ą"))
            self.assertLessEqual(ord(char), ord("ż"))

    def test_unicode_escape_sequences(self):
        """Test Unicode escape sequences in templates."""
        template = r"\xe6\xbf\xe5, \xe9\xe5\xa9\xe5\xe5\xad\xe6\xaf\xe7\xe9\xba\xbc\xe6\xe6"
        result = SG(template).render()

        self.assertIsInstance(result, str)
        self.assertIsNotNone(result)
        # The result should contain the decoded Unicode characters
        # Note: This template contains hex escape sequences that should be decoded

    def test_render_list_email_template(self):
        """Test render_list with email-like template."""
        template = r"[a-z][\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)"
        list_length = 10
        result = SG(template).render_list(list_length)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), list_length)

    def test_render_list_mixed_alphanumeric(self):
        """Test render_list with mixed alphanumeric template."""
        template = r"[a-z\d\d\d\d]{8}"
        list_length = 10
        result = SG(template).render_list(list_length)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), list_length)

    def test_render_list_letter_digit_combination_colon(self):
        """Test render_list with letter-digit combination using colon range syntax."""
        template = r"[\l]{6:10}&[\d]{2}"
        list_length = 10
        result = SG(template).render_list(list_length)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), list_length)

    def test_render_list_letter_digit_combination_hyphen(self):
        """Test render_list with letter-digit combination using hyphen range syntax."""
        template = r"[\l]{6-10}&[\d]{2}"  # support both hyphen and colon for ranges
        list_length = 10
        result = SG(template).render_list(list_length)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), list_length)

    def test_render_list_alternation(self):
        """Test render_list with alternation (OR) operator."""
        template = r"([a-z]{4}|[0-9]{9})"
        list_length = 10
        result = SG(template).render_list(list_length)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), list_length)

    def test_render_list_mixed_character_classes(self):
        """Test render_list with mixed character classes and & operator."""
        template = r"[\d]&[\c]&[\w\p]{6}"
        list_length = 10
        result = SG(template).render_list(list_length)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), list_length)

    def test_render_list_single_character_class(self):
        """Test render_list with single character class."""
        template = r"[\w\p]"
        list_length = 10
        result = SG(template).render_list(list_length)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), list_length)

    def test_render_list_fixed_length_character_class(self):
        """Test render_list with fixed length character class."""
        template = r"[\w\p]{6}"
        list_length = 10
        result = SG(template).render_list(list_length)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), list_length)

    def test_render_list_negative_quantifier(self):
        """Test render_list with negative quantifier."""
        template = r"[\w\p]{-6}"
        list_length = 10
        result = SG(template).render_list(list_length)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), list_length)

    def test_render_list_open_ended_quantifier(self):
        """Test render_list with open-ended quantifier."""
        template = r"[\w\p]{:6}"
        list_length = 10
        result = SG(template).render_list(list_length)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), list_length)

    def test_render_list_zero_to_n_quantifier(self):
        """Test render_list with zero-to-n quantifier."""
        template = r"[\w\p]{0:6}"
        list_length = 10
        result = SG(template).render_list(list_length)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), list_length)

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

        SG(r"[a-z\d\d\d\d]{8}").render_list(list_length, progress_callback=progress_callback)

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
            with self.assertRaises(SG.SyntaxError):
                SG(t).render()

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

    def test_buffered_secure_randomizer(self):
        """BufferedSecureRandom is reachable via SG and drives every path."""
        # Reachable without an extra import.
        rng = SG.BufferedSecureRandom
        from strgen import BufferedSecureRandom as ModuleLevel

        assert rng is ModuleLevel

        # Satisfies the randomizer contract.
        instance = rng()
        for method in ("randint", "choice", "choices", "shuffle"):
            assert hasattr(instance, method)

        # Fixed-length class (choices path).
        result = SG(r"[\d]{10}", randomizer=rng()).render_set(2000)
        assert len(result) == 2000
        assert all(len(s) == 10 and s.isdigit() for s in result)

        # Range quantifier (randint -> getrandbits path). A tiny buffer on a
        # single reused instance forces many refills across the 200 renders.
        ranged_sg = SG(r"[\d]{2:5}", randomizer=rng(bufsize=64))
        ranged = [ranged_sg.render() for _ in range(200)]
        assert all(2 <= len(s) <= 5 for s in ranged)

        # Seeding is a no-op: two instances still differ.
        a = SG(r"[\w]{16}", randomizer=rng()).render()
        b = SG(r"[\w]{16}", randomizer=rng()).render()
        assert a != b

        # The fast choices override (byte rejection sampling) is unbiased.
        # Reuse one generator so the 1 MB buffer is allocated once.
        digit_sg = SG(r"[\d]", randomizer=rng())
        counts = collections.Counter(digit_sg.render() for _ in range(20000))
        assert set(counts) == set("0123456789")
        # each digit within a generous band around the 2000 expected
        assert all(1700 < c < 2300 for c in counts.values())

        # Alphabets larger than one byte fall back to the standard path.
        big = SG(r"[Ā-Ԁ]{4}", randomizer=rng()).render()
        assert len(big) == 4

    def test_randomizer_is_per_instance(self):
        """Each generator owns its randomizer.

        Previously the randomizer was a class attribute, so constructing a
        second generator clobbered the RNG of every existing one. This
        interleaves two seeded instances and asserts each stays independent.
        """
        pattern = r"[\w]{20}"

        a = SG(pattern, seed=1)
        b = SG(pattern, seed=2)

        # Interleave renders across the two instances.
        a_first = a.render()
        b.render()
        a_second = a.render()

        # 'a' must behave exactly like a standalone seed=1 generator,
        # unaffected by 'b' having been constructed and used in between.
        ref = SG(pattern, seed=1)
        assert a_first == ref.render()
        assert a_second == ref.render()

    def test_custom_bad_randomizer(self):
        pattern = r"[\w]{10}&([\d]{10}|M3W9MF_lH3906I14O50)"
        sg = SG(pattern, randomizer=CustomBadRandomizer())
        with self.assertRaises(AttributeError):
            sg.render()

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
        assert SG(r"1&abc").count() == len(SG(r"1&abc").render_set(24))
        assert SG(r"[\u\d]{2}|[abc]{3}", uaf=100).count() == len(
            SG(r"[\u\d]{2}|[abc]{3}", uaf=100).render_list(1323, unique=True)
        )

    def test_count_and_operator(self):
        """count() over '&' is deterministic and only defined for fixed operands."""
        # Fixed (literal) operands: distinct permutations of "1abc" = 4! = 24.
        sg = SG(r"1&abc")
        assert sg.count() == 24
        assert sg.count() == len(sg.render_set(24))

        # Deterministic across repeated calls. Previously this rendered once and
        # counted that single sample, so the value varied with the random draw.
        assert len({SG(r"1&abc").count() for _ in range(20)}) == 1

        # Operands that can vary have no single well-defined count: raise rather
        # than return a draw-dependent number.
        with self.assertRaises(NotImplementedError):
            SG(r"[\d]{2}&[\d]{1}").count()

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
        # SG('1|2|3[abc]{1}'
        # ['1c', '2b', '1b', '2c', '2c', '3c', '3c', '2b', '1c', '1c']

        # NOT Correct:
        # SG('1|2|[abc]{1}'
        # ['1c', '2b', '1b', '2c', '2c', '3c', '3c', '2b', '1c', '1c']


class TestParserRegressions(unittest.TestCase):
    """Regression tests for parser defects.

    These assert the *intended* behavior and are expected to fail until the
    parser/escape handling is fixed. Each maps to a demonstrated bug.
    """

    def test_escaped_non_meta_in_literal_not_doubled(self):
        """`\\a` should be a literal 'a', not 'aa'.

        getLiteral re-adds the escaped char because the loop variable still
        holds it after consumption.
        """
        self.assertEqual(SG(r"\a").render(), "a")
        self.assertEqual(SG(r"foo\bar").render(), "foobar")

    def test_escaped_backslash_literal(self):
        """An escaped backslash is a single literal backslash."""
        self.assertEqual(SG(r"\\x").render(), "\\x")
        self.assertEqual(SG(r"a\\b").render(), "a\\b")

    def test_escaped_backslash_before_class(self):
        """A literal backslash immediately before a character class must parse.

        `\\[abc]` => one backslash followed by one of a/b/c.
        """
        result = SG(r"\\[abc]").render()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "\\")
        self.assertIn(result[1], "abc")

    def test_escaped_backslash_before_class_with_prefix(self):
        result = SG(r"x\\[ab]").render()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[:2], "x\\")
        self.assertIn(result[2], "ab")

    def test_source_at_start_of_pattern(self):
        """A `${name}` source at index 0 must render (last() is None there)."""
        self.assertEqual(SG(r"${names}").render(names=["A"]), "A")

    def test_empty_class_raises_syntax_error(self):
        """An empty character class is a template error, not a randrange crash."""
        for t in (r"[]", r"[]{3}"):
            with self.assertRaises(SG.SyntaxError):
                SG(t).render()

    def test_parse_errors_are_syntax_errors(self):
        """Malformed templates raise SG.SyntaxError, not bare Exception/TypeError."""
        for t in (r"[a]{", r"[a]{1", r"${ }", r"${1bad}"):
            with self.assertRaises(SG.SyntaxError):
                SG(t).render()

    def test_existing_syntax_errors_still_raise(self):
        """Baselines that already raise SG.SyntaxError; lock them in."""
        for t in (r"[a]{x}", r"[a-]", r"[\w]{10:}"):
            with self.assertRaises(SG.SyntaxError):
                SG(t).render()


if __name__ == "__main__":
    unittest.main()
