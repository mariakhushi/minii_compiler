# lexer_parser.py
import re
from lark import Lark, Transformer

# ---- Simple tokenizer (lab-style summary) ----
KEYWORDS = {"int", "print", "if", "else", "while", "main"}
OPERATORS = {"==","!=",">=","<=","+","-","*","/","=","<",">"}
PUNCTS = {";", ",", "(", ")", "{", "}"}

_token_spec = [
    ("COMMENT",  r"//[^\n]*"),
    ("NUMBER",   r"\d+"),
    ("ID",       r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP",       r"==|!=|>=|<=|[+\-*/=<>]"),
    ("PUNCT",    r"[;,(){}]"),
    ("SKIP",     r"[ \t\r\n]+"),
    ("MISMATCH", r"."),
]
_tok_re = re.compile("|".join(f"(?P<{n}>{p})" for n,p in _token_spec))

def tokenize_code(code: str):
    cats = {"Keyword":[], "Identifier":[], "Constant":[], "Operator":[], "Punctuation":[], "Comment":[]}
    for m in _tok_re.finditer(code):
        kind = m.lastgroup; val = m.group()
        if kind == "COMMENT": cats["Comment"].append(val); continue
        if kind == "SKIP":    continue
        if kind == "NUMBER":  cats["Constant"].append(val); continue
        if kind == "ID":
            if val in KEYWORDS: cats["Keyword"].append(val)
            else: cats["Identifier"].append(val)
            continue
        if kind == "OP":      cats["Operator"].append(val); continue
        if kind == "PUNCT":   cats["Punctuation"].append(val); continue
        if kind == "MISMATCH": raise ValueError(f"Unexpected char: {val}")
    return cats

# ---- Parser + AST (Lark) ----
GRAMMAR = r"""
    start: "int" "main" "(" ")" "{" stmt* "}"

    ?stmt: decl ";" 
         | assign ";" 
         | print_stmt ";"
         | if_stmt
         | while_stmt
         | "{" stmt* "}"        -> block

    decl: "int" CNAME ("=" expr)?
    assign: CNAME "=" expr
    print_stmt: "print" "(" expr ")"
    if_stmt: "if" "(" expr ")" stmt ("else" stmt)?
    while_stmt: "while" "(" expr ")" stmt

    ?expr: logic
    ?logic: rel
          | logic "==" rel   -> eq
          | logic "!=" rel   -> ne
    ?rel: add
        | rel ">"  add       -> gt
        | rel "<"  add       -> lt
        | rel ">=" add       -> ge
        | rel "<=" add       -> le
    ?add: mul
        | add "+" mul        -> add
        | add "-" mul        -> sub
    ?mul: atom
        | mul "*" atom       -> mul
        | mul "/" atom       -> div
    ?atom: NUMBER            -> number
         | CNAME             -> var
         | "(" expr ")"

    %import common.CNAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

class AST(Transformer):
    def number(self, n): return ("num", int(n[0]))
    def var(self, n):    return ("var", str(n[0]))
    def add(self, i):    return ("add", i[0], i[1])
    def sub(self, i):    return ("sub", i[0], i[1])
    def mul(self, i):    return ("mul", i[0], i[1])
    def div(self, i):    return ("div", i[0], i[1])
    def eq(self, i):     return ("eq",  i[0], i[1])
    def ne(self, i):     return ("ne",  i[0], i[1])
    def gt(self, i):     return ("gt",  i[0], i[1])
    def lt(self, i):     return ("lt",  i[0], i[1])
    def ge(self, i):     return ("ge",  i[0], i[1])
    def le(self, i):     return ("le",  i[0], i[1])
    def decl(self, i):
        name = str(i[0]); init = i[1] if len(i)==2 else None
        return ("decl", name, init)
    def assign(self, i): return ("assign", str(i[0]), i[1])
    def print_stmt(self, i): return ("print", i[0])
    def block(self, items):  return ("block", list(items))
    def if_stmt(self, items):
        cond = items[0]; then = items[1]; els = items[2] if len(items)==3 else None
        return ("if", cond, then, els)
    def while_stmt(self, items):
        return ("while", items[0], items[1])

_parser = Lark(GRAMMAR, parser="lalr")
def parse_code(code: str):
    tree = _parser.parse(code)
    ast = AST().transform(tree)
    return list(ast.children)  # flat list of stmts inside main{}
