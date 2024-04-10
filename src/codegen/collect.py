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
from codegen.function import IRFunction
from codegen.irframe import IRFrame
from codegen.irtypes import IRTypes
from codegen.type import IRType
from enum import Enum
from functools import reduce
from parser.ast.base import AstNode
from parser.ast.block import Block
from parser.ast.decl import FunctionDecl, TypeDecl
from parser.ast.param import Param
from semantic.check import Semantic
from semantic.type import CompositeType, FunctionType, NamedType, ProtocolType, Type
from typing import Dict, List
from utils.alternate import alternate
from utils.builtin import BASE_TYPE, CTOR_NAME
import llvmlite.ir as ir
import utils.visitor as visitor

class CollectStage (Enum):

  COLLECT = 1
  LINK = 2
  COMPLETE = 3

class CollectVisitor:

  def __init__(self, stage: CollectStage) -> None:

    self.stage = stage

  @staticmethod
  def irTypeFromType (type_: Type, types: IRTypes) -> ir.Type:

    return types [BASE_TYPE.name if isinstance (type_, ProtocolType) else type_.name] # type: ignore

  @staticmethod
  def mangleFunction (name: str, type_: FunctionType):

    params: Dict[str, NamedType] = type_.params # type: ignore
    return_type: NamedType = type_.type_ # type: ignore

    name = f'{name}['
    name = reduce (lambda a, e: f'{a}{e.name},', params.values (), name)
    name = f'{name}({return_type.name})]'

    return name

  @visitor.on ('node')
  def visit (self, node: AstNode, module: ir.Module, semantic: Semantic, frame: IRFrame, types: IRTypes, prefix: List[CompositeType] = []): # type: ignore

    raise CodegenException (node, 'falling through')

  @visitor.when (Block)
  def visit (self, node: Block, module: ir.Module, semantic: Semantic, frame: IRFrame, types: IRTypes, prefix: List[CompositeType] = []): # type: ignore

    for stmt in node.stmts:

      self.visit (stmt, module, semantic, frame, types, prefix = prefix) # type: ignore

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl, module: ir.Module, semantic: Semantic, frame: IRFrame, types: IRTypes, prefix: List[CompositeType] = []): # type: ignore

    name: str = '.'.join ([ *map (lambda a: a.name, prefix), node.name ])
    type_: FunctionType = semantic.scope [name]

    match self.stage:

      case CollectStage.COLLECT:

        first: IRFunction | None = None

        for alternative in alternate (type_):

          if not first:

            first = IRFunction (ir.FunctionType (ir.VoidType (), []), None) # type: ignore
          else:

            first.add_sibling (ir.FunctionType (ir.VoidType (), []), None) # type: ignore

        assert (first)

        frame [name] = first

      case CollectStage.LINK:

        assert (first := frame [name]) # type: ignore

        for alternative, func in zip (alternate (type_), first.candidates):

          funcn = CollectVisitor.mangleFunction (name, alternative) # type: ignore

          func.type.args = [ CollectVisitor.irTypeFromType (param, types) for param in alternative.params.values () ] # type: ignore
          func.type.return_type = CollectVisitor.irTypeFromType (alternative.type_, types) # type: ignore

          if len (prefix) > 0:

            basenm = '.'.join (map (lambda a: a.name, prefix))
            basety = types [basenm]

            func.type.args.insert (0, basety)

            if node.name != CTOR_NAME:

              typety: IRType = types ['.'.join (map (lambda a: a.name, prefix))] # type: ignore

              if (methods := typety.methods.get (node.name, None)) == None:

                typety.methods [node.name] = (methods := [])

              methods.append (func.type)

          func._value = ir.Function (module, func.type, ''.join ([ funcn ]))

  @visitor.when (Param)
  def visit (self, node: Param, module: ir.Module, semantic: Semantic, frame: IRFrame, types: IRTypes, prefix: List[CompositeType] = []): # type: ignore

    match self.stage:

      case CollectStage.LINK:

        if len (prefix) > 0:

          type_: CompositeType = semantic.types ['.'.join (map (lambda a: a.name, prefix))]
          attribute: Type = type_.attributes [node.name]

          typety: IRType = types ['.'.join (map (lambda a: a.name, prefix))] # type: ignore
          typety.attributes [node.name] = CollectVisitor.irTypeFromType (attribute, types)

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl, module: ir.Module, semantic: Semantic, frame: IRFrame, types: IRTypes, prefix: List[CompositeType] = []): # type: ignore

    name: str = '.'.join ([ *map (lambda a: a.name, prefix), node.name ])
    type_: CompositeType = semantic.types [name]

    match self.stage:

      case CollectStage.COLLECT:

        types [name] = IRType (module.context, node.name)

        self.visit (node.body, module, semantic, frame, types, prefix = [ *prefix, type_ ]) # type: ignore

      case CollectStage.LINK:

        assert (type_.parent)
        assert (isinstance (parentty := types [type_.parent.name], IRType))
        assert (isinstance (refty := types [type_.name], IRType))
        refty.parent = parentty

        self.visit (node.body, module, semantic, frame, types, prefix = [ *prefix, type_ ]) # type: ignore

      case CollectStage.COMPLETE:

        assert (isinstance (refty := types [type_.name], IRType))

        refty.complete (module)
