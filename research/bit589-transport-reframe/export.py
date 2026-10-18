"""Write the explicit word of a relocation sequence with its exact optimal frames, for the unchanged official checkers.

Moves are applied in order, each to the word produced by the previous one (search.py's (kind, section, index,
source, insertion index) tuples). Frames come from reframe.optimum; closed frames outside the catalogue are appended.
D, start and final are unchanged; C is rebuilt as the literal reverse of the z-destination gates of A then B at the
full frame (H4). The written word is then replayed by PR589's tune/wlib.py (exact F2 endpoint on every column, frame
nesting, paid profile); run code/xcheck_p.py on it for the independent interface audit.

Usage: export.py WORD.json.gz C OUT.json.gz MOVES_JSON
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
"""
import copy
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reframe as R
import search as S
from pairs import View

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/e8-bit-p111-tuned/tune'))
import wlib  # noqa: E402  (PR589's exact replay, unchanged)


def build(path, z, moves):
    word = R.Word(R.load(path))
    cur = word
    for mv in moves:
        A, B = S.apply(cur, tuple(mv))
        cur = View(word, A, B)
    opt = R.optimum(word, cur.A, cur.B, z, want_frames=True)
    if opt is None:
        raise SystemExit('no legal frame assignment')
    w = copy.deepcopy(word.w)
    idx = {m: i for i, m in enumerate(word.fm)}

    def fid(m):
        if m not in idx:
            idx[m] = len(w['frames'])
            w['frames'].append([i for i in range(w['v']) if m >> i & 1])
        return idx[m]

    fr = opt['frames']
    nA = len(cur.A)
    w['A'] = [[fid(fr[k]), t, list(ss)] for k, (f, t, ss) in enumerate(cur.A)]
    w['B'] = [[fid(fr[nA + k]), t, list(ss)] for k, (f, t, ss) in enumerate(cur.B)]
    w['C'] = wlib.rebuild_C(w)
    return w, opt


def main():
    path, c, out, moves = sys.argv[1], Fraction(sys.argv[2]), sys.argv[3], json.loads(sys.argv[4])
    w, opt = build(path, float(c), moves)
    replayed = {int(k): v for k, v in wlib.paid(w).items()}  # asserts the exact endpoint and nesting
    assert replayed == opt['profile'], (replayed, opt['profile'])
    sha = wlib.save(w, out)
    print(json.dumps(dict(out=out, sha256=sha, moves=moves, profile=replayed, frames=len(w['frames']),
                          gates={s: len(w[s]) for s in 'DABC'})))


if __name__ == '__main__':
    main()
