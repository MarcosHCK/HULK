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
from parser.ast.indirection import ClassAccess
from parser.ast.value import VariableValue

class DestructiveAssignment (Value):

  def __init__ (self, over: ClassAccess | VariableValue, value: Value, **kw):

    super ().__init__ (**kw)

    self.over = over
    self.value = value
