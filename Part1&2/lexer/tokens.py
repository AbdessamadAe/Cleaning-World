# --------------------------------
# Token IDs (for parser output)
# --------------------------------
TOKEN_IDS = {
    # World & Agent
    'WORLD': 1, 'AGENT': 2, 'SIZE': 3, 'ENTRY_DEF': 4, 'EXIT_DEF': 5,
    'OBSTACLE_DEF': 6, 'DIRT_DEF': 7,

    # Directions
    'N': 8, 'E': 9, 'S': 10, 'W': 11,

    # Variables & Control
    'VAR': 12, 'IF': 13, 'THEN': 14, 'ELSE': 15, 'ENDIF': 16,
    'WHILE': 17, 'DO': 18, 'ENDWHILE': 19,

    # Actions
    'MOVE': 20, 'TURN': 21, 'LEFT': 22, 'RIGHT': 23, 'CLEAN': 24, 'BACKTRACK': 25, 'REPORT': 55,

    # Sensors / Conditions
    'SENSE': 26, 'DIRT': 27, 'OBSTACLE': 28, 'UNVISITED': 29, 'ENTRY': 30, 'EXIT': 31,

    # Functions
    'FUNC': 32, 'RETURNS': 33, 'RETURN': 34,

    # Types
    'TYPE_INT': 35, 'TYPE_VOID': 36,

    # Logical Operators
    'AND': 37, 'OR': 38, 'NOT': 39,

    # Relational / Arithmetic
    'ASSIGN': 40, 'PLUS': 41, 'MINUS': 42, 'EQ': 43, 'NEQ': 44, 'LT': 45, 'GT': 46,

    # Punctuation
    'LBRACE': 47, 'RBRACE': 48, 'LPAREN': 49, 'RPAREN': 50,
    'COMMA': 51, 'SEMICOLON': 52,

    # Literals & IDs
    'INT_LIT': 53, 'ID': 54
}

# --------------------------------
# Reserved words
# --------------------------------
reserved = {}
special_cases = {'INT': 'TYPE_INT', 'VOID': 'TYPE_VOID'}  # Manual overrides

for token_name in TOKEN_IDS:
    if token_name.isalpha() and not token_name.startswith(('TYPE_', 'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN')):
        reserved[token_name] = token_name

reserved.update(special_cases)