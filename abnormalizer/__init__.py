# -*- coding: utf-8 -*-

"""Top-level package for abnormalizer."""

__author__ = """student"""
__email__ = 'student@42.fr'
__version__ = '0.1.0'

import logging
import os
import sys

log_file_path = os.path.expanduser("~/formatter_debug_logs.txt")
logger = logging.getLogger(__name__)

filehandler = logging.FileHandler(filename=log_file_path, mode='w')
streamhandler = logging.StreamHandler(stream=sys.stdout)
streamhandler.setLevel(logging.WARNING)
filehandler.setLevel(logging.DEBUG)
logger.addHandler(filehandler)
logger.addHandler(streamhandler)
logger.setLevel(logging.DEBUG)


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