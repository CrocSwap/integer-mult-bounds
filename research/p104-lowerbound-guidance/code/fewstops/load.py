import sys
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
D='<word-rung-package>/data/'
W=pk.load(D+'t7669.json.gz'); C=pk.load(D+'7113_CALLER.json')
n=W['public']; P=W['program']; F=W['frames']; dim=[len(f) for f in F]
def span(B):
    S={0}
    for b in B: S|={x^b for x in S}
    return frozenset(S)
SP=[span(b) for b in F]
live=set(W['live']); H=W['hosted']
cls={}
for r in live: cls[r]='X'; cls[r+112]='Y'
for r in H['X2']: cls[r]='X2'
for r in H['Y2']: cls[r]='Y2'
def kind(r): return 'O' if r>=n else cls.get(r,'H')
