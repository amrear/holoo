import sys
import os

import ply.yacc as yacc
from anytree import Node, RenderTree
from tabulate import tabulate

from SyntaxTreeNode import STN
from SymbolTable import VariableSymbol, FunctionSymbol
from utils import *

import lex
tokens = lex.tokens

function_symbols = set()

precedence = (
    ('left', 'LOGICAL_OR'),
    ('left', 'LOGICAL_AND'),
    ('left', 'BITWISE_OR'),
    ('left', 'BITWISE_XOR'),
    ('left', 'BITWISE_AND'),
    ('nonassoc', 'EQUAL', 'NOT_EQUAL'),
    ('nonassoc', 'LESS', 'LESS_EQUAL', 'GREATER', 'GREATER_EQUAL'),
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'DIV', 'MOD'),
    ('right', 'BITWISE_NOT'),
    ('right', 'LOGICAL_NOT'),
    ('right', 'UMIN'),
)

def p_program(p):
    '''
    program : program_helper program_helper2
    '''

    p[0] = STN('program', children(p))


def p_program_helper(p):
    '''
    program_helper : field_dcl program_helper
                   | empty
    '''

    p[0] = helper(p)

def p_program_helper2(p):
    '''
    program_helper2 : func_dcl program_helper2
                    | func_dcl
    '''

    p[0] = helper(p)


def p_field_dcl(p):
    '''
    field_dcl : type field_dcl_cnt field_dcl_helper ';'
    '''

    p[0] = STN('field_dcl', children(p))


def p_field_dcl_helper(p):
    '''
    field_dcl_helper : ',' field_dcl_cnt
                     | empty
    '''

    p[0] = helper(p)

def p_field_dcl_cnt(p):
    '''
    field_dcl_cnt : id ';'
                  | id '[' int_const ']' ';'
    '''

    p[0] = STN('field_dcl_cnt', children(p))


def p_func_dcl(p):
    '''
    func_dcl : VOID id '(' ')' block
             | tuple id '(' ')' block
             | VOID id '(' type id func_dcl_helper ')' block
             | tuple id '(' type id func_dcl_helper ')' block
    '''

    if len(p) == 9:
        p = list(p)
        pro = p.pop(6)
        for i, x in enumerate(pro, start=6):
            p.insert(i, x)

    function_symbols.add(get_func_symbol(p))

    p[0] = STN('func_dcl', children(p))


def p_func_dcl_helper(p):
    '''
    func_dcl_helper : ',' type id func_dcl_helper
                    | empty
    '''

    p[0] = helper(p)


def p_tuple(p):
    '''
    tuple : '(' type tuple_helper ')'
          | type
    '''

    p[0] = STN('tuple', children(p))


def p_tuple_helper(p):
    '''
    tuple_helper : ',' type
                 | empty
    '''

    p[0] = helper(p)


def p_block(p):
    '''
    block : '{' block_helper block_helper2 '}'    
    '''

    p[0] = STN('block', children(p))


def p_block_helper(p):
    '''
    block_helper : var_dcl block_helper
                 | empty
    '''

    p[0] = helper(p)


def p_block_helper2(p):
    '''
    block_helper2 : statement block_helper2
                  | empty
    '''

    p[0] = helper(p)


def p_var_dcl(p):
    '''
    var_dcl : type var_dcl_cnt var_dcl_helper ';'
            | CONST type var_dcl_cnt var_dcl_helper ';'
    '''
    
    is_const = children(p)[0].value == 'const'
    variable_type = var_type(p)
    variable_ids = var_ids(p)

    for variable_id in variable_ids:
        sym = VariableSymbol(variable_type, variable_id, is_const)

    p[0] = STN('var_dcl', children(p), sym)


def p_var_dcl_helper(p):
    '''
    var_dcl_helper : ',' var_dcl_cnt var_dcl_helper
                   | empty
    '''

    p[0] = helper(p)


def p_var_dcl_cnt(p):
    '''
    var_dcl_cnt : id ASSIGN expr
                | id
    '''

    p[0] = STN('var_dcl_cnt', children(p))


def p_type(p):
    '''
    type : INT
         | BOOL
         | FLOAT
         | LONG
         | CHAR
         | DOUBLE
         | STRING
    '''

    p[0] = STN('type', children(p))


def p_statement(p):
    '''
    statement : assignment ';'
              | func_call ';'
              | cond_stmt ';'
              | loop_stmt ';'
              | RETURN return_helper ';'
              | RETURN expr return_helper ';'
              | expr ';'
              | BREAK ';'
              | CONTINUE ';'
              | SIZEOF '(' type ')' ';'
    '''

    p[0] = STN('statement', children(p))

def p_return_helper(p):
    '''
    return_helper : ',' expr return_helper
                  | empty
    '''

    p[0] = helper(p)

def p_assignment(p):
    '''
    assignment : variable ASSIGN expr
               | '(' id return_assignment ')' ASSIGN func_call
    '''

    p[0] = STN('assignment', children(p))


def p_return_assignment(p):
    '''
    return_assignment : ',' id return_assignment
                      | empty
    '''

    p[0] = helper(p)


def p_cond_stmt(p):
    '''
    cond_stmt : IF '(' expr ')' block
              | IF '(' expr ')' block ELSE block
              | SWITCH '(' id ')' '{' switch_helper DEFAULT ':' block '}'
    '''

    p[0] = STN('cond_stmt', children(p))


def p_switch_helper(p):
    '''
    switch_helper : CASE int_const ':' block  switch_helper
                  | empty
    '''

    p[0] = helper(p)


def p_loop_stmt(p):
    '''
    loop_stmt : FOR '(' ';' expr ';' expr ')' block
              | FOR '(' ';' expr ';' assignment ')' block
              | FOR '(' ';' expr ';' ')' block
              | FOR '(' var_dcl ';' expr ';' expr ')' block
              | FOR '(' var_dcl ';' expr ';' assignment ')' block
              | FOR '(' var_dcl ';' expr ';' ')' block
              | WHILE '(' expr ')' block
    '''

    p[0] = STN('loop_stmt', children(p))


def p_func_call(p):
    '''
    func_call : id '(' ')'
              | id '(' parameters ')'
    '''

    p[0] = STN('func_call', children(p))


def p_parameters(p):
    '''
    parameters : expr
               | expr ',' parameters 
    '''

    p[0] = STN('parameters', children(p))



def p_variable(p):
    '''
    variable : id indices_helper
             | id
             | INC variable
             | DEC variable
             | variable INC
             | variable DEC
    '''

    p[0] = STN('variable', children(p))


def p_indices_helper(p):
    '''
    indices_helper : '[' variable ']' indices_helper
                   | empty
    '''
    
    p[0] = helper(p)


def p_expr(p):
    '''
    expr : expr LOGICAL_AND expr
         | expr LOGICAL_OR expr
         | expr BITWISE_NOT expr
         | expr BITWISE_AND expr
         | expr BITWISE_OR expr
         | expr BITWISE_XOR expr
         | expr ADD expr
         | expr SUB expr
         | expr MUL expr
         | expr DIV expr
         | expr MOD expr
         | expr EQUAL expr
         | expr NOT_EQUAL expr
         | expr GREATER expr
         | expr LESS expr
         | expr GREATER_EQUAL expr
         | expr LESS_EQUAL expr
         | '(' expr ')'
         | func_call
         | variable
         | const_val
         | SUB expr %prec UMIN
         | LOGICAL_NOT expr
    '''

    p[0] = STN('expr', children(p))

def p_const_val(p):
    '''
    const_val : int_const
              | REAL_CONST
              | CHR_CONST
              | STR_CONST
              | TRUE
              | FALSE
    '''

    p[0] = STN('const_val', children(p))

def p_id(p):
    '''
    id : IDENTIFIER
    '''

    p[0] = STN('id', children(p))


def p_int_const(p):
    '''
    int_const : dec_const
              | hex_const
              | oct_const
              | long_const
    '''

    p[0] = STN('int_const', children(p))


def p_dec_const(p):
    '''
    dec_const : DEC_CONST
    '''

    p[0] = STN('dec_const', children(p))

def p_hex_const(p):
    '''
    hex_const : HEX_CONST
    '''

    p[0] = STN('hex_const', children(p))

def p_oct_const(p):
    '''
    oct_const : OCT_CONST
    '''

    p[0] = STN('oct_const', children(p))

def p_long_const(p):
    '''
    long_const : LONG_CONST
    '''

    p[0] = STN('long_const', children(p))

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    print(f"Syntax error.")
    if p is not None:
        print(f"in line {p.lineno} token {p.value}.")
    sys.exit(1)

input_file = sys.argv[1]

with open(f'input/{input_file}') as f:
    inp = f.read()

parser = yacc.yacc()
parsed = parser.parse(inp)
tree = build_tree(parsed, None)

lex.lex.input(inp)

with open(f'output/{os.path.splitext(input_file)[0]}.tokens', 'w', encoding='utf-8') as f:
    while True:
        t = lex.lex.token()
        if not t:
            break

        punc = {'(', ')', '[', ']', '{', '}', '.', ',', ':', ';'}
        if t.type in punc:
            t.type = 'PUNCTUATION'

        print(f"<'{t.value}', {t.type}>", file=f)


with open(f'output/{os.path.splitext(input_file)[0]}.syntree', 'w', encoding='utf-8') as f:
    for pre, fill, node in RenderTree(tree):
        print("%s%s" % (pre, node.name), file=f)


function_symbols_table = []
variable_symbols_table = []

for fs in function_symbols:
    function_symbols_table.append([fs.return_type, fs.name, fs.arguments])
    for v in fs.variables:
        if v.name in [x[2] for x in variable_symbols_table]:
            sys.exit(f"Variable {v.name} has been declared at least twice.")

        variable_symbols_table.append([v.is_const, v.type, v.name, fs.name])

if not "here" in [x[1] for x in function_symbols_table]:
    sys.exit("function here was not found in the source code.")
else:
    i = [x[1] for x in function_symbols_table].index("here")
    if function_symbols_table[i][0] != "void":
        sys.exit("the return type of here must be void.")
    elif function_symbols_table[i][2]:
        sys.exit("here does not take any arguments.")

with open(f'output/{os.path.splitext(input_file)[0]}.symtab', 'w', encoding='utf-8') as f:
    print("FUNCTIONS: ", file=f)
    print(tabulate(function_symbols_table, headers=["return_type", "name", "arguments"], tablefmt="simple_grid"), file=f)

    print("\n", file=f)

    print("VARIABLES: ", file=f)
    print(tabulate(variable_symbols_table, headers=["is_const", "type", "name", "in_function"], tablefmt="simple_grid"), file=f)
