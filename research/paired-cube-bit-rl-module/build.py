#!/usr/bin/env python3
"""Build the p = 12 bit word with module.PATTERN through PR168's unchanged producer.

Copyright 2026 Joel Pulikkan (GamingPuzzled). Apache-2.0. Prepared with Anthropic Claude assistance.
research/paired-cube-bit/paired_cube_bit_word.py is imported unchanged; only its p = 12 all-but-one module
(nested_prefix) is replaced by module.module.  --solve recomputes the carrier matching (Hopcroft-Karp), freezes it in arcs_p12.json and
writes out/ from the frozen arcs; the default regenerates from the frozen arcs and requires byte-identical out/ files.
"""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/paired-cube-bit')); sys.path.insert(0, str(HERE))
import paired_cube_bit_word as B
import module

B.nested_prefix = module.module


def main():
    assert not sys.flags.optimize, 'run without -O'
    solve = '--solve' in sys.argv
    arcs_path = HERE / 'arcs_p12.json'
    frozen = None if solve else json.loads(arcs_path.read_text())
    if solve:      # solve the matching, freeze it, then build from the frozen arcs so frame ids match --check
        arcs_path.write_text(B.dumps(B.build(12, None, log=lambda *a: None)[2]))
        frozen = json.loads(arcs_path.read_text())
    out, prf, arcs, exp = B.build(12, frozen, log=lambda *a: None)
    assert arcs == frozen, 'frozen arcs reproduced'
    files = {'word_p12.json': B.dumps(out), 'profile_p12.json': B.dumps(prf)}
    files.update({'%s_p12.json' % k: B.dumps(v) for k, v in exp.items()})
    if solve:
        (HERE / 'out').mkdir(exist_ok=True)
        for name, text in files.items(): (HERE / 'out' / name).write_text(text)
    else:
        for name, text in files.items():
            assert (HERE / 'out' / name).read_text() == text, 'byte-identical regeneration of ' + name
    print('PASS %s p=12 pattern %s: R %d, W %d, gauges %d, float a_b %.7e' % ('wrote' if solve else 'regenerated',
          module.PATTERN, prf['R'], prf['W_per_vertex'], prf['selected_roles'],
          B.float_root(prf['child_histogram'], prf['W_per_vertex'], prf['m'])))


if __name__ == '__main__':
    main()
