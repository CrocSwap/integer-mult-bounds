# Agreement of the two orbit implementations: same hyperplane/type counts and the same multiset of invariants per type.
import sys, json, gzip
from collections import Counter
def inv(path):
    T=json.load(gzip.open(path,'rt'))
    return Counter((t['j'],t['nonorth'],len(t['D']),tuple(sorted(bin(r).count('1') for r in t['orth']))) for t in T), T
a,Ta=inv(sys.argv[1]); b,Tb=inv(sys.argv[2])
na=sum(t['nonorth'] for t in Ta); nb=sum(t['nonorth'] for t in Tb)
print('implementation A: types',len(Ta),'nonorth',na,'orth',len(Ta)-na,'min|D| nonorth',min(len(t['D']) for t in Ta if t['nonorth']))
print('implementation B: types',len(Tb),'nonorth',nb,'orth',len(Tb)-nb,'min|D| nonorth',min(len(t['D']) for t in Tb if t['nonorth']))
ok=(a==b and na==nb==4022 and len(Ta)-na==318 and min(len(t['D']) for t in Ta if t['nonorth'])==30)
print('per-type invariant multisets (node class, orthogonal?, |D|, orthogonality degree sequence) identical:',a==b)
print('PASS orbit recount: 4022 nonorth types, 318 orth types, min |D| = 30, both implementations' if ok else 'FAIL orbit recount')
sys.exit(0 if ok else 1)
