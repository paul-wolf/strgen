# Copyright (c) 2013-2020, Paul Wolf
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# 3. Neither the name of Yewleaf Ltd. nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Original author: paul.wolf@yewleaf.com


import random
import string
import types
import typing
import math
import itertools
from abc import ABC, abstractmethod
from collections import Counter
from math import factorial

__version__ = "0.4.4"
__author__ = "Paul Wolf"
__license__ = "BSD"


def permutation_count(s):
    """Return the number of different permutations of s.
    math.perm does not exist before P3.8.
    https://codereview.stackexchange.com/questions/132704/counting-permutations-without-repetitions-for-a-number-or-a-string
    """
    c = 1
    for i in Counter(s).values():
        c *= factorial(i)
    return factorial(len(s)) // c


def randomizer_factory(seed) -> random.Random:
    """Return class instance that will provide randint, choice, shuffle.

    If there is a seed, we need to use Random.

    """
    if seed:
        return random.Random(seed)
    try:
        return random.SystemRandom()
    except Exception:
        return random.Random()


class StringGenerator:
    """Generate a randomized string of characters using a template.

    The purpose of this class is to generate a string of characters
    according to a template.  The template language is superficially
    similar to regular expressions but fundamentally different in
    purpose.

    Usage:

       StringGenerator(<template>).render()

    or:

       StringGenerator(<template>).render_list(10, unique=True)

    The latter produces a list of 10 strings that are unique within
    the list.

    Example:

       `StringGenerator(r"[\\d]{10}").render_list(10, unique=True)`

    This generates 10 unique strings containing digits. Each will be
    10 characters in length.

    """

    randomizer: typing.Optional[random.Random] = None

    class SyntaxError(Exception):
        """Catch syntax errors."""

    class UniquenessError(Exception):
        """Catch when template can't generate required list count."""

    meta_chars = "[]{}()|&$"
    mytab = " " * 4

    string_code = {
        "d": string.digits,
        "w": "_" + string.ascii_letters + string.digits,
        "W": string.whitespace + string.punctuation,
        "s": string.whitespace,
        "p": string.punctuation,
        "l": string.ascii_letters,
        "u": string.ascii_uppercase,
        "U": string.ascii_uppercase,
        "c": string.ascii_lowercase,
        "o": string.octdigits,
        "h": string.hexdigits,
        "r": string.printable,
    }
    string_code_help = {
        "d": "digits",
        "w": "_" + "ascii_letters + digits",
        "W": "whitespace + punctuation",
        "s": "whitespace",
        "p": "punctuation",
        "l": "ascii_letters",
        "u": "ascii_uppercase",
        "U": "ascii_uppercase",
        "c": "ascii_lowercase",
        "o": "octdigits",
        "h": "hexdigits",
        "r": "printable",
    }

    class StringNode(ABC):
        """The abstract class for all nodes"""

        @abstractmethod
        def render(self, **kwargs):
            pass

        @abstractmethod
        def count(self, **kwargs):
            pass

        @abstractmethod
        def dump(self):
            pass

    class Sequence:
        """Render a sequence of nodes from the template."""

        def __init__(self, seq):
            """seq is a list."""
            self.seq = seq  # list of StringNodes

        def render(self, **kwargs):
            return "".join([x.render(**kwargs) for x in self.seq])

        def count(self, **kwargs):
            """This sequence of counts:
            P x P x P...
            The cummulative product.
            """
            d = [_.count(**kwargs) for _ in self.seq]
            x = 1
            for i in d:
                x *= i
            return x


        def dump(self, level=-1):
            print((StringGenerator.mytab * level) + f"{self.__class__.__name__}")
            for s in self.seq:
                s.dump(level + 1)

    class SequenceOR(Sequence):
        """Randomly choose from operands."""

        def render(self, **kwargs):
            """Return on of a sequence of nodes."""

            return self.seq[
                StringGenerator.randomizer.randint(0, len(self.seq) - 1)
            ].render(**kwargs)

        def count(self, **kwargs):
            return sum([x.count(**kwargs) for x in self.seq])

        def dump(self, level=-1):
            print((StringGenerator.mytab * level) + repr(self))
            for s in self.seq:
                s.dump(level + 1)

        def __repr__(self):
            return f"{self.__class__.__name__}"

        def __str__(self):
            return "OR"

    class SequenceAND(Sequence):
        """Render a permutation without replacement
        of characters from operands.
        """

        def render(self, **kwargs):
            """Return a permutation without replacement of all characters in seq.
            """
            char_list = list("".join([x.render(**kwargs) for x in self.seq]))
            StringGenerator.randomizer.shuffle(char_list)
            return "".join(char_list)

        def count(self, **kwargs):
            """This does not work for complex expressions."""
            char_list = list("".join([x.render(**kwargs) for x in self.seq]))
            return permutation_count(char_list)

        def dump(self, level=-1):
            print((StringGenerator.mytab * level) + repr(self))
            for s in self.seq:
                s.dump(level + 1)

        def __str__(self):
            return "AND"

        def __repr__(self):
            return f"{self.__class__.__name__}"

    class Literal(StringNode):
        """Render a literal string."""

        def __init__(self, chars):
            self.literal = chars  # a literal string

        def render(self, **kwargs):
            return self.literal

        def count(self, **kwargs):
            return 1

        def dump(self, level=0):
            print((StringGenerator.mytab * level) + repr(self))

        def __str__(self):
            return self.literal

        def __repr__(self):
            return f"{self.__class__.__name__}: {self.literal}"

    class CharacterSet(StringNode):
        """Render a random combination from a set of characters."""

        def __init__(self, chars, start, cnt):
            self.chars = chars
            try:
                self.start = int(start)
                self.cnt = int(cnt)
            except Exception as e:
                raise e

        def render(self, **kwargs):
            cnt = 1
            if self.start > -1:
                cnt = StringGenerator.randomizer.randint(self.start, self.cnt)
            else:
                cnt = self.cnt

            return "".join(
                self.chars[StringGenerator.randomizer.randint(0, len(self.chars) - 1)]
                for x in range(cnt)
            )

        def count(self, **kwargs):
            """Permutation with replacement.
            The cummulative sum of c ** r
            """
            if self.start < 0:
                # fixed length
                return len(self.chars) ** self.cnt
            # range
            return sum([len(self.chars) ** r for r in range(self.start, self.cnt + 1)])

        def dump(self, level=0):
            print(StringGenerator.mytab * level + repr(self))

        def __str__(self):
            return f"start={self.start}, cnt={self.cnt}, chars={self.chars}"

        def __repr__(self):
            return (
                f"{self.__class__.__name__}: start={self.start}, cnt={self.cnt}, chars={self.chars}"
            )

    class Source(StringNode):
        """Render a string from a generator, list, function."""

        def __init__(self, source):
            self.source = source

        def render(self, **kwargs):
            src = kwargs.get(self.source) if self.source in kwargs else ""
            if isinstance(
                src,
                (
                    list,
                    set,
                    tuple,
                ),
            ):
                return str(StringGenerator.randomizer.choice(src))
            if callable(src):
                return str(src())
            elif isinstance(src, types.GeneratorType):
                return str(next(src))
            else:
                return str(src)

        def count(self, **kwargs):
            """Since a source name can be a callable, we can't say what the count
            is.

            """
            raise NotImplementedError("Cannot get count for source nodes")

        def dump(self, level=0):
            print((StringGenerator.mytab * level) + "$%s" % self.source)

        def __repr__(self):
            return f"{self.__class__.__name__}: {self.source}"

        def __str__(self):
            return str(self)

    def __init__(self, pattern, uaf=10, randomizer=None, seed=None):
        try:
            self.pattern = pattern
        except NameError:
            self.pattern = pattern
        self.seq = None
        self.index = -1
        self.unique_attempts_factor = uaf
        self.seq = self.getSequence()
        if randomizer:
            if not (
                hasattr(randomizer, "randint")
                and hasattr(randomizer, "choice")
                and hasattr(randomizer, "shuffle")
            ):
                Exception(
                    "The randomizer class instance must provide at least these methods: randint, choice, shuffle"
                )
            StringGenerator.randomizer = randomizer
        else:
            StringGenerator.randomizer = randomizer_factory(seed)

    def current(self):
        if self.index < len(self.pattern):
            return self.pattern[self.index]
        return None

    def peek(self):
        """Just an alias."""
        return self.current()

    def next(self):
        self.index += 1
        return self.current()

    def lookahead(self):
        if self.index + 1 < len(self.pattern):
            return self.pattern[self.index + 1]
        return None

    def last(self):
        if self.index == 0:
            return None
        return self.pattern[self.index - 1]

    def getQuantifier(self):
        start = -1
        bracket = self.next()
        # we should only be here because that was a bracket
        if not bracket == "{":
            raise Exception("parse error getting quantifier")
        d = ""
        digits = "0"
        while True:
            d = self.next()
            if not d:
                raise Exception("unexpected end of input getting quantifier")
            if d == ":" or d == "-":
                start = int(digits)
                digits = "0"
                continue
            if d == "}":
                if self.last() in ":-":
                    # this happens if the user thinks the quantifier
                    # behaves like python slice notation in allowing uppper range to be open
                    raise StringGenerator.SyntaxError("quantifier range must be closed")
                break
            if d.isnumeric():
                digits += d
            else:
                raise StringGenerator.SyntaxError("non-digit in count")
        return [start, int(digits)]

    def getSource(self):
        """Extract the identifier out of this construct: ${mylist}: mylist"""
        bracket = self.next()
        # we should only be here because that was a bracket
        if not bracket == "{":
            raise Exception("parse error getting source")
        c = ""
        identifier = ""
        while True:
            c = self.next()
            if not c:
                raise Exception("unexpected end of input getting source")
            if c == "}":
                break
            else:
                identifier += c
        if not identifier or not identifier.isidentifier():
            raise StringGenerator.SyntaxError("not a valid identifier: %s" % identifier)
        return StringGenerator.Source(identifier)

    def getCharacterRange(self, f, t):
        chars = ""
        # support z-a as a range
        if not ord(f) < ord(t):
            tmp = f
            f = t
            t = tmp
        if (ord(t) - ord(f)) > 10000:  # protect against large sets ?
            raise Exception(
                "character range too large: %s - %s: %s" % (f, t, ord(t) - ord(f))
            )
        for c in range(ord(f), ord(t) + 1):
            chars += chr(c)
        return chars

    def getCharacterSet(self):
        """Get a character set with individual members or ranges.

        Current index is on '[', the start of the character set.

        """

        chars = ""
        c = None
        cnt = 1
        start = 0

        while True:
            c = self.next()
            if self.lookahead() == "-" and not c == "\\":
                f = c
                self.next()  # skip hyphen
                c = self.next()  # get far range
                if not c or (c in self.meta_chars):
                    raise StringGenerator.SyntaxError("unexpected end of class range")
                chars += self.getCharacterRange(f, c)
            elif c == "\\":
                if self.lookahead() == "\\":
                    c = self.next()
                    chars += c
                    continue
                if self.lookahead() in self.meta_chars:
                    c = self.next()
                    chars += c
                    continue
                elif self.lookahead() in self.string_code:
                    c = self.next()
                    chars += self.string_code[c]
            elif c and c not in self.meta_chars:
                chars += c
            if c == "]":
                if self.lookahead() == "{":
                    [start, cnt] = self.getQuantifier()
                else:
                    start = -1
                    cnt = 1
                break
            if c and c in self.meta_chars and not self.last() == "\\":
                raise StringGenerator.SyntaxError(
                    "Un-escaped character in class definition: %s" % c
                )
            if not c:
                break

        return StringGenerator.CharacterSet(chars, start, cnt)

    def getLiteral(self):
        """Get a sequence of non-special characters."""
        # we are on the first non-special character

        chars = ""
        c = self.current()
        while True:
            if c and c == "\\":
                c = self.next()
                if c:
                    chars += c
                continue
            elif not c or (c in self.meta_chars):
                break
            else:
                chars += c
            if self.lookahead() and self.lookahead() in self.meta_chars:
                break
            c = self.next()
        return StringGenerator.Literal(chars)

    def getSequence(self, level=0):
        """Get a sequence of nodes.

        We support only two operators: '|' and '&'

        """
        operand_stack = list()
        op = None
        seq = list()

        def commit_operands():
            """Append to seq if operands."""
            nonlocal operand_stack, op, seq
            if op and operand_stack:
                klass = (
                    StringGenerator.SequenceOR
                    if op == "|"
                    else StringGenerator.SequenceAND
                )
                seq.append(klass(operand_stack[:]))
                operand_stack = list()
                op = None

        sequence_closed = False
        while True:
            c = self.next()
            if not c:
                break
            if c and c not in self.meta_chars:
                seq.append(self.getLiteral())
            elif c and c == "$" and self.lookahead() == "{":
                if not self.last() in "&|":
                    commit_operands()
                seq.append(self.getSource())
            elif c == "[" and not self.last() == "\\":
                # if this is the first node after an op
                # it is a right operand
                # otherwise, stop collecting operands
                if self.last() and not self.last() in "&|":
                    commit_operands()
                seq.append(self.getCharacterSet())
            elif c == "(" and not self.last() == "\\":
                if self.last() and not self.last() in "&|":
                    commit_operands()
                seq.append(self.getSequence(level + 1))
            elif c == ")" and not self.last() == "\\":
                # end of this sequence
                if level == 0:
                    # there should be no parens here
                    raise StringGenerator.SyntaxError("Extra closing parenthesis")
                sequence_closed = True
                break
            elif c in "|&" and not self.last() == "\\":
                if op and not op == c:
                    # handle the case where we switch operators
                    commit_operands()
                op = c
            else:
                if c in self.meta_chars and not self.last() == "\\":
                    raise StringGenerator.SyntaxError(
                        "Un-escaped special character: %s" % c
                    )

            if op and len(seq):
                operand_stack.append(seq.pop())

        commit_operands()

        if level > 0 and not sequence_closed:
            # it means we are finishing a non-first-level sequence without closing parens
            raise StringGenerator.SyntaxError("Missing closing parenthesis")

        return StringGenerator.Sequence(seq)

    def render(self, **kwargs) -> str:
        """Produce a randomized string that fits the template/pattern.

        Args:
            None

        Returns:
            The generated string.

        """
        return self.seq.render(**kwargs)

    def count(self, **kwargs) -> int:
        return self.seq.count(**kwargs)

    def dump(self, cnt=None, **kwargs):
        """Print the parse tree and then call render for an example."""
        import sys

        if not self.seq:
            self.seq = self.getSequence()
        print("StringGenerator version: %s" % (__version__))
        print("Python version: %s" % sys.version)
        print(
            f"Random method provider class: {StringGenerator.randomizer.__class__.__name__}"
        )
        self.seq.dump()
        print(f"Potential outcome count: {self.count()}")
        print("Example result:")
        if cnt:
            return self.render_list(cnt, **kwargs)
        return self.render(**kwargs)

    def render_list(
        self, cnt, unique=False, progress_callback=None, **kwargs
    ) -> typing.List:
        """Return a list of generated strings.

        Args:
            cnt (int): length of list
            unique (bool): whether to make entries unique
            progress_callback: callable

        Returns:
            list.

        We keep track of total attempts because a template may
        specify something impossible to attain, like [1-9]{} with cnt==1000

        """

        rendered_list = []
        i = 0
        total_attempts = 0
        while True:
            if i >= cnt:
                break
            if total_attempts > cnt * self.unique_attempts_factor:
                raise StringGenerator.UniquenessError("couldn't satisfy uniqueness")
            s = self.render(**kwargs)
            if unique:
                if s not in rendered_list:
                    rendered_list.append(s)
                    i += 1
            else:
                rendered_list.append(s)
                i += 1
            total_attempts += 1

            # Optionally trigger the progress indicator to inform others about our progress
            if progress_callback and callable(progress_callback):
                progress_callback(i, cnt)

        return rendered_list

    def render_set(self, cnt, **kwargs) -> typing.Set:
        """Return a set of generated strings that will as a result be unique.

        Args:
            cnt (int): length of list

        Returns:
            set

        This is like `render_list(n, unique=True)` but will not take a callback and returns a set.
        It will be much faster than `render_list()`.

        Caution: this will not check if the solution set is
        feasible. It will be stuck in a loop if you use a large sample space . The following
        will never complete:

            SG("[123]{2}").render_set(100)

        """

        results: typing.Set = set()
        while len(results) < cnt:
            results |= {self.render(**kwargs) for _ in range(cnt - len(results))}

        return results

    def __str__(self):
        return self.render()

    def __repr__(self):
        return f"{self.__class__.__name__}, {self.pattern}, {self.randomizer.__class__.__name__}"
