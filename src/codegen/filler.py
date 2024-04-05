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
from codegen.frame import Frame
from codegen.frame import Mode as FrameMode
from codegen.types import Types
from parser.ast.assignment import DestructiveAssignment
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
from typing import Dict, List
from parser.types import CTOR_NAME, CompositeType
from utils.builtins import BOOLEAN_TYPE, NUMBER_TYPE, STRING_TYPE
import llvmlite.ir as ir
import utils.visitor as visitor

class FillerVisitor:

  def __init__(self, compose: None | ir.IdentifiedStructType = None) -> None:

    self.compose = compose
    pass

  @visitor.on ('node')
  def visit (self, builder, node, frame, types):

    pass

  @visitor.when (BinaryOperator)
  def visit (self, builder: ir.IRBuilder, node: BinaryOperator, frame: Frame, types: Types) -> ir.Value:

    match node.operator:

      case 'as' | 'is':

        raise Exception ('unimplemented')

      case _:

        lhs = self.visit (builder, node.argument, frame, types) # type: ignore
        rhs = self.visit (builder, node.argument2, frame, types) # type: ignore

        match node.operator:

          case '+': return builder.fadd (lhs, rhs) # type: ignore
          case '-': return builder.fsub (lhs, rhs) # type: ignore
          case '*': return builder.fmul (lhs, rhs) # type: ignore
          case '/': return builder.fdiv (lhs, rhs) # type: ignore
          case '%': return builder.frem (lhs, rhs) # type: ignore

          case '&': return builder.and_ (lhs, rhs) # type: ignore
          case '|': return builder.or_ (lhs, rhs) # type: ignore

          case '==' | '!=' | '<=' | '>=' | '<' | '>':

            return builder.fcmp_ordered (node.operator, lhs, rhs)

          case _: raise Exception ('unimplemented')

  @visitor.when (Block)
  def visit (self, builder: ir.IRBuilder, node: Block, frame: Frame, types: Types) -> ir.Value:

    value: ir.Value

    for stmt in node.stmts:

      if (last := self.visit (builder, stmt, frame, types)) != None: # type: ignore

        value = last

    return value

  @visitor.when (ClassAccess)
  def visit (self, builder: ir.IRBuilder, node: ClassAccess, frame: Frame, types: Types) -> ir.Value:

    assert (node.typeref)

    base = self.visit (builder, node.base, frame.clone (mode = FrameMode.INDIRECT), types) # type: ignore
    ref = types.struct (node.typeref.name)

    match frame.mode:

      case FrameMode.NORMAL: return ref.gep (builder, base, ref.attribute (node.field))

      case FrameMode.INVOKE:

        if node.field != CTOR_NAME:

          return ref.gep (builder, base, ref.function (node.field))
        else:

          name = f'{node.typeref.name}.{node.field}'
          ctor = types.function (name, [ types[node.typeref.name] ])

          print (f'{node.typeref.name}.{node.field}', ctor)
          raise Exception ('unimplemented')

      case _: raise Exception ('unsupported access')

  @visitor.when (Conditional)
  def visit (self, builder: ir.IRBuilder, node: Conditional, frame: Frame, types: Types) -> ir.Value:

    nowbb: ir.Block = builder.block # type: ignore
    nowfn: ir.Function = builder.function # type: ignore

    directbb = nowfn.append_basic_block ('direct')
    reversebb = nowfn.append_basic_block ('reverse')
    joinbb = nowfn.append_basic_block ('join')

    builder.position_at_end (directbb)
    direct = self.visit (builder, node.direct, frame, types) # type: ignore
    cdirectbb = builder.block

    builder.position_at_end (reversebb)
    reverse = self.visit (builder, node.reverse, frame, types) # type: ignore
    creversebb = builder.block

    builder.position_at_end (nowbb)

    store = builder.alloca (direct.type, 1) # type: ignore
    cond = self.visit (builder, node.condition, frame, types) # type: ignore

    builder.cbranch (cond, directbb, reversebb)

    builder.position_at_end (cdirectbb)
    builder.store (direct, store)
    builder.branch (joinbb)

    builder.position_at_end (creversebb)
    builder.store (reverse, store)
    builder.branch (joinbb)

    builder.position_at_end (joinbb)

    return builder.load (store)

  @visitor.when (Constant)
  def visit (self, builder: ir.IRBuilder, node: Constant, frame: Frame, types: Types) -> ir.Value:

    if isinstance (node.value, bool): return ir.Constant (types [BOOLEAN_TYPE.name], 1 if node.value else 0)
    elif isinstance (node.value, float): return ir.Constant (types [NUMBER_TYPE.name], node.value)
    elif isinstance (node.value, str): return ir.Constant (types [STRING_TYPE.name], node.value.encode ('utf-8'))
    else: raise Exception (f'unknown constant type \'{type (node.value)}\'')

  @visitor.when (DestructiveAssignment)
  def visit (self, builder: ir.IRBuilder, node: DestructiveAssignment, frame: Frame, types: Types) -> ir.Value:

    over = self.visit (builder, node.over, frame.clone (mode = FrameMode.INDIRECT), types) # type: ignore
    value = self.visit (builder, node.value, frame, types) # type: ignore

    builder.store (value, over)

    return value

  @visitor.when (FunctionDecl)
  def visit (self, builder: ir.IRBuilder, node: FunctionDecl, frame: Frame, types: Types) -> None:

    alts: Dict[str, ir.FunctionType]

    if not self.compose:

      alts = types [node.name] # type: ignore
    else:

      alts = types [f'{self.compose.name}.{node.name}'] # type: ignore

    for signature, alt in alts.items ():

      d_frame = frame.clone ()
      d_types = types.clone ()

      func: ir.Function = frame[signature] # type: ignore

      arguments = func.args if not self.compose else func.args [1:]
      implementor = ir.IRBuilder (func.append_basic_block ())

      for name, type_, value in zip (map (lambda e: e.name, node.params), alt.args, arguments):

        implementor.store (value, (store := implementor.alloca (type_, 1)))
        d_frame [name] = store

      if self.compose != None:

        d_frame ['self'] = func.args [0]
        d_frame ['base'] = func.args [0]

        d_types.add ('self', self.compose)
        d_types.add ('base', self.compose)

      implementor.ret (self.visit (implementor, node.body, d_frame, types)) # type: ignore

  @visitor.when (Invoke)
  def visit (self, builder: ir.IRBuilder, node: Invoke, frame: Frame, types: Types) -> ir.Value:

    arguments = list (map (lambda a: self.visit (builder, a, frame, types), node.arguments)) # type: ignore
    frame = frame.clone (mode = FrameMode.INVOKE)

    for i, argument in enumerate (arguments):

      frame [f'@a{i}'] = argument

    target = self.visit (builder, node.target, frame, types) # type: ignore

    return builder.call (target, list (arguments))

  @visitor.when (Let)
  def visit (self, builder: ir.IRBuilder, node: Let, frame: Frame, types: Types) -> ir.Value:

    frame = frame.clone ()

    for param in node.params:

      name = param.name
      value = self.visit (builder, param.value, frame, types) # type: ignore

      frame [name] = (store := builder.alloca (value.type, 1)) # type: ignore

      builder.store (value, store)

    return self.visit (builder, node.body, frame, types) # type: ignore

  @visitor.when (NewValue)
  def visit (self, builder: ir.IRBuilder, node: NewValue, frame: Frame, types: Types) -> ir.Value:

    arguments = map (lambda a: self.visit (builder, a, frame, types), node.arguments) # type: ignore
    arguments = [ builder.alloca (types [node.typeref.name], 1), *arguments ]
    params = map (lambda v: v.type, frame.locals.values ()) # type: ignore
    params = [ ir.PointerType (types [node.typeref.name]), *params ]

    if (name := types.function (f'{node.typeref.name}.{CTOR_NAME}', params)) != None:

      return builder.call (frame [name], arguments, f'new {node.typeref.name}')
    else:

      raise CodegenException (node, 'no function candidate found')

  @visitor.when (TypeDecl)
  def visit (self, builder: ir.IRBuilder, node: TypeDecl, frame: Frame, types: Types) -> None:

    FillerVisitor (compose = types [node.name]).visit (builder, node.body, frame, types) # type: ignore

  @visitor.when (UnaryOperator)
  def visit (self, builder: ir.IRBuilder, node: UnaryOperator, frame: Frame, types: Types) -> ir.Value:

    lhs = self.visit (builder, node.argument, frame, types) # type: ignore

    match node.operator:

      case '!': return builder.not_ (lhs) # type: ignore

      case _: raise Exception ('unimplemented')

  @visitor.when (VariableValue)
  def visit (self, builder: ir.IRBuilder, node: VariableValue, frame: Frame, types: Types) -> ir.Value:

    match frame.mode:

      case FrameMode.NORMAL: return builder.load (frame [node.name])
      case FrameMode.INDIRECT: return frame [node.name]

      case FrameMode.INVOKE:

        params: List[ir.Type] = list (map (lambda v: v.type, frame.locals.values ())) # type: ignore

        if (name := types.function (node.name, params)) != None:
          
          return frame[name]
        else:

          raise CodegenException (node, 'no function candidate found')

  @visitor.when (While)
  def visit (self, builder: ir.IRBuilder, node: While, frame: Frame, types: Types) -> ir.Value:

    nowfn: ir.Function = builder.function # type: ignore

    backbb = nowfn.append_basic_block ('back')
    directbb = nowfn.append_basic_block ('direct')
    joinbb = nowfn.append_basic_block ('join')

    builder.branch (backbb)
    builder.position_at_end (directbb)

    direct = self.visit (builder, node.direct, frame, types) # type: ignore
    cdirectbb = builder.block

    builder.position_at_end (backbb)

    cond = self.visit (builder, node.condition, frame, types) # type: ignore
    store = builder.alloca (direct.type, 1) # type: ignore

    builder.cbranch (cond, directbb, joinbb)

    builder.position_at_end (cdirectbb)
    builder.store (direct, store)
    builder.branch (backbb)

    builder.position_at_end (joinbb)

    return builder.load (store)
