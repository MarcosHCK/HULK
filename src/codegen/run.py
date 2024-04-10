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
from codegen.compile import default_triple
from ctypes import CFUNCTYPE
from typing import List
import llvmlite.binding as llvm

def run (module: llvm.ModuleRef, stdlib: List[str]):

  target = llvm.Target.from_triple (default_triple)
  machine = target.create_target_machine ()

  with llvm.create_mcjit_compiler (module, machine) as jit:

    for file in stdlib:

      jit.add_object_file (file)

    jit.finalize_object ()

    cfunc = jit.get_function_address ('main')
    cfunc = CFUNCTYPE (None) (cfunc)

    cfunc ()
