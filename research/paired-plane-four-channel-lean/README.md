# Four scalar channels imply the normalized C5 pivot equation

This package closes the **factorization-to-pivot** gap left explicit in
[PR2525](https://github.com/CrocSwap/integer-mult-bounds/pull/2525).
For a nontrivial commutative coefficient ring, a five-by-five matrix of
two-by-two blocks with identity diagonal and the C5 forbidden zeros cannot
factor through four scalar channels. The coefficients and free blocks may be
asymmetric. The result is checked by Lean 4.34.1 using only its standard
axioms; no Mathlib installation is required.

It does not formalize the library statement that ordinary field rank at most
four supplies such a factorization, the source JSON interpretation, or the
full rank49 theorem. These remain separate interfaces. There is no new rank
optimum, physical COPY bill, supplier or exponent claim.

## Formal statement and proof boundary

`Pivot.ThroughFour m u v` states the literal factorization

```text
m[i,j] = u[i,0] v[j,0] + u[i,1] v[j,1],
```

where each entry is a two-by-two scalar matrix. Thus `u` and `v` are a general
10-by-4 and 4-by-10 factorization, with no restriction to diagonal or commuting
blocks. `Pivot.factor_to_pivot` assumes only this factorization and
`m[0,0]=m[2,2]=I_2`, `m[0,2]=m[2,0]=0`. It derives

```text
m[i,j] = m[i,0] m[0,j] + m[i,2] m[2,j].
```

The proof stacks the selected factor rows into `p` and columns into `q`.
The four pivot equations give `pq=I_4`. `Four.reverse_inverse` derives
`qp=I_4` over a commutative ring by determinant and adjugate identities.
Associativity then gives the displayed normalized equation. `Algebra.lean`
proves the required four-by-four scalar polynomial identities; scalar
commutativity is used there, not commutativity of two-by-two blocks.

`Pivot.no_four_channels` applies the unchanged predecessor
`PairedC5.no_four_pivot`. Its hypothesis is now an arbitrary four-channel
factorization, rather than the normalized pivot equation itself.
`Pivot.relaxed_through_four` gives explicit integer factors for the
predecessor's one-edge-relaxed example. Its only forbidden pair violations
are the B-D pair documented in PR2525, so the full zero pattern matters.

The mathematical rank consequence over a field follows externally from the
usual rank-factorization theorem (padding with zero channels if necessary).
The new Lean theorem does not use that library theorem and does not redefine
ordinary matrix rank as `ThroughFour`.

## Reproduce

From the repository root, with Lean4.34.1 and Python3.10+:

```sh
python3 -I -B research/paired-plane-four-channel-lean/check_lean.py --lean /path/to/lean
python3.12 scripts/research_package.py --package research/paired-plane-four-channel-lean
```

The first command performs a fresh isolated module build, prints all twelve
theorem axiom inventories, and rejects four actual altered Lean programs:
wrong reverse-inverse conclusion, a nonzero pivot cross block, omitted ring
nontriviality, and a broken relaxed factor. The polynomial build may take
several minutes; its bound is900 seconds, with120 seconds for each later
module or mutation. Temporary compiled modules are not used as submitted
evidence. `--out NEW_FILE` saves a receipt and refuses an existing path.

The registered Python replay checks the **recorded** Lean receipt against the
three exact source files and unchanged predecessor bytes, then rejects four
receipt/source corruptions. It does not invoke Lean. `LEAN-CHECK.json` records
the actual local kernel run; it is not a hosted-CI claim. The positive relaxed
factor is also kernel checked. Separate AI review checked factor orientation,
ring hypotheses and the remaining rank boundary; no human review is claimed.

## Sources and credit

`Schur.lean` is byte-for-byte PR2525 at
`ed86bcbe8f728e5412a6ef8f1910bac38f073f51`, with Git blob and SHA256 in
`SOURCES.json`. That work (ywz65 with OpenAI Codex assistance) formalized the
normalized C5 obstruction and externally bound it to the selected mask.
PR2484 by thakrarsagar supplied the scalar minrank49 construction and C5/I44
certificate; Cinna Davis supplied the paired-plane matching and Adam Gall
the scalar permission contract. This package claims only the missing formal
factorization normalization, not priority for those results. PR2541's
all-block-size written rank theorem is complementary and already covers the
mathematical rank bound more generally.

The picker assigned `complex-rank-shape-decoder`, priority revision4, nonce
`5daa35e3a3b51d84040a502049bb18ef`. The prescribed ceiling replay and lever
screen passed as orientation. The scope is explicitly **changed**: this is
a formal lower-bound interface handoff, not a new per-call profile clearing
the card's5% gate. Exact card, base, overlap, claim and next questions are in
`TASK.json`. Prepared for ywz65 with substantial OpenAI Codex assistance in
proof construction, checking and writing. Apache-2.0.

## Open next questions

Connect a maintained field matrix-rank definition to `ThroughFour` with exact
row and column indexing, then formally embed the source-bound C5 and isolated
I44 block. That would close the remaining ordinary-rank and source-interface
gaps for the fixed scalar instance. The first step is a rank-factorization
adapter; the blocker here is the absence of a matrix-rank library and formal
source parser, not a missing normalized-pivot hypothesis. No native cost
conclusion follows from closing those formal interfaces alone.
