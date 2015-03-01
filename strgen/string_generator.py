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

Original author: paul.wolf@yewleaf.com

"""
import random
import string

__version__ = '0.1.5'
__author__ = 'Paul Wolf'
__license__ = 'BSD'
#__all__ = ['StringGenerator', '']

try:
    # try to use cryptographically strong methods
    sr = random.SystemRandom()
    randint = sr.randint
    choice = sr.choice
    sample = sr.sample
    shuffle = sr.shuffle
except Exception as e:
    #print(e)
    # fall back if necessary
    randint = random.randint
    choice = random.choice
    sample = random.sample
    shuffle = random.shuffle

# check that we have python 2 functions available if we are under 3
try:
    x = unichr(0)
except NameError:
    unichr = chr

class StringGenerator(object):
    u"""Generate a randomized string of characters using a template.

    The purpose of this class is to generate a string of characters
    according to a template.  The template language is superficially
    similar to regular expressions but fundamentally different in
    purpose.

    Usage:

       StringGenerator(<template>).render()

    or:

       StringGenerator(<template>).render_list(10,unique=True)

    The latter produces a list of 10 strings that are unique within the list.

    Example: 

       StringGenerator("[\d]{10}").render_list(10,unique=True)
        
    This generates 10 unique strings containing digits. Each will be 10 characters in length.

    """
    class SyntaxError(Exception):
        pass


    meta_chars = u'[]{}()|&$'
    mytab = u" "*4

    string_code = {
        u'd':string.digits,
        u'w':'_'+string.ascii_letters+string.digits,
        u'W':string.whitespace+string.punctuation,
        u's':string.whitespace,
        u'p':string.punctuation,
        u'l':string.ascii_letters,
        u'u':string.ascii_uppercase,
        u'c':string.ascii_lowercase,
        u'o':string.octdigits,
        u'h':string.hexdigits,
        u'r':string.printable,
        #u'a':string.ascii_letters,
    }
    string_code_help = {
        u'd':u'digits',
        u'w':u"_" + 'ascii_letters + digits',
        u'W':u'whitespace + punctuation',
        u's':u'whitespace',
        u'p':u'punctuation',
        u'l':u'ascii_letters',
        u'u':u'ascii_uppercase',
        u'c':u'ascii_lowercase',
        u'o':u'octdigits',
        u'h':u'hexdigits',
        u'r':u'printable',
        #u'a':u'ascii_letters',
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
            print((StringGenerator.mytab*level) + u"sequence:")
            for s in self.seq:
                s.dump(level + 1)


    class SequenceOR(Sequence):
        u"""Randomly choose from operands. """

        def render(self):
            # return just one of the items in self.seq
            return self.seq[randint(0,len(self.seq)-1)].render()
        
        def dump(self,level=-1):
            print( (StringGenerator.mytab*level) + u"OR" )
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
            print( (StringGenerator.mytab*level) + u"AND" )

            for s in self.seq:
                s.dump(level + 1)

    class Literal(StringNode):
        u""" Render a literal string. """

        def __init__(self,chars):
            self.literal = chars # a literal string

        def render(self):
            return self.literal

        def dump(self,level=0):
            print( (StringGenerator.mytab*level) + self.literal )

        def __unicode__(self):
            return self.literal

        def __str__(self):
            return str(self)
                            
    class CharacterSet(StringNode):
        u""" Render a random combination from a set of characters. """

        def __init__(self,chars,start,cnt):
            self.chars = chars
            try:
                self.start = int(start)
                self.cnt = int(cnt)
            except Exception as e:
                raise e

        def render(self):
            cnt = 1
            if self.start > -1:
                cnt = randint(self.start,self.cnt)
            else:
                cnt = self.cnt
            return u''.join(self.chars[randint(0,len(self.chars)-1)] for x in range(cnt))

        def dump(self,level=0):
            print( StringGenerator.mytab*level+str(self) )

        def __unicode__(self):
            return u'%s:%s:%s'%(self.start,self.cnt,self.chars)

        def __str__(self):
            return '%s:%s:%s'%(self.start,self.cnt,self.chars)

    def __init__(self,pattern,uaf=10):
        try:
            self.pattern = unicode(pattern)            
        except NameError:
            self.pattern = pattern
        self.seq = None
        self.index = -1
        self.unique_attempts_factor = uaf
        self.seq = self.getSequence()

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
                raise StringGenerator.SyntaxError(u"non-digit in count")
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
                    raise StringGenerator.SyntaxError(u"unexpected end of class range")
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
            if c in self.meta_chars and not self.last() == u"\\":
                raise StringGenerator.SyntaxError(u"Un-escaped character in class definition: %s"%c)
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


    def getSequence(self,level=0):
        u"""Get a sequence of nodes."""

        seq = []
        op = ''
        left_operand = None
        right_operand = None
        sequence_closed = False
        while True:
            c = self.next()
            if not c:
                break
            if c and c not in self.meta_chars:
                seq.append(self.getLiteral())
            elif c == u'[' and not self.last() == u'\\':
                seq.append(self.getCharacterSet())
            elif c == u'(' and not self.last() == u'\\':
                seq.append(self.getSequence(level+1))
            elif c == u')' and not self.last() == u'\\':
                # end of this sequence
                if level == 0:
                    # there should be no parens here
                    raise StringGenerator.SyntaxError(u"Extra closing parenthesis")
                sequence_closed = True
                break
            elif c == u'|' and not self.last() == u'\\':
                op = c
            elif c == u'&' and not self.last() == u'\\':
                op = c
            else:
                if c in self.meta_chars and not self.last() == u"\\":
                    raise StringGenerator.SyntaxError(u"Un-escaped special character: %s"%c)

            #print( op,len(seq) )
            if op and not left_operand:
                if not seq or len(seq) < 1:
                    raise StringGenerator.SyntaxError(u"Operator: %s with no left operand"%op)
                left_operand = seq.pop()
            elif op and len(seq) >= 1 and left_operand:
                right_operand = seq.pop()

                #print( "popped: [%s] %s:%s"%( op, left_operand, right_operand) )
                if op == u'|':
                    seq.append(StringGenerator.SequenceOR([left_operand,right_operand]))
                elif op == u'&':
                    seq.append(StringGenerator.SequenceAND([left_operand,right_operand]))

                op = u''
                left_operand = None
                right_operand = None

        # check for syntax errors
        if op:
            raise StringGenerator.SyntaxError(u"Operator: %s with no right operand"%op)
        if level > 0 and not sequence_closed:
            # it means we are finishing a non-first-level sequence without closing parens
            raise StringGenerator.SyntaxError(u"Missing closing parenthesis")

        return StringGenerator.Sequence(seq)

    def render(self):
        u"""Produce a randomized string that fits the template/pattern.

        Args:
            None

        Returns:
            unicode. The generated string.

        """
        #if not self.pattern:
        #    raise Exception(u"No pattern specified")
        #if not self.seq:
        #    # parse the template
        #    self.seq = self.getSequence()
        return self.seq.render()

    def dump(self):
        import sys
        u"""Print the parse tree and then call render for an example."""
        if not self.seq:
            self.seq = self.getSequence()
        print("StringGenerator version: %s"%(__version__))
        print("Python version: %s"%sys.version)
        print("Random method provider class: %s"%randint.im_class.__name__)
        self.seq.dump()
        return self.render()


    def render_list(self,cnt,unique=False):
        u"""Return a list of generated strings.

        Args:
            cnt (int): length of list
            unique (bool): whether to make entries unique

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

        print("random method provider class: %s"%randint.im_class.__name__)

        for t in test_list:
            print(u"%s == %s"%(t,StringGenerator(t).render()))

        return 
