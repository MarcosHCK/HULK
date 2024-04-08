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
from enum import Enum
from codegen.struct import IRMethod, IRMethodInvoke, IRStructType
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
from parser.ast.value import VariableValue
from semantic.type import CompositeType
from typing import List
from utils.builtin import BASE_NAME, BASE_VARIABLE, BOOLEAN_TYPE, CTOR_NAME, NUMBER_TYPE, SELF_NAME, SELF_VARIABLE, STRING_TYPE
import llvmlite.ir as ir
import utils.visitor as visitor

class VarMode (Enum):

  VALUE = 0
  ADDRESS = 1
  INVOKE = 2

PrefixChain = List[CompositeType]
class GenerateVisitor:

  @visitor.on ('node')
  def visit (self, node, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    raise CodegenException (node, 'falling through')

  @visitor.when (BinaryOperator)
  def visit (self, node: BinaryOperator, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    match node.operator:

      case 'as' | 'is':

        raise Exception ('unimplemented')

      case _:

        lhs = self.visit (node.argument, builder, frame, types, varm = varm, prefix = prefix) # type: ignore
        rhs = self.visit (node.argument2, builder, frame, types, varm = varm, prefix = prefix) # type: ignore

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
  def visit (self, node: Block, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    for stmt in node.stmts:

      if (last := self.visit (stmt, builder, frame, types, varm = varm, prefix = prefix)) != None: # type: ignore

        value = last

    return value

  @visitor.when (ClassAccess)
  def visit (self, node: ClassAccess, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    base = self.visit (node.base, builder, frame, types, varm = VarMode.ADDRESS, prefix = prefix) # type: ignore
    ref = types [node.type_.name] # type: ignore

    assert (isinstance (ref, IRStructType))

    match varm:

      case VarMode.VALUE: return builder.load (ref.gep (builder, base, node.field))
      case VarMode.ADDRESS: return ref.gep (builder, base, node.field)

      case VarMode.INVOKE:

        if node.field != CTOR_NAME:

          return ref.gep (builder, base, node.field)
        else:

          name = '.'.join ([ *map (lambda a: a.name, prefix), CTOR_NAME ])

          if (ctorn := types.function (name, [ base.type ])) == None: # type: ignore

            raise CodegenException (node, 'no function candidate found')

          return IRMethodInvoke (base, frame [ctorn])

      case _: raise Exception ('unsupported access')

  @visitor.when (Conditional)
  def visit (self, node: Conditional, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    nowbb: ir.Block = builder.block # type: ignore
    nowfn: ir.Function = builder.function # type: ignore

    directbb = nowfn.append_basic_block ('direct')
    reversebb = nowfn.append_basic_block ('reverse')
    joinbb = nowfn.append_basic_block ('join')

    builder.position_at_end (directbb)
    direct = self.visit (node.direct, builder, frame, types, varm = varm, prefix = prefix) # type: ignore
    cdirectbb = builder.block

    builder.position_at_end (reversebb)
    reverse = self.visit (node.reverse, builder, frame, types, varm = varm, prefix = prefix) # type: ignore
    creversebb = builder.block

    builder.position_at_end (nowbb)

    store = builder.alloca (direct.type, 1) # type: ignore
    cond = self.visit (node.condition, builder, frame, types, varm = varm, prefix = prefix) # type: ignore

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
  def visit (self, node: Constant, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    if isinstance (node.value, bool): return ir.Constant (types [BOOLEAN_TYPE.name], 1 if node.value else 0)
    elif isinstance (node.value, float): return ir.Constant (types [NUMBER_TYPE.name], node.value)
    elif isinstance (node.value, str): return ir.Constant (types [STRING_TYPE.name], node.value.encode ('utf-8'))
    else: raise Exception (f'unknown constant type \'{type (node.value)}\'')

  @visitor.when (DestructiveAssignment)
  def visit (self, node: DestructiveAssignment, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    over = self.visit (node.over, builder, frame, types, varm = VarMode.ADDRESS, prefix = prefix) # type: ignore
    value = self.visit (node.value, builder, frame, types, varm = varm, prefix = prefix) # type: ignore
    builder.store (value, over)
    return value

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    name = '.'.join ([ *map (lambda a: a.name, prefix), node.name ])

    for _func, _type_ in [ (frame [link], types [link]) for link in types.links [name] ]:

      func: ir.Function = _func # type: ignore
      type_: ir.FunctionType = _type_ # type: ignore

      descent = frame.clone ()
      implementor = ir.IRBuilder (func.append_basic_block ())
      params = [ param.name for param in node.params ]

      if len (prefix) > 0:

        descent [BASE_NAME if node.name == CTOR_NAME else BASE_VARIABLE] = func.args [0]
        params = [ SELF_NAME if node.name == CTOR_NAME else SELF_VARIABLE, *params ]

      for argn, argt, argv in zip (params, type_.args, func.args):

        implementor.store (argv, (store := implementor.alloca (argt, 1)))
        descent [argn] = store

      implementor.ret (self.visit (node.body, implementor, descent, types, varm = varm, prefix = prefix)) # type: ignore

  @visitor.when (Invoke)
  def visit (self, node: Invoke, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    arguments = list (map (lambda a: self.visit (a, builder, frame, types, varm = varm, prefix = prefix), node.arguments)) # type: ignore
    descent = frame.clone ()

    for i, argument in enumerate (arguments):

      descent [f'@a{i}'] = argument

    target = self.visit (node.target, builder, descent, types, varm = VarMode.INVOKE, prefix = prefix) # type: ignore

    if isinstance (target, IRMethodInvoke):

      return target.call (builder, arguments)
    else:
      return builder.call (target, arguments)

  @visitor.when (Let)
  def visit (self, node: Let, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    descent = frame.clone ()

    for param in node.params:

      name = param.name
      value = self.visit (param.value, builder, frame, types, varm = varm, prefix = prefix) # type: ignore

      descent [name] = (store := builder.alloca (value.type, 1)) # type: ignore

      builder.store (value, store)

    return self.visit (node.body, builder, descent, types, varm = varm, prefix = prefix) # type: ignore

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    self.visit (node.body, builder, frame, types, varm = varm, prefix = [ *prefix, types [node.name] ]) # type: ignore

  @visitor.when (UnaryOperator)
  def visit (self, node: UnaryOperator, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    lhs = self.visit (builder, node.argument, frame, types) # type: ignore

    match node.operator:

      case '-': return builder.neg (lhs) # type: ignore
      case '!': return builder.not_ (lhs) # type: ignore

      case _: raise Exception ('unimplemented')

  @visitor.when (VariableValue)
  def visit (self, node: VariableValue, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    match varm:

      case VarMode.VALUE: return builder.load (frame [node.name])
      case VarMode.ADDRESS: return frame [node.name]

      case VarMode.INVOKE:

        params: List[ir.Type] = [ *map (lambda v: v.type, frame.locals.values ()) ] # type: ignore

        if (name := types.function (node.name, params)) != None:
          
          return frame [name]
        else:

          raise CodegenException (node, 'no function candidate found')

  @visitor.when (While)
  def visit (self, node: While, builder: ir.IRBuilder, frame: IRFrame, types: IRTypes, varm: VarMode = VarMode.VALUE, prefix: PrefixChain = []) -> ir.Value: # type: ignore

    nowfn: ir.Function = builder.function # type: ignore

    backbb = nowfn.append_basic_block ('back')
    directbb = nowfn.append_basic_block ('direct')
    joinbb = nowfn.append_basic_block ('join')

    builder.branch (backbb)
    builder.position_at_end (directbb)

    direct = self.visit (node.direct, builder, frame, types, varm = varm, prefix = prefix) # type: ignore
    cdirectbb = builder.block

    builder.position_at_end (backbb)

    cond = self.visit (node.condition, builder, frame, types, varm = varm, prefix = prefix) # type: ignore
    store = builder.alloca (direct.type, 1) # type: ignore

    builder.cbranch (cond, directbb, joinbb)

    builder.position_at_end (cdirectbb)
    builder.store (direct, store)
    builder.branch (backbb)

    builder.position_at_end (joinbb)

    return builder.load (store)
