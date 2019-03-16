# -*- coding: utf-8 -*-

from typing import List
from abc import abstractmethod
from . import TokenLike

"""
rather, parser lite
not constructing a full AST, just globbing tokens together into "structure" or "function" objects
"""

from pygments.token import Token as PT
from . import Token

class TokenGlob(TokenLike):
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
    
    @abstractmethod
    def formatted(self):
        pass

    @property
    def value(self):
        return "".join([t.value for t in self.tokens])

class PreProcessorDirective(TokenGlob):
    @staticmethod
    def consume(tokens):
        """  This modifies the list in-place and is therefore considered dubious by some """
        capturing = False
        idx = 0
        while (idx < len(tokens)):
            token = tokens[idx]
            if not capturing and \
                token.ttype == PT.Comment.Preproc and \
                    token.value == '#':
                capturing = True
                start = idx
            elif capturing and token.value == '\n':
                tokens[start: idx + 1] = [PreProcessorDirective(tokens[start:idx + 1])]
                capturing = False
                idx = start
            idx += 1
        return tokens

    def formatted(self, indent_spaces: int) -> str:
        self.tokens[1].value = self.tokens[1].value.lstrip()
        import ipdb; ipdb.set_trace()
        return f"#{' '*indent_spaces}{' '.join([t.value for t in self.tokens[1:-1]])}\n"

def find_range_of_tokens_within_scope(tokens, start_index: int, punctuation: str):
    closure = {"{": "}", "(": ")"}[punctuation]
    idx = start_index
    sum = 0
    first = None
    last = None
    while not (first and last):
        if not first and punctuation in tokens[idx].value:
            first = idx
        if punctuation in tokens[idx].value:
            sum += 1
        if closure in tokens[idx].value:
            sum -= 1
        if (sum == 0):
            last = idx
        idx += 1
    return (first, last)

class Function(TokenGlob):
    @staticmethod
    def consume(tokens):
        capturing = False
        idx = 0
        while (idx < len(tokens)):
            token = tokens[idx]
            if not capturing and \
                token.ttype == PT.Name and \
                    token.value == '#':
                capturing = True
                start = idx
            elif capturing and token.value == '\n':
                tokens[start: idx + 1] = [PreProcessorDirective(tokens[start:idx + 1])]
                capturing = False
                idx = start
            idx += 1
        return tokens

class FunctionPrototype(TokenGlob):
    pass

class Structure(TokenGlob):
    pass

class TypedefStructure(TokenGlob):
    pass

def glob_tokens(tokens: List[Token]) -> List[TokenLike]:
    globbed_tokens = PreProcessorDirective.consume(tokens)
    return globbed_tokens
    hmm = [g for g in globbed_tokens if isinstance(g, PreProcessorDirective)]
    import ipdb; ipdb.set_trace()
