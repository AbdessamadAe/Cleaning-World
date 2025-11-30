# parser.py
import ply.yacc as yacc
from collections import deque
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../Part1&2/lexer'))

import lexer as lexer_module
from tokens import tokens

# ---------- CST node ----------
class CSTNode:
    def __init__(self, node_type, children=None, value=None, lineno=None):
        self.type = node_type        # Node category (e.g., 'program', 'expr', 'stmt')
        self.children = children if children is not None else []
        self.value = value           # Semantic value (for literals, identifiers, coordinates)
        self.lineno = lineno         # Source line number for better debugging (I hope we never need it)
        
    def add_child(self, child):
        if child is not None:
            self.children.append(child)
            
    def __repr__(self, level=0):
        indent = '  ' * level
        result = f"{indent}{self.type}"
        
        if self.value is not None:
            result += f": {self.value}"
            
        if self.lineno is not None:
            result += f" [line {self.lineno}]"
            
        result += "\n"
        
        for child in self.children:
            if isinstance(child, CSTNode):
                result += child.__repr__(level + 1)
            else:
                result += f"{indent}  {repr(child)}\n"
                
        return result

# ---------- Grammar arithmetic rules ----------
"""
    This defines how arithmetic operations are going to be parsed
    left:  Left-associative
    so for e.g: a + b + c = (a + b) + c
"""
precedence = (
    ('left', 'PLUS', 'MINUS'),
)

# program -> world_def function_list_opt agent_def
def p_program(p):
    'program : world_def function_list_opt agent_def'
    p[0] = CSTNode('program', [p[1], p[2], p[3]], lineno=p.lineno(1))

# function list optional
def p_function_list_opt_empty(p):
    'function_list_opt :'
    p[0] = CSTNode('function_list_opt', [])

def p_function_list_opt(p):
    'function_list_opt : function_list'
    p[0] = p[1]

def p_function_list(p):
    'function_list : function_decl'
    p[0] = CSTNode('function_list', [p[1]], lineno=p.lineno(1))

# function_decl: FUNC ID '(' param_list_opt ')' RETURNS type '{' stmt_list '}'
def p_function_decl(p):
    "function_decl : FUNC ID LPAREN param_list_opt RPAREN RETURNS type LBRACE stmt_list RBRACE"
    p[0] = CSTNode('function_decl', [
        p[4],  # param_list_opt
        p[7],  # type
        p[9]   # stmt_list
    ], value=p[2], lineno=p.lineno(1))  # function name stored in value

def p_param_list_opt_empty(p):
    'param_list_opt :'
    p[0] = CSTNode('param_list_opt', [])

def p_param_list_opt(p):
    'param_list_opt : param_list'
    p[0] = p[1]

def p_param_list_single(p):
    'param_list : param_decl'
    p[0] = CSTNode('param_list', [p[1]], lineno=p.lineno(1))

def p_param_list_more(p):
    'param_list : param_decl COMMA param_list'
    p[0] = CSTNode('param_list', [p[1]] + p[3].children, lineno=p.lineno(1))

def p_param_decl(p):
    'param_decl : ID'
    p[0] = CSTNode('param_decl', value=p[1], lineno=p.lineno(1))

def p_type_int(p):
    'type : TYPE_INT'
    p[0] = CSTNode('type', value='int', lineno=p.lineno(1))

def p_type_void(p):
    'type : TYPE_VOID'
    p[0] = CSTNode('type', value='void', lineno=p.lineno(1))

# world definition rules
def p_world_def(p):
    'world_def : WORLD ID LBRACE world_body RBRACE'
    p[0] = CSTNode('world_def', [p[4]], value=p[2], lineno=p.lineno(1))  # world name in value

def p_world_body_single(p):
    'world_body : world_stmt'
    p[0] = CSTNode('world_body', [p[1]], lineno=p.lineno(1))

def p_world_body_more(p):
    'world_body : world_stmt world_body'
    p[0] = CSTNode('world_body', [p[1]] + p[2].children, lineno=p.lineno(1))

# world statements
def p_world_stmt_size(p):
    'world_stmt : SIZE LPAREN INT_LIT COMMA INT_LIT RPAREN SEMICOLON'
    p[0] = CSTNode('size_decl', value=(p[3], p[5]), lineno=p.lineno(1))

def p_world_stmt_entry(p):
    'world_stmt : ENTRY_DEF LPAREN INT_LIT COMMA INT_LIT COMMA dir RPAREN SEMICOLON'
    direction = p[7].value if isinstance(p[7], CSTNode) else p[7]
    p[0] = CSTNode('entry_decl', value=(p[3], p[5], direction), lineno=p.lineno(1))

def p_world_stmt_exit(p):
    'world_stmt : EXIT_DEF LPAREN INT_LIT COMMA INT_LIT COMMA dir RPAREN SEMICOLON'
    direction = p[7].value if isinstance(p[7], CSTNode) else p[7]
    p[0] = CSTNode('exit_decl', value=(p[3], p[5], direction), lineno=p.lineno(1))

def p_world_stmt_obstacle(p):
    'world_stmt : OBSTACLE_DEF LPAREN INT_LIT COMMA INT_LIT RPAREN SEMICOLON'
    p[0] = CSTNode('obstacle_decl', value=(p[3], p[5]), lineno=p.lineno(1))

def p_world_stmt_dirt(p):
    'world_stmt : DIRT_DEF LPAREN INT_LIT COMMA INT_LIT RPAREN SEMICOLON'
    p[0] = CSTNode('dirt_decl', value=(p[3], p[5]), lineno=p.lineno(1))

# agent definition
def p_agent_def(p):
    'agent_def : AGENT ID LBRACE stmt_list RBRACE'
    p[0] = CSTNode('agent_def', [p[4]], value=p[2], lineno=p.lineno(1))  # agent name in value

# stmt list
def p_stmt_list_single(p):
    'stmt_list : stmt'
    p[0] = CSTNode('stmt_list', [p[1]], lineno=p.lineno(1))

def p_stmt_list_more(p):
    'stmt_list : stmt stmt_list'
    p[0] = CSTNode('stmt_list', [p[1]] + p[2].children, lineno=p.lineno(1))

# statements
def p_stmt_var_decl(p):
    'stmt : VAR ID ASSIGN expr SEMICOLON'
    p[0] = CSTNode('var_decl', [p[4]], value=p[2], lineno=p.lineno(1))

def p_stmt_assign(p):
    'stmt : ID ASSIGN expr SEMICOLON'
    p[0] = CSTNode('assign', [p[3]], value=p[1], lineno=p.lineno(1))

def p_stmt_if(p):
    'stmt : IF condition THEN stmt_list ELSE stmt_list ENDIF SEMICOLON'
    p[0] = CSTNode('if_stmt', [p[2], p[4], p[6]], lineno=p.lineno(1))

def p_stmt_while(p):
    'stmt : WHILE condition DO stmt_list ENDWHILE SEMICOLON'
    p[0] = CSTNode('while_stmt', [p[2], p[4]], lineno=p.lineno(1))

def p_stmt_move(p):
    'stmt : MOVE SEMICOLON'
    p[0] = CSTNode('move_stmt', lineno=p.lineno(1))

def p_stmt_turn(p):
    'stmt : TURN turn_dir SEMICOLON'
    p[0] = CSTNode('turn_stmt', [p[2]], lineno=p.lineno(1))

def p_stmt_clean(p):
    'stmt : CLEAN SEMICOLON'
    p[0] = CSTNode('clean_stmt', lineno=p.lineno(1))

def p_stmt_backtrack(p):
    'stmt : BACKTRACK SEMICOLON'
    p[0] = CSTNode('backtrack_stmt', lineno=p.lineno(1))

def p_stmt_report(p):
    'stmt : REPORT expr SEMICOLON'
    p[0] = CSTNode('report_stmt', [p[2]], lineno=p.lineno(1))

def p_stmt_return(p):
    'stmt : RETURN expr SEMICOLON'
    p[0] = CSTNode('return_stmt', [p[2]], lineno=p.lineno(1))

def p_stmt_function_call(p):
    'stmt : function_call SEMICOLON'
    p[0] = CSTNode('call_stmt', [p[1]], lineno=p.lineno(1))

# turn direction
def p_turn_dir_left(p):
    'turn_dir : LEFT'
    p[0] = CSTNode('left_dir', value='LEFT', lineno=p.lineno(1))

def p_turn_dir_right(p):
    'turn_dir : RIGHT'
    p[0] = CSTNode('right_dir', value='RIGHT', lineno=p.lineno(1))

# function call
def p_function_call(p):
    'function_call : ID LPAREN arg_list_opt RPAREN'
    p[0] = CSTNode('function_call', [p[3]], value=p[1], lineno=p.lineno(1))

def p_arg_list_opt_empty(p):
    'arg_list_opt :'
    p[0] = CSTNode('arg_list_opt', [])

def p_arg_list_opt(p):
    'arg_list_opt : arg_list'
    p[0] = p[1]

def p_arg_list_single(p):
    'arg_list : expr'
    p[0] = CSTNode('arg_list', [p[1]], lineno=p.lineno(1))

def p_arg_list_more(p):
    'arg_list : expr COMMA arg_list'
    p[0] = CSTNode('arg_list', [p[1]] + p[3].children, lineno=p.lineno(1))

# condition and sense expressions
def p_condition_sense(p):
    'condition : SENSE sense_expr'
    p[0] = CSTNode('sense_condition', [p[2]], lineno=p.lineno(1))

def p_condition_unary_not(p):
    'condition : NOT condition'
    p[0] = CSTNode('not_condition', [p[2]], lineno=p.lineno(1))

def p_condition_and(p):
    'condition : condition AND condition'
    p[0] = CSTNode('and_condition', [p[1], p[3]], lineno=p.lineno(1))

def p_condition_or(p):
    'condition : condition OR condition'
    p[0] = CSTNode('or_condition', [p[1], p[3]], lineno=p.lineno(1))

def p_condition_relop(p):
    'condition : expr relop expr'
    p[0] = CSTNode('relop_condition', [p[1], p[2], p[3]], lineno=p.lineno(1))

def p_condition_unvisited(p):
    'condition : UNVISITED'
    p[0] = CSTNode('unvisited_condition', lineno=p.lineno(1))

def p_sense_expr(p):
    'sense_expr : DIRT'
    p[0] = CSTNode('dirt_sense', value='DIRT', lineno=p.lineno(1))

def p_sense_obs(p):
    'sense_expr : OBSTACLE'
    p[0] = CSTNode('obstacle_sense', value='OBSTACLE', lineno=p.lineno(1))

def p_sense_exit(p):
    'sense_expr : EXIT'
    p[0] = CSTNode('exit_sense', value='EXIT', lineno=p.lineno(1))

def p_sense_entry(p):
    'sense_expr : ENTRY'
    p[0] = CSTNode('entry_sense', value='ENTRY', lineno=p.lineno(1))

# relops
def p_relop_eq(p):
    'relop : EQ'
    p[0] = CSTNode('eq_op', value='EQ', lineno=p.lineno(1))

def p_relop_neq(p):
    'relop : NEQ'
    p[0] = CSTNode('neq_op', value='NEQ', lineno=p.lineno(1))

def p_relop_lt(p):
    'relop : LT'
    p[0] = CSTNode('lt_op', value='LT', lineno=p.lineno(1))

def p_relop_gt(p):
    'relop : GT'
    p[0] = CSTNode('gt_op', value='GT', lineno=p.lineno(1))
    

# expressions
def p_expr_plus(p):
    'expr : term PLUS expr'
    p[0] = CSTNode('plus_expr', [p[1], p[3]], value='+', lineno=p.lineno(2))

def p_expr_minus(p):
    'expr : term MINUS expr'
    p[0] = CSTNode('minus_expr', [p[1], p[3]], value='-', lineno=p.lineno(2))

def p_expr_term(p):
    'expr : term'
    p[0] = p[1]

def p_term_id(p):
    'term : ID'
    p[0] = CSTNode('identifier', value=p[1], lineno=p.lineno(1))

def p_term_int(p):
    'term : INT_LIT'
    p[0] = CSTNode('integer_literal', value=p[1], lineno=p.lineno(1))

def p_term_call(p):
    'term : function_call'
    p[0] = p[1]

# dir (for ENTRY/EXIT)
def p_dir_n(p):
    'dir : N'
    p[0] = CSTNode('direction', value='N', lineno=p.lineno(1))

def p_dir_e(p):
    'dir : E'
    p[0] = CSTNode('direction', value='E', lineno=p.lineno(1))

def p_dir_s(p):
    'dir : S'
    p[0] = CSTNode('direction', value='S', lineno=p.lineno(1))

def p_dir_w(p):
    'dir : W'
    p[0] = CSTNode('direction', value='W', lineno=p.lineno(1))

# error handling
def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} (value={p.value!r}) line={getattr(p, 'lineno', '?')}")
        # Debug: show the next few tokens to understand context
        print("Next tokens for debugging:")
        for i in range(5):
            tok = lexer.token()
            if tok:
                print(f"  {tok.type}: {tok.value}")
            else:
                print("  No more tokens")
                break
    else:
        print("Syntax error at EOF")

# create lexer instance
lexer = lexer_module.lexer

# build the parser
parser = yacc.yacc()

def write_cst_to_file(cst, filename):
    """Write the Concrete Syntax Tree to output file"""
    base_name = os.path.basename(filename)
    name_without_ext = os.path.splitext(base_name)[0]
    
    # Write to Part3&4/CSTs/ directory (absolute path from parser location)
    parser_dir = os.path.dirname(__file__)
    csts_dir = os.path.join(parser_dir, '..', 'CSTs')
    csts_dir = os.path.abspath(csts_dir)
    os.makedirs(csts_dir, exist_ok=True)
    
    cst_filename = os.path.join(csts_dir, f"{name_without_ext}_cst.txt")
    
    with open(cst_filename, 'w') as f:
        f.write(f"Concrete Syntax Tree for: {base_name}\n")
        f.write("=" * 50 + "\n")
        f.write(str(cst))
    
    print(f"CST written to: {cst_filename}")
    return cst_filename

# convenience parse function
def parse(text=None, filename=None):
    if filename:
        with open(filename, 'r') as f:
            text = f.read()
        
        cst = parser.parse(text, lexer=lexer, tracking=True)
        
        if cst:
            write_cst_to_file(cst, filename)
        
        return cst
    elif text is not None:
        return parser.parse(text, lexer=lexer, tracking=True)
    else:
        raise ValueError("provide text or filename")
