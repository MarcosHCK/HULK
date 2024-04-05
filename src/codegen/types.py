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
from parser.types import CTOR_NAME, CompositeType, FunctionType, ProtocolType, TypeRef
from typing import Any, Dict, List
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

  def fit (self, context: ir.Context, typeref: TypeRef) -> ir.Type:

    if (refty := self._store.get (typeref.name, None)) == None:

      if isinstance (typeref, CompositeType) and not isinstance (typeref, ProtocolType):

        self._store [typeref.name] = (refty := context.get_identified_type (typeref.name))

        attributes = filter (lambda e: isinstance (e, FunctionType) == False, typeref.members.values ())
        functions = filter (lambda e: isinstance (e, FunctionType) == True, typeref.members.values ())

        attributes = map (lambda e: self.fit (context, e), attributes) # type: ignore
        functions = reduce (lambda a, e: [ *self.fit_function (context, e), *a ], functions, []) # type: ignore
        functions = map (lambda e: ir.PointerType (e), functions)

        parent = ir.IntType (32) if not typeref.parent else self.fit (context, typeref.parent) # type: ignore

        refty.set_body (parent, *attributes, *functions)

      elif isinstance (typeref, FunctionType):

        self._store [typeref.name] = (alt := { })

        for typeref in alternate (typeref):

          alt [Types.mangle (typeref.name, typeref)] = (refty := ir.FunctionType (ir.VoidType (), []))

          refty.args = list (map (lambda e: self.fit (context, e), typeref.params)) # type: ignore
          refty.return_type = self.fit (context, typeref.typeref) # type: ignore

      elif not isinstance (typeref, ProtocolType):

        raise Exception (f'unknown type \'{str (typeref)}:{type (typeref)}\'')

    return refty

  def fit_function (self, context: ir.Context, typeref: FunctionType) -> List[ir.FunctionType]:

    self.fit (context, typeref)

    return self [typeref.name].values () # type: ignore

  def function (self, name: str, params: List[ir.Type]) -> None | str:

    alts: Dict[str, ir.FunctionType] = self [name] # type: ignore

    for name, alt in alts.items ():

      if alt.args == params: return name

    return None

  def get (self, key: str, default: Any = None) -> None | ir.Type:

    return self._store.get (key, default)

  @staticmethod
  def mangle (name:str, typeref: FunctionType) -> str:

    name = reduce (lambda a, e: f'{a}{e.name},', typeref.params, f'{name}[')
    name = f'{name}({typeref.typeref.name})]'

    return name
