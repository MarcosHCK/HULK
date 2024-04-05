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
from ctypes import CFUNCTYPE, c_int32
import llvmlite.binding as llvm

def run (module: llvm.ModuleRef) -> int:

  with llvm.create_mcjit_compiler (module, llvm.Target.from_default_triple ().create_target_machine ()) as jit:

    jit.add_object_file ('hulklib.o')
    jit.finalize_object ()

    cfunc = jit.get_function_address ('main')
    cfunc = CFUNCTYPE (c_int32) (cfunc)

    return cfunc ()
