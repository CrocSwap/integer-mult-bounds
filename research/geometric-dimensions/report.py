"""Collect completed exact circuit screens and architecture-specific bounds.

Run explore.py first. This collector does not rerun the C++ producer; its
input files are explicitly listed and hashed in the report.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from math import comb
import json

from family import checks, saving_upper, TARGET
from matching import matching, small_hall_control

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    dimensions=[]
    for h in (24,26,27,29,30,32):
        path=ROOT/f'build/geometric-dimensions/{h}/result.json'
        result=json.loads(path.read_text())
        assert result['h']==h
        row=result['checked']
        assert row['every_boundary_sum_verified'] and row['every_template_addition_disjoint']
        v,m=comb(h,5),h**3
        assert result['original']['outputs']==10*v+comb(h,2)
        assert row['role_upper_bound']==row['optimized_additions']+10*v+comb(h,2)
        assert row['new_star_additions']==sum(x['multiplicity']*min(x['additions'].values()) for x in result['templates'])
        eta=F(v-6*comb(h,2)*(h-2),2*m*(v+row['role_upper_bound']))
        upper=saving_upper(eta,m)
        assert upper<TARGET
        dimensions.append(dict(h=h,roles=row['role_upper_bound'],eta=eta,
                               exact_saving_upper=upper,below_pr9_certified_bit_saving=True,
                               producer_check=row,screen_file=str(path.relative_to(ROOT)),
                               screen_sha256=sha256(path.read_bytes()).hexdigest()))
    report=dict(status='RESEARCH EXTENSIONS AND NEGATIVE SCREENS; NO NEW KAPPA',
                dimensions=dimensions, family=checks(),
                explicit_matchings=[matching(h) for h in (8,10,24,26,28,30,32)],
                small_hall_controls=[small_hall_control(*args) for args in ((9,5,2),(11,7,3))],
                source_sha256={p.name:sha256(p.read_bytes()).hexdigest()
                               for p in sorted(HERE.iterdir()) if p.suffix in ('.py','.cpp')},
                dependency_pr9_commit='cfd6a2baded9dba990b987934474a7721d6ca3fb')
    (HERE/'report.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
    print('PASS: six exact circuit screens below the PR #9 saving')
    print('PASS:',sum(row['five_sets'] for row in report['explicit_matchings']),
          'matching images checked across seven dimensions')
    print('PASS: exact architecture-specific bounds for q=5 and all q>=7')


if __name__=='__main__':main()
