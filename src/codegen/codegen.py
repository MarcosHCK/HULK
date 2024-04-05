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
from codegen.collector import CollectorVisitor
from codegen.filler import FillerVisitor
from codegen.frame import Frame
from codegen.types import Types
from parser.ast.base import AstNode
from parser.types import FunctionType, ProtocolType
from semantic.scope import Scope
from typing import Dict
from utils.builtins import BOOLEAN_TYPE
from utils.builtins import NUMBER_TYPE
from utils.builtins import STRING_TYPE
import llvmlite.binding as llvm
import llvmlite.ir as ir

class Codegen ():

  def __init__ (self) -> None:

    super ().__init__ ()

    self.types = Types ()

    self.types.add (BOOLEAN_TYPE.name, ir.IntType (1))
    self.types.add (NUMBER_TYPE.name, ir.DoubleType ())
    self.types.add (STRING_TYPE.name, ir.PointerType (ir.IntType (8)))

  def generate (self, ast: AstNode, scope: Scope) -> ir.Module:

    builder = ir.IRBuilder ()
    module = ir.Module ()

    module.triple = llvm.get_default_triple ()

    mainty = ir.FunctionType (ir.IntType (32), [])
    main = ir.Function (module, mainty, 'main')

    frame = Frame ()
    types = self.types.clone ()

    CollectorVisitor ().visit (module.context, ast, frame, scope, types) # type: ignore

    for name, type_ in scope.types.items ():

      if not isinstance (type_, ProtocolType):

        types.fit (module.context, type_)

    for name, type_ in scope.variables.items ():

      types.fit (module.context, type_)

      if isinstance (type_, FunctionType):

        alt: Dict[str, ir.FunctionType] = types[type_.name] # type: ignore

        for name, functy in alt.items ():

          frame [name] = ir.Function (module, functy, name)

    builder.position_at_end (main.append_basic_block (name = 'entry'))

    FillerVisitor ().visit (builder, ast, frame, types) # type: ignore
    builder.ret (ir.Constant (mainty.return_type, 0))

    llvm.parse_assembly (str (module)).verify ()
    return module
