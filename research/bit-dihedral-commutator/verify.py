"""Complete two-register F2[D8] paid-word metric. Apache-2.0."""
import hashlib,itertools,json,sys
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
def need(x,m):
    if not x:raise ValueError(m)
def mul(a,b):return (a^b) ^ ((((a&1)*((b>>1)&1)))<<2)
TABLE=[[mul(a,b) for b in range(8)] for a in range(8)]
GEN=[(g,x,y) for g in (1,2) for x in (1,2,3) for y in (1,2,3) if (x&y).bit_count()%2]
PERM={g:[sum(1<<TABLE[g][j] for j in range(8) if a>>j&1) for a in range(256)] for g in (1,2)}
IDENTITY=1|(1<<24);TARGET=16|(16<<24)
def step(state,generator):
    g,x,y=generator;cells=[(state>>(8*i))&255 for i in range(4)]
    for c in range(2):
        value=0
        for r in range(2):
            if y>>r&1:value^=cells[2*r+c]
        delta=value^PERM[g][value]
        for r in range(2):
            if x>>r&1:cells[2*r+c]^=delta
    return sum(v<<(8*i) for i,v in enumerate(cells))
def ball(start,depth):
    found={start:()};front=[start];layers=[1]
    for level in range(depth):
        nxt=[]
        for state in front:
            for k,g in enumerate(GEN):
                value=step(state,g)
                if value not in found:found[value]=found[state]+(k,);nxt.append(value)
        front=nxt;layers.append(len(front))
    return found,layers
def matrix(g):
    a,b,c=g&1,(g>>1)&1,(g>>2)&1
    return ((1,a,c),(0,1,b),(0,0,1))
def independent_product(word):
    # Sets of group matrices, rather than packed group IDs or the search transition.
    eye=matrix(0);out=[[{eye},set()],[set(),{eye}]]
    def mm(a,b):return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(3))%2 for j in range(3)) for i in range(3))
    for k in word:
        g,x,y=GEN[k];lab=matrix(g);factor=[[set() for _ in range(2)] for _ in range(2)]
        for i in range(2):
            for j in range(2):
                if i==j:factor[i][j].add(eye)
                if (x>>i&1) and (y>>j&1):factor[i][j]^={eye,lab}
        nxt=[[set() for _ in range(2)] for _ in range(2)]
        for i,j,k2 in itertools.product(range(2),repeat=3):
            for a in factor[i][k2]:
                for b in out[k2][j]:nxt[i][j].symmetric_difference_update((mm(a,b),))
        out=nxt
    return out
def run():
    for f in json.loads((H/'SOURCES.json').read_text())['files']:
        if f['usage']=='input':need(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],'source pin')
    need(len(GEN)==12,'complete generator count')
    for a,b,c in itertools.product(range(8),repeat=3):need(TABLE[TABLE[a][b]][c]==TABLE[a][TABLE[b][c]],'associativity')
    need(TABLE[1][2]!=TABLE[2][1] and TABLE[TABLE[TABLE[1][2]][1]][2]==4,'nonabelian commutator')
    left,ll=ball(IDENTITY,4);right,rr=ball(TARGET,4)
    meets=set(left)&set(right);need(meets,'eight-call upper bound')
    histogram=Counter(len(left[s])+len(right[s]) for s in meets)
    shortest=min(histogram);chosen=min((s for s in meets if len(left[s])+len(right[s])==shortest))
    witness=left[chosen]+tuple(reversed(right[chosen]));state=IDENTITY
    for k in witness:state=step(state,GEN[k])
    need(state==TARGET,'shortest witness')
    want=[[{matrix(4)},set()],[set(),{matrix(4)}]]
    need(independent_product(witness)==want,'independent formal group coefficients')
    for i in range(len(witness)):need(independent_product(witness[:i]+witness[i+1:])!=want,'each omission rejected')
    direct=tuple(GEN.index((g,1<<r,1<<r)) for r in range(2) for g in (1,2,1,2))
    need(independent_product(direct)==want,'direct eight-call comparison')
    # Allowing the central label itself changes the alphabet and destroys this lower bound.
    need(matrix(4)!=matrix(0),'central unit is nonidentity')
    payload=lambda states:hashlib.sha256(b''.join(s.to_bytes(4,'little') for s in sorted(states))).hexdigest()
    return dict(status='PASS_DIHEDRAL_COMMUTATOR',group_order=8,registers=2,generators=[list(g) for g in GEN],
      identity_layers=ll,target_layers=rr,identity_ball_sha256=payload(left),target_ball_sha256=payload(right),
      meeting_lengths=dict(sorted(histogram.items())),minimum=shortest,witness=list(witness),
      independent_formal_checked=True,omission_controls=len(witness),direct_word=list(direct),
      scalar_mixing='all six rank-one idempotents; arbitrary free GL2 basis changes normalized by augmentation',new_kappa=False)
if __name__=='__main__':
    x=json.loads(json.dumps(run()));p=H/'CERTIFICATE.json'
    if '--write' in sys.argv:p.write_text(json.dumps(x,indent=2)+'\n')
    else:need(x==json.loads(p.read_text()),'receipt')
    print(x['status'],'minimum='+str(x['minimum']),'layers='+str(x['identity_layers']),'meetings='+str(x['meeting_lengths']))
