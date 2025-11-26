# parser.py
import ply.yacc as yacc
from collections import deque
import sys
import os

# Add the lexer directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../Part1&2/lexer'))

# Import tokens from the lexer
from tokens import tokens
import lexer as lexer_module

# ---------- Simple generic CST node ----------
class CSTNode:
    def __init__(self, nodetype, children=None, token=None):
        self.type = nodetype
        self.children = children if children is not None else []
        self.token = token   # optional: store the lexeme/token for leaves

    def add_child(self, c):
        self.children.append(c)

    def __repr__(self, level=0):
        indent = '  ' * level
        if self.token is not None:
            return f"{indent}{self.type}: {self.token}\n"
        s = f"{indent}{self.type}\n"
        for ch in self.children:
            if isinstance(ch, CSTNode):
                s += ch.__repr__(level+1)
            else:
                s += f"{indent}  {repr(ch)}\n"
        return s

# ---------- Grammar rules (from supplied grammar) ----------
precedence = (
    ('left', 'PLUS', 'MINUS'),
)

# program -> world_def function_list_opt agent_def
def p_program(p):
    'program : world_def function_list_opt agent_def'
    p[0] = CSTNode('program', [p[1], p[2], p[3]])

# function list optional
def p_function_list_opt_empty(p):
    'function_list_opt :'
    p[0] = CSTNode('function_list_opt', [])

def p_function_list_opt(p):
    'function_list_opt : function_list'
    p[0] = p[1]

def p_function_list(p):
    'function_list : function_decl'
    p[0] = CSTNode('function_list', [p[1]])

# function_decl: FUNC ID '(' param_list_opt ')' RETURNS type '{' stmt_list '}'
def p_function_decl(p):
    "function_decl : FUNC ID LPAREN param_list_opt RPAREN RETURNS type LBRACE stmt_list RBRACE"
    p[0] = CSTNode('function_decl', [
        CSTNode('FUNC', token=p[2]),
        p[4],
        p[7],
        p[9]
    ])

def p_param_list_opt_empty(p):
    'param_list_opt :'
    p[0] = CSTNode('param_list_opt', [])

def p_param_list_opt(p):
    'param_list_opt : param_list'
    p[0] = p[1]

def p_param_list_single(p):
    'param_list : param_decl'
    p[0] = CSTNode('param_list', [p[1]])

def p_param_list_more(p):
    'param_list : param_decl COMMA param_list'
    p[0] = CSTNode('param_list', [p[1]] + p[3].children)

def p_param_decl(p):
    'param_decl : ID'
    p[0] = CSTNode('param_decl', [], token=p[1])

def p_type_int(p):
    'type : TYPE_INT'
    p[0] = CSTNode('type', [], token='int')

def p_type_void(p):
    'type : TYPE_VOID'
    p[0] = CSTNode('type', [], token='void')

# world definition rules
def p_world_def(p):
    'world_def : WORLD ID LBRACE world_body RBRACE'
    p[0] = CSTNode('world_def', [CSTNode('WORLD', token=p[2]), p[4]])

def p_world_body_single(p):
    'world_body : world_stmt'
    p[0] = CSTNode('world_body', [p[1]])

def p_world_body_more(p):
    'world_body : world_stmt world_body'
    p[0] = CSTNode('world_body', [p[1]] + p[2].children)

# world statements
def p_world_stmt_size(p):
    'world_stmt : SIZE LPAREN INT_LIT COMMA INT_LIT RPAREN SEMICOLON'
    p[0] = CSTNode('SIZE', [], token=(p[3], p[5]))

def p_world_stmt_entry(p):
    'world_stmt : ENTRY_DEF LPAREN INT_LIT COMMA INT_LIT COMMA dir RPAREN SEMICOLON'
    p[0] = CSTNode('ENTRY_DEF', [], token=(p[3], p[5], p[7].token if isinstance(p[7], CSTNode) else p[7]))

def p_world_stmt_exit(p):
    'world_stmt : EXIT_DEF LPAREN INT_LIT COMMA INT_LIT COMMA dir RPAREN SEMICOLON'
    p[0] = CSTNode('EXIT_DEF', [], token=(p[3], p[5], p[7].token if isinstance(p[7], CSTNode) else p[7]))

def p_world_stmt_obstacle(p):
    'world_stmt : OBSTACLE_DEF LPAREN INT_LIT COMMA INT_LIT RPAREN SEMICOLON'
    p[0] = CSTNode('OBSTACLE_DEF', [], token=(p[3], p[5]))

def p_world_stmt_dirt(p):
    'world_stmt : DIRT_DEF LPAREN INT_LIT COMMA INT_LIT RPAREN SEMICOLON'
    p[0] = CSTNode('DIRT_DEF', [], token=(p[3], p[5]))

# agent definition
def p_agent_def(p):
    'agent_def : AGENT ID LBRACE stmt_list RBRACE'
    p[0] = CSTNode('agent_def', [CSTNode('AGENT', token=p[2]), p[4]])

# stmt list
def p_stmt_list_single(p):
    'stmt_list : stmt'
    p[0] = CSTNode('stmt_list', [p[1]])

def p_stmt_list_more(p):
    'stmt_list : stmt stmt_list'
    p[0] = CSTNode('stmt_list', [p[1]] + p[2].children)

# statements
def p_stmt_var_decl(p):
    'stmt : VAR ID ASSIGN expr SEMICOLON'
    node = CSTNode('var_decl', [], token=p[2])
    node.add_child(p[4])
    p[0] = node

def p_stmt_assign(p):
    'stmt : ID ASSIGN expr SEMICOLON'
    node = CSTNode('assign', [], token=p[1])
    node.add_child(p[3])
    p[0] = node

def p_stmt_if(p):
    'stmt : IF condition THEN stmt_list ELSE stmt_list ENDIF SEMICOLON'
    p[0] = CSTNode('if', [p[2], p[4], p[6]])

def p_stmt_while(p):
    'stmt : WHILE condition DO stmt_list ENDWHILE SEMICOLON'
    p[0] = CSTNode('while', [p[2], p[4]])

def p_stmt_move(p):
    'stmt : MOVE SEMICOLON'
    p[0] = CSTNode('move')

def p_stmt_turn(p):
    'stmt : TURN turn_dir SEMICOLON'
    p[0] = CSTNode('turn', [p[2]])

def p_stmt_clean(p):
    'stmt : CLEAN SEMICOLON'
    p[0] = CSTNode('clean')

def p_stmt_backtrack(p):
    'stmt : BACKTRACK SEMICOLON'
    p[0] = CSTNode('backtrack')

def p_stmt_report(p):
    'stmt : REPORT expr SEMICOLON'
    p[0] = CSTNode('report', [p[2]])

def p_stmt_return(p):
    'stmt : RETURN expr SEMICOLON'
    p[0] = CSTNode('return', [p[2]])

def p_stmt_function_call(p):
    'stmt : function_call SEMICOLON'
    p[0] = CSTNode('call_stmt', [p[1]])

# turn direction
def p_turn_dir_left(p):
    'turn_dir : LEFT'
    p[0] = CSTNode('LEFT', token='LEFT')

def p_turn_dir_right(p):
    'turn_dir : RIGHT'
    p[0] = CSTNode('RIGHT', token='RIGHT')

# function call
def p_function_call(p):
    'function_call : ID LPAREN arg_list_opt RPAREN'
    p[0] = CSTNode('function_call', [CSTNode('name', token=p[1]), p[3]])

def p_arg_list_opt_empty(p):
    'arg_list_opt :'
    p[0] = CSTNode('arg_list_opt', [])

def p_arg_list_opt(p):
    'arg_list_opt : arg_list'
    p[0] = p[1]

def p_arg_list_single(p):
    'arg_list : expr'
    p[0] = CSTNode('arg_list', [p[1]])

def p_arg_list_more(p):
    'arg_list : expr COMMA arg_list'
    p[0] = CSTNode('arg_list', [p[1]] + p[3].children)

# condition and sense expressions
def p_condition_sense(p):
    'condition : SENSE sense_expr'
    p[0] = CSTNode('sense_condition', [p[2]])

def p_condition_unary_not(p):
    'condition : NOT condition'
    p[0] = CSTNode('not', [p[2]])

def p_condition_and(p):
    'condition : condition AND condition'
    p[0] = CSTNode('and', [p[1], p[3]])

def p_condition_or(p):
    'condition : condition OR condition'
    p[0] = CSTNode('or', [p[1], p[3]])

def p_condition_relop(p):
    'condition : expr relop expr'
    p[0] = CSTNode('relop', [p[1], p[2], p[3]])

def p_condition_unvisited(p):
    'condition : UNVISITED'
    p[0] = CSTNode('unvisited')

def p_sense_expr(p):
    'sense_expr : DIRT'
    p[0] = CSTNode('sense', token='DIRT')

def p_sense_obs(p):
    'sense_expr : OBSTACLE'
    p[0] = CSTNode('sense', token='OBSTACLE')

def p_sense_exit(p):
    'sense_expr : EXIT'
    p[0] = CSTNode('sense', token='EXIT')

def p_sense_entry(p):
    'sense_expr : ENTRY'
    p[0] = CSTNode('sense', token='ENTRY')

# relops
def p_relop_eq(p):
    'relop : EQ'
    p[0] = CSTNode('EQ')

def p_relop_neq(p):
    'relop : NEQ'
    p[0] = CSTNode('NEQ')

def p_relop_lt(p):
    'relop : LT'
    p[0] = CSTNode('LT')

def p_relop_gt(p):
    'relop : GT'
    p[0] = CSTNode('GT')

# expressions
def p_expr_plus(p):
    'expr : term PLUS expr'
    p[0] = CSTNode('plus', [p[1], p[3]])

def p_expr_minus(p):
    'expr : term MINUS expr'
    p[0] = CSTNode('minus', [p[1], p[3]])

def p_expr_term(p):
    'expr : term'
    p[0] = p[1]

def p_term_id(p):
    'term : ID'
    p[0] = CSTNode('id', token=p[1])

def p_term_int(p):
    'term : INT_LIT'
    p[0] = CSTNode('int', token=p[1])

def p_term_call(p):
    'term : function_call'
    p[0] = p[1]

# dir (for ENTRY/EXIT)
def p_dir_n(p):
    'dir : N'
    p[0] = CSTNode('DIR', token='N')

def p_dir_e(p):
    'dir : E'
    p[0] = CSTNode('DIR', token='E')

def p_dir_s(p):
    'dir : S'
    p[0] = CSTNode('DIR', token='S')

def p_dir_w(p):
    'dir : W'
    p[0] = CSTNode('DIR', token='W')

# error handling
def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} (value={p.value!r}) line={getattr(p, 'lineno', '?')}")
    else:
        print("Syntax error at EOF")

# create lexer instance
lexer = lexer_module.lexer

# build the parser
parser = yacc.yacc()

# convenience parse function
def parse(text=None, filename=None):
    if filename:
        with open(filename, 'r') as f:
            text = f.read()
        return parser.parse(text, lexer=lexer, tracking=True)
    elif text is not None:
        return parser.parse(text, lexer=lexer, tracking=True)
    else:
        raise ValueError("provide text or filename")
