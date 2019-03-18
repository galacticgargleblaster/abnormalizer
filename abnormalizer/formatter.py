from pygments.formatter import Formatter
from pygments.token import Token as PygmentsToken
from . import logger, MAX_ROW_SIZE, MAX_FUNCTIONS_PER_FILE, FormatSpec
from .token import Token, TokenLike
from .parser import grouped_by_language_feature
from .language import LanguageFeature, PreProcessorDirective, StructureLike, FunctionDefinition
from collections import namedtuple
from typing import List
import logging
import os 
import sys

SPECIAL = \
"""/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   nothing_to_see_here.h                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: student <student@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 1967/08/25 00:00:00 by student           #+#    #+#             */
/*   Updated: 4242/42/42 66:66:66 by studnet          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */
"""


def vis_len(value: str) -> int:
    """ a tab usually prints as four spaces """
    return len(value) + (value.count("\t") * 3)


"""
need to do some light parsing after tokenization, need to be able to identify struct scopes, function scopes

line wrapping (depends on token type)
    - Comment.Special, insert **
    - all others, tab to global scope

space preprocesser directives

Determine global scope spacing
"""

MAX_COMMENT_LINE_LEN = MAX_ROW_SIZE - len("**    ")

def format_block_comment(value: str) -> str:
    """ naively wraps lines and removes extra ** """
    input_lines = value.split("\n")
    wrapped_lines = []
    for line in input_lines:
        while vis_len(line) > MAX_ROW_SIZE:
            wrapped_lines.append(f"{line[:MAX_COMMENT_LINE_LEN]}")
            line = f"**\t{line[MAX_COMMENT_LINE_LEN:]}"
        wrapped_lines.append(line)
    formatted_lines = []
    for lineno, line in enumerate(wrapped_lines):
        if (line.rstrip() == "**" and (lineno > 0) and \
            ((wrapped_lines[lineno - 1].rstrip() in ("**", "/*") \
                or (wrapped_lines[lineno + 1].rstrip() == "*/")))):
            pass
        else:
            formatted_lines.append(line)
    return "\n".join(formatted_lines)

class HeaderFileFormatter(object):
    """ adds include-guards """
    pass

class SourceFileFormatter(object):
    pass

class NormeFormatter(Formatter):
    """
    maintains state while formatting a file
    """

    def __init__(self):
        self.spec = FormatSpec()

    @staticmethod
    def preprocess_tokens(tokens: List[Token]):
        """
        trims whitespace from tokens and pops whitespace tokens entirely
        """
        clean_tokens = []
        for token in tokens:
            logger.info(token)
            token.remove_trailing_whitespace()
            if token.ttype == PygmentsToken.Comment.Multiline:
                token.value = format_block_comment(token.value)
            clean_tokens.append(token)
        return clean_tokens

    def format(self, tokensource, outfile):
        tokens = [Token(ttype=ttype, value=value) for ttype, value in list(tokensource)]
        tokens = self.preprocess_tokens(tokens)

        # gotta glob the preprocessor defines together before removing all whitespace
        # because preprocessor directives' syntax relies on whitespace 
        globs = grouped_by_language_feature(tokens)
        
        # all whitespace can be removed after globbing is done.
        globs = [e for e in globs if isinstance(e, LanguageFeature) or e.strip() != ''] 
        [g.remove_whitespace() for g in globs if isinstance(g, LanguageFeature)]

        n_function_defns = len([f for f in globs if isinstance(f, FunctionDefinition)])
        if n_function_defns > MAX_FUNCTIONS_PER_FILE:
            logger.warning(f"there are {n_function_defns} function definitions. (limit {MAX_FUNCTIONS_PER_FILE})")

        for token in globs:
            if (token.ttype == PygmentsToken.Comment.Special):
                outfile.write(SPECIAL)
            elif (isinstance(token, PreProcessorDirective)):
                if "#endif" in token.value:
                    self.spec.define_depth_n_spaces -= 1
                outfile.write(token.formatted(self.spec))
                if "#if" in token.value:
                    self.spec.define_depth_n_spaces += 1
            elif (isinstance(token, LanguageFeature)):
                outfile.write(token.formatted(self.spec))
            else:
                outfile.write(token.value)
            outfile.write('\n')
