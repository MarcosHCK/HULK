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
from parser.ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from parser.ast.param import Param
from parser.semantic.exception import SemanticException
from parser.semantic.scope import Scope
from parser.types import AnyType, CompositeType, FunctionType, ProtocolType
import utils.visitor as visitor

class CollectorVisitor:

  def __init__(self, scope: Scope) -> None:

    self.scope = scope

  def dive (self, node: AstNode):

    scope = self.scope.clone ()
    collector = CollectorVisitor (scope)

    collector.visit (node) # type: ignore

    return scope.diff (self.scope)

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
    arr = list (dif.values ())

    ret = self.scope.derive (node.typeref or AnyType ())

    ref = FunctionType (node.name, arr, ret)

    if (last := self.scope.addv (node.name, ref)) != None:

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

    div = self.dive (node.body).variables

    ref = ProtocolType (node.name, dict (div), None)

    if (last := self.scope.addt (node.name, ref)) != None:

      if isinstance (last, ProtocolDecl):

        raise SemanticException (node, f'redefining protocol \'{last.name}\'')

      else:

        raise SemanticException (node, f'redefining type \'{last.name}\'')

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl) -> None:

    div = self.dive (node.body).variables

    ref = CompositeType (node.name, dict (div), None)

    if (last := self.scope.addt (node.name, ref)) != None:

      if isinstance (last, ProtocolDecl):

        raise SemanticException (node, f'redefining protocol \'{last.name}\'')

      else:

        raise SemanticException (node, f'redefining type \'{last.name}\'')
