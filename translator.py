from __future__ import annotations

import sys

from isa import (
    Opcode,
    op3,
    op1,
    op2,
    write_code,
    op0,
)


def command_to_opcode(command):

    return {
        "nop": Opcode.NOP,
        "hlt": Opcode.HLT,
        "inc": Opcode.INC,
        "dec": Opcode.DEC,
        "add": Opcode.ADD,
        "sub": Opcode.SUB,
        "mul": Opcode.MUL,
        "div": Opcode.DIV,
        "mod": Opcode.MOD,
        "mov": Opcode.MOV,
        "test": Opcode.TEST,
        "jg": Opcode.JG,
        "jng": Opcode.JNG,
        "jz": Opcode.JZ,
        "jnz": Opcode.JNZ,
        "jmp": Opcode.JMP,
    }.get(command, Opcode.NOP)


def read_asm(source_filename: str) -> tuple[int, list[str]]:
    lines = []
    source_loc = 0
    with open(source_filename) as file:
        for line in file:
            source_loc += 1
            line = line.strip()
            if line != "":
                lines.append(line)
    return source_loc, lines


def delete_comments(lines: list[str]) -> list[str]:
    lines_without_comments = []
    for line in lines:
        comment_index = line.find(";")
        if comment_index == -1:
            lines_without_comments.append(line)
        elif comment_index != 0:
            if line[:comment_index].count("'") % 2 == 1 and line[comment_index + 1 :].count("'") % 2 == 1:
                comment_index_new = line[comment_index + 1 :].find(";")
                if comment_index_new == -1:
                    lines_without_comments.append(line)
                else:
                    line = line[: comment_index + comment_index_new + 1]
                    line = line.strip()
                    lines_without_comments.append(line)
            else:
                line = line[:comment_index]
                line = line.strip()
                lines_without_comments.append(line)
    return lines_without_comments


def is_label(line: str) -> bool:
    return line.endswith(":")


def is_word(line: str) -> bool:
    return line.startswith(".word")


def word_is_str(word: str) -> bool:
    return word.startswith("'") and word.endswith("'")


PROGRAM_START_POSITION_IN_MEMORY = 4  # Считается, что до этого хранится служебная информация, изменение которой недопустимо


def find_labels(lines: list[str]) -> dict:
    labels = {}  # Хранит по ключ label_name значение label_position
    position = PROGRAM_START_POSITION_IN_MEMORY
    for line in lines:
        if is_label(line):  # Строка соответствует метке
            assert line not in labels, "Code error: label redefinition"
            labels[line[:-1]] = position

        elif is_word(line):  # Строка соответствует слову (.word)
            word = line[6::]
            word_length = 0
            if word_is_str(word):  # Данные строкового типа
                for symbol in word:
                    if 48 <= ord(symbol) <= 57:
                        word_length = word_length + 1
                    else:
                        break
                position += len(word[word_length:-1])
            else:  # Данные числового типа или сслыка на метку
                position += 1

        else:  # Строка соответствует команде
            position += 1
    return labels


def find_words(lines: list[str], labels: dict) -> list:
    words = []
    position = PROGRAM_START_POSITION_IN_MEMORY
    for line in lines:
        if is_word(line):  # Строка соответствует слову (.word)
            word = line[6::]
            if word_is_str(word):  # Данные строкового типа
                for symbol in word[1:-1]:
                    words.append(
                        {
                            "index": position,
                            "opcode": Opcode.NOP,
                            "arg_1": str(ord(symbol)),
                            "is_indirect_1": False,
                            "arg_2": None,
                            "is_indirect_2": None,
                        }
                    )
                    position += 1

                words.append(
                    {
                        "index": position,
                        "opcode": Opcode.NOP,
                        "arg_1": str(0),
                        "is_indirect_1": False,
                        "arg_2": None,
                        "is_indirect_2": None,
                    }
                )
                position += 1

            elif word.isdigit():  # Данные числового типа
                words.append(
                    {
                        "index": position,
                        "opcode": Opcode.NOP,
                        "arg_1": word,
                        "is_indirect_1": False,
                        "arg_2": None,
                        "is_indirect_2": None,
                    }
                )
                position += 1

            elif word in labels:  # Данные - ссылка на метку
                words.append(
                    {
                        "index": position,
                        "opcode": Opcode.NOP,
                        "arg_1": str(labels[word]),
                        "is_indirect_1": False,
                        "arg_2": None,
                        "is_indirect_2": None,
                    }
                )
                position += 1

            else:  # Не предвиденный тип данных для слова (.word)
                raise AssertionError("Code error: incorrect word" + word)

        elif not (is_label(line)):  # Строка соответствует команде
            position += 1

    return words


REGISTERS = ["r0", "r1", "r2", "r3"]


def parse_address(address: str, opcode: Opcode, labels: dict) -> tuple[str, bool, bool]:
    if address.startswith("(") and address.endswith(")"):
        is_indirect = True
        address = address[1:-1]
    else:
        is_indirect = False

    assert address.isdigit() or address in labels or address in REGISTERS, "Code error: missing address " + address

    in_labels = address in labels
    if in_labels:
        if opcode != Opcode.MOV and opcode not in op3:
            raise AssertionError("Code error: command " + str(opcode) + " only register-to-register")
        address = str(labels[address])

    return address, is_indirect, in_labels


def parse_command_to_code(line: str, position: int, labels: dict) -> dict:
    command = line.split(" ")[0]
    opcode = command_to_opcode(command)
    assert opcode != Opcode.NOP, "Code error: there is no such command " + command

    arg_1 = None
    is_indirect_1 = None
    arg_2 = None
    is_indirect_2 = None

    if command in op0:
        assert len(line.split(" ")) == 1, "Code error: the command " + command + " must have 0 args"

    elif command in op3 or command in op1:
        assert len(line[len(command) + 1 : :].split(", ")) == 1, (
            "Code error: the command " + command + " must have 1 args"
        )
        arg_1, is_indirect_1, in_labels_1 = parse_address(line[len(command) + 1 : :].split(", ")[0], opcode, labels)

    elif command in op2:
        assert len(line[len(command) + 1 : :].split(", ")) == 2, (
            "Code error: the command " + command + " must have 2 args"
        )
        args = line[len(command) + 1 : :].split(", ")
        arg_1, is_indirect_1, in_labels_1 = parse_address(args[0], opcode, labels)
        arg_2, is_indirect_2, in_labels_2 = parse_address(args[1], opcode, labels)
        assert not (in_labels_1 and in_labels_2), "Code error: mem-to-mem operations prohibited"
        assert not (is_indirect_1 and is_indirect_2), "Code error: double indirect addressing is prohibited"
        assert not (arg_1.startswith("r") and is_indirect_1), "Code error: indirect addressing with regs is prohibited"
        assert not (arg_2.startswith("r") and is_indirect_2), "Code error: indirect addressing with regs is prohibited"

    return {
        "index": position,
        "opcode": opcode,
        "arg_1": arg_1,
        "is_indirect_1": is_indirect_1,
        "arg_2": arg_2,
        "is_indirect_2": is_indirect_2,
    }


def find_code(lines: list[str], labels: dict) -> list:
    code = []
    position = PROGRAM_START_POSITION_IN_MEMORY
    for line in lines:
        if not (is_label(line) or is_word(line)):  # Строка соответствует команде
            code.append(parse_command_to_code(line, position, labels))
            position += 1

        elif is_word(line):  # Строка соответствует данным
            word = line[6::]
            if word_is_str(word):  # Данные строкового типа
                position += len(word[1:-1]) + 1  # +1, так как считаем нуль-терминатор
            else:  # Данные числового типа или сслыка на метку
                position += 1
    return code


def find_start(labels: dict) -> list:
    assert "_start" in labels, "Code error: Label _start not found"
    return [
        {
            "index": 0,
            "opcode": Opcode.JMP,
            "arg_1": str(labels["_start"]),
            "is_indirect_1": False,
            "arg_2": None,
            "is_indirect_2": None,
        }
    ]


def sort_code_by_index(code: list) -> list:
    return sorted(code, key=lambda d: d["index"])


def translate(lines: list[str]):
    lines = delete_comments(lines)

    labels = find_labels(lines)
    start = find_start(labels)
    words = find_words(lines, labels)
    code = find_code(lines, labels)

    return sort_code_by_index(start + words + code)


def main(source_filename: str, target_filename: str):
    source_loc, lines = read_asm(source_filename)
    code = translate(lines)
    write_code(target_filename, code)

    print(f"source LoC: {source_loc} code instr: {len(code)}")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source_filename, target_filename = sys.argv
    main(source_filename, target_filename)
