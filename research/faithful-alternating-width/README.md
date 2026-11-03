# Exact faithful width for degenerate alternating trace labels

An alternating binary n-space with radical dimension k has the following
minimum ambient width for an injective ordinary-dot-product realization:

```text
0        if n=0;
n+1      if n>0 and k=0;
n+k      if k>0.
```

For an F4 Hermitian form of dimension d and rank a, this is `2d+1` when
`a=d>0`, and `4d-2a` when `a<d`. The zero-dimensional case needs no bits.
This answers the faithful label-width part of the degenerate-restriction
opening in [Maximooch's PR831](https://github.com/CrocSwap/integer-mult-bounds/pull/831).
It is a scoped written proof with a constructive algorithm and finite exact
corroboration. No new kappa or selected-frontier change is claimed.

[PROOF.md](PROOF.md) gives the all-dimension lower bound and explicit
attaining vectors. The construction retains every radical direction. When
both the nonsingular part and radical are nonzero, sharing one padding
coordinate saves one bit over embedding those parts separately.
For example `H direct sum 0_2`, the trace form of `diag(1,0)` over F4,
embeds faithfully with images `3,6,15,48` in six bits. Six is optimal;
separate padding would use seven.

## Evidence and reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/faithful-alternating-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/faithful-alternating-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/faithful-alternating-width
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/faithful-alternating-width --check-source-history
```

The standalone verifier enumerates every alternating matrix through dimension
six and constructs an injective realization for each. It checks every Gram
entry, every vector image and every null vector on that domain. A separate
literal search enumerates all ordered even-vector tuples in ambient widths
zero through six for source dimensions zero through three; their first
injective realizations must give the asserted minimum. Further changed-basis
fixtures reach dimension 32. Explicit rejection controls cover invalid forms,
radical collapse, a wrong Gram matrix and unnecessary padding.

The first local replay passed 33,868 forms, all twelve independent literal
minimum problems after 34,846 candidate tuples, 273 larger fixtures and ten
rejection controls. The constructor corpus has canonical SHA256
`d119625804bc6c39a3ca7a5298cc6ee48c0285928e5b77465b9d348131af60fa`.
The written proof supplies the uniform result; these bounded computations
corroborate it.

Replay prints `PASS_FAITHFUL_ALTERNATING_WIDTH` in a generated JSON receipt
bound to the six package-file hashes. It writes no files. Normal and optimized
commands use the same explicit checks. Registered replay additionally
authenticates the pinned source/provenance metadata. It does not execute or
audit the predecessors' verifiers or native programs.

## Scope and limits

This changes the complex-rank-shape-decoder card to a geometric interface
lemma. The cheap selected-baseline binding command passed before the change.
The lemma identifies an exact width cost that Gram rank alone misses; it
does not price a complete decoder or claim a full signed-moment improvement.

Only binary linear identities and Gram pairings are preserved. A prescribed
quadratic phase or weight modulo four can impose further conditions. Source
incidence, nested physical frames, native absolute phase, dirty restoration,
hosting, paid compiler/caller costs and all-size multiplication obligations
remain open. No predecessor scientific replay, Lean, Docker or selected cold
replay was run.

## Open next questions

1. What is the minimum faithful width when a specified quadratic refinement
   must also equal ambient Hamming weight modulo four? This determines
   whether the minimum Gram embedding preserves the required native phase.
   Start with one hyperbolic block and one radical direction, separating
   whether the refinement vanishes on the radical. Quadratic type and
   ambient weight congruences are the missing constraints.
2. Can a concrete degenerate source/read interface use this minimum embedding
   with a favorable complete invoice? Start by declaring one actual label
   space, all entry/exit frames and its prescribed phases. The physical
   itinerary, native implementation and full caller bill remain missing.

## Sources and credit

This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. New material is Apache-2.0.

Credit Maximus Putnam / Maximooch, PR831, for the Hermitian trace-radical
identity, the alternating-compatible interface and its degenerate-restriction
opening; Joel Pulikkan / GamingPuzzled, the endpoint normal-form authors and
hipotures / PR41 retain the lineage credited there. Credit THU New Media
Research Center / thu-nmrc, PR5464, for its earlier nonalternating degenerate
embedding and radical-completion lower bound. Its native construction is a
separate result and is not replayed here. Hyperbolic splitting and the
dimension bound are classical linear algebra; no global literature priority
is claimed. The new deliverable is the uniform alternating minimum, explicit
constructor and singular-trace width corollary under this faithful contract.
Exact source bytes and the original priority card are pinned in SOURCES.json.

The advance claim is [recorded in the handoff thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362861).

## Verification implementation bounds

The constructor accepts alternating forms through dimension 32 and emits at
most 64 bits per image. Its hyperbolic split has at most sixteen stages and
at most 496 candidate pairs per stage. It uses no recursion. The full-matrix
census is streamed through dimension six, with at most 64 vectors in each
literal image span. The independent minimum search uses at most 31 candidate
vectors per coordinate and source dimension at most three. It retains just
the first width for each of twelve Gram matrices. Each function is shorter
than sixty lines. Explicit invariant and rejection checks remain active with
optimized Python. Warning-strict normal and optimized replay are registered.

Power-of-Ten rule 3 has a CPython managed-allocation deviation in verify.py.
Integer, list, set and JSON allocations occur during verification. Their
live sizes are bounded by the dimensions and streamed domains above; no
corpus of all 33,868 embeddings is retained. The complete boundary and maximum
dimension are exercised locally. A fixed-allocation implementation would be
a separate port if this verifier becomes a constrained native component.
