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
from codegen.codegen import Codegen
from lexer.lexer import Lexer, Token
from parser.parser import Parser
from semantic.checker import SemanticChecker
from typing import Iterable
from utils.viewer import PrintVisitor
import argparse

def ignore (source: Iterable[Token]):

  lastline = 1
  lastcolumn = 1

  for token in source:

    if (token.type != Token.IGNORE):

      lastcolumn = token.column
      lastline = token.line
      yield token

  yield Token (lastcolumn + 1, lastline, 'EOF', None) # type: ignore

def program ():

  parser = argparse.ArgumentParser (description = 'hulk compiler')

  parser.add_argument ('input', help = 'input file', nargs = '*')

  args = parser.parse_args ()

  for file in args.input:

    with open (file, 'r') as stream:

      lines = stream.readlines ()
      tokens = ignore (Lexer (lines)) 
      ast = Parser (tokens)

      print ('\n'.join (PrintVisitor ().visit (ast)))
      print ('-*-*-')

      scope = SemanticChecker ().check (ast)

      print ('\n'.join (PrintVisitor ().visit (ast)))
      print ('-*-*-')

      module = Codegen ().generate (ast, scope)

      print (module)

program ()
