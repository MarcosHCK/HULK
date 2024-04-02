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
from .ast.assignment import DestructiveAssignment
from .ast.base import TypeRef
from .ast.block import Block
from .ast.conditional import Conditional
from .ast.constant import Constant
from .ast.decl import FunctionDecl, ProtocolDecl, TypeDecl
from .ast.indirection import ClassAccess
from .ast.invoke import Invoke
from .ast.let import Let
from .ast.loops import While
from .ast.operator import BinaryOperator, UnaryOperator
from .ast.param import Param, VarParam
from .ast.value import NewValue
import utils.visitor as visitor

class PrintVisitor (object):

  @visitor.on ('node')
  def visit (self, node):

    pass

  @visitor.when (BinaryOperator)
  def visit (self, node: BinaryOperator):

    oper = [ ]

    oper.extend (self.visit (node.argument))
    oper.append (f' {node.operator} ')

    oper.extend (self.visit (node.argument2))

    return [ ''.join (oper) ]

  @visitor.when (Block)
  def visit (self, node: Block):

    lines = [ ]

    for stmt in node.stmts:

      lines.extend (self.visit (stmt))

    return lines

  @visitor.when (ClassAccess)
  def visit (self, node: ClassAccess):

    access = [ ]

    access.extend (self.visit (node.base))
    access.append (f'.{node.field}')

    return [ ''.join (access) ]

  @visitor.when (Constant)
  def visit (self, node: Constant):

    return [ str (node.value) ]

  @visitor.when (Conditional)
  def visit (self, node: Conditional):

    if_ = [ 'if (' ]

    if_.extend (self.visit (node.condition))
    if_.append (') {')

    if_ = [ ''.join (if_) ]

    if_.extend (list (map (lambda a: f'  {a}', self.visit (node.direct))))
    if_.append ('} else {')

    if_.extend (list (map (lambda a: f'  {a}', self.visit (node.reverse))))
    if_.append ('}')

    return if_

  @visitor.when (DestructiveAssignment)
  def visit (self, node: DestructiveAssignment):

    assigment = [ ]

    assigment.extend (self.visit (node.over))
    assigment.append (' := ')

    assigment.extend (self.visit (node.value))

    return [ ''.join (assigment) ]

  @visitor.when (FunctionDecl)
  def visit (self, node: FunctionDecl):

    function = [ f'function {node.name} (' ]

    for i, param in enumerate (node.params):

      if i > 0:

        function.append (', ')

      function.extend (self.visit (param))

    function.append (')')

    if (node.typeref):

      function.append (': ')
      function.extend (self.visit (node.typeref))

    function.append (' {')

    function = [ ''.join (function) ]

    function.extend (list (map (lambda a: f'  {a}', self.visit (node.body))))
    function.append ('}')

    return function

  @visitor.when (Invoke)
  def visit (self, node: Invoke):

    invoke = [ ]

    invoke.extend (self.visit (node.target))
    invoke.append (' (')

    for i, argument in enumerate (node.arguments):

      if i > 0:

        invoke.append (', ')

      invoke.extend (self.visit (argument))

    invoke.append (')')

    return [ ''.join (invoke) ]

  @visitor.when (Let)
  def visit (self, node: Let):

    let = [ 'let ' ]

    for i, param in enumerate (node.params):

      if i > 0:

        let.append (', ')

      let.extend (self.visit (param))

    let.append (' in {')

    let = [ ''.join (let) ]

    let.extend (list (map (lambda a: f'  {a}', self.visit (node.body))))
    let.append ('}')

    return let

  @visitor.when (NewValue)
  def visit (self, node: NewValue):

    value = [ f'new {node.type} (' ]

    for i, argument in enumerate (node.arguments):

      if i > 0:

        value.append (', ')

      value.extend (self.visit (argument))

    value.append (')')

    return [ ''.join (value) ]

  @visitor.when (Param)
  def visit (self, node: Param):

    param = [ f'{node.name}' ]

    if node.typeref:

      param.append (': ')
      param.extend (self.visit (node.typeref))

    return [ ''.join (param) ]

  @visitor.when (ProtocolDecl)
  def visit (self, node: ProtocolDecl):

    protocol = [ f'protocol {node.name}' ]

    if (node.parent):

      protocol.append (f' extends {node.parent}')

    protocol.append (' {')

    protocol = [ ''.join (protocol) ]

    protocol.extend (list (map (lambda a: f'  {a}', self.visit (node.body))))
    protocol.append ('}')

    return protocol

  @visitor.when (TypeDecl)
  def visit (self, node: TypeDecl):

    type_ = [ f'type {node.name}' ]

    type_.append (' (')

    for i, param in enumerate (node.params):

      if i > 0:

        type_.append (', ')

      type_.extend (self.visit (param))

    type_.append (')')

    if node.parent:

      type_.append (f' inherits {node.parent} (')

      for i, value in enumerate (node.parentctor):

        if i > 0:
  
          type_.append (', ')
  
        type_.extend (self.visit (value))

      type_.append (')')

    type_.append (' {')

    type_ = [ ''.join (type_) ]

    type_.extend (list (map (lambda a: f'  {a}', self.visit (node.body))))
    type_.append ('}')

    return type_

  @visitor.when (TypeRef)
  def visit (self, node: TypeRef):

    ref = [ f'{node.name}' ]

    if (node.vector):

      ref.append (' []')

    return [ ''.join (ref) ]

  @visitor.when (UnaryOperator)
  def visit (self, node: UnaryOperator):

    oper = [ ]

    oper.append (f'{node.operator} ')
    oper.extend (self.visit (node.argument))

    return [ ''.join (oper) ]

  @visitor.when (VarParam)
  def visit (self, node: VarParam):

    varparam = [ ]

    param = Param (node.name, node.typeref)

    varparam.extend (self.visit (param))
    varparam.append (' = ')

    varparam.extend (self.visit (node.value))

    return [ ''.join (varparam) ]

  @visitor.when (While)
  def visit (self, node: While):

    while_ = [ 'while (' ]

    while_.extend (self.visit (node.condition))
    while_.append (') {')

    while_ = [ ''.join (while_) ]

    while_.extend (list (map (lambda a: f'  {a}', self.visit (node.direct))))
    while_.append ('}')

    return while_