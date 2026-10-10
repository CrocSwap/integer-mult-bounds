"""Freeze restore-selection.json: the early-restoration helpers of the gen5 word after the descent, target-square,
kernel and second-descent stages. Census from the actual word: at the first cleanup ADD, helpers of current dimension 22
whose only later scalar incidence is one write a -= c*b with an unwritten donor b of dimension 22 and a nondegenerate
23-dimensional rational span. Usage: python3 -B discovery/build_restore_selection.py [OUT]"""
import sys,json,importlib.util,hashlib,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;PKG=HERE.parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
ctx=load('g_prepare',PKG/'prepare.py').prepare()
producer=load('g_phys',PKG/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT'])
producer=load('g_parity',PKG/'parity_transform.py').run(producer)
dmod=load('g_descent',PKG/'descent_transform.py');producer=dmod.run(producer)
producer=load('g_target',PKG/'target_transform.py').run(producer)
producer=load('g_kernel',PKG/'kernel_transform.py').run(producer)
producer=dmod.run(producer,selection_path=PKG/'descent2-selection.json')
W,C=producer['W'],producer['C'];v=W.v;old=producer['records'];initial=producer['initial_state'];n=len(initial);FULL=producer['FULL']
cats=producer['physical']['category_names'];cleanup=cats.index('cleanup_gate')
cut=next(k//6 for k in range(0,len(old),6)if old[k]==1 and old[k+5]==cleanup)
state=dict(initial);atcut=None;later={};written_after={}
for k in range(0,len(old),6):
    op,a,b,c,f,z=old[k:k+6];i=k//6
    if i==cut:atcut=dict(state)
    if op==0:state[a]=c;continue
    if op==2:state[b]=f;continue
    if op==3:del state[b];continue
    if i>=cut:
        later.setdefault(a,[]).append(('w',b,i));written_after.setdefault(a,[]).append(i)
        later.setdefault(b,[]).append(('r',a,i))
sha_basis=lambda B:hashlib.sha256(json.dumps(B,separators=(',',':')).encode()).hexdigest()
entries=[];donors=set();rej=collections.Counter()
for a in range(2*v,n):
    g=later.get(a)
    if not g or atcut.get(a) is None:continue
    if len(g)!=1 or g[0][0]!='w':rej['other later incidence']+=1;continue
    _,b,i=g[0]
    if b==n or b in donors or b in later and any(x[0]=='w' for x in later[b] if x[2]<i):rej['donor written or reused']+=1;continue
    if any(cut<=w<i for w in written_after.get(b,[])):rej['donor written']+=1;continue
    fa,fb=atcut[a],atcut[b]
    if C.dimf[fa]!=22 or C.dimf[fb]!=22:rej['dimensions']+=1;continue
    E=W.register(C.B[fa]+C.B[fb])
    if C.dimf[E]!=23 or not C.nondeg(E):rej['span full or degenerate']+=1;continue
    op,x,y,c,f,z=old[6*i:6*i+6];assert op==1 and (x,y)==(a,b) and f==FULL
    entries.append(dict(record=i,helper=a,donor=b,scalar=[a,b,c,z],entrance_dimension=C.dimf[initial[a]],helper_dimension=22,donor_dimension=22,end_dimension=23,end_basis_sha256=sha_basis(C.B[E])));donors.add(b)
print('cut',cut,'entries',len(entries),'rejections',dict(rej))
# expected histogram delta: per entry two rank-2 climbs (a 22->24, b 22->24) become three rank-1 climbs (a->E, b->E, b E->FULL)
delta={'1':3*len(entries),'2':-2*len(entries)}
sel=dict(status='FROZEN_EARLY_RESTORATION_SELECTION',provenance='discovery/build_restore_selection.py on the gen5 word after the descent, target-square, kernel and second-descent stages (PR280 early-restoration rule generalised to the actual word). Prepared by Rohan Arun with Anthropic Claude assistance.',
    input_raw_sha256=hashlib.sha256(old.tobytes()).hexdigest(),input_scalar_sha256=producer['physical']['scalar_projection_sha256'],source_record_count=len(old)//6,cut_record=cut,
    selected_helper_count=len(entries),expected_local_histogram_delta=delta,expected_rank_mass=producer['physical']['paid_rank_mass']-len(entries),expected_added_calls=len(entries),expected_scalar_additions=producer['physical']['weighted_scalar_events'],entries=sorted(entries,key=lambda e:e['record']))
(Path(sys.argv[1]) if len(sys.argv)>1 else PKG/'restore-selection.json').write_text(json.dumps(sel,indent=1)+'\n')
print('wrote',len(entries),'entries; delta',delta,'rank mass',sel['expected_rank_mass'])
