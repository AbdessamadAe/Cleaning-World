from parser.parser import parse
from semantics_analyzer.semantic import analyze_cst
import os

def run_file(path):
    cst = parse(filename=path)
    print("===== CST =====")
    print(cst)

    ast, errors = analyze_cst(cst)
    if ast:
        print("\n===== AST =====")
        print(ast)
        
        # Write AST to file
        filename = os.path.basename(path)
        name_without_ext = os.path.splitext(filename)[0]
        asts_dir = os.path.join(os.path.dirname(__file__), 'ASTs')
        os.makedirs(asts_dir, exist_ok=True)
        ast_filepath = os.path.join(asts_dir, f"{name_without_ext}_ast.txt")
        with open(ast_filepath, 'w') as f:
            f.write(str(ast))
        print(f"\nAST written to: {ast_filepath}")
    else:
        print("No AST produced")

    if errors:
        print("\n===== SEMANTIC ERRORS =====")
        for e in errors:
            print("- " + e)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Please provide the program file path, e.g. `python parser.py ../programs/program1.cl`")
        print("Available test programs:")
        test_dir = "./programs"
        if os.path.exists(test_dir):
            for file in sorted(os.listdir(test_dir)):
                if file.endswith('.cl'):
                    print(f"  {os.path.join(test_dir, file)}")

        sys.exit(1)

    run_file(sys.argv[1])
