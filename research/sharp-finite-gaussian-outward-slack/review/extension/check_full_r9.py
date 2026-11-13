"""Independent dense-vertex verification of the radius-nine optimum."""
from pathlib import Path
from types import ModuleType
from itertools import product
import hashlib,json,sys

SOURCE=Path(__file__).with_name('full_graph_library.py')
M=ModuleType('independent_full_graph_library');M.__file__=str(SOURCE)
exec(compile(SOURCE.read_bytes(),str(SOURCE),'exec'),M.__dict__)
PAIR=(78,73);RADIUS=9
LO,HI=M.gap_interval(*PAIR)
def strict(a,b):
    if a<=b:return True
    if (a,b)==PAIR:return False
    lo,hi=M.gap_interval(a,b)
    if hi<LO:return True
    if lo>HI:return False
    raise ValueError(('unseparated exact radical gaps',a,b))
def signature(points):
    h=hashlib.sha256()
    for point in sorted(points):h.update((','.join(map(str,point))+'\n').encode())
    return h.hexdigest()
def main():
    r=RADIUS;r2=r*r
    pairs=[(a,b) for a in range(-r,r+1) for b in range(-r,r+1) if a*a+b*b<=r2]
    xs=sorted((a,b,c,d) for a,b in pairs for c,d in pairs if a*a+b*b+c*c+d*d<=r2)
    all_edges=[tuple(M.candidates(x)) for x in xs]
    graph=[tuple(y for y in ys if strict(M.n2(y),M.n2(x))) for x,ys in zip(xs,all_edges)]
    matching,left,right,rounds=M.maximum_matching(graph)
    T={xs[i] for i in left}
    M.need(len(T)-len(right)==64,'strict radius-nine Hall deficiency')
    M.need(right=={y for x in T for y in M.candidates(x) if strict(M.n2(y),M.n2(x))},'complete lifted Hall neighborhood')
    inclusive=[tuple(y for y in ys if strict(M.n2(y),M.n2(x)) or (M.n2(y),M.n2(x))==PAIR) for x,ys in zip(xs,all_edges)]
    plus,lp,rp,prounds=M.maximum_matching(inclusive)
    M.need(all(y is not None for y in plus) and not lp and not rp,'attaining full injection')
    equality=sum((M.n2(y),M.n2(x))==PAIR for x,y in zip(xs,plus))
    M.need(equality>0,'attaining threshold edge present')
    rows=[]
    from collections import Counter
    for kind,points in [('input_cut',T),('output_cut',right)]:
        counts=Counter(M.dtype(x) for x in points)
        rows.append({'side':kind,'orbits':[{'absolute_coordinates':k[0],'negative_product':k[1],'size':n} for k,n in sorted(counts.items())]})
    result={'marker':'PASS_INDEPENDENT_FULL_RADIUS_NINE_OPTIMUM','radius':r,'threshold_pair':PAIR,
            'inputs':len(xs),'complete_error_one_edges':sum(map(len,all_edges)),
            'strict_edges':sum(map(len,graph)),'inclusive_edges':sum(map(len,inclusive)),
            'strict_matching':sum(y is not None for y in matching),'strict_cut_inputs':len(T),'strict_cut_outputs':len(right),'deficiency':len(T)-len(right),
            'inclusive_matching':len(plus),'attaining_edges':equality,'augmenting_rounds':[rounds,prounds],
            'cut_input_sha256':signature(T),'cut_output_sha256':signature(right),
            'matching_sha256':signature(tuple(x)+tuple(y) for x,y in zip(xs,plus)),
            'orbit_counts':rows,'library_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'independence':'full individual-vertex matching and rational radical intervals; imports no author orbit-flow code, receipts or certificates',
            'negative_control':'strict predecessor graph has deficit64; equality edges restore a full injection',
            'scope':'finite radius-nine optimum and global necessary lower bound only; no global sufficiency'}
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
