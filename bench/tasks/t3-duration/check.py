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
    parse_duration = rpc.load('solution', 'parse_duration', cls=False)

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
