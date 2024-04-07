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
from typing import Dict, List
from parser.ast.assignment import DestructiveAssignment
from parser.ast.base import AstNode
from parser.ast.block import Block
from parser.ast.decl import FunctionDecl, TypeDecl
from parser.ast.indirection import ClassAccess
from parser.ast.param import Param, VarParam
from parser.ast.value import VariableValue
from semantic.exception import SemanticException
from semantic.scope import Scope
from semantic.type import CompositeType, FunctionType, NamedType, UnionType
from semantic.types import Types
from semantic.typing import TypingVisitor
from utils.alternate import alternate
from utils.builtin import CTOR_NAME, SELF_NAME
import utils.visitor as visitor

CollectList = None | Dict[str, AstNode]

class TransformStage (Enum):

  COLLECT_FUNCTIONS = 1
  TRIM_ATTRIBUTES = 2
  GUESS_ARGUMENTS = 3

class TransformVisitor:

  def __init__ (self, stage: TransformStage) -> None:

    self.stage = stage

  @visitor.on ('node')
  def visit (self, node, scope: Scope, types: Types, collected: CollectList = None, prefix: List[CompositeType] = []) -> CollectList: # type: ignore

    raise SemanticException (node, 'falling through')

  @visitor.when (Block)
  def visit (self, node: Block, scope: Scope, types: Types, collected: CollectList = None, prefix: List[CompositeType] = []) -> CollectList: # type: ignore

    match self.stage:

      case TransformStage.COLLECT_FUNCTIONS | TransformStage.GUESS_ARGUMENTS:

        acc = { }

        for stmt in node.stmts:

          last = self.visit (stmt, scope, types, collected = collected, prefix = prefix) # type: ignore

          if isinstance (last, dict):

            acc = { **acc, **last } # type: ignore

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

        for alternative in alternate (functy):

          try:

            descent [name] = alternative
            TypingVisitor ().visit (node, descent, types, prefix = prefix) # type: ignore
          except SemanticException as e:

            continue

          for set_, type_ in zip (valid, [ alternative.type_, *alternative.params.values () ]):

            assert (isinstance (type_, NamedType))

            set_.add (type_.name)

        params = OrderedDict ()
        valid = [ [ *map (lambda a: types [a], set_) ] for set_ in valid ]
        valid = [ set_[0] if len (set_) == 1 else UnionType (set_) for set_ in valid ]

        for key, set_ in zip (functy.params.keys (), valid [1:]):

          params [key] = set_

        functy._params = params
        functy._type_ = valid [0]

  @visitor.when (VarParam)
  def visit (self, node: VarParam, scope: Scope, types: Types, collected: CollectList = None, prefix: List[CompositeType] = []) -> CollectList: # type: ignore

    match self.stage:

      case TransformStage.TRIM_ATTRIBUTES:

        if len (prefix) > 0 and collected != None:

          name: str = '.'.join ([ *map (lambda a: a.name, prefix), CTOR_NAME ])
          ctor: FunctionDecl = collected [name] # type: ignore

          ctor.body.stmts.insert (-1, DestructiveAssignment (ClassAccess (VariableValue (SELF_NAME), node.name), node.value))

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl, scope: Scope, types: Types, collected: CollectList = None, prefix: List[CompositeType] = []) -> CollectList: # type: ignore

    return self.visit (node.body, scope, types, collected = collected, prefix = [ *prefix, types [node.name] ]) # type: ignore
