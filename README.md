Mini Lisp Compiler
===

### How the code works

1. **Lexer (PLY's Lex Module)**:  
   - Defines tokens for the Lisp-like language.  
   - Implements rules for recognizing identifiers, numbers, booleans, operators (`+`, `-`, `*`, `/`, `mod`), logical operators (`and`, `or`, `not`), and control flow keywords (`if`, `define`, `fun`).  
   - Reserved keywords (`print-num`, `print-bool`) are explicitly defined to avoid conflicts with identifiers.  
   - Ignores whitespace and handles illegal characters gracefully.  

2. **Parser (PLY's Yacc Module)**:  
   - The grammar rules are defined to parse expressions, statements, and entire programs.  
   - Produces an Abstract Syntax Tree (AST) using Python's built-in `ast` module for syntax trees.  
   - Supports arithmetic operations, logic operations, conditional expressions, function definitions, function calls, variable assignments, and print statements.  

3. **AST Generation**:  
   - The parser constructs an AST for the input Lisp-like code. Each rule transforms parsed tokens into corresponding AST nodes, such as `ast.BinOp` for binary operations, `ast.IfExp` for conditional expressions, and `ast.Lambda` for function definitions.  

4. **Code Execution**:  
   - The AST is compiled using Python's `compile` function and executed using the `exec` function in a sandboxed environment.  

5. **Error Handling**:  
   - Syntax errors during parsing are raised as `SyntaxError`.  
   - Runtime errors during execution are caught and displayed to the user.  

### Usage
To run the program:  
1. Save it to a file, e.g., `mini_lisp.py`.  
2. Prepare a `.lsp` file containing the Lisp-like code.  
3. Execute it as follows:  
   ```bash
   python3 mini_lisp.py <filename>.lsp
   
   ```

To run many files:  
Run the `autorun.py`  
```bash
python3 autorun.py <filename>.py
```
