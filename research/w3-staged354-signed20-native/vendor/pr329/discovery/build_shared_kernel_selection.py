"""Freeze kernel-selection.json from a shared-donor closure search result (discovery/coll/closure_pack.py), bound to
the fresh p = 10 word after the stages before the kernel stage (portable_bit.STAGES). Each search entry is
{pivot, donors, basis (E rows) or line}; the cut read is read off this word and the expected one-stage histogram
delta off the emitted word. A later kernel round would use TAG = kernel2 (kernel_transform.run(..., tag=TAG)).
Not run by verify.py.
Usage: python3 -B discovery/build_shared_kernel_selection.py SEARCH.json [TAG]
Chafik Boukhalfa (chafreaky), Anthropic Claude assistance; Apache-2.0."""
import sys,json,importlib.util,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
TAG=sys.argv[2] if len(sys.argv)>2 else 'kernel'
ctx=load('portable527_prepare',ROOT/'prepare.py').prepare()
run=load('portable527_physical',ROOT/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT'],output_dir=None)
run=load('portable527_parity',ROOT/'parity_transform.py').run(run)
STAGES=load('portable527_bitstages',ROOT/'portable_bit.py').STAGES;assert TAG in STAGES
kt=load('portable527_kernel_any',ROOT/'kernel_transform.py');rm=load('portable527_reorder',ROOT/'reorder_transform.py')
for st in STAGES[:STAGES.index(TAG)]:
    if st.startswith('reorder'):run=rm.run(run,tag=st)
    elif st.startswith('kernel'):run=kt.run(run,tag=st)
    else:run=load('portable527_'+st,ROOT/(st+'_transform.py')).run(run)
W=run['W'];v=W.v;n=2*v+len(run['context']['regs']);old=run['records'];cats=run['physical']['category_names'];readcat=cats.index('dirty_read');ZERO=run['ZERO']
lastread={}
for k in range(0,len(old),6):
    op,a,b,c,f,z=old[k:k+6]
    if op==1 and z==readcat and f==ZERO and v<=a<2*v and c%2:lastread[b]=k//6
src=json.loads(Path(sys.argv[1]).read_text());families=[]
for e in src:
    basis=e.get('basis') or [e['line']];ms=[e['pivot']]+list(e['donors']);cut=max(lastread[s]for s in ms)
    families.append(dict(pivot=e['pivot'],donors=list(e['donors']),cut_read=[old[6*cut+j]for j in(1,2,3)],rank=len(basis),basis=basis,kind='shared-donor-rank%d'%len(basis)))
sel=dict(status='P10_SHARED_DONOR_KERNEL_ENTRIES',tag=TAG,provenance='discovery/coll (lines.py/planes.py + closure_pack.py: per-entrance maximum-weight closure over alternate response bases; shared donors after PR319) on the p = 10 word after '+'/'.join(STAGES[:STAGES.index(TAG)])+'; prepared with Anthropic Claude assistance',n=n,v=v,input_raw_sha256=hashlib.sha256(old.tobytes()).hexdigest(),input_scalar_sha256=run['physical']['scalar_projection_sha256'],selected_pairs=0,selected_families=len(families),expected_local_delta={},pairs=[],families=families)
out,initial,final,entries,execution,cats2,proof,n2,v2=kt.transform(run,sel,TAG)
hist=collections.Counter()
for k in range(0,len(out),6):
    if out[k]==0 and out[k+4]:hist[out[k+4]]+=1
    elif out[k]==2:hist[out[k+5]]+=1
delta=collections.Counter(hist);delta.subtract({int(r):c for r,c in run['physical']['paid_histogram'].items()})
sel['expected_local_delta']={str(r):c for r,c in sorted(delta.items())if c}
sel['entrance_rank_histogram']={str(r):c for r,c in sorted(proof['entrance_rank_histogram'].items())};sel['total_entrance_rank']=proof['total_entrance_rank'];sel['donor_sharing_histogram']=proof['donor_sharing_histogram']
assert sel['total_entrance_rank']%5==0,'total entrance rank must be a multiple of 5 for the m = 100 bank tiling'
import math;phi=lambda r:r*math.log(100/r)
(ROOT/(TAG+'-selection.json')).write_text(json.dumps(sel,indent=1)+'\n')
print('wrote',TAG,len(families),'entries; rank',proof['total_entrance_rank'],'delta',sel['expected_local_delta'],'phi %.3f'%sum(c*phi(int(r))for r,c in sel['expected_local_delta'].items()),'sharing',proof['donor_sharing_histogram'])
