#!/usr/bin/env python3
"""Strict paired 204 CLEAR certificate and remaining-live-rank gate.

No stored rank is trusted: closed active-row replay plus fresh final public rank
proves rank of ALL OTHER LIVE rows at each CLEAR. It does not prove public-only
rank at any cut, nor physical erasure, rounding, phase, or supplier U.
"""
import argparse
import copy
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

SOURCE_GZ='bfe2a4fb54dd82940ba78d8b3efd4f587e3fc9e978ccfd48561199d2c9fb4887'
SOURCE_CAN='c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de'
CERT_SHA='7b9bd8c52beeaca7331c49a7904eeee92b9eaf830311bfdbbc60b69a57c77a6d'
EDITS={38369:(["MOVE",902,3,618,False],["MOVE",902,3,373,False]),
38623:(["MOVE",1091,373,618,False],None),
40279:(["ADD",1091,902,"1/2",618],["ADD",1091,902,"1/2",373]),
40280:(["MOVE",1091,618,733,False],["MOVE",1091,373,733,False]),
41663:(["MOVE",902,618,913,False],["MOVE",902,373,913,False])}

def need(ok,msg):
    if not ok: raise ValueError(msg)
def sha(b): return hashlib.sha256(b).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def load(p): return json.loads(Path(p).read_bytes())
def output(p,x): Path(p).write_bytes(canon(x)+b'\n')
def index(k,n):
    need(isinstance(k,str) and k.isascii() and k.isdigit() and str(int(k))==k,'noncanonical index')
    i=int(k); need(0<=i<n,'index outside public domain'); return i

def unpack(d,n):
    need(isinstance(d,dict),'row not object'); out={}
    for k,v in d.items():
        i=index(k,n); need(isinstance(v,str),'rational not text')
        q=Q(v); need(q!=0,'zero rational entry'); out[i]=q
    return out

def pack(d): return {str(k):str(v) for k,v in sorted(d.items()) if v}
def rank(rows):
    pivots={}
    for row in rows:
        cur=dict(row)
        while cur:
            col=min(cur)
            if col not in pivots:
                v=cur[col]; pivots[col]={k:x/v for k,x in cur.items()}; break
            p=pivots[col]; f=cur[col]
            for k,v in p.items():
                x=cur.get(k,Q(0))-f*v
                if x: cur[k]=x
                else: cur.pop(k,None)
    return len(pivots)

def check_record(c,idx,clock,owner,occ,chart,dim,init,init_chart,moves,live,rows,n):
    need(isinstance(c,dict) and c['clear_index']==idx and c['event']==clock and c['field']==owner,'clear index/clock/owner mismatch')
    need(c['lifetime']==occ and c['chart']==chart and c['dim']==dim and c['init_event']==init and c['init_chart']==init_chart and c['owned_moves']==moves,'lifetime metadata mismatch')
    target=unpack(c['erased'],n); coeff=unpack(c['certificate'],n)
    need(c['erased_support']==len(target) and c['terms']==len(coeff),'support count mismatch')
    need(c['other_live']==len(live)-1 and c['other_rank']==n and c['verified_exact'] is True,'rank/metadata mismatch')
    need(target==rows[owner],'erased row mismatch')
    acc={}
    for k,v in coeff.items():
        need(k in live and k!=owner,'provider not live or is target')
        for col,x in rows[k].items():
            z=acc.get(col,Q(0))+v*x
            if z:acc[col]=z
            else:acc.pop(col,None)
    need(acc==target,'certificate relation mismatch')
    need(bool(target) or not coeff,'zero clear must have empty certificate')
    return {'clear_index':idx,'event':clock,'field':owner,'lifetime':occ,'chart':chart,
            'erased':pack(target),'certificate':pack(coeff),'public_support':len(coeff)}

def replay(w,certs,n,expected_count,expected_zeros,dirty_init=False):
    need(w['public']==n and type(w['owned_fields']) is int and w['owned_fields']>=0,'dimensions')
    N=n+w['owned_fields']; frames=w['frames']; initial=w['initial']; final=w['final']
    need(len(initial)==len(final)==n,'public boundary shape')
    def chart(c): need(type(c) is int and 0<=c<len(frames),'invalid chart')
    def role(r): need(type(r) is int and 0<=r<N and r in live,'illegal/inactive operand')
    for c in initial+final:chart(c)
    rows=[{i:Q(1)} for i in range(n)]+[{} for _ in range(N-n)]
    live=set(range(n)); cur=list(initial)+[None]*(N-n); occ=Counter(); opened={}; records=[]; zeros=0; peak=0
    need(len(certs)==expected_count,'certificate inventory mismatch')
    for i,e in enumerate(w['program']):
        need(isinstance(e,list) and len(e)>=2,'malformed event')
        op,r=e[:2]; need(type(r) is int and 0<=r<N,'invalid field')
        if op=='INIT':
            need(len(e)==3 and r>=n and r not in live,'illegal INIT');chart(e[2])
            rows[r]={0:Q(1)} if dirty_init else {}; need(not rows[r],'nonzero fresh INIT')
            live.add(r);cur[r]=e[2];occ[r]+=1;opened[r]={'init':i,'chart':e[2],'moves':[]};peak=max(peak,len(opened))
        elif op=='CLEAR':
            need(len(e)==3 and r>=n and r in opened and r in live and cur[r]==e[2],'illegal CLEAR')
            z=opened[r]; idx=len(records);need(idx<len(certs),'missing certificate')
            item=check_record(certs[idx],idx,i,r,occ[r],e[2],len(frames[e[2]]),z['init'],z['chart'],z['moves'],live,rows,n)
            zeros+=not bool(rows[r]); records.append(item); del opened[r]; live.remove(r); rows[r]={};cur[r]=None
        elif op=='MOVE':
            need(len(e)==5,'MOVE shape'); role(r);a,b,flag=e[2:];chart(a);chart(b)
            need(type(flag) is bool and flag==(r>=n) and cur[r]==a,'MOVE ownership/coframe')
            cur[r]=b
            if r>=n:opened[r]['moves'].append([i,a,b])
        elif op in ('ADD','COPY','SCALE'):
            need(len(e)==(4 if op=='SCALE' else 5),'scalar shape');role(r)
            src=None if op=='SCALE' else e[2]
            if src is not None:role(src);need(src!=r,'self scalar')
            v=Q(e[2] if src is None else e[3]); c=e[3] if src is None else e[4]; chart(c)
            need(v!=0 and cur[r]==c and (src is None or cur[src]==c),'scalar coframe/coefficient')
            if op=='COPY':
                need(not rows[r],'COPY dirty destination');rows[r]={k:v*x for k,x in rows[src].items() if v*x}
            elif op=='SCALE':rows[r]={k:v*x for k,x in rows[r].items() if v*x}
            else:
                d=dict(rows[r])
                for k,x in rows[src].items():
                    z=d.get(k,Q(0))+v*x
                    if z:d[k]=z
                    else:d.pop(k,None)
                rows[r]=d
        else:raise ValueError('unknown opcode / external birth or reload')
    need(len(records)==expected_count and zeros==expected_zeros,'clear or zero count mismatch')
    need(not opened and live==set(range(n)) and cur[:n]==final,'final ownership/charts')
    final_rank=rank_guard(rows[:n],n)
    return {'records':records,'final_public_rank':final_rank,'peak':peak,'zero_rows':zeros,
            'public_support_terms':sum(x['public_support'] for x in records),
            'final_public_rows':[pack(x) for x in rows[:n]],
            'other_rank_definition':'rank of all other live rows immediately before CLEAR',
            'rank_argument':'closed active-row span nonincreasing from initial n, final public rank n'}

def bind_lifetimes(program,certs,n):
    # Derive lifetime ordinals from literal INIT/CLEAR chronology, not supplier metadata.
    out=copy.deepcopy(certs); counts=Counter(); active={}; j=0
    for i,e in enumerate(program):
        if e[0]=='INIT':
            r=e[1]; need(type(r) is int and r>=n and r not in active,'lifetime INIT binding')
            counts[r]+=1; active[r]=counts[r]
        elif e[0]=='CLEAR':
            r=e[1]; need(r in active and j<len(out),'lifetime CLEAR binding')
            need(out[j]['clear_index']==j and out[j]['event']==i and out[j]['field']==r,'lifetime source record order')
            out[j]['lifetime']=active.pop(r);j+=1
    need(not active and j==len(out),'lifetime complete binding')
    return out

def endpoint_guard(source,candidate):
    need(source==candidate,'final public endpoint mismatch')

def map_records(certs,reverse):
    out=copy.deepcopy(certs)
    for c in out:
        for key in ('event','init_event'):
            x=c[key];need(type(x) is int and 0<=x<len(reverse) and reverse[x] is not None,'unmapped lifetime clock');c[key]=reverse[x]
        for m in c['owned_moves']:
            need(isinstance(m,list) and len(m)==3 and type(m[0]) is int and 0<=m[0]<len(reverse) and reverse[m[0]] is not None,'unmapped move');m[0]=reverse[m[0]]
    return out

def fixture_cert(i,event,field,init,erased,cert,other_live,n,lifetime=1):
    return {'clear_index':i,'event':event,'field':field,'lifetime':lifetime,'chart':0,'dim':1,'init_event':init,'init_chart':0,'owned_moves':[],
      'erased_support':len(erased),'erased':erased,'other_live':other_live,'other_rank':n,'certificate':cert,'terms':len(cert),'verified_exact':True}

def controls():
    # Pro's public-rank counterexample: remaining live rank is 2 at first
    # CLEAR despite public rank 1; both certificates have public providers.
    w={'public':2,'owned_fields':2,'frames':[[0]],'initial':[0,0],'final':[0,0],
       'program':[['INIT',2,0],['INIT',3,0],['ADD',2,0,'1',0],['ADD',0,2,'-1',0],['ADD',3,1,'1',0],['CLEAR',3,0],['ADD',0,2,'1',0],['CLEAR',2,0]]}
    cs=[fixture_cert(0,5,3,1,{'1':'1'},{'1':'1'},3,2),fixture_cert(1,7,2,0,{'0':'1'},{'0':'1'},2,2)]
    result=replay(w,cs,2,2,0); need(result['final_public_rank']==2 and rank([{}, {1:Q(1)}])==1,'public-rank counterexample')
    def rejects(label,fn,reason=None):
        try:fn()
        except (ValueError,KeyError,IndexError,ZeroDivisionError) as e:
            if reason is not None:need(reason in str(e),'control rejected for wrong reason: '+label+' '+str(e))
            return label
        raise ValueError('control accepted: '+label)
    tests=[]
    # Synthetic positive nonzero relation in the exact production predicate:
    # target x+y, two live public providers x and y, and an active owner.
    rows=[{0:Q(1)},{1:Q(1)},{0:Q(1),1:Q(1)}]
    good=fixture_cert(0,4,2,0,{'0':'1','1':'1'},{'0':'1','1':'1'},2,2)
    def check(c):return check_record(c,0,4,2,1,0,1,0,0,[],{0,1,2},rows,2)
    check(good)
    for label,change,reason in (
      ('witness_coefficient',lambda c:c['certificate'].__setitem__('0','2'),'certificate relation mismatch'),
      ('delete_witness_term',lambda c:(c['certificate'].pop('0'),c.__setitem__('terms',1)),'certificate relation mismatch'),
      ('corrupt_erased_row',lambda c:c['erased'].__setitem__('0','2'),'erased row mismatch'),
      ('wrong_event',lambda c:c.__setitem__('event',5),'clear index/clock/owner mismatch'),
      ('wrong_owner',lambda c:c.__setitem__('field',1),'clear index/clock/owner mismatch'),
      ('wrong_init_event',lambda c:c.__setitem__('init_event',1),'lifetime metadata mismatch'),
      ('wrong_lifetime',lambda c:c.__setitem__('lifetime',2),'lifetime metadata mismatch'),
      ('wrong_chart',lambda c:c.__setitem__('chart',1),'lifetime metadata mismatch')):
        mutated=copy.deepcopy(good);change(mutated)
        tests.append(rejects(label,lambda m=mutated:check(m),reason))
    a=copy.deepcopy(cs);a[0]['other_rank']=1;tests.append(rejects('falsified_other_rank',lambda:replay(w,a,2,2,0)))
    # A=x, B=y; copy A to owned S, then subtract S from A. Removing S
    # destroys x although a fabricated record continues to claim rank two.
    fabricated=copy.deepcopy(cs); need(all(x['other_rank']==2 for x in fabricated),'fixture metadata')
    retained=[{}, {1:Q(1)}, {0:Q(1)}]; need(rank(retained)==2,'fixture pre-clear rank')
    tests.append(rejects('final_rank_loss_with_fabricated_metadata',lambda:rank_guard(retained[:2],2)))
    tests.append(rejects('dirty_fresh_INIT',lambda:replay(w,cs,2,2,0,dirty_init=True)))
    bad=copy.deepcopy(w);bad['program'][2]=['RELOAD',2,0];tests.append(rejects('external_reload',lambda:replay(bad,cs,2,2,0)))
    # At first clear, S is a live owned row; equality can be valid while forbidden.
    tests.append(rejects('owned_provider',lambda:check_record(fixture_cert(0,0,3,0,{'0':'1'},{'2':'1'},3,2),0,0,3,1,0,1,0,0,[],{0,1,2,3},[{0:Q(1)},{1:Q(1)},{0:Q(1)},{0:Q(1)}],2)))
    z={'public':1,'owned_fields':1,'frames':[[0]],'initial':[0],'final':[0],'program':[['INIT',1,0],['CLEAR',1,0],['INIT',1,0],['CLEAR',1,0]]}
    zc=[fixture_cert(0,1,1,0,{}, {},1,1),fixture_cert(1,3,1,2,{}, {},1,1,lifetime=2)]
    replay(z,zc,1,2,2)
    tests.append(rejects('missing_zero_clear',lambda:replay(z,zc[:1],1,2,2)))
    tests.append(rejects('duplicate_zero_clear_same_count',lambda:replay(z,[zc[0],zc[0]],1,2,2)))
    bad=copy.deepcopy(w);bad['program'][3]=['COPY',0,2,'1',0];tests.append(rejects('dirty_COPY',lambda:replay(bad,cs,2,2,0)))
    tests.append(rejects('negative_provider',lambda:unpack({'-1':'1'},2)))
    tests.append(rejects('boolean_provider',lambda:unpack({True:'1'},2)))
    tests.append(rejects('final_public_nonidentity',lambda:endpoint_guard([{'0':'1'},{'1':'1'}],[{'1':'1'},{'0':'1'}]),'final public endpoint mismatch'))
    # Production binding and map with a fixed 204-record denominator, including
    # zero rows. Replace, rather than append, one certificate to preserve count.
    program=[]; records=[]
    for i in range(204):
        program.extend([['INIT',1,0],['CLEAR',1,0]])
        records.append(fixture_cert(i,2*i+1,1,2*i,{}, {},1,1,lifetime=i+1))
    bound=bind_lifetimes(program,records,1); identity=list(range(len(program)))
    mapped=map_records(bound,identity);need(len(mapped)==204,'fixture 204 mapping')
    tests.append(rejects('missing_204_zero',lambda:bind_lifetimes(program,records[:-1],1)))
    duplicate=copy.deepcopy(records);duplicate[100]=copy.deepcopy(duplicate[99])
    tests.append(rejects('duplicate_204_zero_same_count',lambda:bind_lifetimes(program,duplicate,1),'lifetime source record order'))
    return {'rejected':tests,'public_rank_counterexample':'accepted remaining-live rank 2, public rank 1 at cut; final rank 2'}

def rank_guard(rows,n):
    actual=rank(rows); need(actual==n,'final public rank loss'); return actual

def main(root,built,out):
    root=Path(root);built=Path(built);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    try:
        pkg=root/'inputs/pr7624/research/p104-w2-primal-dual-bypass'
        sr=(pkg/'data/word.json.gz').read_bytes();cr=(built/'candidate-word.json.gz').read_bytes();cert_raw=(pkg/'evidence/certs-step1.json').read_bytes();m=load(built/'edit-manifest.json')
        need(sha(sr)==SOURCE_GZ and sha(cert_raw)==CERT_SHA,'source bytes mismatch')
        s=json.loads(gzip.decompress(sr)); c=json.loads(gzip.decompress(cr));doc=json.loads(cert_raw); sc=doc['clears']
        need(sha(canon(s))==SOURCE_CAN and m['source_canonical_sha256']==SOURCE_CAN and m['source_gzip_sha256']==SOURCE_GZ,'source canonical/manifest mismatch')
        need(sha(canon(c))==m['candidate_canonical_sha256'] and sha(cr)==m['candidate_gzip_sha256'],'candidate hash mismatch')
        need(doc['summary']['sha256']==SOURCE_GZ and doc['summary']['clears']==doc['summary']['certified']==len(sc)==204,'source certificate identity')
        need((s['public'],s['owned_fields'],len(s['program']))==(1501,68,77372) and len(c['program'])==77371,'word shape')
        need({k:v for k,v in s.items() if k!='program'}=={k:v for k,v in c.items() if k!='program'},'metadata mismatch')
        need(m['metadata_sha256']==sha(canon({k:v for k,v in s.items() if k!='program'})),'metadata hash mismatch')
        expect=[{'original_index':i,'old':a,'new_or_null':b} for i,(a,b) in EDITS.items()]
        need(m['edits']==expect,'five edits mismatch')
        orig=[i for i in range(len(s['program'])) if i!=38623];rev=[None if i==38623 else i-(i>38623) for i in range(len(s['program']))]
        need(m['candidate_origins']==orig and m['original_to_candidate']==rev,'origin map mismatch')
        for i,e in enumerate(s['program']):
            if i in EDITS:
                old,new=EDITS[i];need(e==old,'source edit literal')
                if new is None:continue
                need(c['program'][rev[i]]==new,'candidate edit literal')
            else:need(c['program'][rev[i]]==e,'unadvertised edit')
        sc=bind_lifetimes(s['program'],sc,1501)
        cc=map_records(sc,rev)
        control=controls();source=replay(s,sc,1501,204,7);candidate=replay(c,cc,1501,204,7)
        need(source['peak']==candidate['peak']==50,'peak differs')
        endpoint_guard(source['final_public_rows'],candidate['final_public_rows'])
        for a,b in zip(source['records'],candidate['records']):
            need(a['event']!=38623 and rev[a['event']]==b['event'],'clear mapping')
            need({k:v for k,v in a.items() if k!='event'}=={k:v for k,v in b.items() if k!='event'},'changed owned clear or certificate')
        sd={'summary':dict(doc['summary']),'clears':sc};cd={'summary':dict(doc['summary']),'clears':cc};cd['summary']['sha256']=sha(cr);cd['summary']['word']='candidate-word.json.gz'
        output(out/'source-certificates.json',sd);output(out/'candidate-certificates.json',cd)
        report={'schema':'compose7624-certificates/v1','status':'PASS_CERTIFICATES_204','source_gzip_sha256':sha(sr),'source_canonical_sha256':SOURCE_CAN,'candidate_gzip_sha256':sha(cr),'candidate_canonical_sha256':sha(canon(c)),'source_certificate_sha256':sha(cert_raw),'manifest_sha256':sha((built/'edit-manifest.json').read_bytes()),'source':source,'candidate':candidate,'controls':control,'limitations':['remaining-live rank is not public-only rank at cuts','no physical erasure or numerical supplier U established']}
        output(out/'certificate.json',report);output(out/'status.json',{'status':report['status'],'certificate_sha256':sha((out/'certificate.json').read_bytes()),'source_count':204,'candidate_count':204})
    except Exception as e:
        output(out/'status.json',{'status':'INCOMPLETE','error_type':type(e).__name__,'error':str(e)})
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root');p.add_argument('--built');p.add_argument('--out');p.add_argument('--controls-only',action='store_true');a=p.parse_args()
    if a.controls_only:
        need(not any((a.root,a.built,a.out)),'controls-only takes no word arguments')
        print(json.dumps({'status':'PASS_CONTROLS_ONLY','controls':controls(),'optimized_mode_safe':'explicit raises; other scientific oracles have separate mode policies'},sort_keys=True))
    else:
        need(all((a.root,a.built,a.out)),'--root, --built, --out required');main(a.root,a.built,a.out)
