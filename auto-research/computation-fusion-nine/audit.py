"""Budget-gated tests of two whole-stage replacements. No new bound.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'research/kappa-nine'))
from target_budget import audit as baseline_audit, encode, require, root_bounds


def moment(rows, m, W):
    """Optimistic moment permitting a full-width child for rejection only.

    A full-width child does NOT satisfy the inherited contraction theorem.
    Allowing it at cost (m/m)^tau=1 makes this a more generous budget screen.
    """
    require(m > 1 and W > 0, 'invalid parent')
    lower = upper = Q(0)
    for t, count in rows.items():
        require(type(t) is int and 0 < t <= m and count >= 0, 'invalid child')
        lo, hi = root_bounds(Q(m, t)) if t < m else (Q(1), Q(1))
        weight = Q(count*t, W*m)
        lower += weight*lo
        upper += weight*hi
    return lower, upper


def xor(*streams):
    result = set()
    for stream in streams:
        result.symmetric_difference_update(stream)
    return frozenset(result)


def reframe(stream, mask):
    """Formal F2 group algebra: D_S D_T = D_(S symmetric-difference T).

    An atom (input, mask) denotes an entire independent input stream after
    a coordinate partial interchange. Equality here is an operator identity.
    """
    return frozenset((source, address_mask ^ mask) for source, address_mask in stream)


def atom(name):
    return frozenset({(name, 0)})


def operator_controls():
    # a=b=2, ambient dimension 4. These are algebra controls, not a geometry search.
    U, E, full = 0b0001, 0b0101, 0b1111
    A, R = E ^ U, full ^ E
    x, y, z = atom('x'), atom('y'), atom('arbitrary_auxiliary')
    logical_x = reframe(x, U)
    first_source = reframe(logical_x, E)
    first_target = reframe(xor(y, logical_x), A)
    old_target_copy = reframe(y, full)
    B = reframe(first_target, R)
    final_B = xor(B, reframe(old_target_copy, U))
    require(final_B == reframe(x, full), 'single-shear readout identity')
    require(old_target_copy == reframe(y, full), 'first output preserved')
    require(xor(B, old_target_copy) != reframe(x, full), 'rank-one correction is essential')
    require(xor(B, reframe(y, U)) != reframe(x, full), 'full old-target transform is essential')
    packet_cases = []
    # Different representative common cuts; not an optimization or exhaustive search.
    for K in (0, U, E, full):
        left, right = reframe(logical_x, K), reframe(y, K)
        gate_left, gate_right = right, xor(left, right)
        out_A = reframe(gate_left, full ^ K)
        out_B = reframe(gate_right, full ^ U ^ K)
        corrected = xor(out_B, reframe(out_A, U))
        require(out_A == reframe(y, full) and corrected == reframe(x, full), 'packet identity')
        ranks = [(K ^ U).bit_count(), K.bit_count(),
                 (full ^ K).bit_count(), (full ^ U ^ K).bit_count()]
        require(sum(ranks) == 2*full.bit_count(), 'packet frame mass')
        packet_cases.append(dict(common_frame_mask=K, four_edge_ranks=ranks,
                                 correction_rank=1))
    return dict(status='exact formal stream identities, not a new finite network',
                single_shear_first_source=sorted(first_source),
                single_shear_target_before_correction=sorted(B),
                unchanged_arbitrary_auxiliary=sorted(z),
                packet_cases=packet_cases,
                omitted_correction_and_untransformed_copy_controls_rejected=True)


def transparent_word_control(omit_final_clear=False):
    """All seven independent bits; generic JLV=I invocation restoration.

    L(z)=(z0+z1,z1+z2,z2), V(x)=(x0,x1,0),
    J(z)=(z0+z1+z2,z1+z2). The actual large producer is inherited.
    """
    x = [1, 2]
    y = [4, 8]
    initial_z = z = [16, 32, 64]

    def L(v): return [v[0]^v[1], v[1]^v[2], v[2]]
    def Li(v): return [v[0]^v[1]^v[2], v[1]^v[2], v[2]]
    def J(v): return [v[0]^v[1]^v[2], v[1]^v[2]]
    def V(v): return [v[0]^x[0], v[1]^x[1], v[2]]
    for index, step in enumerate(('L', 'J', 'Li', 'V', 'L', 'J', 'Li', 'V')):
        if step == 'J':
            y = [a^b for a,b in zip(y,J(z))]
        elif step == 'L': z = L(z)
        elif step == 'Li': z = Li(z)
        elif not (omit_final_clear and index == 7): z = V(z)
    return dict(x=x, y=y, z=z, expected_x=[1,2], expected_y=[5,10],
                expected_z=initial_z, restored=z == initial_z)


def single_shear_budget(baseline):
    b = baseline['bit']
    p = json.loads((ROOT/'research/kappa-nine/baseline/profiles-23.json').read_text())
    N, m, a = b['N'], b['m'], p['h']
    B = N//p['v']*p['R']
    W = 2*N+B
    # Keep first invocation; delete the entire second bank and invocation.
    # Grant perfect macro batching and erase all fixed central losses.
    rows = Counter({m: N, m-a: N+B, a-1: 2*N, 1: N, a: B})
    total = sum(t*n for t,n in rows.items())
    require(total-W*m == (a-1)*N, 'single-shear rank excess')
    bounds = moment(rows,m,W)
    require(bounds[0] > 1, 'unexpected target headroom')
    # Even grant away the entire original-source growth/cleanup obligation.
    free_source = rows.copy()
    free_source[a-1] -= N
    require(sum(t*n for t,n in free_source.items()) == W*m, 'free-source mass')
    free_bounds = moment(free_source,m,W)
    require(free_bounds[0] > 1, 'free-source exclusion')
    return dict(status='REJECTED before construction search', N=N, m=m,
        first_axis=a, retained_auxiliaries=B, W=W, optimistic_child_profile=rows,
        rank_mass=total, capacity=W*m, rank_excess=(a-1)*N,
        moment_interval=bounds, source_growth_free_moment_interval=free_bounds,
        source_growth_free_rank_mass=W*m,
        assumptions=['first invocation and its data-growth cuts retained',
          'original target copied and fully interchanged for readout',
          'target final reframe and rank-one output correction paid',
          'all fixed central loss erased and every retained macro ideally batched',
          'full-width child allowed for screening, not certified as contracting'],
        construction_supplied=False)


def packet_budget(m):
    # Four mandatory edges at a common matrix K:
    # rank(K-P), rank(K), rank(I-K), rank(I-P-K).
    # Pairing the second/third gives >=m. Pairing first/fourth gives
    # >=rank(I-2P)=m. Grant cross-edge packing into full-width children.
    rows = Counter({m:2, 1:1})
    lower = moment(rows,m,2)
    require(lower[0] > 1, 'packet lower bound')
    # K=0 gives an actual commuting-frame inventory before optimistic packing.
    example = Counter({m:1,m-1:1,1:2})
    return dict(status='REJECTED before construction search', m=m, W_per_pair=2,
        universal_four_edge_rank_lower_bound=2*m,
        rank_with_endpoint_correction_lower_bound=2*m+1,
        pooled_optimistic_child_profile=rows, moment_lower_interval=lower,
        K_zero_profile=example, K_zero_moment_interval=moment(example,m,2),
        even_free_endpoint_correction_has_rank_mass_at_least_capacity=True,
        scope='Single common-frame two-register gate, retained source P/0 and sink I/(I-P), rank-one copied endpoint correction. Commuting idempotent cuts give legal partial-swap quotients. The matrix inequality also holds for arbitrary K in rank-difference bookkeeping; no claim about uncharged alternative address primitives.',
        construction_supplied=False)


def audit():
    pinned = baseline_audit()
    baseline = json.loads((ROOT/'research/kappa-nine/baseline/certificate.json').read_text())
    word = transparent_word_control()
    require(word['restored'] and word['y'] == word['expected_y'], 'dirty auxiliary control')
    require(not transparent_word_control(True)['restored'], 'missing cleanup control')
    sources = ['research/kappa-nine/target_budget.py',
               'research/kappa-nine/baseline/SOURCE.json',
               'research/architecture-nine/REPORT.md',
               'references/copied-centers/pr29/two-stage-16-note.tex',
               'notes/copied-centers-lemma.tex']
    return dict(status='TWO COMPUTATION-LEVEL FUSIONS SCREENED; NO NEW KAPPA',
        target=Q(1,512), necessary_bit_saving=Q(1,511),
        necessary_complex_saving_at_beta_1_over_20=Q(20,9709),
        pinned_baseline=pinned['baseline'],
        hypothetical_assembly_rows_replayed=len(pinned['hypothetical_joint_target']['all_47_slacks']),
        operator_controls=operator_controls(), dirty_auxiliary_control=word,
        retained_target=single_shear_budget(baseline),
        common_frame_packet=packet_budget(baseline['bit']['m']),
        designs_considered=2, construction_experiments=0,
        stop_reason='Both complete optimistic profiles fail; goal requires stopping before construction.',
        source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=audit()
    if args.output:
        args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print('PASS two complete budget rejections, formal stream identities, dirty restoration and pinned inputs')
    print('No construction search, improved exponent or publication')
