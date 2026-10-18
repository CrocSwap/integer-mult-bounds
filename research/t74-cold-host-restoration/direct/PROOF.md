# Direct cold-host restoration: finite domain and certificate

The input is 184 literal hosted words: 92 distinct hostee/host pairs from the
retained J archive, in both orientations. Ninety-four words were retained in the
archive; 90 missing extra-orientation variants were rebuilt. A second filename
for `b-473_277` is a duplicate payload and is not a 185th case. `SOURCE-PINS.json`
binds the original gzip files and canonical payloads. The two original parent
words are included, and `verify_derivation` checks every literal hosting edit,
fixed interface, invertible warp, pulled-back correction, and derived cleanup.
Changed optimal gate frames are checked for feasibility and their actual invoice;
optimality is unnecessary for this obstruction.

The exact input commit is `dfbc5ba121d5d23381393f178be8d4ba25ebfa4d` of
`research/t74-r10-hosting-leads`, based on the PR #2802 construction. Source
notices and the complete lineage are retained by the enclosing package.
`USED-inverse_prelude.py.txt` records the exact operator-repair source used by the
original search. The independent checker imports none of that source.

## Recovery and frame-floor exclusion

Immediately after the new host warp, let `z` be the host's value. We maintain an
exact rational expression for `z` in the current registers. On a forward gate
`x += a*y`, its coefficient on `y` decreases by `a` times its coefficient on `x`.
A scale divides the coefficient; a warp right-composes the corresponding inverse
operator. This is inverse substitution, not floating-point linear algebra.
All 131,788 sampled expressions are scalar. They cover every B and restore slot
after the hosted value's final read, including the end of both sections.

Every gate shares a frame between its registers. Frames are monotone between
fixed warp interfaces. The smallest possible frame at a gate is therefore the
join of its incoming forced subspaces and any equality pin imposed there. At
an A/B cut or warp, the preceding gate must attain the prescribed frame: no
unrecorded paid climb is allowed. These joins give exact necessary lower floors
for every refitting of the unchanged word. They are implemented independently
in `engine.Model`, using only Gaussian elimination in GF(2)^9.

To apply a direct scalar recovery to one host, its final frame must contain the
join of the forced frames of all registers in that expression. All sampled joins
have rank at least eight. Thus no sampled direct recovery can restore the host
at rank seven or lower. This conclusion concerns the current-register recovery
expression; it does not exclude a new scalar basis or a changed word.

## Rank-eight contiguous recovery

A rank-eight join determines its candidate rank-eight end uniquely. There are
35,068 rank-eight slots. Slots are identified only when the recovery expression,
its frame join, and the immediately preceding and following gate/warp for every
participating register agree. Every skipped operation then commutes with the
inserted recovery block, both algebraically and in the frame dependency graph.
This gives 720 classes. All 8,208 permutations of their three or four additions
are checked. All host coefficients equal one, so no untested scale is needed.

The scanner samples before warps at the next B boundary, whereas the insertion
routine uses the position after those warps. The verifier explicitly checks all
115,780 B sample boundaries: no warp at any such boundary touches a participating
register. The two conventions therefore coincide in this domain.

An inverse warp at the zero-frame entrance and identity initial corrections
cancel the otherwise surviving `K(x_host)`. This restores the intended own-input
algebraic contract when the scalar undo succeeds. It adds only a zero-to-zero
frame event. The checker includes that event in each candidate lattice. The
operator lane supplies a separately audited full-end fixture; the direct checker
also retains a positive full-end frame fixture to avoid vacuous rejection.

For every one of the 8,208 candidates, forward propagation forces a vector
outside a target's fixed port-hyperplane end. The replay emits a target, its
forced lower basis, end basis, and a missing vector. The verifier separately
checks that the missing vector has odd dot product with the target port. These
are exact incompatibility witnesses, not optimizer failures. All 8,208 candidates
have such a target-end witness. Merely increasing other helpers' terminal frames
cannot remove it: helper ends supply upper constraints, and the independently
propagated lower target frames do not use those upper constraints.

## Replay and limits

Run from any directory, with Python 3.12+ and no installed packages:

```sh
python3 -I -S -B direct/verify.py --workers 4
```

`--workers` accepts 1 through 24. `--quick` checks six representative words
(3,856 slots, 16 classes, 204 orders), while authenticating and deriving all 184
inputs. The default checks the complete finite domain. `--output` optionally
writes a receipt outside the verifier directory; the source package is never
modified. The final complete replay, including all 184 provenance derivations, took
42.60 seconds with four workers; an earlier full replay took 22.23 seconds
with 24 workers. `RESULT.json` binds the final executed source and input hashes.

Positive controls cover the known scalar expression, its rank-eight frame
floor, and a feasible full-end recovery. Negative controls reject a rank-eight
end for that full-tail fixture, a flipped source write, an incompatible warp
frame, and a changed port frame.

This proves a scoped obstruction for contiguous direct recovery with the fixed
scalar words and interfaces. It does not cover staged recovery at distinct
times, new scalar bases, new warp interfaces, precomputed combinations, changed
target/consumer contracts, or arbitrary hosting. It is not a new kappa bound or
a formal proof of the complete multiplication theorem.
