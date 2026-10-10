import os, sys


def _main():
    # read and delete the nonce BEFORE the untrusted solution is imported
    nf = os.environ.get('CHECK_NONCE_FILE'); nonce = ''
    if nf and os.path.exists(nf):
        nonce = open(nf).read().strip(); os.unlink(nf)
    sys.path.insert(0, '.')
    from solution import LRUCache

    def _plain(v, depth=0):
        if depth > 8: raise AssertionError('result nested too deep')
        if v is None or type(v) in (bool, int, float, str): return v
        if type(v) in (list, tuple): return type(v)(_plain(x, depth + 1) for x in v)
        if type(v) is dict: return {_plain(k, depth + 1): _plain(x, depth + 1) for k, x in v.items()}
        raise AssertionError('non-plain result type: %s' % type(v).__name__)

    def _guard(f):
        def g(*a, **k): return _plain(f(*a, **k))
        return g

    _cls = LRUCache

    class LRUCache:
        def __init__(self, *a, **k): object.__setattr__(self, '_o', _cls(*a, **k))
        def __getattr__(self, n): return _guard(getattr(self._o, n))

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
    print('OK' + (' ' + nonce if nonce else ''))


_main()
