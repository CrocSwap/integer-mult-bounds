"""Rebuild the frozen 504-helper supplier, without rerunning any search.

The explicit entrance selection is the input proof object. Every selected
response relation is recomputed over rational numbers by the attributed
gauge/kernel rewriter, then the fixed scalar word is frame-coalesced.
Prepared for icekylinx with GPT-6 Astra assistance. Apache-2.0.
"""
import argparse
import gzip
import json
import subprocess
import sys
from pathlib import Path


def main():
    if not __debug__:
        raise SystemExit('Assertions must be enabled.')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    a = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    a.work = a.work.resolve()
    assert not a.work.exists(), 'Use a new output directory.'
    a.work.mkdir(parents=True)
    subprocess.run([sys.executable, '-B', str(root/'code/construct_504.py'),
                    str(root/'inputs/hamming'), str(a.work/'raw')], check=True)
    sys.path.insert(0, str(root/'vendor/gk'))
    import gk_common as common
    import gk_word as g
    word = json.load(gzip.open(a.work/'raw/FULL-WORD.json.gz'))
    common.V = g.V = word['report']['v']
    common.DATA = g.DATA = 8*8*common.V
    selection = json.loads((root/'inputs/SELECTION.json').read_text())
    changed = g.build(word, selection, check=True)
    for key in ('global_profile', 'live', 'complex_coarse_float', 'gain_percent_float'):
        changed['report'].pop(key, None)
    changed['report'].update(v=112, h=9, R=504, cst=64,
        local_rank_mass=sum(int(r)*z for r,z in changed['report']['local_profile'].items()),
        status='REBUILT_EXACT_SELECTED_WORD_PENDING_INDEPENDENT_REPLAY')
    selected = a.work/'selected'
    selected.mkdir()
    (selected/'FULL-WORD.json.gz').write_bytes(g.dump(changed))
    subprocess.run([sys.executable, '-B', str(root/'code/coalesce_frames.py'),
                    '--word', str(selected/'FULL-WORD.json.gz'),
                    '--out', str(a.work/'coalesced')], check=True)
    print(a.work/'coalesced/FULL-WORD.json.gz', flush=True)


if __name__ == '__main__':
    main()
