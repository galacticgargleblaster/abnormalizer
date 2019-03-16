# -*- coding: utf-8 -*-

"""Main module."""


from .parser import BaseParser
from .lexer import FTLexer
from .formatter import NormeFormatter
import pygments
from io import StringIO

def normalized(filename):
    with open(filename, 'r') as f:
        raw = f.read()
    tokens = pygments.lex(raw, FTLexer())
    fmt = NormeFormatter()
    output = StringIO("") 
    fmt.format(tokens, output)
    return output
