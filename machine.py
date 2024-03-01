from __future__ import annotations

import argparse
import copy
import logging
import typing
from enum import Enum

from isa import AddressType, Opcode, Term, Word, deserialize, addr_ops, value_ops, WordType
from stdlib import INPUT_PORT, OUTPUT_PORT


def read_code(src: typing.TextIO) -> list[Word]:
    text = src.read()
    return deserialize(text)


def read_input(in_file: typing.TextIO) -> list[str]:
    if in_file is None:
        return []
    tokens = []
    for char in in_file.read():
        tokens.append(char)
    return tokens


class Reg(tuple[str], Enum):
    ACR, IPR, INR = "acr", "ipr", "inr"
    ADR, DAR, SPR = "adr", "dar", "spr"


class AluOp(Enum):
    SUM = "sum"
    MUL = "mul"
    MOD = "mod"
    DIV = "div"


extend_20 = 0x01
plus_1 = 0x02
set_flags = 0x04
inv_left = 0x08
inv_right = 0x10


def extend_bits(val: int, count: int) -> int:
    bit = (val >> (count - 1)) & 0x1
    if bit == 0:
        return val & ((1 << count) - 1)
    return val | ((-1) << count)


mask_64 = (1 << 64) - 1

n_flag = 0x8
z_flag = 0x4
v_flag = 0x2
c_flag = 0x1


def alu_sum(left: int, right: int, carry: int = 0) -> (int, int):
    result = 0
    for i in range(64):
        bit_res = ((left >> i) & 0x1) + ((right >> i) & 0x1) + ((carry >> i) & 0x1)
        result |= (bit_res & 0x1) << i
        carry |= (bit_res & 0x2) << i
    flags = 0
    if (result >> 63) & 0x1 == 1:
        flags |= n_flag
    if result & mask_64 == 0:
        flags |= z_flag
    if ((carry >> 63) & 0x1) != ((carry >> 64) & 0x1):
        flags |= v_flag
    if (carry >> 64) & 0x1 == 1:
        flags |= c_flag
    return result & mask_64, flags


class DataPath:
    def __init__(self, memory_size: int, memory: list[Word], input_tokens: list[str]):
        assert memory_size >= len(memory), "data_memory_size must be greater than data_memory size"
        for word in memory:
            if word.tag == WordType.BINARY:
                assert 0 <= word.val < (1 << 32), "all binary words in memory must be uint32"
        self.memory_size = memory_size
        self.memory = copy.deepcopy(memory)
        for _ in range(memory_size - len(memory)):
            self.memory.append(Word(WordType.BINARY, val=0))
        self.input_tokens = input_tokens
        self.output_tokens = []
        # registers
        self.inr = None
        self.acr, self.ipr = 0, 0
        self.adr, self.dar, self.spr = 0, 0, memory_size
        self.flr = 0

    def signal_read_data_memory(self):
        assert self.adr < self.memory_size, f"adr ({self.adr}) out of data_memory_size ({self.memory_size})"
        if self.adr == INPUT_PORT:
            if len(self.input_tokens) == 0:
                raise EOFError()
            symbol = self.input_tokens.pop(0)
            logging.debug(f"input: {symbol!r} <- {''.join(self.input_tokens)!r}")
            self.dar = ord(symbol)
        else:
            word = self.memory[self.adr]
            assert word.tag == WordType.BINARY, f"unknown word tag to read {word.tag}"
            self.dar = word.val

    def signal_write_data_memory(self):
        if self.adr == OUTPUT_PORT:
            assert 0 <= self.dar <= 0x10FFFF, f"dar contains unknown symbol, got {self.dar}"
            symbol = chr(self.dar)
            logging.debug(f"output: {''.join(self.output_tokens)!r} <- {symbol!r}")
            self.output_tokens.append(symbol)
        else:
            word = self.memory[self.adr]
            assert word.tag == WordType.BINARY, f"Cant write in read-only memory {word.tag}"
            word.val = self.dar

    def negative(self) -> bool:
        return self.flr & n_flag != 0

    def zero(self) -> bool:
        return self.flr & z_flag != 0

    def overflow(self) -> bool:
        return self.flr & v_flag != 0

    def carry(self) -> bool:
        return self.flr & c_flag != 0

    def left_alu_val(self, left: Reg | None) -> int:
        if left is None:
            return 0
        assert left in (Reg.ACR, Reg.IPR, Reg.INR), f"incorrect left register, got {left}"
        if left == Reg.INR:
            return self.inr.instr.arg.val
        return getattr(self, left.value[0])

    def right_alu_val(self, right: Reg | None) -> int:
        if right is None:
            return 0
        assert right in (Reg.ADR, Reg.DAR, Reg.SPR), f"incorrect right register, got {right}"
        return getattr(self, right.value[0])

    def alu(self, left: int, right: int, op: AluOp, opts: int) -> int:
        left = ~left if opts & inv_left != 0 else left
        right = ~right if opts & inv_right != 0 else right

        left = extend_bits(left, 20) if opts & extend_20 != 0 else left

        if op == AluOp.SUM:
            output, flags = alu_sum(left & mask_64, right & mask_64, 1 if opts & plus_1 != 0 else 0)
            if opts & set_flags != 0:
                self.flr = flags
        elif op == AluOp.MUL:
            output = left * right
        elif op == AluOp.MOD:
            assert left >= 0, f"mod can performed only with non-negatives, got left={left}"
            assert right > 0, f"mod can performed only with positive argument, got right={right}"
            output = left % right
        elif op == AluOp.DIV:
            assert left >= 0, f"div can performed only with non-negatives, got left={left}"
            assert right > 0, f"div can performed only with positive argument, got right={right}"
            output = left // right
        else:
            raise NotImplementedError(op)

        return output & mask_64

    def set_regs(self, alu_out: int, regs: list[Reg]):
        for reg in regs:
            assert reg in (Reg.ACR, Reg.IPR, Reg.ADR, Reg.DAR, Reg.SPR), f"unsupported register {reg}"
            setattr(self, reg.value[0], alu_out)

    def signal_alu(
        self,
        left: Reg | None = None,
        right: Reg | None = None,
        alu_op: AluOp = AluOp.SUM,
        set_regs: list[Reg] | None = None,
        opts: int = 0,
    ):
        if set_regs is None:
            set_regs = []
        left_val = extend_bits(self.left_alu_val(left), 64)
        right_val = extend_bits(self.right_alu_val(right), 64)
        output = self.alu(left_val, right_val, alu_op, opts)
        self.set_regs(output, set_regs)

    def signal_fetch_instr(self) -> Term:
        self.inr = self.memory[self.ipr]
        assert self.inr.tag == WordType.INSTRUCTION, f"Cant fetch instruction, next is {self.inr.tag}"
        return self.inr.instr

    def __repr__(self):
        regs_repr = (
            f"acr={hex(self.acr)} ipr={hex(self.ipr)} "
            f"adr={hex(self.adr)} dar={hex(self.dar)} spr={hex(self.spr)} "
            f"flr={hex(self.flr)}"
        )
        stack_repr = f"stack_top={'?' if self.spr >= len(self.memory) else hex(self.memory[self.spr].val)}"
        return f"{regs_repr} {stack_repr}"


class ControlUnit:
    def __init__(self, data_path: DataPath):
        self.data_path = data_path
        self.ticks = 0

        self.control_instruction_executors: dict[Opcode, typing.Callable[[Term], None]] = {
            Opcode.HALT: self.execute_halt_control_instruction,
            Opcode.CALL: self.execute_call_control_instruction,
            Opcode.RETURN: self.execute_return_control_instruction,
            Opcode.JUMP_EQUAL: self.execute_branch_equal_control_instruction,
            Opcode.JUMP_GREATER: self.execute_branch_greater_control_instruction,
            Opcode.JUMP_GREATER_EQUAL: self.execute_branch_greater_equal_control_instruction,
            Opcode.JUMP: self.execute_branch_any_control_instruction,
        }

        self.ordinary_instruction_executors: dict[Opcode, typing.Callable[[], None]] = {
            Opcode.NOOP: self.execute_noop,
            Opcode.LOAD: self.execute_load,
            Opcode.STORE: self.execute_store,
            Opcode.PUSH: self.execute_push,
            Opcode.POP: self.execute_pop,
            Opcode.POPN: self.execute_popn,
            Opcode.COMPARE: self.execute_compare,
            Opcode.INCREMENT: self.execute_inc,
            Opcode.DECREMENT: self.execute_dec,
            Opcode.MODULO: self.execute_modulo,
            Opcode.ADD: self.execute_add,
            Opcode.SUBTRACT: self.execute_subtract,
            Opcode.MULTIPLY: self.execute_multiply,
            Opcode.DIVIDE: self.execute_divide,
            Opcode.INVERSE: self.execute_inverse,
        }

    def tick(self):
        self.ticks += 1

    def execute_halt_control_instruction(self, instr: Term):
        raise StopIteration()

    def execute_call_control_instruction(self, instr: Term):
        assert instr.arg.tag == AddressType.ABSOLUTE, f"unsupported addressing for call, got {instr}"
        self.data_path.signal_alu(right=Reg.SPR, set_regs=[Reg.ADR, Reg.SPR], opts=inv_left)
        self.tick()
        self.data_path.signal_alu(left=Reg.IPR, set_regs=[Reg.DAR], opts=plus_1)
        self.tick()
        self.data_path.signal_write_data_memory()
        self.tick()
        self.data_path.signal_alu(left=Reg.INR, set_regs=[Reg.IPR], opts=extend_20)
        self.tick()

    def execute_pop_into(self, reg: Reg):
        self.data_path.signal_alu(right=Reg.SPR, set_regs=[Reg.ADR])
        self.tick()
        self.data_path.signal_read_data_memory()
        self.tick()
        self.data_path.signal_alu(right=Reg.DAR, set_regs=[reg])
        self.tick()
        self.data_path.signal_alu(right=Reg.SPR, set_regs=[Reg.SPR], opts=plus_1)
        self.tick()

    # noinspection PyUnusedLocal
    def execute_return_control_instruction(self, instr: Term):
        self.execute_pop_into(Reg.IPR)

    def execute_branch_equal_control_instruction(self, instr: Term):
        assert instr.arg.tag == AddressType.RELATIVE_IPR, f"unsupported addressing for bre, got {instr}"
        if self.data_path.zero():
            self.data_path.signal_alu(left=Reg.IPR, set_regs=[Reg.ADR])
            self.tick()
            self.data_path.signal_alu(left=Reg.INR, right=Reg.ADR, set_regs=[Reg.IPR], opts=extend_20)
            self.tick()
        else:
            self.data_path.signal_alu(left=Reg.IPR, set_regs=[Reg.IPR], opts=plus_1)
            self.tick()

    def execute_branch_greater_control_instruction(self, instr: Term):
        assert instr.arg.tag == AddressType.RELATIVE_IPR, f"unsupported addressing for brg, got {instr}"
        if self.data_path.negative() == self.data_path.overflow() and self.data_path.zero() is False:
            self.data_path.signal_alu(left=Reg.IPR, set_regs=[Reg.ADR])
            self.tick()
            self.data_path.signal_alu(left=Reg.INR, right=Reg.ADR, set_regs=[Reg.IPR], opts=extend_20)
            self.tick()
        else:
            self.data_path.signal_alu(left=Reg.IPR, set_regs=[Reg.IPR], opts=plus_1)
            self.tick()

    def execute_branch_greater_equal_control_instruction(self, instr: Term):
        assert instr.arg.tag == AddressType.RELATIVE_IPR, f"unsupported addressing for brge, got {instr}"
        if self.data_path.negative() == self.data_path.overflow() or self.data_path.zero() is True:
            self.data_path.signal_alu(left=Reg.IPR, set_regs=[Reg.ADR])
            self.tick()
            self.data_path.signal_alu(left=Reg.INR, right=Reg.ADR, set_regs=[Reg.IPR], opts=extend_20)
            self.tick()
        else:
            self.data_path.signal_alu(left=Reg.IPR, set_regs=[Reg.IPR], opts=plus_1)
            self.tick()

    def execute_branch_any_control_instruction(self, instr: Term):
        assert instr.arg.tag in (
            AddressType.ABSOLUTE,
            AddressType.RELATIVE_IPR,
        ), f"unsupported addressing for br, got {instr}"
        if instr.arg.tag == AddressType.ABSOLUTE:
            self.data_path.signal_alu(left=Reg.INR, set_regs=[Reg.IPR], opts=extend_20)
            self.tick()
        else:
            self.data_path.signal_alu(left=Reg.IPR, set_regs=[Reg.ADR])
            self.tick()
            self.data_path.signal_alu(left=Reg.INR, right=Reg.ADR, set_regs=[Reg.IPR], opts=extend_20)
            self.tick()

    def execute_control_instruction(self, instr: Term) -> bool:
        opcode = instr.op
        if opcode not in self.control_instruction_executors:
            return False
        self.control_instruction_executors[opcode](instr)
        return True

    def address_decode(self, instr: Term):
        addr = instr.arg
        if addr.tag == AddressType.EXACT:
            pass
        elif addr.tag == AddressType.ABSOLUTE:
            self.data_path.signal_alu(left=Reg.INR, set_regs=[Reg.ADR], opts=extend_20)
            self.tick()
        elif addr.tag == AddressType.RELATIVE_SPR:
            self.data_path.signal_alu(left=Reg.INR, right=Reg.SPR, set_regs=[Reg.ADR], opts=extend_20)
            self.tick()
        elif addr.tag == AddressType.RELATIVE_INDIRECT_SPR:
            self.data_path.signal_alu(left=Reg.INR, right=Reg.SPR, set_regs=[Reg.ADR], opts=extend_20)
            self.tick()
            self.data_path.signal_read_data_memory()
            self.tick()
            self.data_path.signal_alu(right=Reg.DAR, set_regs=[Reg.ADR])
            self.tick()
        else:
            raise NotImplementedError(f"unsupported address type for address decoding, got {instr}")

    def value_fetch(self, instr: Term):
        addr = instr.arg
        if addr.tag == AddressType.EXACT:
            self.data_path.signal_alu(left=Reg.INR, set_regs=[Reg.DAR], opts=extend_20)
            self.tick()
        elif addr.tag in (AddressType.ABSOLUTE, AddressType.RELATIVE_SPR, AddressType.RELATIVE_INDIRECT_SPR):
            self.data_path.signal_read_data_memory()
            self.tick()
        else:
            raise NotImplementedError(f"unsupported address type for value fetching, got {instr}")

    def execute_noop(self):
        self.tick()

    def execute_load(self):
        self.data_path.signal_alu(right=Reg.DAR, set_regs=[Reg.ACR])
        self.tick()

    def execute_store(self):
        self.data_path.signal_alu(left=Reg.ACR, set_regs=[Reg.DAR])
        self.tick()
        self.data_path.signal_write_data_memory()
        self.tick()

    def execute_push(self):
        self.data_path.signal_alu(right=Reg.SPR, set_regs=[Reg.ADR, Reg.SPR], opts=inv_left)
        self.tick()
        self.data_path.signal_alu(left=Reg.ACR, set_regs=[Reg.DAR])
        self.tick()
        self.data_path.signal_write_data_memory()
        self.tick()

    def execute_pop(self):
        self.execute_pop_into(Reg.ACR)

    def execute_popn(self):
        self.data_path.signal_alu(right=Reg.SPR, set_regs=[Reg.SPR], opts=plus_1)
        self.tick()

    def execute_compare(self):
        self.data_path.signal_alu(left=Reg.ACR, right=Reg.DAR, opts=inv_right | plus_1 | set_flags)
        self.tick()

    def execute_inc(self):
        self.data_path.signal_read_data_memory()
        self.tick()
        self.data_path.signal_alu(right=Reg.DAR, set_regs=[Reg.DAR], opts=plus_1)
        self.tick()
        self.data_path.signal_write_data_memory()
        self.tick()

    def execute_dec(self):
        self.data_path.signal_read_data_memory()
        self.tick()
        self.data_path.signal_alu(right=Reg.DAR, set_regs=[Reg.DAR], opts=inv_left)
        self.tick()
        self.data_path.signal_write_data_memory()
        self.tick()

    def execute_modulo(self):
        self.data_path.signal_alu(left=Reg.ACR, right=Reg.DAR, alu_op=AluOp.MOD, set_regs=[Reg.ACR])
        self.tick()

    def execute_add(self):
        self.data_path.signal_alu(left=Reg.ACR, right=Reg.DAR, set_regs=[Reg.ACR])
        self.tick()

    def execute_subtract(self):
        self.data_path.signal_alu(left=Reg.ACR, right=Reg.DAR, set_regs=[Reg.ACR], opts=inv_right | plus_1)
        self.tick()

    def execute_multiply(self):
        self.data_path.signal_alu(left=Reg.ACR, right=Reg.DAR, alu_op=AluOp.MUL, set_regs=[Reg.ACR])
        self.tick()

    def execute_divide(self):
        self.data_path.signal_alu(left=Reg.ACR, right=Reg.DAR, alu_op=AluOp.DIV, set_regs=[Reg.ACR])
        self.tick()

    def execute_inverse(self):
        self.data_path.signal_alu(left=Reg.ACR, set_regs=[Reg.ACR], opts=inv_left | plus_1)
        self.tick()

    def execute(self, instr: Term):
        opcode = instr.op
        if opcode not in self.ordinary_instruction_executors:
            raise NotImplementedError(f"Unknown instruction, got {instr}")
        self.ordinary_instruction_executors[opcode]()

    def finalize(self):
        self.data_path.signal_alu(left=Reg.IPR, set_regs=[Reg.IPR], opts=plus_1)

    def execute_ordinary_instruction(self, instr: Term):
        if instr.op in addr_ops or instr.op in value_ops:
            self.address_decode(instr)
        if instr.op in value_ops:
            self.value_fetch(instr)
        self.execute(instr)
        self.finalize()

    def execute_next_instruction(self):
        instruction = self.data_path.signal_fetch_instr()
        logging.debug(self)
        logging.debug(instruction.op.name)
        if not self.execute_control_instruction(instruction):
            self.execute_ordinary_instruction(instruction)

    def __repr__(self):
        state_repr = f"tick={self.ticks}"
        dp_repr = f"{self.data_path}"
        return f"{state_repr}\t{dp_repr}".expandtabs(10)


def simulation(code: list[Word], input_tokens: list[str], memory_size: int = 0x1FFF, limit: int = 5_000):
    data_path = DataPath(memory_size, code, input_tokens)
    control_unit = ControlUnit(data_path)
    instruction_proceed = 0

    try:
        while instruction_proceed < limit:
            control_unit.execute_next_instruction()
            instruction_proceed += 1
    except EOFError:
        logging.warning("Input buffer is empty")
    except StopIteration:
        pass

    if instruction_proceed >= limit:
        logging.warning(f"Limit {limit} exceeded")

    return "".join(data_path.output_tokens), instruction_proceed, control_unit.ticks


def main(src: typing.TextIO, in_file: typing.TextIO):
    logging.getLogger().setLevel(logging.DEBUG)

    code = read_code(src)
    input_tokens = read_input(in_file)
    output, instr, ticks = simulation(code, input_tokens)

    logging.info(f"instr: {instr} ticks: {ticks}")
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute lisp executable file.")
    parser.add_argument("src", type=argparse.FileType("r"), metavar="executable_file", help="executable file")
    parser.add_argument(
        "--input",
        "-i",
        dest="in_file",
        type=argparse.FileType(encoding="utf-8"),
        metavar="input_file",
        help="file with input data for executable (default: empty file)",
    )
    namespace = parser.parse_args()
    main(namespace.src, namespace.in_file)
