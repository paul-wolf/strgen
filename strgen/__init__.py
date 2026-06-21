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


import os
import random
import string
import types
import typing
import math
import itertools
from abc import ABC, abstractmethod
from collections import Counter, namedtuple
from math import factorial

__version__ = "0.5.1"
__author__ = "Paul Wolf"
__license__ = "BSD"


# A lexer token. ``type`` is one of the structural kinds (LBRACKET, PIPE, ...)
# or "CHAR"/"EOF". ``escaped`` is only meaningful for CHAR tokens and records
# whether the character came from a backslash escape, so the parser can tell a
# literal "[" from a class opener without ever re-examining backslashes.
Token = namedtuple("Token", ["type", "value", "escaped"], defaults=[False])


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


class BufferedSecureRandom(random.Random):
    """Cryptographically secure RNG that buffers ``os.urandom`` in bulk.

    ``random.SystemRandom`` reads from the OS entropy pool on every draw, which
    means one syscall per random value. Generating large batches (e.g.
    ``render_set(1_000_000)``) then spends most of its time in the kernel.

    This class draws the exact same entropy -- raw ``os.urandom`` bytes, each
    consumed once and never expanded by a userspace PRNG -- but reads it in big
    chunks, amortizing the syscall across many values. It is therefore as
    secure as ``SystemRandom`` (suitable for tokens, passwords, keys) while
    being substantially faster for bulk generation.

    Pass it via the ``randomizer`` argument; it is reachable without an extra
    import as ``StringGenerator.BufferedSecureRandom``::

        SG(r"[\\w\\p]{32}", randomizer=SG.BufferedSecureRandom()).render_set(50000)

    Being entropy-based, it ignores seeding.
    """

    def __init__(self, bufsize=1 << 20):
        self._buf = b""
        self._i = 0
        self._bufsize = bufsize
        super().__init__()

    def _take(self, n):
        """Return n fresh random bytes, refilling the buffer when needed."""
        if self._i + n > len(self._buf):
            self._buf = os.urandom(max(n, self._bufsize))
            self._i = 0
        chunk = self._buf[self._i : self._i + n]
        self._i += n
        return chunk

    def random(self):
        """Return a 53-bit float in [0.0, 1.0), as SystemRandom.random does."""
        return (int.from_bytes(self._take(7), "big") >> 3) * (2.0**-53)

    def getrandbits(self, k):
        if k <= 0:
            raise ValueError("number of bits must be greater than zero")
        nbytes = (k + 7) // 8
        return int.from_bytes(self._take(nbytes), "big") >> (nbytes * 8 - k)

    def choices(self, population, weights=None, *, cum_weights=None, k=1):
        """Unweighted draws map bytes straight to indices via rejection
        sampling, skipping the per-pick float construction in random(). This is
        the hot path for character sets and is several times faster. Weighted
        draws, an empty population, or alphabets larger than one byte fall back
        to the standard implementation (which still uses our random()).
        """
        n = len(population)
        if weights is not None or cum_weights is not None or n == 0 or n > 256:
            return super().choices(population, weights, cum_weights=cum_weights, k=k)
        limit = 256 - (256 % n)  # largest multiple of n <= 256; reject above it for uniformity
        out = []
        append = out.append
        take = self._take
        while len(out) < k:
            for byte in take(k - len(out)):
                if byte < limit:
                    append(population[byte % n])
                    if len(out) == k:
                        break
        return out

    def seed(self, *args, **kwargs):
        """No-op: entropy-based, so there is no seed state to set."""

    def _notimplemented(self, *args, **kwargs):
        raise NotImplementedError("BufferedSecureRandom is entropy-based; state cannot be saved or restored")

    getstate = setstate = _notimplemented


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

    # Per-instance; assigned in __init__. Declared here only as a type hint so
    # it is never a shared class attribute (which would let one instance clobber
    # another's RNG and break seeded determinism / thread-safety).
    randomizer: typing.Optional[random.Random]

    # Exposed here so callers can opt into the fast secure RNG without a second
    # import: SG(pattern, randomizer=SG.BufferedSecureRandom()).
    BufferedSecureRandom = BufferedSecureRandom

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
        def render(self, randomizer, **kwargs):
            pass

        @abstractmethod
        def count(self, randomizer, **kwargs):
            pass

        @abstractmethod
        def dump(self):
            pass

    class Sequence:
        """Render a sequence of nodes from the template."""

        def __init__(self, seq):
            """seq is a list."""
            self.seq = seq  # list of StringNodes

        def render(self, randomizer, **kwargs):
            return "".join([x.render(randomizer, **kwargs) for x in self.seq])

        def count(self, randomizer, **kwargs):
            """This sequence of counts:
            P x P x P...
            The cummulative product.
            """
            d = [_.count(randomizer, **kwargs) for _ in self.seq]
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

        def render(self, randomizer, **kwargs):
            """Return on of a sequence of nodes."""

            return self.seq[randomizer.randint(0, len(self.seq) - 1)].render(randomizer, **kwargs)

        def count(self, randomizer, **kwargs):
            return sum([x.count(randomizer, **kwargs) for x in self.seq])

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

        def render(self, randomizer, **kwargs):
            """Return a permutation without replacement of all characters in seq."""
            char_list = list("".join([x.render(randomizer, **kwargs) for x in self.seq]))
            randomizer.shuffle(char_list)
            return "".join(char_list)

        def count(self, randomizer, **kwargs):
            """Number of distinct outcomes of a permutation ('&') of the operands.

            '&' shuffles together the characters produced by all operands. When
            every operand is fixed -- it has exactly one possible value, i.e.
            ``count() == 1`` -- the multiset of characters is known, and the
            answer is just the number of distinct permutations of that multiset.

            When an operand can vary (e.g. a character set), the set of
            characters being shuffled changes with each random draw, so there is
            no single well-defined count. Rather than return a misleading,
            draw-dependent number (the previous behaviour) we raise
            NotImplementedError. See ``StringGenerator.count`` for the full set
            of assumptions behind counting.
            """
            operand_counts = [node.count(randomizer, **kwargs) for node in self.seq]
            if all(c == 1 for c in operand_counts):
                # every operand is fixed, so the multiset of characters is known
                chars = "".join(node.render(randomizer, **kwargs) for node in self.seq)
                return permutation_count(chars)
            raise NotImplementedError(
                "count() is undefined for '&' over operands that are not fixed; "
                "the result would depend on the random draw"
            )

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

        def render(self, randomizer, **kwargs):
            return self.literal

        def count(self, randomizer, **kwargs):
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

        def render(self, randomizer, **kwargs):
            if self.start > -1:
                cnt = randomizer.randint(self.start, self.cnt)
            else:
                cnt = self.cnt

            # choices() draws all cnt characters in a single C-level call, far
            # faster than one randint() per character for large outputs.
            return "".join(randomizer.choices(self.chars, k=cnt))

        def count(self, randomizer, **kwargs):
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
            return f"{self.__class__.__name__}: start={self.start}, cnt={self.cnt}, chars={self.chars}"

    class Source(StringNode):
        """Render a string from a generator, list, function."""

        def __init__(self, source):
            self.source = source

        def render(self, randomizer, **kwargs):
            src = kwargs.get(self.source) if self.source in kwargs else ""
            if isinstance(
                src,
                (
                    list,
                    set,
                    tuple,
                ),
            ):
                return str(randomizer.choice(src))
            if callable(src):
                return str(src())
            elif isinstance(src, types.GeneratorType):
                return str(next(src))
            else:
                return str(src)

        def count(self, randomizer, **kwargs):
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
        self.pattern = pattern
        self.pos = 0
        self.unique_attempts_factor = uaf
        self.tokens = self._tokenize()
        self.seq = self._parse()
        if randomizer:
            if not (
                hasattr(randomizer, "randint")
                and hasattr(randomizer, "choice")
                and hasattr(randomizer, "choices")
                and hasattr(randomizer, "shuffle")
            ):
                Exception(
                    "The randomizer class instance must provide at least these methods: "
                    "randint, choice, choices, shuffle"
                )
            self.randomizer = randomizer
        else:
            self.randomizer = randomizer_factory(seed)

    def getCharacterRange(self, f, t):
        chars = ""
        # support z-a as a range
        if not ord(f) < ord(t):
            f, t = t, f
        if (ord(t) - ord(f)) > 10000:  # protect against large sets ?
            raise Exception("character range too large: %s - %s: %s" % (f, t, ord(t) - ord(f)))
        for c in range(ord(f), ord(t) + 1):
            chars += chr(c)
        return chars

    # ----- Tokenizer ------------------------------------------------------

    # Structural metacharacters each map to their own token type. Everything
    # else becomes a CHAR token. Crucially, a backslash escape is resolved
    # exactly once here into a CHAR token (escaped=True), so the parser never
    # sees a backslash and never has to guess whether a metacharacter was
    # escaped via lookbehind.
    _meta_token = {
        "[": "LBRACKET",
        "]": "RBRACKET",
        "{": "LBRACE",
        "}": "RBRACE",
        "(": "LPAREN",
        ")": "RPAREN",
        "|": "PIPE",
        "&": "AMP",
        "$": "DOLLAR",
    }

    def _tokenize(self):
        """Turn self.pattern into a flat list of tokens ending in EOF."""
        tokens = []
        pattern = self.pattern
        i = 0
        n = len(pattern)
        while i < n:
            ch = pattern[i]
            if ch == "\\":
                if i + 1 < n:
                    tokens.append(Token("CHAR", pattern[i + 1], True))
                    i += 2
                else:
                    # A trailing backslash escapes nothing; drop it.
                    i += 1
                continue
            kind = self._meta_token.get(ch)
            if kind:
                tokens.append(Token(kind, ch))
            else:
                tokens.append(Token("CHAR", ch))
            i += 1
        tokens.append(Token("EOF", None))
        return tokens

    # ----- Parser ---------------------------------------------------------

    def _peek(self):
        return self.tokens[self.pos]

    def _advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _parse(self):
        self.pos = 0
        return self._parse_sequence(level=0)

    def _parse_literal(self):
        """Consume a run of CHAR tokens into a single Literal node."""
        chars = []
        while self._peek().type == "CHAR":
            chars.append(self._advance().value)
        return StringGenerator.Literal("".join(chars))

    def _parse_source(self):
        """Parse a ${identifier} source; '$' and '{' are the current tokens."""
        self._advance()  # $
        self._advance()  # {
        chars = []
        while True:
            tok = self._advance()
            if tok.type == "EOF":
                raise StringGenerator.SyntaxError("unexpected end of input getting source")
            if tok.type == "RBRACE":
                break
            chars.append(tok.value if tok.value is not None else "")
        identifier = "".join(chars)
        if not identifier or not identifier.isidentifier():
            raise StringGenerator.SyntaxError("not a valid identifier: %s" % identifier)
        return StringGenerator.Source(identifier)

    def _parse_quantifier(self):
        """Parse a {m}, {m:n} or {m-n} quantifier; '{' is the current token."""
        self._advance()  # {
        start = -1
        digits = "0"
        prev_was_separator = False
        while True:
            tok = self._advance()
            if tok.type == "EOF":
                raise StringGenerator.SyntaxError("unexpected end of input getting quantifier")
            if tok.type == "RBRACE":
                if prev_was_separator:
                    # the user likely expected python slice notation, where the
                    # upper bound may be left open; we require a closed range
                    raise StringGenerator.SyntaxError("quantifier range must be closed")
                break
            if tok.type == "CHAR" and tok.value in ":-":
                start = int(digits)
                digits = "0"
                prev_was_separator = True
                continue
            if tok.type == "CHAR" and tok.value.isnumeric():
                digits += tok.value
                prev_was_separator = False
                continue
            raise StringGenerator.SyntaxError("non-digit in count")
        return [start, int(digits)]

    def _parse_character_class(self):
        """Parse a [...] class with individual members, ranges and shortcuts.

        The current token is the opening '['.
        """
        self._advance()  # [
        chars = []
        closed = False
        while True:
            tok = self._peek()
            if tok.type == "EOF":
                # Unterminated class. The original parser tolerated this, so we
                # keep that behavior rather than introduce a new error here.
                break
            if tok.type == "RBRACKET":
                self._advance()
                closed = True
                break
            if tok.type != "CHAR":
                raise StringGenerator.SyntaxError("Un-escaped character in class definition: %s" % tok.value)

            nxt = self.tokens[self.pos + 1]
            if not tok.escaped and nxt.type == "CHAR" and not nxt.escaped and nxt.value == "-":
                # a range: <near> '-' <far>
                near = self._advance().value
                self._advance()  # hyphen
                far = self._advance()
                if far.type != "CHAR":
                    raise StringGenerator.SyntaxError("unexpected end of class range")
                chars.append(self.getCharacterRange(near, far.value))
                continue

            if tok.escaped and tok.value in self.string_code:
                chars.append(self.string_code[tok.value])
            else:
                chars.append(tok.value)
            self._advance()

        text = "".join(chars)
        if not text:
            raise StringGenerator.SyntaxError("empty character class")

        if closed and self._peek().type == "LBRACE":
            start, cnt = self._parse_quantifier()
        elif closed:
            start, cnt = -1, 1
        else:
            # unterminated class: original left start=0 (renders 0 or 1 char)
            start, cnt = 0, 1
        return StringGenerator.CharacterSet(text, start, cnt)

    def _parse_sequence(self, level=0):
        """Parse a sequence of nodes, honoring the '|' and '&' operators.

        The operator handling mirrors the original parser: operands are
        gathered onto a stack and committed into a SequenceOR/SequenceAND
        whenever the operator changes or a new operand group begins.
        """
        operand_stack = []
        op = None
        seq = []

        def commit_operands():
            nonlocal operand_stack, op, seq
            if op and operand_stack:
                klass = StringGenerator.SequenceOR if op == "|" else StringGenerator.SequenceAND
                seq.append(klass(operand_stack[:]))
                operand_stack = []
                op = None

        # Track whether the previously consumed token was a binary operator so
        # we can tell if a new '[', '(' or '${' opens a fresh operand group.
        prev_exists = False
        prev_is_operator = False
        sequence_closed = False

        while True:
            tok = self._peek()
            t = tok.type

            if t == "EOF":
                break
            elif t == "CHAR":
                seq.append(self._parse_literal())
                prev_exists, prev_is_operator = True, False
            elif t == "DOLLAR" and self.tokens[self.pos + 1].type == "LBRACE":
                if prev_exists and not prev_is_operator:
                    commit_operands()
                seq.append(self._parse_source())
                prev_exists, prev_is_operator = True, False
            elif t == "LBRACKET":
                if prev_exists and not prev_is_operator:
                    commit_operands()
                seq.append(self._parse_character_class())
                prev_exists, prev_is_operator = True, False
            elif t == "LPAREN":
                if prev_exists and not prev_is_operator:
                    commit_operands()
                self._advance()  # (
                seq.append(self._parse_sequence(level + 1))
                prev_exists, prev_is_operator = True, False
            elif t == "RPAREN":
                if level == 0:
                    raise StringGenerator.SyntaxError("Extra closing parenthesis")
                self._advance()  # )
                sequence_closed = True
                break
            elif t in ("PIPE", "AMP"):
                if op and not op == tok.value:
                    # operator switched; flush the pending operand group
                    commit_operands()
                op = tok.value
                self._advance()
                prev_exists, prev_is_operator = True, True
            else:
                # LBRACE, RBRACE, or a '$' not introducing a source.
                raise StringGenerator.SyntaxError("Un-escaped special character: %s" % tok.value)

            if op and len(seq):
                operand_stack.append(seq.pop())

        commit_operands()

        if level > 0 and not sequence_closed:
            # finishing a nested sequence without a closing parenthesis
            raise StringGenerator.SyntaxError("Missing closing parenthesis")

        return StringGenerator.Sequence(seq)

    def render(self, **kwargs) -> str:
        """Produce a randomized string that fits the template/pattern.

        Args:
            None

        Returns:
            The generated string.

        """
        return self.seq.render(self.randomizer, **kwargs)

    def count(self, **kwargs) -> int:
        r"""Return the size of the generation sample space for the template.

        This is the number of distinct strings the template can produce, but
        only under the following assumptions. Where they do not hold, the value
        is the size of the *generation* space (the number of ways the template
        can be filled in), which may exceed the number of distinct strings:

        * **Character classes contain no duplicate characters.** ``len(chars)``
          is used as the alphabet size, so a class with repeats (e.g.
          ``[a\d\d]``) counts each repeat as a separate option and overcounts.
          The generator also weights repeated characters more heavily when
          rendering, so this number reflects that weighting.
        * **Alternation (``|``) branches are disjoint.** The count sums the
          branch sizes, which equals the number of distinct results only if no
          two branches can produce the same string; overlapping branches
          overcount.
        * **Permutation (``&``) is applied only to fixed operands.** For ``&``
          over operands that can vary, the count depends on the random draw, so
          ``count()`` raises NotImplementedError instead of guessing.

        ``count()`` also raises NotImplementedError if the template contains a
        ``${...}`` source, since a source may be an arbitrary callable or list
        whose size is unknown.
        """
        return self.seq.count(self.randomizer, **kwargs)

    def dump(self, cnt=None, **kwargs):
        """Print the parse tree and then call render for an example."""
        import sys

        if not self.seq:
            self.seq = self._parse()
        print("StringGenerator version: %s" % (__version__))
        print("Python version: %s" % sys.version)
        print(f"Random method provider class: {self.randomizer.__class__.__name__}")
        self.seq.dump()
        print(f"Potential outcome count: {self.count()}")
        print("Example result:")
        if cnt:
            return self.render_list(cnt, **kwargs)
        return self.render(**kwargs)

    def render_list(self, cnt, unique=False, progress_callback=None, **kwargs) -> typing.List:
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
