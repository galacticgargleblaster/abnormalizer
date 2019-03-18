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
streamhandler.setLevel(logging.WARNING)
filehandler.setLevel(logging.DEBUG)
logger.addHandler(filehandler)
logger.addHandler(streamhandler)
logger.setLevel(logging.DEBUG)


MAX_ROW_SIZE = 80
MAX_FUNCTIONS_PER_FILE = 5

class FormatSpec(object):
    global_scope_n_chars = 0
    define_depth_n_spaces = 0

