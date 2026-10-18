"""Recompute exact determinants for every physically consumed source527 basis.
Based on PR234's prime coverage check; substantial OpenAI Codex assistance.
"""
from collections import Counter
from pathlib import Path
import hashlib,importlib.util,json,time
HERE=Path(__file__).resolve().parent

def basis_hash(basis):return hashlib.sha256(json.dumps(basis,separators=(',',':')).encode()).hexdigest()

def validate_record(row,dimension,determinant,allowed_primes):
    assert type(row['dimension'])is int and type(row['determinant'])is int and type(row['residual'])is int,'exact integer witness fields'
    assert row['dimension']==dimension and row['determinant']==determinant!=0,'exact determinant mismatch or singular basis'
    assert 0<row['residual']<2**80,'retained prime lower bound'
    product=row['residual']
    for prime,exponent in row['factors'].items():
        p=int(prime);assert p in allowed_primes and type(exponent)is int and exponent>0,'factor shape';product*=p**exponent
    assert product==abs(determinant),'factor identity'

def run(context,physical,progress=lambda text:None):
    started=time.monotonic();w,c=context['W'],context['C']
    p=HERE/'prime_witnesses.py';spec=importlib.util.spec_from_file_location('source527_exact_prime_validator',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    required=set(w.opframe)|set(w.w['source_frame'])|set(w.w['root_frame'])|{w.w['full_frame'],w.register([])}
    required.update(g['frame']for g in w.gauge.values())
    for e in w.k['entries']:required.update((e['mix_frame'],e['deliver_frame']))
    for t in range(w.v):required.add(w.register(w.module.kernel([c.cov[t]],w.h)[0]))
    required.update(g['frame']for g in context['agg']+context['rankgroups']+context['echelon'])
    required.update(r['mix_frame']for r in context['pair_selection'])
    used=set();groups={}
    for row in physical['used_frames']:
        f=row['frame_id'];assert f not in used;used.add(f)
        h=basis_hash(c.B[f]);assert h==row['basis_sha256'] and len(c.B[f])==c.dimf[f]==row['dimension'],'fresh physical basis identity'
        groups.setdefault(h,f)
    assert {basis_hash(c.B[f])for f in required}<=set(groups),'base and added transform coverage'
    determinants={};largest=0;prime_factors=set();witnesses={}
    for j,(h,f)in enumerate(sorted(groups.items())):
        B=c.B[f];s=list(map(sum,B))
        gram=[[9*sum(a*b for a,b in zip(x,y))-s[i]*s[k]for k,y in enumerate(B)]for i,x in enumerate(B)]
        det=module.det(gram);powers,residual=module.factor_witness(det)
        row=dict(dimension=len(B),determinant=det,residual=residual,factors={p:e for p,e in powers.items()if e})
        validate_record(row,len(B),det,module.PRIMES);prime_factors.update(map(int,row['factors']));witnesses[h]=row
        determinants[h]=det;largest=max(largest,abs(det).bit_length())
        if j and j%5000==0:progress('Validated '+str(j)+' exact basis determinants')
    ranks=Counter();bundle_bases=set()
    for role,g in w.gauge.items():
        if role in w.donor or role in context['borrow']:continue
        a=g['dim'];h=basis_hash(c.B[g['frame']]);d=determinants[h]
        assert 0<5*a<120 and d!=0;ranks[a]+=1;bundle_bases.add(h)
        assert abs(d**5)==abs(d)**5
    assert ranks=={12:18,13:48,18:13,20:2200}and len(bundle_bases)==231
    assert 2*120**3*10**16<2**80
    from copy import deepcopy
    controls=[]
    def reject(name,call):
        try:call()
        except AssertionError:controls.append(name)
        else:raise AssertionError('invalid witness accepted: '+name)
    first=next(iter(groups));row=witnesses[first];det=determinants[first]
    missing=dict(witnesses);missing.pop(first)
    def coverage(actual,wanted):assert set(actual)==set(wanted),'complete current basis coverage'
    reject('missing current basis',lambda:coverage(groups,missing))
    changed=deepcopy(row);changed['determinant']=det+1;reject('incorrect determinant',lambda:validate_record(changed,row['dimension'],det,module.PRIMES))
    changed_factor=deepcopy(row);changed_factor['residual']+=1;reject('incorrect factor identity',lambda:validate_record(changed_factor,row['dimension'],det,module.PRIMES))
    singular=deepcopy(row);singular['determinant']=0;reject('singular basis',lambda:validate_record(singular,row['dimension'],module.det([[1,2],[1,2]]),module.PRIMES))
    huge=deepcopy(row);huge['residual']=2**80;reject('residual at prime lower bound',lambda:validate_record(huge,row['dimension'],det,module.PRIMES))
    noninteger=deepcopy(row);noninteger['residual']=float(row['residual']);reject('noninteger residual',lambda:validate_record(noninteger,row['dimension'],det,module.PRIMES))
    return dict(status='PASS_FRESH_ALL_ACTUAL527_BASIS_DETERMINANTS_AND_FIVEFOLD_BUNDLES',unique_bases=len(groups),current_frame_ids=len(used),basis_inventory_sha256=hashlib.sha256(json.dumps(sorted(groups),separators=(',',':')).encode()).hexdigest(),maximum_determinant_bits=largest,prime_factors=sorted(prime_factors),all_remaining_factors_below_2_power_80=True,independent_entrances=sum(ranks.values()),bundled_unique_bases=len(bundle_bases),entrance_rank_counts=dict(ranks),controls=controls,physical_inventory_bound=True,seconds=time.monotonic()-started,scope='Every actual physical basis is freshly evaluated over exact integers; all527 source frames, target transformations and caps are covered. Five disjoint copies inherit nondegeneracy; compiler and prime supply remain theorem dependencies.')
