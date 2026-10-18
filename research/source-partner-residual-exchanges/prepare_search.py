"""Recover pinned sources and construct the single nominated order's search inputs.

Apache-2.0. Derived from PR2530 by zxv; OpenAI Codex assistance.
"""
import argparse
import gzip
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent/'source-partner-lifetimes'
sys.path.insert(0, str(SOURCE))
from build import prepare


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', type=Path, required=True)
    args = ap.parse_args()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    p = prepare(work/'prepared')
    for a, b in [('eight-providers.json', 'new/BORROW-PROVIDERS.json'),
                 ('eight-fill.json.gz', 'new/borrow-fill/FILL.json.gz'),
                 ('eight-alias-base.json.gz', 'new/borrow/words/BORROW-WORD-43base.json.gz')]:
        shutil.copy2(SOURCE/'evidence'/a, p/b)
    sp = importlib.util.spec_from_file_location('window_source', p/'vendor/build_parent.py')
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    d = json.loads(gzip.decompress((SOURCE/'evidence/order-screen.json.gz').read_bytes()))
    order = [[s, r] for s, r in sorted(((s, r) for s in range(9) for r in range(74)),
             key=lambda sr: (8*sr[0]+2*sr[1]+(sr[0] == 2), sr[0], sr[1]))]
    assert order == json.loads((HERE/'evidence/CANDIDATE-ORDER.json').read_text())
    d['order'] = order
    d['windows'] = mod.actual_windows(mod.read(p/'inputs/GLOBAL-TEMPLATE.json.gz'), order)[0]
    out = work/'packing'
    out.mkdir()
    (out/'order-screen.json').write_text(json.dumps(d))
    shutil.copy2(SOURCE/'evidence/interval-packing-neworder.json', out/'baseline-packing.json')
    shutil.copy2(SOURCE/'evidence/eight-alias-base.json.gz', out/'eight-alias-base.json.gz')
    print('SOURCE_PARTNER_SEARCH_WORK=' + str(out))
    print('SOURCE_PARTNER_PREPARED=' + str(p))


if __name__ == '__main__':
    main()
