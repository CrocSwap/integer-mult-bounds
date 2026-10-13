"""Port one 504-helper construction stage onto the K-triangle word.  Apache-2.0.  Prepared with Claude Code assistance.

usage: build_port_stage.py --shadow-input I4 --shadow-output O4 --input I8 --map HELPER-MAP.json --gk-dir GK --out DIR

The shadow pair (I4 -> O4) is one stage of a 504-helper chain, rebuilt in the same run from pinned sources.  I8 is the
K-triangle word at the matching point of its own chain, and HELPER-MAP.json is the 504 -> R register map written by
construct_k_triangle.py.  Registers below 448 keep their ids; the removed packet copies have no image.

The port does the following:
* It renumbers I4 and O4 through the map and drops their gates that touch a removed register.
* It matches gates by scalar operation (the gate without its frame), aligning I4 with O4 and I4 with I8 separately.
* It builds O8 in O4 gate order:
  * each matched gate is taken from I8, with O4's frame wherever the stage changed that frame;
  * each gate the stage introduced is taken from O4;
  * each I8-only gate (the K-triangle reads) stays after the O4 image of its I8 predecessor.
* It replays the stage's entrance (start_extra) and target_levels changes.
* It rebuilds the cleanup with the inherited inverse rule.

The constructor is a search transfer only.  The verifier certifies the output independently: the generalised native
audit (exact forward and inverse replay of every column, native frame chains) runs on every ported word, and every
input and output is pinned by content hash."""
import argparse, copy, difflib, gzip, hashlib, json, sys
from collections import Counter
from pathlib import Path

assert __debug__, 'Assertions required'
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]


def regs(g): return (g[1], g[2]) if g[0] == 'add' else (g[1],)


def key(g): return json.dumps(g[:-1])


def inverse(e):
    e = copy.deepcopy(e)
    if e[0] == 'add': e[3] *= -1
    else: e[2], e[3] = e[3], e[2]
    e[-1] = list(FULL); return e


def align(xs, ys):
    """index map xs -> ys over runs of equal scalar operations"""
    sm = difflib.SequenceMatcher(None, [key(g) for g in xs], [key(g) for g in ys], autojunk=False)
    return {i1 + k: j1 + k for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag == 'equal' for k in range(i2 - i1)}


def transfer_section(I4, O4, I8, stats):
    a, b = align(I4, O4), align(I4, I8)
    o2i = {j: i for i, j in a.items()}; i8from4 = {j: i for i, j in b.items()}
    anchor = {j8: a[i4] for j8, i4 in i8from4.items() if i4 in a}
    pending, last = {}, -1
    for j8, g in enumerate(I8):
        if j8 in anchor: last = anchor[j8]
        elif j8 not in i8from4: pending.setdefault(last, []).append(copy.deepcopy(g)); stats['kept_own'] += 1
        else: stats['dropped_by_stage'] += 1
    out = list(pending.get(-1, []))
    for k, g in enumerate(O4):
        if k in o2i:
            i4 = o2i[k]
            if i4 in b:
                g8 = copy.deepcopy(I8[b[i4]])
                if I4[i4][-1] != g[-1]: g8[-1] = copy.deepcopy(g[-1]); stats['frames_changed'] += 1
                out.append(g8)
        else:
            out.append(copy.deepcopy(g)); stats['introduced'] += 1
        out.extend(pending.get(k, []))
    return out


def main():
    ap = argparse.ArgumentParser()
    for k in ('--shadow-input', '--shadow-output', '--input', '--map', '--gk-dir', '--out'): ap.add_argument(k, type=Path, required=True)
    a = ap.parse_args(); assert not a.out.exists()
    sys.path.insert(0, str(a.gk_dir)); import gk_word as G, gk_common as C
    G.V = C.V = 112
    rd = lambda p: json.loads(gzip.decompress(p.read_bytes()))
    enc = lambda x: json.dumps(x, sort_keys=True, separators=(',', ':')).encode(); sha = lambda x: hashlib.sha256(x).hexdigest()
    I4, O4, I8 = rd(a.shadow_input), rd(a.shadow_output), rd(a.input)
    fm = {int(k): int(v) for k, v in json.loads(a.map.read_text())['map'].items()}
    assert all(fm[k] == k for k in fm if k < 448), 'only ids >= 448 may move'
    R = I8['report']['R']; assert sorted(fm.values()) == list(range(224 + R)), 'map is not onto the K-triangle registers'
    assert I4['report'].get('R', 504) == 504 and len(fm) + len(set(range(728)) - set(fm)) == 728
    rem = set(range(728)) - set(fm)
    rn = lambda r: fm[r]
    touches = lambda g: any(r in rem for r in regs(g))
    def rg(g):
        g = copy.deepcopy(g); g[1] = rn(g[1])
        if g[0] == 'add': g[2] = rn(g[2])
        return g
    def rn_word(w):
        w = copy.deepcopy(w)
        for s in ('A', 'B', 'cut', 'precondition', 'cleanup'):
            if s in w: w[s] = [rg(g) for g in w[s] if not touches(g)]
        for k in ('start_extra', 'helper_final'):
            if k in w: w[k] = {str(rn(int(r))): f for r, f in w[k].items() if int(r) not in rem}
        return w
    I4r, O4r = rn_word(I4), rn_word(O4)
    O8 = copy.deepcopy(I8); stats = {s: Counter() for s in ('A', 'B')}
    for s in ('A', 'B'): O8[s] = transfer_section(I4r[s], O4r[s], I8[s], stats[s])
    for k in ('start_extra', 'target_levels'):
        x, y = I4r.get(k, {}), O4r.get(k, {}); d = dict(I8.get(k, {}))
        for r in set(x) | set(y):
            if x.get(r) != y.get(r):
                if r in y: d[r] = y[r]
                else: d.pop(r, None)
        if k in O4 or k in I8: O8[k] = dict(sorted(d.items(), key=lambda kv: int(kv[0])))
    for k in O4:
        if k not in ('A', 'B', 'cleanup', 'report', 'start_extra', 'target_levels', 'cut', 'precondition'):
            assert O4r[k] == I4r[k], 'stage changed an unported field: ' + k
    O8['cleanup'] = [inverse(e) for e in reversed(O8['A'] + O8['B']) if not 112 <= e[1] < 224]
    H = G.profile(O8)
    ws = [9 - len(G.basis(O8['start_extra'].get(str(224 + h), []))) for h in range(R)]
    O8['report'] = dict(I8['report'], local_profile={str(k): v for k, v in sorted(H.items())}, local_rank_mass=sum(k * v for k, v in H.items()),
                        width_inventory={str(k): v for k, v in sorted(Counter(ws).items())})
    a.out.mkdir(parents=True); (a.out / 'FULL-WORD.json.gz').write_bytes(gzip.compress(enc(O8), mtime=0))
    receipt = dict(status='PORTED_STAGE_PENDING_NATIVE_AUDIT', R=R, removed_504_helpers=sorted(rem),
                   shadow_input_content_sha256=sha(enc(I4)), shadow_output_content_sha256=sha(enc(O4)), input_content_sha256=sha(enc(I8)),
                   output_content_sha256=sha(enc(O8)), sections={s: dict(v) for s, v in stats.items()}, local_profile=O8['report']['local_profile'],
                   scope='Transfer construction only; exactness, frame chains and profile are certified by the native audit run on the output.')
    (a.out / 'PORT-STAGE.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', newline='\n'); print(json.dumps(receipt, indent=2))


main()
