# -*- coding: utf-8 -*-

"""Console script for abnormalizer."""
import sys
import click
from .abnormalizer import normalized 
import shutil


@click.command()
@click.argument("filename")
def main(filename):
    """Console script for abnormalizer."""
    if not (filename.endswith(".h") or filename.endswith(".c")):
        raise IOError("invalid file extension")
    shutil.copy(filename, f"{filename}.BAK")
    output = normalized(filename)
    output.seek(0)
    with open(filename, "w") as f:
        f.write(output.read())
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
