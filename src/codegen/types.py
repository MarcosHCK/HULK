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
from functools import reduce
from parser.types import CompositeType, FunctionType, TypeRef
from typing import List
import llvmlite.ir as ir

class Types:

  def __getitem__ (self, key: str) -> ir.Type:

    return self._store [key]

  def __init__ (self) -> None:

    self._store = { }

  def add (self, name: str, type_: ir.Type) -> None | ir.Type:

    was = self._store.get (name, None)

    self._store [name] = type_
    return was

  def clone (self):

    child = Types ()

    for name, type_ in self._store.items ():

      child._store [name] = type_

    return child

  def fit (self, typeref: TypeRef) -> ir.Type:

    if (refty := self._store.get (typeref.name, None)) == None:

      if isinstance (typeref, CompositeType):

        self._store [typeref.name] = (refty := ir.LiteralStructType ([]))

        refty.elements = list (map (lambda e: self.fit (e), typeref.members.values ())) # type: ignore

      elif isinstance (typeref, FunctionType):

        self._store [typeref.name] = (alt := { })

        for typeref in alternate (typeref):

          alt [Types.mangle (typeref.name, typeref)] = (refty := ir.FunctionType (ir.VoidType (), []))

          refty.args = list (map (lambda e: self.fit (e), typeref.params)) # type: ignore
          refty.return_type = self.fit (typeref.typeref) # type: ignore

      else: raise Exception (f'unknown type \'{str (typeref)}\'')

    return refty

  @staticmethod
  def mangle (name:str, typeref: FunctionType) -> str:

    name = reduce (lambda a, e: f'{a}{e.name},', typeref.params, f'{name}[')
    name = f'{name}({typeref.typeref.name})]'

    return name
