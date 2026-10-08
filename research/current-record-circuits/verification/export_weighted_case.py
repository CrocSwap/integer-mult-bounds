#!/usr/bin/env python3
"""Export exact upward-rounded characteristic weights for the Std Lean case."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
from math import factorial

if sys.flags.optimize:
    raise RuntimeError('Run the export without Python -O/-OO; assertion checks are required.')


def export(candidate,output):
    d=json.loads(candidate.read_text());m,W=d['bit']['m'],d['bit']['W']
    saving=Q(d['bit_saving']);scale=10**40;rows=[];total=0
    for width,multiplicity in sorted((int(t),n)for t,n in d['bit']['child_multiplicities'].items()):
        log_upper=Q(d['bit']['moment']['logarithms'][str(width)]['upper'])
        v=saving*log_upper
        F=width*(sum((v**j/Q(factorial(j)) for j in range(9)),Q())+
                 v**9/(Q(factorial(9))*(1-v/10)))
        z=F*scale;rounded=-(-z.numerator//z.denominator)
        assert Q(rounded,scale)>=F
        total+=multiplicity*rounded
        rows.append(dict(width=width,multiplicity=multiplicity,log_upper=str(log_upper),v=str(v),
                         F_upper=str(F),rounded_F_upper_numerator=rounded,rounding_scale=scale,
                         rounding_slack=str(Q(rounded,scale)-F)))
    denominator=m*W*scale;upper=Q(total,denominator)
    assert upper<1 and len(d['assembly']['constraints'])==47
    result=dict(status='exact_weighted_F_rounding_and_47_slacks_passed',upper_enclosure_kind='taylor8_tail',source_commit=d['source']['commit'],
        source_certificate_sha256=d['source']['files']['certificates/split-pair-kappa.json'],
        refined_certificate_sha256=sha256(candidate.read_bytes()).hexdigest(),m=m,W=W,total_rank=d['bit']['total_rank'],
        bit_saving=d['bit_saving'],kappa=d['kappa'],rows=rows,weighted_upper_numerator=total,
        weighted_upper_denominator=denominator,rounded_moment_upper=str(upper),rounded_moment_gap=str(1-upper),
        named_slacks=d['assembly']['constraints'],named_margins=d['assembly']['margins'],parameters=d['assembly']['parameters'],
        comparison=dict(old_published_kappa=d['comparison']['baseline71_kappa'],old_bit_saving=d['comparison']['baseline71_bit_saving'],
                        old_formal_scoped_limit=d['comparison']['baseline71_scoped_limit'],exceeds_old_scoped_limit=Q(d['kappa'])>Q(d['comparison']['baseline71_scoped_limit']),
                        parameter_only=False,new_producer_claim=False,new_compiler_word_claim=True,
                        baseline71_network_at_new_saving_lower=d['comparison']['baseline71_network_at_new_saving_lower'],
                        baseline71_network_rejected_at_new_saving=d['comparison']['baseline71_network_rejected_at_new_saving']),
        scope='New profile-aware compiler words on the pinned PR71 graph; fresh full word/basis/frame/profile validation, inherited data geometry and all-size interfaces.')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS weighted rows',len(rows),'moment gap',float(1-upper),'kappa',d['kappa'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('candidate',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();export(a.candidate,a.output)
