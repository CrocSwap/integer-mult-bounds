#!/usr/bin/env python3
"""Exact candidate replay. Apache-2.0; substantial OpenAI Codex assistance."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,gzip,importlib.util,json,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,message):
    if not ok:raise ValueError(message)
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def authenticate():
    for row in read(HERE/'SOURCES.json')['files']:
        if row['usage']=='input':need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'Changed authenticated input '+row['path'])
def span(B):
    s={0}
    for x in B:s|={y^x for y in tuple(s)}
    return s
def gates(word):
    out={};phase=None;ordinal=Counter()
    for e in word:
        if e[0]=='phase':phase=e[1]
        elif e[0]=='scalar':
            g=e[1];refs=g[1:3] if g[0] in ('add','copy') else g[1:2]
            if all(r[0]=='L' for r in refs):out[phase,ordinal[phase]]=e;ordinal[phase]+=1
    return out
def synth(c,raw):
    cur=c['start'][:];out=[];spaces=list(map(span,c['frames']))
    def move(r,f):
        old=cur[r]
        if old==f:return
        need(spaces[old]<spaces[f],'Non-nested physical transport')
        out.append(['climb','hyperplane-retimed',r,old,f,len(c['frames'][f])-len(c['frames'][old])]);cur[r]=f
    for e in raw:
        if e[0]=='climb':continue
        if e[0]=='scalar':
            g=e[1];refs=g[1:3] if g[0] in ('add','copy') else g[1:2]
            for typ,r in refs:
                if typ=='L':move(r,e[2])
        elif e[0]=='warp':move(e[1][1],e[3]);cur[e[1][1]]=e[4]
        out.append(deepcopy(e))
    for r,f in enumerate(c['final']):move(r,f)
    return out
def regenerate(source,patch):
    c=deepcopy(source['canonical']);words=deepcopy(source['programs']);seen=set()
    for r,a,b in patch['helper_entrances']:
        need(224<=r<632 and r not in seen and c['start'][r]==a,'Unique arbitrary helper entrance pin');seen.add(r);c['start'][r]=b
    for p in words.values():
        gs=gates(p);seen=set()
        for phase,i,a,b in patch['contacts']:
            key=(phase,i);need(key not in seen and gs[key][2]==a,'Unique chronological scalar-contact pin');seen.add(key);gs[key][2]=b
    c['local_profile']=patch['paid'];c['R']=408
    words={d:synth(c,p) for d,p in words.items()}
    need(c['start'][:224]==source['canonical']['start'][:224] and c['final']==source['canonical']['final'],'Actual main ABI and all final references fixed')
    for d,p in words.items():
        old=source['programs'][d]
        need([e[1] for e in p if e[0]=='scalar']==[e[1] for e in old if e[0]=='scalar'],'Every scalar opcode, order and coefficient')
        need([e for e in p if e[0] in ('warp','center','adapter','residual_adapter')]==[e for e in old if e[0] in ('warp','center','adapter','residual_adapter')],'All native maps, centers, main adapters and owned events retained')
    H=Counter()
    for r in range(224,632):
        a,b=c['start'][r],c['final'][r];need(span(c['frames'][a])<span(c['frames'][b]),'Strict productive arbitrary helper');H[len(c['frames'][b])-len(c['frames'][a])]+=1
    need(H=={int(k):v for k,v in patch['helpers'].items()} and sum(H.values())==408,'All independent helper jobs, once each')
    return c,words,H

def invoice(H,P):
    T=Counter({r:18*n for r,n in H.items()});paid=Counter({r:18*n for r,n in P.items()});paid[1]+=15*112
    T[145]+=224
    for length in (7,8):
        for j in range(1,length+1):T[1+8*(j+1)]+=224;paid[8*(j+1)]+=224
    return T,paid

def run():
    authenticate();source=read(HERE/'inputs/pr4610-word.json.gz');patch=read(HERE/'PATCH.json');c,words,H=regenerate(source,patch)
    VROOT=HERE/'vendor';F=load(VROOT/'research/fresh-helper-boundary/native.py','hyper_F')
    V=F.load(VROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','hyper_V');X=F.load(VROOT/'research/kappa-rebuild/complex/native_extensions.py','hyper_X')
    P={int(k):v for k,v in patch['paid'].items()};checks={}
    for d,p in words.items():
        rows,rec=X.literal_replay(V,c,p,d=='backward');need(all(rows['L',r]==V.expected(('L',r),[],d=='backward',False) for r in range(632)),'All 632 arbitrary input columns')
        V.replay(p,c,[],d=='backward',False);need({int(k):v for k,v in rec['paid_profile'].items()}==P,'Complete paid invoice')
        need(rec['real_scalar_allowance']==(158168 if d=='backward' else 158120),'Full scalar allowance retained')
        checks[d]={'arbitrary_persistent_columns':632,'real_scalar_allowance':rec['real_scalar_allowance'],'max_formal_prefix_l1':str(rec['max_formal_prefix_l1'])}
        print('PASS_NATIVE',d,flush=True)
    ce=F.load(VROOT/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py','hyper_ce');pr=F.load(VROOT/'research/kappa-function-composition/complex/prune_native.py','hyper_pr')
    fc={}
    def frame(i):
        if i not in fc:fc[i]=ce.canonical_frame(9,c['frames'][i])
        return fc[i]
    def lower(a,b,r):
        op=frame(a).adjoint().then(frame(b));out={}
        for d in ('forward','backward'):
            actual=pr.conjugate(ce,op) if d=='backward' else op;rec=X.N.lower_exact(pr,ce,actual);need(rec['rank']==r,'Exact phase-aware rank');out[d]=rec
        return out
    edges=lambda p:{tuple(e[3:6]) for e in p if e[0]=='climb'}
    new=sorted(edges(words['forward'])-edges(source['programs']['forward']));phase_paid=[{'input':a,'output':b,'rank':r,'recipes':lower(a,b,r)} for a,b,r in new]
    phase_helpers=[]
    for r,a,b in patch['helper_entrances']:
        end=c['final'][r];rank=len(c['frames'][end])-len(c['frames'][b]);phase_helpers.append({'role':r,'input':b,'output':end,'rank':rank,'recipes':lower(b,end,rank)})
    need(edges(words['forward'])==edges(words['backward']),'Same complete physical edge set in both orientations')
    bad=deepcopy(words['forward']);next(e for e in bad if e[0]=='climb')[5]+=1;rejected=False
    try:V.replay(bad,c,[],False,False)
    except (ValueError,AssertionError):rejected=True
    need(rejected,'False emitted paid rank rejected')
    witness=phase_paid[0];rec=deepcopy(witness['recipes']['forward']);rec['left']['phase']=(rec['left']['phase']+1)%4
    op=frame(witness['input']).adjoint().then(frame(witness['output']));decoded=pr.monomial(ce,rec['right'],9).then(ce.fourier(9,range(rec['rank']))).then(pr.monomial(ce,rec['left'],9))
    need(op.tab==decoded.tab and op.zero_state()!=decoded.zero_state(),'Absolute-phase mutation rejected independently of tableau')
    E=load(HERE/'intervals.py','hyper_intervals');T,paid=invoice(H,P)
    need(sum(r*n for r,n in T.items())-sum(r*n for r,n in paid.items())==752,'Whole rank surplus remains 752')
    def margin(C):
        a,b=E.moment(T,1-C),E.moment(paid,1-C);return a[0]-b[1],a[1]-b[0]
    lo,hi=Q('.0030216758'),Q('.0030216759');need(margin(lo)[0]>0 and margin(hi)[1]<0,'Strict p16 raw crossing enclosure')
    oldP={int(k):v for k,v in source['canonical']['local_profile'].items()};oldH=Counter(len(c['frames'][source['canonical']['final'][r]])-len(c['frames'][source['canonical']['start'][r]]) for r in range(224,632))
    local=[]
    for C in (Q('.0030216'),Q('.004')):
        nt,np=E.moment(H,1-C),E.moment(P,1-C);ot,op=E.moment(oldH,1-C),E.moment(oldP,1-C);gain=nt[0]-np[1]-ot[1]+op[0];need(gain>0,'Strict entire local moment improvement');local.append({'C':str(C),'gain_lower':str(gain)})
    return {'status':'PASS_COORDINATED_HYPERPLANE_NATIVE_PHASE_MOMENT','native':checks,'changed_helper_entrances':len(patch['helper_entrances']),'changed_contacts':len(patch['contacts']),'helpers':dict(H),'paid':P,'new_paid_phase_pairs':phase_paid,'changed_helper_phase_normalizers':phase_helpers,'whole_targets':dict(T),'whole_paid':dict(paid),'rank_surplus':752,'raw_crossing':[str(lo),str(hi)],'raw_lower_margin':str(margin(lo)[0]),'raw_upper_margin':str(margin(hi)[1]),'local_strict_gain':local,'controls':['false_paid_rank_rejected','wrong_absolute_phase_rejected'],'new_kappa':None,'scope':'Exact local supplier, all-fiber gauge proof, complete p16 raw moment. Finite/compiler, precision and outer admission remain separate.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    if sys.flags.optimize:
        # Inherited source assertions remain enabled even under an optimized caller.
        raise SystemExit(subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),*(['--write'] if a.write else [])],check=False).returncode)
    result=run();target=HERE/'RESULT.json'
    if a.write:target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(read(target)==json.loads(json.dumps(result)),'Deterministic complete receipt')
    print(result['status'],flush=True)
