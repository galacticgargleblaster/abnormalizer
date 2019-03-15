# -*- coding: utf-8 -*-

"""Main module."""

from pygments.lexers.c_cpp import CLexer
from pygments.lexer import RegexLexer
from pygments.token import *
import pygments
import copy

INCOMPLETE_HEADER_REGEX = r'(\/\*\n)(\*{2}.*?[^ ]*\n)'


class FTLexer(CLexer):
    tokens = copy.deepcopy(CLexer.tokens)
    # Add an extra token regext to pick out the obstreperous FT header
    tokens['whitespace'].insert(8, (r'(/(\\\n)?[*][\w\W]*?[*]/\n){11}', Comment.Special))