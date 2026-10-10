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
    LRUCache = rpc.load('solution', 'LRUCache', cls=True)

    c = LRUCache(2)
    c.put(1, 1); c.put(2, 2)
    assert c.get(1) == 1
    c.put(3, 3)
    assert c.get(2) == -1
    c.put(4, 4)
    assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4
    c = LRUCache(1)
    c.put(1, 'a'); c.put(1, 'b')
    assert c.get(1) == 'b'
    c.put(2, 'c')
    assert c.get(1) == -1 and c.get(2) == 'c'
    print('OK' + (' ' + nonce if nonce else ''))


_main()
