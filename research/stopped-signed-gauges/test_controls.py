#!/usr/bin/env python3
"""Reject corrupted endpoint, stopping, moment and three-stock certificates."""
import copy
from fractions import Fraction as Q

def run(certificate,validate):
    examples=[]
    def changed(name,edit):
        c=copy.deepcopy(certificate);edit(c);examples.append((name,c))
    changed('omitted_endpoint_singleton',lambda c:c['complex']['profile']['child_multiplicities'].__setitem__('1',c['complex']['profile']['child_multiplicities']['1']-1))
    changed('stale_complex_halving_depth',lambda c:c['assembly']['finite_bridge']['complex'].__setitem__('halving_degree',17))
    changed('omitted_ordinary_leaf_stock',lambda c:c['assembly']['finite_bridge'].__setitem__('ordinary_leaf_row_degree',0))
    changed('stale_row_degree4000',lambda c:c['assembly']['finite_bridge']['rows'].__setitem__('degree',4000))
    changed('unpaid_early_dirty_readouts',lambda c:c['assembly']['finite_bridge']['complex'].__setitem__('scalar_group_upper',1633627072))
    changed('unstopped_coarse_saving_claimed_ordinary',lambda c:c['ordinary_bit'].__setitem__('saving',c['ordinary_bit']['coarse_saving']))
    changed('falsified_complex_moment',lambda c:c['complex']['moment'].__setitem__('upper','0'))
    changed('falsified_assembly_slack',lambda c:c['assembly']['constraints'].__setitem__('g3_above_kappa','1'))
    changed('adjacent_kappa_grid',lambda c:c.__setitem__('kappa',str(Q(c['kappa'])+Q(1,10**18))))
    changed('unbound_signed_word',lambda c:c['input_sha256'].__setitem__('complex_word','0'*64))
    passed=[]
    for name,c in examples:
        try:validate(c)
        except (AssertionError,ValueError):passed.append(name)
        else:raise AssertionError('Negative control accepted: '+name)
    return passed

if __name__=='__main__':
    import independent_check as audit
    certificate=audit.read(audit.HERE/'certificate.json')
    profiles,inputs=audit.rebuild()
    results=run(certificate,lambda c:audit.validate(c,profiles,inputs))
    print('PASS',len(results),'stopped signed-gauge corruption controls')
