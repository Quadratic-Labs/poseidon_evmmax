from . import bytecode
from .memory import MemoryAllocator, Variable, Array
from .ops import ops_by_name
from .types import Hex


class Program:
    def __init__(self):
        self.memory = MemoryAllocator()
        self.segments = {}
        self.ops = []

    def __getitem__(self, key):
        return self.segments[key]

    def segment(self, label):
        self.segments[label] = ProgramSegment(self)
        return self.segments[label]

    def compile_runtime(self):
        return bytecode.from_ops(self.ops)


class ProgramSegment:
    def __init__(self, program):
        self.program = program
        self.memory = program.memory
        self.ops = []
        self.offset = None

    def __len__(self):
        return sum(op.nbytes() for op in self.ops)
        # return len(self.ops)

    def _push_if_not_none(self, *args):
        # Assume that last args are on stack and ordered (possibly empty)
        accept_missing = True
        for arg in reversed(args):
            if arg is not None:
                accept_missing = False
                self.push(arg)
            else:  # missing
                if not accept_missing:
                    raise ValueError(
                        f"Unordered arguments are not supported")

    def stop(self):
        self.ops.append(ops_by_name["STOP"])

    def add(self, x=None, y=None):
        self._push_if_not_none(x, y)
        self.ops.append(ops_by_name["ADD"])

    def mul(self, x=None, y=None):
        self._push_if_not_none(x, y)
        self.ops.append(ops_by_name["MUL"])

    def sub(self, x=None, y=None):
        self._push_if_not_none(x, y)
        self.ops.append(ops_by_name["SUB"])

    def div(self, x=None, y=None):
        self._push_if_not_none(x, y)
        self.ops.append(ops_by_name["DIV"])

    def sdiv(self, x=None, y=None):
        self._push_if_not_none(x, y)
        self.ops.append(ops_by_name["SDIV"])

    def mod(self, x=None, y=None):
        self._push_if_not_none(x, y)
        self.ops.append(ops_by_name["MOD"])

    def smod(self, x=None, y=None):
        self._push_if_not_none(x, y)
        self.ops.append(ops_by_name["SMOD"])

    def addmod(self, x=None, y=None, N=None):
        self._push_if_not_none(x, y, N)
        self.ops.append(ops_by_name["ADDMOD"])

    def mulmod(self, x=None, y=None, N=None):
        self._push_if_not_none(x, y, N)
        self.ops.append(ops_by_name["MULMOD"])

    def exp(self, x=None, y=None):
        self._push_if_not_none(x, y)
        self.ops.append(ops_by_name["EXP"])

    def calldatacopy(self, dest=None, offset=None, size=None):
        if isinstance(dest, Variable):
            self.push(dest.m_size)
            self.push(offset)
            self.push(dest.addr)
        else:
            self._push_if_not_none(dest, offset, size)
        self.ops.append(ops_by_name["CALLDATACOPY"])
    
    def mload(self, orig=None):
        if isinstance(orig, Variable):
            self.push(orig.addr)
        else:
            self._push_if_not_none(orig)
        self.ops.append(ops_by_name["MLOAD"])

    def mstore(self, dest=None, value=None):
        if isinstance(dest, Variable):
            if isinstance(dest, Array):
                dest.check_compatibility(value)
                for vr, vl in dest.zip(value):
                    self.push(vl)
                    self.push(vr.addr)
                    self.ops.append(ops_by_name["MSTORE"])
            else:
                self._push_if_not_none(value)
                self.push(dest.addr)
                self.ops.append(ops_by_name["MSTORE"])
        else:
            self._push_if_not_none(dest, value)
            self.ops.append(ops_by_name["MSTORE"])
            
    def return_(self, orig=None, size=None):
        if isinstance(orig, Variable):
            self.push(orig.m_size)
            self.push(orig.addr)
        else:
            self._push_if_not_none(orig, size)
        self.ops.append(ops_by_name["RETURN"])

    def push(self, x=None):
        if x is None:
            x = Hex(-1)
        if isinstance(x, int):
            x = Hex(x)
        if x.nbytes() > 32:
                raise ValueError(f"Push value too big: "
                                 f"{x} is {x.nbytes()} bytes, max is 32")
        name = f"PUSH{x.nbytes()}"
        op = ops_by_name[name].set_arg(x)
        self.ops.append(op)

    def dup(self, x=1):
        if x not in range(1, 17):
            raise ValueError(f"Dup index out of bounds: must be 1..16, "
                             f"passed {x}")
        self.ops.append(ops_by_name[f"DUP{x}"])

    def swap(self, x=1):
        if x not in range(1, 17):
            raise ValueError(f"Swap index out of bounds: must be 1..16, "
                             f"passed {x}")
        self.ops.append(ops_by_name[f"SWAP{x}"])

    def jump(self, dest=None):
        if isinstance(dest, Variable):
            self.mload(dest)
            self.ops.append(ops_by_name["JUMP"])
        elif dest is not None:
            self.push(dest)
            self.ops.append(ops_by_name["JUMP"])

    def jumpdest(self):
        self.ops.append(ops_by_name["JUMPDEST"])

    def call(self, rp, to):
        return_addr = Hex(self.offset + len(self)
                          + to.nbytes() + rp.addr.nbytes() + 5)
        temp_size = return_addr.nbytes() 
        return_addr = Hex(return_addr + temp_size)
        if Hex(return_addr).nbytes() > temp_size:
            return_addr = Hex(return_addr + 1)
        self.mstore(dest=rp, value=return_addr)
        self.jump(to)
        self.jumpdest()

    def pop(self):
        self.ops.append(ops_by_name["POP"])

    def setmodx(self, modulus):
        # self.push(modulus.addr + self.memory.size_max * 8)
        # self.push(modulus.addr)
        self.push(self.memory.size_max)
        self.push(modulus.addr)
        self.ops.append(ops_by_name["SETMODX"])

    def addmodx(self, dest, x, y):
        op = ops_by_name["ADDMODX"]
        args = "".join([
            str(self.memory.slot(dest)), 
            str(self.memory.slot(x)), 
            str(self.memory.slot(y)),
        ])
        op = op.set_arg(Hex(args))
        self.ops.append(op)

    def mulmontx(self, dest, x, y):
        op = ops_by_name["MULMONTX"]
        args = "".join([
            str(self.memory.slot(dest)), 
            str(self.memory.slot(x)), 
            str(self.memory.slot(y)),
        ])
        op = op.set_arg(Hex(args))
        self.ops.append(op)
