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
from codegen.collect import CollectStage
from codegen.collect import CollectVisitor
from codegen.function import IRFunction
from codegen.generate import GenerateVisitor
from codegen.irframe import IRFrame
from codegen.irtypes import IRTypes
from codegen.type import IRType
from codegen.value import IRReference
from parser.ast.base import AstNode
from semantic.check import Semantic
from typing import Any
from semantic.type import FunctionType
from utils.alternate import alternate
from utils.builtin import BASE_TYPE, CTOR_NAME, STDLIB_BASECTOR
from utils.builtin import BOOLEAN_TYPE
from utils.builtin import builtin_constants
from utils.builtin import builtin_functions
from utils.builtin import NUMBER_TYPE
from utils.builtin import STRING_TYPE
import llvmlite.ir as ir

class Codegen:

  def __init__(self) -> None:

    pass

  @staticmethod
  def constant (module: ir.Module, name: str, frame: IRFrame, type: ir.Type, value: Any):

    var = ir.GlobalVariable (module, type, name)
    val = ir.Constant (type, value)

    var.global_constant = True
    var.initializer = val # type: ignore

    frame [name] = IRReference (var)

    return var

  @staticmethod
  def initialize (module: ir.Module, frame: IRFrame, types: IRTypes):

    types [BASE_TYPE.name] = (basety := IRType (module.context, BASE_TYPE.name))
    types [BOOLEAN_TYPE.name] = ir.IntType (1)
    types [NUMBER_TYPE.name] = ir.DoubleType ()
    types [STRING_TYPE.name] = ir.PointerType (ir.IntType (8))

    base_ctor_name = '.'.join ([ BASE_TYPE.name, CTOR_NAME ])
    base_ctor_signature = CollectVisitor.mangleFunction (base_ctor_name, STDLIB_BASECTOR)
    base_ctor_ty = ir.FunctionType (basety, [ basety ])
    base_ctor = ir.Function (module, base_ctor_ty, base_ctor_signature)

    frame [base_ctor_name] = IRFunction (base_ctor_ty, base_ctor)

    for name, (type_, value) in builtin_constants.items ():

      frame [name] = Codegen.constant (module, name, frame, types [type_.name], value) # type: ignore

    for name, type_ in builtin_functions.items ():

      first: IRFunction | None = None

      for alternative_ in alternate (type_):

        alternative: FunctionType = alternative_ # type: ignore

        ir_name = CollectVisitor.mangleFunction (type_.name, alternative) # type: ignore
        ir_args = [ CollectVisitor.irTypeFromType (param, types) for param in alternative.params.values () ]
        ir_return = CollectVisitor.irTypeFromType (alternative.type_, types)

        ir_type = ir.FunctionType (ir_return, ir_args)
        ir_func = ir.Function (module, ir_type, ir_name)

        if not first:

          first = IRFunction (ir_type, ir_func)
        else:

          first.add_sibling (ir_type, ir_func)

      frame [type_.name] = first # type: ignore

    basety.attributes = { '@type': ir.IntType (32) }
    basety.complete (module)

  def generate (self, ast: AstNode, semantic: Semantic, name: str = ''):

    builder = ir.IRBuilder ()
    module = ir.Module (name)

    frame = IRFrame ()
    types = IRTypes ()

    mainty = ir.FunctionType (ir.VoidType (), [])
    main = ir.Function (module, mainty, 'main')

    builder.position_at_end (mainbb := main.append_basic_block ())

    Codegen.initialize (module, frame, types)
    CollectVisitor (stage = CollectStage.COLLECT).visit (ast, module, semantic, frame, types) # type: ignore
    CollectVisitor (stage = CollectStage.LINK).visit (ast, module, semantic, frame, types) # type: ignore
    CollectVisitor (stage = CollectStage.COMPLETE).visit (ast, module, semantic, frame, types) # type: ignore

    GenerateVisitor ().visit (ast, builder, frame, types) # type: ignore

    builder.ret_void ()

    return module
