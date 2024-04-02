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
from .base import TypeRef
from .base import Value
from typing import Optional

class Param (Value):

  def __init__ (self, name: str, typeref: TypeRef, **kwargs):

    super ().__init__ (**kwargs)

    self.name = name
    self.typeref = typeref

class VarParam (Param):

  def __init__ (self, name: str, typeref: TypeRef, value: Value, **kwargs):

    super ().__init__ (name = name, typeref = typeref, **kwargs)

    self.value = value
