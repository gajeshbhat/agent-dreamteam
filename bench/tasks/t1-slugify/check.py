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
    slugify = rpc.load('solution', 'slugify', cls=False)

    assert slugify('Hello, World!') == 'hello-world'
    assert slugify('  a  b ') == 'a-b'
    assert slugify('---') == ''
    assert slugify('Foo__Bar 9') == 'foo-bar-9'
    assert slugify('') == ''
    print('OK' + (' ' + nonce if nonce else ''))


_main()
