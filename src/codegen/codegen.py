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
from codegen.collect import CollectStage, CollectVisitor
from codegen.generate import GenerateVisitor
from codegen.irframe import IRFrame
from codegen.irtypes import IRTypes
from codegen.struct import IRStructType
from parser.ast.base import AstNode
from semantic.check import Semantic
from typing import Any
from utils.builtin import BASE_TYPE, BOOLEAN_TYPE, NUMBER_TYPE, STRING_TYPE
from utils.builtin import builtin_constants
import llvmlite.binding as llvm
import llvmlite.ir as ir

class Codegen:

  @staticmethod
  def initialize (module: ir.Module, frame: IRFrame, types: IRTypes):

    types [BASE_TYPE.name] = (basety := IRStructType (module.context, BASE_TYPE.name))
    types [BOOLEAN_TYPE.name] = ir.IntType (1)
    types [NUMBER_TYPE.name] = ir.DoubleType ()
    types [STRING_TYPE.name] = ir.PointerType (ir.IntType (8))

    for name, (type_, value) in builtin_constants.items ():

      frame [name] = Codegen.constant (module, name, frame, types [type_.name], value) # type: ignore

    basety.attributes = { '@type': ir.IntType (32) }
    basety.complete (module)

  @staticmethod
  def constant (module: ir.Module, name: str, frame: IRFrame, type: ir.Type, value: Any):

    var = ir.GlobalVariable (module, type, name)
    val = ir.Constant (type, value)

    var.global_constant = True
    var.initializer = val # type: ignore

    frame [name] = var

    return var

  def generate (self, ast: AstNode, semantic: Semantic) -> ir.Module:

    builder = ir.IRBuilder ()
    module = ir.Module ()

    mainty = ir.FunctionType (ir.IntType (32), [])
    main = ir.Function (module, mainty, 'main')

    frame = IRFrame ()
    types = IRTypes ()

    builder.position_at_end (main.append_basic_block (name = 'entry'))

    Codegen ().initialize (module, frame, types)
    CollectVisitor (CollectStage.COLLECT).visit (ast, module, semantic, frame, types) # type: ignore
    CollectVisitor (CollectStage.LINK).visit (ast, module, semantic, frame, types) # type: ignore
    print (module)
    GenerateVisitor ().visit (ast, builder, frame, types) # type: ignore

    builder.ret (ir.Constant (mainty.return_type, 0))

    print (module)
    llvm.parse_assembly (str (module)).verify ()
    import os
    os._exit (0)

    return module
