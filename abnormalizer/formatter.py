from pygments.formatter import Formatter
from pygments.token import Token as PygmentsToken
from . import Token, TokenLike, logger
from .parser import glob_tokens, PreProcessorDirective
from collections import namedtuple
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
/*   Created: 1666/06/06 66:66:66 by student           #+#    #+#             */
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

    # def get_global_scope(self, tokens) -> int:
    #     global_scope = 0
    #     (PygmentsToken.Keyword, "typedef"), GreedyAnything, (PygmentsToken.Name)
    #     (PygmentsToken.Keyword, "struct"), GreedyAnything, (PygmentsToken.Name)
    #     (PygmentsToken.Name || PygmentsToken.Keyword.Type), GreedyAnything, (PygmentsToken.Name)


    def mutate_tokens(self, tokensource):
        """ mutates the tokensource and maybe updates global scope? """
        tokensource = list(tokensource)
        tokens = [Token(ttype=ttype, value=value) for ttype, value in tokensource]
        clean_tokens = []
        for idx, token in enumerate(tokens):
            logger.info(token)
            token.remove_trailing_whitespace()
            if token.ttype == PygmentsToken.Comment.Multiline:
                token.value = format_block_comment(token.value)

            if (token.value == '\n' and  token.ttype == PygmentsToken.Text and idx > 0 \
                and tokens[idx-1].value == '\n' and tokens[idx-1].ttype == PygmentsToken.Text):
                logger.info(f"trimming newline at token idx {idx}, because the previous token was also a newline.")
                logger.info(f'previous: {tokens[idx-1]}')
                logger.info(f'current: {tokens[idx]}')
            else:
                clean_tokens.append(token)
        return clean_tokens

    def format(self, tokensource, outfile):
        tokens = self.mutate_tokens(tokensource)
        globs = glob_tokens(tokens)

        for token in tokens:
            if (token.ttype == PygmentsToken.Comment.Special):
                outfile.write(SPECIAL)
                continue
            elif (isinstance(token, PreProcessorDirective)):
                outfile.write(token.formatted(self.preprocessor_define_depth))
                if "#if" in token.value:
                    self.preprocessor_define_depth += 1
                elif "#endif" in token.value:
                    self.preprocessor_define_depth -= 1
                continue
            outfile.write(token.value)
