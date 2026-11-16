#!/usr/bin/env python3
"""One fixed #7620 rank-one differential certificate, not a physical proof."""
import argparse
import bisect
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path

N=1569; NP=1501; CUT=38487
SOURCE='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d'
SOURCE_GZ='2eb2cf1d29529c68a6cb1c0639de3065a805858d3492068e76b70c5a5e80a81c'
EDITS={38486:(["MOVE",902,3,595,False],["MOVE",902,3,373,False]),
38487:(["ADD",1532,902,"2",595],None),
38785:(["ADD",1479,902,"-1/2",595],None),
38786:(["ADD",1255,902,"-1",595],None),
38787:(["ADD",1495,902,"-3/2",595],None),
38788:(["MOVE",1091,373,618,False],None),
38789:(["MOVE",902,595,618,False],None),
38790:(["ADD",1091,902,"1/2",618],["ADD",1091,902,"1/2",373]),
38813:(["MOVE",1091,618,733,False],["MOVE",1091,373,733,False]),
41448:(["MOVE",902,618,913,False],["MOVE",902,373,913,False])}
INCIDENTS=[(37803,['ADD',1091,1097,'1/2',373]),(38482,['ADD',643,902,'-1/4',3]),(38483,['ADD',496,902,'-1/2',3]),(38484,['ADD',1466,902,'1/2',3]),(38485,['ADD',450,902,'-1/2',3]),(38486,EDITS[38486][0]),(38487,EDITS[38487][0]),(38785,EDITS[38785][0]),(38786,EDITS[38786][0]),(38787,EDITS[38787][0]),(38788,EDITS[38788][0]),(38789,EDITS[38789][0]),(38790,EDITS[38790][0]),(38813,EDITS[38813][0]),(38815,['ADD',1091,1093,'-1',733]),(38941,['MOVE',1091,733,238,False]),(38943,['ADD',1091,1087,'1',238]),(41448,EDITS[41448][0]),(41449,['ADD',985,902,'-1',913])]
INJECTIONS={38487:(1532,F(-2)),38785:(1479,F(1,2)),38786:(1255,F(1)),38787:(1495,F(3,2))}


def require(x,msg):
    if not x: raise ValueError(msg)

def digest(b): return hashlib.sha256(b).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def load_gz(p):
    b=Path(p).read_bytes();return json.loads(gzip.decompress(b)),digest(b)
def unpack(row):
    require(isinstance(row,dict),'row must be dictionary'); out={}
    for k,v in row.items():
        i=int(k);q=F(v)
        require(str(i)==k and 0<=i<N and q,'bad row entry');out[i]=q
    return out

def pack(row): return {str(k):str(v) for k,v in sorted(row.items()) if v}
def put(a,i,v):
    if v:a[i]=v
    else:a.pop(i,None)

def multiply(c,b):return {i:q*b for i,q in c.items() if q*b}
def difference(a,b):
    z=unpack(a)
    for i,v in unpack(b).items():put(z,i,z.get(i,F(0))-v)
    return z

def reverse_prefix(program):
    # c is the covector of normalized field 902 at CUT, before the ADD.
    z={902:F(1)}
    for event in reversed(program[:CUT]):
        op,r=event[:2]; a=z.get(r,F(0))
        if op in ('INIT','CLEAR'):z.pop(r,None)
        elif op=='MOVE':pass
        elif op=='SCALE':put(z,r,a*F(event[2]))
        elif op=='ADD':put(z,event[2],z.get(event[2],F(0))+a*F(event[3]))
        elif op=='COPY':
            z.pop(r,None);put(z,event[2],z.get(event[2],F(0))+a*F(event[3]))
        else:raise ValueError('unknown prefix opcode')
    require(z,'source covector c is zero');return z

def index_rows(seq,kind):
    out={}
    for x in seq:
        key=x['original_clock'];require(type(key) is int and key not in out,'duplicate '+kind+' clock');out[key]=x
    return out

def assert_identity(a,b,fields,label):
    for f in fields:require(a[f]==b[f],label+' mismatch '+f)

def compare_row(candidate,original,b,c,label):
    require(difference(candidate,original)==multiply(c,b),'rank-one mismatch '+label)


def certificate(root,built,exact):
    root=Path(root);built=Path(built);exact=Path(exact)
    word,wsha=load_gz(root/'inputs/pr7620/data/word.json.gz')
    require(wsha==SOURCE_GZ and digest(canonical(word))==SOURCE,'source custody')
    cand,csha=load_gz(built/'candidate-word.json.gz')
    manifest=json.loads((built/'edit-manifest.json').read_text())
    result,esha=load_gz(exact/'EXACT.json.gz')
    exact_raw=gzip.decompress((exact/'EXACT.json.gz').read_bytes())
    exact_status_raw=(exact/'status.json').read_bytes()
    exact_status=json.loads(exact_status_raw)
    require(exact_status.get('status')=='U_CONDITIONAL_LITERAL_EXACT_ONLY', 'exact stage not successful')
    require(exact_status.get('exact_gzip_sha256')==esha and exact_status.get('exact_sha256')==digest(exact_raw), 'exact output hash mismatch')
    require(exact_raw==canonical(result), 'exact output encoding mismatch')
    require(result['schema']=='compose7620-exact/v1','exact schema')
    binding=result['source']
    require(exact_status.get('source')==binding, 'exact status source binding mismatch')
    require(binding['original_canonical_sha256']==SOURCE and binding['original_gzip_sha256']==wsha and binding['candidate_canonical_sha256']==digest(canonical(cand)) and binding['candidate_gzip_sha256']==csha and binding['manifest_sha256']==digest((built/'edit-manifest.json').read_bytes()), 'exact receipt binding')
    require(word['public']==NP and word['owned_fields']==68 and len(word['program'])==77194,'source shape')
    require(len(cand['program'])==77188,'candidate size')
    for k in word:
        if k!='program':require(cand.get(k)==word[k],'metadata differs '+k)
    require(set(cand)==set(word),'metadata keys differ')
    program=word['program']; origin=[]; expected=[]
    def operands(e):return {e[1],e[2]} if e[0] in ('ADD','COPY') else {e[1]}
    require([(i,program[i]) for i in range(37803,41450) if operands(program[i]) & {902,1091}]==INCIDENTS,'incident closure')
    require(program[41461]==['ADD',902,985,'1/2',913], 'later 902 feedback literal')
    require(program[41465]==['ADD',1548,902,'-1/2',913], 'later 1548 owned read literal')
    for i,e in enumerate(program):
        if i in EDITS:
            old,new=EDITS[i];require(e==old,'source edit literal '+str(i))
            if new is not None:origin.append(i);expected.append(new)
        else:origin.append(i);expected.append(e)
    require(cand['program']==expected,'candidate literal reconstruction')
    require(manifest.get('schema')=='compose7620-edit-manifest/v1', 'manifest schema')
    require(manifest.get('source_git_blob')=='2b8a259e017748ab5a3b98c22b42b8d3113edfce', 'manifest source blob')
    require(manifest['source_canonical_sha256']==SOURCE and manifest['source_gzip_sha256']==wsha, 'manifest source binding')
    require(manifest['candidate_canonical_sha256']==digest(canonical(cand)) and manifest['candidate_gzip_sha256']==csha, 'manifest candidate binding')
    require(manifest['candidate_origins']==origin,'manifest origin mismatch')
    reverse=[None]*len(program)
    for j,i in enumerate(origin):reverse[i]=j
    require(manifest['original_to_candidate']==reverse,'manifest reverse mismatch')
    for i in range(CUT+1,38788):
        e=program[i]
        require(not(e[0] in ('ADD','COPY','SCALE','INIT','CLEAR') and e[1]==902),'902 changed between removed deliveries')
    c=reverse_prefix(program)
    old=result['original'];new=result['candidate']
    oldclear=index_rows(old['clears'],'old clear');newclear=index_rows(new['clears'],'new clear')
    oldint=index_rows(old['interfaces'],'old interface');newint=index_rows(new['interfaces'],'new interface')
    oldcopy=index_rows(old['copy_guards'],'old copy');newcopy=index_rows(new['copy_guards'],'new copy')
    virtual=index_rows(new['virtual_deleted_interfaces'],'virtual deleted interface')
    expectedclear={i for i,e in enumerate(program) if e[0]=='CLEAR'}
    expectedcopy={i for i,e in enumerate(program) if e[0]=='COPY'}
    expectedint={i for i,e in enumerate(program) if (e[0]=='SCALE' and e[1]>=NP) or (e[0] in ('ADD','COPY') and (e[1]>=NP or e[2]>=NP))}
    require(len(oldclear)==len(newclear)==167 and set(oldclear)==set(newclear)==expectedclear,'CLEAR census')
    require(set(oldcopy)==expectedcopy and set(oldint)==expectedint,'original observation inventory')
    require(set(oldcopy)==set(newcopy),'COPY census')
    deleted_owned={i for i,e in enumerate(program) if i in INJECTIONS and (e[1]>=NP or e[2]>=NP)}
    require(set(oldint)-set(newint)==deleted_owned and not(set(newint)-set(oldint)),'owned interface census')
    require(set(virtual)==deleted_owned,'virtual deleted interface census')
    beta=[F(0)]*N; trace=[]; transitions=[]; feedback=[]; clear_receipt=[]; interface_receipt=[]; copy_receipt=[]
    seen_clear=set();seen_int=set();seen_copy=set()
    for i,e in enumerate(program):
        op,r=e[:2]; bbefore=beta[r]; source_before=beta[e[2]] if op in ('ADD','COPY') else None
        if i in oldclear:
            require(op=='CLEAR' and e[1]==oldclear[i]['owner'] and e[2]==oldclear[i]['chart'],'clear original binding')
            a,b=oldclear[i],newclear[i]
            assert_identity(a,b,['owner','lifetime','chart'],'CLEAR')
            require(a['candidate_clock']==reverse[i] and b['candidate_clock']==reverse[i], 'CLEAR candidate clock')
            compare_row(b['row'],a['row'],beta[r],c,'CLEAR '+str(i))
            clear_receipt.append({'original_clock':i,'candidate_clock':reverse[i],'owner':r,'lifetime':a['lifetime'],'chart':a['chart'],'beta':str(beta[r])});seen_clear.add(i)
        if i in oldcopy:
            require(op=='COPY','copy original binding');a,b=oldcopy[i],newcopy[i]
            assert_identity(a,b,['dest','source','chart','dest_lifetime','source_lifetime'],'COPY')
            require(a['candidate_clock']==reverse[i] and b['candidate_clock']==reverse[i], 'COPY candidate clock')
            compare_row(b['row'],a['row'],beta[r],c,'COPY guard '+str(i))
            require(not unpack(a['row']) and not unpack(b['row']),'dirty COPY guard')
            copy_receipt.append({'original_clock':i,'candidate_clock':reverse[i],'dest':r,'beta':str(beta[r])});seen_copy.add(i)
        if i in oldint:
            a=oldint[i];b=virtual[i] if i in deleted_owned else newint[i]
            require(a['event']==e and b['event']==e, 'interface original event mismatch')
            assert_identity(a,b,['dest','source','dest_lifetime','source_lifetime','chart'],'interface')
            require(a['candidate_clock']==reverse[i] and b['candidate_clock']==reverse[i], 'interface candidate clock')
            if i in deleted_owned:
                require(b.get('candidate_cut')==bisect.bisect_left(origin,i), 'virtual deleted candidate cut mismatch')
            compare_row(b['dest_before'],a['dest_before'],beta[r],c,'interface dest '+str(i))
            s=e[2] if op in ('ADD','COPY') else None
            if s is not None:compare_row(b['source_before'],a['source_before'],beta[s],c,'interface source '+str(i))
            interface_receipt.append({'original_clock':i,'candidate_clock':reverse[i],'dest':r,'source':s,'dest_beta_before':str(beta[r]),'source_beta_before':str(beta[s]) if s is not None else None,'virtual_deleted':i in deleted_owned});seen_int.add(i)
        if op in ('INIT','CLEAR'):beta[r]=F(0)
        elif op=='MOVE':pass
        elif op=='SCALE':beta[r]*=F(e[2])
        elif op=='ADD':beta[r]+=F(e[3])*beta[e[2]]
        elif op=='COPY':beta[r]=F(e[3])*beta[e[2]]
        else:raise ValueError('unknown opcode')
        if i in INJECTIONS:
            require(beta[902]==0,'feedback at deleted source '+str(i))
            target,q=INJECTIONS[i];require(target==r,'injection destination');beta[r]+=q
        if i in oldint and i not in deleted_owned:
            compare_row(newint[i]['dest_after'],oldint[i]['dest_after'],beta[r],c,'interface after '+str(i))
            interface_receipt[-1]['dest_beta_after']=str(beta[r])
        if beta[r]!=bbefore:transitions.append({'original_clock':i,'destination':r,'op':op,'before':str(bbefore),'after':str(beta[r])})
        if i in (41461,41465):
            feedback.append({'original_clock':i,'event':e,'source_beta_before':str(source_before),
                             'destination_beta_before':str(bbefore),'destination_beta_after':str(beta[r])})
        if i in INJECTIONS:trace.append({'original_clock':i,'destination':r,'source_beta':'0','injection':str(INJECTIONS[i][1]),'before':str(bbefore),'after':str(beta[r])})
    require(seen_clear==set(oldclear) and seen_int==set(oldint) and seen_copy==set(oldcopy),'unvisited observations')
    require([x['original_clock'] for x in feedback]==[41461,41465] and 41465 in seen_int,'missing feedback or owned read')
    require(len(old['endpoint_rows'])==len(new['endpoint_rows'])==N,'endpoint count')
    for r in range(N):compare_row(new['endpoint_rows'][r],old['endpoint_rows'][r],beta[r],c,'endpoint '+str(r))
    require(all(not beta[r] for r in range(NP)),'nonzero public endpoint beta')
    return {'schema':'rankone7620/v1','status':'RANKONE_ONLY_UNQUALIFIED','source_word_canonical_sha256':SOURCE,
        'source_word_gzip_sha256':wsha,'candidate_word_canonical_sha256':digest(canonical(cand)),'candidate_word_gzip_sha256':csha,
        'exact_gzip_sha256':esha,'exact_sha256':digest(exact_raw),'exact_status_sha256':digest(exact_status_raw),
        'source_covector':pack(c),'source_cut':CUT,'source_nonzero':True,
        'injections':trace,'beta_transitions':transitions,'later_feedback':feedback,
        'endpoint_beta':{str(i):str(v) for i,v in enumerate(beta) if v},
        'clear_beta':clear_receipt,'interface_beta':interface_receipt,'copy_guard_beta':copy_receipt,
        'scope':'normalized rational differential under common whole-private reset U; no physical or price qualification'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--built',required=True);p.add_argument('--exact',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    try:
        x=certificate(a.root,a.built,a.exact)
        (out/'RANKONE.json').write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
        status={'status':x['status']}
        code=0
    except Exception as e:
        status={'status':'INCOMPLETE','error_type':type(e).__name__,'error':str(e)}
        code=1
    (out/'status.json').write_text(json.dumps(status,sort_keys=True,indent=2)+'\n')
    print(json.dumps(status,sort_keys=True),flush=True)
    return code

if __name__=='__main__':raise SystemExit(main())
