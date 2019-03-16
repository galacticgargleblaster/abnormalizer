# -*- coding: utf-8 -*-

"""Console script for abnormalizer."""
import sys
import click
from .abnormalizer import normalized 


@click.command()
@click.argument("filename")
@click.option("--dry_run", default=1, help="Don't overwrite the file, print the output to stdout")
def main(filename, dry_run):
    """Console script for abnormalizer."""
    output = normalized(filename)
    output.seek(0)
    if (dry_run):
        sys.stdout.write(output.read())
    else:
        with open(filename, "w") as f:
            f.write(output.read())
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
