import os, sys


def _main():
    # read and delete the nonce BEFORE the untrusted solution is imported
    nf = os.environ.get('CHECK_NONCE_FILE'); nonce = ''
    if nf and os.path.exists(nf):
        nonce = open(nf).read().strip(); os.unlink(nf)
    sys.path.insert(0, '.')
    from solution import toposort

    def _plain(v, depth=0):
        if depth > 8: raise AssertionError('result nested too deep')
        if v is None or type(v) in (bool, int, float, str): return v
        if type(v) in (list, tuple): return type(v)(_plain(x, depth + 1) for x in v)
        if type(v) is dict: return {_plain(k, depth + 1): _plain(x, depth + 1) for k, x in v.items()}
        raise AssertionError('non-plain result type: %s' % type(v).__name__)

    def _guard(f):
        def g(*a, **k): return _plain(f(*a, **k))
        return g
    toposort = _guard(toposort)

    assert toposort({'a': ['b', 'c'], 'b': ['c'], 'c': []}) == ['c', 'b', 'a']
    assert toposort({'x': [], 'y': [], 'z': []}) == ['x', 'y', 'z']
    assert toposort({'a': ['d']}) == ['d', 'a']
    assert toposort({'b': ['a'], 'c': ['a'], 'a': []}) == ['a', 'b', 'c']
    assert toposort({}) == []
    for bad in ({'a': ['b'], 'b': ['a']}, {'a': ['a']}):
        try: toposort(bad)
        except ValueError: pass
        else: raise AssertionError('no ValueError for cycle')
    print('OK' + (' ' + nonce if nonce else ''))


_main()
