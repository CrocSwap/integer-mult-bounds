"""Original exact audit of the supplied weighted892 interior seam cost contract.
Reads only inert source and JSON data. Does not run any supplied checker.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
import reproduce_p10 as b
support=b.support
HERE=support.out('arithmetic','placeholder').parent
PARAM=support.OUTPUT/'matching'
BRIDGE=support.OUTPUT/'weighted'
CERT=support.OUTPUT/'certificates'
CLOSURE=support.HERE/'witnesses'

def sha(data):return hashlib.sha256(data).hexdigest()
def gram(x,y):return 9*sum(a*z for a,z in zip(x,y))-sum(x)*sum(y)
def echelon(rows):
    out={}
    for vector in rows:
        row=list(map(F,vector))
        for j,pivot in sorted(out.items()):
            q=row[j];row=[x-q*y for x,y in zip(row,pivot)]
        j=next((i for i,x in enumerate(row) if x),None)
        if j is not None:
            q=row[j];out[j]=[x/q for x in row]
    return out

def belongs(vector,frame):
    if 'a' in frame:return all(sum(x*y for x,y in zip(a,vector))==0 for a in frame['a'])
    row=list(map(F,vector))
    for j,pivot in sorted(echelon(frame['b']).items()):
        q=row[j];row=[x-q*y for x,y in zip(row,pivot)]
    return not any(row)

def run():
    proof=b.read('proof/FINITE_BIT_ACCOUNTING.md');cover=b.read('proof/three-stage-cover-bit.tex');finite=b.read('finite_check.py');bank=b.read('bank_check.py')
    assert 'Per good edge, pay at most 8m^2+8 elementary' in proof and 'Allocate 128N^3 ring operations per edge per low class' in proof
    assert 'For a split idempotent $P$' in cover and 'of split rank $r$ relative to $I$' in cover
    assert 'E*good+E*(128*N**3)' in finite and 'factors=maxops+(m-1)+m' in bank
    paths={'word':PARAM/'word_weighted892.json','base_seams':PARAM/'scalar_and_seams892.json','charts':CERT/'weighted892-seam-charts.json','path_census':PARAM/'full_path_census892.json'}
    raw={k:p.read_bytes() for k,p in paths.items()};data={k:json.loads(x) for k,x in raw.items()};charts=data['charts'];base=data['base_seams'];hashes={k:sha(x) for k,x in raw.items()}
    assert charts['candidate_word_sha256']==base['candidate_word_sha256']==hashes['word']
    assert charts['seam_receipt_sha256']==hashes['base_seams']
    assert charts['source_head']==base['source_head']==b.HEAD
    frames=b.read('bitword/selected/bit/frames_p10.json.gz')['frames'];programs={x['program_id']:x for x in charts['factor_programs']}
    assert len(programs)==57 and len(charts['role_uses'])==73
    largest=0;num=den=0;prime_support=set()
    for program in programs.values():
        columns=program['basis_columns'];matrix=[[F(x) for x in row] for row in zip(*columns)];inverse=[[F(x) for x in row] for row in program['inverse']]
        assert len(columns)==20 and all(len(x)==20 for x in columns)
        for left,right in ((matrix,inverse),(inverse,matrix)):
            for i,row in enumerate(left):
                for j,col in enumerate(zip(*right)):assert sum(x*y for x,y in zip(row,col))==int(i==j)
        replay=[row[:] for row in matrix];largest=max(largest,len(program['factors']));assert len(program['factors'])==program['count']
        for kind,i,j,q in program['factors']:
            q=F(q);num=max(num,abs(q.numerator));den=max(den,q.denominator)
            if kind=='swap':replay[i],replay[j]=replay[j],replay[i]
            elif kind=='scale':replay[i]=[q*x for x in replay[i]]
            elif kind=='add':replay[i]=[x+q*y for x,y in zip(replay[i],replay[j])]
            else:raise AssertionError('unknown factor')
        assert replay==[[F(int(i==j)) for j in range(20)] for i in range(20)]
        r=program['rank'];de=program['donor_dimension'];df=program['recipient_dimension'];assert 0<=de<=df<=20 and r==df-de
        E=frames[str(program['donor_end_frame'])];Fframe=frames[str(program['recipient_gauge_frame'])]
        assert E['dim']==de and Fframe['dim']==df
        residual=columns[:r];donor=columns[r:r+de];outside=columns[r+de:]
        assert len(outside)==20-df
        assert all(belongs(c,Fframe) for c in residual+donor)
        assert all(belongs(c,E) for c in donor)
        assert all(gram(c,e)==0 for c in residual for e in donor)
        assert all(gram(c,e)==0 for c in outside for e in residual+donor)
        value=abs(int(program['determinant']));assert value>0
        for prime in (2,3,11):
            while value%prime==0:value//=prime;prime_support.add(prime)
        assert value==1
    assert (largest,num,den)==(155,21,36)
    seams={(x['donor'],x['recipient']):x for x in base['seams']};ranks=Counter()
    for use in charts['role_uses']:
        seam=seams[use['donor'],use['recipient']];program=programs[use['program_id']]
        assert use['stream']==seam['physical_stream'] and use['read_order']==seam['read_order']
        assert program['donor_end_frame']==seam['donor_end_frame'] and program['recipient_gauge_frame']==seam['recipient_gauge_frame']
        assert use['rank']==program['rank'];ranks[use['rank']]+=1
    assert ranks[0]==30 and sum(n for r,n in ranks.items() if r)==43
    paid_seams=43*5*60;good=8*100**2+8;matrix=128*200**3
    report=dict(status='PASS_EXACT_WEIGHTED892_SEAM_GENERIC_COST_CONTRACT',source_head=b.HEAD,physical_admission=False,
        inputs={k:dict(path=str(paths[k]),sha256=hashes[k],bytes=len(raw[k])) for k in paths},programs_replayed=57,seam_uses=73,positive_rank_seams=43,zero_rank_seams=30,seam_rank_census=dict(sorted(ranks.items())),max_chart_factors=155,max_factor_numerator=21,max_factor_denominator=36,chart_determinant_prime_support=sorted(prime_support),
        exact_split_projector_argument='Invertible basis columns partition as (F intersect E-perp), E, and F-perp. Exact source-frame membership, pairwise G-orthogonality and both inverse products are verified. Thus the first-block projector is exactly P_F-P_E, split rank dim(F)-dim(E); for equal dimensions it is zero.',
        cost=dict(generic_wrappers_per_paid_child=good,ring_preparation_per_paid_child=matrix,positive_seam_occurrences_all_stages_replicas=paid_seams,seam_wrapper_allocation_already_within_E=paid_seams*good,seam_preparation_allocation_already_within_E=paid_seams*matrix,incremental_seam_surcharge=0,zero_rank_recursive_children=0),
        bank_normalizer_scope='The retained400 chart/599 normalizer bound applies to endpoint/residual bank selectors. It is not the reason interior seams are paid. New seam normalization is compiled through the generic split-idempotent child allowance.',
        zero_rank_scope='Rank-zero transitions emit no recursive MOVE child and no per-child generic wrapper. Their existing scalar operations, scheduling/descriptor preparation and any fixed table scans remain in unit-expanded scalar counts and the inherited primitive constant. No extra dense normalization pass is introduced.',
        no_double_counting='The43 positive seams already occur in the rebuilt paid-path histogram. Their5*60 occurrences are included in E, and the displayed seam allocations are subsets of E*good and E*128*N^3, not extra terms.',
        hypotheses=['Every changed positive seam is present in the measured full paid-path census.','The inherited generic weighted-child compiler and prefix-dependent unit adapter implementations satisfy the retained interfaces.','Complete weighted892/fixed19 chronology, scalar norms, endpoint charts and bank table are bound separately.','The inherited full primitive constant and all-size cutoff remain uninstantiated.'])
    for k,path in paths.items():assert sha(path.read_bytes())==hashes[k]
    return report
if __name__=='__main__':
    result=run();(HERE/'weighted892-seam-cost-contract.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('status','programs_replayed','seam_uses','positive_rank_seams','zero_rank_seams','cost')},indent=2))
