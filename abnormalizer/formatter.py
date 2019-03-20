from pygments.formatter import Formatter
from pygments.token import Token as PT 
from . import logger, MAX_LINE_LENGTH, MAX_FUNCTIONS_PER_FILE, FormatSpec, printed_length
from .token import Token, TokenLike
from .parser import grouped_by_language_feature
from .language import LanguageFeature, PreProcessorDirective, StructureLike, FunctionDefinition, GlobalScopeContributor, StructureBase, FunctionPrototype
from collections import namedtuple
from typing import List
import logging
import os 
import sys

SPECIAL = \
"""/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   turns_out_this_does_not_matter.h                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: student <student@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 1967/08/25 00:00:00 by student           #+#    #+#             */
/*   Updated: 4242/42/42 66:66:66 by studnet          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */"""

MAX_COMMENT_LINE_LEN = MAX_LINE_LENGTH - len("**    ")

def format_block_comment(value: str) -> str:
    """ naively wraps lines and removes extra ** """
    input_lines = value.split("\n")
    wrapped_lines = []
    for line in input_lines:
        while printed_length(line) > MAX_LINE_LENGTH:
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
            if token.ttype == PT.Comment.Multiline:
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

        self.spec.user_defined_type_names = [t \
                                            for s in globs if isinstance(s, StructureBase) \
                                            for t in s.user_defined_types]
        self.spec.user_defined_type_names = set(self.spec.user_defined_type_names)

        self.spec.global_scope_n_chars = max([c.minimum_global_scope_indentation(self.spec)
                                                for c in globs if isinstance(c, GlobalScopeContributor)])
        if self.spec.global_scope_n_chars % 4:
            self.spec.global_scope_n_chars += (4 - (self.spec.global_scope_n_chars % 4))

        for idx, glob in enumerate(globs):
            formatted_glob = ""
            if (glob.ttype == PT.Comment.Special):
                formatted_glob = SPECIAL
            elif (isinstance(glob, PreProcessorDirective)):
                if "#endif" in glob.value:
                    self.spec.define_depth_n_spaces -= 1
                formatted_glob = glob.formatted(self.spec)
                if "#if" in glob.value:
                    self.spec.define_depth_n_spaces += 1
            elif (isinstance(glob, LanguageFeature)):
                formatted_glob = glob.formatted(self.spec)
            else:
                formatted_glob = glob.value
            
            if any(printed_length(line) > MAX_LINE_LENGTH for line in formatted_glob.split("\n")):
                logger.warning("variable names are too long to be formatted correctly")
            outfile.write(formatted_glob)
            if any([isinstance(glob, relevant_type) and idx + 1 < len(globs) and isinstance(globs[idx + 1], relevant_type)\
                    for relevant_type in [PreProcessorDirective, FunctionPrototype]]):
                pass
            elif idx == len(globs) - 1:
                pass
            else:
                outfile.write('\n')
            outfile.write('\n')
