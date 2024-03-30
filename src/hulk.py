# Copyright 2021-2025
# This file is part of HULK.
#
# HULK is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HULK is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HULK.  If not, see <http://www.gnu.org/licenses/>.
#
from lexer.lexer import Lexer, Token
import argparse

def program ():

  parser = argparse.ArgumentParser (description = 'hulk compiler')

  parser.add_argument ('input', help = 'input file', nargs = '*')

  args = parser.parse_args ()

  for file in args.input:

    with open (file, 'r') as stream:

      for token in Lexer (stream.readlines ()):

        if (token.type != Token.IGNORE):

          val = token.value.rjust (13, ' ')
          print (f'{val} of {token.type}')

program ()
