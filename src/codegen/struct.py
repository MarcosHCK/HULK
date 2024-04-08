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
from collections import namedtuple
from codegen.irtypes import TypeDict
from typing import Dict, Iterable, Self
import llvmlite.ir as ir

Index = namedtuple ('Index', [ 'depth', 'order' ])
IndexDict = Dict[str, Index]

class IRMethod (ir.Function):

  def __init__ (self, module, ftype, name):

    super ().__init__ (module, ftype, name)

class IRMethodInvoke (ir.Value):

  def __init__ (self, instance: ir.Value, function: ir.Value) -> None:

    super ().__init__ ()

    self._instance = instance
    self._function = function

  def call (self, builder: ir.IRBuilder, arguments: Iterable[ir.Value]):

    arguments = [ self._instance, *arguments ]

    return builder.call (self._function, arguments)

class IRMethodType (ir.FunctionType):

  def __init__ (self, return_type, args, var_arg = False):

    super ().__init__ (return_type, args, var_arg)

class IRStructType (ir.Type):

  @property
  def name (self): return self._name
  @property
  def type (self): return self._type

  @property
  def attributes (self): return self._attributes
  @property
  def methods (self): return self._methods
  @property
  def parent (self): return self._parent

  @attributes.setter
  def attributes (self, value: TypeDict): self._attributes = value
  @methods.setter
  def methods (self, value: TypeDict): self._methods = value
  @parent.setter
  def parent (self, value: Self): self._parent = value

  def __init__ (self, context: ir.Context, name: str, packed: bool = False):
    
    super ().__init__ ()

    self._index: IndexDict = {}
    self._name: str = name
    self._size = None
    self._type = context.get_identified_type (name)

    self._attributes: TypeDict = { }
    self._methods: TypeDict = { }
    self._parent: None | Self = None

  def complete (self, module: ir.Module) -> int:

    if not self._size:

      index = 0
      fields = [ ]

      if self.parent:

        index = self.parent.complete (module)

      for name, type_ in self.attributes.items ():

        if self._index.get (name) != None:

          raise Exception (f'duplicated struct member \'{name}\'')
        else:

          fields.append (type_)
          self._index [name] = Index (0, index)
          index = index + 1

      for name, type_ in self.methods.items ():

        depth = 0
        for_ = None
        first = self

        while (first := first.parent) != None:

          depth = depth + 1

          if (for_ := first._index.get (name, None)) != None:
            break

        self._index [name] = Index (depth if for_ != None else 0, for_ if for_ != None else index)
        index = index if for_ != None else 1 + index

        if not for_:

          fields.append (type_.as_pointer ())

      self._type.set_body (*fields)
      self._size = index

    return self._size

  def gep (self, builder: ir.IRBuilder, value: ir.Value, name: str):

    depth, index = self._index [name]
    first = self

    for i in range (depth):

      value = builder.extract_value (value, 0)
      first = first.parent # type: ignore

    return builder.extract_value (value, index)

  def _to_string (self):

    return self._type._to_string ()
