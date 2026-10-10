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
    wrap = rpc.load('solution', 'wrap', cls=False)

    assert wrap('the quick brown fox', 10) == ['the quick', 'brown fox']
    assert wrap('a b c d', 3) == ['a b', 'c d']
    assert wrap('supercalifragilistic is long', 8) == ['supercalifragilistic', 'is long']
    assert wrap('', 5) == [] and wrap('   ', 5) == []
    assert wrap('one', 3) == ['one']
    print('OK' + (' ' + nonce if nonce else ''))


_main()
