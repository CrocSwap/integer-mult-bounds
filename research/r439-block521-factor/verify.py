#!/usr/bin/env python3
"""Independent exact finite verification of the shorter R439 frame-521 circuit.

The verifier does not import search.py. Prepared with substantial OpenAI assistance; Apache-2.0.
"""
import argparse,copy,gzip,hashlib,importlib.util,itertools,json,struct,subprocess,sys,tempfile
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
WORD='research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
CHECKER='research/e8-bit-p111-tuned/code/xcheck_p.py'
EXPORTER='research/e8-bit-carrier-skeleton/code/bit/export_records.py'
class Reject(Exception): pass
def need(ok,msg):
    if not ok: raise Reject(msg)
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def digest(v): return hashlib.sha256(canonical(v)).hexdigest()
def matrix(ops,n):
    cols=[]
    for c in range(n):
        x=[int(i==c) for i in range(n)]
        for a,b in ops:
            need(type(a) is int and type(b) is int and 0<=a<n and 0<=b<n and a!=b,'invalid operation'); x[a]+=x[b]
        cols.append(x)
    return [list(r) for r in zip(*cols)]
def dominated(a,b): return all(x<=y for p,q in zip(a,b) for x,y in zip(p,q))
def pins():
    s=json.loads((HERE/'SOURCES.json').read_text()); need(s['base_commit']=='f567884aeb8851b6e794af1184119a3bfbe1e631','base pin')
    for p,h in s['files'].items(): need(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,'source pin: '+p)
def bind(word,c):
    b=c['binding']; need((b['source'],b['section'],b['slice'],b['frame'])==(WORD,'B',[314,361],521),'binding')
    oldg=word['B'][314:361]; regs=b['registers']; need(regs==[10,13,32,34,39,42,76,79,83,85,104,107],'register binding')
    need(len(oldg)==47 and all(f==521 and len(ss)==1 for f,_,ss in oldg),'source block')
    idx={r:i for i,r in enumerate(regs)}; need(sorted({d for _,d,_ in oldg}|{s for _,_,ss in oldg for s in ss})==regs,'source wires')
    old=[(idx[d],idx[ss[0]]) for _,d,ss in oldg]; newg=c['gates']
    need(len(newg)==31 and all(f==521 and d in idx and len(ss)==1 and ss[0] in idx and d!=ss[0] for f,d,ss in newg),'candidate shape')
    new=[(idx[d],idx[ss[0]]) for _,d,ss in newg]; mo,mn=matrix(old,12),matrix(new,12)
    need(mo==mn,'integer map'); ro,rn=matrix(old[::-1],12),matrix(new[::-1],12); need(dominated(rn,ro),'reverse domination')
    strict=sum(x<y for p,q in zip(rn,ro) for x,y in zip(p,q)); need(strict>0,'strict reverse gain')
    for val in range(1<<12):
        a=[(val>>i)&1 for i in range(12)]; b=list(a)
        for ops,state in ((old,a),(new,b)):
            for d,s in ops: state[d]^=state[s]
        need(a==b,'F2 table')
    return old,new,{'boolean_inputs_checked':4096,'forward_integer_sha256':digest(mo),'reverse_old_total':sum(map(sum,ro)),'reverse_new_total':sum(map(sum,rn)),'reverse_strict_entries':strict}
def cleanup(w):
    full=next(i for i,f in enumerate(w['frames']) if len(f)==w['v'])
    return [[full,d,list(ss)] for _,d,ss in reversed(w['A']+w['B']) if d<w['v'] or d>=2*w['v']]
def candidate(word,c):
    w=copy.deepcopy(word); w['B'][314:361]=copy.deepcopy(c['gates']); w['C']=cleanup(w); return w
def paths(w):
    fs=list(map(set,w['frames'])); ps=[[f] for f in w['start']]
    def move(r,f):
        if ps[r][-1]!=f: need(fs[ps[r][-1]]<fs[f],'illegal frame move'); ps[r].append(f)
    for k in 'DABC':
        for f,d,ss in w[k]:
            for r in [d,*ss]: move(r,f)
    for r,f in enumerate(w['final']): move(r,f)
    return ps
def endpoint(w):
    n=2*w['v']+w['R']; v=w['v']; state=[{i} for i in range(n)]
    def run(k):
        for _,d,ss in w[k]:
            for s in ss: state[d].symmetric_difference_update(state[s])
    run('D');run('A'); snap=[state[r].copy() for r in w['ret']]
    for t,reads in enumerate(w['scatter']):
        for k in reads: state[v+t].symmetric_difference_update(snap[k])
    run('B');run('C')
    for r,x in enumerate(state): need(x==({r,r-v} if v<=r<2*v else {r}),'endpoint register '+str(r))
    return n
def checker():
    s=importlib.util.spec_from_file_location('r439_owner_checker',ROOT/CHECKER); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def bill(w,out):
    out.mkdir(parents=True); wp=out/'word.json.gz'; wp.write_bytes(gzip.compress(canonical(w),mtime=0))
    subprocess.run([sys.executable,'-I','-B',str(ROOT/EXPORTER),str(wp),str(out/'records')],check=True,capture_output=True,text=True)
    raw=(out/'records/249-records.bin').read_bytes(); need(len(raw)%24==0,'record alignment'); rec=list(struct.iter_unpack('<6i',raw)); n=2*w['v']+w['R']; bounds=[]
    for rev in (False,True):
        norms=[1]*(n+1); maximum=1; opened=False
        for op,a,b,c,_,_ in (reversed(rec) if rev else rec):
            if op==0: continue
            if rev and op in (2,3): op=5-op
            if op==1: norms[a]+=abs(c)*norms[b]; maximum=max(maximum,norms[a])
            elif op==2: need(not opened,'nested copy'); norms[b]=norms[a]; opened=True
            elif op==3: need(opened,'erase without copy'); norms[b]=0; opened=False
            else: raise Reject('record opcode')
        need(not opened,'unclosed copy'); bounds.append(maximum)
    payload=64*bounds[0]**3*bounds[1]**2; need(payload<1<<104,'payload cap')
    return {'records':len(rec),'adds':sum(x[0]==1 for x in rec),'copies':sum(x[0]==2 for x in rec),'erasures':sum(x[0]==3 for x in rec),'forward_positive_bound':bounds[0],'reverse_positive_bound':bounds[1],'payload_bits':payload.bit_length(),'record_sha256':hashlib.sha256(raw).hexdigest()},rec
def reject(name,fn):
    try: fn()
    except Reject: return name
    raise Reject('negative control accepted: '+name)
def verify(out):
    pins(); c=json.loads((HERE/'CANDIDATE.json').read_text()); word=json.loads(gzip.decompress((ROOT/WORD).read_bytes())); old,new,block=bind(word,c); w=candidate(word,c)
    need(all(w[k]==word[k] for k in word if k not in ('B','C')),'unrelated field'); need(w['C']==cleanup(w),'literal cleanup')
    p0,p1=paths(word),paths(w); need(p0==p1,'frame paths'); endpoint(word); columns=endpoint(w)
    dim,labels,flow,hyp,con,_=checker().check(w); need(all(hyp.values()) and all(con.values()),'H1-H5 interface')
    profile=Counter(dim.fdim[b]-dim.fdim[a] for p in p1 for a,b in itertools.pairwise(p)); profile.update(t['rank'] for t in flow['totals'])
    expected={1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}; need(dict(sorted(profile.items()))==expected,'profile'); need(sum(k*v for k,v in profile.items())==5129,'rank mass')
    before,r0=bill(word,out/'before'); after,r1=bill(w,out/'after'); need((before['adds'],after['adds'])==(24305,24273),'ADD bill')
    need(before['copies']==after['copies']==9 and before['erasures']==after['erasures']==9,'copy bill'); need(Counter(x for x in r0 if x[0]!=1)==Counter(x for x in r1 if x[0]!=1),'non-ADD events')
    need(after['forward_positive_bound']==41191 < before['forward_positive_bound']==49347,'forward bound'); need(after['reverse_positive_bound']==1005338 < before['reverse_positive_bound']==1113070,'reverse bound'); need(after['payload_bits']==92 < before['payload_bits']==93,'payload bits')
    controls=[]; bad=copy.deepcopy(c); bad['gates'][0][2]=[10] if bad['gates'][0][2]!=[10] else [13]; controls.append(reject('mutated_source',lambda:bind(word,bad)))
    bad=copy.deepcopy(c); bad['gates'].pop(); controls.append(reject('unpaid_gate',lambda:bind(word,bad)))
    controls.append(reject('inverted_domination',lambda:need(dominated(matrix(old[::-1],12),matrix(new[::-1],12)),'inverted domination')))
    bad=copy.deepcopy(w); bad['C'].pop(); controls.append(reject('omitted_cleanup',lambda:endpoint(bad)))
    bad=copy.deepcopy(w); del bad['B'][314]; bad['C']=cleanup(bad); controls.append(reject('missing_gate_matching_cleanup',lambda:endpoint(bad)))
    bad=copy.deepcopy(w); bad['B'][314][0]=0; controls.append(reject('illegal_frame',lambda:paths(bad)))
    stale=copy.deepcopy(w); stale['C']=word['C']; endpoint(stale); controls.append(reject('stale_cleanup_H4',lambda:need(stale['C']==cleanup(stale),'H4')))
    return {'status':'PASS_R439_BLOCK521_FACTOR','base_commit':c['base_commit'],'assignment_seed':10,'block':block,'columns':columns,'closed_frames':labels['frames'],'copy_ranks':[t['rank'] for t in flow['totals']],'paid_profile':{str(k):v for k,v in sorted(profile.items())},'rank_mass':5129,'identical_register_frame_paths':len(p1),'hypotheses':hyp,'conclusion':con,'before':before,'after':after,'adds_saved':32,'new_kappa_claim':False,'candidate_content_sha256':hashlib.sha256(canonical(w)).hexdigest(),'negative_controls':controls,'search':c['search']}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);ap.add_argument('--record-certificate',action='store_true');a=ap.parse_args()
    if a.out:
        need(not a.out.exists(),'output exists'); out=a.out
    else:
        tmp=tempfile.TemporaryDirectory(prefix='r439-b521-');out=Path(tmp.name)
    report=verify(out)
    cert=HERE/'CERTIFICATE.json'
    if a.record_certificate: need(not cert.exists(),'certificate exists'); cert.write_text(json.dumps(report,indent=2)+'\n')
    else: need(report==json.loads(cert.read_text()),'certificate mismatch')
    print('PASS_R439_BLOCK521_FACTOR gates=47->31 ADDs=24305->24273 columns=661 controls=7 rank_mass=5129 kappa=unchanged')
if __name__=='__main__': main()
