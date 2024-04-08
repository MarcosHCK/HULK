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
from typing import Any, Dict, Iterator, Self
import llvmlite.ir as ir

ValueDict = Dict[str, ir.Value]

class IRFrame:

  @property
  def locals (self) -> ValueDict:

    return self._locals

  def __getitem__ (self, key: str) -> ir.Value:

    return self._store [key]

  def __init__ (self) -> None:

    self._locals: ValueDict = { }
    self._store: ValueDict = { }

  def __iter__ (self) -> Iterator[str]:

    return self._store.__iter__ ()

  def __setitem__ (self, key: str, value: ir.Value) -> None:

    self._locals [key] = value
    self._store [key] = value

  def clone (self):

    child = IRFrame ()

    child._store = { **self._store }

    return child

  def get (self, key: str, default: Any) -> None | ir.Value:

    return self._store.get (key, default)

  def items (self):

    return self._store.items ()
