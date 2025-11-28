# lexer.py
import sys
import ply.lex as lex
from tokens import TOKEN_IDS, reserved
import os

# --------------------------------
# Tables
# --------------------------------
symbol_table = {}
literal_table = {}




def _init_symbol_table():
    for lexeme, tok in reserved.items():
        symbol_table[lexeme] = {'token': tok, 'kind': 'reserved'}


# Initialize symbol table
_init_symbol_table()

# --------------------------------
# Token regex rules
# --------------------------------
t_SEMICOLON = r';'
t_COMMA     = r','
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_EQ        = r'=='
t_NEQ       = r'!='
t_LT        = r'<'
t_GT        = r'>'
t_ASSIGN    = r'='

# Ignore spaces and tabs
t_ignore = ' \t'

# --------------------------------
# Token rules as functions
# --------------------------------
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    else:
        t.type = 'ID'
        if t.value not in symbol_table:
            symbol_table[t.value] = {'token': 'ID', 'kind': 'id'}
    return t


def t_INT_LIT(t):
    r'\d+'
    t.value = int(t.value)
    literal_table[t.value] = literal_table.get(t.value, 0) + 1
    return t


def t_comment(t):
    r'//[^\n]*'
    pass


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"[LEXICAL ERROR] Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)


# Build lexer
lexer = lex.lex()

# --------------------------------
# Lexer driver
# --------------------------------
def run_lexer(filename: str):
    with open(filename, 'r') as f:
        data = f.read()

    lexer.input(data)
    token_lines = []
    debug_lines = []

    while True:
        tok = lexer.token()
        if not tok:
            break

        token_id = TOKEN_IDS.get(tok.type, 0)
        token_line = f"{tok.lineno:<3} {token_id:<4} {tok.type:<12} {tok.value}"
        debug_line = f"Line {tok.lineno} Token #{token_id}: {tok.value}"

        token_lines.append(token_line)
        debug_lines.append(debug_line)

    base_name = os.path.basename(filename)        
    name_without_ext = os.path.splitext(base_name)[0]
    stream_filename = f"{name_without_ext}_stream.txt"

    # Write “To Parser” output
    with open(f'output/{stream_filename}', "w") as f:
        f.write("\n".join(token_lines))

    # Print “To Screen” output
    print("=== DEBUG OUTPUT ===")
    print("\n".join(debug_lines))

    # Print Symbol & Literal Tables
    print("\n=== SYMBOL TABLE (partial) ===")
    for name, info in sorted(symbol_table.items()):
        print(f"{name:15} -> {info['token']:10} ({info['kind']})")

    print("\n=== LITERAL TABLE ===")
    for val, count in sorted(literal_table.items()):
        print(f"{val:5} (occurrences: {count})")

    print(f'\nToken stream written to output/{stream_filename}')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_lexer(sys.argv[1])
    else:
        print("Please provide the program file path, e.g. `python lexer.py ../programs/program1.cl`")
