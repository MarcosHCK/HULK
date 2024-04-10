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
import llvmlite.binding as llvm
import llvmlite.ir as ir

llvm.initialize ()
llvm.initialize_native_target ()
llvm.initialize_native_asmprinter ()

default_triple = llvm.get_default_triple ()

def compile (module: ir.Module, level: int = 0) -> llvm.ModuleRef:

  module.triple = default_triple

  (mod := llvm.parse_assembly (str (module))).verify ()

  if level > 0:

    passes = llvm.create_module_pass_manager ()

    if level > 0:

      passes.add_instruction_combining_pass ()
      passes.add_reassociate_expressions_pass ()
      passes.add_cfg_simplification_pass ()
      passes.add_gvn_pass ()

    if level > 1:

      passes.add_arg_promotion_pass ()
      passes.add_break_critical_edges_pass ()

    if level > 1 and level < 2:

      passes.add_dead_code_elimination_pass ()

    if level > 2:

      passes.add_aggressive_instruction_combining_pass ()
      passes.add_aggressive_dead_code_elimination_pass ()
      passes.add_dead_arg_elimination_pass ()

    passes.run (mod)

  return mod
