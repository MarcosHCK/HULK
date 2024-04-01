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
from parser.ast.param import Param
from typing import List

class FunctionDecl (AstNode):

  def __init__ (self, name: str, arguments: List[Param], annotation: AstNode, body: Block):

    super ().__init__ ()

    self.annotation = annotation
    self.arguments = arguments
    self.body = body
    self.name = name

class ProtocolDecl (AstNode):

  def __init__ (self, name: str, parent: str, body: List[AstNode]):

    super ().__init__ ()

    self.body = body
    self.name = name
    self.parent = parent

class TypeDecl (AstNode):

  def __init__ (self, name: str, params: List[AstNode], parent: str, parentctor: List[AstNode], body: List[AstNode]):

    super ().__init__ ()

    self.body = body
    self.name = name
    self.params = params
    self.parent = parent
    self.parentctor = parentctor
