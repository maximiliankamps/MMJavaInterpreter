from Parser import Stack
binop = {"plus", "minus", "div", "mul"}
binop_map = {"plus": "iadd", "minus": "isub", "div": "idiv", "mul": "imul"}

cmp = {"d_equal", "greater_equal"}
cmp_map = {"d_equal": "icmpe", "greater_equal": "icmpge"}


class INTERPRETER:
    def __init__(self, ast_root):
        self.local_var_table = {}
        self.create_local_var_table(ast_root.get_child(1))
        self.bseq = []
        self.label_table = []  # contains addresses for labels
        self.create_bytecode_seq(ast_root.get_child(0))
        self.stack = Stack([])
        self.bseq_ptr = -1
        self.p_ctr = 0

    # ast_node must be DECL top node
    def create_local_var_table(self, ast_node):
        for child in ast_node.get_children():
            if child.get_ttype() == "decl":
                self.create_local_var_table(child)
            else:
                self.local_var_table[child.get_value()] = 0

    def print_local_var_table(self):
        print("_____________________")
        print("Local variable table:")
        for k in self.local_var_table.keys():
            print("Name:", k, "| Value:", self.local_var_table[k])
        print("_____________________")

    def print_label_table(self):
        print(self.label_table)

    # ast_node must be STMT top node
    # very confusion if and while translation
    def create_bytecode_seq(self, ast_node):
        if ast_node is None:
            return
        if ast_node.get_ttype() == "assign":
            self.create_bytecode_seq(ast_node.get_child(0))
            self.bseq.append(("istore", ast_node.get_child(1).get_value()))
        elif ast_node.get_ttype() in binop:
            self.create_bytecode_seq(ast_node.get_child(1))
            self.create_bytecode_seq(ast_node.get_child(0))
            self.bseq.append(binop_map[ast_node.get_ttype()])
        elif ast_node.get_ttype() == "print":
            self.create_bytecode_seq(ast_node.get_child(0))
            self.bseq.append("print")
        elif ast_node.get_ttype() == "number":
            self.bseq.append(("iconst", ast_node.get_value()))
        elif ast_node.get_ttype() == "name":
            self.bseq.append(("iload", ast_node.get_value()))
        elif ast_node.get_ttype() == "while":
            next_block = None
            loop_label = len(self.label_table)  # Index of loop label in label table
            self.label_table.append(len(self.bseq))  # Address to which goto should jmp in bseq
            end_label = len(self.label_table)  # Index of end label in label table
            # Address to which failed cmp should jmp in bseq, will be set after evaluating loop body
            self.label_table.append(-1)
            self.create_bytecode_seq(ast_node.get_child(1))  # Add cmp arguments to bseq
            # Add cmp type with label to stack
            self.bseq.append((cmp_map[ast_node.get_child(1).get_ttype()], end_label))
            if len(ast_node.get_child(0).get_children()) > 1:
                body_child = ast_node.get_child(0).get_child(1)
                next_block = ast_node.get_child(0).get_child(0)  # recurse on block after while
                self.create_bytecode_seq(body_child)  # Add loop body to stack
            else:
                self.create_bytecode_seq(ast_node.get_child(0))  # Add loop body to stack
            self.bseq.append(("goto", loop_label))
            self.label_table[end_label] = len(self.bseq)  # Set the loop label
            if next_block is not None:
                self.create_bytecode_seq(next_block)
        elif ast_node.get_ttype() == "if":
            child_len = len(ast_node.get_children())
            next_block_label = len(self.label_table)
            self.label_table.append(-1)

            self.create_bytecode_seq(ast_node.get_child(child_len-1))  # Add cmp arguments to bseq
            self.bseq.append((cmp_map[ast_node.get_child(child_len-1).get_ttype()], next_block_label))  #  add cmp to bseq
            self.create_bytecode_seq(ast_node.get_child(child_len-2))  # add if block to bseq

            if ast_node.get_child(0).get_ttype() == "else":
                else_node = ast_node.get_child(0)
                else_child_len = len(else_node.get_children())

                skip_else_label = len(self.label_table)
                self.bseq.append(("goto", skip_else_label))  # after executing if block skip else block
                self.label_table.append(-1)

                self.label_table[next_block_label] = len(self.bseq)  # if else cond fails, jmp to else block
                self.create_bytecode_seq(else_node.get_child(else_child_len - 1))  # add else block to bseq

                if else_child_len == 2:  # if there is a block after else block add it to bseq
                    self.create_bytecode_seq(else_node.get_child(else_child_len - 2))

                self.label_table[skip_else_label] = len(self.bseq)
            else:  # there is no else block
                self.label_table[next_block_label] = len(self.bseq)
                if len(ast_node.get_children()) == 3:  # there is a block after the if statement
                    self.create_bytecode_seq(ast_node.get_child(0))  # add block to bseq


        else:
            for child in reversed(ast_node.get_children()):
                self.create_bytecode_seq(child)

    def print_bytecode_seq(self):
        for i, b in enumerate(self.bseq):
            print(i, ":", b)

    def execute_bytecode(self):
        while self.p_ctr < len(self.bseq):
            cmd = self.bseq[self.p_ctr]

            if cmd == "iadd":
                self.iadd()
            elif cmd == "isub":
                self.isub()
            elif cmd == "imul":
                self.imul()
            elif cmd == "idiv":
                self.idiv()
            elif cmd == "print":
                self.print()
            elif cmd[0] == "iconst":
                self.iconst(cmd[1])
            elif cmd[0] == "iload":
                self.iload(cmd[1])
            elif cmd[0] == "istore":
                self.istore(cmd[1])
            elif cmd[0] == "goto":
                self.goto(cmd[1])
                continue
            elif cmd[0] == "icmpe":
                self.icmpe(cmd[1])
                continue
            elif cmd[0] == "icmpge":
                self.icmpge(cmd[1])
                continue
            self.p_ctr = self.p_ctr + 1

        self.p_ctr = 0
        for key in self.local_var_table.keys():
            self.local_var_table[key] = 0
        print("exit 0")

    def iconst(self, v):
        self.stack.push(v)

    def istore(self, x):
        self.local_var_table[x] = self.stack.pop()

    def iload(self, x):
        self.stack.push(self.local_var_table[x])

    def print(self):
        print("<print>", self.stack.pop())

    def goto(self, addr):
        self.p_ctr = self.label_table[int(addr)]

    def icmpe(self, addr):
        a = int(self.stack.pop())
        b = int(self.stack.pop())
        if a != b:
            self.p_ctr = self.label_table[int(addr)]
        else:
            self.p_ctr = self.p_ctr + 1

    def icmpge(self, addr):
        a = int(self.stack.pop())
        b = int(self.stack.pop())
        if a > b:
            self.p_ctr = self.label_table[int(addr)]
        else:
            self.p_ctr = self.p_ctr + 1


    def iadd(self):
        self.stack.push(int(self.stack.pop()) + int(self.stack.pop()))

    def isub(self):
        b = int(self.stack.pop())
        a = int(self.stack.pop())
        self.stack.push(a - b)

    def imul(self):
        self.stack.push(int(self.stack.pop()) * int(self.stack.pop()))

    def idiv(self):
        b = int(self.stack.pop())
        a = int(self.stack.pop())
        self.stack.push(int(a / b))













