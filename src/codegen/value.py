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
import llvmlite.ir as ir

#
# Abstract type
#

class IRValueBase (object):

  @property
  def type (self): return self._type

  def __init__ (self, type_: ir.Type, value: ir.Value, managed: bool = False) -> None:

    super ().__init__ ()

    self._managed = managed
    self._type = type_
    self._value = value

  def address (self, builder: ir.IRBuilder): raise Exception ('non-pointer value')
  def value (self, builder: ir.IRBuilder): return self._value

#
# Concrete types
#

class IRReference (IRValueBase):

  def __init__ (self, value: ir.Value, managed: bool = False) -> None:

    assert (isinstance (valuety := value.type, ir.PointerType)) # type: ignore

    super ().__init__ (valuety.pointee, value, managed = managed)

  def address (self, builder: ir.IRBuilder): return self._value
  def store (self, builder: ir.IRBuilder, value: ir.Value): builder.store (value, self.address (builder))
  def value (self, builder: ir.IRBuilder): return builder.load (self.address (builder))

class IRValue (IRValueBase):

  def __init__ (self, value: ir.Value) -> None:

    super ().__init__ (value.type, value) # type: ignore

class IRVariable (IRReference):

  def __init__ (self, builder: ir.IRBuilder, type_: ir.Type, managed: bool = False) -> None:

    super ().__init__ (builder.alloca (type_, 1), managed = managed)

  @staticmethod
  def create (builder: ir.IRBuilder, value: ir.Value):

    (self := IRVariable (builder, value.type)).store (builder, value) # type: ignore
    return self
