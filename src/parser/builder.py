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
from parser.ast.base import BASE_TYPE
from parser.ast.block import Block
from parser.ast.conditional import Conditional, ConditionalEntry
from parser.ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from parser.ast.invoke import Invoke
from parser.ast.let import Let
from parser.ast.loops import While
from parser.ast.operator import BinaryOperator, UnaryOperator
from parser.ast.param import Param, VarParam
from parser.ast.value import BooleanValue, NumberValue, StringValue, VariableValue
from typing import Tuple

def build_binary_operator (args: Tuple):

  return BinaryOperator (args [1], args [0], args [2])

def build_block (args: Tuple):

  return Block (args [0])

def build_boolean_value (args: Tuple):

  return BooleanValue (args [0])

def build_conditional (args: Tuple):

  return Conditional (args [0])

def build_conditional_entry (args: Tuple, else_: bool):

  if (else_):

    return ConditionalEntry (None, args [1])
  else:

    return ConditionalEntry (args [0], args [1])

def build_for (args: Tuple):

  param = args [0]
  block = args [1]

  varname = param.param.name
  vartype = param.param.annotation
  isvector = param.param.isvector

  iterparam = VarParam (Param ('iterable', None, False), param.value)
  itercond = VariableValue ('iter')
  varparam = VarParam (Param (varname, vartype, isvector), VariableValue ('iter'))

  return Let ([iterparam], Block ([ While (itercond, Block ([ Let ([varparam], block) ])) ]))

def build_function_decl (args: Tuple, annotated: bool, virtual: bool):

  annotation = None if not annotated else args [2]
  body = None if virtual else (args [3] if annotated else args [2])

  name = args [0]
  params = args [1]

  return FunctionDecl (name, params, annotation, body)

def build_invoke (args: Tuple):

  return Invoke (args [0], args [1])

def build_let (args: Tuple):

  return Let (args [1], args [3])

def build_list_begin (args: Tuple, index: int):

  return [ args [index] ]

def build_list_empty (args: Tuple):

  return [ ]

def build_list_join (args: Tuple, list1at: int, list2at: int):

  arglist = [ ]
  arglist.extend (args [list1at])
  arglist.extend (args [list2at])

  return arglist

def build_list_next (args: Tuple, elmat: int, listat: int):

  arglist = [ ]
  arglist.append (args [elmat])
  arglist.extend (args [listat])

  return arglist

def build_number_value (args: Tuple):

  return NumberValue (args [0])

def build_param (args: Tuple, annotated: bool, isvector: bool):

  if (not annotated):

    return Param (args [0], None, False)
  else:

    return Param (args [0], args [2], isvector)

def build_pickarg (args: Tuple, index: int):

  return args [index]

def build_protocol_decl (args: Tuple, extends: bool):

  if (not extends):

    return ProtocolDecl (args [0], None, args [1])
  else:

    return ProtocolDecl (args [0], args [1], args [2])

def build_string_value (args: Tuple):

  return StringValue (args [0])

def build_type_decl (args: Tuple, inherits: bool):

  if (not inherits):

    return TypeDecl (args [0], BASE_TYPE, args [1])
  else:

    return TypeDecl (args [0], args [1], args [2])

def build_unary_operator (args: Tuple):

  return UnaryOperator (args [0], args [1])

def build_varparam (args: Tuple):

  return VarParam (args [0], args [2])

def build_var_value (args: Tuple):

  return VariableValue (args [0])

def build_while (args: Tuple):

  return While (args [0], args [1])
