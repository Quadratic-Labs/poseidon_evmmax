from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .types import Hex


@dataclass
class Op:
    name: str
    code: Hex
    arg_nbytes: int
    arg: Hex
    stack_in: int
    stack_out: int
    gas: int

    def to_hex(self):
        nb = self.arg.nbytes()
        if self.arg_nbytes < nb:
            raise ValueError(f"Op {self.name} argument too big")
        return self.code + self.arg.to_hex(zfill=self.arg_nbytes)

    def nbytes(self):
        return len(self.to_hex()) // 2

    def set_arg(self, arg):
        return Op(self.name, self.code, self.arg_nbytes, arg, self.stack_in, self.stack_out, self.gas)


def counts(ops: Iterable[Op]) -> Mapping[str, int]:
    res = {}
    for op in ops:
        name = ''.join(i for i in op.name if not i.isdigit())
        res[name] = res.get(name, 0) + 1
    return res


ops = [
    Op('STOP', '00', 0, Hex(-1), 0, 0, 0),
    Op('ADD', '01', 0, Hex(-1), 0, 0, 0),
    Op('MUL', '02', 0, Hex(-1), 0, 0, 0),
    Op('SUB', '03', 0, Hex(-1), 0, 0, 0),
    Op('DIV', '04', 0, Hex(-1), 0, 0, 0),
    Op('SDIV', '05', 0, Hex(-1), 0, 0, 0),
    Op('MOD', '06', 0, Hex(-1), 0, 0, 0),
    Op('SMOD', '07', 0, Hex(-1), 0, 0, 0),
    Op('ADDMOD', '08', 0, Hex(-1), 0, 0, 0),
    Op('MULMOD', '09', 0, Hex(-1), 0, 0, 0),
    Op('EXP', '0a', 0, Hex(-1), 0, 0, 0),
    Op('SIGNEXTEND', '0b', 0, Hex(-1), 0, 0, 0),
    Op('LT', '10', 0, Hex(-1), 0, 0, 0),
    Op('GT', '11', 0, Hex(-1), 0, 0, 0),
    Op('SLT', '12', 0, Hex(-1), 0, 0, 0),
    Op('SGT', '13', 0, Hex(-1), 0, 0, 0),
    Op('EQ', '14', 0, Hex(-1), 0, 0, 0),
    Op('ISZERO', '15', 0, Hex(-1), 0, 0, 0),
    Op('AND', '16', 0, Hex(-1), 0, 0, 0),
    Op('OR', '17', 0, Hex(-1), 0, 0, 0),
    Op('XOR', '18', 0, Hex(-1), 0, 0, 0),
    Op('NOT', '19', 0, Hex(-1), 0, 0, 0),
    Op('BYTE', '1a', 0, Hex(-1), 0, 0, 0),
    Op('SHL', '1b', 0, Hex(-1), 0, 0, 0),
    Op('SHR', '1c', 0, Hex(-1), 0, 0, 0),
    Op('SAR', '1d', 0, Hex(-1), 0, 0, 0),
    Op('SHA3', '20', 0, Hex(-1), 0, 0, 0),

    # MODMAX codes
    Op('SETMODX', '21', 0, Hex(-1), 0, 0, 0),
    Op('ADDMODX', '22', 3, Hex(-1), 0, 0, 0),
    Op('SUBMODX', '23', 3, Hex(-1), 0, 0, 0),
    Op('MULMONTX', '24', 3, Hex(-1), 0, 0, 0),
    Op('TOMONTX', '25', 0, Hex(-1), 0, 0, 0),
    # End MODMAX

    Op('ADDRESS', '30', 0, Hex(-1), 0, 0, 0),
    Op('BALANCE', '31', 0, Hex(-1), 0, 0, 0),
    Op('ORIGIN', '32', 0, Hex(-1), 0, 0, 0),
    Op('CALLER', '33', 0, Hex(-1), 0, 0, 0),
    Op('CALLVALUE', '34', 0, Hex(-1), 0, 0, 0),
    Op('CALLDATALOAD', '35', 0, Hex(-1), 0, 0, 0),
    Op('CALLDATASIZE', '36', 0, Hex(-1), 0, 0, 0),
    Op('CALLDATACOPY', '37', 0, Hex(-1), 0, 0, 0),
    Op('CODESIZE', '38', 0, Hex(-1), 0, 0, 0),
    Op('CODECOPY', '39', 0, Hex(-1), 0, 0, 0),
    Op('GASPRICE', '3a', 0, Hex(-1), 0, 0, 0),
    Op('EXTCODESIZE', '3b', 0, Hex(-1), 0, 0, 0),
    Op('EXTCODECOPY', '3c', 0, Hex(-1), 0, 0, 0),
    Op('RETURNDATASIZE', '3d', 0, Hex(-1), 0, 0, 0),
    Op('RETURNDATACOPY', '3e', 0, Hex(-1), 0, 0, 0),
    Op('BLOCKHASH', '40', 0, Hex(-1), 0, 0, 0),
    Op('COINBASE', '41', 0, Hex(-1), 0, 0, 0),
    Op('TIMESTAMP', '42', 0, Hex(-1), 0, 0, 0),
    Op('NUMBER', '43', 0, Hex(-1), 0, 0, 0),
    Op('DIFFICULTY', '44', 0, Hex(-1), 0, 0, 0),
    Op('GASLIMIT', '45', 0, Hex(-1), 0, 0, 0),
    Op('POP', '50', 0, Hex(-1), 0, 0, 0),
    Op('MLOAD', '51', 0, Hex(-1), 0, 0, 0),
    Op('MSTORE', '52', 0, Hex(-1), 0, 0, 0),
    Op('MSTORE8', '53', 0, Hex(-1), 0, 0, 0),
    Op('SLOAD', '54', 0, Hex(-1), 0, 0, 0),
    Op('SSTORE', '55', 0, Hex(-1), 0, 0, 0),
    Op('JUMP', '56', 0, Hex(-1), 0, 0, 0),
    Op('JUMPI', '57', 0, Hex(-1), 0, 0, 0),
    Op('PC', '58', 0, Hex(-1), 0, 0, 0),
    Op('MSIZE', '59', 0, Hex(-1), 0, 0, 0),
    Op('GAS', '5a', 0, Hex(-1), 0, 0, 0),
    Op('JUMPDEST', '5b', 0, Hex(-1), 0, 0, 0),
    Op('PUSH0', '5f', 0, Hex(-1), 0, 0, 0),
    Op('PUSH1', '60', 1, Hex(-1), 0, 0, 0),
    Op('PUSH2', '61', 2, Hex(-1), 0, 0, 0),
    Op('PUSH3', '62', 3, Hex(-1), 0, 0, 0),
    Op('PUSH4', '63', 4, Hex(-1), 0, 0, 0),
    Op('PUSH5', '64', 5, Hex(-1), 0, 0, 0),
    Op('PUSH6', '65', 6, Hex(-1), 0, 0, 0),
    Op('PUSH7', '66', 7, Hex(-1), 0, 0, 0),
    Op('PUSH8', '67', 8, Hex(-1), 0, 0, 0),
    Op('PUSH9', '68', 9, Hex(-1), 0, 0, 0),
    Op('PUSH10', '69', 10, Hex(-1), 0, 0, 0),
    Op('PUSH11', '6a', 11, Hex(-1), 0, 0, 0),
    Op('PUSH12', '6b', 12, Hex(-1), 0, 0, 0),
    Op('PUSH13', '6c', 13, Hex(-1), 0, 0, 0),
    Op('PUSH14', '6d', 14, Hex(-1), 0, 0, 0),
    Op('PUSH15', '6e', 15, Hex(-1), 0, 0, 0),
    Op('PUSH16', '6f', 16, Hex(-1), 0, 0, 0),
    Op('PUSH17', '70', 17, Hex(-1), 0, 0, 0),
    Op('PUSH18', '71', 18, Hex(-1), 0, 0, 0),
    Op('PUSH19', '72', 19, Hex(-1), 0, 0, 0),
    Op('PUSH20', '73', 20, Hex(-1), 0, 0, 0),
    Op('PUSH21', '74', 21, Hex(-1), 0, 0, 0),
    Op('PUSH22', '75', 22, Hex(-1), 0, 0, 0),
    Op('PUSH23', '76', 23, Hex(-1), 0, 0, 0),
    Op('PUSH24', '77', 24, Hex(-1), 0, 0, 0),
    Op('PUSH25', '78', 25, Hex(-1), 0, 0, 0),
    Op('PUSH26', '79', 26, Hex(-1), 0, 0, 0),
    Op('PUSH27', '7a', 27, Hex(-1), 0, 0, 0),
    Op('PUSH28', '7b', 28, Hex(-1), 0, 0, 0),
    Op('PUSH29', '7c', 29, Hex(-1), 0, 0, 0),
    Op('PUSH30', '7d', 30, Hex(-1), 0, 0, 0),
    Op('PUSH31', '7e', 31, Hex(-1), 0, 0, 0),
    Op('PUSH32', '7f', 32, Hex(-1), 0, 0, 0),
    Op('DUP1', '80', 0, Hex(-1), 0, 0, 0),
    Op('DUP2', '81', 0, Hex(-1), 0, 0, 0),
    Op('DUP3', '82', 0, Hex(-1), 0, 0, 0),
    Op('DUP4', '83', 0, Hex(-1), 0, 0, 0),
    Op('DUP5', '84', 0, Hex(-1), 0, 0, 0),
    Op('DUP6', '85', 0, Hex(-1), 0, 0, 0),
    Op('DUP7', '86', 0, Hex(-1), 0, 0, 0),
    Op('DUP8', '87', 0, Hex(-1), 0, 0, 0),
    Op('DUP9', '88', 0, Hex(-1), 0, 0, 0),
    Op('DUP10', '89', 0, Hex(-1), 0, 0, 0),
    Op('DUP11', '8a', 0, Hex(-1), 0, 0, 0),
    Op('DUP12', '8b', 0, Hex(-1), 0, 0, 0),
    Op('DUP13', '8c', 0, Hex(-1), 0, 0, 0),
    Op('DUP14', '8d', 0, Hex(-1), 0, 0, 0),
    Op('DUP15', '8e', 0, Hex(-1), 0, 0, 0),
    Op('DUP16', '8f', 0, Hex(-1), 0, 0, 0),
    Op('SWAP1', '90', 0, Hex(-1), 0, 0, 0),
    Op('SWAP2', '91', 0, Hex(-1), 0, 0, 0),
    Op('SWAP3', '92', 0, Hex(-1), 0, 0, 0),
    Op('SWAP4', '93', 0, Hex(-1), 0, 0, 0),
    Op('SWAP5', '94', 0, Hex(-1), 0, 0, 0),
    Op('SWAP6', '95', 0, Hex(-1), 0, 0, 0),
    Op('SWAP7', '96', 0, Hex(-1), 0, 0, 0),
    Op('SWAP8', '97', 0, Hex(-1), 0, 0, 0),
    Op('SWAP9', '98', 0, Hex(-1), 0, 0, 0),
    Op('SWAP10', '99', 0, Hex(-1), 0, 0, 0),
    Op('SWAP11', '9a', 0, Hex(-1), 0, 0, 0),
    Op('SWAP12', '9b', 0, Hex(-1), 0, 0, 0),
    Op('SWAP13', '9c', 0, Hex(-1), 0, 0, 0),
    Op('SWAP14', '9d', 0, Hex(-1), 0, 0, 0),
    Op('SWAP15', '9e', 0, Hex(-1), 0, 0, 0),
    Op('SWAP16', '9f', 0, Hex(-1), 0, 0, 0),
    Op('LOG0', 'a0', 0, Hex(-1), 0, 0, 0),
    Op('LOG1', 'a1', 0, Hex(-1), 0, 0, 0),
    Op('LOG2', 'a2', 0, Hex(-1), 0, 0, 0),
    Op('LOG3', 'a3', 0, Hex(-1), 0, 0, 0),
    Op('LOG4', 'a4', 0, Hex(-1), 0, 0, 0),
    Op('CREATE', 'f0', 0, Hex(-1), 0, 0, 0),
    Op('CALL', 'f1', 0, Hex(-1), 0, 0, 0),
    Op('CALLCODE', 'f2', 0, Hex(-1), 0, 0, 0),
    Op('RETURN', 'f3', 0, Hex(-1), 0, 0, 0),
    Op('DELEGATECALL', 'f4', 0, Hex(-1), 0, 0, 0),
    Op('STATICCALL', 'fa', 0, Hex(-1), 0, 0, 0),
    Op('REVERT', 'fd', 0, Hex(-1), 0, 0, 0),
    Op('INVALID', 'fe', 0, Hex(-1), 0, 0, 0),
    Op('SELFDESTRUCT', 'ff', 0, Hex(-1), 0, 0, 0)
]
ops_by_code = {op.code: op for op in ops}
ops_by_name = {op.name: op for op in ops}
