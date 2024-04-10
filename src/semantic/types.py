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
from semantic.type import Type, TypeDict
from typing import Any, Dict, Iterator

class Types:

  def __getitem__ (self, key: str) -> Type:

    return self._store [key]

  def __init__ (self) -> None:

    self._store: TypeDict = { }

  def __iter__ (self) -> Iterator[str]:

    return self._store.__iter__ ()

  def __setitem__ (self, key: str, value: Type) -> None:

    self._store [key] = value

  def get (self, key: str, default: Any) -> None | Type:

    return self._store.get (key, default)

  def items (self):

    return self._store.items ()
