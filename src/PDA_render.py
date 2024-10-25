import graphviz as gviz


def render_pda(pda, filename):
    g = gviz.Digraph('G', filename=f'{filename}')

    for q in pda.Q:
        g.node(q.name_str(), q.to_string(), shape="circle")
        if q == pda.q0:
            g.node(q.name_str(), q.to_string(), style="filled")
        if q in pda.F:
            g.node(q.name_str(), q.to_string(), shape="doublecircle")
    for t in pda.trans:
        g.edge(t[0].name_str(), t[2].name_str(), t[1])

    g.view()

def render_ast(ast_root, filename):
    g = gviz.Digraph('G', filename=f'{filename}')

    W = [ast_root]

    while W:
        node = W.pop()
        if node.get_children():
            g.node(str(node), node.to_string(), shape="box")
        else:
            g.node(str(node), node.to_string(), shape="box", style="filled")
        W.extend(node.get_children())
        if node.get_parent() is not None:
            g.edge(str(node.get_parent()), str(node), None)
    g.view()




