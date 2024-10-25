def bind_children(parent, child_list):
    for child in child_list:
        child.set_parent(parent)
        parent.add_child(child)


class AST_NODE:
    def __init__(self, token):
        self.token = token
        self.children = []
        self.parent = None

    def to_string(self):
        return self.token.to_string()

    def get_token(self):
        return self.token

    def set_token(self, t):
        self.token = t

    def get_ttype(self):
        return self.token.get_ttype()

    def get_value(self):
        return self.token.get_value()

    def set_parent(self, p):
        self.parent = p

    def get_parent(self):
        return self.parent

    def add_child(self, c):
        self.children.append(c)

    def replace_child(self, old, new):
        i = self.children.index(old)
        self.children[i] = new

    def remove_child(self, child):
        i = self.children.remove(child)

    def get_children(self):
        return self.children

    def get_child(self, pos):
        return self.children[pos]

