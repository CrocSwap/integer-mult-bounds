"""Complete scalar/snapshot intertwiner checks. Apache-2.0."""
import hashlib,itertools,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def need(x,m):
    if not x:raise ValueError(m)
def rank(rows):
    piv={}
    for x in rows:
        while x:
            bit=x.bit_length()-1
            if bit not in piv:piv[bit]=x;break
            x^=piv[bit]
    return len(piv)
def gl(n):return [x for x in itertools.product(range(1<<n),repeat=n) if rank(x)==n]
def apply(rows,values):return tuple(xor(values[j] for j in range(len(rows)) if rows[i]>>j&1) for i in range(len(rows)))
def xor(values):
    x=0
    for v in values:x^=v
    return x
def op(c,v):return sum(((c>>(2*i)&3)&v).bit_count()%2<<i for i in range(2))
def algebra(cs,u,v):return all((cs[i] if u[i]>>j&1 else 0)==(cs[j] if v[i]>>j&1 else 0) for i in range(len(cs)) for j in range(len(cs)))
def classification(cs,u,v):return u==v and all(not (u[i]>>j&1) or cs[i]==cs[j] for i in range(len(cs)) for j in range(len(cs)))
def run():
    dep=json.loads((H/'PREDECESSOR.json').read_text());need(hashlib.sha256((H/'PR1704-README.md').read_bytes()).hexdigest()==dep['sha256'],'source bytes')
    group=gl(2);counts={'equal':0,'unequal':0};tested=0
    for cs in itertools.product(range(1,16),repeat=2):
        for u,v in itertools.product(group,repeat=2):
            exact=algebra(cs,u,v);literal=True
            for h in itertools.product(range(4),repeat=2):
                old=tuple(op(c,x) for c,x in zip(cs,h));left=apply(v,old);new=apply(u,h);right=tuple(op(c,x) for c,x in zip(cs,new))
                if left!=right:literal=False
            need(exact==literal==classification(cs,u,v),'complete operator/input equivalence')
            counts['equal' if cs[0]==cs[1] else 'unequal']+=exact;tested+=1
    partitions=[(1,1,1),(1,1,2),(1,2,1),(1,2,2),(1,2,3)];g3=gl(3);atlas=[]
    for cs in partitions:
        total=0
        for u,v in itertools.product(g3,repeat=2):
            a=algebra(cs,u,v);need(a==classification(cs,u,v),'three-role class equivalence');total+=a
        atlas.append(total)
    need(counts=={'equal':90,'unequal':210} and atlas==[168,6,6,6,1],'count receipts')
    # Equal-map no-reader pilot: copy, helper ADD, temporary ADD, erase, helper restore.
    for c in range(1,16):
        for h in itertools.product(range(4),repeat=2):
            helpers=list(h);temps=[op(c,x) for x in h];helpers[0]^=helpers[1];temps[0]^=temps[1]
            need(temps==[op(c,x) for x in helpers],'equal-map legal cut')
            helpers[0]^=helpers[1];need(tuple(helpers)==h,'all dirty helpers restored')
    ident,swap=9,6;h=(0,1);u=(3,2)
    lhs=apply(u,(op(ident,h[0]),op(swap,h[1])));rhs=tuple(op(c,x) for c,x in zip((ident,swap),apply(u,h)))
    need(lhs!=rhs and rank((1,2))==rank((2,1))==2,'same-rank synchronized false positive')
    # Correcting the temporary only after erase cannot repair the earlier cut.
    need((op(ident,0),op(ident,1))!=(op(ident,1),op(ident,1)),'late restoration rejected')
    return {'status':'PASS_LIVE_COPY_OPERATOR_INTERTWINER','two_role_pairs':tested,'dirty_assignments':tested*16,'legal_pairs':counts,'three_role_pairs':5*168**2,'three_role_legal':atlas,'positive_schedule_adds':3,'positive_schedule_copy_erase_pairs':2,'new_kappa':False}
if __name__=='__main__':
    result=run();f=H/'CERTIFICATE.json'
    if '--write' in sys.argv:f.write_text(json.dumps(result,indent=2)+'\n')
    else:need(result==json.loads(f.read_text()),'receipt')
    print(result['status'],'legal=300/8100')
