"""Independent full primitive matrix replay on an exact dyadic grid."""
from fractions import Fraction as Q
N=725
S=1<<32
def index(ref):
    kind,i=ref
    if not (type(i) is int and ((kind=='L' and 0<=i<716) or (kind=='C' and 0<=i<8) or (kind=='W' and i==0))):
        raise ValueError('invalid physical scalar reference')
    return i if kind=='L' else 716+i if kind=='C' else 724
def replay(primitives,backward):
    rows=[[S*int(i==j) for j in range(N)] for i in range(N)]
    env=[Q(1)]*N;peak=Q(1);counts={}
    for op in primitives:
        tag=op[0];t=index(op[1]);counts[tag]=counts.get(tag,0)+1
        if tag=='clear':rows[t]=[0]*N;env[t]=Q(0)
        elif tag=='copy':s=index(op[2]);rows[t]=rows[s][:];env[t]=env[s]
        elif tag=='double':rows[t]=[2*x for x in rows[t]];env[t]*=2
        elif tag=='halve':
            if any(x%2 for x in rows[t]):raise ValueError('fixed grid not exact')
            rows[t]=[x//2 for x in rows[t]];env[t]/=2
        elif tag=='negate':rows[t]=[-x for x in rows[t]]
        elif tag in ('add','subtract'):
            s=index(op[2]);sign=1 if tag=='add' else -1
            rows[t]=[a+sign*b for a,b in zip(rows[t],rows[s])];env[t]+=env[s]
        else:raise ValueError('unknown primitive')
        peak=max(peak,env[t])
    for i,row in enumerate(rows):
        expected=[0]*N
        if i<716:expected[i]=S
        if backward and i<112:expected[112+i]=-S
        if not backward and 112<=i<224:expected[i-112]=S
        if row!=expected:raise ValueError('complete primitive endpoint row '+str(i))
    return {'columns':N,'primitive_count':sum(counts.values()),'primitive_counts':counts,
            'positive_prefix':str(peak),'positive_prefix_bits':peak.numerator.bit_length()-peak.denominator.bit_length()+1,
            'exact_grid_denominator_power':32}


def panel_replay(panel,targets,helpers,C,backward):
    refs=targets+helpers;lookup={r:i for i,r in enumerate(refs)};n=len(refs)
    rows=[[Q(int(i==j)) for j in range(n)] for i in range(n)]
    for op in panel:
        tag,t=op[:2];t=lookup[t]
        if tag=='scale':
            q=Q(op[2],op[3]);q=1/q if backward else q
            rows[t]=[q*x for x in rows[t]]
        elif tag=='add':
            s=lookup[op[2]];q=Q(op[3],op[4])
            if backward:t,s,q=s,t,-q
            rows[t]=[a+q*b for a,b in zip(rows[t],rows[s])]
        else:raise ValueError('panel opcode')
    nt=len(targets)
    for i,row in enumerate(rows):
        expected=[Q(int(i==j)) for j in range(n)]
        if not backward and i<nt:
            for j,x in enumerate(C[i]):expected[nt+j]+=Q(x,8)
        if backward and i>=nt:
            for j in range(nt):expected[j]-=Q(C[j][i-nt],8)
        if row!=expected:raise ValueError('panel arbitrary-input endpoint')
    return {'columns':n,'orientation':'inverse_transpose' if backward else 'forward'}
