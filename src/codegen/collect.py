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
from codegen.exception import CodegenException
from codegen.irframe import IRFrame
from codegen.irtypes import IRTypes
from codegen.struct import IRMethod, IRMethodType, IRStructType
from enum import Enum
from parser.ast.block import Block
from parser.ast.decl import FunctionDecl, TypeDecl
from semantic.check import Semantic
from semantic.type import CompositeType, FunctionType, NamedType
from typing import Iterable, List, OrderedDict, Tuple
from utils.alternate import alternate
from utils.builtin import CTOR_NAME
import llvmlite.ir as ir
import utils.visitor as visitor

class CollectStage (Enum):

  COLLECT = 1
  LINK = 2

class CollectVisitor:

  def __init__(self, stage: CollectStage) -> None:

    self.stage = stage

  @visitor.on ('node')
  def visit (self, node, module: ir.Module, semantic: Semantic, frame: IRFrame, types: IRTypes, prefix: List[CompositeType] = []) -> ir.Type: # type: ignore

    raise CodegenException (node, 'falling through')

  @visitor.when (Block)
  def visit (self, node: Block, module: ir.Module, semantic: Semantic, frame: IRFrame, types: IRTypes, prefix: List[CompositeType] = []) -> ir.Type: # type: ignore

    for stmt in node.stmts:

      last = self.visit (stmt, module, semantic, frame, types, prefix = prefix) # type: ignore

    return last

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl, module: ir.Module, semantic: Semantic, frame: IRFrame, types: IRTypes, prefix: List[CompositeType] = []) -> ir.Type: # type: ignore

    name: str = '.'.join ([ *map (lambda a: a.name, prefix), node.name ])
    type_: FunctionType = semantic.scope [name]

    match self.stage:

      case CollectStage.COLLECT:

        for alterntive in alternate (type_):

          funcn = IRTypes.mangle (name, alterntive)

          if len (prefix) > 0:

            types [funcn] = IRMethodType (ir.VoidType (), [])
          else:

            types [funcn] = ir.FunctionType (ir.VoidType (), [])

          types.link (name, funcn)

      case CollectStage.LINK:

        for alterntive in alternate (type_):

          funcn: str = IRTypes.mangle (name, alterntive)

          refty: ir.FunctionType = types [funcn] # type: ignore
          return_type: NamedType = type_.type_ # type: ignore

          refty.args = [ *map (lambda a: types [a.name], type_.params.values ()) ] # type: ignore
          refty.return_type = types [return_type.name]

          if len (prefix) == 0:

            frame [funcn] = ir.Function (module, refty, funcn)
          else:
  
            selfty = types ['.'.join (map (lambda a: a.name, prefix))]
            selfpy = selfty.as_pointer ()

            refty.args.insert (0, selfpy)

            frame [funcn] = IRMethod (module, refty, funcn)

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl, module: ir.Module, semantic: Semantic, frame: IRFrame, types: IRTypes, prefix: List[CompositeType] = []) -> ir.Type: # type: ignore

    name: str = '.'.join ([ *map (lambda a: a.name, prefix), node.name ])
    type_: CompositeType = semantic.types [name]

    match self.stage:

      case CollectStage.COLLECT:

        types [name] = IRStructType (module.context, node.name)

      case CollectStage.LINK:

        assert (type_.parent)
        assert (isinstance (parentty := types [type_.parent.name], IRStructType))
        assert (isinstance (refty := types [name], IRStructType))

        attributes: Iterable[Tuple[str, NamedType]] = type_.attributes.items () # type: ignore
        methods: Iterable[Tuple[str, FunctionType]] = filter (lambda t: t[1].name != CTOR_NAME, type_.methods.items ()) # type: ignore
        methods_: OrderedDict[str, ir.Type] = OrderedDict ()

        for name, method in methods:

          for alterntive in alternate (method):

            funcn: str = IRTypes.mangle (name, alterntive)

            methods_ [name] = types ['.'.join ([ *map (lambda a: a.name, [ *prefix, type_ ]), funcn ])]

        refty.parent = parentty
        refty.attributes = OrderedDict (map (lambda t: (t[0], types [t[1].name]), attributes))
        refty.methods = methods_

        refty.complete (module)

    self.visit (node.body, module, semantic, frame, types, prefix = [ *prefix, type_ ]) # type: ignore
