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
from parser.ast.base import AstNode
from parser.ast.block import Block
from parser.ast.decl import TypeDecl
from parser.ast.param import Param
from semantic.exception import SemanticException
from semantic.scope import Scope
from semantic.type import CompositeType, UnionType
from semantic.types import Types
from typing import List
from semantic.typing import TypingVisitor
import utils.visitor as visitor

class ComplainVisitor:

  @visitor.on ('node')
  def visit (self, node: AstNode, scope: Scope, types: Types, prefix: List[CompositeType] = []):

    raise SemanticException (node, 'falling through')

  @visitor.when (Block)
  def visit (self, node: Block, scope: Scope, types: Types, prefix: List[CompositeType] = []):

    for stmt in node.stmts:

      self.visit (stmt, scope, types, prefix = prefix) # type: ignore

  @visitor.when (Param)
  def visit (self, node: Param, scope: Scope, types: Types, prefix: List[CompositeType] = []):

    if len (prefix) > 0:

      type_ = prefix[-1].attributes [node.name]

      if isinstance (type_, UnionType):

        tail = ', '.join (map (lambda a: TypingVisitor.describe (a), type_.types [:-1]))
        expect = f'{tail} or {TypingVisitor.describe (type_.types [-1])}'

        raise SemanticException (node, f'can not guess attribute type, candidates are {expect}')

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl, scope: Scope, types: Types, prefix: List[CompositeType] = []):

    self.visit (node.body, scope, types, prefix = [ *prefix, types [node.name] ]) # type: ignore
