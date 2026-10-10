"""Trusted side of the grader.

check.py runs in this (parent) process and holds the nonce. The untrusted solution is
imported only in a CHILD process with a scrubbed environment; the parent asks it to make
calls and receives plain JSON values or an exception name. The solution therefore never
shares a process, stack or environment with the nonce, and cannot print the verdict.
"""
import builtins, json, os, select, subprocess, sys

if len(sys.argv) > 1 and sys.argv[1] == "--child":          # ---- untrusted side ----
    import importlib
    sys.path.insert(0, os.getcwd())
    proto = os.fdopen(os.dup(1), "w")
    os.dup2(2, 1)                                           # solution prints go to stderr
    mod = importlib.import_module(sys.argv[2])
    objs = {}

    def plain(v, depth=0):
        if depth > 8: raise TypeError("result nested too deep")
        if v is None or type(v) in (bool, int, float, str): return v
        if type(v) in (list, tuple): return [plain(x, depth + 1) for x in v]
        if type(v) is dict: return {str(k): plain(x, depth + 1) for k, x in v.items()}
        raise TypeError("non-plain result type: %s" % type(v).__name__)

    for line in sys.stdin:
        m = json.loads(line)
        try:
            if m["op"] == "new":
                objs[len(objs) + 1] = getattr(mod, m["name"])(*m["args"])
                r = {"obj": len(objs)}
            else:
                tgt = getattr(mod, m["name"]) if m.get("obj") is None else getattr(objs[m["obj"]], m["name"])
                r = {"ok": plain(tgt(*m["args"]))}
        except BaseException as e:
            r = {"exc": type(e).__name__, "msg": str(e)[:200]}
        proto.write(json.dumps(r) + "\n"); proto.flush()
    sys.exit(0)


class _Proc:                                                # ---- trusted side ----
    def __init__(self, module):
        env = {"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"}   # no nonce, no secrets
        self.p = subprocess.Popen([sys.executable, "-I", os.path.abspath(__file__), "--child", module],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  env=env, cwd=os.getcwd(), text=True)

    def rpc(self, msg, timeout=15):
        try:
            self.p.stdin.write(json.dumps(msg) + "\n"); self.p.stdin.flush()
        except (BrokenPipeError, ValueError):
            raise AssertionError("solution process died")
        if not select.select([self.p.stdout], [], [], timeout)[0]:
            self.p.kill(); raise AssertionError("solution timed out")
        line = self.p.stdout.readline()
        if not line: raise AssertionError("solution process died or printed nothing")
        r = json.loads(line)
        if "exc" in r:
            cls = getattr(builtins, r["exc"], None)
            raise (cls if isinstance(cls, type) and issubclass(cls, BaseException) else RuntimeError)(r.get("msg", r["exc"]))
        return r


class _Obj:
    def __init__(self, proc, oid): self._proc, self._oid = proc, oid
    def __getattr__(self, name):
        return lambda *a: self._proc.rpc({"op": "call", "obj": self._oid, "name": name, "args": list(a)})["ok"]


def load(module, name, cls=False):
    proc = _Proc(module)
    if cls:
        return lambda *a: _Obj(proc, proc.rpc({"op": "new", "name": name, "args": list(a)})["obj"])
    return lambda *a: proc.rpc({"op": "call", "name": name, "args": list(a)})["ok"]
