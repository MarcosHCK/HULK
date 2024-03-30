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
from parser.ast.block import Block
from parser.ast.decl import FunctionDecl
from parser.ast.invoke import Invoke
from parser.ast.operator import BinaryOperator, UnaryOperator
from parser.ast.param import Param
from parser.ast.value import BooleanValue, NumberValue, StringValue
from typing import Tuple

def build_binary_operator (args: Tuple):

  return BinaryOperator (args [1], args [0], args [2])

def build_block (args: Tuple):

  return Block (args [0])

def build_boolean_value (args: Tuple):

  return BooleanValue (args [0])

def build_function_decl (args: Tuple):

  return FunctionDecl (args [1], args [2], args [3])

def build_invoke (args: Tuple):

  return Invoke (args [0], args [1])

def build_list_begin (args: Tuple, index: int):

  return [ args [index] ]

def build_list_next (args: Tuple, elmat: int, listat: int):

  arglist = [ ]
  arglist.append (args [elmat])
  arglist.extend (args [listat])

  return arglist

def build_number_value (args: Tuple):

  return NumberValue (args [0])

def build_param (args: Tuple, annotated: bool, isvector: bool):

  if (not annotated):

    return Param (args [0])
  else:

    return Param (args [0], args [2], isvector)

def build_pickarg (args: Tuple, index: int):

  return args [index]

def build_string_value (args: Tuple):

  return StringValue (args [0])

def build_unary_operator (args: Tuple):

  return UnaryOperator (args [0], args [1])
