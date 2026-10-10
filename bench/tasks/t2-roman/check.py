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
    roman_to_int = rpc.load('solution', 'roman_to_int', cls=False)

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
