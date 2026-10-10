import os, sys


def _main():
    # read and delete the nonce BEFORE the untrusted solution is imported
    nf = os.environ.get('CHECK_NONCE_FILE'); nonce = ''
    if nf and os.path.exists(nf):
        nonce = open(nf).read().strip(); os.unlink(nf)
    sys.path.insert(0, '.')
    from solution import roman_to_int

    def _plain(v, depth=0):
        if depth > 8: raise AssertionError('result nested too deep')
        if v is None or type(v) in (bool, int, float, str): return v
        if type(v) in (list, tuple): return type(v)(_plain(x, depth + 1) for x in v)
        if type(v) is dict: return {_plain(k, depth + 1): _plain(x, depth + 1) for k, x in v.items()}
        raise AssertionError('non-plain result type: %s' % type(v).__name__)

    def _guard(f):
        def g(*a, **k): return _plain(f(*a, **k))
        return g
    roman_to_int = _guard(roman_to_int)

    assert roman_to_int('III') == 3
    assert roman_to_int('IX') == 9
    assert roman_to_int('LVIII') == 58
    assert roman_to_int('MCMXCIV') == 1994
    assert roman_to_int('MMXXIV') == 2024
    for bad in ('', 'ABC', 'iv'):
        try: roman_to_int(bad)
        except ValueError: pass
        else: raise AssertionError('no ValueError for %r' % bad)
    print('OK' + (' ' + nonce if nonce else ''))


_main()
