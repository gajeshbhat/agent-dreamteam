import os, sys


def _main():
    # read and delete the nonce BEFORE the untrusted solution is imported
    nf = os.environ.get('CHECK_NONCE_FILE'); nonce = ''
    if nf and os.path.exists(nf):
        nonce = open(nf).read().strip(); os.unlink(nf)
    sys.path.insert(0, '.')
    from solution import evaluate

    def _plain(v, depth=0):
        if depth > 8: raise AssertionError('result nested too deep')
        if v is None or type(v) in (bool, int, float, str): return v
        if type(v) in (list, tuple): return type(v)(_plain(x, depth + 1) for x in v)
        if type(v) is dict: return {_plain(k, depth + 1): _plain(x, depth + 1) for k, x in v.items()}
        raise AssertionError('non-plain result type: %s' % type(v).__name__)

    def _guard(f):
        def g(*a, **k): return _plain(f(*a, **k))
        return g
    evaluate = _guard(evaluate)

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
    print('OK' + (' ' + nonce if nonce else ''))


_main()
