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
from cgi import print_arguments
from typing import Dict, List

class TypeRef:

  def clone (self, **kwargs):

    child = TypeRef (self.name, self.vector, **kwargs)

    return child

  def __eq__(self, __value: object) -> bool:

    if not isinstance (__value, TypeRef):

      return super ().__eq__ (__value)
    else:

      return self.name == __value.name and self.vector == __value.vector

  def __init__ (self, name: str, vector: bool, **kwargs):

    super ().__init__ ()

    self.name = name
    self.vector = vector

  def __str__ (self) -> str:

    return f'{self.name}{"" if not self.vector else "[]"}'

class AnyType (TypeRef):

  def clone (self, **kwargs):

    child = AnyType (**kwargs)

    return child

  def __eq__(self, __value: object) -> bool:

    if not isinstance (__value, TypeRef):

      return super ().__eq__ (__value)

    else:

      return True

  def __init__ (self, **kwargs):

    super ().__init__ (name = 'any', vector = False, **kwargs)

class CompositeType (TypeRef):

  def clone (self, **kwargs):

    child = CompositeType (self.name, self.members, **kwargs)

    return child

  def __eq__ (self, __value: object) -> bool:

    if not isinstance (__value, CompositeType):

      return super ().__eq__ (__value)

    else:

      return super ().__eq__ (__value) and self.members == __value.members

  def __init__ (self, name: str, members: Dict[str, TypeRef], **kwargs):

    super ().__init__ (name = name, vector = kwargs.get ('vector', False))

    self.members = members

class FunctionType (TypeRef):

  def clone (self, **kwargs):

    child = FunctionType (self.name, self.params, self.typeref, **kwargs)

    return child

  def __eq__ (self, __value: object) -> bool:

    if not isinstance (__value, FunctionType):

      return super ().__eq__ (__value)

    else:

      return super ().__eq__ (__value) and self.typeref == __value.typeref and self.params == __value.params

  def __init__ (self, name: str, params: List[TypeRef], typeref: TypeRef, **kwargs):

    super ().__init__ (name = name, vector = kwargs.get ('vector', False))

    self.params = params
    self.typeref = typeref

  def __str__ (self) -> str:

    return f'{self.name} ({", ".join (list (map (lambda a: str (a), self.params)))}) -> {self.typeref}'

class ProtocolType (CompositeType):

  def clone (self, **kwargs):

    child = ProtocolType (self.name, self.members, **kwargs)

    return child

  def __eq__ (self, __value: object) -> bool:

    if not isinstance (__value, CompositeType):

      return super ().__eq__ (__value)

    else:

      for name, member in self.members.items ():

        other = __value.members.get (name)

        print (other, member, other == None, other != member)

        if other == None or other != member:

          return False

      return True

  def __init__ (self, name: str, members: Dict[str, TypeRef], **kwargs):

    super ().__init__ (name = name, members = members, vector = kwargs.get ('vector', False))
