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
from codegen.alternate import alternate
from codegen.frame import Frame
from codegen.types import Types
from parser.ast.block import Block
from parser.ast.decl import FunctionDecl
from parser.types import FunctionType
from semantic.exception import SemanticException
from semantic.scope import Scope
import llvmlite.ir as ir
from semantic.typing import TypingVisitor
import utils.visitor as visitor

class CollectorVisitor:

  @visitor.on ('node')
  def visit (self, node, frame: Frame, scope: Scope, types: Types):

    pass

  @visitor.when (Block)
  def visit (self, node: Block, frame: Frame, scope: Scope, types: Types):

    for stmt in node.stmts:

      self.visit (stmt, frame, scope, types) # type: ignore

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl, frame: Frame, scope: Scope, types: Types):

    valid: Dict[str, ir.FunctionType] = { }
    typeref: FunctionType = scope.getv (node.name) # type: ignore

    for alt in alternate (typeref):

      d_scope = scope.clone ()
      d_types = types.clone ()

      d_scope.variables [node.name] = alt

      try:

        TypingVisitor (d_scope).visit (node) # type: ignore

        d_types.fit (alt)

        alts: Dict[str, ir.FunctionType] = d_types [node.name] # type: ignore

        for name, alt in alts.items ():

          valid [name] = alt

      except SemanticException:

        pass

    types.add (node.name, valid) # type: ignore
