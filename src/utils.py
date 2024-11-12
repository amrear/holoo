from anytree import Node, RenderTree

from SyntaxTreeNode import STN
from SymbolTable import VariableSymbol, FunctionSymbol

def flatten(x):
    if isinstance(x, list):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]
    
def build_tree(child, parent):
    if not isinstance(child, STN):
        return 
       
    p = Node(child, parent)

    for c in child.children:
        build_tree(c, p)

    return p

def children(p):
    tmp = []
    for t in p[1:]:
        if isinstance(t, STN):
            tmp.append(t)
        elif isinstance(t, list):
            tmp += t
        else:
            tmp.append(STN(t))

    return tmp

def helper(p):
    return [t if isinstance(t, STN) else STN(t) for t in flatten(p[1:]) if t]

def var_type(p):
    if children(p)[0].value == 'const':
        return children(p)[1].children[0].value
    else:
        return children(p)[0].children[0].value
    
def var_ids(p):
    res = []
    for ch in children(p):
        if ch.value == 'var_dcl_cnt':
            for chh in ch.children:
                if chh.value == 'id':
                    res.append(chh.children[0].value)

    return res
    
def get_func_symbol(p):
    return_type = get_return_type(p)
    function_id = get_func_id(p)
    function_arguments = get_func_args(p)

    variables = set()

    for fa in function_arguments:
        variables.add(VariableSymbol(fa[0], fa[1], False))

    for c in list(p)[-1].children:
        if c.value == 'var_dcl':
            variables.add(c.variable_symbol)
    
    return FunctionSymbol(return_type, function_id, function_arguments, variables)

def get_return_type(p):
    if p[1] == "void":
        return "void"
    elif len(p[1].children) == 1:
        return p[1].children[0].children[0].value
    else:
        p = p[1].children[1:-1]
        return [x.children[0].value for x in p if x.value != ',']
    

def get_func_id(p):
    return (p[2].children[0].value)

def get_func_args(p):
    if len(p) != 6:
        args = p[4:-2]
        return [(args[i].children[0].value, args[i+1].children[0].value)for i in range(0, len(args), 3)]
    else:
        return list()

