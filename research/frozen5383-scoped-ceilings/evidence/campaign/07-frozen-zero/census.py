#!/usr/bin/env python3
"""Frozen PR5383 paid-row census over Q[F_72]; no candidate code imports.

This grammar proves zeros under every invertible-generator representation.
Nonzero free words alone do not establish actual-native nonzero specialization.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import gzip, hashlib, json, resource, time

HERE=Path(__file__).resolve().parent
CAP=HERE.parent/'09-capsule-cold/capsule-v1'
WORD='snapshot/research/kappa-joint-relations-20261023/WORD.json.gz'
HEAD='4bd6efa51a495a7c7b7754915cf0244e7e60969e'
MANIFEST='ae6a1b933c386feabc9bab3300163df41e94bd3ddeeff973955695d33d5b11c8'

def need(p,s):
    if not p: raise ValueError(s)
def digest(b): return hashlib.sha256(b).hexdigest()
def encode(o): return json.dumps(o,sort_keys=True,separators=(',',':')).encode()
def merge(dst,k,q):
    q+=dst.get(k,0)
    if q: dst[k]=q
    else: dst.pop(k,None)
def row_data(row):
    return [[list(r),list(w),q.numerator,q.denominator] for (r,w),q in sorted(row.items())]
def row_record(index,e,role,row):
    data=row_data(row)
    groups=Counter(tuple(t[0]) for t in data)
    singleton=next((t for t in data if groups[tuple(t[0])]==1),None)
    return dict(event=index,literal=e,role=list(role),terms=len(data),row_sha256=digest(encode(data)),
                free_word_nonzero=bool(data),minimal_coefficient=data[0] if data else None,
                independent_monomial_certificate=singleton,row=data)

def run(word,trace=None,mutate=False):
    c=word['canonical']; pivots=sorted(int(p) for p in word['relation_basis'])
    owned={('C',i) for i in range(9)}|{('L',p) for p in pivots}
    roles={('L',i) for i in range(632)}|owned
    state={r:{(r,()):Q(1)} for r in roles}
    frames={('L',i):f for i,f in enumerate(c['start'])}
    frames.update({('C',i):None for i in range(9)})
    paid=Counter(); rows=[]; zeros=[]; peak=641; changed=False
    for index,event in enumerate(word['programs']['backward']):
        kind=event[0]
        if kind=='scalar':
            g,frame=event[1:]; dst=tuple(g[1])
            if g[0]=='clear':
                need(dst in owned,'clear only owned')
                state[dst]={};frames[dst]=frame
            else:
                need(frames[dst]==frame,'scalar output frame')
                if g[0]=='scale': state[dst]={k:q*Q(*g[2:]) for k,q in state[dst].items()}
                else:
                    src=tuple(g[2]);need(src!=dst and frames[src]==frame,'scalar source frame')
                    if g[0]=='copy':
                        need(dst in owned and not state[dst],'COPY into cleared owned')
                        state[dst]=dict(state[src])
                    else:
                        need(g[0]=='add','known ADD')
                        q=Q(*g[3:])
                        if mutate and not changed: q=-q;changed=True
                        for k,a in tuple(state[src].items()): merge(state[dst],k,q*a)
        elif kind=='warp':
            _,r,op,old,new=event;dst=tuple(r)
            need(frames[dst]==old,'warp input frame')
            out={}
            for (r,w),q in state[dst].items():
                nw=w[1:] if w and w[0]==-op else (op,)+w
                merge(out,(r,nw),q)
            state[dst]=out;frames[dst]=new
        elif kind in ('climb','center'):
            if kind=='climb': _,_,i,old,new,rank=event;dst=('L',i)
            else: _,i,old,new,rank=event;dst=('C',i)
            need(rank>0 and frames[dst]==old,'positive paid input frame')
            need(rank==abs(len(c['frames'][new])-len(c['frames'][old])),'literal rank')
            rec=row_record(index,event,dst,state[dst]);rows.append({k:v for k,v in rec.items() if k!='row'})
            witness=rec['independent_monomial_certificate']
            need(witness is not None,'each paid row has an uncancelled invertible monomial coefficient')
            need(tuple(witness[0]) in roles-owned,'witness belongs to a retained independent input')
            if trace: trace.write(encode(rec)+b'\n')
            paid[rank]+=1;frames[dst]=new
        elif kind=='zero_retag':
            _,r,old,new=event;dst=tuple(r)
            need(frames[dst]==old,'old zero frame')
            if state[dst]:
                return {'status':'REJECTED_NONZERO_EXISTING_ZERO_RETAG','event':index,
                        'literal':event,'minimal_coefficient':row_data(state[dst])[0]}
            zeros.append(dict(event=index,literal=event,terms=0,already_published=True))
            frames[dst]=new
        else: need(kind in ('phase','adapter'),'declared inherited marker')
        # The census is bounded by total live sparse terms, sampled every event.
        peak=max(peak,sum(map(len,state.values())))
    need(len(roles-owned)==624 and len(owned)==17,'624 independent plus 17 arbitrary owned')
    need(len(zeros)==8,'eight existing zeros not new savings')
    need(all(not state[r] for r in owned),'owned returns erased')
    for i in range(632):
        r=('L',i)
        need(frames[r]==c['final'][i],'retained final frame')
        if r in owned: continue
        want={(r,()):Q(1)}
        if i<112:want[(('L',i+112),())]=Q(-1)
        if state[r]!=want:
            residual=dict(state[r])
            for k,q in want.items():merge(residual,k,-q)
            return {'status':'REJECTED_RETAINED_ENDPOINT','role':list(r),
                    'minimal_residual_coefficient':row_data(residual)[0]}
    return dict(status='CENSUS_COMPLETE',orientation='backward',persistent_independent_columns=624,
        arbitrary_owned_columns=17,paid_histogram=dict(sorted(paid.items())),paid_rows=len(rows),
        zero_remaining_paid_rows=[r for r in rows if not r['free_word_nonzero']],
        existing_zero_retags=zeros,rows=rows,peak_live_free_terms=peak)

def main():
    start=time.monotonic(); raw_manifest=(CAP/'IMMUTABLE-MANIFEST.json').read_bytes()
    need(digest(raw_manifest)==MANIFEST,'frozen immutable manifest')
    manifest=json.loads(raw_manifest);need(manifest['candidate_head']==HEAD,'exact head')
    checked=[]
    for r in manifest['rows']:
        raw=(CAP/r['capsule_path']).read_bytes()
        need(digest(raw)==r['sha256'],'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob'],'source blob')
        checked.append({k:r[k] for k in ('capsule_path','sha256','git_blob','source_commit')})
    raw=(CAP/WORD).read_bytes(); payload=gzip.decompress(raw);word=json.loads(payload)
    tracepath=HERE/'PAID-ROWS-v2.jsonl.gz'
    with gzip.GzipFile(filename=str(tracepath),mode='wb',mtime=0) as trace: census=run(word,trace)
    mutant=run(word,mutate=True)
    need(mutant['status'] in ('REJECTED_NONZERO_EXISTING_ZERO_RETAG','REJECTED_RETAINED_ENDPOINT'),'preparation sign control rejects')
    invoice=HERE.parent/'02-census/INVOICE-v1.json'
    result=dict(schema='frozen5383-paid-zero-census/v2',candidate_head=HEAD,manifest_sha256=MANIFEST,
        word_sha256=digest(raw),word_payload_sha256=digest(payload),source_inputs=checked,
        census_engine_sha256=digest(Path(__file__).read_bytes()),
        independent_whole_invoice={'path':str(invoice.relative_to(HERE.parent)),
            'sha256':digest(invoice.read_bytes()),'paid':64148,'productive':10800,'rank_surplus':752,
            'scope':'Consumed independent worker02 receipt, not recomputed by this zero-row census'},
        overlap_clearance_sha256=digest((HERE.parent.parent/'price-plane-swarm-plan-20261024/ROOT-5125-CLEARANCE.json').read_bytes()),
        grammar={'coefficients':'exact rational','generators':'72 independent invertible symbols',
                 'relations':'adjacent signed-generator inverse cancellation only',
                 'field_rows':'linear combination of (entry role, reduced left operator word)',
                 'tensor':'termwise generator substitution; rational coefficients outside tensor powers'},
        scope='Frozen backward local word only; no new relation, preparation, pivot, helper, word-order or forward-transpose search',
        census=census,controls={'flipped_first_preparation_ADD':mutant},
        new_paid_deletions=0,whole_invoice_delta={'paid':0,'productive':0,'ordinary':0,'owned_slots':0},
        native_specialization_status='CLOSED_BY_INDEPENDENT_SINGLE_MONOMIAL_COEFFICIENT_IN_EVERY_PAID_ROW',
        nonzero_proof={
            'entry_coefficient':'For each row, the selected retained independent entry has exactly one reduced free word with rational coefficient q != 0; all other entries may be set to zero',
            'native_specialization':'Every source native generator is invertible. A reduced word evaluates to an invertible operator U at every positive tensor width; q*U is nonzero',
            'literal_counterexample':'At each row separately set the selected entry to U^{-1} e0 and every other independent and arbitrary owned entry to zero. The logical input row of the paid job is q e0 != 0',
            'physical_gauge':'The exact source frame/chart is invertible. The corresponding physical paid input is also nonzero, including its unchanged absolute phase',
            'tensor':'Evaluate words termwise with source tensor powers and keep q outside the tensor power; invertibility holds at every positive width',
            'certificate_rows':len(census['rows']),
            'selected_monomial_max_length':max(len(r['independent_monomial_certificate'][1]) for r in census['rows']),
            'does_not_establish':'No lower-rank obstruction, changed-preparation obstruction, global optimum, or algorithmic impossibility follows'},
        conclusion='All 3282 remaining literal positive backward paid inputs are nonzero on the frozen 624-independent-plus-17-owned boundary at every positive width; no additional identity-on-zero deletion exists in this exact frozen word',
        row_trace={'file':tracepath.name,'sha256':digest(tracepath.read_bytes()),'bytes':tracepath.stat().st_size},
        runtime_seconds=time.monotonic()-start,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (HERE/'RESULT-v2.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('candidate_head','new_paid_deletions','native_specialization_status','runtime_seconds','max_rss_kib')}))
    print(json.dumps({k:census[k] for k in ('paid_histogram','paid_rows','peak_live_free_terms','zero_remaining_paid_rows')}))

if __name__=='__main__':main()
