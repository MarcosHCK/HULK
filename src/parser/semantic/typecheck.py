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
from parser.ast.invoke import Invoke
from ..ast.decl import FunctionDecl
from ..ast.assignment import DestructiveAssignment
from ..ast.base import BOOL_TYPE, NUMBER_TYPE, STRING_TYPE
from ..ast.block import Block
from ..ast.conditional import Conditional
from ..ast.constant import Constant
from ..ast.let import Let
from ..ast.loops import While
from ..ast.operator import BinaryOperator, UnaryOperator
from ..ast.param import Param, VarParam
from ..ast.types import AnyType, FunctionType, TypeRef
from ..ast.value import VariableValue
from .exception import SemanticException
from .scope import Scope
import utils.visitor as visitor

class TypeCheckVisitor:

  def __init__ (self, scope: Scope, invoker: bool = False) -> None:

    self.invoker = invoker
    self.scope = scope

  @visitor.on ('node')
  def visit (self, node):

    pass

  @visitor.when (BinaryOperator)
  def visit (self, node: BinaryOperator) -> TypeRef:

    value: TypeRef

    match node.operator:

      case 'as': value = node.argument2 # type: ignore
      case 'is': value = BOOL_TYPE

      case '@' | '@@': value = STRING_TYPE

      case _:

        arg1 = self.visit (node.argument) # type: ignore
        arg2 = self.visit (node.argument2) # type: ignore

        if (arg1 != arg2):

          raise SemanticException (node, f'incompatible types \'{arg1}\' and \'{arg2}\' for \'{node.operator}\' operator')

        else:

          match node.operator:

            case '==' | '!=' | '>=' | '<=' | '>' | '<': value = BOOL_TYPE
            case _: value = (arg2 if isinstance (arg1, AnyType) else arg1)

    node.typeref = value

    return value

  @visitor.when (Block)
  def visit (self, node: Block) -> TypeRef:

    value: TypeRef

    for stmt in node.stmts:

      value = self.visit (stmt) # type: ignore

    node.typeref = value

    return value

  @visitor.when (Conditional)
  def visit (self, node: Conditional) -> TypeRef:

    if (self.visit (node.condition) != BOOL_TYPE): # type: ignore

      raise SemanticException (node.condition, f'conditional value is not a \'{BOOL_TYPE}\' value')

    direct = self.visit (node.direct) # type: ignore

    if not isinstance (node, While):

      reverse = self.visit (node.reverse) # type: ignore

      if direct != reverse:

        raise SemanticException (node.reverse, f'branch value type \'{reverse}\' differs from conditional type \'{direct}\'')

    node.typeref = direct
    return direct

  @visitor.when (Constant)
  def visit (self, node: Constant) -> TypeRef:

    value: TypeRef

    if isinstance (node.value, bool): value = BOOL_TYPE
    elif isinstance (node.value, float): value = NUMBER_TYPE
    elif isinstance (node.value, str): value = STRING_TYPE
    else: raise Exception (f'can not extract type info from {type (node.value)}')

    node.typeref = value

    return value

  @visitor.when (DestructiveAssignment)
  def visit (self, node: DestructiveAssignment) -> TypeRef:

    over = self.visit (node.over) # type: ignore
    value = self.visit (node.value) # type: ignore

    if (over != value): # type: ignore

      raise SemanticException (node.over, f'can not assign a \'{value}\' value to a \'{self.visit (node.over)}\' variable') # type: ignore

    node.typeref = over if isinstance (value, AnyType) else value

    return node.typeref

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl) -> TypeRef:

    scope = self.scope.clone ()
    params = [ ]

    for param in node.params:

      typeref = self.visit (param) # type: ignore
      typeref = typeref or AnyType ()

      param.typeref = typeref
      params.append (param.typeref)

      scope.addv (param.name, typeref)

    body = TypeCheckVisitor (scope).visit (node.body) # type: ignore
    typeref = node.typeref or AnyType ()

    if body != typeref:

      raise SemanticException (node, f'can not return a \'{body}\' value from a function with \'{typeref}\' return type')

    typeref = body if isinstance (typeref, AnyType) else typeref
    value = FunctionType (node.name, params, typeref)

    node.typeref = typeref
    self.scope.addv (node.name, value)

    return value

  @visitor.when (Invoke)
  def visit (self, node: Invoke) -> TypeRef:

    arguments = list (map (lambda a: self.visit (a), node.arguments)) # type: ignore
    target = TypeCheckVisitor (self.scope, invoker = True).visit (node.target) # type: ignore

    if not isinstance (target, FunctionType):

      raise SemanticException (node, f'attempt to call a \'{target}\' value')

    elif len (target.params) != len (arguments):

      raise SemanticException (node, f'{target.name} function requires {len (target.params)}, {len (arguments)} were given')

    elif target.params != arguments:

      for typea, typeb in zip (arguments, target.params):

        if typea != typeb:

          raise SemanticException (node, f'can not assign a \'{typeb}\' value to a \'{typea}\' variable')

      raise Exception ('invalid argument types')

    node.typeref = target.typeref

    return node.typeref

  @visitor.when (Let)
  def visit (self, node: Let) -> TypeRef:

    scope = self.scope.clone ()

    for param in node.params:

      scope.addv (param.name, self.visit (param)) # type: ignore

    node.typeref = TypeCheckVisitor (scope).visit (node.body) # type: ignore

    return node.typeref

  @visitor.when (Param)
  def visit (self, node: Param) -> None | TypeRef:

    return node.typeref

  @visitor.when (UnaryOperator)
  def visit (self, node: UnaryOperator) -> TypeRef:

    match node.operator:

      case '!':

        if self.visit (node.argument) != BOOL_TYPE: # type: ignore

          raise SemanticException (node, f'invalid \'{self.visit (node.operator)}\' for \'{node.operator}\' operator') # type: ignore

        value = BOOL_TYPE

      case _: value = self.visit (node.argument) # type: ignore

    node.typeref = value

    return value

  @visitor.when (VariableValue)
  def visit (self, node: VariableValue) -> TypeRef:

    value = self.scope.getv (node.name)

    if not value:

      raise SemanticException (node, f'unknown variable \'{node.name}\'')

    elif not self.invoker and isinstance (value, FunctionType):

      raise SemanticException (node, f'functions can not be accessed as variables')

    node.typeref = value

    return value

  @visitor.when (VarParam)
  def visit (self, node: VarParam) -> TypeRef:

    value = self.visit (node.value) # type: ignore

    if node.typeref != None and node.typeref != value:

      raise SemanticException (node, f'can not assign a \'{value}\' value to a \'{node.typeref}\' variable')

    node.typeref = value

    return value
