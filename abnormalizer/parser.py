# -*- coding: utf-8 -*-

"""Main module."""

class BaseParser():
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.raw = f.read()

class HeaderFileParser(BaseParser):
    pass

class SourceFileParser(BaseParser):
    pass

class FileParser():
    def __new__(cls, filename):
        if filename.endswith(".h"):
            return HeaderFileParser(filename)
        elif filename.endswith(".c"):
            return SourceFileParser(filename)
        else:
            raise IOError("invalid file extension")

