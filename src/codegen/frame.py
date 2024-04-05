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
from enum import Enum
from typing import Dict
import llvmlite.ir as ir

class Mode (Enum):

  INDIRECT = 1
  INVOKE = 2
  NORMAL = 0

class Frame:

  @property
  def locals (self): return self._locals
  @property
  def mode (self) -> Mode: return self._mode
  @mode.setter
  def mode (self, value: Mode): self._mode = value

  def __getitem__ (self, key: str) -> ir.Value:

    return self._store [key]

  def __init__ (self, mode: Mode = Mode.NORMAL, store: None | Dict[str, ir.Value] = None):

    self._locals: Dict[str, ir.Value] = { }
    self._mode: Mode = mode
    self._store: Dict[str, ir.Value] = store or { }

  def __setitem__ (self, key: str, value: ir.Value) -> None:

    self._store [key] = value
    self._locals [key] = value

  def clone (self, mode: None | Mode = None, store: None | Dict[str, ir.Value] = None):

    child = Frame (mode = mode or self.mode, store = store or { **self._store })

    return child
