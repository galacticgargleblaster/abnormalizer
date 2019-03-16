from pygments.formatter import Formatter
from pygments.token import *
from collections import namedtuple
import logging
import os 

IM_SO_SORRY = \
"""/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   violation_of_best_practices.h                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: student <student@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 4242/42/42 66:66:66 by student           #+#    #+#             */
/*   Updated: 4242/42/42 66:66:66 by studnet          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */
"""

class Token(object):
    def __init__(self, ttype, value):
        self.ttype = ttype
        self.value = value

    def remove_trailing_whitespace(self) -> None:
        self.value = "\n".join([line.rstrip() for line in self.value.split("\n")])

LOGLEVEL = logging.DEBUG
log_file_path = os.path.expanduser("~/formatter_logs.txt")
logger = logging.getLogger(__name__)
filehandler = logging.FileHandler(filename=log_file_path)
filehandler.setLevel(LOGLEVEL)
logger.addHandler(filehandler)
logger.setLevel(LOGLEVEL)
logger.info("\n\n")

class NormeFormatter(Formatter):
    """
    maintains state while formatting a file
    """
    MAX_ROWSIZE = 80

    def __init__(self):
        self.preprocessor_define_depth = 0
       

    def preformat(self, tokensource):
        """ mutates the tokensource and maybe updates global scope? """
        tokensource = list(tokensource)
        tokens = [Token(ttype=ttype, value=value) for ttype, value in tokensource]
        clean_tokens = []
        for idx, token in enumerate(tokens):
            token.remove_trailing_whitespace()
            logger.info(f"{token.ttype}:\n{token.value}\n")

            if (token.value == '\n' and idx > 0 and tokens[idx-1].value == '\n'):
                logger.info(f"trimming newline at token idx {idx}")
                continue
            else:
                clean_tokens.append(token)
        return clean_tokens

    def format(self, tokensource, outfile):
        tokens = self.preformat(tokensource)
        for token in tokens:
            if (token.ttype == Comment.Special):
                outfile.write(IM_SO_SORRY)
                continue;
            outfile.write(token.value)
