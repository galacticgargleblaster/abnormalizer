from pygments.formatter import Formatter
from pygments.token import Token as PygmentsToken
from . import Token, TokenLike, logger
from .parser import glob_tokens, PreProcessorDirective, Function, FunctionPrototype, StructureLike, GlobalDeclaration, TokenGlob
from collections import namedtuple
from typing import List
import logging
import os 
import sys

SPECIAL = \
"""/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   violation_of_best_practices.h                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: student <student@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 1967/08/25 00:00:00 by student           #+#    #+#             */
/*   Updated: 4242/42/42 66:66:66 by studnet          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */
"""

MAX_ROWSIZE = 80

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

MAX_COMMENT_LINE_LEN = MAX_ROWSIZE - len("**    ")

def format_block_comment(value: str) -> str:
    """ naively wraps lines and removes extra ** """
    input_lines = value.split("\n")
    wrapped_lines = []
    for line in input_lines:
        while vis_len(line) > MAX_ROWSIZE:
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

class NormeFormatter(Formatter):
    """
    maintains state while formatting a file
    """

    def __init__(self):
        self.preprocessor_define_depth = 0
        self.global_scope_n_tabs = 0

    @staticmethod
    def preprocess_tokens(tokens: List[Token]):
        """
        trims whitespace from tokens and pops whitespace tokens entirely
        """
        clean_tokens = []
        for idx, token in enumerate(tokens):
            logger.info(token)
            token.remove_trailing_whitespace()
            if token.ttype == PygmentsToken.Comment.Multiline:
                token.value = format_block_comment(token.value)
            clean_tokens.append(token)
        return clean_tokens

    

    @staticmethod
    def remove_whitespace_tokens(globs: List[TokenLike]):
        for entity in globs:
            import ipdb; ipdb.set_trace()
            if isinstance(entity, TokenGlob):
                [t.strip() for t in entity.tokens]
                entity.remove_empty_tokens()
            else:
                entity.strip()
                if entity.value == '':
                    globs.remove(entity)
        return globs

    def format(self, tokensource, outfile):
        tokens = [Token(ttype=ttype, value=value) for ttype, value in list(tokensource)]
        tokens = self.preprocess_tokens(tokens)
        globs = glob_tokens(tokens)  # gotta glob the preprocessor defines together before removing all whitespace
        # all whitespace can be removed after globbing is done.

        print(f"went from {len(globs)}")
        globs = [e for e in globs if isinstance(e, TokenGlob) or e.strip() != ''] 
        print(f"to {len(globs)} by trimming whitespace")

        for token in globs:
            if (token.ttype == PygmentsToken.Comment.Special):
                outfile.write(SPECIAL)
            elif (isinstance(token, PreProcessorDirective)):
                outfile.write(token.formatted(self.preprocessor_define_depth))
                if "#if" in token.value:
                    self.preprocessor_define_depth += 1
                elif "#endif" in token.value:
                    self.preprocessor_define_depth -= 1
            elif (isinstance(token, StructureLike)):
                outfile.write(token.formatted(self.global_scope_n_tabs))
            else:
                outfile.write(token.value)
