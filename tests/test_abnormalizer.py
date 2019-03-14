#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `abnormalizer` package."""


import unittest
from click.testing import CliRunner

from abnormalizer import abnormalizer
from abnormalizer import cli

import os
HERE = os.path.dirname(os.path.abspath(__file__))

TEST_FILE_DIR = 'test_files'
ABNORMAL_LIBLIST = os.path.join(HERE, TEST_FILE_DIR, "liblist.h")

class TestAbnormalizer(unittest.TestCase):
    """Tests for `abnormalizer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.parser = abnormalizer.FileParser(ABNORMAL_LIBLIST)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'abnormalizer.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
