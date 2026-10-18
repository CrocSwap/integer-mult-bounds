"""Exact dirty-column checks and adversarial controls. Apache-2.0.

Linear-form helper adapted from Douglas R. Colkitt's
tests/test_complex_compression.py. Substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
import unittest
from audit import expected_map, verify_dag, check_pins
from circuit import JointTies
from complex_compression import invoke
from experiments.disjoint_tensor import scalar_program


class Linear:
    def __init__(self, coefficients):
        self.coefficients={k:Q(v) for k,v in coefficients.items() if v}
    def __add__(self, other):
        if other==0: return self
        c=dict(self.coefficients)
        for k,v in other.coefficients.items(): c[k]=c.get(k,Q(0))+v
        return Linear(c)
    __radd__=__add__
    def __mul__(self, scalar):
        return Linear({k:v*scalar for k,v in self.coefficients.items()})
    __rmul__=__mul__
    def __sub__(self, other): return self+(-1)*other
    def __eq__(self, other):
        return isinstance(other,Linear) and self.coefficients==other.coefficients


def full_dirty_columns(code, inverse=False):
    v=len(code['triples']); R=code['roles']; h=code['h']
    values=[Linear({i:1}) for i in range(2*v+R+h+1)]
    banks=[values[:v],values[v:2*v],values[2*v:2*v+R],values[2*v+R:]]
    old=[list(bank) for bank in banks]
    invoke(*banks,code,inverse=inverse)
    if banks[0]!=old[0] or banks[2:]!=old[2:]:
        raise ValueError('dirty inputs were not restored')
    sign=-1 if inverse else 1
    if banks[1]!=[b+sign*a for a,b in zip(old[0],old[1])]:
        raise ValueError('signed endpoint differs')
    return len(values)


class Controls(unittest.TestCase):
    def circuit(self): return JointTies(8,4,((1,1),),(1,2,3,0))
    def test_all_independent_dirty_columns_both_signs(self):
        code=scalar_program(self.circuit())
        for inverse in (False,True): self.assertGreater(full_dirty_columns(code,inverse),0)
    def test_invalid_recipe(self):
        for kwargs in ({'flips':((1,2),)}, {'flips':((1,1),(1,1))},
                       {'order':(0,0,2,3)}, {'root_split':0}):
            args=dict(h=8,root_split=4); args.update(kwargs)
            with self.assertRaises((ValueError,TypeError)): JointTies(**args)
    def test_altered_output_coefficient(self):
        c=self.circuit(); node=next(iter(c.outputs.values())); c.support[node]^=1
        with self.assertRaises(ValueError): verify_dag(c,expected_map(8))
    def test_overlapping_sum(self):
        c=self.circuit(); node=next(n for n in c.active if c.args[n]); a,b=c.args[node]
        c.args[node]=(a,a)
        with self.assertRaises(ValueError): verify_dag(c,expected_map(8))
    def test_cyclic_sum(self):
        c=self.circuit(); node=next(n for n in c.active if c.args[n]); a,b=c.args[node]
        c.args[node]=(node,b)
        with self.assertRaises(ValueError): verify_dag(c,expected_map(8))
    def test_omitted_source_access(self):
        code=scalar_program(self.circuit()); code['sources']=code['sources'][1:]
        with self.assertRaises(ValueError): full_dirty_columns(code)
    def test_wrong_weighted_injection(self):
        code=scalar_program(self.circuit()); i,s,q=code['outputs'][0]
        code['outputs'][0]=(i,s,-q)
        with self.assertRaises(ValueError): full_dirty_columns(code)
    def test_omitted_mixer_gate(self):
        code=scalar_program(self.circuit()); code['gates']=code['gates'][1:]
        with self.assertRaises(ValueError): full_dirty_columns(code)
    def test_source_bindings(self):
        self.assertEqual(check_pins()['base_commit'],'bbc600db2fc15007b7c914f4f2b2ed55fa909c87')


if __name__=='__main__': unittest.main()
