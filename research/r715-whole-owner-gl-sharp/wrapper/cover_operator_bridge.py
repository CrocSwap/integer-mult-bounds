"""Finite cover-owner bridge, independently checked on PR471's pinned witness.

New bridge checker by OpenAI Codex; source construction/normalization is Dugongue
PR471, with inherited chafreaky/DaysSky/icekylinx sources kept separately.
This checks exact witness injection and a complete small-cover operator on all
dirty basis columns. It does not enumerate the O(89,2) cover or prove all-size
compiler and analytic contracts.
"""
import gzip, hashlib, json, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def read(path):
    b = path.read_bytes()
    return json.loads(gzip.decompress(b) if path.suffix == '.gz' else b)

def owner_injection(t, phases):
    full = []
    for p in phases['recipes']:
        bs = tuple(sorted({p['q']} | {v for c in p['idle_children'] for v in c['orthogonal_axes']}))
        assert len(bs) == 89
        assert all(((a & b).bit_count() & 1) == (i == j) for i,a in enumerate(bs) for j,b in enumerate(bs))
        full.append(bs)
    idle = {x['idx']:x for x in t['execution_schedule'] if x['kind']=='idle'}
    total = duplicate_families = max_multiplicity = 0
    digest = hashlib.sha256()
    for call in t['calls']:
        owners = set(); footprints = defaultdict(set); multiplicity = Counter()
        active_families = {x[0] for x in call['owners'][:240]}
        assert len(active_families) == 240
        for h,(family, route) in enumerate(call['owners'][240:]):
            kind,i,off,foot,w,spec = route
            assert kind==5 and foot==9 and w in (8,9)
            assert family not in active_families
            pair,sp = divmod(family % 1200,240);side,port=divmod(sp,120)
            assert pair == idle[i]['pair']
            phase = phases['recipes'][port]['idle_children'][idle[i]['phase_children'][side]]
            active = phase['orthogonal_axes'][off:off+w]
            fp = tuple(active + ([spec] if w==8 else []))
            assert len(fp)==len(set(fp))==9 and set(fp)<=set(full[port])
            assert not footprints[family].intersection(fp)
            footprints[family].update(fp)
            sigma = fp + tuple(v for v in full[port] if v not in fp)
            assert len(sigma)==89 and set(sigma)==set(full[port])
            owner = (family, sigma)
            assert owner not in owners, 'same actual owner for every cover d'
            owners.add(owner);multiplicity[family]+=1;total+=1
            digest.update(json.dumps([call['stage'],call['replica'],h,family,sigma],separators=(',',':')).encode()+b'\n')
        assert len(owners)==560
        duplicate_families += sum(n-1 for n in multiplicity.values())
        max_multiplicity=max(max_multiplicity,max(multiplicity.values()))
    assert total==43120
    return dict(status='PASS_EXACT_WHOLE_COVER_OWNER_INJECTION',calls=len(t['calls']),helpers=total,
                same_family_additional_roles=duplicate_families,max_helpers_per_family_per_call=max_multiplicity,
                sigma_stream_sha256=digest.hexdigest(),
                proof='For fixed d, (f,d*sigma^-1) equality implies equal f and sigma by group cancellation. Each checked sigma is an orthonormal full-basis permutation.')

class Matrix:
    """Gaussian integer numerator matrix over one common power-of-two denominator."""
    def __init__(self):
        self.n=96;self.a=[[int(i==j) for j in range(96)] for i in range(112)]
        self.b=[[0]*96 for _ in range(112)];self.den=0
    def add(self,dst,src,c=1):
        a,b=self.a,self.b
        # These are whole arrays with independent address cells, including alias controls.
        aa=[r[:] for r in a[src:src+16]];bb=[r[:] for r in b[src:src+16]]
        for x in range(16):
            a[dst+x]=[u+c*v for u,v in zip(a[dst+x],aa[x])]
            b[dst+x]=[u+c*v for u,v in zip(b[dst+x],bb[x])]
    def copy(self,dst,src):
        assert all(not any(r) for r in self.a[dst:dst+16]+self.b[dst:dst+16])
        self.a[dst:dst+16]=[r[:] for r in self.a[src:src+16]]
        self.b[dst:dst+16]=[r[:] for r in self.b[src:src+16]]
    def erase(self,dst,src):
        assert self.a[dst:dst+16]==self.a[src:src+16] and self.b[dst:dst+16]==self.b[src:src+16]
        self.a[dst:dst+16]=[[0]*96 for _ in range(16)]
        self.b[dst:dst+16]=[[0]*96 for _ in range(16)]
    def phase(self,base,axis,sign):
        for x in range(16):
            if x>>axis&1:
                aa=self.a[base+x];bb=self.b[base+x]
                self.a[base+x]=[-sign*z for z in bb];self.b[base+x]=[sign*z for z in aa]
    def swap_axes(self,base,i,j):
        aa=[r[:] for r in self.a[base:base+16]];bb=[r[:] for r in self.b[base:base+16]]
        for x in range(16):
            y=x ^ (((x>>i&1) ^ (x>>j&1))*((1<<i)|(1<<j)))
            self.a[base+x]=aa[y];self.b[base+x]=bb[y]
    def C(self,base,axis):
        aa=[r[:] for r in self.a[base:base+16]];bb=[r[:] for r in self.b[base:base+16]]
        self.a=[[2*z for z in r] for r in self.a]
        self.b=[[2*z for z in r] for r in self.b];self.den+=1
        for x in range(16):
            y=x^(1<<axis)
            self.a[base+x]=[a-b+c+d for a,b,c,d in zip(aa[x],bb[x],aa[y],bb[y])]
            self.b[base+x]=[b+a+d-c for a,b,c,d in zip(aa[x],bb[x],aa[y],bb[y])]
    def equals(self,other):
        d=max(self.den,other.den)
        return all((x<<(d-self.den))==(y<<(d-other.den)) for A,B in ((self.a,other.a),(self.b,other.b)) for a,b in zip(A,B) for x,y in zip(a,b))

def complete_toy(orientation,mutation=None):
    # G={1,s}, with s swapping (0,1) and (2,3). Helpers share family H,
    # sigma_1=1 and sigma_2=s: at cover d owners are H_d,H_(d*s).
    z=Matrix();sgn=-1 if orientation=='forward' else 1
    for d in range(2):
        source=16*d if orientation=='forward' else 32+16*d
        target=32+16*d if orientation=='forward' else 16*d
        h1,h2=64+16*d,64+16*(d^1)
        if mutation=='alias-cover-owner':h2=h1
        axis,spectator=2*d,2*d+1
        # R^-1 before all scalar operations. Phi=L*C*R follows cleanup;
        # L^-1 is last. The complete helper endpoint is C tensor I.
        for h in (h1,h2):
            if mutation!='omit-entry-wrapper':z.phase(h,spectator,-1)
        z.copy(96,source)
        z.add(h1,h2)
        z.add(target,h1,-sgn)
        z.add(h1,96)
        z.add(target,h1,sgn)
        if mutation!='omit-dirty-restoration':z.add(h1,96,-1)
        z.add(h1,h2,-1)
        z.erase(96,source)
        for h in (h1,h2):
            z.phase(h,spectator,1);z.C(h,axis);z.swap_axes(h,axis,spectator)
            if mutation!='omit-exit-wrapper':z.swap_axes(h,axis,spectator)
    # Remaining child acts on the untouched spectator coordinates.
    if mutation!='omit-idle-remainder':
        for h in (64,80):
            z.C(h,1);z.C(h,3)
    expected=Matrix()
    for d in range(2):
        source=16*d if orientation=='forward' else 32+16*d
        target=32+16*d if orientation=='forward' else 16*d
        expected.add(target,source,sgn)
    for h in (64,80):
        for axis in range(4):expected.C(h,axis)
    return z.equals(expected)

def main():
    t=read(Path(sys.argv[1]));phase=read(Path(sys.argv[2]));out=Path(sys.argv[3])
    result=owner_injection(t,phase)
    mutations=['alias-cover-owner','omit-entry-wrapper','omit-exit-wrapper','omit-dirty-restoration','omit-idle-remainder']
    for orientation in ('forward','backward'):
        assert complete_toy(orientation)
        for m in mutations:assert not complete_toy(orientation,m),(orientation,m)
    result['toy']=dict(status='PASS_EXACT_GAUSSIAN_DYADIC_FULL_OPERATOR',cover_classes=2,ambient_axes=4,
                       independent_dirty_columns=96,orientations=2,scalar_adds_copies_erases_included=True,
                       same_family_helpers=2,restored_spectators=True,mutations_rejected=mutations)
    result['scope']='Exact candidate owner injection plus complete toy operator; actual candidate local dirty rows and full512-column normalizers checked separately. Does not enumerate the enormous cover or certify all-size analytic assumptions.'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
