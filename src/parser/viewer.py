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
from parser.ast.assignment import DestructiveAssignment
from parser.ast.block import Block
from parser.ast.conditional import Conditional
from parser.ast.constant import Constant
from parser.ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from parser.ast.indirection import ClassAccess
from parser.ast.invoke import Invoke
from parser.ast.let import Let
from parser.ast.loops import While
from parser.ast.operator import BinaryOperator, UnaryOperator
from parser.ast.param import Param, VarParam
from parser.ast.value import NewValue, VariableValue
from semantic.type import AnyType, NamedType, Type
from semantic.typing import TypingVisitor
import utils.visitor as visitor

class PrintVisitor (object):

  @visitor.on ('node')
  def visit (self, node: object): # type: ignore

    pass

  @visitor.when (BinaryOperator)
  def visit (self, node: BinaryOperator): # type: ignore

    oper = [ ]

    oper.extend (self.visit (node.argument)) # type: ignore
    oper.append (f' {node.operator} ')

    oper.extend (self.visit (node.argument2)) # type: ignore

    return [ ''.join (oper) ]

  @visitor.when (Block)
  def visit (self, node: Block): # type: ignore

    lines = [ ]

    for stmt in node.stmts:

      lines.extend (self.visit (stmt)) # type: ignore

    return lines

  @visitor.when (ClassAccess)
  def visit (self, node: ClassAccess): # type: ignore

    access = [ ]

    access.extend (self.visit (node.base)) # type: ignore
    access.append (f'.{node.field}')

    return [ ''.join (access) ]

  @visitor.when (Constant)
  def visit (self, node: Constant): # type: ignore

    return [ str (node.value) ]

  @visitor.when (Conditional)
  def visit (self, node: Conditional): # type: ignore

    if_ = [ 'if (' ]

    if_.extend (self.visit (node.condition)) # type: ignore
    if_.append (') {')

    if_ = [ ''.join (if_) ]

    if_.extend (list (map (lambda a: f'  {a}', self.visit (node.direct)))) # type: ignore
    if_.append ('} else {')

    if_.extend (list (map (lambda a: f'  {a}', self.visit (node.reverse)))) # type: ignore
    if_.append ('}')

    return if_

  @visitor.when (DestructiveAssignment)
  def visit (self, node: DestructiveAssignment): # type: ignore

    assigment = [ ]

    assigment.extend (self.visit (node.over)) # type: ignore
    assigment.append (' := ')

    assigment.extend (self.visit (node.value)) # type: ignore

    return [ ''.join (assigment) ]

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl): # type: ignore

    function = [ f'function {node.name} (' ]

    for i, param in enumerate (node.params):

      if i > 0:

        function.append (', ')

      function.extend (self.visit (param)) # type: ignore

    function.append (')')

    if (node.type_):

      function.append (': ')
      function.extend (self.visit (node.type_)) # type: ignore

    function.append (' {')

    function = [ ''.join (function) ]

    function.extend (list (map (lambda a: f'  {a}', self.visit (node.body)))) # type: ignore
    function.append ('}')

    return function

  @visitor.when (Invoke)
  def visit (self, node: Invoke): # type: ignore

    invoke = [ ]

    invoke.extend (self.visit (node.target)) # type: ignore
    invoke.append (' (')

    for i, argument in enumerate (node.arguments):

      if i > 0:

        invoke.append (', ')

      invoke.extend (self.visit (argument)) # type: ignore

    invoke.append (')')

    return [ ''.join (invoke) ]

  @visitor.when (Let)
  def visit (self, node: Let): # type: ignore

    let = [ 'let ' ]

    for i, param in enumerate (node.params):

      if i > 0:

        let.append (', ')

      let.extend (self.visit (param)) # type: ignore

    let.append (' in {')

    let = [ ''.join (let) ]

    let.extend (list (map (lambda a: f'  {a}', self.visit (node.body)))) # type: ignore
    let.append ('}')

    return let

  @visitor.when (NewValue)
  def visit (self, node: NewValue): # type: ignore

    value = [ f'new ' ]

    value.extend (self.visit (node.type_)) # type: ignore
    value.append (' (')

    for i, argument in enumerate (node.arguments):

      if i > 0:

        value.append (', ')

      value.extend (self.visit (argument)) # type: ignore

    value.append (')')

    return [ ''.join (value) ]

  @visitor.when (Param)
  def visit (self, node: Param): # type: ignore

    param = [ f'{node.name}' ]

    if node.type_:

      param.append (': ')
      param.extend (self.visit (node.type_)) # type: ignore

    return [ ''.join (param) ]

  @visitor.when (ProtocolDecl)
  def visit (self, node: ProtocolDecl): # type: ignore

    protocol = [ f'protocol {node.name}' ]

    if (node.parent):

      protocol.append (f' extends {node.parent}')

    protocol.append (' {')

    protocol = [ ''.join (protocol) ]

    protocol.extend (list (map (lambda a: f'  {a}', self.visit (node.body)))) # type: ignore
    protocol.append ('}')

    return protocol

  @visitor.when (Type)
  def visit (self, type_: Type): # type: ignore

    return [ TypingVisitor.describe (type_) ]

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl): # type: ignore

    type_ = [ f'type {node.name}' ]

    if node.parent:

      type_.append (f' inherits {node.parent}')

    type_.append (' {')

    type_ = [ ''.join (type_) ]

    type_.extend (list (map (lambda a: f'  {a}', self.visit (node.body)))) # type: ignore
    type_.append ('}')

    return type_

  @visitor.when (UnaryOperator)
  def visit (self, node: UnaryOperator): # type: ignore

    oper = [ ]

    oper.append (f'{node.operator} ')
    oper.extend (self.visit (node.argument)) # type: ignore

    return [ ''.join (oper) ]

  @visitor.when (VariableValue)
  def visit (self, node: VariableValue): # type: ignore

    return [ node.name ]

  @visitor.when (VarParam)
  def visit (self, node: VarParam): # type: ignore

    varparam = [ ]

    param = Param (node.name, node.type_)

    varparam.extend (self.visit (param)) # type: ignore
    varparam.append (' = ')

    varparam.extend (self.visit (node.value)) # type: ignore

    return [ ''.join (varparam) ]

  @visitor.when (While)
  def visit (self, node: While):

    while_ = [ 'while (' ]

    while_.extend (self.visit (node.condition)) # type: ignore
    while_.append (') {')

    while_ = [ ''.join (while_) ]

    while_.extend (list (map (lambda a: f'  {a}', self.visit (node.direct)))) # type: ignore
    while_.append ('}')

    return while_
