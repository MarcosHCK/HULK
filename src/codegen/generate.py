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
from codegen.function import IRFunction, IRMethod
from codegen.irframe import IRFrame
from codegen.irtypes import IRTypes
from codegen.type import IRType
from codegen.value import IRReference, IRValue, IRValueBase, IRVariable
from parser.ast.assignment import DestructiveAssignment
from parser.ast.base import AstNode
from parser.ast.block import Block
from parser.ast.conditional import Conditional
from parser.ast.constant import Constant
from parser.ast.decl import FunctionDecl, TypeDecl
from parser.ast.indirection import ClassAccess
from parser.ast.invoke import Invoke
from parser.ast.let import Let
from parser.ast.loops import While
from parser.ast.operator import BinaryOperator, UnaryOperator
from parser.ast.value import NewValue, VariableValue
from typing import Dict, List, Set
from utils.builtin import BASE_NAME, SELF_NAME
from utils.builtin import BASE_VARIABLE, SELF_VARIABLE
from utils.builtin import BOOLEAN_TYPE, NUMBER_TYPE, STRING_TYPE
from utils.builtin import CTOR_NAME
import llvmlite.ir as ir
import utils.visitor as visitor

VisitResult = IRValueBase

class Destroyed (Exception):

  @property
  def node (self): return self._node
  @property
  def value (self): return self._value

  def __init__(self, node: AstNode, value: IRValueBase, *args: object) -> None:
    
    super ().__init__ (*args)

    self._node = node
    self._value = value

class GenerateVisitor:

  @staticmethod
  def fillctor (builder: ir.IRBuilder, self_: ir.Value, frame: IRFrame, prefix: List[IRType]):

    type_: IRType = prefix [-1]

    base: str = '.'.join ([ *map (lambda a: a.name, prefix), '' ])
    fields: Dict[str, Dict[ir.Type, IRFunction]] = {}

    for name, value in frame.items ():

      if name.startswith (base):

        field: str = name [len (base):]
        head: IRFunction = value # type: ignore

        fields [field] = (candidates := {})

        for func in head.candidates:

          candidates [func.type] = func

    for method_name in type_.methods.keys ():

      for store, functy in type_.index_bare (builder, self_, method_name):

        builder.store (fields [method_name] [functy].function, store)

  @visitor.on ('node')
  def visit (self, node: AstNode, builder: ir.IRBuilder, frame: IRFrame, types: IRType, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    raise CodegenException (node, 'falling through')

  @visitor.when (BinaryOperator)
  def visit (self, node: BinaryOperator, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    match node.operator:

      case 'as' | 'is':

        raise Exception ('unimplemented')

      case _:

        lhs = self.visit (node.argument, builder, frame, types, prefix = prefix) # type: ignore
        rhs = self.visit (node.argument2, builder, frame, types, prefix = prefix) # type: ignore

        match node.operator:

          case '+': return IRValue (builder.fadd (lhs.value (builder), rhs.value (builder))) # type: ignore
          case '-': return IRValue (builder.fsub (lhs.value (builder), rhs.value (builder))) # type: ignore
          case '*': return IRValue (builder.fmul (lhs.value (builder), rhs.value (builder))) # type: ignore
          case '/': return IRValue (builder.fdiv (lhs.value (builder), rhs.value (builder))) # type: ignore
          case '%': return IRValue (builder.frem (lhs.value (builder), rhs.value (builder))) # type: ignore

          case '&': return IRValue (builder.and_ (lhs.value (builder), rhs.value (builder))) # type: ignore
          case '|': return IRValue (builder.or_ (lhs.value (builder), rhs.value (builder))) # type: ignore

          case '==' | '!=' | '<=' | '>=' | '<' | '>':

            return IRValue (builder.fcmp_ordered (node.operator, lhs.value (builder), rhs.value (builder)))

          case _: raise Exception (f'unimplemented operator \'{node.operator}\'')

  @visitor.when (Block)
  def visit (self, node: Block, builder: ir.IRBuilder, frame: IRFrame, types: IRType, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    value = None

    for stmt in node.stmts:

      if (last := self.visit (stmt, builder, frame, types, prefix = prefix)) != None: # type: ignore
        value = last

    return value # type: ignore

  @visitor.when (Conditional)
  def visit (self, node: Conditional, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> IRValue: # type: ignore

    nowfn: ir.Function = builder.function # type: ignore

    directbb = nowfn.append_basic_block ('direct')
    reversebb = nowfn.append_basic_block ('reverse')
    joinbb = nowfn.append_basic_block ('join')

    cond = self.visit (node.condition, builder, frame, types, prefix = prefix) # type: ignore

    builder.cbranch (cond.value (builder), directbb, reversebb)

    builder.position_at_end (directbb)
    direct = self.visit (node.direct, builder, frame, types, prefix = prefix) # type: ignore

    builder.branch (joinbb)

    builder.position_at_end (reversebb)
    reverse = self.visit (node.reverse, builder, frame, types, prefix = prefix) # type: ignore

    builder.branch (joinbb)

    builder.position_at_end (joinbb)
    phi = builder.phi (direct.type)

    phi.add_incoming (direct.value (builder), directbb)
    phi.add_incoming (reverse.value (builder), reversebb)
    return IRValue (phi)

  @visitor.when (ClassAccess)
  def visit (self, node: ClassAccess, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    base: IRValue = self.visit (node.base, builder, frame, types, prefix = prefix) # type: ignore
    type: IRType = types [node.type_.name] # type: ignore

    if node.field != CTOR_NAME:

      return type.index (builder, base.value (builder), node.field)
    else:

      func = frame ['.'.join ([ *map (lambda a: a.name, prefix [:-1]), type.name, node.field ])]
      return IRMethod (base.value (builder), func._type, func._value) # type: ignore

  @visitor.when (Constant)
  def visit (self, node: Constant, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    if isinstance (node.value, bool): return IRValue (ir.Constant (types [BOOLEAN_TYPE.name], 1 if node.value else 0))
    elif isinstance (node.value, float): return IRValue (ir.Constant (types [NUMBER_TYPE.name], node.value))
    elif isinstance (node.value, str): return IRValue (ir.Constant (types [STRING_TYPE.name], node.value.encode ('utf-8')))
    else: raise CodegenException (node, f'unknown constant type \'{type (node.value)}\'')

  @visitor.when (DestructiveAssignment)
  def visit (self, node: DestructiveAssignment, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    over = self.visit (node.over, builder, frame, types, prefix = prefix) # type: ignore
    value = self.visit (node.value, builder, frame, types, prefix = prefix) # type: ignore

    assert (isinstance (over, IRReference))

    over.store (builder, value.value (builder))

    return value

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    name: str = '.'.join ([ *map (lambda a: a.name, prefix), node.name ])
    first: IRFunction = frame [name] # type: ignore

    for candidate in first.candidates:

      func: ir.Function = candidate.function # type: ignore

      descent = IRFrame ()
      implementor = ir.IRBuilder (funcbb := func.append_basic_block ())

      for name, value in frame.items ():
        descent [name] = value

      for name, value in zip ([ p.name for p in node.params ], func.args [1 if len (prefix) > 0 else 0:]): 
        descent [name] = IRVariable.create (implementor, value)

      if len (prefix) > 0:

        ir_self = func.args [0]

        descent [SELF_NAME if node.name == CTOR_NAME else SELF_VARIABLE] = IRVariable.create (implementor, ir_self)

        if (parent := prefix [-1].parent) != None:

          ir_base: ir.Value = implementor.bitcast (ir_self, parent) # type: ignore

          descent [BASE_NAME if node.name == CTOR_NAME else BASE_VARIABLE] = IRVariable.create (implementor, ir_base)

        if node.name == CTOR_NAME:

          GenerateVisitor.fillctor (implementor, ir_self, frame, prefix)

      implementor.ret (self.visit (node.body, implementor, descent, types, prefix = prefix).value (implementor)) # type: ignore

  @visitor.when (Invoke)
  def visit (self, node: Invoke, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    arguments = map (lambda a: self.visit (a, builder, frame, types, prefix = prefix), node.arguments) # type: ignore
    target = self.visit (node.target, builder, frame, types, prefix = prefix) # type: ignore

    assert (isinstance (target, IRFunction))
    return IRValue (target.call (builder, [ *map (lambda a: a.value (builder), arguments) ]))

  @visitor.when (Let)
  def visit (self, node: Let, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    descent = IRFrame ()

    for name, value in frame.items ():
      descent [name] = value

    for name, value in [ (p.name, self.visit (p.value, builder, frame, types, prefix = prefix)) for p in node.params ]: # type: ignore
      descent [name] = IRVariable.create (builder, value.value (builder))

    return self.visit (node.body, builder, descent, types, prefix = prefix) # type: ignore

  @visitor.when (NewValue)
  def visit (self, node: NewValue, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    assert (isinstance (type_ := types [node.type_.name], IRType)) # type: ignore

    self_: IRReference = type_.create (builder)
    ctor: IRFunction = frame ['.'.join ([ *map (lambda a: a.name, [ *prefix, type_ ]), CTOR_NAME ])] # type: ignore

    return IRValue (ctor.call (builder, [ self_.address (builder) ]))

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    return self.visit (node.body, builder, frame, types, prefix = [ *prefix, types [node.name] ]) # type: ignore

  @visitor.when (UnaryOperator)
  def visit (self, node: UnaryOperator, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    lhs = self.visit (node.argument, builder, frame, types, prefix = prefix) # type: ignore

    match node.operator:

      case '-': return IRValue (builder.neg (lhs.value (builder))) # type: ignore
      case '!': return IRValue (builder.not_ (lhs.value (builder))) # type: ignore
      case _: raise Exception (f'unimplemented operator \'{node.operator}\'')

  @visitor.when (VariableValue)
  def visit (self, node: VariableValue, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> VisitResult: # type: ignore

    return frame [node.name]

  @visitor.when (While)
  def visit (self, node: While, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, prefix: List[IRType] = []) -> IRValue: # type: ignore

    nowbb: ir.Block = builder.block # type: ignore
    nowfn: ir.Function = builder.function # type: ignore

    builder.position_at_end (directbb := nowfn.append_basic_block ('direct'))

    value = self.visit (node.direct, builder, frame, types, prefix = prefix) # type: ignore

    builder.position_at_end (nowbb)

    store = IRVariable (builder, value.type)

    builder.branch (backbb := nowfn.append_basic_block ('back'))
    builder.position_at_end (directbb)

    store.store (builder, value.value (builder))

    builder.branch (backbb)
    builder.position_at_end (backbb)

    cond = self.visit (node.condition, builder, frame, types, prefix = prefix) # type: ignore

    builder.cbranch (cond.value (builder), directbb, joinbb := nowfn.append_basic_block ('join'))
    builder.position_at_end (joinbb)

    return IRValue (store.value (builder))
