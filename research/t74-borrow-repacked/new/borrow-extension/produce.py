"""Exact additional whole-helper borrowing nominations; inherited builder read-only.

New choices are nominated here, then checked by the source's independent auditor.
No host, native or kappa admission is inferred from the nomination.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
import argparse,copy,gzip,hashlib,importlib.util,json,sys,time,subprocess,os
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'borrow'
sys.path.insert(0,str(SOURCE))
import emit_word as E
def need(ok,label):
    if not ok:raise ValueError(label)

def linear(cols,x):
    out=0
    for i,c in enumerate(cols):
        if x>>i&1:out^=c
    return out

def rank(xs):
    b={}
    for x in xs:
        while x:
            i=x.bit_length()
            if i not in b:b[i]=x;break
            x^=b[i]
    return len(b)

def extend(xs,h):
    out=list(xs)
    need(rank(out)==len(out),'independent frame basis')
    for i in range(h):
        if rank(out+[1<<i])>len(out):out.append(1<<i)
    need(len(out)==h,'complete frame basis')
    return out

def change(source,target,h):
    # Same deterministic basis completion as retained PR2226 operators.change;
    # copied mathematics here avoids importing NumPy for binary nomination.
    need(len(source)==len(target),'equal handoff dimensions')
    a,b=extend(source,h),extend(target,h)
    perm=[linear(a,x) for x in range(1<<h)]
    need(len(set(perm))==len(perm),'invertible source frame')
    back=[0]*len(perm)
    for i,j in enumerate(perm):back[j]=i
    G=[linear(b,back[1<<i]) for i in range(h)]
    need(rank(G)==h,'invertible nominated basis map')
    need(E.span([linear(G,x) for x in source])==E.span(target),'nominated source-to-target frame map')
    return G

def rd(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())

def recount(w):
    v=w['report']['v'];n=2*v+w['report']['R'];full=tuple(1<<i for i in range(w['report']['h']-1,-1,-1))
    start=[(p,) for p in w['ports']]+[()]*(n-v)
    for r,f in w['start_extra'].items():start[int(r)]=tuple(f)
    cur=list(map(E.span,start));paid=Counter()
    def climb(r,f):
        f=E.span(f);need(cur[r]<=f,('nonnested actual profile',r))
        d=(len(f).bit_length()-1)-(len(cur[r]).bit_length()-1)
        if d:paid[d]+=1
        cur[r]=f
    for e in w['A']:
        for r in E.incident(e):climb(r,e[-1])
    lev={int(t):E.span(f) for t,f in w['target_levels'].items()}
    for r,f in zip(w['centers'],w['center_frames']):
        f=E.span(f);targets={lev.get(e[1]-v,frozenset({0})) for e in w['cut'] if e[2]==r}
        for t in sorted(targets,key=lambda x:-len(x)):
            need(t<=f,'center nesting')
            d=(len(f).bit_length()-1)-(len(t).bit_length()-1)
            if d:paid[d]+=1
            f=t
    warps=defaultdict(list)
    for p,r,G,U,F in w['warps']:warps[p].append((r,U,F))
    for p in range(len(w['B'])+1):
        for r,U,F in warps[p]:
            need(cur[r]==E.span(U),'new actual handoff frame')
            cur[r]=E.span(F)
        if p<len(w['B']):
            e=w['B'][p]
            for r in E.incident(e):climb(r,e[-1])
    for e in w['restore']:
        for r in E.incident(e):climb(r,e[-1])
    live=set(range(n))-set(w['removed'])
    ends={r:full for r in live}
    for r in range(v,2*v):ends[r]=[x for x in range(1,512) if (x&w['ports'][r-v]).bit_count()%2==0]
    for r,f in w['helper_final'].items():ends[int(r)]=f
    for r in live:climb(r,ends[r])
    inventory=Counter(len(E.span(ends[r])).bit_length()-len(E.span(start[r])).bit_length() for r in live if r>=2*v)
    return dict(sorted(paid.items())),dict(sorted(inventory.items()))

def assemble(S,case):
    w=E.assemble(S,case);n=S['n'];v=S['v'];restored=set(S['restored']);full=E.frame_basis(S['full'])
    byp=defaultdict(list)
    for x in S['warps']:byp[x[0]].append(x)
    fw=list(w['A'])
    for p in range(len(w['B'])+1):
        for x in sorted(byp[p],key=lambda x:x[5]):fw.append(['warp',x[1],x[5]])
        if p<len(w['B']):fw.append(w['B'][p])
    fw+=w['restore'];buf=lambda r:r+n if r in restored else r
    cleanup=[]
    for g in reversed([g for g in fw if g[0]=='warp' or not(v<=g[1]<2*v)]):
        if g[0]=='warp':cleanup.append(['warp',buf(g[1]),-g[2],full])
        elif g[0]=='add':cleanup.append(['add',buf(g[1]),buf(g[2]),-g[3],g[4],full])
        else:cleanup.append(['scale',buf(g[1]),g[3],g[2],full])
    w['cleanup']=cleanup;w.pop('warp_order')
    prof,inv=recount(w);w['report']['local_profile']=prof;w['report']['width_inventory']=inv
    return w

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=['base','extra'],default='base')
    p.add_argument('--out',type=Path,required=True);p.add_argument('--expected',type=Path);p.add_argument('--controls',action='store_true')
    
    args=p.parse_args();case=args.case;canon='gauge44' if case=='base' else 'extra'
    source_paths=[Path(__file__).resolve(),HERE/'extension_controls.py']+[SOURCE/q for q in ['emit_word.py','audit_local.py','borrow_controls.py']]+sorted((SOURCE/'inputs').glob('*'))
    if args.expected:source_paths.append(args.expected.resolve())
    # Paths in receipts remain repository-relative, even after relocation.
    input_hashes={q.relative_to(SOURCE.parent.parent).as_posix():hashlib.sha256(q.read_bytes()).hexdigest() for q in source_paths}
    w=rd(SOURCE/'inputs'/f'{canon}.canonical.json.gz');wit=rd(SOURCE/'inputs'/f'witness_43_{case}.json');blocks=rd(SOURCE/'inputs/blocks.json')['sources'][0]['blocks']
    target,donor=619,299;dest=args.out.resolve();need(not dest.is_relative_to(SOURCE.parent.parent.resolve()),'output must be external to source package')
    need(not dest.exists(),'preserve previous candidate');dest.mkdir(parents=True)
    pairs=[(619,530)]
    for target,donor in pairs:
        need(target not in {x['register'] for x in wit['pairs']},'target not already borrowed')
        need(donor not in {x['borrow_from'] for x in wit['pairs']},'fresh donor')
        block=next((b for b in blocks if target in b['helpers']),None)
        if block is None:
            hs=set(range(target//8*8,target//8*8+8))
            internal=[j for j,g in enumerate(w['B']) if set(E.incident(g))<=hs]
            external=[j for j,g in enumerate(w['B']) if j>min(internal) and set(E.incident(g))&hs and not set(E.incident(g))<=hs]
            block={'helpers':sorted(hs),'first_correction':min(internal),'first_input':min(external)}
            blocks.append(block)
        deadline=block['first_input']
        cur={r:w['start'][r] for r in range(2*w['v']+w['R'])};last={}
        for e in w['A']:
            for r in E.incident(e):cur[r]=e[-1]
        for j,e in enumerate(w['B'][:deadline]):
            for r in E.incident(e):cur[r]=e[-1];last[r]=j
        need(not any(donor in E.incident(e) for e in w['B'][deadline:]),'donor actually retired')
        deferred=[]
        for j in range(block['first_correction'],block['first_input']):
            e=w['B'][j]
            if set(E.incident(e))<=set(block['helpers']):deferred.append(e)
        sequence=deferred+w['B'][deadline:]
        first=next(e for e in sequence if target in E.incident(e))
        U=w['frames'][cur[donor]];F=w['frames'][first[-1]];dim=len(U);T=E.frame_basis(E.span(F))[:dim]
        need(len(T)==dim,'rank-zero handoff width')
        G=change(U,T,w['h'])
        new={'register':target,'base':block['helpers'][0]//8*8,'dimension':len(w['frames'][w['start'][target]]),'deadline':deadline,'low':False,'borrow_from':donor,'retirement_B_event':last.get(donor,-1),'retirement_basis':U,'retirement_dimension':dim,'old_final_dimension':len(w['frames'][w['final'][donor]]),'handoff_B':deadline,'handoff_basis':T,'handoff_paid_rank':0,'anticipate':False}
        wit['pairs'].append(new);wit['gaussian']['records'].append({'operator':len(wit['pairs']),'G_columns':G})
    begin=time.monotonic();S=E.build(w,blocks,wit)
    corrections=[]
    for r in range(w['v'],2*w['v']):
        expected={(r,()):Q(1),(r-w['v'],()):Q(1)};actual=dict(S['val'][r]);E.add(actual,expected,Q(-1))
        for (var,word),coeff in actual.items():
            need(w['start'][var]==0,('nonzero-frame initial correction needed',var))
            corrections.append({'target':r,'source':var,'operator_word':list(word),'coefficient':str(-coeff)})
    if corrections:
        wit['initial_corrections']+=corrections;S=E.build(w,blocks,wit)
    for r in range(w['v'],2*w['v']):need(S['val'][r]=={(r,()):Q(1),(r-w['v'],()):Q(1)},'exact target map before cleanup')
    S=E.finish(S);word=assemble(S,case)
    raw=json.dumps(word,separators=(',',':')).encode();path=dest/'BORROW-WORD.json.gz';path.write_bytes(gzip.compress(raw,mtime=0));(dest/'WITNESS.json').write_text(json.dumps(wit,indent=2)+'\n',encoding='utf8')
    child_env=os.environ.copy();child_env.pop('PYTHONOPTIMIZE',None)
    cmd=[sys.executable,'-B',str(SOURCE/'audit_local.py'),'--word',str(path),'--base',str(SOURCE/'inputs'/f'{canon}.canonical.json.gz'),'--output',str(dest/'AUDIT.json')]
    audit=subprocess.run(cmd,env=child_env,capture_output=True,text=True,encoding='utf8',timeout=120);(dest/'audit.log').write_text(audit.stdout+audit.stderr,encoding='utf8')
    need(audit.returncode==0,'independent local audit failed: '+audit.stdout[-2500:]+audit.stderr[-2500:])
    if args.expected:
        expected=rd(args.expected)
        need(json.loads(raw)==expected,'regenerated word differs from frozen expected payload')
    if args.controls:
        control=subprocess.run([sys.executable,'-B',str(SOURCE/'borrow_controls.py'),str(path),str(SOURCE/'inputs'/f'{canon}.canonical.json.gz'),str(dest/'CONTROLS.json')],env=child_env,capture_output=True,text=True,encoding='utf8',timeout=180)
        (dest/'controls.log').write_text(control.stdout+control.stderr,encoding='utf8')
        need(control.returncode==0,'independent negative controls failed')
        control=subprocess.run([sys.executable,'-B',str(HERE/'extension_controls.py'),'--word',str(path),'--base',str(SOURCE/'inputs'/f'{canon}.canonical.json.gz'),'--out',str(dest/'EXTENSION-CONTROLS.json')],env=child_env,capture_output=True,text=True,encoding='utf8',timeout=90)
        (dest/'extension-controls.log').write_text(control.stdout+control.stderr,encoding='utf8')
        need(control.returncode==0,'new44th alias negative controls failed')
    need(input_hashes=={q.relative_to(SOURCE.parent.parent).as_posix():hashlib.sha256(q.read_bytes()).hexdigest() for q in source_paths},'published source inputs were modified')
    result={'source_inputs_unchanged':True,'source_sha256':input_hashes,'status':'PASS_EXACT_NEW_LOCAL_ALIAS_BOTH_ORIENTATIONS','additional_pairs':pairs,'case':case,'profile':word['report']['local_profile'],'inventory':word['report']['width_inventory'],'mass':sum(int(r)*n for r,n in word['report']['local_profile'].items()),'owned_FULL_buffers':len(S['restored']),'warps':len(word['warps']),'added_initial_corrections':len(corrections),'compressed_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(raw).hexdigest(),'seconds':time.monotonic()-begin,'expected_matched':bool(args.expected),'negative_controls_replayed':bool(args.controls),'scope':'Actual scalar/operator/frame trace only; native phase/lowering, hosting and complete paid profile/invoice are checked separately.'}
    (dest/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
