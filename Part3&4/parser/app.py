# run_parser.py
from parser import parse

def run_file(path):
    cst = parse(filename=path)
    print("===== CST =====")
    print(cst)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python run_parser.py <sourcefile>")
        sys.exit(1)
    run_file(sys.argv[1])
