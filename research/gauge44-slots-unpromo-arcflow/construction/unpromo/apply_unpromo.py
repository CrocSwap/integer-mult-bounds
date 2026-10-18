"""apply_unpromo.py BASE-WORD RECIPE OUT-WORD [--mutant NAME]
Apply an explicit entrance-restoration recipe: the listed entering helpers get the recorded dimension-four entrance
frames, the listed B gates get the recorded frames, the scalar program is unchanged, and the report's local profile,
rank mass and width inventory are set to the recipe's expected values (the native stage recomputes and checks them).
Standard library only; the output is pinned by content SHA256.
Mutants (must be rejected downstream): 'wrong_entrance' puts one entrance frame outside its first gate's frame;
'nonmonotone' lowers one changed gate frame below the entrance it serves; 'skip_frames' keeps the old gate frames
(a legal but more expensive word: its profile differs from the recipe's)."""
import gzip, hashlib, json, sys


def basis(vs):
    piv = {}
    for a in vs:
        while a:
            bit = a.bit_length() - 1
            if bit in piv: a ^= piv[bit]
            else: piv[bit] = a; break
    for k in sorted(piv):
        for j in piv:
            if j > k and piv[j] >> k & 1: piv[j] ^= piv[k]
    return [piv[k] for k in sorted(piv, reverse=True)]


def contained(a, b):
    return basis(list(a) + list(b)) == basis(list(b))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    mutant = None
    for a in sys.argv[1:]:
        if a.startswith('--mutant='): mutant = a.split('=', 1)[1]
    base_path, recipe_path, out_path = args
    raw = gzip.decompress(open(base_path, 'rb').read())
    assert hashlib.sha256(raw).hexdigest() == json.load(open(recipe_path))['base_sha256'], 'base word pin'
    w = json.loads(raw); r = json.load(open(recipe_path))
    for h in r['helpers']:
        key = str(h); old = basis(w['start_extra'][key]); new = basis(r['entrance_frames'][key])
        assert contained(new, old) and len(new) == len(old) - 1, ('expected a one-dimension lower entrance', h)
        w['start_extra'][key] = list(new)
    for sec, i, frame in r['gate_frames']:
        if mutant == 'skip_frames': break
        if sec == 'early_cleanup': w[sec][i][1] = list(frame)
        else: w[sec][i][-1] = list(frame)
    if mutant == 'wrong_entrance':
        h = str(r['helpers'][0]); sec, i, frame = r['gate_frames'][0]
        # a dimension-four space with a vector outside the first gate frame: replace the last basis vector by the
        # lowest standard basis vector not in that gate frame
        gate = basis(frame); U = basis(w['start_extra'][h])
        extra = next(1 << k for k in range(9) if not contained([1 << k], gate))
        w['start_extra'][h] = basis(U[:-1] + [extra])
    elif mutant == 'nonmonotone':
        sec, i, frame = r['gate_frames'][0]
        w[sec][i][-1] = basis(frame)[:-2]
    rep = dict(w['report'])
    rep['local_profile'] = r['expected_profile']
    rep['local_rank_mass'] = sum(int(k) * v for k, v in r['expected_profile'].items())
    rep['width_inventory'] = r['expected_width_inventory']
    w['report'] = rep
    data = json.dumps(w, separators=(',', ':')).encode()
    open(out_path, 'wb').write(gzip.compress(data, mtime=0))
    digest = hashlib.sha256(data).hexdigest()
    if mutant is None:
        assert digest == r['expect_sha256'], 'output word pin'
    print(json.dumps(dict(status='PASS_UNPROMO_APPLY' if mutant is None else 'MUTANT_' + mutant, sha256=digest,
                          helpers=len(r['helpers']), gate_frames=len(r['gate_frames']))))


if __name__ == '__main__':
    main()
