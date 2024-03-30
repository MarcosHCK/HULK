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
from parser.ast.invoke import Invoke
from parser.ast.operator import BinaryOperator, UnaryOperator
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

    stmts = node.expressions
    stmts = list (map (lambda a: self.visit (a), stmts))

    return '\n'.join (stmts)

  @visitor.when (Invoke)
  def visit (self, node: Invoke, tabs = 0):

    args = node.arguments
    args = ', '.join (list (map (lambda a: self.visit (a), args)))

    return f'({node.funcname} ({args}))'

  @visitor.when (UnaryOperator)
  def visit (self, node: UnaryOperator, tabs = 0):

    return f'({node.operator} {self.visit (node.argument)})'

  @visitor.when (ValueNode)
  def visit (self, node: ValueNode, tabs = 0):

    return str (node.value)
