# lexer.py
import ply.lex as lex
from tokens import tokens

# ---------------------------
# Token regex definitions
# ---------------------------

# Punctuation
t_SEMICOLON = r';'
t_COMMA     = r','
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'

# Operators
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_ASSIGN    = r'='
t_EQ        = r'=='
t_NEQ       = r'!='
t_LT        = r'<'
t_GT        = r'>'

# Ignored characters (whitespace)
t_ignore = ' \t'

# ---------------------------
# Reserved word map
# ---------------------------

reserved = {
    # --- World & Agent ---
    'WORLD': 'WORLD',
    'AGENT': 'AGENT',
    'SIZE': 'SIZE',
    'ENTRY': 'ENTRY',
    'EXIT': 'EXIT',
    'OBSTACLE_DEF': 'OBSTACLE_DEF',
    'DIRT_DEF': 'DIRT_DEF',

    # --- Directions ---
    'N': 'N',
    'E': 'E',
    'S': 'S',
    'W': 'W',

    # --- Variable & control ---
    'VAR': 'VAR',
    'IF': 'IF',
    'THEN': 'THEN',
    'ELSE': 'ELSE',
    'ENDIF': 'ENDIF',
    'WHILE': 'WHILE',
    'DO': 'DO',
    'ENDWHILE': 'ENDWHILE',

    # --- Actions ---
    'MOVE': 'MOVE',
    'TURN': 'TURN',
    'LEFT': 'LEFT',
    'RIGHT': 'RIGHT',
    'CLEAN': 'CLEAN',
    'BACKTRACK': 'BACKTRACK',

    # --- Sensors & conditions ---
    'SENSE': 'SENSE',
    'DIRT': 'DIRT',
    'OBSTACLE': 'OBSTACLE',
    'UNVISITED': 'UNVISITED',

    # --- Functions ---
    'FUNC': 'FUNC',
    'RETURNS': 'RETURNS',
    'RETURN': 'RETURN',

    # --- Data Types ---
    'INT': 'TYPE_INT',
    'VOID': 'TYPE_VOID',

    # --- Logical operators ---
    'AND': 'AND',
    'OR': 'OR',
    'NOT': 'NOT',
}

# ---------------------------
# Token functions
# ---------------------------

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_INT_LIT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_comment(t):
    r'//[^\n]*'
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# ---------------------------
# Build lexer
# ---------------------------

lexer = lex.lex()

# ---------------------------
# Run
# ---------------------------

if __name__ == "__main__":
    with open("../program.cl", "r") as f:
        data = f.read()
    lexer.input(data)

    with open("stream.txt", "w") as wf:
        for tok in lexer:
            wf.write(f"{tok.type:15} {tok.value}\n")
