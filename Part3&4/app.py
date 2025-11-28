from parser.parser import parse
import os
# from semantics_analyzer.semantic import analyze_cst

def run_file(path):
    cst = parse(filename=path)
    print("===== CST =====")
    print(cst)

    # I commented the analyzer to avoid errs while testing the parser
    # the analyzer should be changed to output to the ASTs foolder.
    """
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
    """

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
