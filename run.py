import sys
from lexer_parser import parse_code, tokenize_code
from symbol_table import SymbolTable
from ir_codegen import gen_program, tac_to_assembly

def main():
    # ------------------ Input Handling ------------------
    if len(sys.argv) > 1:
        # Case 1: Input from file
        with open(sys.argv[1]) as f:
            src = f.read()
    else:
        print("Enter your program (finish with an empty line, or press Enter immediately for default):")
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip() == "":
                break
            lines.append(line)
        if lines:
            # Case 2: Input from terminal
            src = "\n".join(lines)
        else:
            # Case 3: Default example
            src = """
int main(){
  int a = 5;
  int b = 3;
  if (a > b) { print(a - b); } else { print(b - a); }
  int i = 0;
  while (i < 3) { print(i); i = i + 1; }
}
"""

    # ------------------ Phase 1: Source ------------------
    print("=== Source Code ===\n")
    print(src)

    # ------------------ Phase 2: Tokenization ------------------
    print("\n=== Token List (summary) ===")
    cats = tokenize_code(src)
    for k, v in cats.items():
        print(f"{k} ({len(v)}): {', '.join(v) if v else '-'}")
    with open("out/tokens.txt", "w") as f:
        for k, v in cats.items():
            f.write(f"{k} ({len(v)}): {', '.join(v) if v else '-'}\n")

    # ------------------ Phase 3: Parsing ------------------
    print("\n=== Parsing → AST (statements) ===")
    ast = parse_code(src)
    for i, stmt in enumerate(ast, 1):
        print(i, stmt)

    # ------------------ Phase 4: Symbol Table ------------------
    print("\n=== Symbol Table (after declarations) ===")
    st = SymbolTable()
    for i, s in enumerate(ast, 1):
        if s[0] == "decl":
            st.insert(s[1], "int", line=i)
    st.dump("out/symtab.txt")

    # ------------------ Phase 5: TAC ------------------
    print("\n=== Three Address Code (TAC) ===")
    code = gen_program(ast, st)
    for c in code:
        print(c)
    with open("out/ir.tac", "w") as f:
        f.write("\n".join(code))

    # ------------------ Phase 6: Assembly ------------------
    print("\n=== Assembly-like Code ===")
    asm = tac_to_assembly(code)
    for line in asm:
        print(line)
    with open("out/assembly.txt", "w") as f:
        f.write("\n".join(asm))

    print("\nSaved: out/tokens.txt, out/symtab.txt, out/ir.tac, out/assembly.txt")

if __name__ == "__main__":
    main()
