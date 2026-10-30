"""Shared-donor response kernel on the pinned PR436 R740 bit word (bitE8/1), from a frozen selection.
Mechanism and code: chafreaky's #417 (vendor/kernel417: stages.kernel and the e8core exact replay with the source-span rule;
#320/#329 kernel lineage); selection re-derived on this word with #417's discovery tools (ILS, chi scored at m = 64).
Each entry: pivot p starts at entrance E (inside the first frame of p and of every donor), leaves the frame-0 completion
gates; each donor pays d += p at E at the start of A and again at FULL after C (F2: response(p) = XOR responses(donors)).
Checks here: selection bound to the exact input word, kernel applied, full exact replay (legality, F2 on all columns,
source spans), output bound to the frozen hash, every new frame root-closed with Gram determinant (form <x,y>/2) a power
of two (no new bad primes), total entrance rank = 0 mod 8 (exact width-64 bank tiling, checked in bit_global/bit_audit).
Original kernel integration by rohanarun, with Anthropic Claude assistance. This R740 selection and integration by OpenAI Codex; Apache-2.0."""
import json, os, sys, hashlib
from fractions import Fraction as Q
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'vendor/kernel417'))
from stages import kernel, content_sha
from e8core import replay, Lat
D = Path(os.environ['E8_OUTPUT']) / 'bit426-source-centres'
src = D / 'bit-source-centres.json'; pre = D / 'bit-source-centres-prekernel.json'
c = json.loads(src.read_bytes()); pre.write_bytes(src.read_bytes())
sel = json.loads((HERE / 'stages/kernel-selection.json').read_text())
assert sel['input_sha256'] == content_sha(c), 'selection bound to a different input word'
w, ne, tot, nd = kernel(c, sel['entries'])
assert tot % 8 == 0 and tot == sel['total_entrance_rank']
r = replay(w, span_mode='z'); assert not r['viol'], r['viol'][:5]
assert content_sha(w) == sel['output_sha256'], 'output differs from the frozen selection output'
L = Lat(w['lines']); n0 = len(c['frames']); newdets = []
assert w['frames'][:n0] == c['frames']
def det(M):
    M = [[Q(x) for x in r] for r in M]; d = Q(1); k = len(M)
    for i in range(k):
        p = next((j for j in range(i, k) if M[j][i]), None)
        if p is None: return Q(0)
        if p != i: M[i], M[p] = M[p], M[i]; d = -d
        d *= M[i][i]
        for j in range(i + 1, k):
            f = M[j][i] / M[i][i]; M[j] = [a - f * b for a, b in zip(M[j], M[i])]
    return d
for fr in w['frames'][n0:]:
    m = sum(1 << i for i in fr); assert L.close(m) == m, 'new frame not root-closed'
    vs = [w['lines'][i] for i in fr]
    # basis of the span: greedy independent roots
    B = []
    for x in vs:
        if len(B) < 8 and abs(det([[sum(a * b for a, b in zip(u, v)) for v in B + [x]] for u in B + [x]])) != 0: B.append(x)
    G = [[Q(sum(a * b for a, b in zip(u, v)), 2) for v in B] for u in B]; g = det(G); assert g > 0
    num, den = g.numerator, g.denominator
    for x in (num, den):
        while x % 2 == 0: x //= 2
        assert x == 1, ('new frame Gram determinant has an odd prime factor', fr, g)
    newdets.append(str(g))
D.joinpath('bit-source-centres-pre-retime.json').write_bytes(json.dumps(w, sort_keys=True, separators=(',', ':')).encode())
# The kernel output is followed by a source-bound joint A/B retime with the same scalar operands.
from primitive_retime import apply
rt=json.loads((HERE / 'stages/retime-selection.json').read_text())
w=apply(w,rt)
D.joinpath('bit-source-centres.json').write_bytes(json.dumps(w, sort_keys=True, separators=(',', ':')).encode())
assert json.loads((HERE/'stages/final-word.json').read_text())==w
r2 = replay(w, span_mode='z'); assert not r2['viol'], r2['viol'][:5]
res = dict(status='PASS_KERNEL_AND_PRIMITIVE_RETIME_STAGE', entries=ne, total_entrance_rank=tot, donor_slots=nd, new_frames=len(w['frames']) - n0,
           new_frame_gram_determinants=sorted(set(newdets)), kernel_histogram=dict(sorted(r['H'].items())), local_histogram=dict(sorted(r2['H'].items())), columns=r2['n'],
           input_sha256=sel['input_sha256'], kernel_output_sha256=sel['output_sha256'], output_sha256=rt['output_sha256'], primitive_retime_moves=len(rt['gates']))
(D / 'bit-kernel-receipt.json').write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps(res))
