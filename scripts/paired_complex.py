"""Paired weighted-triple exclusion in eumemic's complex side interface.

The inherited point-label and injection-splitting verifier is from PR #3.
The new disjoint producer is PairedTriple, with unchanged pair-star correction.
"""
from fractions import Fraction as Q
from math import comb,log,log1p
import argparse,json
from paired_triple_circuit import PairedTriple
from complex_circuit import ComplexSideCircuit,Checks

class PairedComplex(ComplexSideCircuit):
    def build_disjoint(self):
        paired=PairedTriple(self.h)
        nodes={0:0}|{j+1:self.input[t] for j,t in enumerate(paired.inputs)}
        for n in sorted(paired.active):
            if paired.args[n]:
                a,b=paired.args[n];nodes[n]=self.add(nodes[a],nodes[b],'d0')
        for S,n in paired.outputs.items():self.emit(S,nodes[n],Q(1,2))
