Cleaning-World Compiler Project

Languages and Compilers – Final Project (Parts 1–5)

Overview

This repository contains the complete implementation of the Cleaning-World language and its execution pipeline, developed as a semester-long project for the Languages and Compilers course at AUI.

The project implements all major phases of a compiler, from language design and lexical analysis to execution via direct interpretation. The language allows users to define a grid-based world and program an agent using variables, control structures, functions, and built-in robot actions.

Project Parts

The project is structured according to the five required deliveries:

Part 1 – Language Design

Definition of the Cleaning-World language

Lexeme specification table (lexeme, regex, token, additional info)

Grammar specification (BNF/EBNF)

Sample programs covering the language constructs

Part 2 – Lexical Analyzer

Lexer implemented using PLY (Python Lex)

Tokenization of keywords, identifiers, literals, operators, punctuation

Symbol table initialization and identifier handling

Lexer output generated for sample programs

Part 3 – Parser

Parser implemented using PLY Yacc (LALR(1))

Grammar implementation based on the language design

Concrete Syntax Tree (CST) generation

CSTs written to files for each test program

Part 4 – Static Semantics Analyzer

Declaration-before-use checks

Duplicate declaration detection

Function argument validation

Conversion from CST to Abstract Syntax Tree (AST)

Readable ASTs generated for each test program

Part 5 – Execution via Direct Interpretation

Direct interpretation of the AST (no code generation)

Stack-based execution for function calls

Unified execution pipeline connecting all phases

Runtime output written to files and optionally printed

Repository Structure
Cleaning-World-main/
│
├── Part1&2/
│   ├── design-table.txt          # Lexeme specification table
│   ├── BNF.txt                   # Grammar specification
│   ├── lexer/
│   │   ├── lexer.py
│   │   └── tokens.py
│   └── programs/                # Sample programs for Parts 1 & 2
│
├── Part3&4/
│   ├── parser/
│   │   └── parser.py
│   ├── semantics_analyzer/
│   │   ├── semantic.py
│   │   └── ast_nodes.py
│   ├── CSTs/                     # Generated CST files
│   ├── ASTs/                     # Generated AST files
│   └── programs/                # Test programs for Parts 3 & 4
│
├── Part5/
│   ├── run_complete.py           # Full pipeline: parse → analyze → execute
│   ├── interpreter.py            # AST interpreter
│   ├── programs/                # Final test programs
│   └── output/                  # Execution results
│
├── Final_Report.pdf              # Final written report
└── README.md

How the System Works (High-Level)

Lexical Analysis
The lexer converts source code into a token stream using regular expressions.

Parsing
The parser validates syntax and produces a Concrete Syntax Tree (CST).

Static Semantic Analysis
The CST is checked for semantic correctness and transformed into an AST.

Interpretation
The AST is executed directly by the interpreter using a stack-based model.

All phases are connected by the script Part5/run_complete.py.

Requirements

Python 3.x

ply (Python Lex-Yacc)

Install dependencies:

pip install ply

Running the Project

From the repository root:

python Part5/run_complete.py --print Part5/programs/test_loops.cl


To run silently (output written to file only):

python Part5/run_complete.py Part5/programs/test_loops.cl


Execution results are written to:

Part5/output/<program_name>_output.txt

Example Programs (Part 5)

The following programs are provided in Part5/programs/:

test_conditionals.cl – tests relational and boolean expressions

test_loops.cl – tests looping and variable updates

test_functions.cl – tests function definitions and calls

These programs collectively exercise all major language constructs.

Design Choices (Summary)

Single-file programs to avoid unnecessary file-handling complexity

Direct world initialization inside the language

Iteration instead of recursion for loops

Functions with pass-by-value parameters and simple return types

LALR(1) parsing using PLY to avoid LL(1) grammar constraints

Direct AST interpretation instead of code generation to reduce complexity

These choices prioritize simplicity, correctness, and full integration of all compiler phases.

Documentation

Full design rationale, feedback incorporation, and detailed explanations are available in Final_Report.pdf

CST and AST files are provided for all test programs

Lexer and parser coverage is documented using line-based testing tables in the report

Final Notes

This repository represents the final integrated submission (Parts 1–5) of the Cleaning-World project.
All components are functional, connected, and tested end-to-end.