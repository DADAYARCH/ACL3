from __future__ import annotations

import argparse
import copy
import logging
import typing
from enum import Enum

from isa import AddressType, Opcode, Term, Word, WordType, addr_ops, deserialize, value_ops
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
    AC, IP, IR = "ac", "ip", "ir"
    AR, DR, SP = "ar", "dr", "sp"


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


mask_32 = (1 << 32) - 1

n_flag = 0x8
z_flag = 0x4
v_flag = 0x2
c_flag = 0x1


def alu_sum(left: int, right: int, carry: int = 0) -> (int, int):
    result = 0
    for i in range(32):
        bit_res = ((left >> i) & 0x1) + ((right >> i) & 0x1) + ((carry >> i) & 0x1)
        result |= (bit_res & 0x1) << i
        carry |= (bit_res & 0x2) << i
    flags = 0
    if (result >> 31) & 0x1 == 1:
        flags |= n_flag
    if result & mask_32 == 0:
        flags |= z_flag
    if ((carry >> 31) & 0x1) != ((carry >> 32) & 0x1):
        flags |= v_flag
    if (carry >> 32) & 0x1 == 1:
        flags |= c_flag
    return result & mask_32, flags


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
        self.ir = None
        self.ac, self.ip = 0, 0
        self.ar, self.dr, self.sp = 0, 0, memory_size
        self.fl = 0

    def signal_read_memory(self):
        assert self.ar < self.memory_size, f"ar ({self.ar}) out of data_memory_size ({self.memory_size})"
        if self.ar == INPUT_PORT:
            if len(self.input_tokens) == 0:
                raise EOFError()
            symbol = self.input_tokens.pop(0)
            logging.debug(f"input: {symbol!r} <- {''.join(self.input_tokens)!r}")
            self.dr = ord(symbol)
        else:
            word = self.memory[self.ar]
            assert word.tag == WordType.BINARY, f"unknown word tag to read {word.tag}"
            self.dr = word.val

    def signal_write_memory(self):
        if self.ar == OUTPUT_PORT:
            assert 0 <= self.dr <= 0x10FFFF, f"dr contains unknown symbol, got {self.dr}"
            symbol = chr(self.dr)
            logging.debug(f"output: {''.join(self.output_tokens)!r} <- {symbol!r}")
            self.output_tokens.append(symbol)
        else:
            word = self.memory[self.ar]
            assert word.tag == WordType.BINARY, f"Cant write in read-only memory {word.tag}"
            word.val = self.dr

    def negative(self) -> bool:
        return self.fl & n_flag != 0

    def zero(self) -> bool:
        return self.fl & z_flag != 0

    def overflow(self) -> bool:
        return self.fl & v_flag != 0

    def carry(self) -> bool:
        return self.fl & c_flag != 0

    def left_alu_val(self, left: Reg | None) -> int:
        if left is None:
            return 0
        assert left in (Reg.AC, Reg.IP, Reg.IR), f"incorrect left register, got {left}"
        if left == Reg.IR:
            return self.ir.instr.arg.val
        return getattr(self, left.value[0])

    def right_alu_val(self, right: Reg | None) -> int:
        if right is None:
            return 0
        assert right in (Reg.AR, Reg.DR, Reg.SP), f"incorrect right register, got {right}"
        return getattr(self, right.value[0])

    def alu(self, left: int, right: int, op: AluOp, opts: int) -> int:
        left = ~left if opts & inv_left != 0 else left
        right = ~right if opts & inv_right != 0 else right

        left = extend_bits(left, 20) if opts & extend_20 != 0 else left

        if op == AluOp.SUM:
            output, flags = alu_sum(left & mask_32, right & mask_32, 1 if opts & plus_1 != 0 else 0)
            if opts & set_flags != 0:
                self.fl = flags
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

        return output & mask_32

    def set_regs(self, alu_out: int, regs: list[Reg]):
        for reg in regs:
            assert reg in (Reg.AC, Reg.IP, Reg.AR, Reg.DR, Reg.SP), f"unsupported register {reg}"
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
        left_val = extend_bits(self.left_alu_val(left), 32)
        right_val = extend_bits(self.right_alu_val(right), 32)
        output = self.alu(left_val, right_val, alu_op, opts)
        self.set_regs(output, set_regs)

    def signal_fetch_instr(self) -> Term:
        self.ir = self.memory[self.ip]
        assert self.ir.tag == WordType.INSTRUCTION, f"Cant fetch instruction, next is {self.ir.tag}"
        return self.ir.instr

    def __repr__(self):
        regs_repr = (
            f"ac={hex(self.ac)} ip={hex(self.ip)} "
            f"ar={hex(self.ar)} dr={hex(self.dr)} sp={hex(self.sp)} "
            f"fl={hex(self.fl)}"
        )
        stack_repr = f"stack_top={'?' if self.sp >= len(self.memory) else hex(self.memory[self.sp].val)}"
        return f"{regs_repr} {stack_repr}"


class ControlUnit:
    def __init__(self, data_path: DataPath):
        self.data_path = data_path
        self.ticks = 0

        self.control_instruction_executors: dict[Opcode, typing.Callable[[Term], None]] = {
            Opcode.HALT: self.execute_halt_control_instruction,
            Opcode.CALL: self.execute_call_control_instruction,
            Opcode.RETURN: self.execute_return_control_instruction,
            Opcode.JUMP_EQUAL: self.execute_jump_equal_control_instruction,
            Opcode.JUMP_GREATER: self.execute_jump_greater_control_instruction,
            Opcode.JUMP_GREATER_EQUAL: self.execute_jump_greater_equal_control_instruction,
            Opcode.JUMP: self.execute_jump_control_instruction,
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
        self.data_path.signal_alu(right=Reg.SP, set_regs=[Reg.AR, Reg.SP], opts=inv_left)
        self.tick()
        self.data_path.signal_alu(left=Reg.IP, set_regs=[Reg.DR], opts=plus_1)
        self.tick()
        self.data_path.signal_write_memory()
        self.tick()
        self.data_path.signal_alu(left=Reg.IR, set_regs=[Reg.IP], opts=extend_20)
        self.tick()

    def execute_pop_into(self, reg: Reg):
        self.data_path.signal_alu(right=Reg.SP, set_regs=[Reg.AR])
        self.tick()
        self.data_path.signal_read_memory()
        self.tick()
        self.data_path.signal_alu(right=Reg.DR, set_regs=[reg])
        self.tick()
        self.data_path.signal_alu(right=Reg.SP, set_regs=[Reg.SP], opts=plus_1)
        self.tick()

    # noinspection PyUnusedLocal
    def execute_return_control_instruction(self, instr: Term):
        self.execute_pop_into(Reg.IP)

    def execute_jump_equal_control_instruction(self, instr: Term):
        assert instr.arg.tag == AddressType.RELATIVE_IPR, f"unsupported addressing for jme, got {instr}"
        if self.data_path.zero():
            self.data_path.signal_alu(left=Reg.IP, set_regs=[Reg.AR])
            self.tick()
            self.data_path.signal_alu(left=Reg.IR, right=Reg.AR, set_regs=[Reg.IP], opts=extend_20)
            self.tick()
        else:
            self.data_path.signal_alu(left=Reg.IP, set_regs=[Reg.IP], opts=plus_1)
            self.tick()

    def execute_jump_greater_control_instruction(self, instr: Term):
        assert instr.arg.tag == AddressType.RELATIVE_IPR, f"unsupported addressing for jmg, got {instr}"
        if self.data_path.negative() == self.data_path.overflow() and self.data_path.zero() is False:
            self.data_path.signal_alu(left=Reg.IP, set_regs=[Reg.AR])
            self.tick()
            self.data_path.signal_alu(left=Reg.IR, right=Reg.AR, set_regs=[Reg.IP], opts=extend_20)
            self.tick()
        else:
            self.data_path.signal_alu(left=Reg.IP, set_regs=[Reg.IP], opts=plus_1)
            self.tick()

    def execute_jump_greater_equal_control_instruction(self, instr: Term):
        assert instr.arg.tag == AddressType.RELATIVE_IPR, f"unsupported addressing for jmge, got {instr}"
        if self.data_path.negative() == self.data_path.overflow() or self.data_path.zero() is True:
            self.data_path.signal_alu(left=Reg.IP, set_regs=[Reg.AR])
            self.tick()
            self.data_path.signal_alu(left=Reg.IR, right=Reg.AR, set_regs=[Reg.IP], opts=extend_20)
            self.tick()
        else:
            self.data_path.signal_alu(left=Reg.IP, set_regs=[Reg.IP], opts=plus_1)
            self.tick()

    def execute_jump_control_instruction(self, instr: Term):
        assert instr.arg.tag in (
            AddressType.ABSOLUTE,
            AddressType.RELATIVE_IPR,
        ), f"unsupported addressing for jmp, got {instr}"
        if instr.arg.tag == AddressType.ABSOLUTE:
            self.data_path.signal_alu(left=Reg.IR, set_regs=[Reg.IP], opts=extend_20)
            self.tick()
        else:
            self.data_path.signal_alu(left=Reg.IP, set_regs=[Reg.AR])
            self.tick()
            self.data_path.signal_alu(left=Reg.IR, right=Reg.AR, set_regs=[Reg.IP], opts=extend_20)
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
            self.data_path.signal_alu(left=Reg.IR, set_regs=[Reg.AR], opts=extend_20)
            self.tick()
        elif addr.tag == AddressType.RELATIVE_SPR:
            self.data_path.signal_alu(left=Reg.IR, right=Reg.SP, set_regs=[Reg.AR], opts=extend_20)
            self.tick()
        elif addr.tag == AddressType.RELATIVE_INDIRECT_SPR:
            self.data_path.signal_alu(left=Reg.IR, right=Reg.SP, set_regs=[Reg.AR], opts=extend_20)
            self.tick()
            self.data_path.signal_read_memory()
            self.tick()
            self.data_path.signal_alu(right=Reg.DR, set_regs=[Reg.AR])
            self.tick()
        else:
            raise NotImplementedError(f"unsupported address type for address decoding, got {instr}")

    def value_fetch(self, instr: Term):
        addr = instr.arg
        if addr.tag == AddressType.EXACT:
            self.data_path.signal_alu(left=Reg.IR, set_regs=[Reg.DR], opts=extend_20)
            self.tick()
        elif addr.tag in (AddressType.ABSOLUTE, AddressType.RELATIVE_SPR, AddressType.RELATIVE_INDIRECT_SPR):
            self.data_path.signal_read_memory()
            self.tick()
        else:
            raise NotImplementedError(f"unsupported address type for value fetching, got {instr}")

    def execute_noop(self):
        self.tick()

    def execute_load(self):
        self.data_path.signal_alu(right=Reg.DR, set_regs=[Reg.AC])
        self.tick()

    def execute_store(self):
        self.data_path.signal_alu(left=Reg.AC, set_regs=[Reg.DR])
        self.tick()
        self.data_path.signal_write_memory()
        self.tick()

    def execute_push(self):
        self.data_path.signal_alu(right=Reg.SP, set_regs=[Reg.AR, Reg.SP], opts=inv_left)
        self.tick()
        self.data_path.signal_alu(left=Reg.AC, set_regs=[Reg.DR])
        self.tick()
        self.data_path.signal_write_memory()
        self.tick()

    def execute_pop(self):
        self.execute_pop_into(Reg.AC)

    def execute_popn(self):
        self.data_path.signal_alu(right=Reg.SP, set_regs=[Reg.SP], opts=plus_1)
        self.tick()

    def execute_compare(self):
        self.data_path.signal_alu(left=Reg.AC, right=Reg.DR, opts=inv_right | plus_1 | set_flags)
        self.tick()

    def execute_inc(self):
        self.data_path.signal_read_memory()
        self.tick()
        self.data_path.signal_alu(right=Reg.DR, set_regs=[Reg.DR], opts=plus_1)
        self.tick()
        self.data_path.signal_write_memory()
        self.tick()

    def execute_dec(self):
        self.data_path.signal_read_memory()
        self.tick()
        self.data_path.signal_alu(right=Reg.DR, set_regs=[Reg.DR], opts=inv_left)
        self.tick()
        self.data_path.signal_write_memory()
        self.tick()

    def execute_modulo(self):
        self.data_path.signal_alu(left=Reg.AC, right=Reg.DR, alu_op=AluOp.MOD, set_regs=[Reg.AC])
        self.tick()

    def execute_add(self):
        self.data_path.signal_alu(left=Reg.AC, right=Reg.DR, set_regs=[Reg.AC])
        self.tick()

    def execute_subtract(self):
        self.data_path.signal_alu(left=Reg.AC, right=Reg.DR, set_regs=[Reg.AC], opts=inv_right | plus_1)
        self.tick()

    def execute_multiply(self):
        self.data_path.signal_alu(left=Reg.AC, right=Reg.DR, alu_op=AluOp.MUL, set_regs=[Reg.AC])
        self.tick()

    def execute_divide(self):
        self.data_path.signal_alu(left=Reg.AC, right=Reg.DR, alu_op=AluOp.DIV, set_regs=[Reg.AC])
        self.tick()

    def execute_inverse(self):
        self.data_path.signal_alu(left=Reg.AC, set_regs=[Reg.AC], opts=inv_left | plus_1)
        self.tick()

    def execute(self, instr: Term):
        opcode = instr.op
        if opcode not in self.ordinary_instruction_executors:
            raise NotImplementedError(f"Unknown instruction, got {instr}")
        self.ordinary_instruction_executors[opcode]()

    def finalize(self):
        self.data_path.signal_alu(left=Reg.IP, set_regs=[Reg.IP], opts=plus_1)

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
