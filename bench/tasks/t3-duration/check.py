import os, sys


def _main():
    # read and delete the nonce BEFORE the untrusted solution is imported
    nf = os.environ.get('CHECK_NONCE_FILE'); nonce = ''
    if nf and os.path.exists(nf):
        nonce = open(nf).read().strip(); os.unlink(nf)
    sys.path.insert(0, '.')
    from solution import parse_duration

    def _plain(v, depth=0):
        if depth > 8: raise AssertionError('result nested too deep')
        if v is None or type(v) in (bool, int, float, str): return v
        if type(v) in (list, tuple): return type(v)(_plain(x, depth + 1) for x in v)
        if type(v) is dict: return {_plain(k, depth + 1): _plain(x, depth + 1) for k, x in v.items()}
        raise AssertionError('non-plain result type: %s' % type(v).__name__)

    def _guard(f):
        def g(*a, **k): return _plain(f(*a, **k))
        return g
    parse_duration = _guard(parse_duration)

    assert parse_duration('1h30m') == 5400
    assert parse_duration('45s') == 45
    assert parse_duration('2d') == 172800
    assert parse_duration('1h1m1s') == 3661
    assert parse_duration('90m') == 5400
    for bad in ('', '5x', 'h', '10', '1h 30m', '1.5h'):
        try: parse_duration(bad)
        except ValueError: pass
        else: raise AssertionError('no ValueError for %r' % bad)
    print('OK' + (' ' + nonce if nonce else ''))


_main()
