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
from parser.ast.base import Value
from parser.ast.constant import Constant
from parser.types import TypeRef
from typing import List

class BooleanValue (Constant):

  def __init__ (self, value: str, **kwargs):

    super ().__init__ (value == 'true', **kwargs)

class DefaultValue (Constant):

  def __init__ (self, **kwargs):

    super ().__init__ (None, **kwargs)

class NewValue (Value):

  def __init__ (self, typeref: TypeRef, arguments: List[Value], **kwargs):

    super ().__init__ (typeref = typeref, **kwargs)

    self.arguments = arguments

class NumberValue (Constant):

  def __init__ (self, value: str, **kwargs):

    super ().__init__ (float (value), **kwargs)

class StringValue (Constant):

  def __init__ (self, value: str, **kwargs):

    super ().__init__ (value [1:-1], **kwargs)

class VariableValue (Value):

  def __init__ (self, name: str, **kwargs):

    super ().__init__ (**kwargs)

    self.name = name
