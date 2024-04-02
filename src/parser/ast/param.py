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
from .base import Annotable
from .base import TypeRef
from .base import Value
from typing import Optional

class Param (Value, Annotable):

  def __init__ (self, name: str, annotation: TypeRef):

    super ().__init__ (typeref = annotation)

    self.name = name

class VarParam (Param):

  def __init__ (self, name: str, annotation: TypeRef, value: Value):

    super ().__init__ (name = name, annotation = annotation)

    self.value = value
