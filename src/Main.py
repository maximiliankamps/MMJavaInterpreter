import re

from Lexer import tokenize_program_str
from Parser import token_str_to_ast
from Parser import parse_error
from PDA_render import render_ast
from Interpreter import *

p0 = "a, b;" \
     "while (3 >= a) {" \
     "  a = a + 1;" \
     "  print(a);" \
     "}" \
     ""

p1 = "a;" \
     "if (a == 3) {" \
     "  print(b);" \
     "}" \
     "print(c);"

p2 = "a;" \
     "if (a == 3) {" \
     "  print(b);" \
     "} else {" \
     "  a = 7 / 4;" \
     "}"
p3 = "a;" \
     "if (a == 3) {" \
     "  print(b);" \
     "}"

pfac = "a, b;" \
       "a = 1;" \
       "while (5 >= b) {" \
       "    b = b + 1;" \
       "    a = a * b;" \
       "    print(a);" \
       "}"
pmin = "a;" \
       "a = 4;" \
       "a = 2 / a;" \
       "print(a);"

help_str = """+ print help: -help
+ exit interpreter: exit
+ load program: load [program name] 
+ execute program: execute 
+ render ast: render_ast
+ render bytecode sequence: print_bseq"""


def print_prog_not_found_str(cmd):
    print(f"No program found, please load a program before using {cmd}")


new_line_chars = {";", "{", "}"}


def print_parse_error(token_l, pos):
    offset = 0
    for i, token in enumerate(token_l):
        cut_of = len(token.get_value()) - 1
        if i == pos:
            print(token.get_value()[:cut_of], " <----- Syntax Error")
            print(" " * offset + "^" * len(token.get_value()))
            break
        if token.get_value() in new_line_chars:
            print(token.get_value())
            offset = 0
        else:
            print(token.get_value(), end='')
            offset = offset + len(token.get_value())


if __name__ == '__main__':
    program_name = None
    program_str = None
    program_ast = None
    interpreter = None

    print("/-----------------------/")
    print("MiniMini-Java-Interpreter")
    print("  Enter -help for help   ")
    print("/-----------------------/")

    while True:
        user_input = re.split("\s+", input("(interp): "))
        cmd = user_input[0]

        if cmd == "help":
            print(help_str)
        elif cmd == "exit":
            break
        elif cmd == "execute":
            if interpreter is None:
                print_prog_not_found_str("execute")
            else:
                interpreter.execute_bytecode()
        elif cmd == "render_ast":
            if interpreter is None:
                print_prog_not_found_str("render_ast")
            else:
                render_ast(program_ast, f"{program_name}_ast")
        elif cmd == "print_bseq":
            if interpreter is None:
                print_prog_not_found_str("print_bseq")
            else:
                interpreter.print_local_var_table()
                interpreter.print_bytecode_seq()
                interpreter.print_label_table()
        elif cmd == "load":
            program_name = user_input[1]
            try:
                file = open(program_name, "r")
            except FileNotFoundError:
                print(f"File with name '{program_name}' not found")
                continue

            program_str = file.read()

            token_list = tokenize_program_str(program_str)
            try:
                program_ast = token_str_to_ast(token_list)
            except Exception:
                print_parse_error(token_list, parse_error.position)
                continue
            interpreter = INTERPRETER(program_ast)
            print(f"Program '{program_name}' successfully loaded")
        else:
            print("Command not found!")
