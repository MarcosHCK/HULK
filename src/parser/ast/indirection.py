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
from parser.ast.base import Value
from parser.types import TypeRef

class Indirection (Value):

  def __init__ (self, base: Value, typeref: None | TypeRef = None, **kwargs):

    super ().__init__ (**kwargs)

    self.base = base
    self.typeref = typeref

class ClassAccess (Indirection):

  def __init__ (self, base: Value, field: str, **kwargs):

    super ().__init__ (base, **kwargs)

    self.field = field

class VectorAccess (Indirection):

  def __init__ (self, base: Value, index: Value, **kwargs):

    super ().__init__ (base, **kwargs)

    self.index = index
