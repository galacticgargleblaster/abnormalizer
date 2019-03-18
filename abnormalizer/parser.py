# -*- coding: utf-8 -*-

from typing import List
from abc import abstractmethod
from . import TokenLike

"""
rather, parser lite
not constructing an AST, just globbing tokens together into "structure" or "function" objects.

These objects need to exist so that we can make assertions like: 
"header file has include guards"
"struct name is prefixed with s_"

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

    def remove_whitespace(self):
        [t.strip() for t in self.tokens]
        self.tokens = [t for t in self.tokens if t.value]

class PreProcessorDirective(TokenGlob):
    def formatted(self, indent_spaces: int) -> str:
        self.tokens[1].value = self.tokens[1].value.lstrip()
        return f"#{' '*indent_spaces}{' '.join([t.value for t in self.tokens[1:]])}"
    

class Function(TokenGlob):
    pass

class FunctionPrototype(TokenGlob):
    pass

class FunctionCall(TokenGlob):
    pass

class GlobalDeclaration(TokenGlob):
    pass

class StructureLike(TokenGlob):
    def formatted(self, global_scope_n_tabs):
        return self.value

def next_punctuation(tokens: List[Token]) -> (int, str):
    """ 
    (int, str)
    (index of punctuation token, string that was matched )
    """
    for idx, token in enumerate(tokens):
        try:
            p = next((p for p in ";({" if p in token.value)) 
            return (idx, p)
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
def consume(tokens):
    idx = 0
    while (idx < len(tokens)):
        token = tokens[idx]
        if token.ttype in [PT.Name, PT.Keyword, PT.Keyword.Type]:
            p_idx, p = next_punctuation(tokens[idx:])
            if p:
                if p == '(':
                    # Could be function (prototype|definition)
                    open_p, close_p = find_range_of_tokens_within_scope(tokens, idx, '(')
                    if tokens[close_p + 1].value == ';':
                        end = close_p + 2  # include the semicolon
                        tokens[idx: end] = [FunctionPrototype(tokens[idx: end])]
                    else:  # It's a function definition
                        open_b, close_b = find_range_of_tokens_within_scope(tokens, close_p, '{')
                        end = close_b + 1
                        tokens[idx: end] = [Function(tokens[idx: end])]
                if p == '{':
                    open_b, close_b = find_range_of_tokens_within_scope(tokens, idx, '{')
                    distance_to_semicolon = distance_to_next_token_containing(tokens, close_b, ';')
                    end = close_b + distance_to_semicolon + 1
                    tokens[idx: end] = [StructureLike(tokens[idx: end])]
                if p == ';':
                    length = distance_to_next_token_containing(tokens, idx, ';') 
                    end = idx + length + 1
                    tokens[idx: end] = [GlobalDeclaration(tokens[idx: end])]
        elif token.ttype == PT.Comment.Preproc and token.value == '#':
            length = distance_to_next_token_containing(tokens, idx, '\n')
            end = idx + length + 1
            tokens[idx: end] = [PreProcessorDirective(tokens[idx: end])]
        idx += 1
    return tokens



def glob_tokens(tokens: List[Token]) -> List[TokenLike]:
    globbed_tokens = consume(tokens)
    return globbed_tokens
    hmm = [g for g in globbed_tokens if isinstance(g, PreProcessorDirective)]
    import ipdb; ipdb.set_trace()
    
