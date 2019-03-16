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

class TokenGlob(object):
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
    
    def capture(format):
        for element in format:
            element.match

    @abstractmethod
    def formatted(self):
        pass

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
        return f"#{' '*indent_spaces}{' '.join([t.value for t in self.tokens[1:-1]])}\n"

class Function(TokenGlob):
    pass
    # for idx, token in enumerate(tokens):
    #     if token.ttype == PT.Name.Function:
    #         for lookback, prev_token in enumerate(tokens[:idx][::-1]):
    #             if prev_token.ttype == PT.Text and prev_token.value == '\n':
    #                 start_idx = idx - lookback

class FunctionPrototype(TokenGlob):
    pass

class Structure(TokenGlob):
    pass

class TypedefStructure(TokenGlob):
    pass

def glob_tokens(tokens: List[Token]) -> List[TokenLike]:
    globbed_tokens = PreProcessorDirective.consume(tokens)
    hmm = [g for g in globbed_tokens if isinstance(g, PreProcessorDirective)]
    import ipdb; ipdb.set_trace()
