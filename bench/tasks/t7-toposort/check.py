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
    toposort = rpc.load('solution', 'toposort', cls=False)

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
