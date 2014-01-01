# -*- coding: utf-8 -*-
u"""
Copyright (c) 2013, Yewleaf Ltd.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

3. Neither the name of Yewleaf Ltd. nor the names of its contributors
may be used to endorse or promote products derived from this software
without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import random
import string

try:
    # try to use cryptographically strong methods
    sr = random.SystemRandom()
    randint = random.sr.randint
    choice = random.sr.choice
    sample = random.sr.sample
    shuffle = random.sr.shuffle
except:
    # fall back if necessary
    randint = random.randint
    choice = random.choice
    sample = random.sample
    shuffle = random.shuffle

class StringGenerator(object):
    u"""Generate a randomized string of characters using a template.

    The purpose of this class is to generate a string of characters
    according to a template.  The template language is superficially
    similar to regular expressions but fundamentally different in
    purpose.

    Constructor
    ===========

       StringGenerator(<template>)

    Usage:

       StringGenerator(<template>).render()

    or:

       StringGenerator(<template>).render_list(10,unique=True)

    The latter produces a list of 10 strings that are unique within the list.

    Example: 

       StringGenerator("[\d]{10}").render_list(10,unique=True)
        
    This generates 10 unique strings containing digits. Each will be 10 characters in length.

    It supports the following constructs:

    Literal: <any string>
    ---------------------
    Any literal string. 

    Example:
    
        abc

    Character class: [<class specification>]
    ----------------------------------------
    Much like in regular expressions, it uses strings of characters
    and hyphen for defining a class of characters.

    Example:
    
        [a-z0-9_]

    Generate a string with lower case letters, digits and the underscore.

    Quantifier: {x:y} 
    ----------------- 
    Where x is lower bound and y is upper bound. This construct must
    always follow immediately a class with no intervening
    whitespace. It is possible to write {:y} as a shorthand for {0:y}
    or {y} to indicate a fixed length.

    Example: 

        [a-z]{0:8}

    Generates a string from zero to 8 in length composed of lower case
    alphabetic characters

        [a-z]{4}|[0-9]{9}

    Generates a string with either four lower case alphbetic
    characters or a string that is 9 digits in length.

    Groups:  (<group sepcification>)
    --------------------------------
    A group specification is a collection of literals, character
    classes or other groups divided by the OR operator '|' or the
    permutation operator '&'.

    OR Operator
    -----------
    The binary '|' operator can be used in a group to cause one of the
    operands to be return and the other to be ignored with an even
    chance.
    
    Permutation Operator
    --------------------
    The binary '&' operator causes its operands to be combined and
    permuted (possibly qualified by a quantifier).  This addresses the
    use case for many password requirements, such as, "at least 6
    characters where 2 or more are digits". This can be done so:

        [\l]{6:10}&[\d]{2}

    If a literal or a group is an operand of the permutation operator,
    it will be have its string value permuted with the other operand.

        foo&bar

    will produce strings like: 

        orbfao
    
    Implicit Concatenation 
    ---------------------- 
    Classes, literals and groups in sequence are concatenated, but
    beware that the permutation operator ('&') will greedily consume
    the sequence of nodes on either side unless parenthenses are used.

        [\d]{8}xxx&yyy

    produces something like: 

         x44132x094xyyy

    but

        [\d]{8}(xxx&yyy)

    Keeps all the digits at the front, which may be the intention:

        98762269xxyyyx

    Special Characters, Escaping and Errors
    ---------------------------------------
    There are fewer special characters than regular expressions: 

        [](){}|&-

    They can be used as literals by escaping with backslash. All other
    characters are treated as literals.  The hyphen is only special in
    a character class, when it appears within square brackets. The
    parser may do unexpected things if errors are made, usually in
    favour of laxness, passing over errors silently, like forgetting
    to close a group or class with closing brackets, having space
    between a class and quantifier.  But the result in the case of
    such an error is not likely to be what is expected or wished for.

    Characters Classes and Quantifiers
    ----------------------------------
    Use a colon in the curly braces to indicate a variable count

        [\w]       # randomly choose a single word character
        [\w]{0:8}  # generate word characters from 0-8 length 
        [\w]{:8}   # a synonym for the above
        [\w]{8}    # generate word characters of exactly 8 in length
        [a-z0-9]   # generate a-z and digits, just one as there is no quantifier
        [a-z0-9_!@]  # you can combine ranges with individual characters

    Using a character class and no quantifier will result in a quantifier of 1. 

    Here's an example of generating a syntactically valid but, hopefully, spurious email address: 

        [a-z][\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)

    The name will begin with a letter and will be from 1 - 11 chars; the last name will be 10 chars
    of lower case letters, each separated by either a dot or underscore. 
    The domain name without domain class will be 1 - 22 chars [a-zA-Z0-9_] and the domain will be
    one of '.com','.net','.org'.

    Using multiple character set codes repeatedly will increase the probability of a character
    from that set occuring in the result string: 

        [a-z\d\d\d\d]

    This will provide a string that is three times more likely to contain a digit than 
    if this were used: 

        [a-z\d]

    When using the unique=True flag, it's possible the generator cannot possibly produce the
    required number of unique strings. For instance: 

       StringGenerator("[0-1]").render_list(100,unique=True)

    This will generate an exception, but not before attempting to generate the strings. 

    The number of times the generator needs to render new strings to
    satisfy the list length and uniqueness is not determined at parse
    time. However, the maximum numer of times it will try is by
    default n * 10 where n is the requested length of the
    list. Therefore, taking the above example, the generator will
    attempt to generate the unique list of 0's and 1's 100*10 = 1000 times.

    Unicode
    -------
    Unicode is supported for both the template and output. 

    Character Sets and Locale 
    ------------------------- 
    Character sets used for backslashed character codes are exactly the
    Python character sets from the string package. Some of these are
    dependent on the locale settings. 

    Randomness Methods
    ------------------
    The generator tries to use random.SystemRandom() for randint,
    shuffle, etc. It falls back to random.randint and associated
    methods if it can't use SystemRandom.

    Design Goals
    ------------
    The module is designed with the following goals in mind:
    
    * Provide an abstract template language without too many
      dependencies on Python to enable the template language to be
      implemented in multiple languages

    * Reduce dependencies on other packages

    * Easy to implement in various languages 

    * As simple as possible while being pragmatic

    * Superficially similar to regular expressions to enable
      developers to quickly pickup the template syntax


    License
    -------
    Released under the BSD license. 


    Original Author: paul.wolf@yewleaf.com


    """

    meta_chars = u'[]{}()|&'
    mytab = u" "*4

    string_code = {
        u'd':string.digits,
        u'w':'_'+string.letters+string.digits,
        u'W':string.whitespace+string.punctuation,
        u's':string.whitespace,
        u'p':string.punctuation,
        u'l':string.letters,
        u'u':string.uppercase,
        u'c':string.lowercase,
        u'o':string.octdigits,
        u'h':string.hexdigits,
        u'r':string.printable,
        u'a':string.ascii_letters,
    }
    string_code_help = {
        u'd':u'digits',
        u'w':u'\'_\' + letters + digits',
        u'W':u'whitespace + punctuation',
        u's':u'whitespace',
        u'p':u'punctuation',
        u'l':u'letters',
        u'u':u'uppercase',
        u'c':u'lowercase',
        u'o':u'octdigits',
        u'h':u'hexdigits',
        u'r':u'printable',
        u'a':u'ascii_letters',
    }


    class StringNode(object):
        u"""The abstract class for all nodes"""        

        def render(self):
            raise Exception(u"abstract class")

        def dump(self):
            raise Exception(u"abstract class")
        
    class Sequence():
        u""" Render a sequence of nodes from the template. """

        def __init__(self,seq):
            u"""seq is a list"""
            self.seq = seq # list of StringNodes

        def render(self):
            return u''.join([ x.render() for x in self.seq])

        def dump(self,level=-1):
            for s in self.seq:
                s.dump(level + 1)


    class SequenceOR(Sequence):
        u"""Randomly choose from operands. """

        def render(self):
            # return just one of the items in self.seq
            return self.seq[randint(0,len(self.seq)-1)].render()
        
        def dump(self,level=-1):
            print (StringGenerator.mytab*level) + u"OR"
            for s in self.seq:
                s.dump(level + 1)

    class SequenceAND(Sequence):
        u"""Render a permutation of characters from operands."""

        def render(self):
            # return a permutation of all characters in seq
            l = list(u''.join([ x.render() for x in self.seq]))
            shuffle(l)
            return u''.join(l)

        def dump(self,level=-1):
            print (StringGenerator.mytab*level) + u"AND"

            for s in self.seq:
                s.dump(level + 1)

    class Literal(StringNode):
        u""" Render a literal string. """

        def __init__(self,chars):
            self.literal = chars # a literal string

        def render(self):
            return self.literal

        def dump(self,level=0):
            print (StringGenerator.mytab*level) + self.literal

        def __unicode__(self):
            return unicode(self.literal)

        def __str__(self):
            return str(unicode(self))
                            
    class CharacterSet(StringNode):
        u""" Render a random combination from a set of characters. """

        def __init__(self,chars,start,cnt):
            self.chars = chars
            try:
                self.start = int(start)
                self.cnt = int(cnt)
            except Exception, e:
                raise e

        def render(self):
            cnt = 1
            if self.start > -1:
                cnt = randint(self.start,self.cnt)
            else:
                cnt = self.cnt
            return u''.join(self.chars[randint(0,len(self.chars)-1)] for x in range(cnt))

        def dump(self,level=0):
            print StringGenerator.mytab*level+unicode(self)

        def __unicode__(self):
            return u'%s:%s:%s'%(self.start,self.cnt,self.chars)

    def __init__(self,pattern,uaf=10):
        self.pattern = unicode(pattern)
        self.seq = None
        self.index = -1
        self.unique_attempts_factor = uaf

    def current(self):
        if self.index < len(self.pattern):
            return self.pattern[self.index]
        return None

    def next(self):
        self.index += 1
        return self.current()

    def lookahead(self):
        if self.index+1 < len(self.pattern):
            return self.pattern[self.index+1]
        return None

    def last(self):
        if self.index == 0:
            return None
        self.pattern[self.index-1]

    def getQuantifier(self):
        start = -1
        cnt = 1
        bracket = self.next()
        # we should only be here because that was a bracket
        if not bracket  == u'{':
            raise Exception(u"parse error getting count")
        d = u''
        digits = u'0'
        while True:
            d = self.next()
            if not d:
                raise Exception(u"unexpected end of input getting count")
            if d == u':':
                start = int(digits)
                digits = u'0'
                continue
            if d == u'}':
                break
            if d.isnumeric():
                digits += d
            else:
                raise Exception(u"non-digit in count")
        return [start,int(digits)]

    def getCharacterRange(self,f,t):
        chars = u''
        # support z-a as a range
        if not ord(f) < ord(t):
            tmp = f
            f = t
            t = tmp
        if (ord(t) - ord(f)) > 10000: # protect against large sets ?
            raise Exception(u"character range too large: %s - %s: %s"(f,t,ord(t)-ord(f)))
        for c in range(ord(f),ord(t)+1):
            chars += unichr(c)
        return chars


    def getCharacterSet(self):
        # index on [
        chars = u''
        c = None
        cnt = 1
        start = 0
        while True:
            c = self.next()
            if self.lookahead() == u'-':
                f = c
                self.next() # skip hyphen
                c = self.next() # get far range
                if not c or (c in self.meta_chars):
                    raise Exception(u"unexpected end of class range")
                chars += self.getCharacterRange(f,c)
            elif c == u'\\':
                if self.lookahead() in self.meta_chars:
                    c = self.next()
                    chars += c
                elif self.lookahead() in self.string_code:
                    c = self.next()
                    chars += self.string_code[c]
            elif c and c not in self.meta_chars:
                chars += c
                
            if c == u']':
                if self.lookahead() == u'{':
                    [start,cnt] = self.getQuantifier()
                else:
                    start = -1
                    cnt = 1
                break
            if not c:
                break

        return StringGenerator.CharacterSet(chars,start,cnt)

    def getLiteral(self):
        u""" Get a sequence of non-special characters"""

        # we are on the first non-special character
        chars = u''
        c = self.current()
        while True:
            if c and c == u"\\":
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


    def getSequence(self):
        u"""Get a sequence of nodes."""

        seq = []
        op = ''
        operand_count = 0
        while True:
            c = self.next()
            if not c:
                break
            if c and c not in self.meta_chars:
                seq.append(self.getLiteral())
                operand_count += 1
            elif c == u'[' and not self.last() == u'\\':
                seq.append(self.getCharacterSet())
                operand_count += 1
            elif c == u'(' and not self.last() == u'\\':
                seq.append(self.getSequence())
                operand_count += 1
            elif c == u')' and not self.last() == u'\\':
                # we never get here because it's eaten by getSquence()
                # unless there are unbalanced parens
                #raise Exception("unbalanced parens")
                pass
            elif c == u'|' and not self.last() == u'\\':
                op = c
                operand_count += 1
            elif c == u'&' and not self.last() == u'\\':
                op = c
                operand_count += 1
            else:
                pass

            #print op,operand_count,len(seq)
            if op and len(seq) > 1 and operand_count > 1:
                # take last two seq entries and create a single entry
                right_operand = seq.pop()
                left_operand = seq.pop()
                #print "popped: [%s] %s:%s"%( op, left_operand, right_operand)
                if op == u'|':
                    seq.append(StringGenerator.SequenceOR([right_operand,left_operand]))
                elif op == u'&':
                    seq.append(StringGenerator.SequenceAND([right_operand,left_operand]))
                operand_count = 0
                op = u''

        return StringGenerator.Sequence(seq)

    def render(self):
        u"""Produce a randomized string that fits the template/pattern."""
        if not self.pattern:
            raise Exception(u"No pattern specified")
        if not self.seq:
            self.seq = self.getSequence()
        return self.seq.render()

    def dump(self):
        u"""Print the parse tree and then call render for an example."""
        if not self.seq:
            self.seq = self.getSequence()
        self.seq.dump()
        return self.render()


    def render_list(self,cnt,unique=False):
        u"""Return a list of generated strings.

        Arguments
            cnt: length of list
            unique: whether to make entries unique

        We keep track of total attempts because a template may
        specify something impossible to attain, like [1-9]{} with cnt==1000

        """
        rendered_list = []
        i = 0
        total_attempts = 0
        while True:
            if i >= cnt:
                break
            if total_attempts > cnt*self.unique_attempts_factor:
                raise Exception(u"couldn't satisfy uniqueness")
            s = self.render()
            if unique:
                if not s in rendered_list:
                    rendered_list.append(s)
                    i += 1
            else:
                rendered_list.append(s)
                i += 1
            total_attempts += 1
        return rendered_list

    @staticmethod
    def tests():
        u"""Run tests"""

        test_list = [
            u"[a-z][\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)",
            u"[a-z\d\d\d\d]{8}",
            u"[\l]{6:10}&[\d]{2}",
            u"([a-z]{4}|[0-9]{9})",
            u"[\d]&[\c]&[\w\p]{6}",
            u'idzie wąż wąską dróżką',
            u'[ą-ż]{8}',
            u'\xe6\xbf\xe5, \xe9\xe5\xa9\xe5\xe5\xad\xe6\xaf\xe7\xe9\xba\xbc\xe6\xe6',
            ]
        for t in test_list:
            print u"%s == %s"%(t,StringGenerator(t).render())
        return 
