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
from .base import Constant, Value
from typing import List

class BooleanValue (Constant):

  def __init__ (self, value: str):

    super ().__init__ (value == 'true')

class DefaultValue (Constant):

  def __init__ (self):

    super ().__init__ (None)

class NewValue (Value):

  def __init__ (self, type_: str, arguments: List[Value]):

    super ().__init__ ()

    self.arguments = arguments
    self.type = type_

class NumberValue (Constant):

  def __init__ (self, value: str):

    super ().__init__ (float (value))

class StringValue (Constant):

  def __init__ (self, value: str):

    super ().__init__ (value [1:-1])

class VariableValue (Constant):

  def __init__ (self, value: str):

    super ().__init__ (value)
