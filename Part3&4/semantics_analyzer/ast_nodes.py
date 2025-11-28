# AST node classes (simple, printable)

class ASTNode:
    def __init__(self, kind, value=None, children=None):
        self.kind = kind
        self.value = value
        self.children = children if children is not None else []

    def add(self, node):
        self.children.append(node)

    def __repr__(self, level=0):
        indent = '  ' * level
        s = f"{indent}{self.kind}"
        if self.value is not None:
            s += f": {self.value}"
        s += "\n"
        for c in self.children:
            if isinstance(c, ASTNode):
                s += c.__repr__(level + 1)
            else:
                s += f"{indent}  {repr(c)}\n"
        return s

# Convenience constructors
def Program(world, functions, agent):
    return ASTNode('Program', children=[world, ASTNode('Functions', children=functions), agent])

def WorldDef(name, stmts):
    return ASTNode('WorldDef', value=name, children=stmts)

def FunctionDef(name, params, ret_type, body):
    return ASTNode('Function', value=name, children=[ASTNode('Params', children=[ASTNode('Param', value=p) for p in params]),
                                                    ASTNode('RetType', value=ret_type),
                                                    ASTNode('Body', children=body)])

def AgentDef(name, stmts):
    return ASTNode('Agent', value=name, children=stmts)

# Statement / Expr helpers
def VarDecl(name, expr):
    return ASTNode('VarDecl', value=name, children=[expr])

def Assign(name, expr):
    return ASTNode('Assign', value=name, children=[expr])

def IfStmt(cond, then_stmts, else_stmts):
    return ASTNode('If', children=[cond, ASTNode('Then', children=then_stmts), ASTNode('Else', children=else_stmts)])

def WhileStmt(cond, body_stmts):
    return ASTNode('While', children=[cond, ASTNode('Body', children=body_stmts)])

def MoveStmt():
    return ASTNode('Move')

def TurnStmt(dir_token):
    return ASTNode('Turn', value=dir_token)

def CleanStmt():
    return ASTNode('Clean')

def BacktrackStmt():
    return ASTNode('Backtrack')

def ReportStmt(expr):
    return ASTNode('Report', children=[expr])

def ReturnStmt(expr):
    return ASTNode('Return', children=[expr])

def CallExpr(name, args):
    return ASTNode('Call', value=name, children=args)

def BinOp(op, left, right):
    return ASTNode('BinOp', value=op, children=[left, right])

def IntLit(v):
    return ASTNode('Int', value=v)

def VarRef(name):
    return ASTNode('Var', value=name)

def SenseExpr(kind):
    return ASTNode('Sense', value=kind)

def UnvisitedExpr():
    return ASTNode('Unvisited')