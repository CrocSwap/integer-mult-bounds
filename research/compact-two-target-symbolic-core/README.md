# Exact invariant agreement for the two-target compact switch

For control radix `B=2^g` and window modulus `N=2^m>B`, the
two-target compact switch with constant source bits `(1,1)` agrees
with the ideal XOR on both members of an ideal orbit exactly when

```text
u0 < B-1,  t0 < B-1,  t1 < B-1,  W0 + t0 < N.
```

[The proof](PROOF.md) establishes this formula for every binary
radix and width in the stated range. PR #7197 obtained the formula
at `B=8, N=32` by finite enumeration and left the symbolic
classification open. The new proof accounts for lower-window
spills across the two subcalls, source-load carries, and saturation
in both temporary digits. The word and five-phase upper construction
come from PR #6812. [PR #7197](https://github.com/CrocSwap/integer-mult-bounds/pull/7197) · [PR #6812](https://github.com/CrocSwap/integer-mult-bounds/pull/6812)

The formula implies that four independent coordinate translations
cannot cover the invariant core when `B>=4`. The minimum is exactly
five when `B>=8` and `5(B-2)<=N`, with a selector that takes the same
value at both ends of the ideal XOR. This is a scoped algebraic proof
with finite corroboration.

## Reproduce

Run from the repository root with CPython 3.12. The local runs use
CPython 3.12.15 on macOS 27.0.1 arm64 and the standard library.

```sh
python3.12 -I -W error -B research/compact-two-target-symbolic-core/verify.py
python3.12 -I -O -W error -B research/compact-two-target-symbolic-core/verify.py
python3.12 -B scripts/research_package.py --package research/compact-two-target-symbolic-core
python3.12 -B scripts/check_research_commit.py --package research/compact-two-target-symbolic-core --check-source-history
```

The direct check writes a report with marker
`PASS_COMPACT_TWO_TARGET_SYMBOLIC_CORE` and SHA256 hashes of the six
package files. It compares the formula with literal packed execution
of both orbit members when needed. Across 984,064 input states it finds
534,112 invariant agreement states. It exhausts the complete dirty
fields at `(B,N)=(2,4),(4,8),(4,16)`. At `(8,16),(8,64)` it sweeps
every lower coordinate and temporary field with both upper source
parities and the four upper block endpoints. The prior
`(B,N)=(8,32)` census is not replayed.

The check also covers all 557,056 relevant coordinate tuples for
the five-entry menus at `(8,64),(16,128)`. Deleting the last entry
misses 72 and 168 tuples, respectively. Seven controls cover all
four clauses, the safe side of the window boundary, an individual raw
agreement whose ideal mate fails, and a valid full-width wrap at
`N=B`.

The largest state grid has 524,288 inputs and the largest cover check
has 524,288 tuples times five phases. The verifier streams the input
grids and keeps no state-indexed table. CPython allocates finite
integer and tuple values during execution. Every failure check
remains active under optimization.

## Scope

The proof concerns the two fixed target positions, exactly two
digits per control, constant sources and the declared live-digit
word. Its cover corollary assumes independent coordinate
translations and an invariant selector. The physical translation,
selection, data movement, cleanup and recursive costs remain open.
No selected assumption, full caller or κ is established. The selected
metadata baseline passed. The selected scientific cold replay, Lean,
Docker, independent human review and formal proof-kernel review are
unclaimed.

The `uniform-transfer-audit` card changes scope to this logical CRT
switch question. The core determines which addresses each translation
can serve without exceptional repair. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19717713)

## Open next questions

- **Other source pairs.** Derive the invariant core when exactly one
  source is constant one. The two lower parities then need not be
  complementary. Begin with the resulting spill and restoration
  equations before classifying any cover.
- **Small-radix menus.** Find the exact minimum when
  `B>=4` and the five-phase packing conditions fail. Begin by deriving
  a cover on the four relevant coordinates. The four-entry adversary
  already applies there, while five-phase attainment is open.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0. Credit the
finite predecessor and its first open question to PR #7197 at
`47419abcd185a088a6b5d2ef9e721ef2651d9729`, and the raw word and
sufficient cover to Benny Zhao in PR #6812 at
`297ad233e8d00d7a7af4a09dc13fed90ede63dc4`. The translation and
conjugation method comes from PR #6231. Credit Cinna Davis's PR #4100
and unpaidmoon's PR #4321 for the compact-switch and live-digit
contracts, John-Michael Smith and Hanson Sun for the terminal carry
and window arguments, and Arham Tahir, Aaron Wang, woklerx and
Douglas Colkitt for the retained agreement and repair work.
[Finite predecessor proof](https://github.com/petalas/integer-mult-bounds/blob/47419abcd185a088a6b5d2ef9e721ef2651d9729/research/compact-two-target-translation-minimum/PROOF.md)
