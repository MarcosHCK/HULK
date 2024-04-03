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
from parser.types import CompositeType, TypeRef

BASE_TYPENAME = 'object'
BOOLEAN_TYPENAME = 'boolean'
DEFAULT_TYPENAME = 'default'
ITERABLE_PROTOCOL = 'iterable'
NUMBER_TYPENAME = 'number'
STRING_TYPENAME = 'string'

BOOLEAN_FALSE = 'false'
BOOLEAN_TRUE = 'true'
DEFAULT_VALUE = 'default'

class AstNode:

  def __init__ (self, line: int = 0, column: int = 0, typeref: TypeRef | None = None, **kwargs):

    super ().__init__ ()

    self.line = line
    self.column = column
    self.typeref = typeref

class Value (AstNode):

  def __init__ (self, **kwargs):

    super ().__init__ (**kwargs)

BASE_TYPE = CompositeType (BASE_TYPENAME, { })
BOOLEAN_TYPE = TypeRef (BOOLEAN_TYPENAME, False)
DEFAULT_TYPE = TypeRef (DEFAULT_TYPENAME, False)
NUMBER_TYPE = TypeRef (NUMBER_TYPENAME, False)
STRING_TYPE = TypeRef (STRING_TYPENAME, False)
