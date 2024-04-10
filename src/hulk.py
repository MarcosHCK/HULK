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
from codegen.compile import compile
from codegen.run import run
from lexer.lexer import Lexer, Token
from parser.parser import Parser
from parser.viewer import PrintVisitor
from typing import Iterable
import argparse

from semantic.check import SemanticCheck

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
  parser.add_argument ('-O', default = 0, help = 'optimization level', metavar = 'LEVEL', type = int)

  args = parser.parse_args ()

  for file in args.input:

    with open (file, 'r') as stream:

      lines = stream.readlines ()
      tokens = ignore (Lexer (lines)) 
      ast = Parser (tokens)

      print ('\n'.join (PrintVisitor ().visit (ast)))
      print ('--*-*-*-*-*--')

      semantic = SemanticCheck ().check (ast)

      print ('\n'.join (PrintVisitor ().visit (ast)))
      print ('--*-*-*-*-*--')

      module = Codegen ().generate (ast, semantic, name = str (file))

      print (module)
      print ('--*-*-*-*-*--')

      module = compile (module, level = args.O)

      print (module)
      print ('--*-*-*-*-*--')

      run (module, [ 'src/stdlib/stdlib.lib' ])

program ()
