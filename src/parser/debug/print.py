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
from parser.ast.base import Constant
from parser.ast.block import Block
from parser.ast.conditional import Conditional, ConditionalEntry
from parser.ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from parser.ast.invoke import Invoke
from parser.ast.let import Let
from parser.ast.loops import While
from parser.ast.operator import BinaryOperator, UnaryOperator
from parser.ast.param import Param, VarParam
import utils.visitor as visitor

class PrintVisitor (object):

  @visitor.on ('node')
  def visit (self, node, tabs):

    pass

  @visitor.when (BinaryOperator)
  def visit (self, node: BinaryOperator, tabs = 0):

    return f'({self.visit (node.argument)} {node.operator} {self.visit (node.argument2)})'

  @visitor.when (Block)
  def visit (self, node: Block, tabs = 0):

    stmts = node.stmts
    stmts = list (map (lambda a: ('  ' * tabs) + self.visit (a, 1 + tabs) + ';', stmts))

    return '\n'.join (stmts)

  @visitor.when (Conditional)
  def visit (self, node: Conditional, tabs = 0):

    entries = [ ]
    first = True

    for entry in node.entries:

      if (not first):

        entries.append (self.visit (entry, 0, False))
      else:

        first = False
        entries.append (self.visit (entry, 0, True))

    return '(' + '\n'.join (entries) + ')'

  @visitor.when (ConditionalEntry)
  def visit (self, node: ConditionalEntry, tabs = 0, first = False): 

    if (not node.condition):

      body = self.visit (node.body, 1 + tabs)

      return 'else {\n' + body + '\n}'

    else:

      body = self.visit (node.body, 1 + tabs)
      condition = self.visit (node.condition)

      return f'{"if" if first else "elif"} ({condition})' + '{\n' + body + '\n}'

  @visitor.when (Constant)
  def visit (self, node: Constant, tabs = 0):

    return str (node.value)

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl, tabs = 0):

    annotation = node.annotation
    arguments = node.arguments
    arguments = list (map (lambda a: self.visit (a), arguments))
    body = node.body
    name = node.name

    body = self.visit (body, 1 + tabs)

    head = f'function {name} ({", ".join (arguments)})'
    tail1 = '' if (not annotation) else f': {annotation}'
    tail2 = '' if (not body) else ' {\n' + body + '\n}'

    return f'{head}{tail1}{tail2}'

  @visitor.when (Invoke)
  def visit (self, node: Invoke, tabs = 0):

    args = node.arguments
    args = ', '.join (list (map (lambda a: self.visit (a), args)))

    return f'({node.funcname} ({args}))'

  @visitor.when (Let)
  def visit (self, node: Let, tabs = 0):

    body = self.visit (node.body, 1 + tabs)

    params = list (map (lambda a: self.visit (a), node.params))
    params = ', '.join (params)

    return f'let {params} in ' + '{\n' + body + '\n}'

  @visitor.when (Param)
  def visit (self, node: Param, tabs = 0):

    if (not node.annotation):

      return node.name
    elif (not node.isvector):

      return f'{node.name}: {node.annotation}'
    else:

      return f'{node.name}: {node.annontation}[]'

  @visitor.when (ProtocolDecl)
  def visit (self, node: ProtocolDecl, tabs = 0):

    body = self.visit (node.body, 1 + tabs)
    name = node.name
    parent = node.parent

    head = f'protocol {name}'
    tail1 = '' if (not parent) else f' extends {parent}'
    tail2 = '' if (not body) else ' {\n' + body + '\n}'

    return f'{head}{tail1}{tail2}'

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl, tabs = 0):

    body = self.visit (node.body, 1 + tabs)
    name = node.name
    parent = node.parent

    head = f'type {name}'
    tail1 = '' if (not parent) else f' inherits {parent}'
    tail2 = '' if (not body) else ' {\n' + body + '\n}'

    return f'{head}{tail1}{tail2}'

  @visitor.when (UnaryOperator)
  def visit (self, node: UnaryOperator, tabs = 0):

    return f'({node.operator} {self.visit (node.argument)})'

  @visitor.when (VarParam)
  def visit (self, node: VarParam, tabs = 0):

    param = self.visit (node.param)
    value = self.visit (node.value)

    return f'{param} = {value}'

  @visitor.when (While)
  def visit (self, node: While, tabs = 0):

    body = self.visit (node.body, 1 + tabs)
    condition = self.visit (node.condition)

    return f'while ({condition})' + '{\n' + body + '\n}'
