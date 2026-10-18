# Compares a fresh log with the recorded log of the same script (evidence/logs/*.log). Lines are normalised by dropping the trailing elapsed-seconds
# integer on the progress lines that carry one (prefixes rep/orbit/subspaces/dim/Z/start cands/pair/DONE <n>) and exact-matching everything else.
# usage: cmp_logs.py FRESH RECORDED [--subset]   --subset: every fresh line must occur in the recorded log (partial replay); default: same multiset of lines.
import sys, re, collections
TS = ('rep ', 'orbit ', 'subspaces ', 'dim ', 'Z ', 'start cands', 'pair ')
def norm(l):
    l = l.rstrip()
    if re.match(r'^DONE \d+$', l): return 'DONE'
    if l.startswith(TS):
        return re.sub(r'\s+\d+$', '', l) if l.startswith(('rep ', 'orbit ', 'subspaces ', 'dim ', 'Z ', 'start cands', 'pair ')) else l
    return l
def lines(p):
    out = [norm(l) for l in open(p, errors='replace') if l.strip()]
    return collections.Counter(out)
a = lines(sys.argv[1]); b = lines(sys.argv[2]); subset = '--subset' in sys.argv
if subset: bad = a - b
else: bad = (a - b) + (b - a)
if bad:
    print('FAIL log comparison', sys.argv[1], 'vs', sys.argv[2]); [print('   ', k[:200]) for k in list(bad)[:5]]; sys.exit(1)
print('PASS log comparison: %d distinct fresh lines %s recorded %s' % (len(a), 'all occur in' if subset else 'identical (normalised) to', sys.argv[2].split('/')[-1]))
