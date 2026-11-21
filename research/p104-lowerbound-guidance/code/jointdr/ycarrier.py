# JOINTDR: word realisation of NETATTR §3(ii) (h=4) with the slack relay carried by public y_8. Exact replay.
from fractions import Fraction as Q
from itertools import product
h=4
def span(B):
    S={0}
    for b in B: S|={x^b for x in S}
    return frozenset(S)
dot=lambda a,b: bin(a&b).count('1')&1
perp=lambda q: frozenset(x for x in range(16) if dot(x,q)==0)
V=frozenset(range(16))
ports=[1,2,4,7,8,11,14]
reg={}; chart={}; kind={}
for p in ports:
    reg['x%d'%p]={'x%d'%p:Q(1)}; chart['x%d'%p]=span([p]); kind['x%d'%p]=('X',p)
    reg['y%d'%p]={}; chart['y%d'%p]=span([]); kind['y%d'%p]=('Y',p)
log=[]; own_move=[0,0]
def move(r,B):
    A=chart[r]
    if kind.get(r,('O',))[0]!='O':
        assert A<B, ('public must strictly ascend',r)
    else:
        assert A<=B or B<=A, ('owned nested',r)
        d=len(B).bit_length()-len(A).bit_length()
        own_move[0 if d>0 else 1]+=abs(d)
    if kind[r][0]=='Y': assert B<=perp(kind[r][1]),('y chart',r)
    if kind[r][0]=='X': assert kind[r][1] in B,('x chart',r)
    chart[r]=B
def init(r,C): reg[r]={}; chart[r]=C; kind[r]=('O',)
def add(r,s,l=1):
    assert chart[r]==chart[s],('co-located',r,s)
    for k,v in reg[s].items():
        reg[r][k]=reg[r].get(k,0)+l*v
        if reg[r][k]==0: del reg[r][k]
a_j=span([1,4]); b_j=span([5]); a_k=span([2,5]); b_k=span([7])
move('x1',a_j); move('x4',a_j); init('j',a_j); add('j','x1'); add('j','x4')
move('j',b_j); move('y7',b_j); add('y7','j'); move('y8',b_j); add('y8','j')   # deposit (odd) + carrier load (even cells)
init('k',a_k); move('y8',a_k); add('k','y8')                                   # carrier ascends b_j -> a_k (free public climb)
move('x2',a_k); add('k','x2'); move('k',b_k); move('y11',b_k); add('y11','k'); move('y14',b_k); add('y14','k')
for p in ports:
    if chart['x%d'%p]!=V: move('x%d'%p,V)
    if chart['y%d'%p]!=perp(p): move('y%d'%p,perp(p))
print('owned ascent R =',own_move[0],' owned descent D =',own_move[1])
na=[1,2,4,7,11,14]
odd={(t,p):reg['y%d'%t].get('x%d'%p,0) for t in na for p in na if t!=p and dot(t,p)}
print('NA(ii) off-diagonal odd cells:',{k:str(v) for k,v in odd.items() if True})
want={(7,1),(7,4),(11,1),(11,2),(14,2),(14,4)}
print('match NA(ii):', all((odd[c]!=0)==(c in want) for c in odd) and all(odd[c]==1 for c in want))
print('y8 final cells (8,p) parity:',[(p,dot(8,p),str(v)) for k,v in reg['y8'].items() for p in [int(k[1:])]])
