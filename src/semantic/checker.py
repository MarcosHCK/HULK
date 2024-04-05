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
from parser.ast.base import AstNode
from semantic.collector import CollectorVisitor
from semantic.scope import Scope
from semantic.typing import TypingVisitor
from utils.builtins import builtin_types
from utils.builtins import builtin_values

class SemanticChecker:

  def __init__(self) -> None:

    scope = Scope ()

    for builtin in builtin_types:

      scope.addt (builtin.name, builtin.typeref)

    for builtin in builtin_values:

      scope.addv (builtin.value, builtin.typeref)

    self.scope = scope

  def check (self, node: AstNode):

    scope = self.scope.clone ()

    CollectorVisitor (scope).visit (node) # type: ignore
    TypingVisitor (scope).visit (node) # type: ignore

    return scope
