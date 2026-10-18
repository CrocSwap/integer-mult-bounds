"""apply_deepen.py BASE-WORD RECIPE OUT-WORD [--mutant NAME]
Apply an explicit end-deepening recipe: the listed low-ended helpers get the recorded seven-dimensional end frames (each
one dimension below, and inside, the helper's current end), the listed gate frames get the recorded frames, the scalar
program is unchanged, and the report's local profile, rank mass and width inventory are set to the recipe's expected
values (the native stage recomputes and checks them). Standard library only; the output is pinned by content SHA256.
Mutants (must be rejected downstream): 'wrong_end' gives one helper a different seven-dimensional subspace of its old
end, one that leaves out a vector of its final gate frame; 'skip_frames' keeps the old gate frames (the final tail gate
frames are eight-dimensional and no longer fit under the new ends); 'stale_profile' keeps the base word's report."""
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
    for h in r['helpers']:
        key = str(h); old = basis(w['helper_final'][key]); new = basis(r['end_frames'][key])
        assert contained(new, old) and len(new) == len(old) - 1 == 7, ('expected a one-dimension lower end', h)
        w['helper_final'][key] = list(new)
    for sec, i, frame in r['gate_frames']:
        if mutant == 'skip_frames': break
        if sec == 'early_cleanup': w[sec][i][1] = list(frame)
        else: w[sec][i][-1] = list(frame)
    if mutant == 'wrong_end':
        h = str(r['mutant_helper']); old = basis(json.loads(raw)['helper_final'][h]); new = basis(r['end_frames'][h])
        # old = new + <e>; F = span(new without one basis vector u, plus e) is another hyperplane of old, and u (a vector
        # of the helper's final gate frame, which equals new) lies outside F
        e = next(x for x in old if not contained([x], new))
        F = basis(new[1:] + [e])
        assert len(F) == 7 and F != new and not contained([new[0]], F)
        w['helper_final'][h] = list(F)
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
    print(json.dumps(dict(status='PASS_DEEPEN_APPLY' if mutant is None else 'MUTANT_' + mutant, sha256=digest,
                          helpers=len(r['helpers']), gate_frames=len(r['gate_frames']))))


if __name__ == '__main__':
    main()
