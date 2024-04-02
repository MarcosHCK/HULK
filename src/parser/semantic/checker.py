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
from parser.ast.base import BOOLEAN_FALSE, BOOLEAN_TRUE
from parser.ast.base import BOOLEAN_TYPE, DEFAULT_TYPE, NUMBER_TYPE
from parser.ast.base import BOOLEAN_TYPENAME, DEFAULT_VALUE
from parser.ast.base import DEFAULT_TYPENAME, NUMBER_TYPENAME
from parser.ast.base import ITERABLE_PROTOCOL
from parser.semantic.scope import Scope
from parser.semantic.typecheck import TypeCheckVisitor
from parser.types import AnyType, FunctionType, ProtocolType

class SemanticChecker:

  def __init__(self) -> None:

    scope = Scope ()

    iterable = ProtocolType (ITERABLE_PROTOCOL, {

      'current': FunctionType ('current', [], AnyType ()),
      'next': FunctionType ('next', [], AnyType ()),
    })

    scope.addt (BOOLEAN_TYPENAME, BOOLEAN_TYPE)
    scope.addt (DEFAULT_TYPENAME, DEFAULT_TYPE)
    scope.addt (ITERABLE_PROTOCOL, iterable)
    scope.addt (NUMBER_TYPENAME, NUMBER_TYPE)

    scope.addv (BOOLEAN_FALSE, BOOLEAN_TYPE)
    scope.addv (BOOLEAN_TRUE, BOOLEAN_TYPE)
    scope.addv (DEFAULT_VALUE, DEFAULT_TYPE)

    self.scope = scope

  def check (self, node: AstNode):

    scope = self.scope.clone ()

    TypeCheckVisitor (scope).visit (node) # type: ignore
