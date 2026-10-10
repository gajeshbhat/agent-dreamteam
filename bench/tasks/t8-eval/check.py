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
    evaluate = rpc.load('solution', 'evaluate', cls=False)

    assert evaluate('1 + 2 * 3') == 7.0
    assert evaluate('(1 + 2) * 3') == 9.0
    assert evaluate('-4 + 10 / 4') == -1.5
    assert evaluate('2 * -3') == -6.0
    assert evaluate(' 8 / 2 / 2 ') == 2.0
    assert evaluate('1.5 * 2') == 3.0
    assert evaluate('--2') == 2.0
    try: evaluate('1 / 0')
    except ZeroDivisionError: pass
    else: raise AssertionError('no ZeroDivisionError')
    for bad in ('', '(1', '1 +', '1 $ 2', ')', '1 2'):
        try: evaluate(bad)
        except ValueError: pass
        else: raise AssertionError('no ValueError for %r' % bad)
    print('OK' + (' ' + nonce if nonce else ''))


_main()
