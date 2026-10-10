import os, sys


def _main():
    # nonce is read and deleted here, in the trusted process; the solution runs in a child
    nf = os.environ.get('CHECK_NONCE_FILE'); nonce = ''
    if nf and os.path.exists(nf):
        nonce = open(nf).read().strip(); os.unlink(nf)
    here = os.path.dirname(os.path.abspath(__file__))
    for d in (here, os.path.join(here, '..', '..')):
        sys.path.insert(0, d)
    import rpc
    parse_csv_line = rpc.load('solution', 'parse_csv_line', cls=False)

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
