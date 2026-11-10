"""Independent coefficient-histogram and fee-credit arithmetic review.

This does not infer equal units or a complete-runtime lower bound.
Prepared for @CubeJerry with OpenAI assistance.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('package');p.add_argument('--output',required=True)
a=p.parse_args();root=Path(a.package).resolve()
w=json.loads(gzip.decompress((root/'data/word.json.gz').read_bytes()))
c=json.loads((root/'data/caller.json').read_text())
assert hashlib.sha256((root/'data/word.json.gz').read_bytes()).hexdigest()=='273e81f176f001684b1fa3eb857992bf58b54748004fcfe806b83adb48d2cc00'
assert hashlib.sha256((root/'data/caller.json').read_bytes()).hexdigest()=='3828d53e80ea97e8b866320f081af20b6b93bfebd58b95b56b85a7afe151af5e'
hist=Counter(Fraction(e[-2]) for e in w['program'] if e[0]=='ADD')
N=sum(hist.values());length_sum=odd_count=old_credit=round_credit=0
for q,n in hist.items():
    numerator,denominator=abs(q.numerator),q.denominator
    L=max(numerator.bit_length(),denominator.bit_length())
    odd=denominator >> ((denominator & -denominator).bit_length()-1)
    length_sum+=n*L
    odd_count+=n*(odd!=1)
    old_credit+=n*4*(numerator.bit_length()+sum(map(int,bin(numerator)[2:]))+denominator.bit_length()+1)
    if denominator!=1:
        round_credit+=n*4*(denominator.bit_length()+1)*(4 if odd!=1 else 1)
assert (N,length_sum,odd_count)==(61052,167955,4079)
assert (old_credit,round_credit)==(1717220,920796)
assert [e[1] for e in c['events'] if e[0]=='J']==list(range(1,19))
factor=18
vector=tuple(factor*x for x in (76*N+22*length_sum+10*odd_count,
    18*N+3*length_sum,156*N+48*length_sum+18*odd_count,38*N+13*length_sum+5*odd_count))
assert vector==(150763536,28850418,317868732,81428148)
raw=sum(vector[:3]);with_rows=sum(vector)

# Replay the immutable predecessor invoice, not the new audit reconstruction.
spec=importlib.util.spec_from_file_location('root_old_invoice',root/'reference/owned_invoice.py')
iv=importlib.util.module_from_spec(spec);spec.loader.exec_module(iv)
local=iv.local_invoice(w);outer=iv.caller_cost(c)
baseline=factor*local['reviewed_per_call']+outer['raw_rest']+outer['lambda_recharge']+factor*w['public']*104
assert baseline==826265904
model=json.loads((root/'reference/PRECISION-GUARDS.json').read_text())['optimistic_tariff_model']
assert model['baseline']==baseline and model['conditional_total']==843431488
release=factor*(old_credit+round_credit)
remaining=model['conditional_total']-release
room=10**9-remaining
assert (release,remaining,room)==(47484288,795947200,204052800)
assert Fraction(raw,room)==Fraction(82913781,34008800)
assert Fraction(with_rows,room)==Fraction(96485139,34008800)
assert raw+remaining==1293429886 and with_rows+remaining==1374858034
assert raw>room and with_rows>room and with_rows<3*room

# Omission and contamination controls must change the claimed coefficients.
assert sum(vector[:3])//18 != raw
copies=[e for e in w['program'] if e[0]=='COPY'];assert len(copies)==1
assert N+len(copies)!=N
assert with_rows-vector[3]!=with_rows
assert 10**9-model['conditional_total']!=room
out=dict(status='pass',method='independent Fraction coefficient histogram and closed aggregate sums; immutable predecessor invoice replay',
    native_ADD=N,distinct_coefficients=len(hist),length_sum=length_sum,odd_ADD=odd_count,
    physical_vector=vector,raw_actions=raw,raw_plus_rows=with_rows,
    released_credit=release,retained_other_model=remaining,replacement_headroom=room,
    necessary_raw_exchange=str(Fraction(raw,room)),necessary_combined_exchange=str(Fraction(with_rows,room)),
    accounting_controls=4,independent_pass_vector_proof='Separate native_physical cross-review required.',
    scientific_sha256={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ('PROOF.md','audit.py')},
    limitations=['Equal B and numerical converter are explicit hypothetical premises.',
                 'Other retained fees are model/upper charges, not runtime lower bounds.',
                 'No complete caller, physical cap failure, or new kappa.'])
Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True))
