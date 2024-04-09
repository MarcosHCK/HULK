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
from parser.ast.assignment import DestructiveAssignment
from parser.ast.base import AstNode
from parser.ast.block import Block
from parser.ast.decl import FunctionDecl, TypeDecl
from parser.ast.indirection import ClassAccess
from parser.ast.param import Param, VarParam
from parser.ast.value import VariableValue
from semantic.exception import SemanticException
from semantic.scope import Scope
from semantic.type import CompositeType, FunctionType, NamedType, ProtocolType, Type, UnionType
from semantic.types import Types
from semantic.typing import TypingVisitor
from typing import Dict, Generator, List, Set
from utils.alternate import alternate
from utils.builtin import CTOR_NAME, SELF_NAME
import utils.visitor as visitor

CollectList = None | Dict[str, AstNode]

class TransformStage (Enum):

  COLLECT_FUNCTIONS = 1
  COLLECT_IMPLEMENTS = 2
  COLLECT_PARAMS = 3
  EXPAND_PROTOCOLS = 4
  GUESS_ARGUMENTS = 5
  GUESS_PARAMS = 6
  TRIM_ATTRIBUTES = 7

def alternatelist (list_: List[List[Type]]) -> Generator[List[Type], None, None]:

  if len (list_) == 0:

    pass
  elif len (list_) == 1:

    for type_ in list_[0]: yield [ type_ ]
  else:

    head = list_ [0]
    tail = list_ [1:]

    for ahead in alternatelist ([ head ]):

      for atail in alternatelist (tail):

        yield [ *ahead, *atail ]

class TransformVisitor:

  def __init__ (self, stage: TransformStage) -> None:

    self.stage = stage

  @visitor.on ('node')
  def visit (self, node, scope: Scope, types: Types, collected: CollectList = None, prefix: List[CompositeType] = []) -> CollectList: # type: ignore

    raise SemanticException (node, 'falling through')

  @visitor.when (Block)
  def visit (self, node: Block, scope: Scope, types: Types, collected: CollectList = None, prefix: List[CompositeType] = []) -> CollectList: # type: ignore

    match self.stage:

      case TransformStage.COLLECT_IMPLEMENTS:

        acc = { }

        for stmt in node.stmts:

          last = self.visit (stmt, scope, types, collected = collected, prefix = prefix) # type: ignore

          if isinstance (last, dict):

            for name, list_ in last.items ():

              acc [name] = acc.get (name, [])
              acc [name] . extend (list_) # type: ignore

        return acc

      case TransformStage.TRIM_ATTRIBUTES:

        index = 0
        stmts = node.stmts

        while (len (stmts) > index):

          self.visit (stmt := stmts [index], scope, types, collected, prefix = prefix) # type: ignore

          if isinstance (stmt, VarParam) and len (prefix) > 0:

            param = Param (stmt.name, stmt.type_, line = stmt.line, column = stmt.column)
            stmts = [ *stmts [:index], param, *stmts [1 + index:] ]
            continue

          index = index + 1

        node.stmts = stmts

      case _:

        acc = { }

        for stmt in node.stmts:

          last = self.visit (stmt, scope, types, collected = collected, prefix = prefix) # type: ignore

          if isinstance (last, dict):

            acc = { **acc, **last } # type: ignore

        return acc

  @visitor.when (FunctionDecl)
  def visit(self, node: FunctionDecl, scope: Scope, types: Types, collected: CollectList = None, prefix: List[CompositeType] = []) -> CollectList: # type: ignore

    name = '.'.join ([ *map (lambda a: a.name, prefix), node.name ])

    match self.stage:

      case TransformStage.COLLECT_FUNCTIONS:

        return { name: node }

      case TransformStage.GUESS_ARGUMENTS:

        descent: Scope = Scope ()
        functy: FunctionType = scope [name] # type: ignore
        valid = [ set () for i in range (1 + len (functy.params)) ]

        for as_, type_ in scope.items ():

          descent [as_] = type_

        for alternative_ in alternate (functy):

          alternative: FunctionType = alternative_ # type: ignore
          descent [name] = alternative_

          try:

            TypingVisitor ().visit (node, descent, types, prefix = prefix) # type: ignore
          except SemanticException as e:

            continue

          for set_, type_ in zip (valid, [ alternative.type_, *alternative.params.values () ]):

            if not isinstance (type_, UnionType):

              assert (isinstance (type_, NamedType))
              set_.add (type_.name)

            else:

              for type_ in type_.types:

                set_.add (type_)

        if any ([ len (set_) == 0 for set_ in valid ]):

          raise SemanticException (node, 'can not guess function signature')

        params = OrderedDict ()
        valid = [ [ *map (lambda a: types [a], set_) ] for set_ in valid ]
        valid = [ set_[0] if len (set_) == 1 else UnionType (set_) for set_ in valid ]

        for key, set_ in zip (functy.params.keys (), valid [1:]):

          params [key] = set_

        functy._params = params
        functy._type_ = valid [0]

  @visitor.when (Param)
  def visit (self, node: Param, scope: Scope, types: Types, collected: CollectList = None, prefix: List[CompositeType] = []) -> CollectList: # type: ignore

    match self.stage:

      case TransformStage.COLLECT_PARAMS:

        if len (prefix) > 0:

          name = '.'.join ([ *map (lambda a: a.name, prefix), node.name ])
          type_ = prefix [-1].attributes [node.name]

          return { name: [ *alternate (type_) ] } # type: ignore

  @visitor.when (VarParam)
  def visit (self, node: VarParam, scope: Scope, types: Types, collected: CollectList = None, prefix: List[CompositeType] = []) -> CollectList: # type: ignore

    match self.stage:

      case TransformStage.TRIM_ATTRIBUTES:

        if len (prefix) > 0 and collected != None:

          name: str = '.'.join ([ *map (lambda a: a.name, prefix), CTOR_NAME ])
          ctor: FunctionDecl = collected [name] # type: ignore

          annot = { 'line': node.value.line, 'column': node.value.column }

          n_var = VariableValue (SELF_NAME, **annot)
          n_acc = ClassAccess (n_var, node.name, **annot)
          n_das = DestructiveAssignment (n_acc, node.value, **annot)

          ctor.body.stmts.insert (-1, n_das)

      case TransformStage.EXPAND_PROTOCOLS:

        name: str = '.'.join ([ *map (lambda a: a.name, prefix), node.name ])

        if isinstance (type_ := scope [name], ProtocolType): # type: ignore

          implements: List[Type] = collected [type_.name] # type: ignore

          scope [name] = (type_ := UnionType (implements))
          node.type_ = type_

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl, scope: Scope, types: Types, collected: CollectList = None, prefix: List[CompositeType] = []) -> CollectList: # type: ignore

    last: Dict[str, List[Type]] = { }

    match self.stage:

      case TransformStage.COLLECT_IMPLEMENTS:

        type_: CompositeType = types [node.name] # type: ignore

        for proto_ in filter (lambda t: isinstance (t, ProtocolType), [ v for k, v in types.items () ]):

          proto: ProtocolType = proto_ # type: ignore

          if proto.implementedBy (type_):

            last [proto.name] = last.get (proto.name, [])
            last [proto.name] . append (type_)

        return last # type: ignore

      case TransformStage.GUESS_PARAMS:

        assert (collected)

        base = '.'.join ([ *map (lambda a: a.name, prefix), node.name ])
        type_: CompositeType = types [node.name] # type: ignore

        attributes_: List[str] = [ *type_.attributes.keys () ]
        collected_: Dict[str, List[Type]] = collected # type: ignore
        valid: List[Set[Type]] = [ set () for i in range (len (attributes_)) ]

        for alternative in alternatelist ([ collected_ ['.'.join ([ base, name ])] for name in attributes_ ]):

          for name, attribute in zip (attributes_, alternative):

            type_.attributes [name] = attribute

          try:
            TypingVisitor ().visit (node, scope, types, prefix = prefix) # type: ignore
          except SemanticException:

            continue

          for set_, attribute in zip (valid, alternative):

            set_.add (attribute)

        if any ([ len (set_) == 0 for set_ in valid ]):

          raise SemanticException (node, 'can not guess type attribute types')

        for name, attribute in zip (attributes_, [ l[0] if len (l) == 1 else UnionType (l) for l in [ [*set_] for set_ in valid ] ]):

          type_.attributes [name] = attribute

      case _:

        return self.visit (node.body, scope, types, collected = collected, prefix = [ *prefix, types [node.name] ]) # type: ignore
