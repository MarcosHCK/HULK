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
from collections import namedtuple
from parser.ast.base import AstNode
from semantic.collect import CollectStage, CollectVisitor
from semantic.scope import Scope
from semantic.transform import TransformStage, TransformVisitor
from semantic.types import Types
from semantic.typing import TypingVisitor
from utils.builtin import builtin_constants
from utils.builtin import builtin_types
from utils.builtin import builtin_values

Semantic = namedtuple ('Semantic', [ 'scope', 'types' ])

class SemanticCheck:

  def check (self, ast: AstNode):

    scope = Scope ()
    types = Types ()

    for name, (type_, _) in builtin_constants.items ():
      scope [name] = type_
    for name, type_ in builtin_types.items ():
      types [name] = type_
    for name, type_ in builtin_values.items ():
      scope [name] = type_

    CollectVisitor (CollectStage.COLLECT).visit (ast, scope, types) # type: ignore
    CollectVisitor (CollectStage.LINK).visit (ast, scope, types) # type: ignore

    for transfor_stage in [ TransformStage.TRIM_ATTRIBUTES, TransformStage.GUESS_ARGUMENTS ]:

      collected = TransformVisitor (TransformStage.COLLECT_FUNCTIONS).visit (ast, scope, types) # type: ignore
      collected = TransformVisitor (transfor_stage).visit (ast, scope, types, collected) # type: ignore

      while True:

        done, _ = TypingVisitor ().visit (ast, scope, types) # type: ignore
        if done  == 0: break

    return Semantic (scope = scope, types = types)
