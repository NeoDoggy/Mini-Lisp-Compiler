import ply.lex as lex
import ply.yacc as yacc
import sys
import re
import os
import subprocess
import ast

# Token list for ply
tokens = (
    'ID','NUM','BOOL',
    'ADD','SUB','MUL','DIV','MOD',
    'LPAREN','RPAREN',
    'GREATER','SMALLER','EQUAL',
    'AND','OR','NOT',
    'IF','DEF','FUNC',
    'PRINTNUM','PRINTBOOL'
)

# reserved words to avoid conflicts
reserved_words = {
    'mod': 'MOD',
    'and': 'AND','or': 'OR','not': 'NOT',
    'if': 'IF','define': 'DEF','fun': 'FUNC',
    'print-num': 'PRINTNUM','print-bool': 'PRINTBOOL' 
}

# Simple tokens
t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_DIV = r'/'
t_MOD = r'mod'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_GREATER = r'>'
t_SMALLER = r'<'
t_EQUAL = r'='
t_AND = r'and'
t_OR = r'or'
t_NOT = r'not'
t_IF = r'if'
t_DEF = r'DEF'
t_PRINTNUM = r'print-num'
t_PRINTBOOL = r'print-bool'
t_FUNC = r'fun'

# DEF tokens with values
def t_NUM(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_BOOL(t):
    r'\#t|\#f'
    t.value = True if t.value == '#t' else False
    return t

def t_ID(t):
    r'[a-z_][a-z0-9_-]*'
    t.type = reserved_words.get(t.value, 'ID')
    return t

# ignore spaces, tabs, and newlines
t_ignore = ' \t\n'

# Error handling rule
def t_error(t):
    print(f"Illegal character at line {t.lineno} near '{t.value[0]}'")
    t.lexer.skip(1)

# LEX
lexer = lex.lex()


# PARSER start

start = 'PROGRAM'

def p_program(p):
    '''PROGRAM : STMTS
    '''
    p[0] = ast.Module(body=p[1], type_ignores=[])

def p_stmts(p):
    '''STMTS : STMT
        | STMT STMTS
    '''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_stmt(p):
    '''STMT : EXPR
        | PRINT_STMT
        | DEFINE_STMT
    '''
    if isinstance(p[1], ast.expr):
        p[0] = ast.Expr(value=p[1], lineno=p.lineno(1), col_offset=0)
    else:
        p[0] = p[1]

def p_expr(p):
    '''EXPR : NUM
        | BOOL
        | ID
        | NUMOP
        | LOGICOP
        | FUNCEXPR
        | FUNCALL
        | IFEXPR
    '''
    if isinstance(p[1], (int, bool)):
        p[0] = ast.Constant(value=p[1], lineno=p.lineno(1), col_offset=0)
    elif isinstance(p[1], str):
        p[0] = ast.Name(id=p[1], ctx=ast.Load(), lineno=p.lineno(1), col_offset=0)
    elif isinstance(p[1], ast.expr):
        p[0] = p[1]
    else:
        raise TypeError(f"Type error at line {p.lineno(1)}")

def p_num_operations(p):
    '''NUMOP : LPAREN ADD EXPR EXPRS RPAREN
        | LPAREN SUB EXPR EXPR RPAREN
        | LPAREN MUL EXPR EXPRS RPAREN
        | LPAREN DIV EXPR EXPR RPAREN
        | LPAREN MOD EXPR EXPR RPAREN
        | LPAREN GREATER EXPR EXPR RPAREN
        | LPAREN SMALLER EXPR EXPR RPAREN
        | LPAREN EQUAL EXPR EXPR RPAREN
    '''
    if p[2] == '+':
        left = p[3]
        for i in p[4]:
            left = ast.BinOp(left=left,
                             op=ast.Add(),
                             right=i,
                             lineno=p.lineno(2),
                             col_offset=0)
        p[0] = left
    elif p[2] == '-':
        left = p[3]
        left = ast.BinOp(left=left,
                            op=ast.Sub(),
                            right=p[4],
                            lineno=p.lineno(2),
                            col_offset=0)
        p[0] = left
    elif p[2] == '*':
        left = p[3]
        for i in p[4]:
            left = ast.BinOp(left=left,
                             op=ast.Mult(),
                             right=i,
                             lineno=p.lineno(2),
                             col_offset=0)
        p[0] = left
    elif p[2] == '/':
        left = p[3]
        left = ast.Call(
            func=ast.Name(id='int', ctx=ast.Load(), lineno=p.lineno(2), col_offset=0),
            args=[ast.BinOp(left=left,
                            op=ast.FloorDiv(),
                            right=p[4],
                            lineno=p.lineno(2),
                            col_offset=0)
                ],
            keywords=[],
            lineno=p.lineno(2),
            col_offset=0
        )
        p[0] = left
    elif p[2] == '>':
        p[0] = ast.Compare(left=p[3],
                           ops=[ast.Gt()],
                           comparators=[p[4]],
                           lineno=p.lineno(2),
                           col_offset=0)
    elif p[2] == '<':
        p[0] = ast.Compare(left=p[3],
                           ops=[ast.Lt()],
                           comparators=[p[4]],
                           lineno=p.lineno(2),
                           col_offset=0)
    elif p[2] == '=':
        p[0] = ast.Compare(left=p[3],
                           ops=[ast.Eq()],
                           comparators=[p[4]],
                           lineno=p.lineno(2),
                           col_offset=0)
    else: # mod
        p[0] = ast.BinOp(left=p[3],
                         op=ast.Mod(),
                         right=p[4],
                         lineno=p.lineno(2),
                         col_offset=0)

def p_logical_op(p):
    '''LOGICOP : LPAREN AND EXPR EXPRS RPAREN 
        | LPAREN OR EXPR EXPRS RPAREN
        | LPAREN NOT EXPR RPAREN
    '''
    if p[2] == 'and':
        left = p[3]
        for i in p[4]:
            left = ast.BoolOp(op=ast.And(),
                              values=[left, i],
                              lineno=p.lineno(2),
                              col_offset=0)
        p[0] = left
    elif p[2] == 'or':
        left = p[3]
        for i in p[4]:
            left = ast.BoolOp(op=ast.Or(),
                              values=[left, i],
                              lineno=p.lineno(2),
                              col_offset=0)
        p[0] = left
    else: # not
        p[0] = ast.UnaryOp(op=ast.Not(),
                           operand=p[3],
                           lineno=p.lineno(2),
                           col_offset=0)

def p_fun_expr(p):
    '''FUNCEXPR : LPAREN FUNC LPAREN IDS RPAREN EXPR RPAREN
    '''
    args = [
        ast.arg(arg=i, annotation=None, lineno=p.lineno(2), col_offset=0) for i in p[4]
    ]
    p[0] = ast.Lambda(
        args=ast.arguments(
            args=args, 
            posonlyargs=[], kwonlyargs=[], 
            kw_defaults=[], defaults=[], 
            vararg=None, kwarg=None
        ),
        body=p[6],
        lineno=p.lineno(2),
        col_offset=0
    )

def p_fun_call(p):
    '''FUNCALL : LPAREN FUNCNAME ARGS RPAREN
        | LPAREN FUNCEXPR ARGS RPAREN
    '''
    p[0] = ast.Call(func=p[2], args=p[3], keywords=[], lineno=p.lineno(2), col_offset=0)

def p_if_expr(p):
    '''IFEXPR : LPAREN IF EXPR EXPR EXPR RPAREN
    '''
    p[0] = ast.IfExp(test=p[3], body=p[4], orelse=p[5], lineno=p.lineno(2), col_offset=0)

def p_exprs(p):
    '''EXPRS : EXPR
        | EXPR EXPRS
    '''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_ids(p):
    '''IDS : ID
           | IDS ID
           |
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_fun_name(p):
    '''FUNCNAME : ID
    '''
    p[0] = ast.Name(id=p[1], ctx=ast.Load(), lineno=p.lineno(1), col_offset=0)

def p_args(p):
    '''ARGS : EXPR
            | ARGS EXPR
            | 
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_print_stmt(p):
    '''PRINT_STMT : LPAREN PRINTNUM EXPR RPAREN
        | LPAREN PRINTBOOL EXPR RPAREN
    '''
    if p[2] == 'print-num':
        p[0] = ast.Expr(value=ast.Call(func=ast.Name(id='print', ctx=ast.Load(), lineno=p.lineno(2), col_offset=0),
                                       args=[p[3]],
                                       keywords=[],
                                       lineno=p.lineno(2),
                                       col_offset=0),
                        lineno=p.lineno(2),
                        col_offset=0)
    else: # if p[2] == 'print-bool'
        bool2tf = ast.IfExp(test=p[3],
                            body=ast.Constant(value='#t', lineno=p.lineno(3), col_offset=0),
                            orelse=ast.Constant(value='#f', lineno=p.lineno(3), col_offset=0),
                            lineno=p.lineno(3),
                            col_offset=0)

        p[0] = ast.Expr(value=ast.Call(func=ast.Name(id='print', ctx=ast.Load(), lineno=p.lineno(2), col_offset=0),
                                       args=[bool2tf],
                                       keywords=[],
                                       lineno=p.lineno(2),
                                       col_offset=0),
                        lineno=p.lineno(2),
                        col_offset=0)

def p_def_stmt(p):
    '''DEFINE_STMT : LPAREN DEF ID EXPR RPAREN
    '''
    target = ast.Name(
        id=p[3],
        ctx=ast.Store(),
        lineno=p.lineno(2),
        col_offset=0
    )
    p[0] = ast.Assign(
        targets=[target],
        value=p[4],
        lineno=p.lineno(2),
        col_offset=0
    )

def p_error(p):
    raise SyntaxError(f"Syntax error at line {p.lineno} near '{p.value}'")

# YACC
parser = yacc.yacc()

# ----MAIN--------------------------------------------------------------------------------

def main():
    # Read the file
    try:
        with open(sys.argv[1], 'r') as file:
            data = file.read()
    except:
        print("Error: File not found" if len(sys.argv) == 2 else f"Error: No file provided\nUsage: python3 {sys.argv[0]} <filename>.lsp")
        sys.exit(1)
    
    # Parse the data
    try:
        result = parser.parse(data, lexer=lexer)
        # ast.fix_missing_locations(result)
        output = compile(result, filename='<ast>', mode='exec')
        exec(output,{})
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()