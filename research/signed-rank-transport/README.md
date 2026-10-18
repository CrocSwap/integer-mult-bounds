# Signed rank transport: what a cheaper register word must exploit

**Scalar-unitary mixing cannot save paid calls in the formal register model.**
A word with target ranks m_j needs at least their sum in paid cost when all
scalar register mixers are unitary, nonzero scalar multiples of unitaries,
or jointly equivalent to unitaries through the positive diagonal metrics
specified below. This permits arbitrary word length and noncommuting frames.
In particular, three rank-three streams cannot be completed in eight calls
within this subclass.

The underlying theorem is broader than Clifford frames: a symmetric
subadditive group metric suffices. A matrix-sparsity metric gives a corollary
for arbitrary invertible matrix frames, free monomial maps and two-sparse
butterflies. The argument is still a **formal group-algebra** argument;
it does not identify arbitrary concrete matrix dependencies with formal
coefficient cancellation.

For general nonunitary mixers, the result becomes a necessary resource
budget: an eight-call, three-stream rank-three solution needs accumulated
paid-row **negative coefficient weight at least 1/2**. At some paid prefix,
the product of a coefficient-row norm and the corresponding inverse-column
norm must be at least **9/8**. These are search diagnostics, not sufficient
conditions or new multiplication exponents.

**No new kappa or positive eight-call primitive is claimed.** The unrestricted
nonunitary search remains open. [PROOF.md](PROOF.md) proves the identities,
subclass obstruction and scope; [NOTICE.md](NOTICE.md) credits the framework,
source code and connection to Ailon's quasi-probability potentials.

## Exact reproduction

From the repository root, using standard-library Python 3.10 or later:

```sh
python3 -B -I -S research/signed-rank-transport/verify.py
```

Expected: `PASS_SIGNED_RANK_TRANSPORT`. An absolute script path works from an
unrelated directory. Run without `-O`; inherited assertions are required and
optimized execution is rejected. No solver, network or generated artifacts
are needed. MANIFEST.json pins package sources; ORIGINS.json pins the two
unchanged predecessor modules.

Run `python3 -B -S research/signed-rank-transport/validate.py` for an isolated
relocated replay and rejection of corrupt pins, false endpoint receipts,
wrong phase inverses, corrupted pairings and optimized execution.

The checker uses Q(omega), omega^2+omega+1=0, exactly. It propagates every
prefix and its actual inverse, checks scalar/free-step conservation and each
paid increment, and compares symbolic Clifford coefficients with independent
exact Gaussian-matrix multiplication. It also verifies both formal inverse
identities. Finite controls support the implementation; they are not the
proof of the unrestricted theorem.

Named controls include:

| Control | Exact outcome |
| --- | --- |
| Nine calls with unitary mixers | Valid full-rank endpoint, potential 9 |
| Eight-call deletion | Failed endpoint, potential 8 |
| Complex mixers with positive diagonal gauges | Same nine/eight-call distinction |
| Two calls with a nonorthogonal mixer | Potential 8/3; one call gains 5/3 using negative mass 1/3; endpoint fails |
| Five-call false positive | Potential exactly 9, but endpoint fails |
| Amplification trap | Correct full-rank coefficient mass 200/201 in the deficient column, but potential 8 and endpoint fails |

There are also 126 independent paid/free inverse controls, squared
coefficient-norm inequalities, and rejection of zero/negative/corrupt metrics
and a shear falsely declared unitary. VALIDATION.json records execution.

## Reusing the diagnostic

For a valid literal word in the inherited `paid`, `free`, `mix3` format,
`transport.audit(word, independent=True)` reports every paid increment,
its preceding negative mass, the squared local norm product and the exact
endpoint status. Use `field.E(a,b)` for a+b*omega scalar entries. The formal
group model in the finite implementation is specifically three-qubit,
three-register; the theorem itself allows arbitrary width and rank metric.

The potential is

    Phi(S) = Re sum_{i,j,g} rank(g) S_ij[g] (S^-1)_ji[g^-1].

Scalar mixing preserves it even for nonunitary matrices. A full-rank
three-stream endpoint requires Phi=9. A near-one coefficient-mass score can
be an amplification artifact; the explicit trap reproduces this failure.
Conversely Phi=9 alone is insufficient, as the five-call control shows.

`transport.check_metrics(matrices, metrics)` checks the sufficient family
obstruction B_k* D_{k+1} B_k=D_k, with strictly positive rational diagonal
metrics. Failure of that test leaves the family unclassified. An isolated
nonunitary-looking block can still belong to an excluded jointly gauged
family; an arbitrary invertible block cannot be called unitary.

Only this standalone package is added. The selected construction and
`upstream/` are unchanged. Its cold replay and the full repository suite are
not claimed as validation of this mathematical addition.
