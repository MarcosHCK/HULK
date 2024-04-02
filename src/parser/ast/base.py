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
from typing import Any

BASE_TYPE = 'Object'
ITERABLE_PROTOCOL = 'Iterable'

class AstNode:

  def __init__ (self, line: int = 0, column: int = 0, **kwargs):

    super ().__init__ ()

    self.line = line
    self.column = column

class Value (AstNode):

  def __init__ (self, **kwargs):

    super ().__init__ (**kwargs)

class TypeRef (AstNode):

  def __init__ (self, name: str, vector: bool, **kwargs):

    super ().__init__ (**kwargs)

    self.name = name
    self.vector = vector
