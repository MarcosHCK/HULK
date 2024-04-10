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
from parser.ast.base import AstNode
from parser.ast.block import Block
from parser.ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from parser.ast.let import Let
from parser.ast.param import Param
from parser.ast.type import TypeRef
from semantic.exception import SemanticException
from semantic.scope import Scope
from semantic.type import AnyType, CompositeType, FunctionType, ProtocolType
from semantic.types import TypeDict, Types
from typing import List
import utils.visitor as visitor

ParentType = None | ProtocolDecl | TypeDecl

class CollectStage (Enum):

  COLLECT = 0
  LINK = 1

class CollectVisitor:

  def __init__(self, stage: CollectStage) -> None:

    self.stage = stage

  @visitor.on ('node')
  def visit (self, node: AstNode, scope: Scope, types: Types, prefix: List[str] = []) -> TypeDict: # type: ignore

    raise SemanticException (node, 'falling through')

  @visitor.when (Block)
  def visit (self, node: Block, scope: Scope, types: Types, prefix: List[str] = []) -> TypeDict: # type: ignore

    acc = { }

    for stmt in node.stmts:

      last = self.visit (stmt, scope, types, prefix = prefix) # type: ignore

      if isinstance (last, dict):

        for name, type_ in last.items ():

          acc [name] = type_

    return acc

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl, scope: Scope, types: Types, prefix: List[str] = []) -> TypeDict: # type: ignore

    name = '.'.join ([ *prefix, node.name ])

    match self.stage:

      case CollectStage.COLLECT:

        if scope.get (name, None) == None:

          scope [name] = (type_ := FunctionType (node.name, OrderedDict (), AnyType ()))
        else:

          raise SemanticException (node, f'redefining \'{name}\'')

      case CollectStage.LINK:

        assert (isinstance (type_ := scope [name], FunctionType))

        for param in node.params:

          if type_.params.get (param.name, None) != None:

            raise SemanticException (node, f'duplicated argument name \'{param.name}\'')
          else:

            assert (not param.type_ or isinstance (param.type_, TypeRef))

            type_.params [param.name] = AnyType () if not param.type_ else types [param.type_.name]

    return { node.name: type_ }

  @visitor.when (Let)
  def visit (self, node: Let, scope: Scope, types: Types, prefix: List[str] = []) -> TypeDict: # type: ignore

    for param in node.params:

      self.visit (param, scope, types, prefix = prefix) # type: ignore

  @visitor.when (Param)
  def visit (self, node: Param, scope: Scope, types: Types, prefix: List[str] = []) -> TypeDict: # type: ignore

    name = '.'.join ([ *prefix, node.name ])

    match self.stage:

      case CollectStage.COLLECT:

        type_ = AnyType ()

      case CollectStage.LINK:

        if scope.get (name, None) == None:

          type_ = AnyType () if not node.type_ else types [node.type_.name] # type: ignore
        else:

          raise SemanticException (node, f'redefining \'{name}\'')

        node.type_ = type_

    return { node.name: type_ }

  @visitor.when (ProtocolDecl | TypeDecl)
  def visit (self, node: ProtocolDecl | TypeDecl, scope: Scope, types: Types, prefix: List[str] = []) -> TypeDict:

    name = '.'.join ([ *prefix, node.name ])

    match self.stage:

      case CollectStage.COLLECT:

        if types.get (name, None) != None:

          raise SemanticException (node, f'redefining \'{name}\'')
        else:

          if isinstance (node, TypeDecl):

            types [name] = (type_ := CompositeType (node.name, { }, { }))
          else:

            types [name] = (type_ := ProtocolType (node.name, { }, { }))

        self.visit (node.body, scope, types, prefix = [ *prefix, name ]) # type: ignore

      case CollectStage.LINK:

        assert (isinstance (type_ := types [name], CompositeType))

        members = self.visit (node.body, scope, types, prefix = [ *prefix, name ]) # type: ignore

        for as_, member in members.items ():

          if not isinstance (member, FunctionType):

            type_.attributes [as_] = member
          else:

            type_.methods [as_] = member

    return { }
