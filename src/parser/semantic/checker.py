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
from ..ast.base import BOOL_TYPE, DEFAULT_TYPE, DEFAULT_VALUE
from ..ast.base import BOOLEAN_FALSE, BOOLEAN_TRUE
from ..ast.base import AstNode
from .scope import Scope
from .typecheck import TypeCheckVisitor

class SemanticChecker:

  def __init__(self) -> None:

    pass

  def check (self, node: AstNode):

    scope = Scope ()

    scope.addv (BOOLEAN_FALSE, BOOL_TYPE)
    scope.addv (BOOLEAN_TRUE, BOOL_TYPE)
    scope.addv (DEFAULT_VALUE, DEFAULT_TYPE)

    TypeCheckVisitor (scope).visit (node) # type: ignore
