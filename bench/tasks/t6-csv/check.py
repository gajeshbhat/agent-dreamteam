import os, sys


def _main():
    # read and delete the nonce BEFORE the untrusted solution is imported
    nf = os.environ.get('CHECK_NONCE_FILE'); nonce = ''
    if nf and os.path.exists(nf):
        nonce = open(nf).read().strip(); os.unlink(nf)
    sys.path.insert(0, '.')
    from solution import parse_csv_line

    def _plain(v, depth=0):
        if depth > 8: raise AssertionError('result nested too deep')
        if v is None or type(v) in (bool, int, float, str): return v
        if type(v) in (list, tuple): return type(v)(_plain(x, depth + 1) for x in v)
        if type(v) is dict: return {_plain(k, depth + 1): _plain(x, depth + 1) for k, x in v.items()}
        raise AssertionError('non-plain result type: %s' % type(v).__name__)

    def _guard(f):
        def g(*a, **k): return _plain(f(*a, **k))
        return g
    parse_csv_line = _guard(parse_csv_line)

    assert parse_csv_line('a,b,c') == ['a', 'b', 'c']
    assert parse_csv_line('a,"b,c",d') == ['a', 'b,c', 'd']
    assert parse_csv_line('"say ""hi""",x') == ['say "hi"', 'x']
    assert parse_csv_line('') == ['']
    assert parse_csv_line(',,') == ['', '', '']
    assert parse_csv_line(' a , b ') == [' a ', ' b ']
    try: parse_csv_line('"abc')
    except ValueError: pass
    else: raise AssertionError('no ValueError for unterminated quote')
    print('OK' + (' ' + nonce if nonce else ''))


_main()
