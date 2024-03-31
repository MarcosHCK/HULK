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
from parser.ast.block import Block
from parser.ast.conditional import Conditional, ConditionalEntry
from parser.ast.decl import FunctionDecl
from parser.ast.invoke import Invoke
from parser.ast.let import Let, LetParam
from parser.ast.operator import BinaryOperator, UnaryOperator
from parser.ast.param import Param
from parser.ast.value import ValueNode
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

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl, tabs = 0):

    args = node.arguments
    args = list (map (lambda a: self.visit (a), args))

    body = self.visit (node.body, 1 + tabs)
    name = node.name

    return f'function {name} ({", ".join (args)})' + '{\n' + body + '\n}'

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

  @visitor.when (LetParam)
  def visit (self, node: LetParam, tabs = 0):

    param = self.visit (node.param)
    value = self.visit (node.value)

    return f'{param} = {value}'

  @visitor.when (Param)
  def visit (self, node: Param, tabs = 0):

    if (not node.annotation):

      return node.name
    elif (not node.isvector):

      return f'{node.name}: {node.annontation}'
    else:

      return f'{node.name}: {node.annontation}[]'

  @visitor.when (UnaryOperator)
  def visit (self, node: UnaryOperator, tabs = 0):

    return f'({node.operator} {self.visit (node.argument)})'

  @visitor.when (ValueNode)
  def visit (self, node: ValueNode, tabs = 0):

    return str (node.value)
