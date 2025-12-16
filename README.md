# Cleaning-World Compiler Project

## Languages and Compilers – Final Project (Parts 1–5)

---

## 📘 Overview

This repository contains the complete implementation of the **Cleaning-World programming language** and its execution pipeline, developed as a semester-long project for the **Languages and Compilers** course at **Al Akhawayn University (AUI)**.

The project implements all major phases of a compiler, from **language design** and **lexical analysis** to **parsing**, **static semantic analysis**, and **execution via direct interpretation**.

The Cleaning-World language allows users to:
- Define a grid-based world
- Program an autonomous cleaning agent
- Use variables, control structures, and functions
- Execute built-in robot actions

All components are fully integrated and tested end-to-end.

---

## ⚙️ How the System Works (High-Level Compiler Pipeline)

The system processes source code through a standard compiler pipeline:

1. **Lexical Analysis**  
   The lexer converts source code into a stream of tokens using regular expressions.

2. **Parsing**  
   The parser validates syntax and produces a **Concrete Syntax Tree (CST)**.

3. **Static Semantic Analysis**  
   The CST is checked for semantic correctness and transformed into an **Abstract Syntax Tree (AST)**.

4. **Interpretation**  
   The AST is executed directly by the interpreter using a stack-based execution model.

All phases are connected and executed by the script:


---

## 🧩 Project Parts and Deliverables

The project is structured according to the five required deliveries.

### **Part 1 – Language Design**
- Definition of the Cleaning-World language
- Lexeme specification table (`design-table.txt`)
- Grammar specification (`BNF.txt`)
- Sample programs covering all language constructs

### **Part 2 – Lexical Analyzer**
- Lexer implemented using **PLY (Python Lex)**
- Tokenization of keywords, identifiers, literals, operators, and punctuation
- Symbol table initialization and identifier handling
- Lexer output generated for sample programs

### **Part 3 – Parser**
- Parser implemented using **PLY Yacc (LALR(1))**
- Grammar implementation based on the language design
- **Concrete Syntax Tree (CST)** generation
- CSTs written to files for each test program

### **Part 4 – Static Semantics Analyzer**
- Declaration-before-use checks
- Duplicate declaration detection
- Function argument validation
- Conversion from CST to **Abstract Syntax Tree (AST)**
- Readable ASTs generated for all test programs

### **Part 5 – Execution via Direct Interpretation**
- Direct interpretation of the AST (no code generation)
- Stack-based execution for function calls
- Unified execution pipeline connecting all phases
- Runtime output written to files and optionally printed

---

## 📂 Repository Structure

Cleaning-World-main/
│
├── Part1&2/
│   ├── design-table.txt          # Lexeme specification table
│   ├── BNF.txt                   # Grammar specification
│   ├── lexer/
│   │   ├── lexer.py
│   │   └── tokens.py
│   └── programs/                # Sample programs (Parts 1 & 2)
│
├── Part3&4/
│   ├── parser/
│   │   └── parser.py
│   ├── semantics_analyzer/
│   │   ├── semantic.py
│   │   └── ast_nodes.py
│   ├── CSTs/                     # Generated CST files
│   ├── ASTs/                     # Generated AST files
│   └── programs/                # Test programs (Parts 3 & 4)
│
├── Part5/
│   ├── run_complete.py           # Full pipeline: parse → analyze → execute
│   ├── interpreter.py            # AST interpreter
│   ├── programs/                # Final test programs
│   └── output/                  # Execution results
│
├── Final_Report.pdf              # Final written report
└── README.md

---
### 💻 Requirements & Running the Project

The project requires Python 3.x and the `ply` library.

#### **Installation**

Install dependencies using pip:

```bash
pip install ply
Running the Project
Execute the run_complete.py script from the repository root, providing the program file path.

Run with console output (Recommended):

Bash

python Part5/run_complete.py --print Part5/programs/test_loops.cl
Run silently (output written to file only):

Bash

python Part5/run_complete.py Part5/programs/test_loops.cl
Output location

Execution results are written to: Part5/output/<program_name>_output.txt

🧪 Example Programs (Part 5)
The following programs are provided in Part5/programs/ and collectively exercise all major language features:

test_conditionals.cl: Tests relational and boolean expressions.

test_loops.cl: Tests looping constructs and variable updates.

test_functions.cl: Tests function definitions and calls.

🎯 Design Choices (Summary)
The following choices were made to prioritize simplicity, correctness, and full integration of all compiler phases:

Single-file programs to avoid unnecessary file-handling complexity.

World initialization handled directly inside the language.

Iterative constructs instead of recursion for loops.

Functions with pass-by-value parameters and simple return types.

LALR(1) parsing using PLY to avoid LL(1) grammar constraints.

Direct AST interpretation instead of code generation to reduce complexity.

📄 Documentation
Full design rationale and explanations are available in Final_Report.pdf.

CST and AST files are generated for all test programs.

Lexer and parser coverage is documented in the report.

✅ Final Notes
This repository represents the final integrated submission (Parts 1–5) of the Cleaning-World compiler project. All components are fully implemented, correctly connected, and tested end-to-end.