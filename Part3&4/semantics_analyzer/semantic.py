# semantic.py -- CST -> AST transformer + simple static semantics checks

from .ast_nodes import *


class SymbolTable:
    """Simple symbol table with nested scopes for variable/function declarations."""
    def __init__(self):
        self.scopes = [{}]  # list of dicts; scope 0 is global

    def push(self):
        """Enter a new scope (e.g., function body or agent body)."""
        self.scopes.append({})

    def pop(self):
        """Exit current scope."""
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, name, info):
        """Declare a name in the current (innermost) scope. Returns False if duplicate."""
        scope = self.scopes[-1]
        if name in scope:
            return False
        scope[name] = info
        return True

    def lookup(self, name):
        """Look up a name in current and outer scopes. Returns None if not found."""
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        return None


class SemanticAnalyzer:
    """Transforms CST to AST and performs static semantic checks."""
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors = []
        self.current_function = None

    def error(self, msg):
        """Record a semantic error."""
        self.errors.append(msg)

    def analyze(self, cst):
        """
        Main entry point: transform CST to AST and check semantics.
        Returns (ast, errors) tuple.
        """
        if cst is None or cst.type != 'program':
            self.error('Invalid CST root')
            return None, self.errors

        world_cst = cst.children[0]
        funcs_cst = cst.children[1]
        agent_cst = cst.children[2]

        # Phase 1: collect and register functions in global scope
        funcs = []
        func_nodes = []
        if funcs_cst:
            if funcs_cst.type == 'function_list':
                func_nodes = funcs_cst.children
            elif funcs_cst.type == 'function_list_opt' and funcs_cst.children:
                # defensive: function_list_opt might wrap the actual list
                first = funcs_cst.children[0]
                if first.type == 'function_list':
                    func_nodes = first.children

        for f in func_nodes:
            # function_decl structure: children = [param_list_opt, type_node, stmt_list], value = function name
            name = f.value
            ret_type = f.children[1].value if len(f.children) > 1 and f.children[1] is not None else 'int'
            params = self._collect_param_names(f.children[0])
            
            # Check for duplicate function declarations
            if not self.symtab.declare(name, {'kind': 'function', 'params': params, 'ret': ret_type}):
                self.error(f"Duplicate function declaration: {name}")
            funcs.append((f, name, params, ret_type))

        # Phase 2: transform world definition
        world_ast = self._transform_world(world_cst)

        # Phase 3: transform functions (bodies in function scope)
        ast_funcs = []
        for f_cst, name, params, ret_type in funcs:
            self.symtab.push()
            # Declare parameters in function scope
            for p in params:
                if not self.symtab.declare(p, {'kind': 'param', 'type': 'int'}):
                    self.error(f"Duplicate parameter name '{p}' in function {name}")
            
            self.current_function = {'name': name, 'ret': ret_type}
            # function_decl children: [param_list_opt, type_node, stmt_list]
            body_node = f_cst.children[2] if len(f_cst.children) > 2 else None
            body_stmts = self._transform_stmt_list(body_node) if body_node else []
            ast_funcs.append(FunctionDef(name, params, ret_type, body_stmts))
            self.symtab.pop()
            self.current_function = None

        # Phase 4: transform agent (agent has its own scope)
        # agent_def structure: value = agent name, children[0] = stmt_list
        agent_name = agent_cst.value
        self.symtab.push()
        agent_body = self._transform_stmt_list(agent_cst.children[0])
        self.symtab.pop()

        ast_prog = Program(world_ast, ast_funcs, AgentDef(agent_name, agent_body))
        return ast_prog, self.errors

    def _collect_param_names(self, param_list_opt):
        """Extract parameter names from param_list_opt CST node."""
        if param_list_opt is None:
            return []
        if param_list_opt.type == 'param_list_opt':
            # param_list_opt can be empty or wrap a param_list
            if not param_list_opt.children:
                return []
            first = param_list_opt.children[0]
            if first.type == 'param_list':
                return [p.value for p in first.children]
        elif param_list_opt.type == 'param_list':
            return [p.value for p in param_list_opt.children]
        return []

    def _transform_world(self, world_cst):
        """Transform world_def CST to AST."""
        # world_def structure: value = world name, children[0] = world_body
        name = world_cst.value
        body = world_cst.children[0]
        stmts = []
        
        for s in body.children:
            # Parser world statements: size_decl, entry_decl, exit_decl, obstacle_decl, dirt_decl
            if s.type == 'size_decl':
                stmts.append(ASTNode('Size', value=s.value))
            elif s.type == 'entry_decl':
                stmts.append(ASTNode('Entry', value=s.value))
            elif s.type == 'exit_decl':
                stmts.append(ASTNode('Exit', value=s.value))
            elif s.type == 'obstacle_decl':
                stmts.append(ASTNode('Obstacle', value=s.value))
            elif s.type == 'dirt_decl':
                stmts.append(ASTNode('Dirt', value=s.value))
        
        return WorldDef(name, stmts)

    def _transform_stmt_list(self, stmt_list_cst):
        """Transform stmt_list CST to list of AST statement nodes."""
        if stmt_list_cst is None:
            return []
        stmts = []
        for s in stmt_list_cst.children:
            stmts.append(self._transform_stmt(s))
        return stmts

    def _transform_stmt(self, node):
        """Transform a statement CST node to AST."""
        t = node.type
        
        if t == 'var_decl':
            # var_decl structure: value = identifier name, children[0] = expr
            name = node.value
            expr = self._transform_expr(node.children[0]) if node.children else None
            if not self.symtab.declare(name, {'kind': 'var', 'type': 'int'}):
                self.error(f"Duplicate variable declaration: {name}")
            return VarDecl(name, expr)
        
        if t == 'assign':
            # assign structure: value = identifier name, children[0] = expr
            name = node.value
            sym = self.symtab.lookup(name)
            if sym is None:
                self.error(f"Assignment to undeclared identifier: {name}")
            expr = self._transform_expr(node.children[0]) if node.children else None
            return Assign(name, expr)
        
        if t == 'if_stmt':
            # if_stmt structure: children = [condition, then_stmt_list, else_stmt_list]
            cond = self._transform_condition(node.children[0])
            then_stmts = self._transform_stmt_list(node.children[1])
            else_stmts = self._transform_stmt_list(node.children[2])
            return IfStmt(cond, then_stmts, else_stmts)
        
        if t == 'while_stmt':
            # while_stmt structure: children = [condition, stmt_list]
            cond = self._transform_condition(node.children[0])
            body_stmts = self._transform_stmt_list(node.children[1])
            return WhileStmt(cond, body_stmts)
        
        if t == 'move_stmt':
            return MoveStmt()
        
        if t == 'turn_stmt':
            # turn_stmt structure: children[0] = turn direction (left_dir or right_dir)
            dir_node = node.children[0]
            return TurnStmt(dir_node.value if hasattr(dir_node, 'value') else None)
        
        if t == 'clean_stmt':
            return CleanStmt()
        
        if t == 'backtrack_stmt':
            return BacktrackStmt()
        
        if t == 'report_stmt':
            # report_stmt structure: children[0] = expr
            expr = self._transform_expr(node.children[0]) if node.children else None
            return ReportStmt(expr)
        
        if t == 'return_stmt':
            # return_stmt structure: children[0] = expr
            if not self.current_function:
                self.error('RETURN used outside of function')
            expr = self._transform_expr(node.children[0]) if node.children else None
            # Check void function return
            if self.current_function and self.current_function.get('ret') == 'void' and expr is not None:
                self.error(f"Function {self.current_function['name']} is void but RETURN has a value")
            return ReturnStmt(expr)
        
        if t == 'call_stmt':
            # call_stmt structure: children[0] = function_call
            call = node.children[0]
            call_expr = self._transform_call(call)
            return ASTNode('CallStmt', children=[call_expr])
        
        self.error(f"Unhandled statement kind: {t}")
        return ASTNode('UnknownStmt', value=t)

    def _transform_condition(self, node):
        """Transform a condition CST node to AST."""
        t = node.type
        
        if t == 'sense_condition':
            # sense_condition structure: children[0] = sense_expr
            sense = node.children[0]
            return SenseExpr(sense.value)
        
        if t == 'not_condition':
            # not_condition structure: children[0] = condition
            return ASTNode('Not', children=[self._transform_condition(node.children[0])])
        
        if t == 'and_condition':
            # and_condition structure: children = [condition, condition]
            left = self._transform_condition(node.children[0])
            right = self._transform_condition(node.children[1])
            return ASTNode('And', children=[left, right])
        
        if t == 'or_condition':
            # or_condition structure: children = [condition, condition]
            left = self._transform_condition(node.children[0])
            right = self._transform_condition(node.children[1])
            return ASTNode('Or', children=[left, right])
        
        if t == 'relop_condition':
            # relop_condition structure: children = [expr, relop_node, expr]
            left = self._transform_expr(node.children[0])
            op_node = node.children[1]
            op = op_node.value if hasattr(op_node, 'value') else op_node.type
            right = self._transform_expr(node.children[2])
            return ASTNode('RelOp', value=op, children=[left, right])
        
        if t == 'unvisited_condition':
            return UnvisitedExpr()
        
        self.error(f"Unhandled condition kind: {t}")
        return ASTNode('UnknownCond', value=t)

    def _transform_expr(self, node):
        """Transform an expression CST node to AST."""
        if node is None:
            return None
        
        t = node.type
        
        if t == 'plus_expr' or t == 'minus_expr':
            op = '+' if t == 'plus_expr' else '-'
            left = self._transform_expr(node.children[0])
            right = self._transform_expr(node.children[1])
            return BinOp(op, left, right)
        
        if t == 'identifier':
            # identifier structure: value = identifier name
            name = node.value
            sym = self.symtab.lookup(name)
            if sym is None:
                self.error(f"Use of undeclared identifier: {name}")
            return VarRef(name)
        
        if t == 'integer_literal':
            # integer_literal structure: value = integer value
            try:
                v = int(node.value)
            except (ValueError, TypeError):
                v = node.value
            return IntLit(v)
        
        if t == 'function_call':
            return self._transform_call(node)
        
        self.error(f"Unhandled expr kind: {t}")
        return ASTNode('UnknownExpr', value=t)

    def _transform_call(self, call_cst):
        """Transform a function_call CST node to AST."""
        # function_call structure: value = function name, children[0] = arg_list_opt
        name = call_cst.value
        args_cst = call_cst.children[0] if call_cst.children else None
        args = []
        
        if args_cst and args_cst.type == 'arg_list':
            for a in args_cst.children:
                args.append(self._transform_expr(a))
        
        # Check that function is declared
        fn = self.symtab.lookup(name)
        if fn is None or fn.get('kind') != 'function':
            self.error(f"Call to undeclared function: {name}")
        else:
            # Check argument count matches parameter count
            expected = len(fn.get('params', []))
            if len(args) != expected:
                self.error(f"Function {name} called with {len(args)} args but expects {expected}")
        
        return CallExpr(name, args)


def analyze_cst(cst):
    """Convenience API: analyze a CST and return (ast, errors) tuple."""
    sa = SemanticAnalyzer()
    return sa.analyze(cst)
