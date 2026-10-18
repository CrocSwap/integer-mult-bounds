# Abelian frame metrics need not embed in ℓ₁

**Research consolidation; no new κ.** PR288 §1.4(a) says that abelian or
cyclic frame groups have ℓ₁-embeddable metrics. This needs an additional
hypothesis on the charged metric. **Eight commuting rational shear frames
already have a rank-distance metric that violates a necessary five-point
ℓ₁ inequality.** Cyclic groups also fail the unrestricted claim. We give
the explicit matrices, two cyclic examples, an all-size family, its exact
ℓ₁ distortion, and positive cycle controls.

This is a counterexample to the unrestricted **metric premise**, not a
counterexample to a multiplication bound, a machine-cost model, or PR288's
separate flag and G₀ theorems. A non-ℓ₁ metric alone establishes no coding
gain. No supplier, recursive invoice, or changed κ is proposed.

## The precise source and the discrepancy

The audited source is eumemic's [PR288](https://github.com/CrocSwap/integer-mult-bounds/pull/288)
at `475a088b5862f75f0b10596cfd6842d19531a5ec`. Its
[README §1.4(a)](https://github.com/eumemic/integer-mult-bounds/blob/475a088b5862f75f0b10596cfd6842d19531a5ec/research/negative-results-paradigm-search/README.md#14-other-primitive-families-and-embedding-known-coding-gap-codes)
states:

> Abelian or cyclic frame groups (units mod N, digit rotations, Z/N
> translations) have l₁-embeddable metrics, so their gap is 1. [arg]

No generating set or metric hypothesis accompanies that row. The complete
[source snapshot](sources/pr288-README.md) is retained byte for byte, with
its original notices. Its Git blob is
`dc04f533bd0f3b185969bb259e876a73714f7285`; [SOURCES.json](SOURCES.json)
records the source head, SHA256, byte count, base, and related work.

The distinction matters: a **cyclic group** need not have the metric of a
**cycle graph**. The same group with different allowed moves has a different
word metric. Abelianness alone is also insufficient.

At base `f567884aeb8851b6e794af1184119a3bfbe1e631`, PR288 is unreviewed in
the central ledger. This note supplies a narrowly scoped correction, not
approval or rejection of that entire PR. In particular, its §1.2(e) and §3
already distinguish G₀ from the full non-abelian Borel model, which remains
outside that theorem. This note neither audits nor resolves those theorems.

## A witness in the stated rational shear metric

The source's §0 and §1.2 use the abelian shears

```
Phi_M = [[I_2, M], [0, I_2]],
Phi_M Phi_N = Phi_(M+N) = Phi_N Phi_M,
d(Phi_M, Phi_N) = rank_Q(N-M).
```

The last equality is the stated rank charge for an additive shear frame
change. We use that charged metric; additional free operations or quotient
metrics require their own analysis. Consider these eight integral 2-by-2 labels:

| i | E_i | O_i |
|---|---|---|
| 0 | `[[0,0],[0,0]]` | `[[0,0],[-1,1]]` |
| 1 | `[[1,0],[0,1]]` | `[[0,1],[0,1]]` |
| 2 | `[[0,1],[-1,0]]` | `[[1,0],[-1,0]]` |
| 3 | `[[1,1],[-1,1]]` | `[[1,1],[0,0]]` |

Every cross difference `E_i-O_j` is nonzero of determinant zero, hence has
rank 1. Every difference of distinct labels in either column has nonzero
determinant, hence rank 2. Their rank metric is exactly `K₄,₄`.
The pentagonal inequality below applied to `(E_0,E_1,E_2,O_0,O_1)` is
violated by 2. Hence the **standard rational shear rank metric itself**
does not admit an isometric ℓ₁ embedding.

All 64 ordered differences, relative shear products, and commutations are
checked. The nonzero 2-by-2 determinants are in `{−2,−1,1,2}`, and each
rank-one difference has an entry ±1. Consequently the ranks also survive
reduction over every field of odd characteristic. A separate Fraction
elimination checks both the 2-by-2 differences and the 4-by-4 operator
differences.

The **shear operators** commute; their **label matrices** need not commute
or preserve a common flag. This is a finite subset of the additive shear
group, not a cyclic subgroup. The isometry to the cyclic example below is
only a metric isometry, not a group homomorphism or a network. In
particular, the cyclic example's involutive target is not transferred to
the torsion-free shear group. The source's separate abelian/flag no-saving
arguments are not contradicted by a failure of ℓ₁ embeddability.

## The separating inequality and cyclic witnesses

Use the additive cyclic group `C₆ = Z/6Z`, with allowed increments
`S = {1,3,5}`, each of cost one. This is an undirected connected Cayley
graph because `S = -S` and contains 1. Every even vertex is adjacent to
every odd vertex. Its shortest-path metric is therefore the metric of
`K₃,₃`: distinct same-parity vertices have distance 2 and opposite-parity
vertices have distance 1.

Take points `(0,2,4,1,3)` and coefficients `b = (1,1,1,-1,-1)`. For any
ℓ₁ metric, the pentagonal inequality is

```
Q(d) = sum_{i<j} b_i b_j d(i,j) <= 0.
```

Here the three positive-point pairs contribute 6, the negative-point pair
contributes 2, and the six cross pairs contribute −6. Thus **Q(d)=2>0**.
This is an exact counterexample, not a failed embedding search.

Why the inequality is necessary: a cut metric `δ_A` is one on separated
pairs and zero otherwise. Write `t = sum_{i in A} b_i`. Since `sum b_i=1`,

```
Q(δ_A) = t(1-t) <= 0,
```

because `t` is an integer. Every finite ℓ₁ metric is a nonnegative sum of
cut metrics: split each coordinate's absolute difference at its ordered
coordinate values. Equivalently, integrate threshold cuts for an L₁
embedding. Nonnegative sums preserve the inequality.

To retain an involutive target, use `C₈` and `S={1,3,5,7}`. The same five
points have the same violation. Translation by 4 is a nonidentity
involution, with distance `d(0,4)=2`; this example is the metric of `K₄,₄`.
These are abstract charged graphs. In particular, we do **not** price a
fixed modular multiplication or digit rotation at one recursive call:
whether it is free or paid in a particular tape interface must be proved
separately.

## All-size family and sharp distortion

For any integer `r>=3`, the cyclic group `C_(2r)` with all odd residues as
unit-cost generators has metric `K_(r,r)`. Restriction to three vertices
in one part and two in the other gives the same pentagonal violation.
Thus the failure is not isolated to the two replayed examples.

More precisely, for `r>=2` its optimal ℓ₁ distortion is

```
D = 2(r-1)/r.
```

Here distortion means the least `D` such that an ℓ₁ distance `ρ` can be
rescaled to satisfy `d <= ρ <= D*d` on every pair.

For the lower bound, give every vertex in one part coefficient +1 and
every vertex in the other part coefficient −1. The coefficient sum is
zero, so on a cut the quadratic sum is `−t²<=0`. Consequently the total
of within-part ℓ₁ distances is at most the total of cross-part distances.
For a noncontracting embedding, the first total is at least
`2r(r−1)`, whereas the second is at most `D*r²`. This proves the bound.

For equality, for each even/odd pair `(e,o)` use the cut `{e,o}` with
weight `1/r`. Each same-part pair is separated by `2r` such cuts, and
each opposite-part pair by `2(r−1)` cuts. The resulting ℓ₁ distances are
respectively 2 and `2(r−1)/r`, proving attainment. The retained certificates
give every cut explicitly for `r=3,4`, hence distortion **4/3 and 3/2**.
This is an embedding statement, not an achievable network saving.

The written cut argument proves the family statement. The finite Python
replay checks only the two stated examples and controls; it is not a formal
proof of the family theorem or of integer multiplication.

## Positive controls and a usable replacement condition

On the same groups, allow only increments `{1,−1}`, each of cost one.
These are ordinary cycle metrics and are ℓ₁. For `C_n`, take every cyclic
interval of `floor(n/2)` vertices as a cut with weight 1/2. A pair at cycle
distance `d<=floor(n/2)` is separated by exactly `2d` intervals, giving its
distance exactly. The checker compares every pair for `n=6,8`.

A safe replacement for the disputed row is:

> An ℓ₁-based no-saving argument requires a cut decomposition of the
> actual charged frame metric. Cyclic or abelian group structure alone
> does not establish that hypothesis. The unit-cost single-step cycle
> metric has such a decomposition; other move sets need their own proof.

The original routing implication is not re-proved here. This note removes
an unsupported route to its hypothesis. It does not reopen a closed search
for a particular primitive with an already proved metric or other
obstruction. In particular, navinor's related
[PR825](https://github.com/CrocSwap/integer-mult-bounds/pull/825), pinned at
`421db1ca2eb26056e82797f94b8c4eecd0120620`, uses a common-flag rational-frame
argument independent of this premise; no PR825 code is imported.
Jeremy Diviney's [PR836](https://github.com/CrocSwap/integer-mult-bounds/pull/836)
at `7ae9124f59694bb1e5acf2ae99c65e63c115b2f4` supplies a distinct signed-rank
argument for unitary mixers with general symmetric subadditive group
metrics. It does not require an ℓ₁ hypothesis and is not contradicted or
replayed here. Neither related PR supplies the counterexample in this note.

## Reproduce

From the repository root, Python 3.10+ and the standard library suffice:

```sh
python3 -I -B research/abelian-cayley-metric-scope/verify.py
```

Expected output:

```text
PASS_ABELIAN_METRIC_SCOPE cayley=2 rational_shears=8 cycle_controls=2 distortion=4/3,3/2 no_new_kappa
```

The command is offline and read-only. It binds the complete source snapshot,
recomputes all four shortest-path matrices and the complete rational shear
rank metric, checks 352 cut inequalities (including trivial cuts), verifies
the distortion witnesses and both exact
cycle embeddings, and compares every field of [CERTIFICATE.json](CERTIFICATE.json).
`--write /new/path.json` writes an additional checked receipt exclusively;
it refuses to overwrite an existing path.

```sh
python3 -I -B research/abelian-cayley-metric-scope/test_verify.py
```

The tests use separate Floyd–Warshall and Fraction-elimination implementations
and literal partition sums, and exercise wrong metrics, changed or omitted
shears, damaged embeddings, missing coverage, source and receipt
corruption, JSON type confusion, optimized
Python, relocation and output preservation. See [VALIDATION.md](VALIDATION.md)
for the actual run results and scope.

The source-guided experiment tested exactly the two graphs above, the
two ordinary-cycle controls, and the eight-point rational shear subset,
stopping once the exact separating inequality, native rank witness,
and matching distortion bounds were established. There was no randomized
graph search, solver, timeout, or unreported infeasibility claim. Assignment
seed 99 chose this scope from the three candidates in [CLAIM.md](CLAIM.md).

## Attribution and retained assumptions

eumemic supplied PR288's research inventory, source wording and explicit
model boundaries, with its disclosed Anthropic Claude assistance. Credit
for the underlying obstruction program and its predecessors remains in
the unchanged source notice. Cut decompositions, pentagonal inequalities
and complete-bipartite metric arguments are standard techniques; no
literature-priority claim is made for these mathematical facts.

This consolidation and its exact checker were prepared by **Jerry Chen
(@CubeJerry), with substantial OpenAI Codex assistance**, under the
repository's Apache-2.0 license. No independent human review is claimed.

The selected PR799/PR741/PR589 construction and its conditional
`κ=1661634653669567/10^18` are unchanged. This note supplies no new physical
realization, all-size compiler, source-access, copy/restoration, whole-call
hosting, precision/tape or analytic-transfer argument. All such obligations
remain where the selected construction and its predecessors leave them.
