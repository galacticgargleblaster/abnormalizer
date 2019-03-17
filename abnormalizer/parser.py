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
        return f"#{' '*indent_spaces}{' '.join([t.value for t in self.tokens[1:-1]])}\n"

class Function(TokenGlob):
    pass

class FunctionPrototype(TokenGlob):
    pass

class GlobalDeclaration(TokenGlob):
    pass

class StructureLike(TokenGlob):
    pass

def next_punctuation(tokens: List[Token]) -> (str):
    for token in tokens:
        try:
            p = next((p for p in ";({" if p in token.value)) 
            return p
        except StopIteration:
            pass
    return None

def distance_to_next_token_containing(tokens, start, substring):
    try:
        return next(\
            (end - start for end in range(start, len(tokens))\
                if substring in tokens[end].value))
    except StopIteration:
        return None

def find_range_of_tokens_within_scope(tokens, start_index: int, punctuation: str):
    """
    finds next token matching punctuation, "first", then finds the closing punctuation "last".
    :return: inclusive range
    """
    closure = {"{": "}", "(": ")"}[punctuation]
    idx = start_index
    sum = 0
    first = None
    last = None
    while first is None:
        if punctuation in tokens[idx].value:
            first = idx
        else:
            idx += 1
    while last is None:
        if punctuation in tokens[idx].value:
            sum += 1
        if closure in tokens[idx].value:
            sum -= 1
        if (sum == 0):
            last = idx + 1
        idx += 1
    return (first, last)

class ScopedThing(TokenGlob):
    """
    Could be either a function, function prototype, structure.  
    All will start at a new line, meaning the preceeding token ends with a '\n'

    FUNCTION PROTOTYPE (functions don't get called at global scope)
    asdf hjkl(type asdf);

    FUNCTION DEFINITION
    asdf jkll(){}

    STRUCT-LIKE
    asdf jklk{};

    GLOBAL
    asdf asdfj;
    assdf asdf[];
    """
    @staticmethod
    def consume(tokens):
        idx = 0
        while (idx < len(tokens)):
            token = tokens[idx]
            if (tokens[idx - 1].value.endswith('\n')):
                if token.ttype in [PT.Name, PT.Keyword, PT.Keyword.Type]:
                    p = next_punctuation(tokens[idx:])
                    if p:
                        if p == '(':
                            open_p, close_p = find_range_of_tokens_within_scope(tokens, idx, '(')
                            if tokens[close_p + 1].value == ';':
                                tokens[idx: close_p + 2] = [FunctionPrototype(tokens[idx: close_p + 2])]
                            else:
                                tokens[idx: close_p + 1] = [Function(tokens[idx: close_p + 1])]
                        if p == '{':
                            open_b, close_b = find_range_of_tokens_within_scope(tokens, idx, '{')
                            try:
                                tokens[idx: close_b + 1] = [StructureLike(tokens[idx: close_b + 1])]
                            except TypeError:
                                import ipdb; ipdb.set_trace()
                        if p == ';':
                            length = distance_to_next_token_containing(tokens, idx, ';') 
                            tokens[idx: length + 1] = [GlobalDeclaration(tokens[idx: idx + length + 1])]
            idx += 1
        return tokens



def glob_tokens(tokens: List[Token]) -> List[TokenLike]:
    globbed_tokens = PreProcessorDirective.consume(tokens)
    globbed_tokens = ScopedThing.consume(tokens)
    return globbed_tokens
    hmm = [g for g in globbed_tokens if isinstance(g, PreProcessorDirective)]
    import ipdb; ipdb.set_trace()
