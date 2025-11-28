# lexer.py
import sys
import ply.lex as lex
from tokens import TOKEN_IDS, reserved
import os

# --------------------------------
# Symbol and Literal Tables
# --------------------------------
symbol_table = {}    # Tracks identifiers and reserved words with their attributes
literal_table = {}   # Tracks integer literals and their frequency


def _init_symbol_table():
    """
    Pre-populate symbol table with reserved words.
    This allows us to distinguish between keywords and user-defined identifiers.
    """
    for lexeme, tok in reserved.items():
        symbol_table[lexeme] = {'token': tok, 'kind': 'reserved'}


# Initialize symbol table with reserved words
_init_symbol_table()

# --------------------------------
# Token regex rules for simple tokens
# --------------------------------
# These are defined as simple regex patterns since they map directly to single characters
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

# These don't produce tokens but help separate other tokens
t_ignore = ' \t'

# --------------------------------
# Complex token rules as functions
# --------------------------------
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    """
    Match identifiers: start with letter/underscore, followed by letters/numbers/underscores.
    
    Logic:
    1. Check if the matched text is a reserved word
    2. If reserved, use the predefined token type
    3. If not reserved, it's a user identifier - add to symbol table if new
    4. Always return the token for parser consumption
    """
    if t.value in reserved:
        # This is a keyword/reserved word - use its predefined token type
        t.type = reserved[t.value]
    else:
        # This is a user-defined identifier
        t.type = 'ID'
        if t.value not in symbol_table:
            # First time seeing this identifier - add to symbol table
            symbol_table[t.value] = {'token': 'ID', 'kind': 'id'}
    return t


def t_INT_LIT(t):
    r'\d+'
    """
    Match integer literals: one or more digits.
    
    Logic:
    1. Convert the string of digits to an integer value
    2. Track frequency in literal table for analysis
    3. Return token with integer value for parser
    """
    t.value = int(t.value)  # Convert from string to integer
    # Count occurrences of this literal value for analysis
    literal_table[t.value] = literal_table.get(t.value, 0) + 1
    return t


def t_comment(t):
    r'//[^\n]*'
    """
    Logic:
    - Comments are ignored by returning nothing
    - The regex matches but no token is produced
    """
    pass


def t_newline(t):
    r'\n+'
    """
    Match newlines to track line numbers.
    
    Logic:
    - Increment line counter by the number of newlines found
    - No token produced for newlines
    """
    t.lexer.lineno += len(t.value) 

def t_error(t):
    """
    Handle lexical errors - called when no token rule matches.
    
    Logic:
    1. Report the illegal character and its location
    2. Skip the problematic character to continue lexing
    3. This allows the lexer to recover from minor errors
    """
    print(f"[LEXICAL ERROR] Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)  # Skip one character and continue lexing


# Build the lexer using PLY's lex engine
lexer = lex.lex()

# --------------------------------
# Lexer driver - main interface
# --------------------------------
def run_lexer(filename: str):
    """
    1. Read source code from file
    2. Feed source to lexer to generate tokens
    3. Process each token to create parser stream and debug output
    4. Write token stream to file for parser consumption
    5. Display debug information and symbol tables
    """
    with open(filename, 'r') as f:
        data = f.read()

    # Feed source code to the lexer
    lexer.input(data)
    
    token_lines = []  
    debug_lines = [] 

    # Process all tokens from the lexer
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more tokens

        # Get token ID from our token definitions, default to 0 if not found
        token_id = TOKEN_IDS.get(tok.type, 0)
        
        # Format token for parser stream file (structured format)
        token_line = f"{tok.lineno:<3} {token_id:<4} {tok.type:<12} {tok.value}"
        
        debug_line = f"Line {tok.lineno} Token #{token_id}: {tok.value}"

        token_lines.append(token_line)
        debug_lines.append(debug_line)

    base_name = os.path.basename(filename)        
    name_without_ext = os.path.splitext(base_name)[0]
    stream_filename = f"{name_without_ext}_stream.txt"

    with open(f'output/{stream_filename}', "w") as f:
        f.write("\n".join(token_lines))

    print("=== DEBUG OUTPUT (To Screen) ===")
    print("\n".join(debug_lines))

    print("\n=== SYMBOL TABLE (partial) ===")
    for name, info in sorted(symbol_table.items()):
        print(f"{name:15} -> {info['token']:10} ({info['kind']})")

    print("\n=== LITERAL TABLE ===")
    for val, count in sorted(literal_table.items()):
        print(f"{val:5} (occurrences: {count})")

    print(f'\nToken stream written to output/{stream_filename}')


if __name__ == "__main__":
    """
    Command-line interface for the lexer.
    
    Usage: python lexer.py <source_file.cl>
    """
    if len(sys.argv) > 1:
        run_lexer(sys.argv[1])
    else:
        print("Please provide the program file path, e.g. `python lexer.py ../programs/program1.cl`")