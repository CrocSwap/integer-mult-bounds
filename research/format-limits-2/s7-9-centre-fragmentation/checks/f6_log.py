"""F6 (CHECKED (log)): parse the shipped, sha256-pinned miner output of the rebuilt #664 word (evidence/F6/miner664_run1.out).
Line 1 is Counter({'disjoint': N, 'grow': G}) (disjoint-lifetime helper pairs, and how many of them need frame growth); line 2 is the Counter of
frame-nested pairs (empty = none).  Not a re-run of the miner."""
import ast, os
from common import *
L = open(os.path.join(ROOT, 'evidence', 'F6', 'miner664_run1.out')).read().strip().split('\n')
def parse(l):
    assert l.startswith('Counter(') and l.endswith(')')
    return ast.literal_eval(l[len('Counter('):-1] or '{}')
pairs, nested = parse(L[0]), parse(L[1])
check('f6.log-2534-disjoint-pairs-all-need-growth-0-nested',
      len(L) == 2 and pairs == {'disjoint': 2534, 'grow': 2534} and nested == {} and sum(nested.values()) == 0,
      'disjoint %d, grow %d, nested %d' % (pairs['disjoint'], pairs['grow'], sum(nested.values())))
done()
