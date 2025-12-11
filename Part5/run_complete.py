"""
Complete execution pipeline: Lexer → Parser → Analyzer → Interpreter
Run a .cl program from source through all stages and display results.
"""

import sys
import os
import contextlib

# Add Part3&4 to path so modules can be found
part3_4_dir = os.path.join(os.path.dirname(__file__), '..', 'Part3&4')
if part3_4_dir not in sys.path:
    sys.path.insert(0, part3_4_dir)

# Now we can import from Part3&4 directly
os.chdir(part3_4_dir)  # Change to Part3&4 so parser can find lexer, etc.
from parser.parser import parse
from semantics_analyzer.semantic import analyze_cst

# Return to Part5 and import interpreter
os.chdir(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.dirname(__file__))
from interpreter import Interpreter


def run_complete_pipeline(filename, do_print=False):
    """
    Execute complete pipeline on a .cl file.
    Returns (success, cst, ast, errors, state).
    """
    if do_print:
        print("=" * 70)
        print(f"Running: {filename}")
        print("=" * 70)

    # Step 1: Parse
    if do_print:
        print("\n[1] LEXER + PARSER")
    try:
        if do_print:
            cst = parse(filename=filename)
        else:
            # suppress parser output when running silently
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                    cst = parse(filename=filename)
        if do_print:
            print("✓ Parse successful")
    except Exception as e:
        if do_print:
            print(f"✗ Parse failed: {e}")
        return False, None, None, None, None

    # Step 2: Semantic Analysis
    try:
        if do_print:
            print("\n[2] SEMANTIC ANALYZER")
        if do_print:
            ast, errors = analyze_cst(cst)
        else:
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                    ast, errors = analyze_cst(cst)
        if errors:
            if do_print:
                print(f"✗ Semantic errors ({len(errors)}):")
                for err in errors:
                    print(f"  - {err}")
            return False, cst, None, errors, None
        if do_print:
            print("✓ Semantic analysis successful")
    except Exception as e:
        if do_print:
            print(f"✗ Analysis failed: {e}")
        return False, cst, None, None, None

    # Step 3: Interpret
    try:
        if do_print:
            print("\n[3] INTERPRETER")
        interpreter = Interpreter()
        if do_print:
            state = interpreter.execute(ast)
            print("✓ Execution successful")
        else:
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                    state = interpreter.execute(ast)
    except Exception as e:
        if do_print:
            print(f"✗ Execution failed: {e}")
        return False, cst, ast, errors, None

    return True, cst, ast, errors, state


def print_results(success, cst, ast, errors, state, output_path=None, do_print=False):
    """Print execution results and optionally write them to a text file.

    If `output_path` is provided, the same output printed to the terminal
    will be written to that file.
    """
    lines = []
    if not success:
        lines.append("\n⚠ Execution did not complete successfully.")
        text = "\n".join(lines)
        print(text)
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as fh:
                fh.write(text)
        return

    lines.append("\n" + "=" * 70)
    lines.append("EXECUTION RESULTS")
    lines.append("=" * 70)

    if state:
        lines.append("")
        lines.append("Agent State:")
        lines.append(f"  Position: ({state.agent_x}, {state.agent_y})")
        lines.append(f"  Direction: {state.agent_dir}")
        lines.append(f"  Dirt cleaned: {state.cleaned_dirt}")

        if state.outputs:
            lines.append("")
            lines.append("Output/Actions:")
            for i, output in enumerate(state.outputs, 1):
                lines.append(f"  {i}. {output}")
        else:
            lines.append("")
            lines.append("No outputs recorded.")

    text = "\n".join(lines)
    if do_print:
        print(text)

    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as fh:
                fh.write(text)
        except Exception as e:
            print(f"Could not write output file {output_path}: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_complete.py [--print] <program.cl>")
        print("\nAvailable test programs:")
        prog_dir = os.path.join(os.path.dirname(__file__), 'programs')
        if os.path.exists(prog_dir):
            for f in sorted(os.listdir(prog_dir)):
                if f.endswith('.cl'):
                    print(f"  python run_complete.py programs/{f}")
        sys.exit(1)

    # Simple arg parsing: allow optional --print flag
    args = sys.argv[1:]
    do_print = False
    if '--print' in args:
        do_print = True
        args.remove('--print')
    if not args:
        print("Error: no filename provided")
        sys.exit(1)
    filename = args[0]
    if not os.path.exists(filename):
        print(f"Error: File not found: {filename}")
        sys.exit(1)

    # Prepare output directory and output filename
    out_dir = os.path.join(os.path.dirname(__file__), 'output')
    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception:
        pass
    base = os.path.basename(filename)
    out_name = os.path.splitext(base)[0] + '_output.txt'
    out_path = os.path.join(out_dir, out_name)

    success, cst, ast, errors, state = run_complete_pipeline(filename, do_print=do_print)
    print_results(success, cst, ast, errors, state, output_path=out_path, do_print=do_print)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
