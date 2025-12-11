"""
AST Interpreter for Cleaning-World Language
Executes AST trees with function calls, control flow, and variable scoping.
"""

class ReturnValue(Exception):
    """Control flow exception for RETURN statements."""
    def __init__(self, value):
        self.value = value


class BreakException(Exception):
    """Control flow exception for breaking out of loops (not used yet, for future)."""
    pass


class InterpreterState:
    """Tracks world state during interpretation."""
    def __init__(self):
        self.visited = set()  # set of (x, y) visited locations
        self.cleaned_dirt = 0  # count of dirt cleaned
        self.agent_x, self.agent_y = None, None  # agent position
        self.agent_dir = None  # agent direction (N, E, S, W)
        self.outputs = []  # collected REPORT outputs


class CallFrame:
    """Represents a function call's local scope."""
    def __init__(self, func_name, locals_dict):
        self.func_name = func_name
        self.locals = locals_dict  # {var_name: value}


class Interpreter:
    """
    Tree-walking interpreter for Cleaning-World AST.
    Supports:
    - Variables with scoping (global, function local, agent local)
    - Function definitions and calls with parameters
    - Control flow (IF, WHILE, RETURN)
    - Built-in actions (MOVE, TURN, CLEAN, BACKTRACK, REPORT)
    - Arithmetic and boolean expressions
    - Sensing conditions (SENSE, UNVISITED, relational operators, AND/OR)
    """

    def __init__(self):
        self.global_vars = {}  # global variables
        self.functions = {}  # {func_name: (params, ret_type, body_ast)}
        self.call_stack = []  # CallFrame list; call_stack[0] is outermost (global)
        self.state = InterpreterState()
        self.return_value = None
        self.should_return = False
        # Basic world model stored on the interpreter/state
        # width/height are 1-based coordinates matching source programs
        self.state.width = None
        self.state.height = None
        self.state.dirt = set()        # set of (x,y) positions with dirt
        self.state.obstacles = set()   # set of (x,y) obstacle positions
        self.state.entry = None        # (x,y)
        self.state.exit = None         # (x,y)
        # history of positions for BACKTRACK
        self.state.history = []

    def execute(self, ast):
        """
        Main entry point. Execute the program AST.
        Returns the interpreter state (outputs, visited, cleaned_dirt, etc).
        """
        if ast.kind != 'Program':
            raise RuntimeError(f"Expected Program, got {ast.kind}")

        # Initialize global scope (empty frame)
        self.call_stack = [CallFrame('__global__', self.global_vars)]

        # Extract world, functions, agent from Program
        world = ast.children[0] if len(ast.children) > 0 else None
        functions_node = ast.children[1] if len(ast.children) > 1 else None
        agent = ast.children[2] if len(ast.children) > 2 else None

        # Phase 1: Initialize world
        if world:
            self._init_world(world)

        # Phase 2: Register functions (don't execute yet)
        if functions_node and functions_node.children:
            for func_node in functions_node.children:
                self._register_function(func_node)

        # Phase 3: Execute agent
        if agent:
            self._execute_agent(agent)

        return self.state

    def _init_world(self, world_ast):
        """Extract world dimensions and initial state."""
        if world_ast.kind != 'WorldDef':
            return

        # Extract size, entry, exit, dirt, obstacles from world_ast.children
        for child in world_ast.children:
            if child.kind == 'Size':
                # Size: (width, height)
                if isinstance(child.value, tuple) and len(child.value) >= 2:
                    self.state.width, self.state.height = child.value[0], child.value[1]
            elif child.kind == 'Entry':
                # Entry: (x, y, direction)
                if isinstance(child.value, tuple) and len(child.value) >= 3:
                    self.state.agent_x, self.state.agent_y, dir_str = child.value[0], child.value[1], child.value[2]
                    self.state.agent_dir = dir_str
                    self.state.entry = (self.state.agent_x, self.state.agent_y)
                    # mark visited and history
                    self.state.visited.add((self.state.agent_x, self.state.agent_y))
                    self.state.history.append((self.state.agent_x, self.state.agent_y))
            elif child.kind == 'Exit':
                if isinstance(child.value, tuple) and len(child.value) >= 2:
                    self.state.exit = (child.value[0], child.value[1])
            elif child.kind == 'Dirt':
                # Dirt: value may be a single tuple or list of tuples
                if child.value:
                    if isinstance(child.value, list):
                        for v in child.value:
                            if isinstance(v, tuple) and len(v) >= 2:
                                self.state.dirt.add((v[0], v[1]))
                    elif isinstance(child.value, tuple) and len(child.value) >= 2:
                        self.state.dirt.add((child.value[0], child.value[1]))
            elif child.kind == 'Obstacle':
                if child.value:
                    if isinstance(child.value, list):
                        for v in child.value:
                            if isinstance(v, tuple) and len(v) >= 2:
                                self.state.obstacles.add((v[0], v[1]))
                    elif isinstance(child.value, tuple) and len(child.value) >= 2:
                        self.state.obstacles.add((child.value[0], child.value[1]))

        # Ensure agent has sensible defaults if ENTRY was not provided
        if self.state.agent_x is None or self.state.agent_y is None or self.state.agent_dir is None:
            # default starting position (1,1) facing North
            self.state.agent_x = 1
            self.state.agent_y = 1
            if self.state.agent_dir is None:
                self.state.agent_dir = 'N'
            # mark visited/history for default
            self.state.visited.add((self.state.agent_x, self.state.agent_y))
            self.state.history.append((self.state.agent_x, self.state.agent_y))

    def _register_function(self, func_node):
        """Register a function definition without executing it."""
        if func_node.kind != 'Function':
            return

        func_name = func_node.value
        params = []
        ret_type = 'void'
        body = None

        # Extract params, return type, body from function node structure
        for child in func_node.children:
            if child.kind == 'Params':
                # Extract parameter names
                for param_node in child.children:
                    if param_node.kind == 'Param':
                        params.append(param_node.value)
            elif child.kind == 'RetType':
                ret_type = child.value if child.value else 'void'
            elif child.kind == 'Body':
                body = child.children

        self.functions[func_name] = (params, ret_type, body)

    def _execute_agent(self, agent_ast):
        """Execute the agent's statement list."""
        if agent_ast.kind != 'Agent':
            return

        # Agent body is in agent_ast.children
        for stmt in agent_ast.children:
            self._execute_stmt(stmt)
            if self.should_return:
                break

    def _execute_stmt(self, stmt):
        """Dispatch statement execution."""
        if not stmt:
            return

        kind = stmt.kind

        if kind == 'VarDecl':
            self._execute_var_decl(stmt)
        elif kind == 'Assign':
            self._execute_assign(stmt)
        elif kind == 'If':
            self._execute_if(stmt)
        elif kind == 'While':
            self._execute_while(stmt)
        elif kind == 'Move':
            self._execute_move(stmt)
        elif kind == 'Turn':
            self._execute_turn(stmt)
        elif kind == 'Clean':
            self._execute_clean(stmt)
        elif kind == 'Backtrack':
            self._execute_backtrack(stmt)
        elif kind == 'Report':
            self._execute_report(stmt)
        elif kind == 'Return':
            self._execute_return(stmt)
        elif kind == 'Call':
            self._eval_call(stmt)
        # else: unknown statement, ignore

    def _execute_var_decl(self, stmt):
        """VarDecl: name (variable name), children[0] is init expression."""
        var_name = stmt.value
        init_val = 0
        if stmt.children:
            init_val = self._eval_expr(stmt.children[0])
        self._set_var(var_name, init_val)

    def _execute_assign(self, stmt):
        """Assign: name (variable), children[0] is expression."""
        var_name = stmt.value
        value = self._eval_expr(stmt.children[0])
        self._set_var(var_name, value)

    def _execute_if(self, stmt):
        """If: children=[condition, Then, Else]."""
        if len(stmt.children) < 3:
            return

        cond_node = stmt.children[0]
        then_node = stmt.children[1]
        else_node = stmt.children[2]

        cond_val = self._eval_condition(cond_node)

        if cond_val:
            # Execute then branch
            if then_node.kind == 'Then' and then_node.children:
                for s in then_node.children:
                    self._execute_stmt(s)
                    if self.should_return:
                        break
        else:
            # Execute else branch
            if else_node.kind == 'Else' and else_node.children:
                for s in else_node.children:
                    self._execute_stmt(s)
                    if self.should_return:
                        break

    def _execute_while(self, stmt):
        """While: children=[condition, Body]."""
        if len(stmt.children) < 2:
            return

        cond_node = stmt.children[0]
        body_node = stmt.children[1]

        while self._eval_condition(cond_node):
            if body_node.kind == 'Body' and body_node.children:
                for s in body_node.children:
                    self._execute_stmt(s)
                    if self.should_return:
                        return
            else:
                break

    def _execute_move(self, stmt):
        """Mock MOVE action."""
        # compute proposed new position based on current direction
        dir_map = {
            'N': (0, -1),
            'E': (1, 0),
            'S': (0, 1),
            'W': (-1, 0),
        }
        dx, dy = dir_map.get(self.state.agent_dir, (0, 0))
        new_x = self.state.agent_x + dx
        new_y = self.state.agent_y + dy

        # Check bounds if known
        if self.state.width is not None and self.state.height is not None:
            if not (1 <= new_x <= self.state.width and 1 <= new_y <= self.state.height):
                self.state.outputs.append(f"[MOVE] Blocked - out of bounds at ({new_x},{new_y})")
                return

        # Check obstacles
        if (new_x, new_y) in self.state.obstacles:
            self.state.outputs.append(f"[MOVE] Blocked by obstacle at ({new_x},{new_y})")
            return

        # perform move
        self.state.agent_x = new_x
        self.state.agent_y = new_y
        self.state.visited.add((new_x, new_y))
        self.state.history.append((new_x, new_y))
        self.state.outputs.append(f"[MOVE] Agent moved to ({new_x},{new_y}) facing {self.state.agent_dir}")

    def _execute_turn(self, stmt):
        """Turn: value is LEFT or RIGHT."""
        direction = stmt.value  # LEFT or RIGHT
        dirs = ['N', 'E', 'S', 'W']
        if self.state.agent_dir in dirs:
            idx = dirs.index(self.state.agent_dir)
            if direction == 'LEFT':
                idx = (idx - 1) % 4
            else:  # RIGHT
                idx = (idx + 1) % 4
            self.state.agent_dir = dirs[idx]
        self.state.outputs.append(f"[TURN {direction}] Now facing {self.state.agent_dir}")

    def _execute_clean(self, stmt):
        """Mock CLEAN action."""
        pos = (self.state.agent_x, self.state.agent_y)
        if pos in self.state.dirt:
            self.state.dirt.remove(pos)
            self.state.cleaned_dirt += 1
            self.state.outputs.append(f"[CLEAN] Dirt cleaned at {pos}. Total: {self.state.cleaned_dirt}")
        else:
            self.state.outputs.append(f"[CLEAN] No dirt at {pos}")

    def _execute_backtrack(self, stmt):
        """Mock BACKTRACK action."""
        if len(self.state.history) <= 1:
            self.state.outputs.append("[BACKTRACK] No previous position to backtrack to")
            return
        # pop current position
        self.state.history.pop()
        prev = self.state.history[-1]
        self.state.agent_x, self.state.agent_y = prev[0], prev[1]
        self.state.outputs.append(f"[BACKTRACK] Agent backtracked to ({self.state.agent_x},{self.state.agent_y})")

    def _execute_report(self, stmt):
        """Report: children[0] is expression to report."""
        if stmt.children:
            val = self._eval_expr(stmt.children[0])
            self.state.outputs.append(f"[REPORT] {val}")

    def _execute_return(self, stmt):
        """Return: children[0] is expression (may be None for void)."""
        # Evaluate return expression (if any) and raise a ReturnValue
        value = None
        if stmt.children:
            value = self._eval_expr(stmt.children[0])
        raise ReturnValue(value)

    def _eval_expr(self, expr):
        """Evaluate an expression and return its value."""
        if not expr:
            return 0

        kind = expr.kind

        if kind == 'Int':
            return expr.value
        elif kind == 'Var':
            return self._get_var(expr.value)
        elif kind == 'BinOp':
            return self._eval_binop(expr)
        elif kind == 'Call':
            return self._eval_call(expr)
        elif kind == 'Sense':
            return self._eval_sense(expr)
        elif kind == 'Unvisited':
            # True if current agent cell has not been visited yet
            pos = (self.state.agent_x, self.state.agent_y)
            return 1 if pos not in self.state.visited else 0
        else:
            return 0

    def _eval_binop(self, expr):
        """BinOp: value is operator, children are [left, right]."""
        op = expr.value
        left = self._eval_expr(expr.children[0]) if len(expr.children) > 0 else 0
        right = self._eval_expr(expr.children[1]) if len(expr.children) > 1 else 0

        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left // right if right != 0 else 0
        else:
            return 0

    def _eval_condition(self, cond):
        """Evaluate a condition node and return boolean."""
        if not cond:
            return False

        kind = cond.kind

        if kind == 'Sense':
            return self._eval_sense(cond)
        elif kind == 'Unvisited':
            pos = (self.state.agent_x, self.state.agent_y)
            return pos not in self.state.visited
        elif kind == 'And':
            left = self._eval_condition(cond.children[0]) if len(cond.children) > 0 else False
            right = self._eval_condition(cond.children[1]) if len(cond.children) > 1 else False
            return left and right
        elif kind == 'Or':
            left = self._eval_condition(cond.children[0]) if len(cond.children) > 0 else False
            right = self._eval_condition(cond.children[1]) if len(cond.children) > 1 else False
            return left or right
        elif kind == 'RelOp':
            return self._eval_relop(cond)
        elif kind == 'Not':
            return not self._eval_condition(cond.children[0]) if cond.children else False
        else:
            return False

    def _eval_relop(self, cond):
        """RelOp: value is operator (LT, GT, EQ, NEQ), children are [left_expr, right_expr]."""
        op = cond.value
        left = self._eval_expr(cond.children[0]) if len(cond.children) > 0 else 0
        right = self._eval_expr(cond.children[1]) if len(cond.children) > 1 else 0

        if op == 'LT':
            return left < right
        elif op == 'GT':
            return left > right
        elif op == 'EQ':
            return left == right
        elif op == 'NEQ':
            return left != right
        else:
            return False

    def _eval_sense(self, sense):
        """Sense: value is sense type (DIRT, OBSTACLE, ENTRY, EXIT), mocked."""
        sense_type = sense.value
        st = sense_type.upper() if isinstance(sense_type, str) else sense_type
        pos = (self.state.agent_x, self.state.agent_y)
        if st == 'DIRT':
            return 1 if pos in self.state.dirt else 0
        if st == 'ENTRY':
            return 1 if self.state.entry == pos else 0
        if st == 'EXIT':
            return 1 if self.state.exit == pos else 0
        if st == 'OBSTACLE':
            # check cell in front of agent
            dir_map = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
            dx, dy = dir_map.get(self.state.agent_dir, (0, 0))
            check = (self.state.agent_x + dx, self.state.agent_y + dy)
            return 1 if check in self.state.obstacles else 0
        return 0

    def _eval_call(self, call):
        """Call: value is function name, children are argument expressions."""
        func_name = call.value

        if func_name not in self.functions:
            raise RuntimeError(f"Undefined function: {func_name}")

        params, ret_type, body = self.functions[func_name]

        # Evaluate arguments
        args = []
        for arg_expr in call.children:
            args.append(self._eval_expr(arg_expr))

        if len(args) != len(params):
            raise RuntimeError(f"Function {func_name} expects {len(params)} args, got {len(args)}")

        # Create function frame with parameters bound to arguments
        local_scope = {}
        for param_name, arg_val in zip(params, args):
            local_scope[param_name] = arg_val

        # Push function frame
        self.call_stack.append(CallFrame(func_name, local_scope))

        # Execute function body and catch ReturnValue to get return expression
        result = 0
        try:
            if body:
                for stmt in body:
                    self._execute_stmt(stmt)
        except ReturnValue as rv:
            result = rv.value if rv.value is not None else 0

        # Pop function frame
        self.call_stack.pop()

        return result

    def _get_var(self, name):
        """Look up a variable in current scope (innermost to outermost)."""
        for frame in reversed(self.call_stack):
            if name in frame.locals:
                return frame.locals[name]
        # If not found, return default 0 to avoid crashing on implicitly-used vars
        return 0

    def _set_var(self, name, value):
        """Set a variable in the current innermost scope."""
        # If the variable exists in any enclosing frame, set it there (nearest)
        for frame in reversed(self.call_stack):
            if name in frame.locals:
                frame.locals[name] = value
                return
        # Otherwise set in the innermost scope (current frame) or global
        if self.call_stack:
            self.call_stack[-1].locals[name] = value
        else:
            self.global_vars[name] = value
