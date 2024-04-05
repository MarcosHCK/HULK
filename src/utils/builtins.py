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
from parser.types import AnyType
from parser.types import CompositeType
from parser.types import CTOR_NAME
from parser.types import FunctionType
from parser.types import ProtocolType
from parser.types import TypeRef
from typing import List

class BuiltinType:

  def __init__ (self, name: str, typeref: TypeRef):

    self.name = name
    self.typeref = typeref

    builtin_types.append (self)

class BuiltinValue:

  def __init__ (self, value: str, typeref: TypeRef):

    self.value = value
    self.typeref = typeref

    builtin_values.append (self)

builtin_types: List[BuiltinType] = [ ]
builtin_values: List[BuiltinValue] = [ ]

BOOLEAN_FALSE = 'false'
BOOLEAN_TRUE = 'true'

BASE_TYPE = BuiltinType ('object', CompositeType ('object', { }))
ITERABLE_TYPE = BuiltinType ('iterable', ProtocolType ('iterable', { 'current': FunctionType ('current', [ ], AnyType ()), 'next': FunctionType ('next', [ ], AnyType ()), }))
BOOLEAN_TYPE = BuiltinType ('boolean', TypeRef ('boolean', False))
NUMBER_TYPE = BuiltinType ('number', TypeRef ('number', False))
STRING_TYPE = BuiltinType ('string', TypeRef ('string', False))

if True:

  func: CompositeType = BASE_TYPE.typeref # type: ignore
  type: FunctionType = FunctionType (CTOR_NAME, [ ], BASE_TYPE.typeref)

  func.members [CTOR_NAME] = type

MATH_COS = BuiltinValue ('cos', FunctionType ('cos', [ NUMBER_TYPE.typeref ], NUMBER_TYPE.typeref))
MATH_EXP = BuiltinValue ('exp', FunctionType ('exp', [ NUMBER_TYPE.typeref ], NUMBER_TYPE.typeref))
MATH_LOG = BuiltinValue ('log', FunctionType ('log', [ NUMBER_TYPE.typeref, NUMBER_TYPE.typeref ], NUMBER_TYPE.typeref))
MATH_POW = BuiltinValue ('pow', FunctionType ('pow', [ NUMBER_TYPE.typeref, NUMBER_TYPE.typeref ], NUMBER_TYPE.typeref))
MATH_RAND = BuiltinValue ('rand', FunctionType ('rand', [ ], NUMBER_TYPE.typeref))
MATH_SIN = BuiltinValue ('sin', FunctionType ('sin', [ NUMBER_TYPE.typeref ], NUMBER_TYPE.typeref))
MATH_SQRT = BuiltinValue ('sqrt', FunctionType ('sqrt', [ NUMBER_TYPE.typeref ], NUMBER_TYPE.typeref))

MATH_E = BuiltinValue ('E', NUMBER_TYPE.typeref)
MATH_PI = BuiltinValue ('PI', NUMBER_TYPE.typeref)

STDLIB_PRINT = BuiltinValue ('print', FunctionType ('print', [ NUMBER_TYPE.typeref ], BOOLEAN_TYPE.typeref))
