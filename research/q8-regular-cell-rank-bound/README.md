# Rank floor for Q8's regular data action

**Conditional linear-circuit bound; no supplier admission, caller mapping, or new κ.**
For `r >= 1` dirty roles, payload width `B >= 1`, a rank-one idempotent coupling
`N = u v^T` over `F_2`, and the regular left action of `Q8` on eight address
blocks, the address-changing part has rank `4B` for the central label `-1` and
`6B` for each order-four label. Therefore a factorization into rank-one
bit-cell updates needs at least `4B` or `6B` updates, respectively. The lower
bound is independent of `r` and of the particular legal `u,v`.

This is a conditional cost statement for a specific primitive alphabet: each
paid instruction changes the full binary state by a matrix of rank at most one.
It is not a lower bound on whole-array XORs, block swaps, arbitrary routing,
selected multiplication calls, or runtime. The Q8 compiler in the predecessor
package uses wider whole-array instructions and supplies an upper invoice in
that different model. Address-label affine ranks and full data-cell displacement
ranks are different quantities; in particular, do not equate the existing
`1/2` affine-label ranks with this `4B/6B` data-cell rank.

## Proof and finite corroboration

The all-parameter proof is in [PROOF.md](PROOF.md). It covers every finite
`r,B >= 1`, every rank-one idempotent coupling (`v^T u = 1`), and all eight
Q8 labels. The verifier independently builds the quaternion multiplication
table and checks the tensor-rank identity on 560 finite instances (`r <= 3`,
`B <= 2`) plus 256 rank-subadditivity pairs. Those computations corroborate the
written proof; they do not supply its universal quantifiers.

## Caller and selected-source boundary

The selected source manifest at base `463113d675af7410ac91d53a4fed51ec6494eb9a`
lists 13 source package roots. A targeted search of their top-level README,
TASK, and frontier documents found no named Q8 regular-action caller or
eight-address payload contract; the exact inventory and search are in
[CALLER-AUDIT.md](CALLER-AUDIT.md). This is a bounded source inventory, not proof
that no implementation or caller exists elsewhere. Open PR #2235 supplies a
separate multitape toolkit and quadratic multiplier; its own description says
the serialized-input, alphabet, and cleanup bridges for a generic caller are
still missing. It does not bind this Q8 action to the selected supplier.

The current selected result remains the maintainer-reviewed conditional finite
construction at `κ = 836330098538459/500000000000000000`, under its inherited
all-size/compiler, common-label/mutable-source, hosting, precision/tape,
analytic and bit H1-H5 assumptions. This package changes neither that record nor
its source.

## Reproduce

From the repository root, using Python 3.12 or newer:

```sh
python3 -I -B research/q8-regular-cell-rank-bound/verify.py
python3 -I -B research/q8-regular-cell-rank-bound/test_verify.py
python3 scripts/research_package.py --package research/q8-regular-cell-rank-bound
```

The first command checks the declared source hashes, typed group construction,
all small tensor fixtures, and its failure controls. The package runner checks
base/blob provenance and the registered replay manifest. These are local
replays; no hosted CI, Lean formalization, independent human review, or selected
cold replay is claimed.

`RESULT.json` is the committed stdout receipt from `verify.py`; regenerate it
with the first command and compare its JSON values. The registered package
runner is pinned to Python 3.12. This host has CPython 3.14.8 but no 3.12
executable, so only its version-independent `--check-only` pass is available
locally; the two verifier commands were run directly under 3.14.8.

## Open next questions

- **Caller binding:** Can a named selected-source caller provide eight contiguous
  address blocks with legal dirty lifetimes? First bind its exact role/address
  map, payload width, chronological cuts, and direct alternative, then price
  transport and hosting. The missing item is an actual caller contract.
- **Primitive mapping:** Does any proposed native call satisfy the rank-one
  bit-cell update hypothesis used here? First write its full binary state map
  and prove its displacement rank and cost. The selected supplier's whole-call
  child model is wider and is not covered by this theorem.

## Credit

Prepared by OpenAI Codex with substantial AI assistance in scope selection,
proof, implementation, verification, and writing. No independent human review
is claimed. Credit Arham Tahir / PR #3137 for the Q8 finite-array compiler and
its exact whole-array invoice, and Gareth Davidson / PR #1333 for the retained
affine-rank method. New work is Apache-2.0.
