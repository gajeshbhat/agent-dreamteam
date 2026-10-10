import os, sys


def _main():
    # read and delete the nonce BEFORE the untrusted solution is imported
    nf = os.environ.get('CHECK_NONCE_FILE'); nonce = ''
    if nf and os.path.exists(nf):
        nonce = open(nf).read().strip(); os.unlink(nf)
    sys.path.insert(0, '.')
    from solution import wrap

    def _plain(v, depth=0):
        if depth > 8: raise AssertionError('result nested too deep')
        if v is None or type(v) in (bool, int, float, str): return v
        if type(v) in (list, tuple): return type(v)(_plain(x, depth + 1) for x in v)
        if type(v) is dict: return {_plain(k, depth + 1): _plain(x, depth + 1) for k, x in v.items()}
        raise AssertionError('non-plain result type: %s' % type(v).__name__)

    def _guard(f):
        def g(*a, **k): return _plain(f(*a, **k))
        return g
    wrap = _guard(wrap)

    assert wrap('the quick brown fox', 10) == ['the quick', 'brown fox']
    assert wrap('a b c d', 3) == ['a b', 'c d']
    assert wrap('supercalifragilistic is long', 8) == ['supercalifragilistic', 'is long']
    assert wrap('', 5) == [] and wrap('   ', 5) == []
    assert wrap('one', 3) == ['one']
    print('OK' + (' ' + nonce if nonce else ''))


_main()
