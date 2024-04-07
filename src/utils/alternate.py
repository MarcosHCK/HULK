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
from collections import OrderedDict
from semantic.type import FunctionType, Type, UnionType
from typing import Generator, List

def alternate (typeref: FunctionType) -> Generator[FunctionType, None, None]:

  if len (typeref.params) == 0:

    for atyperef in alternative (typeref.type_):

      yield FunctionType (typeref.name, OrderedDict (), atyperef)

  else:

    keys = list (typeref.params.keys ())

    for atyperef in alternative (typeref.type_):

      for aparams in alternatives ([ *typeref.params.values () ]):

        params = OrderedDict ()

        for key, value in zip (keys, aparams):

          params [key] = value

        yield FunctionType (typeref.name, params, atyperef)

def alternative (ref: Type) -> Generator[Type, None, None]:

  if not isinstance (ref, UnionType):

    yield ref

  else:

    for fellow in ref.types:

      yield fellow

def alternatives (lref: List[Type]) -> Generator[List[Type], None, None]:

  if len (lref) == 1:

    for aret in alternative (lref[0]):

      yield [ aret ]

  elif len (lref) > 0:

    head = lref[0]
    tail = lref[1:]

    for atail in alternatives (tail):

      for ahead in alternative (head):

        yield [ ahead, *atail ]
