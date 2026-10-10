import re
def evaluate(expr):
    toks = re.findall(r'\d+\.?\d*|\.\d+|[-+*/()]|\S', expr)
    for t in toks:
        if not re.fullmatch(r'\d+\.?\d*|\.\d+|[-+*/()]', t): raise ValueError(t)
    pos = [0]
    def peek(): return toks[pos[0]] if pos[0] < len(toks) else None
    def eat(): pos[0] += 1; return toks[pos[0] - 1]
    def atom():
        t = peek()
        if t is None: raise ValueError('unexpected end')
        if t == '-': eat(); return -atom()
        if t == '(':
            eat(); v = add()
            if peek() != ')': raise ValueError('unbalanced')
            eat(); return v
        if t in ('+', '*', '/', ')'): raise ValueError(t)
        return float(eat())
    def mul():
        v = atom()
        while peek() in ('*', '/'):
            op = eat(); r = atom()
            v = v * r if op == '*' else v / r
        return v
    def add():
        v = mul()
        while peek() in ('+', '-'):
            op = eat(); r = mul()
            v = v + r if op == '+' else v - r
        return v
    if not toks: raise ValueError('empty')
    v = add()
    if peek() is not None: raise ValueError('trailing')
    return v
