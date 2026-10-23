# Proof review: the 216-lifetime floor

## Statement and model

For the frozen 104-source / 104-target P104 paths from the PR1972/PR1991
native-channel inputs, every complete X-only monotone correction word for
`C = I - G/2` needs `L ≥ 216` lifetimes in the widened grammar `G′` defined by
the upstream proof. The proof permits arbitrary rational mixing at an equal
frame, even singular mixing; each lifetime grows through nested frames. It
allows source-independent helper births and helper ends at any frame. There
are no reads from Y, the root code, or original helpers.

The source-lifetime claim is not the 208-flag geometric certificate. Its base
is a program-level arrival count; the extra eight come from the shared-half
count below. The bound does not require restoration or a particular cut
ordering.

## Counting proof audit

Let `B_t` be the lifetimes whose nested paths pass through target hyperplane
`H_t`, and let `b_t = |B_t|`. The exact finite census has 104 distinct target
hyperplanes. A strictly nested lifetime can pass through at most one such
8-dimensional hyperplane, so if `J` lifetimes pass through none,

```text
L = Σ_t b_t + J = 208 + E,
E = Σ_t (b_t - 2) + J ≥ 0.
```

The upstream proof establishes `b_t ≥ 2` for every target: with no source read
at `H_t`, target writes there are spanned by the entering helper values; one
entering value would have to support the entire residual row inside one
hyperplane, contradicted by the checked one-cover fact.

For the full model, the replay classifies 84 targets as certified (“good”):
their intermediate-source counts are in `{0,1,2,4}`. The other 20 are treated
permissively. For a tight certified target (`b_t = 2`), its two helper paths
must pass through complementary 7-dimensional halves. The proof's
singular-mixing lemma says two such tight targets can share both halves only
if the exact pair test `T′` holds on each. The finite `F8′` census finds 12
certified targets that can have both complementary halves paired under `T′`;
these are the only exemptions in this model.

Let `m_c` be the number of non-tight certified targets, `m_p` the number of
non-tight permissive targets, `X = Σ_{non-tight t}(b_t - 2)`, and `J` the junk
lifetimes above. Set

```text
c = 84, π = 20, e = 12, A = c - e - 2π = 32.
```

Every tight certified non-exempt target has at least one imperfect half, so
there are at least `c - m_c - e` imperfect halves. They must be witnessed by:

- a junk lifetime (`γ`), which can witness at most two such halves because a
  7-frame lies in at most two target hyperplanes;
- a lifetime belonging to a non-tight target (`δ`), with at most `X + 2m`
  witnesses, where `m = m_c + m_p`;
- a lifetime belonging to a tight permissive target (`ε`), with at most
  `2(π - m_p)` witnesses.

Subtracting the latter two capacities gives
`h_γ ≥ A - 3m_c - X`. Thus `J ≥ max(0, ceil(h_γ/2))` and `E = X+J` satisfies
both `E ≥ X ≥ m_c` and `E ≥ A/2 - m_c`. Adding these two inequalities gives
`2E ≥ A/2`, hence the integer bound `E ≥ ceil(A/4) = 8`. Therefore
`L ≥ 208 + 8 = 216`.

The proof audit checked the charging cases against the nested-frame contract:
a lifetime crosses at most one 7-frame; any 7-frame is in at most two target
hyperplanes; and a tight target cannot have two lifetimes entering from the
same 7-frame because that would place its full residual support in one
hyperplane. The singular case of the mixing lemma is also handled: a rank-one
mixing matrix makes the two target rows proportional on the shared support,
so `B` is one ratio class and satisfies `T′` by definition.

The row counts `84`, `20`, the 12 exception IDs, and the `T′` pair census are
finite source facts, not consequences of the counting proof. The pinned
two-implementation replay reproduces them. The mathematical argument remains
a written proof, not a machine-checked proof.

## Exact inputs and reproduced values

The replay used the following frozen canonical inputs:

| Input | SHA-256 |
|---|---|
| `research/p104-native-channel/inputs/LOWRANK-WITNESS.json` | `0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e` |
| `research/p104-native-channel/inputs/P104-FIXTURE.json` | `516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4` |
| `research/complex-local-word-ceiling/ceiling.py` | `86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc` |

The exact upstream source hashes are in [UPSTREAM-PINS.json](UPSTREAM-PINS.json).
The replay output includes `good_targets=84`, `floor_full_singular_mixing=216`,
`pairs_passing_Tprime_full=1038`, and `both_halves_Tprime_full_good_targets=12`
with IDs `[1,3,6,7,12,14,41,46,54,74,81,83]`. The baseline selected-result
binding check passed at base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Limits and provenance

The replay checks finite geometry and the encoded complete demo word using two
separate implementations plus the vendored published relay checker. The proof
review here independently follows the written counting argument; it does not
constitute independent human review or formal verification. The grammar is
still restricted to its frozen paths and X-only reads. New frames, new source
access, a changed target contract, or a new correlated source state can fall
outside `G′`.

The result does not show that a word with 216 lifetimes exists. It also does
not price lower-dimensional gathering, primitive count, dirty restoration,
physical hosting or a consumer. The original source handoff pauses this line
unless a sub-7-frame charge is supplied.
