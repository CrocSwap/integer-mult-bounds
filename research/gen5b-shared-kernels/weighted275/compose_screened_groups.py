"""Two deterministic overlap-pruning orders for the three screened line groups."""
from pathlib import Path
from collections import Counter
import gzip,json,math,hashlib
from source_data import ROOT,SOURCE,OUTPUT
CACHE=json.loads(gzip.decompress((OUTPUT/'response-cache.json.gz').read_bytes()))
FRAMES=json.loads(gzip.decompress((SOURCE/'gen5bit/selected/bit/frames_p12.json.gz').read_bytes()))['frames']
def members(entries):return {r for e in entries for r in[e['virtual_pivot']]+e['virtual_donors']}
def phi(r):return r*math.log(120/r)if r else 0
def dim(r):return FRAMES[str(CACHE['roles'][str(r)]['first_base_use']['frame'])]['dim']
def ledger(entries):
 ps={e['virtual_pivot']for e in entries};ds={r for e in entries for r in e['virtual_donors']};assert not ps&ds and len(ps)==len(entries)
 h=Counter()
 for r in ps|ds:
  d=dim(r);h[d]-=1
  if d>1:h[d-1]+=1
 h[1]+=len(ds);h={r:n for r,n in sorted(h.items())if n}
 assert sum(r*n for r,n in h.items())==-len(ps)
 return h,len(ds)
def run():
 groups={n:json.loads((ROOT/f'candidate-line{n}.json').read_text())for n in ('16-17','6-7','2-3')}
 receipts=[]
 for name,left,right in [('keep136','16-17','6-7'),('keep36','6-7','16-17')]:
  accepted=groups[left]['entries'][:];used=members(accepted);remaining=[e for e in groups[right]['entries']if not members([e])&used]
  omitted=[e['virtual_pivot']for e in groups[right]['entries']if members([e])&used];parity=None
  extras=groups['2-3']['entries'];assert not members(extras)&(used|members(remaining))
  if(len(accepted)+len(remaining)+len(extras))%2:
   counts=Counter(r for e in remaining for r in e['virtual_donors'])
   def marginal(e):
    benefit=phi(dim(e['virtual_pivot']))-phi(dim(e['virtual_pivot'])-1)
    release=sum(phi(1)+phi(dim(r)-1)-phi(dim(r))for r in e['virtual_donors']if counts[r]==1)
    return(round((benefit-release)*10**9),e['virtual_pivot'])
   parity=min(remaining,key=marginal);remaining=[e for e in remaining if e is not parity]
  entries=accepted+remaining+extras;H,D=ledger(entries)
  out=dict(source_head='10b40041d4ab8a6610083e95bc571aee3468bca2',selection=name,pivots=len(entries),entries=entries,
    deterministic_pruning=dict(priority_line=left,secondary_line=right,overlap_omitted_pivots=omitted,parity_omitted_pivot=parity['virtual_pivot']if parity else None,parity_rule='Lowest rounded10^9 first-order marginal gain, ties by logical pivot ID.'),
    local_histogram_delta=H,residual_family_delta={24:-len(entries),23:len(entries)},distinct_donors=D,
    scalar_setup_pairs=sum(len(e['donors'])for e in entries),phi_delta=sum(n*phi(r)for r,n in H.items()),
    scope='Deterministic disjoint support pruning of three already screened line groups. Exact F2 relations and first-frame ledger only; full combined alias/scalar/frame/norm/chart/bank admission required; no final12.')
  file=OUTPUT/f'candidate-combined{len(entries)}-{name}.json';file.write_text(json.dumps(out,indent=2)+'\n')
  receipts.append(dict(file=file.name,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),**{k:v for k,v in out.items()if k!='entries'}))
 (OUTPUT/'combined-screen-summary.json').write_text(json.dumps(receipts,indent=2)+'\n');print(json.dumps(receipts,indent=2))
if __name__=='__main__':run()
