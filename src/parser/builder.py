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
from parser.ast.conditional import Conditional
from parser.ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from parser.ast.invoke import Invoke
from parser.ast.let import Let
from parser.ast.loops import While
from parser.ast.operator import BinaryOperator, UnaryOperator
from parser.ast.param import Param, VarParam
from parser.ast.value import BooleanValue, NumberValue, StringValue, VariableValue
from typing import Any, Tuple

def getat (args: Tuple, at: int, default: Any = None):

  return default if at < 0 else args [at]

def build_binary_operator (args: Tuple):

  return BinaryOperator (args [1], args [0], args [2])

def build_block (args: Tuple):

  return Block (args [0])

def build_boolean_value (args: Tuple):

  return BooleanValue (args [0])

def build_conditional (args: Tuple):

  branches = args [0]

  head = branches [0]
  last = branches [-1]
  rest = branches [1:-1]

  rest.reverse ()

  head_body = head [0]
  head_condition = head [1]

  last_body = last [0]

  for branch in rest:

    branch_body = branch [0]
    branch_condition = branch [1]

    tail = Conditional (branch_condition, branch_body, last_body)
    last_body = Block ([ tail ])

  return Conditional (head_condition, head_body, last_body)

def build_conditional_branch (args: Tuple, blockat: int, conditionat: int):

  return (getat (args, blockat), getat (args, conditionat))

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

def build_function_decl (args: Tuple, nameat: int, paramsat: int, bodyat: int, annotationat: int):

  annotation = getat (args, annotationat)
  body = getat (args, bodyat)
  name = getat (args, nameat)
  params = getat (args, paramsat)

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

def build_type_decl (args: Tuple, nameat: int, paramsat: int, parentat: int, parentctorat: int, bodyat: int):

  body = getat (args, bodyat, BASE_TYPE)
  name = getat (args, nameat)
  params = getat (args, paramsat, [])
  parent = getat (args, parentat)
  parentctor = getat (args, parentctorat)

  return TypeDecl (name, params, parent, parentctor, body)

def build_unary_operator (args: Tuple):

  return UnaryOperator (args [0], args [1])

def build_varparam (args: Tuple):

  return VarParam (args [0], args [2])

def build_var_value (args: Tuple):

  return VariableValue (args [0])

def build_while (args: Tuple):

  return While (args [0], args [1])
