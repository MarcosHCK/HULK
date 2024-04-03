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
from parser.ast.assignment import DestructiveAssignment
from parser.ast.base import AstNode
from parser.ast.base import BASE_TYPE, ITERABLE_PROTOCOL
from parser.ast.base import Value
from parser.ast.block import Block
from parser.ast.conditional import Conditional
from parser.ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from parser.ast.indirection import ClassAccess
from parser.ast.invoke import Invoke
from parser.ast.let import Let
from parser.ast.loops import While
from parser.ast.operator import BinaryOperator, UnaryOperator
from parser.ast.param import Param, VarParam
from parser.ast.value import BooleanValue, NewValue, NumberValue, StringValue, VariableValue
from parser.types import CTOR_NAME, AnyType, TypeRef
from lexer.lexer import Token
from typing import Any, List, Tuple

def annot (first: Token):

  if isinstance (first, Token): return { 'line': first.line, 'column': first.column }
  elif isinstance (first, AstNode): return { 'line': first.line, 'column': first.column }
  elif isinstance (first, list): return {} if len (first) == 0 else annot (first [0])
  else: raise Exception (f'can not extract line info from \'{type (first)}\' object')

def getat (args: Tuple, at: int, default: Any = None):

  return default if at < 0 else args [at]

def getvat (args: Tuple, at: int, default: Any = None):

  token = getat (args, at, None)

  return default if not token else token.value

def build_binary_operator (args: Tuple, first: Token, aat: int = 0, bat: int = 2, opat: int = 1):

  op = getvat (args, opat)
  a = getat (args, aat)
  b = getat (args, bat)

  return BinaryOperator (op, a, b, **annot (first))

def build_block (args: Tuple, first: Token, stmtsat: int = 0):

  return Block (getat (args, stmtsat), **annot (first))

def build_boolean_value (args: Tuple, first: Token, valueat: int = 0):

  return BooleanValue (getvat (args, valueat), **annot (first))

def build_class_access (args: Tuple, first: Token, baseat: int = 0, fieldat: int = 1):

  return ClassAccess (getat (args, baseat), getvat (args, fieldat), **annot (first))

def build_conditional (args: Tuple, first: Token, branchesat: int = 0):

  branches = getat (args, branchesat)

  head = branches [0]
  last = branches [-1]
  rest = branches [1:-1]

  rest.reverse ()

  head_body = head [0]
  head_condition = head [1]
  head_annot = head [2]

  last_body = last [0]

  for branch in rest:

    branch_body = branch [0]
    branch_condition = branch [1]
    branch_annot = branch [2]

    tail = Conditional (branch_condition, branch_body, last_body, **branch_annot)
    last_body = Block ([ tail ])

  return Conditional (head_condition, head_body, last_body, **head_annot)

def build_conditional_branch (args: Tuple, first: Token, blockat: int = 1, conditionat: int = 0):

  return (getat (args, blockat), getat (args, conditionat), annot (first))

def build_destructive_assignment (args: Tuple, first: Token, overat: int = 0, valueat: int = 1):

  return DestructiveAssignment (getat (args, overat), getat (args, valueat), **annot (first))

def build_for (args: Tuple, first: Token, paramat: int = 0, blockat: int = 1):

  param: VarParam = getat (args, paramat)
  block: Block = getat (args, blockat)

  name = param.name
  typeref = param.typeref

  itertyperef = TypeRef (ITERABLE_PROTOCOL, False, **annot (first))
  iterparam = VarParam ('iterable', itertyperef, param.value, **annot (first))
  iternext = Invoke (ClassAccess (VariableValue ('iterable'), 'next'), [], **annot (first))
  itercurr = Invoke (ClassAccess (VariableValue ('iterable'), 'current'), [], **annot (first))
  letparam = VarParam (name, typeref, itercurr, **annot (first))

  return Let ([iterparam], Block ([ While (iternext, Block ([ Let ([letparam], block) ])) ]), **annot (first))

def build_functiondecl (args: Tuple, first: Token, nameat: int = 0, paramsat: int = 1, bodyat: int = 2, annotationat: int = 3):

  annotation: TypeRef = getat (args, annotationat)
  body: Block = getat (args, bodyat)
  name: str = getvat (args, nameat)
  params: List[Param] = getat (args, paramsat)

  return FunctionDecl (name, params, annotation, body, **annot (first))

def build_invoke (args: Tuple, first: Token, targetat: int = 0, argumentsat: int = 1):

  return Invoke (getat (args, targetat), getat (args, argumentsat), **annot (first))

def build_let (args: Tuple, first: Token, paramsat: int = 0, blockat: int = 1):

  return Let (getat (args, paramsat), getat (args, blockat), **annot (first))

def build_list_begin (args: Tuple, first: Token, index: int):

  return [ args [index] ]

def build_list_empty (args: Tuple, first: Token):

  return [ ]

def build_list_join (args: Tuple, first: Token, list1at: int = 0, list2at: int = 1):

  arglist = [ ]
  arglist.extend (getat (args, list1at))
  arglist.extend (getat (args, list2at))

  return arglist

def build_list_next (args: Tuple, first: Token, elmat: int = 0, listat: int = 1):

  arglist = [ ]
  arglist.append (getat (args, elmat))
  arglist.extend (getat (args, listat))

  return arglist

def build_newvalue (args: Tuple, first: Token, typeat: int = 0, argumentsat: int = 1):

  arguments = getat (args, argumentsat)
  type_ = getvat (args, typeat)

  return NewValue (TypeRef (type_, False), arguments, **annot (first))

def build_number_value (args: Tuple, first: Token, valueat: int = 0):

  return NumberValue (getvat (args, valueat), **annot (first))

def build_param (args: Tuple, first: Token, nameat: int = 0, annotationat: int = 1):

  name = getvat (args, nameat)
  annotation = getat (args, annotationat)

  return Param (name, annotation, **annot (first))

def build_pickarg (args: Tuple, first: Token, index: int):

  return args [index]

def build_protocoldecl (args: Tuple, first: Token, nameat: int = 0, parentat: int = 1, bodyat: int = 2):

  body = getat (args, bodyat)
  name = getvat (args, nameat)
  parent = getvat (args, parentat)

  return ProtocolDecl (name, parent, body, **annot (first))

def build_string_value (args: Tuple, first: Token, valueat: int = 0):

  return StringValue (getvat (args, valueat), **annot (first))

def build_typedecl (args: Tuple, first: Token, nameat: int = 0, paramsat: int = 1, parentat: int = 2, parentctorat: int = 3, bodyat: int = 4):

  body: Block = getat (args, bodyat)
  name: str = getvat (args, nameat)
  params: List[Param] = getat (args, paramsat)
  parent: str = getvat (args, parentat, BASE_TYPE)
  parentctor: List[Value] = getat (args, parentctorat)

  ctorb = Block ([ Invoke (ClassAccess (VariableValue ('self'), CTOR_NAME), parentctor or [ ]) ])
  ctor = FunctionDecl (CTOR_NAME, params or [ ], None, ctorb)

  body = Block ([ ctor, *body.stmts ]) # type: ignore
  decl = TypeDecl (name, parent, body, **annot (first))

  return decl

def build_typeref (args: Tuple, first: Token, nameat: int = 0, vector: bool = False):

  return TypeRef (getvat (args, nameat), vector, **annot (first))

def build_unary_operator (args: Tuple, first: Token, opat = 0, aat: int = 1):

  return UnaryOperator (getvat (args, opat), getat (args, aat), **annot (first))

def build_varparam (args: Tuple, first: Token, paramat: int = 0, valueat: int = 1):

  param: Param = getat (args, paramat)
  value: Value = getat (args, valueat)

  return VarParam (param.name, param.typeref, value, **annot (first))

def build_var_value (args: Tuple, first: Token, valueat: int = 0):

  return VariableValue (getvat (args, valueat), **annot (first))

def build_while (args: Tuple, first: Token, conditionat: int = 0, blockat: int = 1):

  return While (getat (args, conditionat), getat (args, blockat), **annot (first))
