from Lexer import Token
from SyntaxTree import *
from PDA_render import render_pda
from PDA_render import render_ast

# A production has the following structure name: l_symbol -> [r_symbols]
class Prod_Rule:
    def __init__(self, name, l_symbol, r_symbols):
        self.name = name
        self.l_symbol = l_symbol
        self.r_symbols = r_symbols

    # returns the symbol at pos in r_symbols
    # returns None if the Symbol is out of bounds
    def return_sym(self, pos):
        if pos >= len(self.r_symbols):
            return None
        return self.r_symbols[pos]

    # cmp if 2 productions are the same, here only the names are compared (as they are unique)
    def cmp_prod_rule(self, p2):
        return self.name == p2.name

    # creates a string out of the production, pos indicates at which position the "•" should be places
    def to_string(self, pos):
        r_sym_str = ""
        end = False
        if pos >= len(self.r_symbols):
            end = True
        for i, sym in enumerate(self.r_symbols):
            if i == pos and not end:
                r_sym_str += "• "
            r_sym_str += sym + " "
        if end:
            r_sym_str += "• "
        return self.l_symbol + " -> " + r_sym_str

    def print(self, pos):
        print(self.to_string(pos))


# A state consists of:
# - name
# - Set of productions and the position in the production
# - A shift reduce rule, if the State is a reduced state, else the parameter stays None
class State:
    def __init__(self, name, prod_pos_set):
        self.name = name
        self.prod_pos_set = prod_pos_set
        self.rule = None

    # Compares 2 states -> States are equal if they have the same production_position_set
    def cmp_states(self, prod_pos_set2):
        if len(self.prod_pos_set) != len(prod_pos_set2):  # If the 2 sets have different length they cannot be equal
            return False

        # Check if for every (production,pos) in the first set, if their exists a (production,pos)' in the second set
        for pp in self.prod_pos_set:
            found = False  # Break out of the loop if a corresponding element has been found
            for pp2 in prod_pos_set2:
                if pp[0].cmp_prod_rule(pp2[0]) and pp[1] == pp2[1]:  # Compare elements
                    found = True
                    break
            if not found:
                return False
        return True

    # Returns the name of the state as a str (name is an int)
    def name_str(self):
        return str(self.name)

    # Returns a string of the state
    def to_string(self):
        tmp = ""
        tmp += "State: " + str(self.name) + "\n"
        for pp in self.prod_pos_set:
            tmp += pp[0].to_string(pp[1]) + "\n"
        if self.rule is not None:
            tmp += "red: " + str(self.rule.name)
        return tmp

    def print(self):
        print(self.to_string())

    # Finds all the productions in prod_pos_set for which sym is equal to the element at the current position
    # Return these productions and increments pos
    # Is used in the function create pda to find all the productions for the next state (that can be reached with sym)
    def next_prod_pos_set(self, sym):
        tmp = set()
        for pp in self.prod_pos_set:
            if pp[0].return_sym(pp[1]) == sym:
                tmp.add((pp[0], pp[1] + 1))
        return tmp


# Class to encapsulate a Context Free Grammar
# Is used to create the PDA
class CFG:
    def __init__(self, non_terminals, terminals, final, productions):
        self.non_terminals = non_terminals  # Set of non-terminals
        self.terminals = terminals  # Set of terminals
        self.final = final  # Final non-terminal
        self.productions = productions  # Set of all productions of the grammar

    def get_prod(self, name):
        p = None
        for p in self.productions:
            if p.name == name:
                break
        return p


# Class for a Push Down Automata that is used to create the parsing table
class PDA:
    def __init__(self, q0, Q, F, trans, cfg):
        self.q0 = q0
        self.Q = Q
        self.F = F
        self.trans = trans
        self.cfg = cfg


# Finds all productions in the cfg, for which a (production,position) pair in the set pp exists,
# where at the current position the symbol is a non-terminal
def non_term_rule(pp_set, cfg):
    prod_pos_tmp = set()
    for prod_pos in pp_set:
        sym = prod_pos[0].return_sym(prod_pos[1])
        if sym in cfg.non_terminals:
            for prod in cfg.productions:
                if prod.l_symbol == sym:
                    prod_pos_tmp.add((prod, 0))
    return prod_pos_tmp


def print_prod_pos_set(pp_set):
    for pp in pp_set:
        pp[0].print(pp[1])


# Creates the push down automata
def create_pda(cfg, start_prod):
    i = 1
    start_pp_set = {(start_prod, 0)}
    start_prod_pos_set = start_pp_set.union(non_term_rule(start_pp_set, cfg))
    q0 = State(i, start_prod_pos_set)  # Create the initial state
    i += 1
    W = {q0}  # Initialize the work set
    Q = set()
    F = set()
    trans = set()

    while W != set():
        q = W.pop()  # get the next state from
        Q.add(q)
        for sym in cfg.non_terminals.union(cfg.terminals):  # Iterate over symbols
            if len(q.prod_pos_set) == 1:  # If prod_pos has length == 1 then state might be final
                pp = q.prod_pos_set.pop()
                q.prod_pos_set.add(pp)
                # state is final if the cursor is outside of production and the last symbol is the final symbol
                if len(pp[0].r_symbols) == pp[1] and pp[0].return_sym(pp[1] - 1) == cfg.final:
                    F.add(q)
                    break  # break out of symbol-loop, state is done processing
            if len(q.prod_pos_set) >= 1:  # If prod_pos has length >= 1 then the state might have a reduction rule
                pp = q.prod_pos_set.pop()
                q.prod_pos_set.add(pp)
                if pp[0].return_sym(pp[1]) is None:  # In some production the cursor is outside -> The symbol has a rule
                    q.rule = pp[0]

            # Create next set of productions
            cur_prod_pos_set = q.next_prod_pos_set(sym)

            # Apply non term rule recursive until all reachable productions have been added to cur_prod_pos_set
            tmp = State(-1, set())
            while not tmp.cmp_states(cur_prod_pos_set):
                tmp.prod_pos_set = cur_prod_pos_set
                cur_prod_pos_set = cur_prod_pos_set.union(non_term_rule(cur_prod_pos_set, cfg))

            if cur_prod_pos_set != set():  # If the set isn't empty create a new transition
                q_ = None
                for tmp in W.union(Q):  # Check if state with current prod_pos exists
                    if tmp.cmp_states(cur_prod_pos_set):
                        q_ = tmp
                        break
                if q_ is None:  # state does not exist -> Add new state
                    q_ = State(i, cur_prod_pos_set)
                    i += 1
                    W.add(q_)
                trans.add((q, sym, q_))  # Add new transition between the old and the new state
    return PDA(q0, Q, F, trans, cfg)


# Creates the parsing table out of the pda
# Entries can be accessed via table[state q][symbol] = (state p, type)
# Types:
# - Nothing = 0
# - Shift = 1
# - Reduce = 2      (state p is the name of the reduction rule in this case)
# - Accepted = 3    (state p is -1 in this case)
def create_parsing_table(pda):
    table = {}
    non_terminal = pda.cfg.non_terminals
    terminal = pda.cfg.terminals
    final_terminal = pda.cfg.final

    for q in pda.Q:  # initialize table with all states
        table[q.name] = {}

    for (q, a, p) in pda.trans:  # add all non-terminal and shift entries and final entry
        if a in non_terminal:
            table[q.name][a] = (0, p.name)
        elif a == final_terminal:
            table[q.name][final_terminal] = (3, -1)
        else:
            table[q.name][a] = (1, p.name)

    for q in pda.Q:  # add al reduction and accepting entries
        if q.rule is not None:
            res = table[q.name].keys()
            for t in terminal:
                if t not in res:
                    table[q.name][t] = (2, q.rule.name)
    return table


def print_parsing_table(table):
    etype = {0: "None", 1: "Shift", 2: "Reduce", 3: "Final"}
    for q in table.keys():
        for a in table[q].keys():
            print("[State:", q, "Symbol:", a, etype[table[q][a][0]], table[q][a][1], end="]  ||  ")
        print("")


def get_t_entry(table, st, a):
    return table[st][a]


class Stack:
    def __init__(self, li):
        self.list = li.copy()
        self.list.reverse()

    def stack_len(self):
        return len(self.list)

    def print(self):
        stri = ""
        for elem in self.list:
            stri += elem.to_string()
        return stri

    def to_string(self):
        return self.list

    def push(self, elem):
        self.list.append(elem)

    def set_last(self, elem):
        self.list[len(self.list) - 1] = elem

    def pop(self):
        return self.list.pop()

    def peek(self):
        return self.list[len(self.list) - 1]

    def empty(self):
        return len(self.list) == 0


class Parse_Error:
    position = None


parse_error = Parse_Error


# Returns the root node of the AST tree of word
def parse_word(table, word, cfg):
    state_stack = Stack([1])
    # Stack consists of AST nodes
    symbol_stack = Stack([])
    # Stack consists of Tokens
    word_stack = Stack(word)

    token_str_len = word_stack.stack_len()

    while not word_stack.empty() or not symbol_stack.empty():
        parse_error.position = token_str_len - word_stack.stack_len()
        # print(state_stack.to_string())
        # print(symbol_stack.print(), end=" // ")
        # print(word_stack.print())
        # print("------------------")

        if state_stack.peek() is None:
            state_stack.pop()
            (ptype, st) = get_t_entry(table, state_stack.peek(), symbol_stack.peek().get_ttype())
        else:
            (ptype, st) = get_t_entry(table, state_stack.peek(), word_stack.peek().get_ttype())

        if ptype == 0:
            state_stack.push(st)
        elif ptype == 1:  # shift
            s = word_stack.pop()
            new_node = AST_NODE(s)
            symbol_stack.push(new_node)
            state_stack.push(st)
        elif ptype == 2:  # reduce
            p = cfg.get_prod(st)
            new_node = AST_NODE(Token(p.l_symbol, p.l_symbol))  # create new parent node
            for i in range(len(p.r_symbols)):  # add child nodes to the new parent node
                child_node = symbol_stack.pop()
                child_node.set_parent(new_node)
                new_node.add_child(child_node)
                state_stack.pop()
            symbol_stack.push(new_node)
            state_stack.push(None)
        elif ptype == 3:  # final
            root = AST_NODE(Token("PROG", "PROG"))  # Add the Prog root node
            while not symbol_stack.empty():
                child_node = symbol_stack.pop()
                child_node.set_parent(root)
                root.add_child(child_node)
            return root
    return None


term = {"plus", "minus", "mul", "div", "name", "d_equal", "greater_equal", "number"}
non_term = {"STMT", "EXPR", "BINOP", "COMP"}
remove_symbol = {"{", "}", "(", ")", ",", ";"}


# helper function for simplify ast, finds all alternatives for while and if
def find_alternatives(ast_node):
    children_rev = list(reversed(ast_node.get_children()))
    result = []
    for child in children_rev:
        if child.get_ttype() == "STMT":
            result.append(simplify_ast(child))
    return result


# simplifies the ast, for the interpreter
def simplify_ast(ast_node):
    children_rev = list(reversed(ast_node.get_children()))
    local_root = None

    if ast_node.get_ttype() == "COND":
        op = simplify_ast(children_rev[1])
        local_root = AST_NODE(Token(op.get_ttype(), op.get_value()))
        exp1 = simplify_ast(children_rev[0])
        exp2 = simplify_ast(children_rev[2])
        bind_children(local_root, [exp2, exp1])
        return local_root

    for i, child in enumerate(children_rev):
        if child.get_ttype() == "name" and child.get_parent().get_ttype() == "STMT":
            local_root = AST_NODE(Token("assign", "assign"))
            expr = simplify_ast(children_rev[i + 2])
            name = simplify_ast(child)
            bind_children(local_root, [expr, name])
            return local_root
        if child.get_ttype() == "while":
            local_root = AST_NODE(Token("while", "while"))
            predicate = simplify_ast(children_rev[i + 2])
            body = simplify_ast(children_rev[i + 4])
            bind_children(local_root, [body, predicate])
            return local_root
        if child.get_ttype() == "if":
            local_root = AST_NODE(Token("if", "if"))
            predicate = simplify_ast(children_rev[i + 2])
            if len(children_rev) == 7:  # if else statement
                if_child = simplify_ast(children_rev[4])
                else_children = find_alternatives(children_rev[6])
                else_children.reverse()
                else_node = AST_NODE(Token("else", "else"))
                bind_children(else_node, else_children)
                bind_children(local_root, [else_node, if_child, predicate])
            else:
                alternative_list = find_alternatives(children_rev[i + 4])
                alternative_list.reverse()
                alternative_list.append(predicate)
                bind_children(local_root, alternative_list)
            return local_root
        if child.get_ttype() == "BINOP":
            op = simplify_ast(children_rev[i])
            local_root = AST_NODE(Token(op.get_ttype(), op.get_value()))
            num1 = simplify_ast(children_rev[i + 1])
            num2 = simplify_ast(children_rev[i - 1])
            bind_children(local_root, [num1, num2])
            return local_root
        if child.get_ttype() == "print":
            local_root = AST_NODE(Token("print", "print"))
            expr = simplify_ast(children_rev[i + 2])
            bind_children(local_root, [expr])
            return local_root
        if child.get_ttype() in term and ast_node.get_ttype() != "decl":
            return child
        if child.get_ttype() in non_term:
            ast_node.set_token(Token("block", "block"))
            new_child = simplify_ast(child)
            new_child.set_parent(ast_node)
            ast_node.replace_child(child, new_child)
        if child.get_value() in remove_symbol:
            ast_node.remove_child(child)
        if child.get_ttype() == "DECL":
            child.set_token(Token("decl", "decl"))
            simplify_ast(child)
    return ast_node


r0 = Prod_Rule(0, "PROG", ["DECL", "STMT", "$"])

r1 = Prod_Rule(1, "BINOP", ["plus"])
r2 = Prod_Rule(2, "BINOP", ["minus"])
r3 = Prod_Rule(3, "BINOP", ["div"])
r4 = Prod_Rule(4, "BINOP", ["mul"])

r5 = Prod_Rule(5, "DECL", ["name", "comma", "DECL"])
r6 = Prod_Rule(6, "DECL", ["name", "semicolon"])

r7 = Prod_Rule(7, "EXPR", ["number"])
r8 = Prod_Rule(8, "EXPR", ["name"])
r9 = Prod_Rule(9, "EXPR", ["EXPR", "BINOP", "EXPR"])
r10 = Prod_Rule(10, "EXPR", ["lparen", "EXPR", "rparen"])

r11 = Prod_Rule(11, "STMT", ["STMT", "STMT"])
r12 = Prod_Rule(12, "STMT", ["name", "equal", "EXPR", "semicolon"])
r13 = Prod_Rule(13, "STMT", ["print", "lparen", "EXPR", "rparen", "semicolon"])

r14 = Prod_Rule(14, "STMT", ["while", "lparen", "COND", "rparen", "STMT"])
r15 = Prod_Rule(15, "STMT", ["if", "lparen", "COND", "rparen", "STMT"])
r16 = Prod_Rule(16, "STMT", ["if", "lparen", "COND", "rparen", "STMT", "else", "STMT"])
r17 = Prod_Rule(17, "STMT", ["lbrace", "STMT", "rbrace"])

r18 = Prod_Rule(18, "COND", ["lparen", "COND", "rparen"])
r19 = Prod_Rule(19, "COND", ["EXPR", "COMP", "EXPR"])

r20 = Prod_Rule(20, "COMP", ["d_equal"])
r21 = Prod_Rule(21, "COMP", ["greater_equal"])

cfg = CFG({"PROG", "BINOP", "DECL", "STMT", "EXPR", "REC_DECL", "COND", "COMP"},
          {"number", "semicolon", "plus", "minus", "div", "mul", "$", "print", "while",
           "lparen", "rparen", "equal", "greater_equal", "name", "comma", "if", "else", "lbrace", "rbrace", "d_equal",
           },
          "$",
          {r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19, r20, r21})


def token_str_to_ast(token_str):
    pda = create_pda(cfg, r0)
    table = create_parsing_table(pda)
    # render_pda(pda, "pda")
    ast = parse_word(table, token_str, cfg)
    ast = simplify_ast(ast)
    return ast
