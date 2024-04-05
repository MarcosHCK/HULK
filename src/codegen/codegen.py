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
from typing import Dict
from codegen.frame import Frame
from codegen.types import Types
from codegen.filler import FillerVisitor
from parser.ast.base import AstNode
from parser.types import AnyType, ProtocolType
from semantic.scope import Scope
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
    mainbb = main.append_basic_block (name = 'entry')

    builder.position_at_end (mainbb)

    any = AnyType ()
    frame = Frame ()
    types = self.types.clone ()

    for name, type_ in scope.types.items ():

      if name not in any.name and not isinstance (type_, ProtocolType):

        types.fit (type_)

    for name, type_ in scope.variables.items ():

      if isinstance (types.fit (type_), ir.FunctionType):

        alt: Dict[str, ir.FunctionType] = types[type_.name] # type: ignore

        for name, functy in alt.items ():

          frame[name] = ir.Function (module, functy, name)

    FillerVisitor ().visit (builder, ast, frame, types) # type: ignore
    builder.ret (ir.Constant (mainty.return_type, 0))
    print (module)

    llvm.parse_assembly (str (module)).verify ()
    return module
