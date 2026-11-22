#!/usr/bin/env python3
"""Run e264's genuine 66-bit binary tariff at the changed trial."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import json
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(Path(sys.argv[1]).resolve()))
sys.path.insert(1,str(ROOT))
from upstream import install
install()
from installations import BINARY_C
from raw_binary_stage import binary_word
from unpowered_price import certify
from check_complete import tariff
from independent_binary_price import mass,raw_moments
from strong_binary import graph,caller

word=binary_word()
targets,paid=Counter(word.targets),Counter(word.paid)
assert (targets,paid)==raw_moments(graph(),caller())
margin,cells=certify(BINARY_C,(targets,paid))
assert margin>0 and cells
independent=mass(targets,1-BINARY_C,False)-mass(paid,1-BINARY_C,True)
assert independent>0
print('PASS_461_TWO_DIRECTED_RAW_MARGINS',flush=True)
# This is the literal e264 tariff guard, including the minimum cell share,
# split/moment enclosure and the physical 11/8-bit bound.
bill=tariff(BINARY_C,(targets,paid),134)
assert bill['cells']==len(cells)
print('PASS_461_E264_BINARY_PHYSICAL_TARIFF',flush=True)
result={'binary_trial':str(BINARY_C),'t_denominator_bits':(1-BINARY_C).denominator.bit_length(),
        'directed_margin':str(margin),'independent_mass_difference':str(independent),
        'cell_count':len(cells),'minimum_cell_fraction':str(min(cells.values())),
        'actual_e264_tariff':bill,'scope':'exact finite price/coupling; not a tape-simulation proof'}
Path(sys.argv[2]).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
