# Coordinate-CNOT label saturation with arbitrary dirty workspace

**Scoped written theorem; no new kappa.** For `t` coordinate-SWAP targets in
the formal `F2[GL_2(F2)]` register model, exactly `t` calls of one coordinate-CNOT
label force at least `2t` calls of the other. This holds for any finite number
of restored dirty registers and free scalar mixing. At the saturated `3t`
boundary, the normalized paid factors do not couple the dirty complement.

The [proof](PROOF.md) gives an analytic alternative to the finite step in
Cinna Davis's [PR1541](https://github.com/CrocSwap/integer-mult-bounds/pull/1541)
three-swap theorem, and strengthens Aaron Wang's
[PR1705](https://github.com/CrocSwap/integer-mult-bounds/pull/1705) four-swap
boundary:

| Target | Established consequence |
| --- | --- |
| Three swaps, arbitrary finite dirty workspace | Exactly nine calls; predecessor result now has a short analytic proof |
| Four swaps, arbitrary finite dirty workspace | Minimum is **ten or twelve**; a ten-call word must use **five of each label** |
| Remaining ten-call case | PR1541's credited compression reduces it to at most six roles: four active and two dirty |

There is **no ten-call construction or exclusion** here. PR1705 excluded
two, four and six calls at exactly four registers and left `{8,10,12}`.
The new saturation lemma excludes eight and the unbalanced ten-call counts,
without a larger state census. The earlier three-swap result retains its
predecessors' priority.

## Exact model and complete optimistic bill

The only paid address labels are
`a=[[1,1],[0,1]]` and `b=[[1,0],[1,1]]`; `s=aba=bab` is the swap.
Each unit call is `I+([g]+1)uv^T`, with binary `v^T u=1`. Free scalar
`GL_r(F2)` mixing is normalized by augmentation. The endpoint is
`diag([s],...,[s],1,...,1)` as a **full formal group-algebra matrix**.
Every dirty input has its prescribed output; every undo call is charged.
No other address maps, copies, erasures or clean allocation are allowed.

The direct upper bill is `3t`, with no extra roles or scalar preparation.
Scalar work and workspace are favorably free in the lower-bound model.
An actual supplier would still need its physical/compiler, hosting,
precision/tape and analytic costs. This replaces the rational abelian
starting model with a specified nonabelian binary alphabet; it does not
reduce rational frame entries modulo two.

## Why the new inequality holds

If there are only `t` a-calls, their image vectors form a basis of the active
space. In that basis, each active top block row changes exactly once, from
its input row to its output row. Its two block halves therefore always sum
to the same row. The b-call projectors must sum to zero.

The full sign-quotient matrix equation then forces every a-projector to be
a coordinate projector. At each a-call, its bottom row forces an active
coordinate covector into the span of the b covectors. The b image vectors
already span the active space. Writing their zero sum as `UV=0` gives
`n_b >= rank(U)+rank(V) >= 2t`.

The chronological covector step matters: four legal rank-one projectors
can sum to zero with image rank three but covector rank one. This explicit
near miss rejects a tempting one-span-only argument. The full sign equation
also cannot be replaced by its parity consequence.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/coordinate-cnot-label-saturation
```

Or run the three checks directly:

```sh
python3.12 -I -B research/coordinate-cnot-label-saturation/verify.py
python3.12 -I -B research/coordinate-cnot-label-saturation/independent.py
python3.12 -I -O -B research/coordinate-cnot-label-saturation/test_package.py
```

Expected markers are `PASS_COORDINATE_CNOT_LABEL_SATURATION`,
`PASS_INDEPENDENT_LABEL_SATURATION`, and five passing package test groups.
`verify.py --write` explicitly regenerates the deterministic RESULT.json;
normal replay is read-only. There is no SAT solver, heuristic pruning,
floating-point acceptance or dependency installation.

The two implementations share the stated mathematical model and receipt
format but no executable code. The primary engine multiplies formal
coefficients using actual binary address matrices. The second constructs
permutations and their faithful regular operators, enumerating scalar
projectors separately. Both were written by one Codex agent in this session.

## Finite evidence and failure controls

The written argument establishes the universal statement. The following
bounded computations corroborate it and test the implementation:

* Complete exact-length, label-count-indexed formal censuses through five
  calls on one register and six on two. The two-register layer sizes are
  `1,12,82,496,2640,13552,58408`. These are **not** shortest-distance layer
  sizes: the same matrix at different label counts is deliberately retained.
  Both engines independently obtain the same canonical complete-set hashes.
* A complete `3+3` join enumerates all **1,296 literal six-call two-swap
  words**, with a-count histogram `{2:324,3:648,4:324}`. The primary checker
  verifies the normalization, every relevant chronological cut, both ranks
  and equality-case workspace restriction on all **648 saturated words**.
  The independent engine agrees on the complete sorted-word digest.
* Twenty-five positive words cover `t=1..5`, both saturated labels, changed
  active bases, and zero or one dirty extra. Five deliberately touch and
  restore that extra using two additional paid calls. Full faithful forward
  and reverse replay covers **1,080 columns** and rejects **235 individual
  paid-call omissions**.
* Fifteen primary controls cover six omissions, dirty leakage, a missing
  target, changed/expanded labels, an illegal scalar projector, Boolean
  input, the one-span and trace-only near misses, and a natural-representation
  alias. The last is a nonzero formal off-diagonal perturbation with zero
  natural image; it is not asserted to be a cheaper word.
* Five package test groups exercise optimized read-only relocation, changed
  and missing source bytes, false theorem/cut/count receipts, both-engine
  word/census/attainer corruption, duplicate/nonfinite JSON and missing input
  inventory. Integer receipt fields reject Boolean and floating aliases.

The independent operator engine corroborates finite evidence. It does not
formalize the universal proof or independently derive its ten-call bound.

## Provenance, overlap and scope

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Selected record SHA256:
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Task `bit-new-register-model`, refined to a target-specific relaxation;
OS chooser nonce `8e7454be62cc38c3ccc7edd6bd6d2bc2`. The alternative
helper-contract card was not chosen because its immediate interface question
is already covered by PR1194/1311 and subsequent feedback work.

[TASK.json](TASK.json) records exact predecessor heads, the scope and overlap
coverage. [SOURCES.json](SOURCES.json) pins the original task/selection and the
unchanged PR1414 proof text. The later PR1541/1705 heads are contextual sources;
no pending implementation or certificate is imported. Their credited
compression argument is restated in PROOF.md.

[Discussion #1715](https://github.com/CrocSwap/integer-mult-bounds/discussions/1715)
holds the claim and handoff. The overlap search covers open PR bodies, local
top-level package notes and the ledger, plus Discussion bodies/comments.
It excludes arbitrary diffs/nested code and is not a novelty certificate.

Selected-source binding and package verification are separate from complete
selected cold replay. No full supplier replay, new recursive profile,
physical adoption, Lean proof, independent human review, measured runtime
gain or stronger multiplication exponent is claimed. Existing frozen sources
and the selected frontier are unchanged.

## Open next questions

**Does the balanced ten-call four-swap word exist?** It is the sole remaining
potential saving below twelve in this alphabet. First encode all `5+5` label
patterns with at most six roles, using the credited compression, a full
formal endpoint and a proof-producing solver. The blocker is the remaining
noncommuting projector interaction; neither this theorem nor the small
censuses decide it. A valid word would still need all physical supplier costs.
This question is also structured in TASK.json.

## Credit and license

Credit **commdata2338 / PR1414 and PR1491** for the coordinate-CNOT model,
sign quotient and two/three-swap results; **Gareth Davidson / PR1333** for
scalar normalization and the restricted-alphabet question; **Cinna Davis /
PR1541** for the arbitrary-workspace three-swap theorem and role compression;
and **Aaron Wang / PR1705** for the four-register boundary and explicit
unfinished search. Eumemic / PR288, Ali Romman / PR468 and David Govea / PR720
retain the surrounding rational/register-model credit.

Prepared for **Ross Richardson**, with substantial **OpenAI Codex assistance**
in reasoning, implementation, verification and writing. One agent; no
independent human or proof-assistant review. New work is Apache-2.0.
