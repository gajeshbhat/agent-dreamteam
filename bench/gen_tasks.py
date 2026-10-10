"""Generate bench/tasks/<id>/{prompt.txt,check.py,ref.py,size}. Run: python3 bench/gen_tasks.py"""
import os, textwrap

# Results from the untrusted solution must be plain builtins, so an object whose __eq__ always
# returns True cannot satisfy the asserts.
GUARD = """
    def _plain(v, depth=0):
        if depth > 8: raise AssertionError('result nested too deep')
        if v is None or type(v) in (bool, int, float, str): return v
        if type(v) in (list, tuple): return type(v)(_plain(x, depth + 1) for x in v)
        if type(v) is dict: return {_plain(k, depth + 1): _plain(x, depth + 1) for k, x in v.items()}
        raise AssertionError('non-plain result type: %s' % type(v).__name__)

    def _guard(f):
        def g(*a, **k): return _plain(f(*a, **k))
        return g
WRAP"""
FUN = "    FN = _guard(FN)\n"
CLS = """
    _cls = FN

    class FN:
        def __init__(self, *a, **k): object.__setattr__(self, '_o', _cls(*a, **k))
        def __getattr__(self, n): return _guard(getattr(self._o, n))
"""
T = {}
def task(id, size, fn, prompt, check, ref):
    T[id] = dict(size=size, fn=fn, prompt=textwrap.dedent(prompt).strip(),
                 check=textwrap.dedent(check).strip(), ref=textwrap.dedent(ref).strip())

task("t1-slugify", "small", "slugify", '''
Implement slugify(text) in solution.py: lowercase; every run of non-alphanumeric characters becomes one '-'; strip leading and trailing '-'.''', '''
assert slugify('Hello, World!') == 'hello-world'
assert slugify('  a  b ') == 'a-b'
assert slugify('---') == ''
assert slugify('Foo__Bar 9') == 'foo-bar-9'
assert slugify('') == ''
''', '''
import re
def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
''')

task("t2-roman", "small", "roman_to_int", '''
Implement roman_to_int(s) in solution.py: convert an upper-case Roman numeral to an int (subtractive notation such as IV, IX, XL, XC, CD, CM). Raise ValueError for an empty string or any character that is not one of IVXLCDM.''', '''
assert roman_to_int('III') == 3
assert roman_to_int('IX') == 9
assert roman_to_int('LVIII') == 58
assert roman_to_int('MCMXCIV') == 1994
assert roman_to_int('MMXXIV') == 2024
for bad in ('', 'ABC', 'iv'):
    try: roman_to_int(bad)
    except ValueError: pass
    else: raise AssertionError('no ValueError for %r' % bad)
''', '''
def roman_to_int(s):
    v = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    if not s or any(c not in v for c in s): raise ValueError(s)
    t = 0
    for i, c in enumerate(s):
        t += -v[c] if i + 1 < len(s) and v[c] < v[s[i + 1]] else v[c]
    return t
''')

task("t3-duration", "medium", "parse_duration", '''
Implement parse_duration(s) in solution.py returning total seconds as an int. s is a sequence of <integer><unit> parts with units d (86400), h (3600), m (60), s (1), e.g. '1h30m' = 5400, '2d' = 172800, '90m' = 5400, '1h1m1s' = 3661. Raise ValueError for an empty string, an unknown unit, a missing number, or trailing characters (e.g. '5x', 'h', '10', '1h 30m').''', '''
assert parse_duration('1h30m') == 5400
assert parse_duration('45s') == 45
assert parse_duration('2d') == 172800
assert parse_duration('1h1m1s') == 3661
assert parse_duration('90m') == 5400
for bad in ('', '5x', 'h', '10', '1h 30m', '1.5h'):
    try: parse_duration(bad)
    except ValueError: pass
    else: raise AssertionError('no ValueError for %r' % bad)
''', '''
import re
def parse_duration(s):
    if not re.fullmatch(r'(\\d+[dhms])+', s): raise ValueError(s)
    u = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
    return sum(int(n) * u[c] for n, c in re.findall(r'(\\d+)([dhms])', s))
''')

task("t4-lru", "medium", "LRUCache", '''
Implement class LRUCache in solution.py. LRUCache(capacity) with get(key) -> value or -1 if missing, and put(key, value). When a put would exceed capacity, evict the least recently used key. Both get (of an existing key) and put count as use; putting an existing key updates its value.''', '''
c = LRUCache(2)
c.put(1, 1); c.put(2, 2)
assert c.get(1) == 1
c.put(3, 3)
assert c.get(2) == -1
c.put(4, 4)
assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4
c = LRUCache(1)
c.put(1, 'a'); c.put(1, 'b')
assert c.get(1) == 'b'
c.put(2, 'c')
assert c.get(1) == -1 and c.get(2) == 'c'
''', '''
from collections import OrderedDict
class LRUCache:
    def __init__(self, capacity):
        self.cap, self.d = capacity, OrderedDict()
    def get(self, key):
        if key not in self.d: return -1
        self.d.move_to_end(key); return self.d[key]
    def put(self, key, value):
        self.d[key] = value; self.d.move_to_end(key)
        if len(self.d) > self.cap: self.d.popitem(last=False)
''')

task("t5-wrap", "medium", "wrap", '''
Implement wrap(text, width) in solution.py returning a list of lines. Split text on whitespace; greedily pack words onto lines separated by single spaces so no line is longer than width. A word longer than width goes on its own line unbroken. Empty or whitespace-only text gives [].''', '''
assert wrap('the quick brown fox', 10) == ['the quick', 'brown fox']
assert wrap('a b c d', 3) == ['a b', 'c d']
assert wrap('supercalifragilistic is long', 8) == ['supercalifragilistic', 'is long']
assert wrap('', 5) == [] and wrap('   ', 5) == []
assert wrap('one', 3) == ['one']
''', '''
def wrap(text, width):
    lines, cur = [], ''
    for w in text.split():
        if not cur: cur = w
        elif len(cur) + 1 + len(w) <= width: cur += ' ' + w
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines
''')

task("t6-csv", "medium-hard", "parse_csv_line", '''
Implement parse_csv_line(line) in solution.py returning a list of str fields. Fields are separated by commas. A field may be wrapped in double quotes, in which case it may contain commas and a doubled quote stands for one literal quote. Unquoted fields are returned as is (no stripping). An empty line gives a list with one empty string. Raise ValueError for an unterminated quote.''', '''
assert parse_csv_line('a,b,c') == ['a', 'b', 'c']
assert parse_csv_line('a,"b,c",d') == ['a', 'b,c', 'd']
assert parse_csv_line('"say ""hi""",x') == ['say "hi"', 'x']
assert parse_csv_line('') == ['']
assert parse_csv_line(',,') == ['', '', '']
assert parse_csv_line(' a , b ') == [' a ', ' b ']
try: parse_csv_line('"abc')
except ValueError: pass
else: raise AssertionError('no ValueError for unterminated quote')
''', '''
def parse_csv_line(line):
    out, cur, i, q = [], '', 0, False
    while i < len(line):
        c = line[i]
        if q:
            if c == '"':
                if line[i + 1:i + 2] == '"': cur += '"'; i += 1
                else: q = False
            else: cur += c
        elif c == '"': q = True
        elif c == ',': out.append(cur); cur = ''
        else: cur += c
        i += 1
    if q: raise ValueError('unterminated quote')
    out.append(cur)
    return out
''')

task("t7-toposort", "medium-hard", "toposort", '''
Implement toposort(graph) in solution.py. graph maps each node to a list of the nodes it depends on (dependencies come first in the output). Every node that appears anywhere is included in the result. Among nodes that are ready at the same time, take them in alphabetical order. Raise ValueError if there is a cycle.''', '''
assert toposort({'a': ['b', 'c'], 'b': ['c'], 'c': []}) == ['c', 'b', 'a']
assert toposort({'x': [], 'y': [], 'z': []}) == ['x', 'y', 'z']
assert toposort({'a': ['d']}) == ['d', 'a']
assert toposort({'b': ['a'], 'c': ['a'], 'a': []}) == ['a', 'b', 'c']
assert toposort({}) == []
for bad in ({'a': ['b'], 'b': ['a']}, {'a': ['a']}):
    try: toposort(bad)
    except ValueError: pass
    else: raise AssertionError('no ValueError for cycle')
''', '''
import heapq
def toposort(graph):
    nodes = set(graph) | {d for ds in graph.values() for d in ds}
    deps = {n: set(graph.get(n, [])) for n in nodes}
    ready = [n for n in nodes if not deps[n]]; heapq.heapify(ready)
    out = []
    while ready:
        n = heapq.heappop(ready); out.append(n)
        for m in nodes:
            if n in deps[m]:
                deps[m].discard(n)
                if not deps[m]: heapq.heappush(ready, m)
    if len(out) != len(nodes): raise ValueError('cycle')
    return out
''')

task("t8-eval", "hard", "evaluate", '''
Implement evaluate(expr) in solution.py: evaluate an arithmetic expression string with numbers (ints or decimals), + - * /, parentheses, unary minus, and arbitrary spaces. Standard precedence, left associative. Return a float. Division by zero raises ZeroDivisionError. Any malformed input (empty, unbalanced parentheses, trailing operator, unknown character) raises ValueError. Do not use eval or exec.''', '''
assert evaluate('1 + 2 * 3') == 7.0
assert evaluate('(1 + 2) * 3') == 9.0
assert evaluate('-4 + 10 / 4') == -1.5
assert evaluate('2 * -3') == -6.0
assert evaluate(' 8 / 2 / 2 ') == 2.0
assert evaluate('1.5 * 2') == 3.0
assert evaluate('--2') == 2.0
try: evaluate('1 / 0')
except ZeroDivisionError: pass
else: raise AssertionError('no ZeroDivisionError')
for bad in ('', '(1', '1 +', '1 $ 2', ')', '1 2'):
    try: evaluate(bad)
    except ValueError: pass
    else: raise AssertionError('no ValueError for %r' % bad)
''', '''
import re
def evaluate(expr):
    toks = re.findall(r'\\d+\\.?\\d*|\\.\\d+|[-+*/()]|\\S', expr)
    for t in toks:
        if not re.fullmatch(r'\\d+\\.?\\d*|\\.\\d+|[-+*/()]', t): raise ValueError(t)
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
''')

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks")
for id, t in T.items():
    d = os.path.join(root, id); os.makedirs(d, exist_ok=True)
    open(f"{d}/prompt.txt", "w").write(t["prompt"] + "\n")
    body = textwrap.indent(t["check"], "    ")
    chk = ("import os, sys\n\n\ndef _main():\n"
           "    # nonce is read and deleted here, in the trusted process; the solution runs in a child\n"
           "    nf = os.environ.get('CHECK_NONCE_FILE'); nonce = ''\n"
           "    if nf and os.path.exists(nf):\n"
           "        nonce = open(nf).read().strip(); os.unlink(nf)\n"
           "    here = os.path.dirname(os.path.abspath(__file__))\n"
           "    for d in (here, os.path.join(here, '..', '..')):\n"
           "        sys.path.insert(0, d)\n"
           "    import rpc\n"
           f"    {t['fn']} = rpc.load('solution', '{t['fn']}', cls={t['fn'][0].isupper()})\n\n"
           f"{body}\n"
           "    print('OK' + (' ' + nonce if nonce else ''))\n\n\n_main()\n")
    tmp = f"{d}/check.py.new"; open(tmp, "w").write(chk); os.replace(tmp, f"{d}/check.py")
    open(f"{d}/ref.py", "w").write(t["ref"] + "\n")
    open(f"{d}/size", "w").write(t["size"] + "\n")
print(len(T), "tasks generated")
