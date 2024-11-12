import ply.lex as lex
from ply.lex import TOKEN

tokens = [
    'REAL_CONST',
    'HEX_CONST',
    'OCT_CONST',
    'DEC_CONST',
    'LONG_CONST',
    'CHR_CONST',
    'STR_CONST',
    'IDENTIFIER',
    'EQUAL',
    'NOT_EQUAL',
    'GREATER',
    'GREATER_EQUAL',
    'LESS',
    'LESS_EQUAL',
    'ASSIGN',
    'LOGICAL_NOT',
    'LOGICAL_AND',
    'LOGICAL_OR',
    'BITWISE_NOT',
    'BITWISE_AND',
    'BITWISE_OR',
    'BITWISE_XOR',
    'ADD',
    'SUB',
    'MUL',
    'DIV',
    'MOD',
    'INC',
    'DEC',
]

reserved = {
    'bool': 'BOOL',
    'break': 'BREAK',
    'case': 'CASE',
    'char': 'CHAR',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'double': 'DOUBLE',
    'else': 'ELSE',
    'false': 'FALSE',
    'function': 'FUNCTION',
    'float': 'FLOAT',
    'for': 'FOR',
    'if': 'IF',
    'int': 'INT',
    'long': 'LONG',
    'return': 'RETURN',
    'sizeof': 'SIZEOF',
    'string': 'STRING',
    'switch': 'SWITCH',
    'true': 'TRUE',
    'void': 'VOID',
    'while': 'WHILE'
}

tokens += list(reserved.values())

t_ASSIGN = r'='

t_EQUAL = r'=='
t_NOT_EQUAL = r'!='
t_GREATER = r'>'
t_GREATER_EQUAL = r'>='
t_LESS = r'<'
t_LESS_EQUAL = r'<='

t_LOGICAL_NOT = r'!'
t_LOGICAL_AND = r'&&'
t_LOGICAL_OR = r'\|\|'

t_BITWISE_NOT = r'~'
t_BITWISE_AND = r'&'
t_BITWISE_OR = r'\|'
t_BITWISE_XOR = r'\^'

t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_DIV = r'/'
t_MOD = r'%'

t_INC = r'\+\+'
t_DEC = r'--'

literals = ['(', ')', '{', '}', '[', ']', '.', ',', ':', ';']

t_ignore = ' \t'
t_ignore_COMMENT = r'(@@.*)|(/@(.|\n)*@/)'


REAL1 = r'([+-]?\d+\.\d+)'
REAL2 = r'([+-]?\d+\.)'
REAL3 = r'(\.[+-]?\d+)'
REAL4 = r'([+-]?\d+(e|E)[+-]?\d)'
REAL = REAL1 + r'|' + REAL2 + r'|' + REAL3 + r'|' + REAL4
@TOKEN(REAL)
def t_REAL_CONST(t):
    t.value = float(t.value)
    return t

def t_HEX_CONST(t):
    r'[+-]?0x[0-9a-fA-F]+'
    t.value = int(t.value, base=16)
    return t


def t_OCT_CONST(t):
    r'[+-]?0o\d+'
    t.value = int(t.value, base=8)
    return t


def t_DEC_CONST(t):
    r'[+-]?\d+'
    t.value = int(t.value)

    if t.value < -2 ** 31 or 2 ** 31 - 1 < t.value:
        t.type = 'LONG_CONST'

    return t

def t_CHAR_CONST(t):
    r"'([^\\\n]|(\\.))'"
    t.value = t.value[1:-1]
    return t


def t_STR_CONST(t):
    r'"([^\\\n]|(\\.)){,1000}"'
    t.value = t.value[1:-1]
    return t


def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')    # Check for reserved words
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character {t.value[0]} in line {t.lineno}.")
    t.lexer.skip(1)


lexer = lex.lex()
