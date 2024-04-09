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
from heapq import merge
from typing import Any, Dict, List, OrderedDict, Self, Set

#
# Abstract base classes
#

class Type (object):

  def __init__ (self, **kw) -> None:

    super ().__init__ ()

  @staticmethod
  def compare_types (a, b, strict: bool = False) -> bool:

    if isinstance (a, AnyType): return True if not strict else isinstance (b, AnyType)
    elif isinstance (a, UnionType): return any ([ Type.compare_types (t, b) for t in a.types ]) and (True if not strict else isinstance (b, UnionType) and len (a.types) == len (b.types))
    elif isinstance (a, ProtocolType) and isinstance (b, ProtocolType): return a.name == b.name if strict else b.castableTo (a)
    elif isinstance (a, ProtocolType) and isinstance (b, CompositeType): return a.name == b.name if strict else a.implementedBy (b)
    elif isinstance (a, CompositeType) and isinstance (b, CompositeType): return a.name == b.name if strict else b.castableTo (a)
    elif isinstance (a, NamedType) and isinstance (b, NamedType): return a.name == b.name
    elif isinstance (b, AnyType): return True
    elif isinstance (b, UnionType): return any ([ Type.compare_types (a, t) for t in b.types ]) and (True if not strict else isinstance (a, UnionType) and len (a.types) == len (b.types))
    else: return a == b

  @staticmethod
  def merge (a, b):

    if isinstance (a, UnionType):

      if not isinstance (b, UnionType):

        return Type.merge (a, UnionType ([ b ]))
      else:

        types: Dict[str, Type] = { }

        for type_ in a.types: types [type_.name] = type_ # type: ignore
        for type_ in b.types: types [type_.name] = type_ # type: ignore
        return UnionType ([ *types.values () ])

    elif isinstance (b, UnionType):

      return Type.merge (b, UnionType ([ a ]))
    else:

      return Type.merge (UnionType ([ a ]), UnionType ([ b ]))

TypeDict = Dict[str, Type]

class NamedType (Type):

  def __init__ (self, name: str, **kw) -> None:

    super ().__init__ (**kw)

    self.name = name

#
# Concrete types
#
    
class AnyType (Type):

  def __init__ (self) -> None:

    super ().__init__ ()

class CompositeType (NamedType):

  @property
  def attributes (self):

    return self._attributes

  @property
  def methods (self):

    return self._methods

  @property
  def parent (self):

    return self._parent

  @parent.setter
  def parent (self, parent: None | Self = None) -> None:

    self._parent = parent

  def __getitem__ (self, key: str) -> Type:

    assert (type_ := self.member (key))
    return type_

  def __init__ (self, name: str, attributes: Dict[str, Type], methods: Dict[str, Type], parent: None | Self = None) -> None:

    super ().__init__ (name)

    self._attributes = attributes
    self._methods = methods
    self._parent = parent

  def castableTo (self, other: Self) -> bool:

    first = self

    while (first) != None:

      if Type.compare_types (first, other, True):

        return True

      first = first.parent

    return False

  def circular (self, parent: None | Self):

    while (first := parent) != None:

      if Type.compare_types (first, self, True):

        return True

      parent = first.parent

    return False

  def get (self, key: str, default: Any = None) -> Any | Type:

    return self.member (key, True) or default

  def member (self, key: str, attr: bool = True) -> None | Type:

    if attr and (got := self._attributes.get (key, None)) != None:

      return got
    elif (got := self._methods.get (key, None)) != None:

      return got
    elif self._parent != None:

      return self._parent.member (key, False)

    return None

class FunctionType (NamedType):

  @property
  def params (self):

    return self._params

  @property
  def type_ (self):

    return self._type_

  @type_.setter
  def type_ (self, value: Type) -> None:

    self._type_ = value

  def __init__ (self, name: str, params: OrderedDict[str, Type], type_: Type) -> None:

    super ().__init__ (name)

    self._params = params
    self._type_ = type_

class ProtocolType (CompositeType):

  def __init__ (self, name: str, attributes: Dict[str, Type], methods: Dict[str, Type], parent: None | Self = None) -> None:

    super ().__init__ (name, attributes, methods, parent)

  def implementedBy (self, other: CompositeType) -> bool:

    for name, type_ in ({ **self.attributes, **self.methods }).items ():

      if not Type.compare_types (other.get (name, None), type_):
        return False

    return self.parent == None or self.parent.implementedBy (other)

class Ref (NamedType):

  def __init__(self, name: str) -> None:

    super ().__init__ (name)

class SimpleType (NamedType):

  def __init__ (self, name: str) -> None:

    super ().__init__ (name)

class UnionType (Type):

  @property
  def types (self):

    return self._types

  def __init__ (self, types: List[Type]) -> None:

    super ().__init__ ()

    self._types = types

class VectorType (Type):

  @property
  def type_ (self):

    return self._type_

  def __init__ (self, type_: Type) -> None:

    super ().__init__ ()

    self._type_ = type_
