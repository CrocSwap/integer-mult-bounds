#!/usr/bin/env python3
"""First gate only: independently replay exact dirty-entry words; no physical claim."""
import argparse, collections, gzip, hashlib, json
from fractions import Fraction
from pathlib import Path

N, PUBLIC, EVENTS = 1569, 1501, 77371
SOURCE_GZ = '501876971143a0588403d653852b2305893d9b385be94f0f5d7134ebd97e03f0'
SOURCE_CAN = 'df521d552dc35de6271e67655e4f9c466bc9247d37a5196b85613870209106a2'
HEAD = '5987b208bc05d066f01f800a3d88538cb216eccd'
class Refusal(Exception): pass
def need(x, msg):
    if not x: raise Refusal(msg)
def canon(x): return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
def sha(x): return hashlib.sha256(x).hexdigest()
def readword(p):
    raw=Path(p).read_bytes(); obj=json.loads(gzip.decompress(raw)); return obj,sha(raw),sha(canon(obj))
def special(e):
    op,r=e[:2]
    return op in ('INIT','CLEAR','COPY') or (op=='MOVE' and r>=PUBLIC) or (op=='SCALE' and r>=PUBLIC) or (op=='ADD' and (r>=PUBLIC or e[2]>=PUBLIC))
def span(vectors):
    s={0}
    for v in vectors:
        need(type(v) is int and 0<v<512 and v not in s,'invalid frame')
        s |= {x^v for x in tuple(s)}
    return frozenset(s)
def parse_manifest(m,p):
    """Reconstruct directly; counts and advertised candidate indices are never trusted."""
    need(m.get('source_canonical_sha256')==SOURCE_CAN and m.get('source_gzip_sha256')==SOURCE_GZ and m.get('source_head')==HEAD,'manifest source pin')
    need(isinstance(m.get('delete'),list) and isinstance(m.get('insert_before'),list),'manifest lists')
    dels={}; ins={}
    for d in m['delete']:
        need(isinstance(d,dict),'delete record')
        i=d.get('source_index',d.get('source_clock')); e=d.get('event')
        need(type(i) is int and 0<=i<len(p) and i not in dels and isinstance(e,list) and p[i]==e,'delete clock or literal')
        dels[i]=e
    for d in m['insert_before']:
        need(isinstance(d,dict),'insert record')
        i=d.get('source_index',d.get('source_clock')); es=d.get('events')
        need(type(i) is int and 0<=i<len(p) and i not in ins and isinstance(es,list) and bool(es) and all(isinstance(e,list) for e in es),'insert clock or payload')
        if 'anchor' in d: need(d['anchor']==p[i],'insert anchor')
        ins[i]=es
    out=[]; origins=[]; reverse=[None]*len(p)
    for i,e in enumerate(p):
        for x in ins.get(i,[]): out.append(x); origins.append(None)
        if i not in dels: reverse[i]=len(out);out.append(e);origins.append(i)
    need(all(reverse[i] is not None for i,e in enumerate(p) if special(e)),'deleted protected event')
    for j,e in enumerate(out):
        if special(e): need(origins[j] is not None and e==p[origins[j]],'inserted protected event')
    return out,origins,reverse

def validate_observations(program,origins,seen,reference):
    need(len(program)==len(origins),'origin coverage')
    expected=[origins[i] for i,e in enumerate(program) if special(e)]
    counts=collections.Counter()
    for e in program:
        op,r=e[:2]
        if op=='CLEAR': counts['clear']+=1
        if op in ('INIT','CLEAR') or (op=='MOVE' and r>=PUBLIC): counts['owned']+=1
        if op=='COPY': counts['copy']+=1
        if (op=='SCALE' and r>=PUBLIC) or (op in ('ADD','COPY') and (r>=PUBLIC or e[2]>=PUBLIC)): counts['interface']+=1
    need(tuple(counts[k] for k in ('clear','interface','owned','copy'))==(204,700,455,1),'positive event-derived observation inventory')
    need(all(type(i) is int for i in expected) and len(set(expected))==len(expected),'invalid expected observations')
    need(isinstance(seen,list) and seen==expected and len(set(seen))==len(seen),'missing or duplicate observations')
    need(isinstance(reference,dict) and set(reference)==set(expected),'reference observation coverage')

def final_public_nonidentity(rows,mains):
    need(len(rows)==N and isinstance(mains,set) and mains and all(type(r) is int and 0<=r<PUBLIC for r in mains),'public final inventory')
    count=sum(rows[r]!={r:Fraction(1)} for r in mains)
    need(count>0,'public final identity')
    for r in range(PUBLIC):
        if r not in mains: need(rows[r]=={r:Fraction(1)},'helper final identity')
    return count

class Replay:
    def __init__(self,w,origins,reference=None):
        need(w['public']==PUBLIC and w['owned_fields']==N-PUBLIC,'dimensions')
        self.w=w; self.origins=origins; self.reference=reference
        self.sp=[span(f) for f in w['frames']]
        self.rows=[{i:Fraction(1)} for i in range(N)]
        self.cur=list(w['initial'])+[None]*(N-PUBLIC);need(len(self.cur)==N,'initial charts')
        self.active=set(); self.occ=collections.Counter();self.labels=set();self.peak=0
        self.obs={};self.seen=[];self.cnt=collections.Counter();self.last_origin=-1
    def chart(self,c): need(type(c) is int and 0<=c<len(self.sp),'chart bounds')
    def role(self,r): need(type(r) is int and 0<=r<N and (r<PUBLIC or r in self.active),'inactive or invalid role')
    def observed(self,j,e,kind,payload):
        i=self.origins[j];need(type(i) is int and i>self.last_origin,'protected origin order')
        self.last_origin=i;self.seen.append(i);v=(kind,e,payload)
        if self.reference is None: self.obs[i]=v
        else: need(i in self.reference and self.reference[i]==v,'protected observation mismatch at source clock '+str(i))
    def step(self,j,e):
        need(isinstance(e,list) and len(e)>=2,'event shape');op,r=e[:2]
        need(type(r) is int and 0<=r<N,'role bounds')
        if op=='INIT':
            need(len(e)==3 and r>=PUBLIC and r not in self.active,'invalid init');self.chart(e[2])
            self.active.add(r);self.labels.add(r);self.occ[r]+=1;self.rows[r]={};self.cur[r]=e[2];self.peak=max(self.peak,len(self.active))
            self.cnt['owned']+=1;self.observed(j,e,'owned',(self.occ[r],))
        elif op=='CLEAR':
            need(len(e)==3 and r>=PUBLIC and r in self.active and self.cur[r]==e[2],'invalid clear')
            self.cnt['clears']+=1;self.cnt['owned']+=1
            self.observed(j,e,'clear',(self.occ[r],self.rows[r].copy()))
            self.active.remove(r);self.rows[r]={};self.cur[r]=None
        elif op=='MOVE':
            need(len(e)==5,'move shape');self.role(r);a,b,flag=e[2:];self.chart(a);self.chart(b)
            need(type(flag) is bool and flag==(r>=PUBLIC) and self.cur[r]==a,'move ownership or coframe')
            need((self.sp[a]<self.sp[b] or self.sp[b]<self.sp[a]) if flag else self.sp[a]<self.sp[b],'move nesting')
            self.cur[r]=b
            if flag:
                self.cnt['owned']+=1;self.observed(j,e,'owned',(self.occ[r],))
        elif op in ('ADD','COPY','SCALE'):
            need(len(e)==(4 if op=='SCALE' else 5),'scalar shape');self.role(r)
            s=None if op=='SCALE' else e[2]
            if s is not None: self.role(s);need(s!=r,'self scalar')
            raw=e[2] if s is None else e[3];need(isinstance(raw,str),'coefficient type')
            q=Fraction(raw);c=e[3] if s is None else e[4];self.chart(c)
            need(q!=0 and self.cur[r]==c and (s is None or self.cur[s]==c),'scalar coframe')
            before=self.rows[r].copy(); sr=None if s is None else self.rows[s].copy()
            if op=='COPY': need(not before,'dirty copy')
            if op=='SCALE': self.rows[r]={k:v*q for k,v in before.items() if v*q}
            elif op=='COPY': self.rows[r]={k:v*q for k,v in sr.items() if v*q}
            else:
                out=before.copy()
                for k,v in sr.items():
                    z=out.get(k,Fraction(0))+q*v
                    if z:out[k]=z
                    else:out.pop(k,None)
                self.rows[r]=out
            owned=r>=PUBLIC or (s is not None and s>=PUBLIC)
            if owned: self.cnt['interfaces']+=1
            if op=='COPY': self.cnt['copies']+=1
            if owned or op=='COPY':
                self.observed(j,e,'scalar',(self.occ[r] if r>=PUBLIC else None,self.occ[s] if s is not None and s>=PUBLIC else None,before,sr,self.rows[r].copy()))
        else: raise Refusal('unknown opcode')
    def run(self):
        for j,e in enumerate(self.w['program']): self.step(j,e)
        need(not self.active and self.cur[:PUBLIC]==self.w['final'],'final lifecycle or charts')
        need((self.cnt['clears'],self.cnt['interfaces'],self.cnt['copies'],self.cnt['owned'],len(self.labels),self.peak)==(204,700,1,455,68,50),'positive inventory')
        validate_observations(self.w['program'],self.origins,self.seen,self.reference if self.reference is not None else self.obs)
        return self

def check_case(source,base,m,word):
    rebuilt,origins,reverse=parse_manifest(m,source['program'])
    need(rebuilt==word['program'],'candidate projection mismatch')
    need({k:v for k,v in word.items() if k!='program'}=={k:v for k,v in source.items() if k!='program'},'candidate metadata changed')
    r=Replay(word,origins,base.obs).run()
    need(r.rows==base.rows and r.cur==base.cur,'endpoint mismatch')
    mains=set(source['live'])|{x+112 for x in source['live']}|set(source['hosted']['X2'])|set(source['hosted']['Y2'])
    final_public_nonidentity(r.rows,mains)
    return r,origins,reverse

def one_event(program,event):
    loc=[i for i,e in enumerate(program) if e==event];need(len(loc)==1,'mutation literal not unique');return loc[0]
def reject_control(name,source,base,m,word,kind):
    # Mutants are derived from the actual projected candidate, then replayed by
    # the same interpreter and same protected observations and final comparator.
    p=list(word['program']);_,origins,_=parse_manifest(m,source['program']); origins=list(origins)
    if kind=='preloan':
        i=one_event(p,['ADD',990,226,'-1',260]); e=p.pop(i);origins.pop(i)
        j=one_event(p,['ADD',226,1506,'-1',260]);p.insert(j,e);origins.insert(j,None)
    elif kind=='sign':
        i=one_event(p,['ADD',990,226,'-1',260]);p[i]=['ADD',990,226,'1',260]
    elif kind=='missing_decode':
        i=one_event(p,['ADD',990,226,'1',127]);p.pop(i);origins.pop(i)
    elif kind=='ownership':
        i=one_event(p,['MOVE',226,260,906,False]);p[i]=['MOVE',226,260,906,True]
    else: raise Refusal('unknown mutation')
    mutant=dict(word);mutant['program']=p
    try:
        r=Replay(mutant,origins,base.obs).run()
        need(r.rows==base.rows and r.cur==base.cur,'endpoint mismatch')
    except (Refusal,ValueError,ZeroDivisionError) as ex:
        reason=str(ex)
        if kind=='ownership': need('ownership or coframe' in reason,'ownership control wrong refusal: '+reason)
        else: need('protected observation mismatch' in reason or 'endpoint mismatch' in reason,'mutation wrong refusal: '+reason)
        return {'name':name,'rejected':True,'reason':reason}
    raise Refusal('mutation accepted: '+name)

def metadata_controls(source, manifest):
    # Exercise the production projection parser against actual source literals.
    def reject(name, m, reason):
        try: parse_manifest(m,source['program'])
        except Refusal as ex:
            need(reason in str(ex),'metadata control wrong refusal '+name+': '+str(ex))
            return {'name':name,'rejected':True,'reason':str(ex)}
        raise Refusal('metadata control accepted: '+name)
    def clone(x): return json.loads(json.dumps(x))
    first=manifest['delete'][0]
    key='source_index' if 'source_index' in first else 'source_clock'
    boolean=clone(manifest);boolean['delete'][0][key]=False
    duplicate=clone(manifest);duplicate['delete'].append(clone(first))
    mismatch=clone(manifest);mismatch['delete'][0]['event']=['INVALID',0]
    clear=next(i for i,e in enumerate(source['program']) if e[0]=='CLEAR')
    protected=clone(manifest);protected['delete'].append({key:clear,'event':source['program'][clear]})
    return [reject('boolean_clock',boolean,'delete clock or literal'),
            reject('duplicate_clock',duplicate,'delete clock or literal'),
            reject('wrong_literal',mismatch,'delete clock or literal'),
            reject('deleted_clear',protected,'deleted protected event')]

def source_free_controls():
    rejected=[]
    def reject(name,func,expected):
        try: func()
        except Refusal as ex:
            need(expected in str(ex),'control wrong refusal '+name+': '+str(ex))
            rejected.append(name);return
        raise Refusal('control accepted '+name)
    w={'public':PUBLIC,'owned_fields':N-PUBLIC,'frames':[[],[1]],'initial':[0]*PUBLIC,'final':[0]*PUBLIC,'program':[]}
    r=Replay(w,list(range(4)))
    need(r.rows[1501]=={1501:Fraction(1)},'dirty entry control')
    r.step(0,['INIT',1501,0]);need(r.rows[1501]=={},'init reset control')
    r.step(1,['COPY',1501,0,'2',0])
    need(r.rows[1501]=={0:Fraction(2)} and r.obs[1][2][2]=={} and r.obs[1][2][4]=={0:Fraction(2)},'copy assignment and guard control')
    before=dict(r.rows[1501]); observation_count=len(r.obs)
    reject('dirty_copy',lambda:r.step(2,['COPY',1501,0,'1',0]),'dirty copy')
    need(r.rows[1501]==before and len(r.obs)==observation_count,'dirty copy mutated state')
    r.step(3,['CLEAR',1501,0]);need(r.obs[3][2][1]==before and r.rows[1501]=={} and 1501 not in r.active,'clear before reset control')
    program=([['CLEAR',1501,0]]*204 + [['INIT',1501,0]]*251 + [['ADD',1501,0,'1',0]]*700 + [['COPY',0,1,'1',0]])
    origins=list(range(len(program)));expected=[i for i,e in enumerate(program) if special(e)]; refs={i:('fixture',) for i in expected}
    validate_observations(program,origins,expected,refs)
    reject('both_empty',lambda:validate_observations(program,origins,[],{}),'missing or duplicate observations')
    reject('missing_reference',lambda:validate_observations(program,origins,expected,{}),'reference observation coverage')
    reject('empty_event_inventory',lambda:validate_observations([],[],[],{}),'positive event-derived observation inventory')
    for name,clock in [('clear',0),('owned',204),('interface',455),('copy',len(program)-1)]:
        reject('missing_'+name,lambda c=clock:validate_observations(program,origins,[i for i in expected if i!=c],refs),'missing or duplicate observations')
        reject('duplicate_'+name,lambda c=clock:validate_observations(program,origins,expected+[c],refs),'missing or duplicate observations')
        bad=dict(refs);bad.pop(clock)
        reject('missing_reference_'+name,lambda b=bad:validate_observations(program,origins,expected,b),'reference observation coverage')
    rows=[{i:Fraction(1)} for i in range(N)]
    reject('identity_public_final',lambda:final_public_nonidentity(rows,{0}),'public final identity')
    rows[0]={1:Fraction(1)};need(final_public_nonidentity(rows,{0})==1,'nonidentity positive control')
    return {'status':'PASS_SOURCE_FREE_CONTROLS','rejected':rejected,'positive':['dirty_entry','init_reset','copy_prewrite_and_assignment','clear_pre_reset','nonidentity_public_final']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--controls-only',action='store_true');ap.add_argument('--source');ap.add_argument('--source-metadata')
    ap.add_argument('--case',action='append',nargs=3,metavar=('NAME','WORD','MANIFEST'))
    ap.add_argument('--out');a=ap.parse_args()
    if a.controls_only:
        need(not any((a.source,a.source_metadata,a.case,a.out)),'controls-only takes no other arguments')
        print(json.dumps(source_free_controls(),sort_keys=True));return 0
    need(all((a.source,a.source_metadata,a.case,a.out)),'missing run arguments')
    need(len(a.case)==3 and {x[0] for x in a.case}=={'courier','restop','joint'},'required exact case names')
    out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    result={'status':'REFUSED','cases':[],'controls':[],'scope':'literal exact dirty-entry conditional first gate; no erasure, phase, price or physical qualification'}
    try:
        result['source_free_controls']=source_free_controls()
        source,gz,can=readword(a.source); meta=json.loads(Path(a.source_metadata).read_bytes())
        need(gz==SOURCE_GZ and can==SOURCE_CAN and meta['gzip_sha256']==gz and meta['canonical_sha256']==can and meta['source_head']==HEAD,'source custody')
        need(len(source['program'])==EVENTS,'source event count')
        mains=set(source['live'])|{x+112 for x in source['live']}|set(source['hosted']['X2'])|set(source['hosted']['Y2'])
        base=Replay(source,list(range(EVENTS))).run();final_public_nonidentity(base.rows,mains);result['source']={'gzip_sha256':gz,'canonical_sha256':can,'protected_observations':len(base.obs),'counts':dict(base.cnt),'labels':len(base.labels),'peak':base.peak}
        restop=None; canonical_seen={SOURCE_CAN}
        for name,wp,mp in a.case:
            w,g,c=readword(wp);raw=Path(mp).read_bytes();m=json.loads(raw)
            need(c not in canonical_seen and w['program']!=source['program'],'candidate not distinct or unchanged');canonical_seen.add(c)
            check_case(source,base,m,w)
            result['cases'].append({'name':name,'gzip_sha256':g,'canonical_sha256':c,'manifest_sha256':sha(raw),'events':len(w['program']),'status':'PASS'})
            if name=='restop':restop=(m,w)
        need(restop is not None,'case named restop required for controls')
        result['controls'].extend(metadata_controls(source,restop[0]))
        for k in ('preloan','sign','missing_decode','ownership'):
            result['controls'].append(reject_control(k,source,base,*restop,k))
        result['status']='PASS_LITERAL_EXACT_ONLY'
    except Exception as ex:
        result['error']={'type':type(ex).__name__,'message':str(ex)}
    (out/'result.json').write_bytes(canon(result)+b'\n')
    print(json.dumps({'status':result['status'],'cases':len(result['cases']),'controls':len(result['controls']),'error':result.get('error')},sort_keys=True),flush=True)
    return 0 if result['status']=='PASS_LITERAL_EXACT_ONLY' else 1
if __name__=='__main__': raise SystemExit(main())
