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
from mimetypes import init
from ..ast.base import TypeRef
from typing import Dict

class Scope:

  def __init__ (self) -> None:

    self.variables: Dict[str, TypeRef] = { }

  def addv (self, name: str, typeref: TypeRef) -> None:

    self.variables[name] = typeref

  def getv (self, name: str) -> None | TypeRef:

    return self.variables.get (name)

  def clone (self):

    child = Scope ()

    child.variables = self.variables.copy ()

    return child