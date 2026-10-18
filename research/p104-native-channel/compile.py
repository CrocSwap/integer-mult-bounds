"""Concrete exact Clifford transport for the complete P104 low-rank channel.

Converts compressed root labels to a physical orthonormal binary label basis.
This includes query gathering, but not the side correction or a P104 supplier.
"""
from pathlib import Path
from functools import lru_cache
import argparse,gzip,hashlib,importlib.util,json,sys,time
from itertools import combinations,product
H=Path(__file__).resolve().parent
P=H/'inputs'
CP=H/'vendor/clifford_exact.py'
sp=importlib.util.spec_from_file_location('p104_native_compiler',CP);CE=importlib.util.module_from_spec(sp);sys.modules[sp.name]=CE;sp.loader.exec_module(CE)
NP=H/'vendor/native_verify.py'
sp=importlib.util.spec_from_file_location('p104_independent_native',NP);N=importlib.util.module_from_spec(sp);sp.loader.exec_module(N)

def root_lines():
    out=[]
    for i,j in combinations(range(8),2):
        for s in (-1,1):
            r=[0]*8;r[i]=2;r[j]=2*s;out.append(tuple(r))
    for s in product((-1,1),repeat=7):
        if s.count(-1)%2==0:out.append((1,*s))
    return sorted(out)

def inner(a,b):return sum(x*y for x,y in zip(a,b))//4

def need(ok,why):
    if not ok:raise ValueError(why)

def canon(values):
    piv={}
    for x in values:
        while x:
            j=x.bit_length()-1
            if j in piv:x^=piv[j]
            else:piv[j]=x;break
    for j in sorted(piv):
        for k in piv:
            if k>j and piv[k]>>j&1:piv[k]^=piv[j]
    return tuple(piv[j]for j in sorted(piv,reverse=True))

def label_isometry():
    roots=root_lines();matrix=[sum(((inner(a,b)+1)&1)<<j for j,b in enumerate(roots))for a in roots]
    indices=[];rows=[]
    for i,row in enumerate(matrix):
        if CE.rank(rows+[row])>len(rows):indices.append(i);rows.append(row)
    need(len(indices)==9,'symmetric pairing rank nine')
    labels=[sum(((row>>j)&1)<<k for k,j in enumerate(indices))for row in matrix]
    gram=[labels[i]for i in indices];dual=CE.inv(gram,9)
    dot=lambda a,b:CE.parity(a&CE.mv(dual,b))
    def extend(vs):
        if len(vs)==9:return vs
        candidates=[v for v in range(1,512)if dot(v,v)and all(not dot(v,u)for u in vs)]
        for v in candidates:
            if len(vs)<8 and not any(not dot(v,u)for u in candidates):continue
            out=extend(vs+[v])
            if out is not None:return out
        return None
    orthogonal=extend([]);need(orthogonal is not None,'orthonormal label basis exists')
    transform=lambda x:sum(dot(x,v)<<k for k,v in enumerate(orthogonal))
    physical=[transform(x)for x in labels]
    need(len(set(physical))==120,'injective physical root labels')
    for i in range(120):
        for j in range(120):need(CE.parity(physical[i]&physical[j])==((matrix[i]>>j)&1),'all physical binary pairings')
    return roots,labels,physical,transform,dict(pivot_root_indices=indices,compressed_gram=gram,compressed_dual_gram=dual,orthonormal_basis_compressed=orthogonal,physical_root_labels=physical)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);args=ap.parse_args();destination=args.out_dir;destination.mkdir(parents=True,exist_ok=True)
    need(not any((destination/f).exists()for f in ['NATIVE-RECIPES.json.gz','SUMMARY.json']),'output files already exist')
    started=time.monotonic();need(hashlib.sha256(CP.read_bytes()).hexdigest()=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','pinned native compiler')
    roots,labels,physical,transform,iso=label_isometry();word=json.loads((P/'LOWRANK-WITNESS.json').read_text());fixture=json.loads((P/'P104-FIXTURE.json').read_text())['section4_explicit_P104'];removed={tuple(r)for r in fixture['F0']+fixture['C']};geom={'ports':[r for r in roots if r not in removed]};byroot=dict(zip(roots,physical))
    frame=lambda f:canon(transform(x)for x in f)
    all_frames={frame(f)for f in word['initial_frames'].values()}|{frame(f)for f in word['final_frames'].values()}
    edges={}
    for index,e in enumerate(word['program']):
        if e[0]=='transport':
            old,new=frame(e[2]),frame(e[3]);edges.setdefault((old,new),dict(rank=e[4],events=[]))['events'].append(index);all_frames.update((old,new))
    @lru_cache(None)
    def chart(f):return CE.canonical_frame(9,f)
    recs=[];copy_keys=set();full=tuple(1<<i for i in range(8,-1,-1))
    for e in word['program']:
        if e[0]=='transport'and e[1]=='C':copy_keys.add((frame(e[2]),frame(e[3])))
    for number,((old,new),meta)in enumerate(sorted(edges.items())):
        actual=chart(old).adjoint().then(chart(new));record,compiled=CE.lower_child(actual)
        need(record['rank']==meta['rank'],'native positive rank equals paid frame jump')
        expected=N.adjoint(N.frame(old,9))+N.frame(new,9);N.equal(N.recipe(record),expected,'P104 boundary transport')
        recs.append(dict(old=list(old),new=list(new),rank=meta['rank'],events=meta['events'],recipe=record))
        if number%20==0:print('COMPILED',number+1,len(edges),flush=True)
    adapters=[]
    for reg,f in word['initial_frames'].items():
        if not reg.startswith('X'):continue
        k=int(reg[1:]);normal=byroot[tuple(geom['ports'][k])];ff=frame(f)
        need(ff==(normal,),'source physical singleton')
        intrinsic=CE.cgate(9,normal,1);op=intrinsic.adjoint().then(chart(ff));recipe,_=CE.lower_child(op)
        need(recipe['rank']==0,'source endpoint adapter is monomial');N.equal(N.recipe(recipe),N.adjoint((('C',normal,1),))+N.frame(ff,9),'P104 source endpoint')
        adapters.append(dict(register=reg,position='entry',normal=normal,frame=list(ff),recipe=recipe))
    for reg,f in word['final_frames'].items():
        if not reg.startswith('Y'):continue
        target=int(reg[1:]);normal=byroot[tuple(geom['ports'][target])];ff=frame(f)
        need(all(not CE.parity(v&normal)for v in ff)and len(ff)==8,'target physical hyperplane')
        intrinsic=CE.cgate(9,normal,-1).then(CE.fourier(9));op=chart(ff).adjoint().then(intrinsic);recipe,_=CE.lower_child(op)
        need(recipe['rank']==0,'target endpoint adapter is monomial');N.equal(N.recipe(recipe),N.adjoint(N.frame(ff,9))+(('C',normal,-1),)+N.fourier(9),'P104 target endpoint')
        adapters.append(dict(register=reg,position='exit',normal=normal,frame=list(ff),recipe=recipe))
    copy_columns=0
    for rec in recs:
        old,new=tuple(rec['old']),tuple(rec['new'])
        if (old,new)not in copy_keys:continue
        need(rec['rank']==7,'all private drops rank seven');actual=N.recipe(rec['recipe']);expected=N.adjoint(N.frame(old,9))+N.frame(new,9)
        for j in range(512):need(N.state(actual,j)==N.state(expected,j),'all Gaussian private-drop columns');copy_columns+=1
        print('COPY_COLUMNS',copy_columns,flush=True)
    profile={}
    for rec in recs:profile[rec['rank']]=profile.get(rec['rank'],0)+len(rec['events'])
    expected=json.loads((P/'LOWRANK-RESULT.json').read_text())['paid_profile'];need({str(k):v for k,v in profile.items()}==expected,'native channel paid profile')
    out=dict(status='COMPILED_EXACT_P104_LOW_RANK_CHANNEL',source_pr=1972,source_head='fd82d172f46933fd253c2c6de4bd5eaff5429cfd',upstream_schedule_pr=1940,upstream_schedule_head='a9b7dfe2809092a9a4c90784d12bb60061e995e8',source_witness_sha256=hashlib.sha256((P/'LOWRANK-WITNESS.json').read_bytes()).hexdigest(),source_compiler_sha256=hashlib.sha256(CP.read_bytes()).hexdigest(),source_native_checker_sha256=hashlib.sha256(NP.read_bytes()).hexdigest(),label_isometry=iso,transports=recs,endpoint_adapters=adapters,paid_profile=profile,rank_mass=sum(k*v for k,v in profile.items()),private_drop_basis_columns=copy_columns,scope='Concrete finite Clifford transport and endpoint adapters for the complete low-rank G/2 channel, including gathering and all 72 dirty helper restorations. Not I-G/2 side correction, chronological global hosting, all-size compilation, precision or a new supplier/kappa.')
    raw=(json.dumps(out,sort_keys=True,indent=2)+'\n').encode();(destination/'NATIVE-RECIPES.json.gz').write_bytes(gzip.compress(raw,mtime=0));(destination/'SUMMARY.json').write_text(json.dumps({k:v for k,v in out.items()if k not in('transports','endpoint_adapters','label_isometry')},indent=2)+'\n');print('DONE',len(recs),len(adapters),copy_columns,'seconds',time.monotonic()-started,flush=True)

if __name__=='__main__':main()
