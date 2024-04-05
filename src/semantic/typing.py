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
from parser.ast.block import Block
from parser.ast.conditional import Conditional
from parser.ast.constant import Constant
from parser.ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from parser.ast.indirection import ClassAccess
from parser.ast.invoke import Invoke
from parser.ast.let import Let
from parser.ast.loops import While
from parser.ast.operator import BinaryOperator, UnaryOperator
from parser.ast.param import Param, VarParam
from parser.ast.value import NewValue, VariableValue
from parser.types import AnyType, CompositeType, FunctionType, ProtocolType, TypeRef
from parser.types import compare_types
from semantic.exception import SemanticException
from semantic.scope import Scope
from utils.builtins import BOOLEAN_TYPE
from utils.builtins import NUMBER_TYPE
from utils.builtins import STRING_TYPE
import utils.visitor as visitor

class TypingVisitor:

  def __init__ (self, scope: Scope, compose: None | CompositeType = None) -> None:

    self.compose = compose
    self.scope = scope

  @visitor.on ('node')
  def visit (self, node):

    pass

  @visitor.when (BinaryOperator)
  def visit (self, node: BinaryOperator) -> TypeRef:

    value: TypeRef

    match node.operator:

      case 'as': value = node.argument2 # type: ignore
      case 'is': value = BOOLEAN_TYPE.typeref

      case '@' | '@@': value = STRING_TYPE.typeref

      case _:

        arg1 = self.visit (node.argument) # type: ignore
        arg2 = self.visit (node.argument2) # type: ignore

        if not compare_types (arg1, arg2):

          raise SemanticException (node, f'incompatible types \'{arg1}\' and \'{arg2}\' for \'{node.operator}\' operator')

        else:

          match node.operator:

            case '==' | '!=' | '>=' | '<=' | '>' | '<': value = BOOLEAN_TYPE.typeref
            case _: value = (arg2 if isinstance (arg1, AnyType) else arg1)

    return value

  @visitor.when (Block)
  def visit (self, node: Block) -> TypeRef:

    value: TypeRef

    for stmt in node.stmts:

      value = self.visit (stmt) # type: ignore

    return value

  @visitor.when (ClassAccess)
  def visit (self, node: ClassAccess) -> TypeRef:

    base = self.visit (node.base) # type: ignore

    if not isinstance (base, CompositeType):

      raise SemanticException (node, f'trying to access a non-composite type \'{base}\'')

    else:

      member = base.get_member (node.field)

      if not member:

        raise SemanticException (node, f'trying to access a no existing field \'{node.field}\' in type \'{base}\'')

      else:

        return member

  @visitor.when (Conditional)
  def visit (self, node: Conditional) -> TypeRef:

    if (self.visit (node.condition) != BOOLEAN_TYPE.typeref): # type: ignore

      raise SemanticException (node.condition, f'conditional value is not a \'{BOOLEAN_TYPE.typeref}\' value')

    direct = self.visit (node.direct) # type: ignore

    if not isinstance (node, While):

      reverse = self.visit (node.reverse) # type: ignore

      if not compare_types (direct, reverse):

        raise SemanticException (node.reverse, f'branch value type \'{reverse}\' differs from conditional type \'{direct}\'')

    return direct

  @visitor.when (Constant)
  def visit (self, node: Constant) -> TypeRef:

    value: TypeRef

    if isinstance (node.value, bool): value = BOOLEAN_TYPE.typeref
    elif isinstance (node.value, float): value = NUMBER_TYPE.typeref
    elif isinstance (node.value, str): value = STRING_TYPE.typeref
    else: raise Exception (f'can not extract type info from {type (node.value)}')

    return value

  @visitor.when (DestructiveAssignment)
  def visit (self, node: DestructiveAssignment) -> TypeRef:

    over = self.visit (node.over) # type: ignore
    value = self.visit (node.value) # type: ignore

    if not compare_types (over, value): # type: ignore

      raise SemanticException (node.over, f'can not assign a \'{value}\' value to a \'{self.visit (node.over)}\' variable') # type: ignore

    return over if isinstance (value, AnyType) else value

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl) -> TypeRef:

    name = node.name if not self.compose else f'{self.compose.name}.{node.name}'

    params = []
    scope: Scope = self.scope.clone ()
    value: FunctionType = self.scope.getv (name) # type: ignore

    if self.compose != None:

      scope.addv ('self', self.compose)

      if self.compose.parent != None:

        scope.addv ('base', self.compose.parent)

    for param in value.params:

      params.append (scope.derive (param))

    for i, param in enumerate (params):

      node.params [i].typeref = params [i]
      value.params [i] = params [i]

      scope.addv (node.params [i].name, params [i])

    ref = scope.derive (value.typeref)

    body = TypingVisitor (scope).visit (node.body) or AnyType () # type: ignore

    if not compare_types (body, value.typeref):

      raise SemanticException (node, f'can not return a \'{body}\' value from a function with \'{value.typeref}\' return type')

    ref = value.typeref if isinstance (body, AnyType) else body

    value.typeref = ref
    node.typeref = ref

    return value

  @visitor.when (Invoke)
  def visit (self, node: Invoke) -> TypeRef:

    arguments = list (map (lambda a: self.visit (a), node.arguments)) # type: ignore
    target = self.visit (node.target) # type: ignore

    if not isinstance (target, FunctionType):

      raise SemanticException (node, f'attempt to call a \'{target}\' value')

    if len (arguments) != len (target.params):

      raise SemanticException (node, f'{target.name} function requires {len (target.params)}, got {len (arguments)}')

    elif any ([ not compare_types (a, b) for a, b in zip (arguments, target.params) ]):

      for typea, typeb in zip (arguments, target.params):

        if not compare_types (typea, typeb):

          raise SemanticException (node, f'can not convert a \'{typea}\' value to a \'{typeb}\' type')

      raise Exception ('invalid argument types')

    return target.typeref

  @visitor.when (Let)
  def visit (self, node: Let) -> TypeRef:

    scope = self.scope.clone ()
    typing = TypingVisitor (scope)

    for param in node.params:

      scope.addv (param.name, typing.visit (param)) # type: ignore

    return typing.visit (node.body) # type: ignore

  @visitor.when (NewValue)
  def visit (self, node: NewValue) -> TypeRef:

    value = self.scope.derive (node.typeref) # type: ignore

    if not value:

      raise SemanticException (node, f'unknown type \'{node.typeref}\'')

    elif not compare_types (value, node.typeref):

      raise SemanticException (node, f'composite types array can not be instanciate')

    elif isinstance (value, ProtocolType):

      raise SemanticException (node, f'can not instanciate a \'{value}\' protocol')

    node.typeref = value

    return value

  @visitor.when (Param)
  def visit (self, node: Param) -> None | TypeRef:

    node.typeref = self.scope.getv (node.name)
    node.typeref = self.scope.derive (node.typeref or AnyType ())

    if isinstance (node, VarParam):

      value = self.visit (node.value) # type: ignore

      if not compare_types (value, node.typeref):

        raise SemanticException (node, f'can not assign a \'{value}\' value to a \'{node.typeref}\' variable')

      node.typeref = value if not isinstance (value, AnyType) else node.typeref

    return node.typeref

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl) -> TypeRef:

    scope = self.scope.clone ()
    value: CompositeType = self.scope.gett (node.name) # type: ignore
    parent: CompositeType = self.scope.gett (node.parent) # type: ignore

    if not parent:

      raise SemanticException (node, f'unknown type \'{node.parent}\'')

    elif isinstance (node, ProtocolDecl) and not isinstance (parent, ProtocolType):

      raise SemanticException (node, f'protocol can not extend a \'{parent}\' type')

    elif isinstance (node, TypeDecl) and not isinstance (parent, CompositeType):

      raise SemanticException (node, f'type can not inherit from a \'{parent}\' type')

    value.parent = parent

    for name, member in value.members.items ():

      scope.addv (name, member)

    TypingVisitor (scope, compose = value).visit (node.body) # type: ignore

    return value

  @visitor.when (UnaryOperator)
  def visit (self, node: UnaryOperator) -> TypeRef:

    match node.operator:

      case '!':

        if self.visit (node.argument) != BOOLEAN_TYPE.typeref: # type: ignore

          raise SemanticException (node, f'invalid \'{self.visit (node.operator)}\' for \'{node.operator}\' operator') # type: ignore

        value = BOOLEAN_TYPE.typeref

      case _: value = self.visit (node.argument) # type: ignore

    return value

  @visitor.when (VariableValue)
  def visit (self, node: VariableValue) -> TypeRef:

    value = self.scope.getv (node.name)

    if not value:

      raise SemanticException (node, f'unknown variable \'{node.name}\'')

    return self.scope.derive (value or AnyType ())
