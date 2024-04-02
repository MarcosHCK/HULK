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
from .ast.assignment import DestructiveAssignment
from .ast.base import BASE_TYPE, ITERABLE_PROTOCOL
from .ast.base import TypeRef, Value
from .ast.block import Block
from .ast.conditional import Conditional
from .ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from .ast.indirection import ClassAccess, VectorAccess
from .ast.invoke import Invoke
from .ast.let import Let
from .ast.loops import While
from .ast.operator import BinaryOperator, UnaryOperator
from .ast.param import Param, VarParam
from .ast.value import BooleanValue, NewValue, NumberValue, StringValue, VariableValue
from typing import Any, Tuple

def getat (args: Tuple, at: int, default: Any = None):

  return default if at < 0 else args [at]

def build_binary_operator (args: Tuple, aat: int = 0, bat: int = 2, opat: int = 1):

  return BinaryOperator (getat (args, opat), getat (args, aat), getat (args, bat))

def build_block (args: Tuple, stmtsat: int = 0):

  return Block (getat (args, stmtsat))

def build_boolean_value (args: Tuple, valueat: int = 0):

  return BooleanValue (getat (args, valueat))

def build_class_access (args: Tuple, baseat: int = 0, fieldat: int = 1):

  return ClassAccess (getat (args, baseat), getat (args, fieldat))

def build_conditional (args: Tuple, branchesat: int = 0):

  branches = getat (args, branchesat)

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

def build_conditional_branch (args: Tuple, blockat: int = 1, conditionat: int = 0):

  return (getat (args, blockat), getat (args, conditionat))

def build_destructive_assignment (args: Tuple, overat: int = 0, valueat: int = 1):

  return DestructiveAssignment (getat (args, overat), getat (args, valueat))

def build_for (args: Tuple, paramat: int = 0, blockat: int = 1):

  param: Param = getat (args, paramat)
  block: Block = getat (args, blockat)

  name = param.name
  typeref = param.typeref

  itertyperef = TypeRef (ITERABLE_PROTOCOL, False)
  iterparam = VarParam ('iterable', itertyperef, param.value)
  iternext = Invoke (ClassAccess (VariableValue ('iterable'), 'next'), [])
  itercurr = Invoke (ClassAccess (VariableValue ('iterable'), 'current'), [])
  letparam = VarParam (name, typeref, itercurr)

  return Let ([iterparam], Block ([ While (iternext, Block ([ Let ([letparam], block) ])) ]))

def build_functiondecl (args: Tuple, nameat: int = 0, paramsat: int = 1, bodyat: int = 2, annotationat: int = 3):

  annotation: str = getat (args, annotationat)
  body: Block = getat (args, bodyat)
  name: str = getat (args, nameat)
  params: List[Param] = getat (args, paramsat)

  return FunctionDecl (name, params, annotation, body)

def build_invoke (args: Tuple, targetat: int = 0, argumentsat: int = 1):

  return Invoke (getat (args, targetat), getat (args, argumentsat))

def build_let (args: Tuple, paramsat: int = 0, blockat: int = 1):

  return Let (getat (args, paramsat), getat (args, blockat))

def build_list_begin (args: Tuple, index: int):

  return [ args [index] ]

def build_list_empty (args: Tuple):

  return [ ]

def build_list_join (args: Tuple, list1at: int = 0, list2at: int = 1):

  arglist = [ ]
  arglist.extend (getat (args, list1at))
  arglist.extend (getat (args, list2at))

  return arglist

def build_list_next (args: Tuple, elmat: int = 0, listat: int = 1):

  arglist = [ ]
  arglist.append (getat (args, elmat))
  arglist.extend (getat (args, listat))

  return arglist

def build_newvalue (args: Tuple, typeat: int = 0, argumentsat: int = 1):

  arguments = getat (args, argumentsat)
  type_ = getat (args, typeat)

  return NewValue (type_, arguments)

def build_number_value (args: Tuple, valueat: int = 0):

  return NumberValue (getat (args, valueat))

def build_param (args: Tuple, nameat: int = 0, annotationat: int = 1):

  name = getat (args, nameat)
  annotation = getat (args, annotationat)

  return Param (name, annotation)

def build_pickarg (args: Tuple, index: int):

  return args [index]

def build_protocoldecl (args: Tuple, nameat: int = 0, parentat: int = 1, bodyat: int = 2):

  body = getat (args, bodyat)
  name = getat (args, nameat)
  parent = getat (args, parentat)

  return ProtocolDecl (name, parent, body)

def build_string_value (args: Tuple, valueat: int = 0):

  return StringValue (getat (args, valueat))

def build_typedecl (args: Tuple, nameat: int = 0, paramsat: int = 1, parentat: int = 2, parentctorat: int = 3, bodyat: int = 4):

  body: Block = getat (args, bodyat, BASE_TYPE)
  name: str = getat (args, nameat)
  params: List[Param] = getat (args, paramsat, [ ])
  parent: str = getat (args, parentat)
  parentctor: List[Value] = getat (args, parentctorat, [ ])

  return TypeDecl (name, params, parent, parentctor, body)

def build_typeref (args: Tuple, nameat: int = 0, vector: bool = False):

  return TypeRef (getat (args, nameat), vector)

def build_unary_operator (args: Tuple, opat = 0, aat: int = 1):

  return UnaryOperator (getat (args, opat), getat (args, aat))

def build_varparam (args: Tuple, paramat: int = 0, valueat: int = 1):

  param: Param = getat (args, paramat)
  value: Value = getat (args, valueat)

  return VarParam (param.name, param.typeref, value)

def build_var_value (args: Tuple, valueat: int = 0):

  return VariableValue (args [0])

def build_while (args: Tuple, conditionat: int = 0, blockat: int = 1):

  return While (getat (args, conditionat), getat (args, blockat))
