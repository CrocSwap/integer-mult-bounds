# Table-free integer encoding of local Frobenius automorphisms

Scoped constructive proof with exact finite corroboration.
This work was produced by Nick Petalas. Apache-2.0.
No new kappa or selected-frontier change is claimed.

For every supplied finite field L of characteristic p and every supplied height
list h, [PROOF.md](PROOF.md) constructs inverse integer rank/unrank maps for
all L-algebra automorphisms of

```text
B = L[x_1,...,x_r]/(x_i^(p^h_i)).
```

The output consists of the r generator images in the N-monomial basis.
The decoder constructs no N-by-N multiplication table and rejects no candidate
substitution. It uses O(sum_e r_e^5 + rN) field operations, with polynomial
integer bit cost, for r_e variables of each height e. A uniform integer index
therefore gives an exactly uniform automorphism. This assumes a uniform integer
source; it is not a fixed-length fair-bit sampling claim.

Nick Petalas's [#6578](https://github.com/CrocSwap/integer-mult-bounds/pull/6578)
supplies the local power-kernel, tangent and counting premises and asks the
uniform-sampling question. This package adds the explicit encoding, its inverse
and its resource proof. It does not replay that predecessor's scientific code
or recount its product and tensor orbits. Credit apoursh / #5663 and Ali
Romman / #5459 for the retained structural lineage. The ordered-basis and
positional-integer methods are classical; global literature priority is unclaimed.

## Evidence

The self-contained verifier checks the new maps directly:

- Every one of 5,039 indices in eight local contexts, including F4 and F9,
  round-trips and has distinct generator images. Literal sparse-polynomial
  substitution checks every decoded defining relation and an independently
  computed nonsingular full substitution map.
- All 404 ordered-basis indices in six GL contexts round-trip and pass a
  separate Leibniz determinant calculation.
- Thirty selected indices in six larger or differently ordered contexts
  round-trip, including dimensions eight, nine and sixteen. These are sampled
  indices, not exhaustive large-domain claims.
- Literal basis-product checks run at selected decoded maps. Sixteen controls
  reject invalid indices, forbidden coefficients, singular tangent blocks,
  malformed fields/heights and corrupted literal substitutions.

The verifier prints a generated JSON receipt bound to the current package-file
SHA256 hashes and writes no files. The universal assertion rests on the proof
and cited premises, rather than on these finite checks.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/frobenius-automorphism-codec/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/frobenius-automorphism-codec/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/frobenius-automorphism-codec
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/frobenius-automorphism-codec --check-source-history
```

Another CPython 3.12 path may replace the local path. Expected markers are
`PASS_FROBENIUS_AUTOMORPHISM_CODEC`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. Normal and optimized checks are registered.

## Scope and limitations

The `coverage-law-change` card explicitly changes to this algebraic side
result. It supplies varied changed-basis inputs for future tests; it does not
meet the card's productive-credit acceptance gate. No physical consumer,
native alignment, coefficient-preparation bill, dirty restoration or complete
signed invoice is supplied. All five selected framework assumptions remain.

The executable bounds q to 2,3,4,5,7,8,9, generator count to four, heights to
six and algebra dimension to 64. Its exhaustive contexts are smaller. The
written algorithm covers arbitrary supplied finite fields and finite height
lists. Coefficient-field discovery, semilinear maps, nonsplit products,
tensor-character transport and arbitrary-tensor recognition are separate.
Independent human and formal proof-kernel review are unclaimed. No selected
cold replay, predecessor scientific suite, Lean or Docker build is run.

[SOURCES.json](SOURCES.json) pins the older source text, catalogue and selected
record as provenance at `e54523517d0f03e58352e647c403a5af3e525a57`. There are
no external executable inputs. Live source-reference searches covered all
paginated open and closed PR titles/bodies and found no matching recent
source reuse. Main/merged term searches, active Discussions and reservations
were checked. Sparse local notes, arbitrary diffs and unpublished work remain
overlap limits. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19542478).

## Open next questions

1. Join the local codec to a supplied product decomposition and residue-field
   Galois actions. First specify component permutations, coefficient fields
   and generator-image data and prove a joint bijection. A supplied
   decomposition and semilinear arithmetic contract are prerequisites.
2. Identify a physical changed-basis consumer and price one encoded
   substitution, including coefficients and restoration. That complete paid
   contract is missing; uniform abstract sampling alone does not improve a
   supplier. Structured questions are in [TASK.json](TASK.json).

## Verifier constraints

All code is nonrecursive. Every loop ranges over a bounded field, at most
64 monomials, four generators, a fixed context list, bounded matrix entries
or the finite codec index interval stated above. Every function is below
60 physical lines. Invariants use explicit exceptions and remain enabled
under optimized Python. The finite field definitions are checked on all
their elements before the codecs run. The only local imports are the three
named package modules; no network or subprocess runs occur.

Power of Ten rule 3 deviation: CPython allocates managed integers and
containers during execution. The stated domain guards bound each polynomial,
matrix and index. The exhaustive verifier retains at most 2,880 decoded image
tuples in its uniqueness set; the codec itself retains no census or full
algebra table. Rule 9 deviation: Python field methods, iterator operations
and the sixteen fixed rejection callbacks use runtime dispatch. Their
targets are package-local and bounded. Warning-strict normal and optimized
checks and AST/function-size inspection cover the touched implementation.
