# ir_codegen.py
from typing import List, Tuple
from symbol_table import SymbolTable

_tmp = 0
_lbl = 0
def new_tmp():  # t0, t1...
    global _tmp; t = f"t{_tmp}"; _tmp += 1; return t
def new_lbl():  # L0, L1...
    global _lbl; L = f"L{_lbl}"; _lbl += 1; return L
def reset_state():
    global _tmp, _lbl; _tmp = 0; _lbl = 0

# -------- Expressions → TAC --------
def gen_expr(n, st: SymbolTable) -> Tuple[List[str], str]:
    k = n[0]
    if k == "num":
        t = new_tmp(); return [f"{t} = {n[1]}"], t
    if k == "var":
        name = n[1]
        if not st.lookup(name): raise RuntimeError(f"Undeclared variable '{name}'")
        t = new_tmp(); return [f"{t} = {name}"], t
    if k in ("add","sub","mul","div","eq","ne","gt","lt","ge","le"):
        op = {"add":"+","sub":"-","mul":"*","div":"/","eq":"==","ne":"!=",
              "gt":">","lt":"<","ge":">=","le":"<="}[k]
        c1,t1 = gen_expr(n[1], st); c2,t2 = gen_expr(n[2], st)
        t = new_tmp(); return c1 + c2 + [f"{t} = {t1} {op} {t2}"], t
    raise RuntimeError(f"Unknown expr: {n}")

# -------- Statements → TAC --------
def gen_stmt(n, st: SymbolTable, line=0) -> List[str]:
    k = n[0]
    if k == "decl":
        name, init = n[1], n[2]   # <-- সবসময় এখানে init ডিফাইন হবে
        # আগে থেকে নেই তাহলে insert করো
        if not st.lookup(name):
            st.insert(name, "int", line=line)
        if init is None:
            return [f"{name} = 0"]
        c, t = gen_expr(init, st)
        return c + [f"{name} = {t}"]

    if k == "assign":
        name, e = n[1], n[2]
        if not st.lookup(name): raise RuntimeError(f"Undeclared variable '{name}'")
        c,t = gen_expr(e, st)
        # compile-time div-by-zero check (simple)
        if e[0]=="div" and isinstance(e[2], tuple) and e[2][0]=="num" and e[2][1]==0:
            raise RuntimeError("Division by zero detected at compile-time")
        return c + [f"{name} = {t}"]
    if k == "print":
        c,t = gen_expr(n[1], st); return c + [f"print {t}"]
    if k == "block":
        code: List[str] = []
        for s in n[1]: code += gen_stmt(s, st, line=line)
        return code
    if k == "if":
        cond, then, els = n[1], n[2], n[3]
        c,t = gen_expr(cond, st)
        L_else = new_lbl(); L_end = new_lbl()
        out = c + [f"ifFalse {t} goto {L_else}"]
        out += gen_stmt(then, st, line=line)
        out += [f"goto {L_end}", f"label {L_else}"]
        if els: out += gen_stmt(els, st, line=line)
        out += [f"label {L_end}"]
        return out
    if k == "while":
        cond, body = n[1], n[2]
        L_s = new_lbl(); L_e = new_lbl()
        c,t = gen_expr(cond, st)
        out = [f"label {L_s}"] + c + [f"ifFalse {t} goto {L_e}"]
        out += gen_stmt(body, st, line=line)
        out += [f"goto {L_s}", f"label {L_e}"]
        return out
    raise RuntimeError(f"Unknown stmt: {n}")

def gen_program(stmts, st: SymbolTable) -> List[str]:
    reset_state()
    code: List[str] = []
    for i, s in enumerate(stmts, 1):
        code += gen_stmt(s, st, line=i)
    return code

# -------- TAC → Assembly-like --------
def tac_to_assembly(tac: List[str]) -> List[str]:
    asm: List[str] = []
    for line in tac:
        parts = line.split()
        if not parts: continue
        if parts[0] == "print":
            asm.append(f"PRINT {parts[1]}"); continue
        if parts[0] == "label":
            asm.append(f"LABEL {parts[1]}"); continue
        if parts[0] == "goto":
            asm.append(f"JMP {parts[1]}"); continue
        if parts[0] == "ifFalse":
            # ifFalse t goto Lx  ->  JZ t Lx
            asm.append(f"JZ {parts[1]} {parts[3]}"); continue
        if "=" in parts:
            # x = y op z   |  x = y
            dst = parts[0]
            if len(parts)==5:   # x = y op z
                _,_,a,op,b = parts
                asm += [f"LOAD {a}", f"LOAD {b}",
                        {"+" :"ADD","-":"SUB","*":"MUL","/":"DIV",
                         "==":"CMPEQ","!=":"CMPNE",
                         ">":"CMPGT","<":"CMPLT",
                         ">=":"CMPGE","<=":"CMPLE"}[op],
                        f"STORE {dst}"]
            elif len(parts)==3: # x = y
                _,_,a = parts
                asm += [f"LOAD {a}", f"STORE {dst}"]
            else:
                asm.append(f"# UNHANDLED {line}")
        else:
            asm.append(f"# UNHANDLED {line}")
    return asm
