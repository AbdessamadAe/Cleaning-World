# run_parser.py
from parser.parser import parse
from semantics_analyzer.semantic import analyze_cst

def run_file(path):
    cst = parse(filename=path)
    print("===== CST =====")
    print(cst)

    ast, errors = analyze_cst(cst)
    if ast:
        print("\n===== AST =====")
        print(ast)
    else:
        print("No AST produced")

    if errors:
        print("\n===== SEMANTIC ERRORS =====")
        for e in errors:
            print("- " + e)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python run_parser.py <sourcefile>")
        sys.exit(1)
    run_file(sys.argv[1])
