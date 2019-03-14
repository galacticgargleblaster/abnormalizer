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

class	FileParser():
	def __init__(self, filename):
		with open(filename, 'r') as f:
			self.raw = f.read()
		import ipdb; ipdb.set_trace()

class	HeaderFileParser(FileParser):
	pass

class	SourceFileParser(FileParser):
	pass
