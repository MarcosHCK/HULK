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
from functools import reduce
from typing import Any, Dict, Iterator, List
import llvmlite.ir as ir

from semantic.type import FunctionType, NamedType

TypeDict = Dict[str, ir.Type]
LinkDict = Dict[str, List[str]]

class IRTypes:

  @property
  def links (self) -> LinkDict:

    return self._links

  def __getitem__ (self, key: str) -> ir.Type:

    return self._store [key]

  def __init__ (self) -> None:

    self._links: LinkDict = { }
    self._store: TypeDict = { }

  def __iter__ (self) -> Iterator[str]:

    return self._store.__iter__ ()

  def __setitem__ (self, key: str, value: ir.Type) -> None:

    self._store [key] = value

  def function (self, name: str, params: List[ir.Type]) -> None | str:

    for name, _type_ in [ (link, self [link]) for link in self.links [name] ]:

      type_: ir.FunctionType = _type_ # type: ignore

      if type_.args == params: return name

    return None

  def get (self, key: str, default: Any) -> None | ir.Type:

    return self._store.get (key, default)

  def items (self):

    return self._store.items ()

  def link (self, name: str, as_: str) -> None:

    if (links := self._links.get (name, None)) == None:

      self._links [name] = (links := [])

    links.append (as_)

  @staticmethod
  def mangle (name: str, type_: FunctionType):

    params: Dict[str, NamedType] = type_.params # type: ignore
    return_type: NamedType = type_.type_ # type: ignore

    name = f'{name}['
    name = reduce (lambda a, e: f'{a}{e.name},', params.values (), name)
    name = f'{name}({return_type.name})]'

    return name
