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
from collections import OrderedDict
from enum import Enum
from functools import reduce
from parser.ast.assignment import DestructiveAssignment
from parser.ast.block import Block
from parser.ast.conditional import Conditional
from parser.ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from parser.ast.indirection import ClassAccess
from parser.ast.invoke import Invoke
from parser.ast.let import Let
from parser.ast.loops import While
from parser.ast.operator import BinaryOperator, UnaryOperator
from parser.ast.param import Param, VarParam
from parser.ast.value import Constant, NewValue, VariableValue
from semantic.exception import SemanticException
from semantic.scope import Scope
from semantic.type import AnyType, CompositeType, FunctionType, NamedType, ProtocolType, Type, UnionType, VectorType
from semantic.type import Ref as TypeRef
from semantic.types import Types
from typing import List, Sequence, Tuple
from utils.builtin import BASE_NAME, BASE_VARIABLE, BOOLEAN_TYPE, CTOR_NAME, NUMBER_TYPE, PRINTABLE_TYPE, SELF_NAME, SELF_VARIABLE, STRING_TYPE
import utils.visitor as visitor

TypeReport = Tuple[int, Type]

class TypingVisitor:

  @staticmethod
  def derivate (of: Type, types: Types, hints: List[Type] = []) -> TypeReport:

    actually = of

    if isinstance (of, AnyType | UnionType) and len (hints) > 0:

      return (0 if Type.compare_types (of, actually, True) else 1, reduce (Type.merge, hints))
    elif isinstance (of, AnyType):

      return (1, reduce (Type.merge, [ type_ for _, type_ in types.items () ]))

    return (0, of)

  @staticmethod
  def describe (type_: Type) -> str:

    if isinstance (type_, AnyType):

      return 'any'
    elif isinstance (type_, NamedType):

      return type_.name
    elif isinstance (type_, VectorType):

      return f'{TypingVisitor.describe (type_.type_)}'
    elif isinstance (type_, UnionType):

      return f'union[{",".join (map (lambda a: TypingVisitor.describe (a), type_.types))}]'
    else:

      return type (type_).__name__

  @staticmethod
  def merge (type_: Type, already: int, types: Types, hints: List[Type] = [ ]):

    done, got = TypingVisitor.derivate (type_, types = types, hints = hints)
    return (done + already, got)

  @visitor.on ('node')
  def visit (self, node, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    raise Exception ('falled through')

  @visitor.when (BinaryOperator)
  def visit (self, node: BinaryOperator, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    done = 0
    type_: Type

    match node.operator:

      case 'as' | 'is':

        if not (isinstance (node.argument2, TypeRef)):

          raise SemanticException (node.argument2, 'expecting a type')

        match node.operator:

          case 'as': type_ = types [node.argument2.name] # type: ignore
          case 'is': type_ = BOOLEAN_TYPE

      case _:

        last1, arg1 = self.visit (node.argument, scope, types, prefix = prefix) # type: ignore
        last2, arg2 = self.visit (node.argument2, scope, types, prefix = prefix) # type: ignore
        want: Sequence[NamedType]

        match node.operator:

          case '@' | '@@':

            for against in (want := [ NUMBER_TYPE, STRING_TYPE, PRINTABLE_TYPE ]):

              if Type.compare_types (against, arg1): # type: ignore

                wanted = f'{", ".join ([ *map (lambda a: TypingVisitor.describe (a), want[:-1]) ])}, or {TypingVisitor.describe (want[-1])}'
                raise SemanticException (node.argument2, f'expecting a \'{wanted}\' type, got \'{TypingVisitor.describe (arg1)}\'')

              if Type.compare_types (against, arg2): # type: ignore

                wanted = f'{", ".join ([ *map (lambda a: TypingVisitor.describe (a), want[:-1]) ])}, or {TypingVisitor.describe (want[-1])}'
                raise SemanticException (node.argument2, f'expecting a \'{wanted}\' type, got \'{TypingVisitor.describe (arg2)}\'')

            done = done + last1 + last2
            type_ = STRING_TYPE

          case '==' | '!=':

            for against in (want := [ NUMBER_TYPE, (type_ := BOOLEAN_TYPE) ]):

              if not (Type.compare_types (arg1, against) or not Type.compare_types (arg2, against)):

                arg1 = TypingVisitor.describe (arg1)
                arg2 = TypingVisitor.describe (arg2)

                raise SemanticException (node, f'incompatible types \'{arg1}\' and \'{arg2}\' for \'{node.operator}\' operator')

          case '+' | '-' | '*' | '/' | '%' | '<' | '>' | '<=' | '>=':

            if not (Type.compare_types (arg1, NUMBER_TYPE) and Type.compare_types (arg2, NUMBER_TYPE)):

              arg1 = TypingVisitor.describe (arg1)
              arg2 = TypingVisitor.describe (arg2)

              raise SemanticException (node, f'incompatible types \'{arg1}\' and \'{arg2}\' for \'{node.operator}\' operator')

            match node.operator:

              case '<' | '>' | '<=' | '>=': type_ = BOOLEAN_TYPE
              case _: type_ = NUMBER_TYPE

          case _:

            raise SemanticException (node, f'unknown binary operator \'{node.operator}\'')

        done = done + last1 + last2

    return (0, type_)

  @visitor.when (Block)
  def visit (self, node: Block, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    done = 0
    type_: Type

    for stmt in node.stmts:

      last, type_ = self.visit (stmt, scope, types, prefix = prefix) # type: ignore
      done = done + last

    return (done, type_)

  @visitor.when (ClassAccess)
  def visit (self, node: ClassAccess, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    done, type_ = self.visit (node.base, scope, types, prefix = prefix) # type: ignore

    if not isinstance (type_, CompositeType):

      raise SemanticException (node, f'trying to index a \'{TypingVisitor.describe (type_)}\' type')

    else:

      if (member := type_ [node.field]) == None:

        raise SemanticException (node, f'trying to access a no existing field \'{node.field}\' in \'{TypingVisitor.describe (type_)}\'')

      else:

        node.type_ = type_
        return (done, member)

  @visitor.when (Conditional)
  def visit (self, node: Conditional, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    done, type_ = self.visit (node.condition, scope, types, prefix = prefix) # type: ignore

    if type_ != BOOLEAN_TYPE:

      raise SemanticException (node.condition, f'conditional value is not a \'{TypingVisitor.describe (BOOLEAN_TYPE)}\' value')

    else:

      last, direct = self.visit (node.direct, scope, types, prefix = prefix) # type: ignore
      done = last + done

      if not isinstance (node, While):

        last, reverse = self.visit (node.reverse, scope, types, prefix = prefix) # type: ignore
        done = last + done

        if not Type.compare_types (direct, reverse):

          raise SemanticException (node.reverse, f'branch value type \'{reverse}\' differs from conditional type \'{direct}\'')

    return (done, direct)

  @visitor.when (Constant)
  def visit (self, node: Constant, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    if isinstance (node.value, bool): type_ = BOOLEAN_TYPE
    elif isinstance (node.value, float): type_ = NUMBER_TYPE
    elif isinstance (node.value, str): type_ = STRING_TYPE
    else: raise Exception (f'can not extract type info from {type (node.value)}')

    return (0, type_)

  @visitor.when (DestructiveAssignment)
  def visit (self, node: DestructiveAssignment, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    last1, over = self.visit (node.over, scope, types, prefix = prefix) # type: ignore
    last2, value = self.visit (node.value, scope, types, prefix = prefix) # type: ignore
    done = last1 + last2

    if not Type.compare_types (over, value): # type: ignore

      raise SemanticException (node.over, f'can not assign a \'{TypingVisitor.describe (value)}\' value to a \'{TypingVisitor.describe (over)}\' variable') # type: ignore

    return TypingVisitor.merge (over, done, types, [ value ])

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    done = 0
    name = '.'.join ([ *map (lambda a: a.name, prefix), node.name ])

    descent = Scope ()
    params = OrderedDict ()

    value: FunctionType = scope [name] # type: ignore

    if len (prefix) > 0:

      descent [SELF_NAME if node.name == CTOR_NAME else SELF_VARIABLE] = (overlord := prefix [-1])

      if overlord.parent:

        descent [BASE_NAME if node.name == CTOR_NAME else BASE_VARIABLE] = overlord.parent

    for name, type_ in scope.items ():

      descent [name] = type_

    for name, param in value.params.items ():

      last, type_ = TypingVisitor.derivate (param, types, [])
      done = last + done

      params [name] = type_

    for i, (name, param) in enumerate (zip (value.params.keys (), params)):

      type_ = params [name]

      descent [name] = type_
      node.params [i].type_ = type_
      value.params [name] = type_

    value.type_ = value.type_ or AnyType ()

    if node.body != None:

      done, type_ = self.visit (node.body, descent, types, prefix = prefix) # type: ignore
      done, type_ = TypingVisitor.merge (value.type_, done, types, [ type_ ])

      if not Type.compare_types (value.type_, type_):

        expect = TypingVisitor.describe (type_)
        got = TypingVisitor.describe (value.type_)

        raise SemanticException (node, f'can not return a \'{expect}\' value from a function with \'{got}\' return type')

    value.type_ = type_
    node.type_ = type_

    return (done, value)

  @visitor.when (Invoke)
  def visit (self, node: Invoke, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    descent: List[Type] = []
    done: int = 0

    for other in [ node.target, *node.arguments ]:

      last, down = self.visit (other, scope, types, prefix = prefix) # type: ignore

      descent.append (down)
      done = done + last

    arguments = descent [1:]
    target = descent [0]

    if not isinstance (target, FunctionType):

      raise SemanticException (node, f'attempt to call a \'{TypingVisitor.describe (target)}\' value')
    
    elif any ([ not Type.compare_types (a, b) for a, b in zip (arguments, target.params.values ()) ]):

      for typea, typeb in zip (arguments, target.params.values ()):

        if not Type.compare_types (typea, typeb):

          raise SemanticException (node, f'can not convert a \'{TypingVisitor.describe (typea)}\' value to a \'{TypingVisitor.describe (typeb)}\' type')

      raise Exception ('invalid argument types')

    return (done, target.type_)

  @visitor.when (Let)
  def visit (self, node: Let, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    descent = Scope ()
    done = 0

    for name, variable in scope.items ():

      descent [name] = variable

    for param in node.params:

      last, descent [param.name] = self.visit (param, descent, types, prefix = prefix) # type: ignore
      done = last + done

    if True:

      last, type_ = self.visit (node.body, descent, types, prefix = prefix) # type: ignore
      done = last + done

    return (done, type_)

  @visitor.when (NewValue)
  def visit (self, node: NewValue, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    assert (isinstance (node.type_, NamedType))

    if (type_ := types.get (node.type_.name, None)) == None:

      raise SemanticException (node, f'unknown type \'{TypingVisitor.describe (node.type_)}\'')

    elif isinstance (type_, ProtocolType):

      raise SemanticException (node, f'can not instanciate a protocol')

    elif isinstance (type_, ProtocolType):

      raise SemanticException (node, f'can not instanciate a \'{TypingVisitor.describe (node.type_)}\' type')

    node.type_ = type_

    arguments: List[Type] = []
    ctor: FunctionType = scope ['.'.join ([ type_.name, CTOR_NAME ])] # type: ignore
    done: int = 0

    for other in node.arguments:

      last, down = self.visit (other, scope, types, prefix = prefix) # type: ignore

      arguments.append (down)
      done = done + last

    if any ([ not Type.compare_types (a, b) for a, b in zip (arguments, ctor.params.values ()) ]):

      for typea, typeb in zip (arguments, ctor.params.values ()):

        if not Type.compare_types (typea, typeb):

          raise SemanticException (node, f'can not convert a \'{TypingVisitor.describe (typea)}\' value to a \'{TypingVisitor.describe (typeb)}\' type')

      raise Exception ('invalid argument types')

    return (0, type_)

  @visitor.when (Param)
  def visit (self, node: Param, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    done = 0
    done, type_ = TypingVisitor.merge (node.type_ or AnyType (), done, types, [])

    node.type_ = type_

    if isinstance (node, VarParam):

      last, value = self.visit (node.value, scope, types, prefix = prefix) # type: ignore
      done = last + done

      if not Type.compare_types (type_, value):

        raise SemanticException (node, f'can not assign a \'{TypingVisitor.describe (value)}\' value to a \'{TypingVisitor.describe (type_)}\' variable')

      done, type_ = TypingVisitor.merge (type_, done, types, [ value ])
      node.type_ = type_

    return (done, type_)

  @visitor.when (ProtocolDecl | TypeDecl)
  def visit (self, node: ProtocolDecl | TypeDecl, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    descent = Scope ()
    parent: CompositeType = types.get (node.parent, None) # type: ignore
    value: CompositeType = types.get (node.name, None) # type: ignore

    if not isinstance (node, ProtocolDecl) and not parent:

      raise SemanticException (node, f'unknown type \'{node.parent}\'')

    elif isinstance (node, ProtocolDecl) and node.parent and not isinstance (parent, ProtocolType):

      raise SemanticException (node, f'protocol can not extend a \'{parent}\' type')

    elif isinstance (node, TypeDecl) and not isinstance (parent, CompositeType):

      raise SemanticException (node, f'type can not inherit from a \'{parent}\' type')

    elif value.circular (parent):

      raise SemanticException (node, f'circular inheritance')

    value.parent = parent

    for name, type_ in scope.items ():

      descent [name] = type_

    for name, type_ in [ *value.attributes.items (), *value.methods.items () ]:

      descent [name] = type_

    return self.visit (node.body, scope, types, prefix = [ *prefix, value ]) # type: ignore

  @visitor.when (UnaryOperator)
  def visit (self, node: UnaryOperator, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    match node.operator:

      case '!':

        done, type_ = self.visit (node.argument, scope, types, prefix = prefix) # type: ignore

        if type_ != BOOLEAN_TYPE:

          raise SemanticException (node, f'can not transform a \'{TypingVisitor.describe (type_)}\' to {TypingVisitor.describe (BOOLEAN_TYPE)}') # type: ignore

      case _:

        raise SemanticException (node, f'unknown unary operator \'{node.operator}\'')

    return (done, type_)

  @visitor.when (VariableValue)
  def visit (self, node: VariableValue, scope: Scope, types: Types, prefix: List[CompositeType] = []) -> TypeReport: # type: ignore

    name = node.name

    if not (type_ := scope.get (name, None)):

      raise SemanticException (node, f'unknown variable \'{node.name}\'')

    return (0, type_)
