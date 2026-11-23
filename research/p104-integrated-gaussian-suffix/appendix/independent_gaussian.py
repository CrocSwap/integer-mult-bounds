"""Independent 192-bit rational enclosure and failure controls for the debit."""

from fractions import Fraction as Q
from math import gcd


def floor(q):
    return q.numerator // q.denominator


def ceil(q):
    return -(-q.numerator // q.denominator)


def verify(recipe, powers):
    """Price from the installed paid histogram and cells, not the receipt."""
    c, lower, scale = recipe.trial, 1874, 263772
    t, delta = 1 - c, Q(1, 2**128)
    debit = Q(130699669, 2**30)
    grid = 1 << 160
    psi_lo = psi_hi = numerator_lo = numerator_hi = 0
    for (raw_r, raw_k), share in recipe.cells.items():
        r, k = Q(raw_r), Q(raw_k)
        assert 0 < r and 5 * r <= 4 * k and share > 0
        weight = recipe.paid.histogram[raw_r] * share
        edge_lo, edge_hi = powers(k / r, c)
        lo = weight * r * (edge_lo - 1) / c
        hi = weight * r * (edge_hi - 1) / c
        psi_lo += floor(lo * grid)
        psi_hi += ceil(hi * grid)
        rlo, rhi = powers(r / k, t)
        point = 10 * k - 8 * r - gcd(int(2 * r), int(2 * k))
        average = 9 * (k-r) + t * r*r / (2*k*lower)
        assert 0 < average < point
        numerator_lo += floor(weight * rlo * average * grid)
        numerator_hi += ceil(weight * rhi * average * grid)
    psi_lo, psi_hi = Q(psi_lo, grid), Q(psi_hi, grid)
    numerator_lo, numerator_hi = Q(numerator_lo, grid), Q(numerator_hi, grid)
    assert psi_lo > Q('926899828.8291') and psi_lo <= psi_hi
    low_fringe = numerator_lo / (t * psi_hi)
    high_fringe = numerator_hi / (t * psi_lo)
    assert Q('4.550681') < low_fringe < high_fringe < Q('4.550682')
    base_lo, base_hi = powers(scale * lower, c)
    coefficient = ((1+delta) * (1+Q(4*258, scale)) / (1-delta)**4)
    factor_lo = coefficient * base_lo * (1+low_fringe/lower+delta)
    factor_hi = coefficient * base_hi * (1+high_fringe/lower+delta)
    threshold_lo = powers(2, debit)[0]
    previous_tick_hi = powers(2, debit-Q(1, 2**30))[1]
    assert threshold_lo - factor_hi > Q(2, 10**10)
    # This rejects one extra debit tick using a lower bound on the SAME
    # complete accounting expression; it is not a lower bound on physical work.
    assert factor_lo - previous_tick_hi > Q(4, 10**10)
    old_axes = sum(Q(k)*n for k,n in recipe.targets.histogram.items())
    coarse = 10 * old_axes / (t * psi_hi)
    old_factor_lower = coefficient * base_lo * (1+coarse/lower+delta)
    assert old_factor_lower > powers(2, debit)[1]

    # Show that the averaged estimate is not a valid pointwise cap.
    # Every selected edge is occupied, has positive interval length and is
    # strictly descending; the production calendar's grid makes its grant
    # positive at H>=1024 (checked separately below).
    witness = None
    for (raw_r, raw_k), share in recipe.cells.items():
        r, k = Q(raw_r), Q(raw_k)
        for d in range(lower, lower+40, 2):
            start = 2 * floor(Q(d)*k/(2*r))
            for e in range(start, start+12, 2):
                left, right = max(Q(e), Q(d)*k/r), min(Q(e+2), Q(d+2)*k/r)
                suffix = r*(e-8)-k*(d-8)
                average = 9*(k-r) + t*r*r/(2*k*lower)
                if left < right and suffix > average:
                    assert 0 <= suffix < 10*k-8*r
                    assert e > d and share > 0
                    witness = (r, k, e, d, suffix, left, right)
                    break
            if witness:
                break
        if witness:
            break
    assert witness is not None
    # Replay the actual downward-rounded integral and one real per-owner
    # typed share at the smallest installed Gaussian rank, not a proxy mean.
    from transport import Measure
    r, k, e, d, _, left, right = witness
    typed = next((a, b, share) for (a, rr, b, kk), share in recipe.typed_cells().items()
                 if rr == r and kk == k and share > 0)
    a, b, typed_share = typed
    per_owner = typed_share / recipe.targets.variants[b].histogram[k]
    M = 2**1024
    m = Measure(t, M**6, max(256, 64*M.bit_length()))
    grant = recipe.types()[a].multiplicity * m.mass(left, right)[0] * per_owner
    assert floor(grant) > 0 and e < 2*(M//(1724*306))
    def level(band):
        value, result = Q(lower), 0
        while value*Q(6, 5) <= band:
            value *= Q(6, 5)
            result += 1
        return result
    assert level(d) < level(e)
    print('PASS_INDEPENDENT_GAUSSIAN_ENVELOPE',
          'debit', str(debit), 'interior_edges', len(recipe.cells),
          'previous_debit_tick_rejected', True,
          'coarse_suffix_budget_rejected', True,
          'averaged_bound_not_pointwise_witness', tuple(map(str, witness)),
          'typed_grant_bits', floor(grant).bit_length())
    return dict(debit=str(debit), lower_factor=str(factor_lo), upper_factor=str(factor_hi),
                lower_fringe=str(low_fringe), upper_fringe=str(high_fringe),
                pointwise_witness=tuple(map(str,witness)))
