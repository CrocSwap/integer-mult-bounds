# Isolation for orthogonal simultaneous remainder transfers

**Scoped negative result; no new κ and no selected-result change.** This package
closes one part of the simultaneous-transfer question raised by open PR
[#3296](https://github.com/CrocSwap/integer-mult-bounds/pull/3296). It proves a
conditional operator obstruction for any number of pairwise-orthogonal moved
axes, and independently reproduces the exact singleton facts used by that
argument. PR [#3311](https://github.com/CrocSwap/integer-mult-bounds/pull/3311)
independently replays a different, port-zero literal witness; this package
covers the all-port singleton domain and the orthogonal-axis implication.

## Exact scope and result

The source universe is fixed at main commit
`463113d675af7410ac91d53a4fed51ec6494eb9a`: the authenticated 2,717,280-row
PR3148 fill, the 112 port recipes, the fixed chronology, allocation and template
inputs listed in [SOURCES.json](SOURCES.json), owner replica zero, cover identity,
and PR3187's exact eight-stream Gaussian-integer replay. The proposed per-axis
rule is transcribed in `declared_rule` in [verify.py](verify.py) from PR #3190 at
head `5e4a3235169edddd033889da4e9f47635ff50c3e`: a moved axis belongs to its
donor remainder, donor and receiver differ, and the axis is orthogonal to the
receiver's current remainder axes, every stage entry/exit X/Y translation, the
terminal Y translation, and the donor and receiver terminal translations.
The resulting child ranks must not exceed 51 and each child's axes must remain
orthonormal.

The enumerated domain deliberately relaxes PR #3190's construction restrictions:
it admits any receiver with a nonempty full axis list, including a hosted
receiver, and does not forbid a child from being both donor and receiver in a
bundle. Thus it is a superset for the commuting-rule audit, not an assertion
that every enumerated overlay satisfies the native controller or hosting
contract. Excluding operator-preserving overlays in this superset is stronger
than excluding only the narrower PR #3190 move class.

Across all 112 ports, the verifier enumerates 9,384 candidate single-axis
transfers from a hosted child with a nonempty remainder to another child whose
full axis list is nonempty (the receiver's residual may be empty). Of those,
5,575 fail the declared rule. The other 3,809 pass the
rule and final rank/frame checks. At each such transfer's own moved-axis
Fourier character, the unchanged baseline is the exact scalar matrix and the
single transfer changes the exact 8-by-8 Gaussian-integer matrix. The stored
[RESULT.json](RESULT.json) contains every per-port count and the pair-control's
baseline, singleton and bundle matrices at both moved-axis characters, including
the exact changed entries. This is finite source-bound evidence for those
singleton premises.

## Isolation lemma

Fix any one of the 112 ports and its source-bound schedule. Let
`T_i = (d_i, r_i, v_i)` be a nonempty finite collection of distinct
single-axis transfers from the enumerated singleton domain. Suppose their moved
axes are pairwise orthogonal over `F_2`, each move uses its donor axis at most
once, and the combined final assignment satisfies the rank and within-child
orthonormality checks. For each `i`, let `M_i(v_i)` be the exact replay after
only `T_i`, evaluated at character `v_i`; let `M_B(v_i)` be the replay after
the whole bundle `B`, at the same character.

Then, for every `i`,

```text
M_B(v_i) = M_i(v_i) != M_empty(v_i).
```

For the equality, inspect an idle-cover-sweep phase in the source replay. A
residual axis `w` contributes `dot(character, w)` to its child's phase exponent;
this rule is implemented in PR3187's unchanged
[algebra.py](../rank7-idle-star-stream-obstruction/algebra.py). Set the
character to `v_i`. The selected move changes the residual membership of
`v_i`, with `dot(v_i, v_i) = 1`. Every other moved axis `v_j` contributes zero
because `dot(v_i, v_j) = 0`. Thus all other transfers leave every idle-sweep
phase unchanged at this character. Hosted rows, translations, bridges, local
sweeps, terminal events and chronology are fixed, so the full matrix replay is
exactly the singleton replay. The singleton census proves the inequality for
each possible `T_i`; hence the bundle cannot preserve the operator.

The orthogonality premise also keeps each component's receiver-axis check true
while the bundle is applied: other transferred axes added to or removed from a
receiver have zero dot product with it. Distinct donor axes remain available,
and only the combined rank/frame check adds a bundle-level condition.

This argument quantifies over arbitrary finite bundle size within the stated
source and legality conditions; it does not enumerate bundles. The verifier
also finds a legal port-zero pair, `4→0` with axis `2^32` and `14→0` with axis
`2^72`, and replays the bundle. At each moved-axis character, the bundle matrix
equals the corresponding singleton matrix. Both baselines are `i I_8`; the
singletons differ from them in 2 and 5 matrix entries respectively, so this pair
also supplies an explicit joint-change example. RESULT.json records the exact
baseline, singleton and bundle matrices. The proof, rather than that fixture,
establishes the all-finite-bundle implication.

## Open next questions

This result does **not** exclude a simultaneous bundle containing nonorthogonal
moved axes (including repeated copies of the same vector), an overlay whose
components are not individually in the enumerated singleton domain, another
owner replica, a changed host schedule, or a repaired/rescheduled exchange. It
does not prove that all of PR #3190's proposed gains fail under every repair, and
it does not establish any general κ bound. Those are separate questions.

The next concrete step is to identify the smallest legal simultaneous
hosted-remainder overlay in this fixed schedule with two nonorthogonal moved
axes, then test for a character that isolates it or a written obstruction that
does not require orthogonality. Other replicas and schedule repairs remain
separate scope expansions.

## Reproduction and provenance

The verifier imports PR3187's authenticated source loader and exact event
semantics unchanged. Its new work reconstructs the owner-zero rows for all 112
ports, transcribes the declared rule, enumerates every scoped singleton, and
proves the character-isolation implication above. This is a new binding and
algebraic implication, **not** an independent reimplementation of the physical
operator model. Inputs, Git blobs and SHA256 hashes are pinned in
[SOURCES.json](SOURCES.json); all live inputs are listed in [VERIFY.json](VERIFY.json).

From the repository root, with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/pr3190-distinct-axis-basis-isolation
python3 scripts/research_package.py --package research/pr3190-distinct-axis-basis-isolation --check-only
```

`verify.py --write` regenerates RESULT.json after a deliberate source change;
ordinary verification compares its freshly computed result byte-semantically
to the committed receipt. The registered replay passed with Python 3.12.15; a
direct replay also passed with Python 3.14.8. The verifier uses only the Python
standard library.

The exact replay model and source loader come from Nick Petalas's PR #3187 and
retain its PR3133 notice and credits through the pinned vendor files. The
audited remainder-transfer rule is the one stated by Rohan Arun's open PR #3190
at the head above. New proof and verifier: Cinna Davis, with substantial
OpenAI Codex assistance. No human or proof-kernel review is claimed.
