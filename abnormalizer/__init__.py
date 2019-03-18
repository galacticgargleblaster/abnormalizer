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
streamhandler = logging.StreamHandler(stream=sys.stderr)
streamformatter = logging.Formatter('%(levelname)s: %(message)s')
streamhandler.setFormatter(streamformatter)
streamhandler.setLevel(logging.WARNING)
filehandler.setLevel(logging.DEBUG)
logger.addHandler(filehandler)
logger.addHandler(streamhandler)
logger.setLevel(logging.DEBUG)


MAX_ROW_SIZE = 80
MAX_FUNCTIONS_PER_FILE = 5

def tabs_needed_to_pad_to_scope(line_length: int, scope: int) -> int:
    assert line_length <= scope
    diff = scope - line_length
    if diff:
        return 1 + int(diff / 4)
    return 0


class FormatSpec(object):
    """
    A container class for state that's specific to the file being formatted
    """

    def __init__(self):
        self.global_scope_n_chars = 0
        self.define_depth_n_spaces = 0
        self.mangled_names_mapping = {}
        self.user_defined_type_names = []

    def tabs_needed_to_pad_to_global_scope(self, line_length: int):
        return tabs_needed_to_pad_to_scope(line_length, self.global_scope_n_chars)


