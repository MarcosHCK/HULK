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
from semantic.type import Type
from typing import List

class FunctionDecl (AstNode):

  def __init__ (self, name: str, params: List[Param], type_: None | Type, body: Block, **kw):

    super ().__init__ (**kw)

    self.body = body
    self.name = name
    self.params = params
    self.type_ = type_

class ProtocolDecl (AstNode):

  def __init__ (self, name: str, parent: str, body: Block, **kw):

    super ().__init__ (**kw)

    self.body = body
    self.name = name
    self.parent = parent

class TypeDecl (AstNode):

  def __init__ (self, name: str, parent: str, body: Block, **kw):

    super ().__init__ (**kw)

    self.body = body
    self.name = name
    self.parent = parent
