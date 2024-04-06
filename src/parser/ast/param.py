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
from parser.ast.type import Type

class Param (Value):

  def __init__ (self, name: str, type_: None | Type, **kw):

    super ().__init__ (**kw)

    self.name = name
    self.type_ = type_

class VarParam (Param):

  def __init__ (self, name: str, type_: None | Type, value: Value, **kw):

    super ().__init__ (name = name, type_ = type_, **kw)

    self.value = value
