# semantic.py -- CST -> AST transformer + simple static semantics checks

from ast_nodes import *
# CSTNode comes from parser.parse output; we accept it as input without importing parser (no circular import)

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # list of dicts, 0 = global

    def push(self):
        self.scopes.append({})

    def pop(self):
        self.scopes.pop()

    def declare(self, name, info):
        scope = self.scopes[-1]
        if name in scope:
            return False
        scope[name] = info
        return True

    def lookup(self, name):
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        return None

# Semantic analyzer & transformer
class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors = []
        self.current_function = None

    def error(self, msg):
        self.errors.append(msg)

    def analyze(self, cst):
        # Expect program CSTNode
        if cst is None or cst.type != 'program':
            self.error("Invalid CST root")
            return None, self.errors

        world_cst = cst.children[0]
        funcs_cst = cst.children[1]
        agent_cst = cst.children[2]

        # Phase 1: register functions (global scope)
        funcs = []
        if funcs_cst and funcs_cst.type == 'function_list':
            for f in funcs_cst.children:
                name = f.children[0].token  # 'FUNC' node carrying function name
                ret_type = f.children[2].token if len(f.children) > 2 and f.children[2].token else 'int'
                params = self._collect_param_names(f.children[1])
                # check duplicate function
                if not self.symtab.declare(name, {'kind': 'function', 'params': params, 'ret': ret_type}):
                    self.error(f"Duplicate function declaration: {name}")
                funcs.append((f, name, params, ret_type))

        # Transform world
        world_ast = self._transform_world(world_cst)

        # Transform functions (check bodies)
        ast_funcs = []
        for f_cst, name, params, ret_type in funcs:
            self.symtab.push()
            # declare parameters in function scope
            for p in params:
                ok = self.symtab.declare(p, {'kind': 'param', 'type': 'int'})
                if not ok:
                    self.error(f"Duplicate parameter name '{p}' in function {name}")
            self.current_function = {'name': name, 'ret': ret_type}
            body_stmts = self._transform_stmt_list(f_cst.children[3])
            ast_funcs.append(FunctionDef(name, params, ret_type, body_stmts))
            self.symtab.pop()
            self.current_function = None

        # Transform agent (agent has its own scope)
        agent_name = agent_cst.children[0].token
        self.symtab.push()
        agent_body = self._transform_stmt_list(agent_cst.children[1])
        self.symtab.pop()

        ast_prog = Program(world_ast, ast_funcs, AgentDef(agent_name, agent_body))
        return ast_prog, self.errors

    # helpers
    def _collect_param_names(self, param_list_opt):
        if param_list_opt is None:
            return []
        if param_list_opt.type == 'param_list':
            return [p.token for p in param_list_opt.children]
        return []

    def _transform_world(self, world_cst):
        name = world_cst.children[0].token
        body = world_cst.children[1]
        stmts = []
        for s in body.children:
            if s.type == 'SIZE':
                stmts.append(ASTNode('Size', value=s.token))
            elif s.type == 'ENTRY_DEF':
                stmts.append(ASTNode('Entry', value=s.token))
            elif s.type == 'EXIT_DEF':
                stmts.append(ASTNode('Exit', value=s.token))
            elif s.type == 'OBSTACLE_DEF':
                stmts.append(ASTNode('Obstacle', value=s.token))
            elif s.type == 'DIRT_DEF':
                stmts.append(ASTNode('Dirt', value=s.token))
        return WorldDef(name, stmts)

    def _transform_stmt_list(self, stmt_list_cst):
        stmts = []
        # stmt_list nodes contain children each of which is a stmt node
        for s in stmt_list_cst.children:
            stmts.append(self._transform_stmt(s))
        return stmts

    def _transform_stmt(self, node):
        t = node.type
        if t == 'var_decl':
            name = node.token
            expr = self._transform_expr(node.children[0])
            # declare variable in current scope
            if not self.symtab.declare(name, {'kind': 'var', 'type': 'int'}):
                self.error(f"Duplicate variable declaration: {name}")
            return VarDecl(name, expr)
        if t == 'assign':
            name = node.token
            # check declared
            sym = self.symtab.lookup(name)
            if sym is None:
                self.error(f"Assignment to undeclared identifier: {name}")
            expr = self._transform_expr(node.children[0])
            return Assign(name, expr)
        if t == 'if':
            cond = self._transform_condition(node.children[0])
            then_stmts = [self._transform_stmt(s) for s in node.children[1].children]
            else_stmts = [self._transform_stmt(s) for s in node.children[2].children]
            return IfStmt(cond, then_stmts, else_stmts)
        if t == 'while':
            cond = self._transform_condition(node.children[0])
            body_stmts = [self._transform_stmt(s) for s in node.children[1].children]
            return WhileStmt(cond, body_stmts)
        if t == 'move':
            return MoveStmt()
        if t == 'turn':
            dir_node = node.children[0]
            return TurnStmt(dir_node.value if hasattr(dir_node, 'value') else getattr(dir_node, 'token', None))
        if t == 'clean':
            return CleanStmt()
        if t == 'backtrack':
            return BacktrackStmt()
        if t == 'report':
            expr = self._transform_expr(node.children[0])
            return ReportStmt(expr)
        if t == 'return':
            # return must be inside function
            if not self.current_function:
                self.error("RETURN used outside of function")
            expr = self._transform_expr(node.children[0])
            # return type checks (if function declared void, do not allow expr)
            if self.current_function and self.current_function.get('ret') == 'void' and expr is not None:
                self.error(f"Function {self.current_function['name']} is void but RETURN has a value")
            return ReturnStmt(expr)
        if t == 'call_stmt':
            call = node.children[0]
            call_expr = self._transform_call(call)
            return ASTNode('CallStmt', children=[call_expr])
        # fallback
        self.error(f"Unhandled statement kind: {t}")
        return ASTNode('UnknownStmt', value=t)

    def _transform_condition(self, node):
        t = node.type
        if t == 'sense_condition':
            sense = node.children[0]
            return SenseExpr(sense.token)
        if t == 'not':
            return ASTNode('Not', children=[self._transform_condition(node.children[0])])
        if t == 'and':
            return ASTNode('And', children=[self._transform_condition(node.children[0]), self._transform_condition(node.children[1])])
        if t == 'or':
            return ASTNode('Or', children=[self._transform_condition(node.children[0]), self._transform_condition(node.children[1])])
        if t == 'relop':
            left = self._transform_expr(node.children[0])
            op_node = node.children[1]
            # op_node is a CSTNode like 'EQ' / 'LT' etc
            op = op_node.type if hasattr(op_node, 'type') else str(op_node)
            right = self._transform_expr(node.children[2])
            return ASTNode('RelOp', value=op, children=[left, right])
        if t == 'unvisited':
            return UnvisitedExpr()
        # fallback
        self.error(f"Unhandled condition kind: {t}")
        return ASTNode('UnknownCond', value=t)

    def _transform_expr(self, node):
        if node is None:
            return None
        t = node.type
        if t == 'plus' or t == 'minus':
            op = '+' if t == 'plus' else '-'
            left = self._transform_expr(node.children[0])
            right = self._transform_expr(node.children[1])
            return BinOp(op, left, right)
        if t == 'id':
            name = node.token
            # reference must be declared (variable or function param)
            sym = self.symtab.lookup(name)
            if sym is None:
                self.error(f"Use of undeclared identifier: {name}")
            return VarRef(name)
        if t == 'int':
            return IntLit(node.token)
        if t == 'function_call':
            return self._transform_call(node)
        # fallback
        self.error(f"Unhandled expr kind: {t}")
        return ASTNode('UnknownExpr', value=t)

    def _transform_call(self, call_cst):
        # call_cst.children = [CSTNode('name', token=name), arg_list_opt]
        name = call_cst.children[0].token
        args_cst = call_cst.children[1]
        args = []
        if args_cst and args_cst.type == 'arg_list':
            for a in args_cst.children:
                args.append(self._transform_expr(a))
        # check function declaration
        fn = self.symtab.lookup(name)
        if fn is None or fn.get('kind') != 'function':
            self.error(f"Call to undeclared function: {name}")
        else:
            expected = len(fn.get('params', []))
            if len(args) != expected:
                self.error(f"Function {name} called with {len(args)} args but expects {expected}")
        return CallExpr(name, args)

# Convenience API
def analyze_cst(cst):
    sa = SemanticAnalyzer()
    ast, errs = sa.analyze(cst)
    return ast, errs