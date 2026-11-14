# Implement the complete old-format to packed native bridge with literal strided transport and paid restoration

**Scoped all-size implementation lemma. No new kappa.** This package closes
the old-codec/strided-packing interface specifically left open by #7578,
at its exact head `e9b6d75397e3553af77bab81d5816e4b8708a501`. The current
selected #7000 bound remains conditional on all five global assumptions.

An input-independent graph with **6,003 locations and 43 fixed tapes**
converts the exact old twenty-three-field descriptor and three-bit-coded,
LSB-first complete numerical field to the six-Gamma packed native ABI and
back. It physically infers component width and coefficient multiplicity,
gathers **all 9f selected bits**, preserves every spectator/row/coefficient,
and prepares the entire old-format return before committing to its original
owner. Every private body and head is restored on successful return.

For old payload V_old and old header E, the complete bridge satisfies

```
T <= 2^20 ((9f+1)V_old + E + 1),
K_after <= K_entry + 64(V_old + E + 1).
```

This includes header decoding, unary guides, codec/component reversal,
2·9f stable-partition passes, full-bank copies, commit, erasure and returns.
Erasure never reduces already incurred historical backing. The selected
positive leaf #7429 can consume the resulting packed packet under #7578's
separate common-root numerical premise; its complete child bill remains
additional. This is a direct/leaf-order O(f V_old+E) completion. The fast
nonleaf recurrence and full selected occurrence/owner admission remain open.
The graph's complete time is also **Omega(f V_old+E)**: its repeated full
PACK erasures/rewrites alone cost at least 8f V_old writes. It therefore
requires a changed transport implementation before use at an accelerated
unbounded nonleaf tariff; this lower bound is specific to the new graph.

## Why this is different from the predecessors

#7578 already specifies the semantic permutation and proves that
`V_old/V_packed=3(b+1)/b>3`, so a header-only substitution fails. #6967
already supplies a structured old-coded positive service; #7429 supplies
a literal packed positive service. This package implements their missing
physical format boundary. Stable partition itself, the native C identity,
the Gaussian row bounds and the selected common-grid argument are credited
predecessor results, not new claims here.

The core invariant is that selected position `p_k=u+kK+rho` remains at
that position after the earlier shorter rotations. It can therefore be
extracted to `u+k` by a stable binary separation **within each fixed
prefix**. The exact runtime guide formulas and reverse induction are in
[PROOF.md](PROOF.md). Runtime instructions never inspect a host address,
decoded width/stride, array length or arbitrary-precision value.

## Reproduce

Python 3.12 and the standard library suffice. From this directory, without
Git, network access or any source outside the package:

```
python3 -I -W error -B verify.py
python3 -I -W error -O -B verify.py
```

Both print deterministic JSON ending in status
`PASS_SELECTED_MOVE_PACKED_CODEC`. From a repository checkout use:

```
python3 -B scripts/research_package.py --package research/selected-move-packed-codec
```

Four complete rank-nine f=1 packets execute the real table, including
reservation-compatible geometry a=12,u=2,K=1, recovered r=2/b=3,
a 201-bit cutoff, and b=22. Two same-width service fixtures change the
packed words to test the inverse return; they are **not native C runs**.
Five smaller extracted shuffle tests cover nontrivial K=2/3, rho>0,
multiple prefixes/rows and different record widths against direct indexing.
Thirteen layout/format/ownership controls and ten source mutations detect
the named failures. Complete f>1 or K>1 nine-slot packets are unrun; the
uniform theorem rests on the written invariant and cost proof.

`SOURCE-PINS.json` authenticates all bundled evidence at exact Git/SHA256
bytes. These retained texts are not imported as scientific executables.
`SOURCES.json` binds the canonical catalogue and selected record as
historical provenance. `VERIFY.json` lists every bundled live input.

## Open next questions

The caller supplies complete legal old geometry, disjoint blank private
windows and relative origins. A packed service must return the same width,
extent and heads, preserve the Gamma/bridge state and restore its own
distinct private owners. Malformed-service and interruption rollback,
failure cleanup of a rejecting child, global stock allocation and source
dispatcher/HOME integration are separate obligations. A successful codec
does not prove the full `precision_tape` assumption or a new multiplication
bound. Independent human or formal-kernel acceptance is unclaimed.

1. Bind the bridge to the exact complete selected packed MOVE and actual
   source/owner token, with its numerical domain, private inventory and
   successful return contract. This would connect more than the positive
   middle factor; the enclosing dispatcher still needs a precise ABI.
2. Find an admitted nonleaf implementation whose **complete** packing,
   source access, ordinary children and inverse return fit the selected
   accelerated recurrence. The present direct bill supplies no such gain.

Structured first steps and blockers are in TASK.json. Prepared for
**Jerry Chen / @CubeJerry** with substantial OpenAI assistance. Full
predecessor credit and unchanged original notices are retained in NOTICE.md
and inputs/notices/. No upstream PR was submitted by this package.
