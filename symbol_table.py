class SymbolTable:
    def __init__(self):
        # table নামের dict বানাই
        # name → (type, value, decl_lines, use_lines)
        self.table = {}

    def insert(self, name, typ, value=None, line=0):
        if name in self.table:
            raise RuntimeError(f"Duplicate declaration of '{name}' (line {line})")
        self.table[name] = (typ, value, [line], [])

    def lookup(self, name):
        return self.table.get(name)

    def update(self, name, value, line=0):
        if name not in self.table:
            raise RuntimeError(f"Undeclared variable '{name}' (line {line})")
        typ, _, decl_lines, use_lines = self.table[name]
        self.table[name] = (typ, value, decl_lines, use_lines + [line])

    def dump(self, filename=None):
        """Prints the symbol table and optionally saves to a file"""
        lines = []
        for idx, (name, (typ, val, decls, uses)) in enumerate(self.table.items()):
            line_str = f"({idx}, '{name}', '{typ}', {val}, {decls}, {uses})"
            print(line_str)
            lines.append(line_str)

        if filename:
            with open(filename, "w") as f:
                f.write("\n".join(lines))
