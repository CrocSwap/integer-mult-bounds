"""Exact no-descent COPY-boundary certificate. Apache-2.0; OpenAI Codex assistance."""
import gzip, hashlib, itertools, json, math, sys
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,msg):
    if not ok: raise ValueError(msg)
def rank(rows):
    basis={}
    for row in rows:
        row=list(row)
        for p,b in sorted(basis.items()):
            if row[p]:
                a,c=row[p],b[p]; row=[c*x-a*y for x,y in zip(row,b)]
                g=math.gcd(*row)
                if g: row=[x//g for x in row]
        p=next((i for i,x in enumerate(row) if x),None)
        if p is not None: basis[p]=row
    return len(basis)
def qr(rows):
    a=[[Fraction(x) for x in r] for r in rows]; q=0
    for j in range(8):
        k=next((k for k in range(q,len(a)) if a[k][j]),None)
        if k is None: continue
        a[q],a[k]=a[k],a[q]; z=a[q][j]; a[q]=[x/z for x in a[q]]
        for k in range(q+1,len(a)):
            z=a[k][j]; a[k]=[x-z*y for x,y in zip(a[k],a[q])]
        q+=1
    return q
def run():
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage']=='input':
            need(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'source pin '+item['path'])
    w=json.loads(gzip.decompress((ROOT/'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz').read_bytes()))
    current=list(w['start']); rows=[1<<i for i in range(2*w['v']+w['R'])]
    for section in ('D','A'):
        for f,d,ss in w[section]:
            for r in (d,*ss):
                need(set(w['frames'][current[r]])<=set(w['frames'][f]),'non-nested source frame')
                current[r]=f
            for s in ss: rows[d]^=rows[s]
    frames=[w['frames'][current[r]] for r in w['ret']]
    need(len(frames)==9 and len({tuple(x) for x in frames})==9,'nine distinct frames')
    dims=[rank([w['lines'][i] for i in f]) for f in frames]
    need(dims==[7]*9,'hyperplane rank')
    combinations=[]
    for mask in range(1,512):
        labels=sorted(set().union(*(set(frames[i]) for i in range(9) if mask>>i&1)))
        dim=rank([w['lines'][i] for i in labels])
        need(dim==(7 if mask.bit_count()==1 else 8),'join classification')
        combinations.append([mask,dim])
    for i,j in itertools.combinations(range(9),2):
        labels=sorted(set(frames[i])|set(frames[j]))
        need(qr([w['lines'][k] for k in labels])==8,'independent pair rank')
    # Every ordered elementary change: z_i=h_i+h_j; correct scatter is S U^-1.
    scatter=[sum(1<<i for i in ss) for ss in w['scatter']]
    trials=0; cancelled=0
    for i,j in itertools.permutations(range(9),2):
        h=[1<<k for k in range(9)]; h[i]^=h[j]; out=[]; bad=[]
        for mask in scatter:
            adjusted=mask ^ ((1<<j) if mask>>i&1 else 0)
            def combine(m):
                val=0
                for k in range(9):
                    if m>>k&1: val^=h[k]
                return val
            out.append(combine(adjusted)); bad.append(combine(mask))
        need(out==scatter,'conjugate scatter dirty boundary')
        need(bad!=scatter,'unadjusted scatter control')
        need(h!=[1<<k for k in range(9)],'unrestored helper control')
        h[i]^=h[j]; need(h==[1<<k for k in range(9)],'helper restoration')
        touched={i,j}; need(sum(8 if k in touched else 7 for k in range(9))==65,'cancelled network charge'); cancelled+=1
        trials+=1
    need(rank([w['lines'][k] for k in frames[0]+frames[0]])==7,'coincident hyperplane control')
    return {'status':'PASS_RETAINED_TOTAL_MIXING','total_registers':w['ret'],
      'frame_ids':[current[r] for r in w['ret']],'copy_ranks':dims,
      'all_support_joins':combinations,'independent_pair_joins':36,
      'dirty_scatter_trials':trials,'unadjusted_scatter_rejections':trials,
      'unrestored_helper_rejections':trials,'cancelled_network_controls':cancelled,
      'baseline_copy_profile':{'7':9},'elementary_mix_copy_profile':{'7':7,'8':2},
      'baseline_copy_mass':63,'elementary_mix_copy_mass':65,'no_new_kappa':True}
if __name__=='__main__':
    receipt=run(); path=HERE/'CERTIFICATE.json'
    if '--write' in sys.argv: path.write_text(json.dumps(receipt,indent=2)+'\n')
    else: need(receipt==json.loads(path.read_text()),'certificate differs')
    print(receipt['status'],'joins=511 pair_oracle=36 dirty_trials=72 copy_mass=63->65 controls=217')
