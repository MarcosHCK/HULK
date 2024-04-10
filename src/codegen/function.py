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
from typing import List
from codegen.value import IRValueBase
import llvmlite.ir as ir

class IRFunction (IRValueBase):

  @property
  def type (self) -> ir.FunctionType:

    return super ().type # type: ignore

  @property
  def candidates (self):

    first: IRFunction | None = self

    while first != None:

      yield first
      first = first._next

  @property
  def function (self):

    return self._value

  def __init__(self, type_: ir.FunctionType, value: ir.Value) -> None:

    super ().__init__ (type_, value)

    self._next: IRFunction | None = None

  def add_sibling (self, type_: ir.FunctionType, value: ir.Value) -> None:

    oldnext = self._next
    newnext = IRFunction (type_, value)

    self._next = newnext
    newnext._next = oldnext

  def call (self, builder: ir.IRBuilder, params: List[ir.Value], name: str = ''):

    if (func := self.candidate ([ param.type for param in params ])) == None: # type: ignore

      raise Exception ('no overload candidate found')
    else:

      return builder.call (func.value (builder), params, name = name)

  def candidate (self, params: List[ir.Type]):

    for func in self.candidates:

      if [ *func.type.args ] == params:

        return func

    return None

class IRMethod (IRFunction):

  def __init__ (self, base: ir.Value, type_: ir.FunctionType, value: ir.Value) -> None:

    super ().__init__ (type_, value)

    self._base = base

  def call (self, builder: ir.IRBuilder, params: List[ir.Value]):

    return super ().call (builder, [ self._base, *params ])
