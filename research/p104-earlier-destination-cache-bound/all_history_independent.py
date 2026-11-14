#!/usr/bin/env python3
"""Fresh Q coframe matrices; distinct-prime sparse COLUMN independence.

Only the pinned original word is an input. Root prototype rows are not used.
"""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,math,sys,time
PIN='acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
PRIME=1000033
def need(ok,label):
    if not ok:raise ValueError(label)
def isprime(n):return n>=2 and all(n%d for d in range(2,math.isqrt(n)+1))
def framekey(U):
    s={0}
    for u in U:need(u not in s and 0<u<512,'independent source frame basis');s|={v^u for v in s}
    return tuple(sorted(s))
def add(a,b,q):
    need(a is not b,'separate scalar operands')
    for j,v in b.items():
        z=a.get(j,Q(0))+q*v
        if z:a[j]=z
        else:a.pop(j,None)
def rational_mod(q,prime,inverses):
    if q.denominator not in inverses:
        need(q.denominator%prime!=0,'rational denominator invertible at certificate prime');inverses[q.denominator]=pow(q.denominator%prime,prime-2,prime)
    return (q.numerator%prime)*inverses[q.denominator]%prime

def projected_zero_unit(row,cold,seen):
    if any(h not in cold for h in row):return None
    need(len(row)==1,'maximally zero observation is a single neutral-coordinate unit')
    h=next(iter(row));need(h not in seen,'zero unit rows have distinct neutral coordinates within coframe');seen[h]=True;return h

def column_rank_certificate(columns,expected_rows,prime=PRIME):
    """Columns are sparse vectors indexed by ORIGINAL observation row IDs."""
    basis={};pivots=[];updates=0
    for column,original in sorted(columns.items(),key=lambda item:(len(item[1]),item[0])):
        value=original.copy()
        while value:
            pivot=min(value)
            if pivot not in basis:
                a=value[pivot];inv=pow(a,prime-2,prime);basis[pivot]={r:v*inv%prime for r,v in value.items()};pivots.append({'input_column':column,'pivot_row':pivot,'pivot_value':a});break
            old=basis[pivot];q=value[pivot]
            for r,v in old.items():
                z=(value.get(r,0)-q*v)%prime
                if z:value[r]=z
                else:value.pop(r,None)
            updates+=1
        if len(basis)==expected_rows:break
    return {'rank':len(basis),'expected_rows':expected_rows,'full_row_rank':len(basis)==expected_rows,'pivots':pivots,'column_reductions':updates}
def verify(source, *, prime=PRIME, progress=None, max_seconds=1800):
    """Read only the source; return a receipt. No output files are written."""
    def emit(value):
        if progress is not None:progress(value)
    start=time.monotonic();need(isprime(prime),'distinct modulus is prime by exhaustive trial division');raw=Path(source).read_bytes();need(sha256(raw).hexdigest()==PIN,'exact source byte pin');w=json.loads(gzip.decompress(raw));classes=list(map(framekey,w['frames']));aliases=defaultdict(list)
    for i,k in enumerate(classes):aliases[k].append(i)
    n,owned=w['public'],w['owned_fields'];mains=set(w['live'])|{h+112 for h in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2']);helpers=set(range(n))-mains;need(len(mains)==400 and len(helpers)==1101,'actual main/helper partition')
    target_rank={h:abs(len(w['frames'][w['initial'][h]])-len(w['frames'][w['final'][h]])) for h in helpers};rows=[{h:Q(1)} for h in range(n)]+[None]*owned;cur=w['initial'].copy()+[None]*owned;banks=defaultdict(list);pure=defaultdict(list);paid=Counter();counts=Counter();move_rows={}
    def observe(event,a,f,kind):banks[classes[f]].append({'event':event,'owner':a,'frame':f,'kind':kind,'row':rows[a].copy()})
    for a,f in enumerate(w['initial']):observe(-1,a,f,'entrance')
    for event,e in enumerate(w['program']):
        if event%256==0:need(time.monotonic()-start<max_seconds,'30min bounded exact replay/certificate')
        op,a=e[:2];counts[op]+=1
        if op=='MOVE':
            need(cur[a]==e[2] and rows[a] is not None,'literal live MOVE source');need(e[4]==(a>=n),'source ownership flag')
            left,right=set(classes[e[2]]),set(classes[e[3]]);need((left<right) if a<n else (left<right or right<left),'retained strict nesting grammar')
            r=abs(len(w['frames'][e[2]])-len(w['frames'][e[3]]));need(r>0 and rows[a],'positive paid rank and nonzero unrestricted MOVE row');paid[r]+=1;move_rows[event]=(rows[a].copy(),r,a,e[2],e[3])
            if len(rows[a])==1:
                h=next(iter(rows[a]))
                if h in helpers:pure[h].append((event,r,rows[a][h]))
            cur[a]=e[3];observe(event,a,e[3],'arrival')
        elif op=='INIT':need(a>=n and cur[a] is None and rows[a] is None,'fresh owned INIT');cur[a],rows[a]=e[2],{}
        elif op=='CLEAR':need(a>=n and cur[a]==e[2] and rows[a] is not None,'owned CLEAR chart');cur[a],rows[a]=None,None
        elif op=='SCALE':need(cur[a]==e[-1] and Q(e[2]),'nonzero coframed SCALE');rows[a]={h:Q(e[2])*v for h,v in rows[a].items()}
        elif op in ('ADD','COPY'):
            b=e[2];need(a!=b and cur[a]==cur[b]==e[-1],'coframed scalar contact')
            if op=='COPY':need(a>=n and not rows[a],'COPY into fresh zero')
            add(rows[a],rows[b],Q(e[3]))
        else:raise ValueError(op)
    need(cur==w['final']+[None]*owned,'complete source endpoints and lifetimes');need(len(move_rows)==6279,'all paid MOVE rows collected');need(sum(len(b) for b in banks.values())==7780,'all1501 initial plus6279 arrivals')
    cold={h for h in helpers if Counter(r for event,r,c in pure[h])==Counter({target_rank[h]:1})};need(len(cold)==72,'fresh exact72 pointwise-neutral helpers')
    neutral_moves={pure[h][0][0]:h for h in cold};need(len(neutral_moves)==72,'one distinct pure MOVE per neutral helper');lost=Counter(target_rank[h] for h in cold);removed=Counter(move_rows[e][1] for e in neutral_moves);need(lost==removed,'actual72 target/paid rank cancellation')
    replay_seconds=time.monotonic()-start;emit({'phase':'fresh_exact_Q_matrices_complete','rows':7780,'coframes':len(banks),'neutral_helpers':72,'seconds':replay_seconds})
    inverses={};rational_entries=0;records=[];zero_rows=[];denominator_count=Counter();source_matrix_digest=sha256();projected_matrix_digest=sha256();original_pivots=projected_pivots=0
    def residue(q):
        denominator_count[q.denominator]+=1
        return rational_mod(q,prime,inverses)
    for index,(key,bank) in enumerate(sorted(banks.items(),key=lambda item:(-len(item[1]),aliases[item[0]][0]))):
        need(time.monotonic()-start<max_seconds,'30min bounded matrix certificates');columns=defaultdict(dict);keep=[];zero_units={};row_labels=[];local_zeros=[];fullhash=sha256();projhash=sha256()
        for i,o in enumerate(bank):
            row=o['row'];label={k:v for k,v in o.items() if k!='row'};row_labels.append(label);encoded=[label,[[j,str(v.numerator),str(v.denominator)] for j,v in sorted(row.items())]];fullhash.update((json.dumps(encoded,separators=(',',':'))+'\n').encode());projection={j:v for j,v in row.items() if j not in cold}
            if not projection:
                h=projected_zero_unit(row,cold,zero_units);need(h is not None,'projected zero observation classified');z={**label,'helper':h,'coefficient':str(row[h]),'coframe_representative':aliases[key][0]};local_zeros.append(z);zero_rows.append(z)
            else:
                keep.append(i);projhash.update((json.dumps([label,[[j,str(v.numerator),str(v.denominator)] for j,v in sorted(projection.items())]],separators=(',',':'))+'\n').encode())
            for j,q in row.items():
                v=residue(q);rational_entries+=1
                if v:columns[j][i]=v
        original=column_rank_certificate(columns,len(bank),prime);need(original['full_row_rank'],'unrestricted final coframe matrix row independence')
        kept=set(keep);projected_columns={j:{i:v for i,v in col.items() if i in kept} for j,col in columns.items() if j not in cold};projected_columns={j:col for j,col in projected_columns.items() if col};projected=column_rank_certificate(projected_columns,len(keep),prime);need(projected['full_row_rank'],'maximal-neutral projected final coframe matrix row independence')
        original_pivots+=original['rank'];projected_pivots+=projected['rank'];fullid=fullhash.hexdigest();projid=projhash.hexdigest();source_matrix_digest.update((str(aliases[key][0])+':'+fullid+'\n').encode());projected_matrix_digest.update((str(aliases[key][0])+':'+projid+'\n').encode())
        records.append({'frame_ids':aliases[key],'span':list(key),'row_count':len(bank),'projected_nonzero_row_count':len(keep),'exact_matrix_sha256':fullid,'exact_projected_matrix_sha256':projid,'row_labels':row_labels,'zero_rows':local_zeros,'unrestricted_column_certificate':original,'projected_column_certificate':projected})
        if index<2 or(index+1)%200==0:emit({'phase':'column_certificates','completed_coframes':index+1,'total_coframes':len(banks),'last_frame':aliases[key][0],'last_rows':len(bank),'seconds':time.monotonic()-start})
    zero_initial=[z for z in zero_rows if z['kind']=='entrance'];zero_arrival=[z for z in zero_rows if z['kind']=='arrival'];need(len(zero_initial)==len(zero_arrival)==72,'exact72 initial plus72 paid-arrival zero observations');need({z['event'] for z in zero_arrival}==set(neutral_moves),'maximal neutral zero MOVE list is exactly singleton pure list')
    need(all(z['helper']==neutral_moves[z['event']] for z in zero_arrival),'fresh zero MOVE coordinate identity');need(original_pivots==7780 and projected_pivots==7636,'complete row rank totals')
    out={'status':'EXACT_Q_ALL_COFRAME_HISTORY_INNOVATIONS_CERTIFIED_BY_DISTINCT_PRIME_COLUMNS','source_sha256':PIN,'source_payload_sha256':sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'prime':prime,'prime_verified_by_exhaustive_trial_division':True,'primary_input_only':str(Path(source).resolve()),'source_prototype_inputs_used':False,'instructions':len(w['program']),'main_inputs':len(mains),'helpers':len(helpers),'initial_observations':1501,'MOVE_arrivals':6279,'coframes_with_observations':len(banks),'original_total_row_rank':original_pivots,'max_neutral_nonzero_row_rank':projected_pivots,'zero_initial_rows':72,'zero_MOVE_rows':72,'nonzero_projected_MOVEs':6207,'neutral_helpers':sorted(cold),'zero_MOVE_events':sorted(neutral_moves),'neutral_target_histogram':dict(sorted(lost.items())),'neutral_paid_histogram':dict(sorted(removed.items())),'zero_rows_distinct_units_within_each_coframe':True,'all_2_pow72_subsets_follow_from_unit_extension_lemma':True,'rational_entries_checked':rational_entries,'distinct_rational_denominators':len(inverses),'all_denominators_invertible':True,'exact_source_matrix_collection_sha256':source_matrix_digest.hexdigest(),'exact_projected_matrix_collection_sha256':projected_matrix_digest.hexdigest(),'event_counts':dict(counts),'replay_seconds':replay_seconds,'seconds':time.monotonic()-start,'records':records,'scope':'Whole original MOVE targets and strictly earlier same-coframe histories under arbitrary retained field inputs. Any neutral-helper subset zero. No new source/frames/providers, finite-grid nonlinear decoder claim, physical supplier or kappa.'}
    return out

def controls():
    """Pure read-only controls: no source input, output files or prints."""
    from random import Random
    p=PRIME;tests=[]
    def rowrank(matrix,modulus=None):
        a=[[Q(x) if modulus is None else x%modulus for x in row] for row in matrix];r=0
        for j in range(len(a[0]) if a else 0):
            k=next((i for i in range(r,len(a)) if a[i][j]),None)
            if k is None:continue
            a[r],a[k]=a[k],a[r];v=a[r][j];iv=1/v if modulus is None else pow(v,modulus-2,modulus);a[r]=[x*iv if modulus is None else x*iv%modulus for x in a[r]]
            for i in range(r+1,len(a)):
                v=a[i][j]
                if v:a[i]=[x-v*y if modulus is None else (x-v*y)%modulus for x,y in zip(a[i],a[r])]
            r+=1
            if r==len(a):break
        return r
    def cols(matrix):return {j:{i:row[j]%p for i,row in enumerate(matrix) if row[j]%p} for j in range(len(matrix[0]) if matrix else 0)}
    need(isprime(p) and not isprime(3*p),'prime/composite control');tests.append({'control':'composite_modulus','rejected':True})
    try:rational_mod(Q(1,p),p,{})
    except ValueError as error:tests.append({'control':'noninvertible_rational_denominator','rejected':True,'reason':str(error)})
    else:raise ValueError('invalid denominator accepted')
    rng=Random(72543);cases=0
    for r in range(1,7):
        for n in range(1,8):
            for _ in range(3):
                matrix=[[rng.randrange(-4,5) for j in range(n)] for i in range(r)];need(column_rank_certificate(cols(matrix),r,p)['rank']==rowrank(matrix,p),'dense-row/column rank crosscheck');cases+=1
    matrix=[[1,2,3],[0,1,4],[1,2,3]];cert=column_rank_certificate(cols(matrix),3,p);need(not cert['full_row_rank'] and cert['rank']==2,'duplicate row control');tests.append({'control':'duplicate_row','rejected':True})
    history=[[1,0],[1,p]];target=[0,1];need(rowrank(history)==rowrank(history+[target])==2,'rational target belongs to history');need(rowrank(history,p)==1 and rowrank(history+[target],p)==2,'naive modular miss reproduced');need(not column_rank_certificate(cols(history+[target]),3,p)['full_row_rank'],'modular miss alone rejected');tests.append({'control':'modular_miss_without_full_history_rank','rejected':True})
    need(column_rank_certificate(cols([[1,1],[1,0]]),2,p)['full_row_rank'],'independent unrestricted pitfall');need(column_rank_certificate({},0,p)['full_row_rank'],'vacuous maximal-zero pitfall');need(not column_rank_certificate(cols([[1],[1]]),2,p)['full_row_rank'],'proper subset enables nonzero target')
    try:projected_zero_unit({0:Q(1),1:Q(1)},{0,1},{})
    except ValueError as error:tests.append({'control':'maximal_zero_nonsingleton_x_plus_y_history_target_x','rejected':True,'reason':str(error)})
    else:raise ValueError('maximal-zero nonsingleton accepted')
    seen={};projected_zero_unit({0:Q(1)},{0},seen)
    try:projected_zero_unit({0:Q(2)},{0},seen)
    except ValueError as error:tests.append({'control':'repeated_maxzero_coordinate_within_coframe','rejected':True,'reason':str(error)})
    else:raise ValueError('repeated zero coordinate accepted')
    need(not column_rank_certificate({0:{0:1}},2,p)['full_row_rank'],'retained projected zero row rejected');tests.append({'control':'forgot_to_delete_exact_projected_zero_row','rejected':True})
    return {'status':'PASS_READ_ONLY_INDEPENDENT_ALL_HISTORY_CONTROLS','prime':p,'independent_small_matrix_row_column_crosschecks':cases,'failure_controls':tests,'all_failure_controls_rejected':True,'read_only_no_source_replay':True}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('--out',type=Path);args=parser.parse_args()
    result=verify(args.source,progress=lambda value:print(json.dumps(value),file=sys.stderr,flush=True))
    if args.out is not None:args.out.write_text(json.dumps(result,indent=2)+'\n')
    else:print(json.dumps(result,indent=2))
if __name__=='__main__':main()
