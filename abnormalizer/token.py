from typing import List
from . import logger

class TokenLike(object):
    ttype = None
    value = None

class Token(TokenLike):
    def __init__(self, ttype, value):
        self.ttype = ttype
        self.value = value

    def remove_trailing_whitespace(self) -> None:
        if "\n" in self.value and len(self.value) > 1:
            logger.info(f"removing trailing whitespace from {self.ttype}")
            logger.info(f"before: `{self}`")
            self.value = "\n".join([line.rstrip() for line in self.value.split("\n")])
            logger.info(f"after: `{self}`")
    
    def strip(self) -> str:
        self.value = self.value.strip()
        return self.value

    def __str__(self):
        """ for analysis purposes """
        value = self.value
        value = value.replace('\t', '⇥⇥⇥⇥')
        value = value.replace('\n', '␤\n')
        value = value.replace(' ', '⍽')
        return f"{self.ttype}: `{value}`"


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
        try:
            if punctuation in tokens[idx].value:
                first = idx
            else:
                idx += 1
        except IndexError:
            import ipdb; ipdb.set_trace()
    while last is None:
        if punctuation in tokens[idx].value:
            sum += 1
        if closure in tokens[idx].value:
            sum -= 1
        if (sum == 0):
            last = idx + 1
        idx += 1
    return (first, last)