"""Freeze kernel-selection.json from a pack selection (pairs + families), bound to the fresh p = 10 word after the
descent and target-square stages. The expected one-stage histogram delta is read off the emitted word.
Adapted from PR #299/#308 discovery/build_selection.py. Usage: build_kernel_selection.py PKG PACKED_SELECTION.json OUT"""
import sys,json,importlib.util,hashlib,collections
from pathlib import Path
PKG=Path(sys.argv[1]).resolve();sys.path.insert(0,str(PKG))
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
ctx=load('g_prepare',PKG/'prepare.py').prepare()
producer=load('g_phys',PKG/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT'])
producer=load('g_parity',PKG/'parity_transform.py').run(producer)
producer=load('g_descent',PKG/'descent_transform.py').run(producer)
producer=load('g_target',PKG/'target_transform.py').run(producer)
W=producer['W'];v=W.v;n=2*v+len(producer['context']['regs'])
src=json.loads(Path(sys.argv[2]).read_text())
keep=lambda d,ks:{k:d[k]for k in ks if k in d}
pairs=[keep(p,('a','b','cut_read','rank','basis','first_frame_dims','phi_gain'))for p in src['pairs']]
families=[keep(f,('pivot','donors','cut_read','rank','basis','first_frame_dims','phi_gain','kind','gram_det'))for f in src.get('families',[])]
sel=dict(status='P10_KERNEL_ENTRIES_PER_ENTRY_CUTS',provenance='p10/tools/coll (families.py + pack_restarts.py, adapted from gen4coll/#300/#308) on the p = 10 word after the descent + target squares; prepared with Anthropic Claude assistance',n=n,v=v,input_raw_sha256=hashlib.sha256(producer['records'].tobytes()).hexdigest(),input_scalar_sha256=producer['physical']['scalar_projection_sha256'],selected_pairs=len(pairs),selected_families=len(families),expected_local_delta={},pairs=pairs,families=families)
kt=load('g_kernel',PKG/'kernel_transform.py')
out,initial,final,entries,execution,cats,proof,n2,v2=kt.transform(producer,sel)
hist=collections.Counter()
for k in range(0,len(out),6):
    if out[k]==0 and out[k+4]:hist[out[k+4]]+=1
    elif out[k]==2:hist[out[k+5]]+=1
delta=collections.Counter(hist);delta.subtract({int(r):c for r,c in producer['physical']['paid_histogram'].items()})
sel['expected_local_delta']={str(r):c for r,c in sorted(delta.items())if c}
sel['entrance_rank_histogram']={str(r):c for r,c in sorted(proof['entrance_rank_histogram'].items())};sel['total_entrance_rank']=proof['total_entrance_rank']
assert sel['total_entrance_rank']%5==0,'total entrance rank must be a multiple of 5 for the m = 100 bank tiling'
Path(sys.argv[3]).write_text(json.dumps(sel,indent=1)+'\n')
print('wrote',len(pairs),'pairs',len(families),'families; rank',proof['total_entrance_rank'],'ranks',sel['entrance_rank_histogram'],'delta',sel['expected_local_delta'])
