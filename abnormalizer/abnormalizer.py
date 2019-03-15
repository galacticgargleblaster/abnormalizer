# -*- coding: utf-8 -*-

"""Main module."""

IM_SO_SORRY = \
"""/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   this text damages 42's reputation                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: student <student@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 4242/42/42 66:66:66 by student           #+#    #+#             */
/*   Updated: 4242/42/42 66:66:66 by studnet          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */
"""

from .parser import BaseParser
from .lexer import FTLexer
from .formatter import NormeFormatter
import pygments
from io import StringIO

def reformat(filename):
    with open(filename, 'r') as f:
        raw = f.read()
    tokens = pygments.lex(raw, FTLexer())
    fmt = NormeFormatter()
    output = StringIO() 
    fmt.format(tokens, output)
    return output
