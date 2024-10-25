import re

symbols = ["==", "=", ">=", ";", "\(", "\)", "\{", "\}", "\+", "-", "/", "\*", "print", "if", "while",
           "else", "[a-z,A-Z]", "[1-9][0-9]*|0", '".+"', ","]            #  check how numbers are handled
token_types = {"=": "equal", "==": "d_equal", ">=": "greater_equal", ";": "semicolon",
               "(": "lparen", ")": "rparen", "{": "lbrace", "}": "rbrace",
               "+": "plus", "-": "minus", "*": "mul", "/": "div",
               "print": "print", "if": "if", "else": "else", ",": "comma", "while": "while"}


class Token:
    def __init__(self, ttype, value):
        self.ttype = ttype
        self.value = value

    def to_string(self):
        return "[" + self.ttype + ": '" + self.value + "']"

    def get_ttype(self):
        return self.ttype

    def get_value(self):
        return self.value

    def print(self):
        print(self.to_string())


# Creates regex string for function tokenize_program_str out of symbols
def create_regex():
    str = ""
    for s in symbols:
        str += s + "|"
    return str[:-1]


# Transforms the program into a list of tokens
def tokenize_program_str(program_str):
    symbol_list = re.findall(create_regex(), program_str)  # Get symbols
    token_list = []
    for symbol in symbol_list:  # Classify symbols
        if token_types.get(symbol) is None:
            # Classify dynamic symbols (e.g: 12 -> NUMBER: 12)
            if re.search("[0-9]", symbol):  # is symbol number?
                token_list.append(Token("number", symbol))
            elif re.search('"', symbol):  # is symbol string?
                token_list.append(Token("string", symbol))
            else:  # Symbol is name
                token_list.append(Token("name", symbol))
        else:
            token_list.append(Token(token_types[symbol], symbol))  # Assign symbol to token out of token types
    token_list.append(Token("$", "$"))
    return token_list


program_0 = 'a = 300; ' \
            'if (a >= 0) {' \
            '   print "a is big!";' \
            '}' \
            'else {' \
            'print a;' \
            '}'

if __name__ == '__main__':
    tokenize_program_str(program_0)



