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
from typing import Dict
from parser.ast.base import AstNode
from parser.ast.block import Block
from parser.ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from parser.ast.param import Param
from parser.types import AnyType, CompositeType, FunctionType, ProtocolType, TypeRef
from semantic.exception import SemanticException
from semantic.scope import Scope
import utils.visitor as visitor

ParentDecl = None | ProtocolDecl | TypeDecl

class CollectorVisitor:

  def __init__(self, scope: Scope, compose: ParentDecl = None) -> None:

    self.compose = compose
    self.scope = scope

  def dive (self, node: AstNode, compose: ParentDecl = None):

    scope = self.scope.clone ()
    collector = CollectorVisitor (scope, compose = compose)

    collector.visit (node) # type: ignore

    return scope.diff (self.scope)

  def post (self, fields: Dict[str, TypeRef]):

    for name, field in fields.items ():

      if isinstance (field, FunctionType):

        self.scope.addv (name, FunctionType (name, field.params, field.typeref))

  @visitor.on ('node')
  def visit (self, node):

    pass

  @visitor.when (Block)
  def visit (self, node: Block) -> None:

    for stmt in node.stmts:

      self.visit (stmt) # type: ignore

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl) -> None:

    dif = self.dive (node.params).variables # type: ignore

    ret = self.scope.derive (node.typeref or AnyType ())

    ref = FunctionType (node.name, list (dif.values ()), ret)

    name = node.name if not self.compose else f'{self.compose.name}.{node.name}'

    if (last := self.scope.addv (name, ref)) != None:

      if isinstance (last, FunctionType):

        raise SemanticException (node, f'redefining function \'{last.name}\'')

      else:

        raise SemanticException (node, f'redefining variable \'{last.name}\'')

  @visitor.when (list)
  def visit (self, list: list):

    for param in list:

      self.visit (param) # type: ignore

  @visitor.when (Param)
  def visit (self, node: Param) -> None:

    ref = self.scope.derive (node.typeref or AnyType ())

    if (last := self.scope.addv (node.name, ref)) != None:

      if isinstance (last, FunctionType):

        raise SemanticException (node, f'redefining function \'{last.name}\'')

      else:

        raise SemanticException (node, f'redefining variable \'{last.name}\'')

  @visitor.when (ProtocolDecl)
  def visit (self, node: ProtocolDecl) -> None:

    self.post (div := self.dive (node.body, node).variables)

    ref = ProtocolType (node.name, { name.removeprefix (f'{node.name}.'): ref for name, ref in div.items () }, None)

    if (last := self.scope.addt (node.name, ref)) != None:

      if isinstance (last, ProtocolDecl):

        raise SemanticException (node, f'redefining protocol \'{last.name}\'')

      else:

        raise SemanticException (node, f'redefining type \'{last.name}\'')

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl) -> None:

    self.post (div := self.dive (node.body, node).variables)

    ref = CompositeType (node.name, { name.removeprefix (f'{node.name}.'): ref for name, ref in div.items () }, None)

    if (last := self.scope.addt (node.name, ref)) != None:

      if isinstance (last, ProtocolDecl):

        raise SemanticException (node, f'redefining protocol \'{last.name}\'')

      else:

        raise SemanticException (node, f'redefining type \'{last.name}\'')
