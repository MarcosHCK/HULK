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
from codegen.alternate import alternate
from codegen.frame import Frame
from codegen.types import Types
from parser.ast.block import Block
from parser.ast.decl import FunctionDecl, TypeDecl
from parser.types import CompositeType, FunctionType
from semantic.exception import SemanticException
from semantic.scope import Scope
from semantic.typing import TypingVisitor
from typing import Dict
import llvmlite.ir as ir
import utils.visitor as visitor

class CollectorVisitor:

  def __init__ (self, compose: None | CompositeType = None):

    self.compose = compose

  @visitor.on ('node')
  def visit (self, context: ir.Context, node, frame: Frame, scope: Scope, types: Types):

    pass

  @visitor.when (Block)
  def visit (self, context: ir.Context, node: Block, frame: Frame, scope: Scope, types: Types):

    for stmt in node.stmts:

      self.visit (context, stmt, frame, scope, types) # type: ignore

  @visitor.when (FunctionDecl)
  def visit (self, context: ir.Context, node: FunctionDecl, frame: Frame, scope: Scope, types: Types):

    fnname = node.name if not self.compose else f'{self.compose.name}.{node.name}'
    
    valid: Dict[str, ir.FunctionType] = { }
    typeref: FunctionType = scope.getv (fnname) # type: ignore

    for alt in alternate (typeref):

      d_scope = scope.clone ()
      d_types = types

      d_scope.variables [fnname] = alt

      try:

        TypingVisitor (d_scope, compose = self.compose).visit (node) # type: ignore

        d_types.fit (context, alt)

        alts: Dict[str, ir.FunctionType] = d_types [fnname] # type: ignore

        for name, alt in alts.items ():

          if self.compose:

            alt.args = [ ir.PointerType (types[self.compose.name]), *alt.args ] # type: ignore

          valid [name] = alt

      except SemanticException as e:

        pass

      d_types._store [fnname] = None

    types.add (fnname, valid) # type: ignore

  @visitor.when (TypeDecl)
  def visit (self, context: ir.Context, node: FunctionDecl, frame: Frame, scope: Scope, types: Types):

    compose: CompositeType
    types.fit (context, compose := scope.gett (node.name)) # type: ignore

    CollectorVisitor (compose = compose).visit (context, node.body, frame, scope, types) # type: ignore
