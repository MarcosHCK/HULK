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
from ..ast.base import TypeRef
from typing import Any, Dict

class Scope:

  def __init__ (self) -> None:

    self.types: Dict[str, TypeRef] = { }
    self.variables: Dict[str, TypeRef] = { }

  def addt (self, name: str, typeref: TypeRef) -> None:

    self.types[name] = typeref

  def addv (self, name: str, typeref: TypeRef) -> None:

    self.variables[name] = typeref

  def derive (self, typeref: TypeRef) -> TypeRef:

    better = self.gett (typeref.name)

    if not better:

      return typeref
    else:

      better = better.clone ()

      better.vector = typeref.vector

      return better

  def diff (self, other):

    o_types: Dict[str, TypeRef] = other.types
    o_variables: Dict[str, TypeRef] = other.variables
    scope = Scope ()

    for name, type in self.types.items ():

      if o_types.get (name) == None:

        scope.addt (name, type)

    for name, variable in self.variables.items ():

      if o_variables.get (name) == None:

        scope.addv (name, variable)

    return scope

  def gett (self, name: str, default: Any = None) -> None | TypeRef:

    return self.types.get (name, default)

  def getv (self, name: str, default: Any = None) -> None | TypeRef:

    return self.variables.get (name, default)

  def clone (self):

    child = Scope ()

    child.types = self.types.copy ()
    child.variables = self.variables.copy ()

    return child
