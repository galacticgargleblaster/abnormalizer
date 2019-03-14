# -*- coding: utf-8 -*-

"""Console script for abnormalizer."""
import sys
import click
from abnormalizer import FileParser


@click.command()
@click.argument("filename")
def main(filename):
    """Console script for abnormalizer."""
    FileParser(filename)
    import ipdb; ipdb.set_trace()
    click.echo(filename)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
