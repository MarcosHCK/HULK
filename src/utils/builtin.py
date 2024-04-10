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
import math
from semantic.type import AnyType
from semantic.type import CompositeType
from semantic.type import FunctionType
from semantic.type import ProtocolType
from semantic.type import SimpleType
from semantic.type import Type
from semantic.type import UnionType
from typing import Any, Dict, Tuple

class Constant:

  def __init__ (self, name: str, type_: Type):

    self.name = name
    self.type_ = type_

builtin_constants: Dict[str, Tuple[Type, Any]] = { }
builtin_types: Dict[str, Type] = { }
builtin_functions: Dict[str, Type] = { }

def BuiltinConstant (name: str, type_, value):

  builtin_constants [name] = (type_, value)
  return type_

def BuiltinType (type_):

  builtin_types [type_.name] = type_
  return type_

def BuiltinFunction (type_):

  builtin_functions [type_.name] = type_
  return type_

BASE_NAME = '@base'
CTOR_NAME = '@ctor'
SELF_NAME = '@self'

BASE_VARIABLE = 'base'
SELF_VARIABLE = 'self'

BOOLEAN_FALSE = 'false'
BOOLEAN_TRUE = 'true'
ITERABLE_NEXT = 'next'
ITERABLE_CURRENT = 'current'
PRINTABLE_TOSTRING = 'tostring'

BASE_TYPE = BuiltinType (CompositeType ('object', { }, { }))
BOOLEAN_TYPE = BuiltinType (SimpleType ('boolean'))
ITERABLE_TYPE = BuiltinType (ProtocolType ('iterable', { }, { }))
NUMBER_TYPE = BuiltinType (SimpleType ('number'))
PRINTABLE_TYPE = BuiltinType (ProtocolType ('printable', { }, { }))
STRING_TYPE = BuiltinType (SimpleType ('string'))

BASE_TYPE.methods [CTOR_NAME] = (STDLIB_BASECTOR := FunctionType (f'{CTOR_NAME}', OrderedDict (), BASE_TYPE))
ITERABLE_TYPE.methods [ITERABLE_CURRENT] = FunctionType (f'{ITERABLE_CURRENT}', OrderedDict (), AnyType ())
ITERABLE_TYPE.methods [ITERABLE_NEXT] = FunctionType (f'{ITERABLE_NEXT}', OrderedDict ({ 'a': AnyType () }), BOOLEAN_TYPE)
PRINTABLE_TYPE.methods [PRINTABLE_TOSTRING] = FunctionType (f'{PRINTABLE_TOSTRING}', OrderedDict (), STRING_TYPE)

MATH_E = BuiltinConstant ('E', NUMBER_TYPE, math.e)
MATH_PI = BuiltinConstant ('PI', NUMBER_TYPE, math.pi)

MATH_COS = BuiltinFunction (FunctionType ('cos', OrderedDict ({ 'n': NUMBER_TYPE }), NUMBER_TYPE))
MATH_EXP = BuiltinFunction (FunctionType ('exp', OrderedDict ({ 'n': NUMBER_TYPE }), NUMBER_TYPE))
MATH_LOG = BuiltinFunction (FunctionType ('log', OrderedDict ({ 'n': NUMBER_TYPE, 'n2': NUMBER_TYPE }), NUMBER_TYPE))
MATH_POW = BuiltinFunction (FunctionType ('pow', OrderedDict ({ 'n': NUMBER_TYPE, 'n2': NUMBER_TYPE }), NUMBER_TYPE))
MATH_RAND = BuiltinFunction (FunctionType ('rand', OrderedDict (), NUMBER_TYPE))
MATH_SIN = BuiltinFunction (FunctionType ('sin', OrderedDict ({ 'n': NUMBER_TYPE }), NUMBER_TYPE))
MATH_SQRT = BuiltinFunction (FunctionType ('sqrt', OrderedDict ({ 'n': NUMBER_TYPE }), NUMBER_TYPE))

STDLIB_CONCAT = BuiltinFunction (FunctionType ('concat', OrderedDict ({ 'a': STRING_TYPE, 'b': STRING_TYPE }), STRING_TYPE))
STDLIB_SITOS = BuiltinFunction (FunctionType ('sitos', OrderedDict ({ 'a': UnionType ([ NUMBER_TYPE, STRING_TYPE ]) }), STRING_TYPE))
STDLIB_PRINT = BuiltinFunction (FunctionType ('print', OrderedDict ({ 'a': UnionType ([ NUMBER_TYPE, STRING_TYPE ]) }), BOOLEAN_TYPE))
