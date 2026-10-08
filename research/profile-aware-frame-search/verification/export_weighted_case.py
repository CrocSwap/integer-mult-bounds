#!/usr/bin/env python3
"""Export exact upward-rounded characteristic weights for the Std Lean case."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

if sys.flags.optimize:
    raise RuntimeError('Run the export without Python -O/-OO; assertion checks are required.')


def export(candidate,output):
    d=json.loads(candidate.read_text());m,W=d['bit']['m'],d['bit']['W']
    saving=Q(d['bit_saving']);scale=10**30;rows=[];total=0
    for width,multiplicity in sorted((int(t),n)for t,n in d['bit']['child_multiplicities'].items()):
        log_upper=Q(d['bit']['moment']['logarithms'][str(width)]['upper'])
        v=saving*log_upper;F=width*(1+v+v*v/(2*(1-v/3)))
        z=F*scale;rounded=-(-z.numerator//z.denominator)
        assert Q(rounded,scale)>=F
        total+=multiplicity*rounded
        rows.append(dict(width=width,multiplicity=multiplicity,log_upper=str(log_upper),v=str(v),
                         F_upper=str(F),rounded_F_upper_numerator=rounded,rounding_scale=scale,
                         rounding_slack=str(Q(rounded,scale)-F)))
    denominator=m*W*scale;upper=Q(total,denominator)
    assert upper<1 and len(d['assembly']['constraints'])==47
    result=dict(status='exact_weighted_F_rounding_and_47_slacks_passed',source_commit=d['source']['commit'],
        source_certificate_sha256=d['source']['files']['research/pair-assembly/frame/frame-certificate.json'],
        refined_certificate_sha256=sha256(candidate.read_bytes()).hexdigest(),m=m,W=W,total_rank=d['bit']['total_rank'],
        bit_saving=d['bit_saving'],kappa=d['kappa'],rows=rows,weighted_upper_numerator=total,
        weighted_upper_denominator=denominator,rounded_moment_upper=str(upper),rounded_moment_gap=str(1-upper),
        named_slacks=d['assembly']['constraints'],named_margins=d['assembly']['margins'],parameters=d['assembly']['parameters'],
        comparison=dict(old_published_kappa='5101691/100000000000',old_bit_saving='39859/781250000',
                        old_formal_scoped_limit='39859/781289859',exceeds_old_scoped_limit=Q(d['kappa'])>Q(39859,781289859),
                        parameter_only=False,new_producer_claim=False,new_compiler_word_claim=True,
                        frozen62_network_at_new_saving_lower=d['comparison']['frozen62_network_at_new_saving_lower'],
                        frozen62_network_rejected_at_new_saving=d['comparison']['frozen62_network_rejected_at_new_saving']),
        scope='New profile-aware compiler words on the unchanged frozen PR62 graph; fresh full word/basis/frame/profile validation, inherited data geometry and all-size interfaces.')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS weighted rows',len(rows),'moment gap',float(1-upper),'kappa',d['kappa'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('candidate',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();export(a.candidate,a.output)
