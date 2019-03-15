from pygments.formatter import Formatter
from pygments.token import *


class NormeFormatter(Formatter):
    MAX_ROWSIZE = 80

    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            outfile.write(value)
