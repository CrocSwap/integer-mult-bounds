"""apply_mixed.py BASE-WORD RECIPE OUT-WORD [--mutant NAME]
Apply one provider recipe of the two-provider package to the seven-slot k8 word: the listed entering helpers get the recorded
dimension-four entrance frames (one dimension below, and inside, their promoted entrances), the listed low-ended
helpers get the recorded seven-dimensional end frames (one dimension below, and inside, their ends), the listed gate
frames get the recorded frames, the scalar program is unchanged, and the report's local profile, rank mass and width
inventory are set to the recipe's expected values (the native stage recomputes and checks them). Standard library
only; the output is pinned by content SHA256.
Mutants (must be rejected downstream): 'wrong_entrance' puts one restored entrance outside its first gate's frame;
'wrong_end' gives one deepened helper a different seven-dimensional subspace of its old end that leaves out part of
its final gate frame; 'skip_frames' keeps the old gate frames; 'stale_profile' keeps the base word's report."""
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
    r = json.load(open(recipe_path))
    assert hashlib.sha256(raw).hexdigest() == r['base_sha256'], 'base word pin'
    w = json.loads(raw)
    for h in r['entrance_helpers']:
        key = str(h); old = basis(w['start_extra'][key]); new = basis(r['entrance_frames'][key])
        assert contained(new, old) and len(new) == len(old) - 1 == 4, ('expected a one-dimension lower entrance', h)
        w['start_extra'][key] = list(new)
    for q in r['end_helpers']:
        key = str(q); old = basis(w['helper_final'][key]); new = basis(r['end_frames'][key])
        assert contained(new, old) and len(new) == len(old) - 1 == 7, ('expected a one-dimension lower end', q)
        w['helper_final'][key] = list(new)
    for sec, i, frame in r['gate_frames']:
        if mutant == 'skip_frames': break
        if sec == 'early_cleanup': w[sec][i][1] = list(frame)
        else: w[sec][i][-1] = list(frame)
    if mutant == 'wrong_entrance':
        h = str(r['mutant_entrance_helper'])
        # the helper's first gate (A then B) after the recipe; a dimension-four space with a vector outside its frame
        first = next(e for e in w['A'] + w['B'] if int(h) in (e[1:3] if e[0] == 'add' else e[1:2]))
        gate = basis(first[-1]); U = basis(w['start_extra'][h]); extra = next(1 << k for k in range(9) if not contained([1 << k], gate))
        w['start_extra'][h] = basis(U[:-1] + [extra])
    elif mutant == 'wrong_end':
        q = str(r['mutant_end_helper']); old = basis(json.loads(raw)['helper_final'][q]); new = basis(r['end_frames'][q])
        e = next(x for x in old if not contained([x], new)); F = basis(new[1:] + [e])
        assert len(F) == 7 and F != new and not contained([new[0]], F)
        w['helper_final'][q] = list(F)
    rep = dict(w['report'])
    if mutant != 'stale_profile':
        rep['local_profile'] = r['expected_profile']
        rep['local_rank_mass'] = sum(int(k) * v for k, v in r['expected_profile'].items())
        rep['width_inventory'] = r['expected_width_inventory']
    w['report'] = rep
    data = json.dumps(w, separators=(',', ':')).encode()
    open(out_path, 'wb').write(gzip.compress(data, mtime=0))
    digest = hashlib.sha256(data).hexdigest()
    if mutant is None:
        assert digest == r['expect_sha256'], 'output word pin'
    print(json.dumps(dict(status='PASS_MIXED_APPLY' if mutant is None else 'MUTANT_' + mutant, sha256=digest,
                          entrances=len(r['entrance_helpers']), ends=len(r['end_helpers']), gate_frames=len(r['gate_frames']))))


if __name__ == '__main__':
    main()
