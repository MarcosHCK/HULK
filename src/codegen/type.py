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
from codegen.function import IRFunction, IRMethod
from codegen.value import IRReference, IRValue, IRValueBase
from collections import namedtuple
from enum import Enum
from typing import Dict, List, Self
import llvmlite.ir as ir

PARENT_FIELD = '@parent'

Index = namedtuple ('Index', [ 'depth', 'order', 'type' ])
IndexDict = Dict[str, Index]

MethodDict = Dict[str, List[ir.FunctionType]]
TypeDict = Dict[str, ir.Type]

class FieldType (Enum):

  ATTRIBUTE = 0
  METHOD = 1

class IRType (ir.PointerType):

  @property
  def attributes (self): return self._attributes
  @property
  def methods (self): return self._methods
  @property
  def name (self): return self._name
  @property
  def parent (self): return self._parent

  @attributes.setter
  def attributes (self, value: TypeDict): self._attributes = value
  @methods.setter
  def methods (self, value: MethodDict): self._methods = value
  @parent.setter
  def parent (self, value: Self): self._parent = value

  def __init__ (self, context: ir.Context, name: str):

    self._name = name
    self._type = context.get_identified_type (name)

    self._attributes: TypeDict = { }
    self._index: IndexDict = {}
    self._methods: MethodDict = { }
    self._parent: None | Self = None

    super ().__init__ (self._type)

  @staticmethod
  def check_signature (type_: ir.FunctionType, against: ir.FunctionType):

    return type_.args [1:] == against.args [1:] and type_.return_type == against.return_type

  @staticmethod
  def check_signatures (types: List[ir.FunctionType], against: List[ir.FunctionType]):

    return len (types) == len (against) and not any ([ not IRType.check_signature (a, b) for a, b in zip (against, types) ])

  def complete (self, module: ir.Module):

    if self._type.is_opaque:

      index = 0
      fields = [ ]

      if self.parent:

        self.parent.complete (module)

        fields.append (self.parent._type)
        index = index + 1

      for name, type_ in self.attributes.items ():

        if self._index.get (name) != None:

          raise Exception (f'duplicated struct member \'{name}\'')
        else:

          fields.append (type_)
          self._index [name] = Index (0, index, FieldType.ATTRIBUTE)
          index = index + 1

      for name, types in self.methods.items ():

        depth = 0
        for_ = None
        first = self

        while (first := first.parent) != None:

          depth = depth + 1

          if (against := first.methods.get (name, None)) != None and IRType.check_signatures (types, against):

            for_ = first._index [name]
            break

        if for_ != None:

          self._index [name] = Index (depth, for_.order, FieldType.METHOD)
        else:

          self._index [name] = Index (0, indeces := [], FieldType.METHOD)

          for i, type_ in enumerate (types):

            indeces.append (i + index)
            fields.append (type_.as_pointer ())

          index = index + len (types)

      self._type.set_body (*fields)
      self._size = index

  def create (self, builder: ir.IRBuilder):

    return IRReference (builder.alloca (self._type, 1))

  def index (self, builder: ir.IRBuilder, value: ir.Value, name: str) -> IRValueBase:

    _, _, field_type = self._index [name]

    match field_type:

      case FieldType.ATTRIBUTE:

        value, _ = next (self.index_bare (builder, value, name))
        return IRReference (value)

      case FieldType.METHOD:

        head: IRMethod | None = None

        for func, type_ in self.index_bare (builder, value, name):

          if not head:

            head = IRMethod (value, type_, builder.load (func)) # type: ignore
          else:

            head.add_sibling (type_, builder.load (func)) # type: ignore

        return head # type: ignore

      case _: raise Exception (f'unknown field type {field_type}')

  def index_bare (self, builder: ir.IRBuilder, value: ir.Value, name: str):

    field_type: FieldType
    assert (isinstance (value.type, ir.PointerType)) # type: ignore
    assert (isinstance (value.type.pointee, ir.IdentifiedStructType)) # type: ignore
    assert (value.type.pointee == self._type) # type: ignore

    depth, at, field_type = self._index [name]
    first = (last := self)

    for i in range (depth):

      assert (first)
      assert (self.parent)

      field_offset = ir.Constant (ir.IntType (32), 0)
      pointer_offset = ir.Constant (ir.IntType (32), 0)

      value = builder.gep (value, [ field_offset, pointer_offset ])
      value = builder.bitcast (value, self.parent) # type: ignore

      first = (last := first).parent # type: ignore

    match field_type:

      case FieldType.ATTRIBUTE:

        index: int = at
        field_offset = ir.Constant (ir.IntType (32), 0)
        pointer_offset = ir.Constant (ir.IntType (32), index)
        type_ = last.attributes [name]

        yield (builder.gep (value, [ field_offset, pointer_offset ]), type_)

      case FieldType.METHOD:

        indices: List[int] = at

        assert (len (indices) > 0)
        assert (len (indices) == len (last.methods [name]))

        for index, type_ in zip (indices, last.methods [name]):

          field_offset = ir.Constant (ir.IntType (32), 0)
          pointer_offset = ir.Constant (ir.IntType (32), index)

          yield (builder.gep (value, [ field_offset, pointer_offset ]), type_)

      case _: raise Exception (f'unknown field type {field_type}')
