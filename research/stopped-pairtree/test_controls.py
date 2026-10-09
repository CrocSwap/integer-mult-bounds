#!/usr/bin/env python3
"""Adversarial controls for the complete stopped pair-tree arithmetic ledger."""
import copy
from fractions import Fraction as Q

def run(certificate,validate):
    examples=[]
    def changed(name,edit):
        c=copy.deepcopy(certificate);edit(c);examples.append((name,c))
    changed('omitted_complex_singleton',lambda c:c['complex']['profile']['child_multiplicities'].__setitem__('1',c['complex']['profile']['child_multiplicities']['1']-1))
    changed('omitted_ordinary_leaf_stock',lambda c:c['assembly']['finite_bridge'].__setitem__('ordinary_leaf_row_degree',0))
    changed('stale_two_factor_row_coefficient',lambda c:c['assembly']['finite_bridge']['rows'].__setitem__('coefficient',924))
    changed('wrong_odd_grid_divisor',lambda c:c['assembly']['finite_bridge']['semantic'].__setitem__('fixed_odd_divisor',1))
    changed('unstopped_coarse_saving_claimed_ordinary',lambda c:c['ordinary_bit'].__setitem__('saving',c['ordinary_bit']['coarse_saving']))
    changed('falsified_complex_moment',lambda c:c['complex']['moment'].__setitem__('upper','0'))
    changed('falsified_assembly_slack',lambda c:c['assembly']['constraints'].__setitem__('g3_above_kappa','1'))
    changed('adjacent_kappa_grid',lambda c:c.__setitem__('kappa',str(Q(c['kappa'])+Q(1,10**18))))
    changed('unbound_literal_matching',lambda c:c['input_sha256'].__setitem__('complex','0'*64))
    passed=[]
    for name,c in examples:
        try:validate(c)
        except (AssertionError,ValueError):passed.append(name)
        else:raise AssertionError('Negative control accepted: '+name)
    p=certificate['assembly']['parameters'];old_prefix=1-Q(p['epsilon'])*(1+Q(p['c']))
    assert 0<old_prefix<=Q(certificate['kappa'])
    passed.append('original_prefix_work_margin_at_balanced_parameters')
    return passed

if __name__=='__main__':
    import independent_check as audit
    certificate=audit.read(audit.HERE/'certificate.json')
    profiles,inputs=audit.rebuild()
    results=run(certificate,lambda c:audit.validate(c,profiles,inputs))
    print('PASS',len(results),'stopped pair-tree corruption controls')
