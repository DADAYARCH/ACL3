from __future__ import annotations

import json
from enum import Enum


class Opcode(str, Enum):
    NOOP = "noop"
    HALT = "halt"

    LOAD = "ld"
    STORE = "st"

    CALL = "call"
    RETURN = "ret"

    PUSH = "push"
    POP = "pop"
    POPN = "popn"

    COMPARE = "cmp"
    JUMP_EQUAL = "jme"
    JUMP_GREATER = "jmg"
    JUMP_GREATER_EQUAL = "jmge"
    JUMP = "jmp"

    INCREMENT = "inc"
    DECREMENT = "dec"

    MODULO = "mod"
    ADD = "add"
    SUBTRACT = "sub"
    MULTIPLY = "mul"
    DIVIDE = "div"
    INVERSE = "inv"


no_arg_ops: list[Opcode] = [Opcode.HALT, Opcode.RETURN, Opcode.PUSH, Opcode.POP, Opcode.POPN, Opcode.INVERSE]

addr_ops: list[Opcode] = [
    Opcode.STORE,
    Opcode.CALL,
    Opcode.JUMP_EQUAL,
    Opcode.JUMP_GREATER,
    Opcode.JUMP_GREATER_EQUAL,
    Opcode.JUMP,
    Opcode.INCREMENT,
    Opcode.DECREMENT,
]

value_ops: list[Opcode] = [
    Opcode.LOAD,
    Opcode.COMPARE,
    Opcode.MODULO,
    Opcode.ADD,
    Opcode.SUBTRACT,
    Opcode.MULTIPLY,
    Opcode.DIVIDE,
]

branch_ops: list[Opcode] = [Opcode.JUMP_EQUAL, Opcode.JUMP_GREATER, Opcode.JUMP_GREATER_EQUAL, Opcode.JUMP]


class AddressType(str, Enum):
    EXACT = "#"
    ABSOLUTE = "*"
    RELATIVE_IPR = "*ipr"
    RELATIVE_SPR = "*spr"
    RELATIVE_INDIRECT_SPR = "**spr"


offset_addresses: list[AddressType] = [
    AddressType.RELATIVE_IPR,
    AddressType.RELATIVE_SPR,
    AddressType.RELATIVE_INDIRECT_SPR,
]


class Address:
    def __init__(self, tag: AddressType, val: int):
        self.tag = tag
        self.val = val

    def __str__(self):
        val_str: str = hex(self.val)
        if self.tag in offset_addresses:
            if self.val > 0:
                val_str = "+" + val_str
            elif self.val == 0:
                val_str = ""
        return f"{self.tag.value}{val_str}"


class Term:
    def __init__(self, op: Opcode, arg: str | int | Address | None = None, desc: str | None = None):
        self.op = op
        self.arg = arg
        self.desc = desc

    def __str__(self):
        s = f"{self.op.value}"
        if self.arg:
            s += f" {self.arg}"
        if self.desc:
            s += f" ({self.desc})"
        return s


class WordType(str, Enum):
    INSTRUCTION = "INSTRUCTION"
    BINARY = "BINARY"


class Word:
    def __init__(self, tag: WordType, instr: Term | None = None, val: int | None = None):
        self.tag = tag
        self.instr = instr
        self.val = val


class Code:
    def __init__(self, text: list[tuple[int, int, str, list[Term]]], data: list[tuple[int, int, str, list]]):
        self.text = text
        self.data = data

    def __len__(self):
        last_block = self.text[-1]
        return last_block[0] + last_block[1]


def default_serialize(obj):
    return {k: v for k, v in obj.__dict__.items() if v is not None}


def code_to_words(code: Code) -> list[Word]:
    words = []
    for block in code.text:
        for instr in block[3]:
            words.append(Word(WordType.INSTRUCTION, instr=instr))
    for block in code.data:
        for data in block[3]:
            words.append(Word(WordType.BINARY, val=data))
    return words


def serialize(code: Code) -> str:
    return json.dumps(code_to_words(code), default=default_serialize, indent=2)


def deserialize_arg(raw_arg: dict) -> Address:
    tag = AddressType(raw_arg["tag"])
    val = raw_arg["val"]
    return Address(tag, val)


def deserialize_instruction(raw_instr: dict) -> Term:
    op = Opcode(raw_instr["op"])
    term = Term(op)
    if op not in no_arg_ops:
        term.arg = deserialize_arg(raw_instr["arg"])
    return term


def deserialize(string: str) -> list[Word]:
    words = []
    raw_words = json.loads(string)
    for raw_word in raw_words:
        tag = WordType(raw_word["tag"])
        word = Word(tag)
        match tag:
            case WordType.INSTRUCTION:
                word.instr = deserialize_instruction(raw_word["instr"])
            case WordType.BINARY:
                val = raw_word["val"]
                if isinstance(val, int):
                    word.val = raw_word["val"]
                elif isinstance(val, str):
                    assert len(val) == 1, f"Unknown binary word format, got {val}"
                    word.val = ord(val)
        words.append(word)
    return words
