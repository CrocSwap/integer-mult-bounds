# Exact block-three hook spectrum and an operator-error gap

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

The block-three hook leakage has squared singular values
`0:56, 1/8:48, 5/8:112, 1:64`, where each suffix is a multiplicity.
This new finite spectral certificate strengthens the use of Jacob Alan
Sussman's exact kept-subspace obstruction to approximate completed outputs.
In its linear, columnwise model, joint operator error strictly below
`1/sqrt(8)` still requires at least `ceil(14W/5)` paid calls for W targets.
Five targets with thirteen calls therefore have error at least `1/sqrt(8)`.

The claim type is a **scoped proof**, supported by an exact finite spectral
certificate. It is not a new kappa, supplier construction, optimal
approximate circuit, or complete multiplication theorem.

## Result and exact evidence

At digit width five let `H=V tensor exterior^4 V`, `V=C^8`, and let N be
the 280-dimensional coordinate hook `span{(x,T): x in T, |T|=4}`.
For target `K=C_(e_0) C_(e_1) C_(e_2)`, set
`L=(I-P_N) (K tensor exterior^4 K)|N`.
The [proof](PROOF.md) gives the exact matrix formula and the argument
for arbitrary W, with zero scratch and arbitrary complex register mixing.
Any program allowing arbitrary dirty scratch is also subject to this bound
on its zero-scratch restriction, if that restriction obeys the stated error
contract.

The verifier constructs the Walsh-equivalent leakage as `D/sqrt(32768)`,
then forms the integer Gram matrix `A=D^t D/4096`. It proves

```text
A(A-I)(A-5I)(A-8I) = 0
tr(A^0), tr(A^1), tr(A^2), tr(A^3) = 280, 1120, 6944, 46816
```

These identities determine every spectral multiplicity exactly. No
floating eigensolver, rank census from a predecessor, or external library
is used by the registered verifier. Its output includes SHA256 hashes of
all six package files, computed at execution time.

More generally, the squared joint operator error is bounded below by
`1`, `5/8`, `1/8`, or `0` as the rank budget `80s` lies respectively in
`[0,64W)`, `[64W,176W)`, `[176W,224W)`, or `[224W,infinity)`.
These values are exact for the unrestricted rank approximation relaxation.
Their attainment by legal circuits is not claimed.

## Reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/block3-hook-error-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/block3-hook-error-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/block3-hook-error-spectrum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/block3-hook-error-spectrum --check-source-history
```

Another CPython 3.12 executable may replace the local interpreter path.
Expected verifier status is `PASS_BLOCK3_HOOK_ERROR_SPECTRUM`, with moments
`[280,1120,6944,46816]` and six rejected controls. The controls include two
changed Gram diagonals, four invalid rank inputs, every rank endpoint for
W=1,...,20, and the five-target thirteen/fourteen-call boundary.
All replay output belongs outside the checkout. The verifier writes no files.

## Scope and predecessor credit

Credit Jacob Alan Sussman for the hook and kept-subspace call cap in
[PR #4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628), exact
head `ee4fd87f064017c23e5a86fc1dcfe0a5237caed3`; eumemic for the earlier
kept-subspace certificate method; and Swapnil Jain for the retained P1/P2
lineage. Lee-phys's retained
[two-image prefix](../complex-two-image-hook-prefix/README.md), PR #4688,
records the same width-five hook conventions. No predecessor computation
is replayed here. The new contribution is the exact spectrum and its
quantitative operator-error consequence.

The external #4628 theorem is a cited mathematical premise. Its exact
public source URL is in the proof; this package's source-history preflight
does not certify that external theorem. SOURCES.json pins the main-tree
convention reference as provenance only. The verifier has no external inputs.

The independent-moment card is changed from auditing a paid ledger to a new
approximation obstruction for a small complex unit. This is a side result
about tolerance in a fixed model. It does not affect the selected result.
The complete new family budget is only the rank bound `80s`; it is not a
physical cost invoice. Native lowering, restoration cost, routing, compiler,
stock and finite-precision execution remain outside this package. No family
implementation expansion is proposed.

The norm is the joint operator norm on all designated data inputs and
completed outputs, at width five. Separate blockwise error bounds and
nonlinear rounding require new arguments. No Lean build, physical replay
or complete multiplication-theorem audit is claimed.

## Open next questions

The structured questions are in [TASK.json](TASK.json).

- Can the best error achievable by actual paid-call circuits reach any of
  the rank-relaxation thresholds? Begin with the five-target thirteen-call
  case and a literal linear program; the spectrum alone gives no circuit.
- Can the leakage spectrum be derived in a short symbolic form for general
  hook dimensions? Start with the signed translation symmetries of this
  280-square Gram matrix. No general-dimension formula is claimed here.

Canonical investigation and advance claim:
[handoff comment 19141367](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19141367).
