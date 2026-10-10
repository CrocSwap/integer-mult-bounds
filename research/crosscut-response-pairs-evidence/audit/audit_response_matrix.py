#!/usr/bin/env python3
"""Check target-block invertibility needed for the response identity R=A^-1 C."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

if not __debug__:
    raise SystemExit('assertions required')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--export', type=Path, required=True)
    ap.add_argument('--selection', type=Path, required=True,
                    help='complete JSON list of selected entrances, with cut fields')
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists(), 'use a fresh output path'
    states = json.loads((a.export/'249-states.json').read_text())
    v = states['v']
    raw = (a.export/'249-records.bin').read_bytes()
    events = list(struct.iter_unpack('<6i', raw))
    cuts = sorted({x['cut'] for x in json.loads(a.selection.read_text())})
    rows = []
    for cut in cuts:
        assert 0 <= cut < len(events)
        outgoing, copies, selfadds, shears = 0, 0, 0, 0
        for op, dst, src, coeff, frame, category in events[:cut+1]:
            if op == 1:
                outgoing += v <= src < 2*v and not v <= dst < 2*v
                if v <= src < 2*v and v <= dst < 2*v:
                    shears += 1
                    selfadds += dst == src
            if op == 2:
                copies += v <= dst < 2*v
        assert outgoing == copies == selfadds == 0
        rows.append(dict(cut=cut, target_to_nontarget_adds=outgoing,
                         target_source_copies=copies, target_self_adds=selfadds,
                         target_elementary_shears=shears,
                         prefix_target_matrix_invertible=True))
    result = dict(
        status='PASS_TARGET_PREFIX_BLOCK_TRIANGULARITY',
        word_sha256=hashlib.sha256(raw).hexdigest(),
        selection_sha256=hashlib.sha256(a.selection.read_bytes()).hexdigest(),
        cuts=rows,
        formula_over_F2='prefix y_cut=A y+B x+C d; suffix dirty response R=A^-1 C, so ker(R)=ker(C)',
        scope='Algebraic audit of target block needed by proof wording; does not replace formal-column replay.')
    a.output.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
