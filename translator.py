from __future__ import annotations

import argparse
import collections
import copy
import typing
from enum import Enum

import lexer
import stdlib
from isa import Address, AddressType, Code, Opcode, Term, serialize


def extract_tokens(src) -> list[lexer.TokenInfo]:
    return lexer.lex(src, lexer.token_expressions)


class ASTNode:
    def __init__(
        self, token: lexer.TokenInfo | None = None, parent: ASTNode | None = None, children: list[ASTNode] | None = None
    ):
        self.token = token
        self.parent = parent
        self.children = [] if children is None else children


def build_ast(tokens: list[lexer.TokenInfo]) -> ASTNode:
    root = ASTNode()
    node = root
    for token in tokens:
        if token.string == "(":
            child = ASTNode(token, node)
            node.children.append(child)
            node = child
        elif token.string == ")":
            assert node.parent, "Wrong parenthesis count"
            node = node.parent
        else:
            if token.tag == lexer.STR:
                token.string = token.string[1:-1]
            node.children.append(ASTNode(token, node))
    assert node == root, "Wrong parenthesis count"
    return root


predefined_funcs: dict[str, stdlib.FuncInfo] = {func.name: func for func in stdlib.ALL_FUNCS}


class FuncContext:
    def __init__(self):
        self.args_table: dict[str, int] = {}

    def has_in_acr(self) -> bool:
        return -1 in self.args_table.values()

    def get_in_acr(self) -> str:
        return list(self.args_table.keys())[list(self.args_table.values()).index(-1)]

    def on_push(self):
        self.args_table = {k: v + 1 for k, v in self.args_table.items()}

    def on_pop(self):
        self.args_table = {k: v - 1 for k, v in self.args_table.items()}


class ProgramContext:
    def __init__(self):
        self.defined_funcs: dict[str, stdlib.FuncInfo] = copy.deepcopy(predefined_funcs)
        self.function_table: list[str] = []

        self.str_const_table: list[str] = []
        self.int_const_table: list[int] = []
        self.var_table: list[str] = []
        self.anon_var_table: dict[str, tuple[int, int]] = collections.OrderedDict()
        self.anon_var_pointer = 0
        self.anon_var_counter = 0

        self.func_context: FuncContext | None = None

    def require_func(self, func: str):
        assert func in self.defined_funcs, f"Unknown func {func}"
        if func not in self.function_table:
            self.function_table.append(func)

    def define_func(self, name: str, argc: int):
        assert name not in self.defined_funcs, f"Function {name} already defined"
        assert argc >= 0, f"Function must have positive or zero arguments, got {argc}"
        self.defined_funcs[name] = stdlib.FuncInfo(name, argc)

    def implement_func(self, name: str, code: list[Term]):
        assert name in self.defined_funcs, f"Unknown function to implement, got {name}"
        func_info = self.defined_funcs[name]
        assert len(func_info.code) == 0, f"Reimplementation of function {name}"
        assert len(code) > 0, f"Implementation must have at least 1 statement, got {code}"
        func_info.code = code

    def func_info(self, func: str) -> stdlib.FuncInfo:
        assert func in self.defined_funcs, f"Unknown func {func}"
        return self.defined_funcs[func]

    def require_int_const(self, const: int):
        assert const < (1 << 63), f"Value must be less than {1 << 63}, got {const}"
        assert const > (-(1 << 63) - 1), f"Value must be greater than {- (1 << 63) - 1}, got {const}"
        if const not in self.int_const_table:
            self.int_const_table.append(const)

    def require_str_const(self, const: str):
        assert const[0] != '"', f"Value must be trimmed, got {const}"
        assert const[-1] != '"', f"Value must be trimmed, got {const}"
        if const not in self.str_const_table:
            self.str_const_table.append(const)

    def require_anon_variable(self, size: int) -> str:
        assert size > 0, f"negative size buffer?, got {size}"
        name = f"anon${self.anon_var_counter}"
        self.anon_var_counter += 1
        self.anon_var_table[name] = (self.anon_var_pointer, size)
        self.anon_var_pointer += size
        return name

    def require_variable(self, name: str):
        if name not in self.var_table:
            self.var_table.append(name)

    def set_func_context(self, fc: FuncContext | None):
        self.func_context = fc

    def get_func_context(self) -> FuncContext | None:
        return self.func_context

    def func_context_has_in_acr(self) -> bool:
        return self.func_context and self.func_context.has_in_acr()

    def func_context_on_push(self):
        if self.func_context:
            self.func_context.on_push()

    def func_context_on_pop(self):
        if self.func_context:
            self.func_context.on_pop()


class Tag(Enum):
    INVOKE = "INVOKE"
    INT_CONST = "INT_CONST"
    STR_CONST = "STR_CONST"
    VALUE = "VALUE"
    REFERENCE = "REFERENCE"


class Statement:
    def __init__(self, tag: Tag, name: str | None = None, args: list[Statement] | None = None, val: int | None = None):
        self.tag = tag
        self.name = name
        self.args = [] if args is None else args
        self.val = val


def const_statement(node: ASTNode, context: ProgramContext) -> Statement:
    token = node.token
    assert token.tag in (lexer.INT, lexer.STR), f"Unknown const type {token.tag}"
    match token.tag:
        case lexer.INT:
            int_val = int(node.token.string)
            if (1 << 19) > int_val > (-(1 << 19) - 1):
                return Statement(Tag.VALUE, val=int_val)
            context.require_int_const(int_val)
            return Statement(Tag.INT_CONST, val=int_val)
        case lexer.STR:
            str_val = node.token.string.encode("raw_unicode_escape").decode("unicode_escape")
            context.require_str_const(str_val)
            return Statement(Tag.STR_CONST, name=str_val)


def invoke_statement(node: ASTNode, context: ProgramContext) -> Statement:
    children = node.children
    assert len(children[0].children) == 0, "Name of statement must be string"
    name = children[0].token.string
    func = context.func_info(name)
    children_nodes = children[1:]
    assert func.argc == len(children_nodes), f"Wrong amount of arguments for func {name}"
    children_statements = []
    for i in range(len(children_nodes)):
        children_statements.append(ast_to_statement(children_nodes[i], context))
    return Statement(Tag.INVOKE, name=name, args=children_statements)


def special_statement(node: ASTNode, context: ProgramContext) -> Statement:
    children = node.children
    name = children[0].token.string
    assert name in ("set", "if", "loop"), f"unknown special statement, got {name}"
    match name:
        case "set":
            assert len(children) == 3, "Set statement must contains of variable name and value to set"
            key, val = children[1], children[2]
            assert key.token.tag == lexer.ID, f"variable name must be ID, got {key.token}"
            args = [Statement(Tag.REFERENCE, name=key.token.string), ast_to_statement(val, context)]
            context.require_variable(key.token.string)
            return Statement(Tag.INVOKE, name=name, args=args)
        case "if":
            assert len(children) == 4, "if statement must contains condition and 2 options"
            cond, opt1, opt2 = children[1], children[2], children[3]
            args = [ast_to_statement(cond, context), ast_to_statement(opt1, context), ast_to_statement(opt2, context)]
            return Statement(Tag.INVOKE, name=name, args=args)
        case "loop":
            assert len(children) == 2, "loop statement must contains of only one statement"
            loop = children[1]
            args = [ast_to_statement(loop, context)]
            return Statement(Tag.INVOKE, name=name, args=args)


# noinspection PyUnusedLocal
def reference_statement(node: ASTNode, context: ProgramContext) -> Statement:
    symbol = node.token.string
    return Statement(Tag.REFERENCE, name=symbol)


def math_statement(node: ASTNode, context: ProgramContext) -> Statement:
    children = node.children
    name = children[0].token.string
    assert name in ("mod", "+", "-", "/", "*"), f"unknown math statement, got {name}"
    if name in ("mod", "-", "/"):
        assert len(children) == 3, f"math statement can operate only with 2 args, got {len(children)}"
    args = []
    for child in children[1:]:
        args.append(ast_to_statement(child, context))
    return Statement(Tag.INVOKE, name=name, args=args)


def bool_statement(node: ASTNode, context: ProgramContext):
    children = node.children
    name = children[0].token.string
    assert name in ("=", ">=", ">"), f"unknown boolean statement, got {name}"
    assert len(children) == 3, "= statement must contains of 2 values to compare"
    args = [ast_to_statement(children[1], context), ast_to_statement(children[2], context)]
    return Statement(Tag.INVOKE, name=name, args=args)


def defun_statement(node: ASTNode, context: ProgramContext) -> Statement:
    children = node.children
    name = children[0].token.string
    assert len(children) == 4, "defunc statement must contains of name, arguments and body"

    func_name = children[1].token
    assert func_name.tag == lexer.ID, f"func name must be ID, got {func_name.tag}"
    func_name = func_name.string

    args = children[2].children
    assert children[2].token.string == "(", f"arguments must be in parenthesis, got {children[2].token}"

    name_st = Statement(Tag.REFERENCE, name=func_name)
    args_st = Statement(Tag.INVOKE)
    for arg in args:
        assert arg.token.tag == lexer.ID, f"args must be ID, got {arg}"
        arg_name = arg.token.string
        args_st.args.append(Statement(Tag.REFERENCE, name=arg_name))

    context.define_func(func_name, len(args_st.args))
    body_st = ast_to_statement(children[3], context)
    return Statement(Tag.INVOKE, name=name, args=[name_st, args_st, body_st])


with_children_translators: dict[str, typing.Callable[[ASTNode, ProgramContext], Statement]] = {
    lexer.FUNC: invoke_statement,
    lexer.SPECIAL: special_statement,
    lexer.MATH: math_statement,
    lexer.BOOL: bool_statement,
    lexer.DEFUNC: defun_statement,
    lexer.ID: invoke_statement,
}

without_children_translators: dict[str, typing.Callable[[ASTNode, ProgramContext], Statement]] = {
    lexer.STR: const_statement,
    lexer.INT: const_statement,
    lexer.ID: reference_statement,
}


def ast_to_statement(node: ASTNode, context: ProgramContext) -> Statement:
    children = node.children
    if len(children) > 0:
        tag = children[0].token.tag
        assert tag in with_children_translators, f"unknown node with children token tag, got {tag}"
        return with_children_translators[tag](node, context)
    tag = node.token.tag
    assert tag in without_children_translators, f"unknown node without children token tag, got {tag}"
    return without_children_translators[tag](node, context)


def extract_statements(root: ASTNode, context: ProgramContext) -> list[Statement]:
    statements = []
    for node in root.children:
        statements.append(ast_to_statement(node, context))
    return statements


def translate_invoke_statement_argument(arg: Statement, context: ProgramContext) -> list[Term]:
    arg_code = []
    fc = context.get_func_context()
    assert arg.tag in (
        Tag.VALUE,
        Tag.INT_CONST,
        Tag.STR_CONST,
        Tag.INVOKE,
        Tag.REFERENCE,
    ), f"unknown tag of invoke statement argument, got {arg.tag}"
    match arg.tag:
        case Tag.VALUE:
            if fc and fc.has_in_acr():
                arg_code.append(Term(Opcode.PUSH))
                fc.on_push()
            arg_code.append(Term(Opcode.LOAD, Address(AddressType.EXACT, arg.val)))
        case Tag.INT_CONST | Tag.STR_CONST:
            if fc and fc.has_in_acr():
                arg_code.append(Term(Opcode.PUSH))
                fc.on_push()
            arg = arg.val if arg.tag == Tag.INT_CONST else arg.name
            arg_code.append(Term(Opcode.LOAD, arg))
        case Tag.INVOKE:
            arg_code.extend(translate_invoke_statement(arg, context))
        case Tag.REFERENCE:
            if fc and fc.has_in_acr() and fc.get_in_acr() == arg.name:
                pass
            elif fc and arg.name in fc.args_table:
                if fc.has_in_acr():
                    arg_code.append(Term(Opcode.PUSH))
                    fc.on_push()
                desc = repr(arg.name) + " argument"
                arg_code.append(Term(Opcode.LOAD, Address(AddressType.RELATIVE_SPR, fc.args_table[arg.name]), desc))
            else:
                arg_code.append(Term(Opcode.LOAD, arg.name))
    return arg_code


def translate_read_statement(read: Statement, context: ProgramContext) -> list[Term]:
    code = []
    if context.func_context_has_in_acr():
        code.append(Term(Opcode.PUSH))
        context.func_context_on_push()
    read.anon_var_name = context.require_anon_variable(stdlib.READ_LIMIT + 1)
    code.extend([Term(Opcode.LOAD, read.anon_var_name), Term(Opcode.CALL, read.name)])
    return code


def translate_printi_statement(printi: Statement, context: ProgramContext) -> list[Term]:
    code = []
    if context.func_context_has_in_acr():
        code.append(Term(Opcode.PUSH))
        context.func_context_on_push()
    context.require_func(stdlib.PRINT_FUNC.name)
    printi.anon_var_name = context.require_anon_variable(21)
    code.extend([Term(Opcode.LOAD, printi.anon_var_name), Term(Opcode.PUSH)])
    context.func_context_on_push()
    code.extend(translate_invoke_statement_argument(printi.args[0], context))
    code.extend([Term(Opcode.CALL, printi.name), Term(Opcode.POPN)])
    context.func_context_on_pop()
    return code


def translate_set_statement(set_st: Statement, context: ProgramContext) -> list[Term]:
    variable, value = set_st.args[0], set_st.args[1]
    assert variable.tag == Tag.REFERENCE, f"unexpected variable statement type, got {variable}"
    context.require_variable(variable.name)
    code = translate_invoke_statement_argument(value, context)
    code.append(Term(Opcode.STORE, variable.name))
    return code


math_opcode = {"mod": Opcode.MODULO, "+": Opcode.ADD, "-": Opcode.SUBTRACT, "*": Opcode.MULTIPLY, "/": Opcode.DIVIDE}


def translate_math_statement(statement: Statement, context: ProgramContext) -> list[Term]:
    code = []
    opcode = math_opcode[statement.name]
    last_arg = statement.args[-1]
    code.extend(translate_invoke_statement_argument(last_arg, context))
    code.append(Term(Opcode.PUSH))
    context.func_context_on_push()
    for arg in statement.args[-2::-1]:
        code.extend(translate_invoke_statement_argument(arg, context))
        code.append(Term(opcode, Address(AddressType.RELATIVE_SPR, 0)))
        code.append(Term(Opcode.STORE, Address(AddressType.RELATIVE_SPR, 0)))
    code.append(Term(Opcode.POP))
    context.func_context_on_pop()
    return code


bool_opcode = {"=": Opcode.JUMP_EQUAL, ">": Opcode.JUMP_GREATER, ">=": Opcode.JUMP_GREATER_EQUAL}


def translate_bool_statement(statement: Statement, context: ProgramContext) -> list[Term]:
    code = []
    opcode = bool_opcode[statement.name]
    code.extend(translate_invoke_statement_argument(statement.args[1], context))
    code.append(Term(Opcode.PUSH))
    context.func_context_on_push()
    code.extend(translate_invoke_statement_argument(statement.args[0], context))
    code.extend(
        [
            Term(Opcode.COMPARE, Address(AddressType.RELATIVE_SPR, 0)),
            Term(Opcode.POPN),
            Term(opcode, Address(AddressType.RELATIVE_IPR, 3)),
            Term(Opcode.LOAD, Address(AddressType.EXACT, 0)),
            Term(Opcode.JUMP, Address(AddressType.RELATIVE_IPR, 2)),
            Term(Opcode.LOAD, Address(AddressType.EXACT, 1)),
        ]
    )
    context.func_context_on_pop()
    return code


def translate_if_statement(statement: Statement, context: ProgramContext) -> list[Term]:
    code = []
    cond_code = translate_invoke_statement_argument(statement.args[0], context)
    opt1_code = translate_invoke_statement_argument(statement.args[1], context)
    opt2_code = translate_invoke_statement_argument(statement.args[2], context)
    opt1_code.append(Term(Opcode.JUMP, Address(AddressType.RELATIVE_IPR, len(opt2_code) + 1)))
    cond_code.extend(
        [
            Term(Opcode.COMPARE, Address(AddressType.EXACT, 0)),
            Term(Opcode.JUMP_EQUAL, Address(AddressType.RELATIVE_IPR, len(opt1_code) + 1)),
        ]
    )
    code.extend(cond_code)
    code.extend(opt1_code)
    code.extend(opt2_code)
    return code


def translate_defun_statement(defun: Statement, context: ProgramContext) -> list[Term]:
    func_code = []
    func_name = defun.args[0].name
    arguments: list[Statement] = defun.args[1].args
    func_context = FuncContext()
    if len(arguments) > 0:
        first_argument = arguments[0]
        func_context.args_table[first_argument.name] = -1
    for i, argument in enumerate(arguments[1:]):
        func_context.args_table[argument.name] = 1 + i
    context.set_func_context(func_context)
    func_code.extend(translate_invoke_statement_argument(defun.args[2], context))
    context.set_func_context(None)
    if 0 in func_context.args_table.values():
        func_code.append(Term(Opcode.POPN))
    func_code.append(Term(Opcode.RETURN))
    context.implement_func(func_name, func_code)
    return []


def translate_loop_statement(statement: Statement, context: ProgramContext):
    code = []
    code.extend(translate_invoke_statement_argument(statement.args[0], context))
    code.append(Term(Opcode.JUMP, Address(AddressType.RELATIVE_IPR, -len(code))))
    return code


def translate_invoke_statement_common(statement: Statement, context: ProgramContext) -> list[Term]:
    args = statement.args
    code = []
    for arg in args[-1:0:-1]:
        code.extend(translate_invoke_statement_argument(arg, context))
        code.append(Term(Opcode.PUSH))
        context.func_context_on_push()
    if len(args) > 0:
        code.extend(translate_invoke_statement_argument(args[0], context))
    code.append(Term(Opcode.CALL, statement.name))
    for _ in range(len(args) - 1):
        code.append(Term(Opcode.POPN))
        context.func_context_on_pop()
    return code


special_invoke_statement_translators: dict[str, typing.Callable[[Statement, ProgramContext], list[Term]]] = {
    stdlib.READLINE_FUNC.name: translate_read_statement,
    stdlib.PRINT_INTEGER_FUNC.name: translate_printi_statement,
}


def translate_invoke_statement(statement: Statement, context: ProgramContext) -> list[Term]:
    match statement.name:
        case "set":
            return translate_set_statement(statement, context)
        case "mod" | "+" | "-" | "/" | "*":
            return translate_math_statement(statement, context)
        case "=" | ">" | ">=":
            return translate_bool_statement(statement, context)
        case "if":
            return translate_if_statement(statement, context)
        case "defun":
            return translate_defun_statement(statement, context)
        case "loop":
            return translate_loop_statement(statement, context)
    context.require_func(statement.name)
    if statement.name in special_invoke_statement_translators:
        return special_invoke_statement_translators[statement.name](statement, context)
    return translate_invoke_statement_common(statement, context)


def translate_statement(statement: Statement, context: ProgramContext) -> list[Term]:
    if statement.tag == Tag.INVOKE:
        return translate_invoke_statement(statement, context)
    raise NotImplementedError(f"unknown tag of statement to translate, got {statement.tag}")


def fill_instr_memory(
    func_table: dict[str, int], symbols: set[str], start_code: list[Term], context: ProgramContext
) -> list[tuple[int, int, str, list[Term]]]:
    memory = []
    instr_pointer = 0
    memory.append((0, 1, "#", [Term(Opcode.JUMP, "start")]))
    func_table["#"] = 0
    instr_pointer += 1
    for func_name in context.function_table:
        func_info = context.defined_funcs[func_name]
        func_table[func_info.name] = instr_pointer
        symbols.add(func_info.name)
        memory.append((instr_pointer, len(func_info.code), func_info.name, func_info.code))
        instr_pointer += len(func_info.code)
    func_table["start"] = instr_pointer
    symbols.add("start")
    memory.append((instr_pointer, len(start_code), "start", start_code))
    instr_pointer += len(start_code)
    return memory


def fill_data_memory(
    offset: int,
    const_table: dict[str | int, int],
    var_table: dict[str, int],
    symbols: set[str],
    context: ProgramContext,
) -> list[tuple[int, int, str, list]]:
    memory = []
    data_pointer = offset
    for str_const in context.str_const_table:
        data = [*str_const, "\0"]
        const_table[str_const] = data_pointer
        symbols.add(str_const)
        memory.append((data_pointer, len(data), repr(str_const), data))
        data_pointer += len(data)
    for int_const in context.int_const_table:
        const_table[int_const] = data_pointer
        symbols.add(str(int_const))
        memory.append((data_pointer, 1, str(int_const), [int_const]))
        data_pointer += 1
    for symbol in context.var_table:
        var_table[symbol] = data_pointer
        symbols.add(symbol)
        data_pointer += 1
    for symbol in context.anon_var_table:
        offset, _ = context.anon_var_table[symbol]
        const_table[symbol] = data_pointer + offset
        symbols.add(symbol)
    return memory


def resolve_symbols(
    instr_memory: list[tuple[int, int, str, list[Term]]],
    symbols: set[str],
    func_table: dict[str, int],
    const_table: dict[str | int, int],
    var_table: dict[str, int],
):
    for block in instr_memory:
        for instr in block[3]:
            if isinstance(instr.arg, str):
                assert instr.arg in symbols, f"unknown symbol, got {instr.arg}"
                instr.desc = repr(instr.arg)
                if instr.arg in const_table:
                    instr.desc += " const"
                    instr.arg = Address(AddressType.EXACT, const_table[instr.arg])
                elif instr.arg in var_table:
                    instr.desc += " variable"
                    instr.arg = Address(AddressType.ABSOLUTE, var_table[instr.arg])
                else:
                    instr.desc += " function"
                    instr.arg = Address(AddressType.ABSOLUTE, func_table[instr.arg])
            elif isinstance(instr.arg, int):
                assert str(instr.arg) in symbols, f"unknown symbol, got {instr.arg}"
                instr.desc = f"{instr.arg} const"
                instr.arg = Address(AddressType.ABSOLUTE, const_table[instr.arg])


def translate_into_code(statements: list[Statement], context: ProgramContext) -> Code:
    start_code = []
    for s in statements:
        start_code.extend(translate_statement(s, context))
    start_code.append(Term(Opcode.HALT))

    symbols: set[str] = set()
    const_table: dict[str | int, int] = {}
    var_table: dict[str, int] = {}
    func_table: dict[str, int] = {}

    instr_memory = fill_instr_memory(func_table, symbols, start_code, context)
    offset = instr_memory[-1][0] + instr_memory[-1][1]
    data_memory = fill_data_memory(offset, const_table, var_table, symbols, context)
    resolve_symbols(instr_memory, symbols, func_table, const_table, var_table)

    return Code(instr_memory, data_memory)


def translate(src: str) -> Code:
    tokens = extract_tokens(src)
    ast = build_ast(tokens)
    program_context = ProgramContext()
    statements = extract_statements(ast, program_context)
    return translate_into_code(statements, program_context)


def read_source(src: typing.TextIO) -> str:
    return src.read()


def write_code(dst: typing.TextIO, code: Code) -> (bytearray, str):
    dst.write(serialize(code))


def main(src: typing.TextIO, dst: typing.TextIO):
    source = read_source(src)
    code = translate(source)
    write_code(dst, code)

    loc, code_instr = len(source.split("\n")), len(code)
    print(f"LoC: {loc} code instr: {code_instr}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translates source code into en executable file.")
    parser.add_argument(
        "src", type=argparse.FileType(encoding="utf-8"), metavar="source_file", help="file with source code"
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="dst",
        type=argparse.FileType("w", encoding="utf-8"),
        default="output",
        metavar="output_file",
        help="file for storing an executable (default: output)",
    )
    namespace = parser.parse_args()
    main(namespace.src, namespace.dst)
