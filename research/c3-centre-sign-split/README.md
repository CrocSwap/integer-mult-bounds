# Split every sign character of the c=3 centre block

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the residual signed permutations that
split every sign character of sector `c=3` are 96 explicit involutions. One
commuting pair splits each of those 16 characters into four positive
`A_3`-invariant joint eigenspaces. The trivial character splits as
`216 + 216 + 216 + 216`.

The selected conditional kappa stays `781451/250000000`. [PROOF.md](PROOF.md)
separates the trace-formula proof, the exhaustive stabilizer census, and the
facts that are not claimed.

## Result

The live input is the query pinned in [SOURCES.json](SOURCES.json), SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
Coordinates `0..7` are vectors in `F_2^3`. The column supports are the 14
affine planes, and the support automorphisms are `AGL(3,2)` of order 1344.
Every signed lift induces an orthogonal linear port map, so the symmetry group
has order `344064`.

The stabilizer of sector `3` has order `3072`. Its diagonal sign stabilizer
has order 32, and the 16 patterns with positive sign on coordinate 0 reproduce
the known character dimensions

    {864: 1, 432: 4, 192: 6, 80: 4, 32: 1}.

Exactly 128 stabilizer elements preserve every one of those characters. They
form an elementary abelian group. Thirty-two are diagonal signs and act by a
scalar on each character, so they split nothing. The other 96 are the
involutions

    (0 2)(4 6),   (0 4)(2 6),   (0 6)(2 4),

with opposite signs on the two even cycles and arbitrary signs on the odd
coordinates `{1,3,5,7}`. Each of those 96 splits every character. Cross-coset
pairs, 3072 unordered pairs, give four positive joint eigenvalues on every
character. Same-coset pairs only repeat the two-way split.

One such pair is `u = (0 2)(4 6)` with minus signs on coordinates 0 and 2,
and `v = (0 4)(2 6)` with minus signs on coordinates 0 and 4. Their product
is `(0 6)(2 4)` with minus signs on coordinates 0 and 6. The joint dimensions
are `216^4` on the trivial character, `180+84+84+84` on each 432-dimensional
character, `48^4` on each 192-dimensional character, `44+12+12+12` on each
80-dimensional character, and `8^4` on the 32-dimensional character.

The predecessor involution `g = (1 2)(5 6)` sends sector 3 to 343. The
involution `t = (1 5)(2 6)` fixes sector 3 and preserves only 8 of the 16
characters. Neither is one of the 96.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal interface binding.
The c=3 clause of the handoff
[discussion comment 19144258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144258)
asks which residual signed permutations split every character of `c=3`.
Upstream PR
[#6944](https://github.com/CrocSwap/integer-mult-bounds/pull/6944)
certifies the `c=1` and `c=128` splits for a different pair and records that
`g` does not preserve sector 3. This package starts at that blocker. It does
not split the `c=1` characters that `g` and `t` move, and it does not compute
a characteristic polynomial or an irreducibility test for a 216-dimensional
block.

Krzysztof Wojt's `research/exact-one-slot-gram/` is the degree-881 one-slot
certificate. Nick Petalas's `research/uniform-centre-gram-annihilator/` is the
coarse all-width annihilator. Those certificates were not replayed. A
216-dimensional invariant subspace does not replace either one.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c3-centre-sign-split/verify.py
python3 -B -O research/c3-centre-sign-split/verify.py
python3 -B scripts/research_package.py --package research/c3-centre-sign-split --check-only
```

The direct marker is `PASS_C3_CENTRE_SIGN_SPLIT`. Acceptance uses explicit
checks, so `-O` does not skip them. The run enumerates `AGL(3,2)`, evaluates
`T(3)` for all 344064 signed affine maps, rebuilds the 3072 stabilizer
elements, and tests character preservation on each of them. On the measured
host that takes about four seconds. Rejection controls are a coordinate
transposition, an even double transposition whose cycles carry the same sign,
and a truncated sign average. No Lean, Docker, degree-881 replay, or selected
cold replay was run.

## Overlap

`scripts/find_overlap.py` was refreshed on 2026-11-10 against upstream
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Coverage: local notes 8919 of
8917 HEAD paths, complete; 895 open PRs, pagination complete, fetched
2026-11-10T02:19:29Z; 6934 discussion records, pagination complete, fetched
2026-11-10T02:20:25Z. Closed PRs were searched through local READMEs, task
metadata and the ledger only.

The open PR that meets the same Gram is #6944, head
`26ceb7a0b4e04d4377a31aaa849dcb13e06e4cbc`. Its open question is the `c=3`
clause answered here, plus the separate `c=1` characters moved by `g` and
`t`. No open PR body claims a splitter that preserves sector 3. Discussion
comment 19492873 is the finding attached to #6944. Comment 19146049 is an
unrelated mixed-sign count. This search is not a novelty certificate.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- The characteristic polynomial of one 16-dimensional joint summand of the
  weight-4 `c=3` character is still uncomputed. The trace formula gives the
  dimension without a basis. This is a smaller block than the 216-dimensional
  `A_1` summand, and it lives in sector 3.
- A payload involution from the degree-881 certificate is not a coordinate
  signed permutation. Whether one such involution fixes sector 3 and splits a
  joint space above any further is outside this census.

## Credit

JoyboyBrian's handoff recorded the sign-character dimensions and asked for a
decomposition that covers `c=3`. The `c=1` and `c=128` splits, and the fact
that `g` sends sector 3 to 343, are the certificate in upstream PR #6944.
Ali Romman's PR4958 and PR4720 retain the query and the Bell action. Nick
Petalas's PR5120 is the degree-410 lower bound. Krzysztof Wojt's exact
one-slot package is the degree-881 annihilator. The doubled representation
comes from PR1719. New work is Apache-2.0.
