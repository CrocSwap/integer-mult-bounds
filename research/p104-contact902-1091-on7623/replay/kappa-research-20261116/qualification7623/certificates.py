#!/usr/bin/env python3
"""Source/candidate 180-CLEAR preparation under common U; root executes."""
import argparse, collections, gzip, hashlib, json
from fractions import Fraction as F
from pathlib import Path
SOURCE_GZ='97391721ab7d30f8dd84c8d3c29a3c3ed2df2d65ca55e7ff8329bd09877681d2'
SOURCE_CAN='48e1845e6b24832731705a3ff096b22d2b807428f7d625d06b45adfe3b5a738c'
OLD_GZ='2eb2cf1d29529c68a6cb1c0639de3065a805858d3492068e76b70c5a5e80a81c'
OLD_CERTS='f10f8081d9ebb34e2487ad70ccdcd83aa4cd43fd8e80092af04643ce2445d24d'
EDIT21='9ed885170928fda98709116edc8c09b2482943191e9525627427b4c5391bae3c'
EDIT23='45c7389f95749df04383acc8f0400622406b7293473728dc0a8e339fdfdac011'
NEW_CERTS='bf1df6eff70db4ffe001a61156db5052048d8fc1b300b05612ac84e474c74765'
BASE21='ff8cc4ac45dc89c6dfca54d1954b21edefe599c14d31b2ead7ceeafe3bed1ec8'
MAX_VECTORS=86;MAX_ELIMINATION_OPS=20_000_000;MAX_STORED_TERMS=2_000_000
class Refusal(Exception): pass

def need(test,msg):
    if not test:raise Refusal(msg)
def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def load(path):
    data=Path(path).read_bytes();return json.loads(gzip.decompress(data) if data[:2]==b'\x1f\x8b' else data)
def unpack(row):return {int(k):F(v) for k,v in (row or {}).items() if F(v)}
def pack(row):return {str(k):str(v) for k,v in sorted(row.items()) if v}
def axpy(dst,src,q):
    for k,v in src.items():
        z=dst.get(k,F(0))+q*v
        if z:dst[k]=z
        else:dst.pop(k,None)
def linear(rows,coeff):
    out={}
    for r,q in coeff.items():axpy(out,rows[r],q)
    return out


def one_canonical_relation(target,rows,old_roles,live,n):
    """One exact echelon solve over old public certificate roles plus four fixed public roles.

    This is a fixed finite basis, not a changing bank or coefficient search.
    Free coefficients are zero, pivots use first contributor in sorted order.
    """
    roles=sorted(set(old_roles)|({451,1495,902,985}&live))
    need(len(roles)<=MAX_VECTORS and all(r<n and r in live for r in roles),'relation basis shape')
    basis={};ops=0;stored=0
    for role in roles:
        v=rows[role].copy();rep={role:F(1)}
        while v:
            p=min(v)
            if p not in basis:
                q=v[p];v={k:x/q for k,x in v.items()};rep={k:x/q for k,x in rep.items()}
                stored+=len(v)+len(rep);need(stored<=MAX_STORED_TERMS,'canonical relation storage bound')
                basis[p]=(v,rep);break
            row,weights=basis[p];q=-v[p];ops+=len(row)+len(weights);need(ops<=MAX_ELIMINATION_OPS,'canonical relation operation bound')
            axpy(v,row,q);axpy(rep,weights,q)
    residual=target.copy();answer={}
    while residual:
        p=min(residual)
        if p not in basis:raise Refusal('target not in canonical basis')
        row,weights=basis[p];q=residual[p];ops+=len(row)+len(weights);need(ops<=MAX_ELIMINATION_OPS,'canonical relation operation bound')
        axpy(residual,row,-q);axpy(answer,weights,q)
    need(linear(rows,answer)==target,'canonical relation internal mismatch')
    return answer,{'basis_candidates':len(roles),'pivots':len(basis),'elimination_ops':ops,'stored_terms':stored}


def apply_ancestral(program,origins,edit):
    need(len(program)==edit['base_events'] and len(origins)==len(program),'ancestry base shape')
    dels={}
    for i,e in edit['delete']:
        need(type(i) is int and 0<=i<len(program) and i not in dels and program[i]==e,'ancestry delete mismatch');dels[i]=e
    adds=collections.defaultdict(list)
    for i,events in edit['insert_before']:
        need(type(i) is int and 0<=i<=len(program),'ancestry insertion index');adds[i].extend(events)
    result=[];org=[]
    for i,e in enumerate(program):
        for a in adds[i]:result.append(a);org.append(None)
        if i not in dels:result.append(e);org.append(origins[i])
    for a in adds[len(program)]:result.append(a);org.append(None)
    for a in edit['append']:result.append(a);org.append(None)
    return result,org


def build(root,gate,out):
    root,gate,out=Path(root),Path(gate),Path(out);out.mkdir(parents=True,exist_ok=False);audit={};outputs={}
    try:
        oldroot=root.parent/'kappa-research-20261115b'; oldwordp=oldroot/'inputs/pr7620/data/word.json.gz';oldcertp=oldroot/'inputs/pr7620/evidence/certs.json'
        p21=root/'inputs/pr7621/research/p104-courier-restop-on7620/data';p23=root/'inputs/pr7623/research/p104-loan-snapshot-engine-on7621/data'
        for p,h in [(oldwordp,OLD_GZ),(oldcertp,OLD_CERTS),(p21/'edits.json',EDIT21),(p23/'edits.json',EDIT23),(p23/'clear-certificates.json',NEW_CERTS),(p23/'base-7621-word.json.gz',BASE21),(p23/'word.json.gz',SOURCE_GZ)]:need(sha(p.read_bytes())==h,'input custody: '+str(p))
        oldword=load(oldwordp);oldcert=load(oldcertp);source=load(p23/'word.json.gz');source_hash=sha(canonical(source))
        need(source_hash==SOURCE_CAN and oldcert['summary']['sha256']==OLD_GZ and len(oldcert['clears'])==167,'source/old certificate binding')
        w21,orig21=apply_ancestral(oldword['program'],list(range(len(oldword['program']))),load(p21/'edits.json'))
        base21=load(p23/'base-7621-word.json.gz');need(w21==base21['program'] and {k:v for k,v in oldword.items() if k!='program'}=={k:v for k,v in base21.items() if k!='program'},'7621 reconstruction')
        w23,ancestry=apply_ancestral(w21,orig21,load(p23/'edits.json'))
        need(w23==source['program'] and {k:v for k,v in base21.items() if k!='program'}=={k:v for k,v in source.items() if k!='program'},'7623 reconstruction')
        oldreverse={v:i for i,v in enumerate(ancestry) if v is not None};need(len(oldreverse)==sum(v is not None for v in ancestry),'duplicate ancestral origin')
        for i,e in enumerate(oldword['program']):
            if e[0] in ('INIT','CLEAR') or (e[0]=='MOVE' and e[1]>=1501):need(i in oldreverse and source['program'][oldreverse[i]]==e,'old owned lifetime stream not preserved')
        newcert=load(p23/'clear-certificates.json')['clear_event_index'];need(len(newcert)==13 and all(str(int(k))==k for k in newcert),'new cert inventory')
        result=load(gate/'RESULT.json');need(result['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U' and result['qualified_kappa'] is False,'first gate not complete')
        for name,digest in result['receipt_hashes'].items():need(sha((gate/name).read_bytes())==digest,'first gate receipt mismatch: '+name)
        for name in ('built/candidate-word.json.gz','built/edit-manifest.json','built/status.json','exact/EXACT.json.gz','exact/status.json','rankone/RANKONE.json','rankone/status.json','physical/PHYSICAL.json','physical/status.json','price/PRICE.json'):
            need(name in result['receipt_hashes'],'missing gate receipt: '+name)
        man=load(gate/'built/edit-manifest.json');candidate=load(gate/'built/candidate-word.json.gz');es=load(gate/'exact/status.json');ex=load(gate/'exact/EXACT.json.gz')
        candidate_gz=sha((gate/'built/candidate-word.json.gz').read_bytes());candidate_can=sha(canonical(candidate));ex_gz=sha((gate/'exact/EXACT.json.gz').read_bytes())
        need(man['schema']=='compose7623-edit-manifest/v1' and man['source_gzip_sha256']==SOURCE_GZ and man['source_canonical_sha256']==SOURCE_CAN and man['candidate_gzip_sha256']==candidate_gz and man['candidate_canonical_sha256']==candidate_can,'manifest binding')
        need(es['status']=='U_CONDITIONAL_LITERAL_EXACT_ONLY' and es['exact_gzip_sha256']==ex_gz and es['exact_sha256']==sha(canonical(ex)) and ex['schema']=='compose7623-exact/v1' and es['source']==ex['source'],'exact status binding')
        need(ex['source']['original_gzip_sha256']==SOURCE_GZ and ex['source']['original_canonical_sha256']==SOURCE_CAN and ex['source']['candidate_gzip_sha256']==candidate_gz and ex['source']['candidate_canonical_sha256']==candidate_can and ex['source']['manifest_sha256']==sha((gate/'built/edit-manifest.json').read_bytes()),'exact source binding')
        origin=man['candidate_origins'];reverse=man['original_to_candidate'];need(len(source['program'])==77277 and len(candidate['program'])==len(origin)==77271 and len(reverse)==77277 and all(reverse[i]==j for j,i in enumerate(origin)),'gate origins')
        need(len(ex['original']['clears'])==len(ex['candidate']['clears'])==180,'exact clear count')
        old_by_clock={c['event']:c for c in oldcert['clears']};need(len(old_by_clock)==167,'old clear duplicates')
        for side,word,wordorig,expected,whash in [('source',source,list(range(77277)),ex['original']['clears'],SOURCE_GZ),('candidate',candidate,origin,ex['candidate']['clears'],candidate_gz)]:
            n=word['public'];N=n+word['owned_fields'];need((n,N)==(1501,1569),'word dimensions')
            rows=[{i:F(1)} for i in range(n)]+[{} for _ in range(N-n)];live=set(range(n));chart=list(word['initial'])+[None]*(N-n)
            current={};count=collections.Counter();certificates=[];records=[];seen_old=set();seen_new=set()
            for j,e in enumerate(word['program']):
                op,r=e[:2];sc=wordorig[j];need(type(r) is int and 0<=r<N,'role out of range')
                if op=='INIT':
                    need(r>=n and r not in live,'bad init');live.add(r);rows[r]={};chart[r]=e[2];count[r]+=1;current[r]={'init_event':j,'init_chart':e[2],'moves':[]}
                elif op=='MOVE':
                    need(r in live and chart[r]==e[2],'bad move');chart[r]=e[3]
                    if r>=n:current[r]['moves'].append([j,e[2],e[3]])
                elif op=='CLEAR':
                    k=len(certificates);need(k<180 and r>=n and r in live and chart[r]==e[2],'bad clear');old_origin=ancestry[sc];ob=expected[k]
                    need(ob['original_clock']==sc and ob['candidate_clock']==reverse[sc] and ob['owner']==r and ob['lifetime']==count[r] and ob['chart']==e[2] and unpack(ob['row'])==rows[r],'first gate observation mismatch')
                    if old_origin is not None:
                        need(old_origin in old_by_clock and str(sc) not in newcert,'old clear mapping');prior=old_by_clock[old_origin];need(prior['field']==r and prior['chart']==e[2],'inherited owner/chart')
                        init_source=oldreverse[prior['init_event']];init_side=init_source if side=='source' else reverse[init_source]
                        moves=[[oldreverse[m[0]] if side=='source' else reverse[oldreverse[m[0]]],m[1],m[2]] for m in prior['owned_moves']]
                        need(current[r]['init_event']==init_side and current[r]['init_chart']==prior['init_chart'] and current[r]['moves']==moves,'inherited init/move ancestry');seen_old.add(old_origin)
                        coeff=unpack(prior['certificate']);need(prior['certificate'] is not None,'missing old cert');lineage='inherited_7620'
                    else:
                        need(str(sc) in newcert,'missing new lifetime cert');coeff=unpack(newcert[str(sc)]);seen_new.add(sc);lineage='new_7623'
                    need(all(role<n and role in live and role!=r for role in coeff),'certificate support unavailable')
                    method='retained_exact';stats=None
                    if linear(rows,coeff)!=rows[r]:coeff,stats=one_canonical_relation(rows[r],rows,coeff,live,n);method='canonical_relation'
                    need(all(role in live and role!=r for role in coeff) and linear(rows,coeff)==rows[r],'certificate relation mismatch')
                    certificates.append({'clear_index':k,'event':j,'field':r,'chart':e[2],'dim':len(word['frames'][e[2]]),'init_event':current[r]['init_event'],'init_chart':current[r]['init_chart'],'owned_moves':current[r]['moves'],'erased_support':len(rows[r]),'erased':pack(rows[r]),'other_live':len(live)-1,'other_rank':None,'certificate':pack(coeff),'terms':len(coeff),'verified_exact':True})
                    records.append({'clear_index':k,'event':j,'source_clock':sc,'ancestral_7620_clock':old_origin,'field':r,'lifetime':count[r],'lineage':lineage,'method':method,'solve':stats})
                    live.remove(r);rows[r]={};chart[r]=None;del current[r]
                elif op=='SCALE':
                    need(r in live and chart[r]==e[3] and F(e[2])!=0,'bad scale');q=F(e[2]);rows[r]={k:q*v for k,v in rows[r].items() if q*v}
                elif op in ('ADD','COPY'):
                    s=e[2];q=F(e[3]);need(r in live and s in live and r!=s and q!=0 and chart[r]==chart[s]==e[4],'bad scalar')
                    if op=='COPY':need(not rows[r],'copy guard')
                    axpy(rows[r],rows[s],q)
                else:raise Refusal('unknown opcode')
            need(len(certificates)==180 and seen_old==set(old_by_clock) and seen_new=={int(i) for i in newcert} and not current and live==set(range(n)),'lifetime/source inventory')
            dirty=sum(bool(c['erased']) for c in certificates)
            summary={'word':side,'sha256':whash,'clears':180,'dirty':dirty,'zero_rows':180-dirty,'certified':180,'n_public':n,'min_other_rank':None,'final_public_rank':None,'rank_status':'not recomputed','status':'local_relations_only_standalone_verifier_pending','scope':'public-column identities under common U, no physical erasure or U admission'}
            outputs[side]={'summary':summary,'clears':certificates};audit[side]=records
        # Publish neither certificate until both replays and all relations pass.
        for side,name in [('source','source-certificate.json'),('candidate','certificate.json')]:
            (out/name).write_text(json.dumps(outputs[side],sort_keys=True,indent=2)+'\n')
        report={'status':'PREPARED_RELATIONS_UNVERIFIED_EXTERNALLY','source_gzip_sha256':SOURCE_GZ,'candidate_gzip_sha256':candidate_gz,'gate_result_sha256':sha((gate/'RESULT.json').read_bytes()),'exact_gzip_sha256':ex_gz,'audit':audit,'limitations':'Standalone source and candidate verifications and two controls each pending. Rank metadata unmeasured; U unimplemented.'}
    except Exception as e:
        for name in ('source-certificate.json','certificate.json'):(out/name).unlink(missing_ok=True)
        report={'status':'REFUSED_NO_CERTIFICATES','error_type':type(e).__name__,'reason':str(e),'completed_audit':audit,'limitations':'No partial certificate, physical or U admission.'}
    (out/'status.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--gate',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
    return 0 if build(a.root,a.gate,a.out)['status']=='PREPARED_RELATIONS_UNVERIFIED_EXTERNALLY' else 1
if __name__=='__main__':raise SystemExit(main())
