from collections.abc import Iterator, Iterable

from .ops import ops_by_code, ops_by_name
from .ops import Op


def iter_bytes(hexstring: str) -> Iterator[str]:
    for i in range(0, len(hexstring), 2):
        yield hexstring[i:(i+2)]


def to_ops(bytecode: str) -> Iterator[Op]:
    ibytecode = iter_bytes(bytecode)
    for code in ibytecode:
        try:
            op = ops_by_code[code]
        except KeyError:
            raise ValueError(f"Could not find opcode {code}")
        args = []
        for _ in range(op.arg_nbytes):
            args.append(next(ibytecode))
        op = op.set_arg("".join(args))
        yield op
        

def from_ops(ops: Iterable[Op]) -> str:
    result = []
    for op in ops:
        result.append(op.to_hex())
    return "".join(result)


# DEPRECATED
def op(name, *args):
    name = name.upper()
    s_args = "".join(str(a) for a in args)
    if "0x" in s_args:
        breakpoint()
    if name == "PUSH":
        # if s_args == "00":
        #     name = f"PUSH0"
        #     s_args = ""
        # else:
        size = len(s_args) // 2
        name = f"PUSH{size}"
    code = opcodes_by_name[name]
    return Op(code, s_args)
