# run_parser.py
from parser import parse
from semantic import analyze_cst

def run_file(path):
    cst = parse(filename=path)
    print("===== CST =====")
    print(cst)

    ast, errors = analyze_cst(cst)
    print("\n===== AST =====")
    if ast:
        print(ast)
    else:
        print("No AST produced")

    if errors:
        print("\n===== SEMANTIC ERRORS =====")
        for e in errors:
            print("- " + e)
    else:
        print("\nNo semantic errors detected.")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python run_parser.py <sourcefile>")
        sys.exit(1)
    run_file(sys.argv[1])
