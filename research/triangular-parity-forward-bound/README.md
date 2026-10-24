# Sharp forward macro-prefix bound for triangular parity recursion

For every dyadic size, the exact lower unit triangular Toeplitz parity compiler
has **every forward macro-prefix bounded by `1+η` in infinity norm**, provided
the symbol tail has coefficient l1 norm at most `0 ≤ η ≤ 1`. The bound covers
all legal interleavings of the two disjoint children and is sharp even at a
proper prefix. In particular, the half-tail forward-only bound is **3/2**.

This resolves the remaining forward-only question in
[Discussion #4715](https://github.com/CrocSwap/integer-mult-bounds/discussions/4715#discussioncomment-19130279).
[PR #4731](https://github.com/CrocSwap/integer-mult-bounds/pull/4731), exact head
`3fcaa4d4c0568ce474c593d0882296ff43d3705a`, already proves the common four-cut
bound `1/(1−η)` for `η<1`; its half-tail bound 2 remains sharp for inverse
operators. The present proof uses the correlation between a forward prefix and
its inverse suffix instead of bounding both separately. It does not require
or copy code from that pending package.

## Quantified proposition and schedule

Let `N=2^d`, `d≥0`, and `f=(1,f_1,...,f_(N−1))` have real or complex entries
with `Σ_(j≥1)|f_j| ≤ η ≤ 1`. Write `T=T_N(f)`. A **macro** is one completed
right or left Toeplitz shear in the exact parity recursion of
[`SHALLOW-TOEPLITZ.md` §3](../unconditional-batched-crt/vendor/SHALLOW-TOEPLITZ.md).
Within every node the right shear runs first, both child recursions run next
on disjoint coordinates in any interleaving preserving each child's order,
and the left shear runs after both finish. Include the empty and completed
prefixes. No cut inside a shear is included.

For a cut let `P` be its forward prefix, and `Q` its remaining suffix, so
`T=QP`. Define **`R=P T^(-1)=Q^(-1)`**, with this multiplication direction.
Then

```
||P||_infinity ≤ 1+η.
```

The theorem is about the restored logical-coordinate basis. A physical wire
permutation at a cut only left-multiplies the prefix by a norm-one permutation,
so the same norm bound holds during those reorderings. Literal support and
unit-diagonal assertions below are used only after restoring logical indices.
Simultaneous completed macros on disjoint subtrees may be serialized in either
order; thus their layer boundaries are included as well.

## Proof: disjoint supports retain the lost correlation

First prove an algebraic invariant **without any small-tail hypothesis**:
`P` and `R` have unit diagonal, and `H=P−I` and `G=R−I` have disjoint supports
entrywise. For the one-wire leaf both matrices are the identity. At any node
write `f(z)=e(z²)+z o(z²)`, and, modulo `z^(N/2)`, put

```
k=o/e,       s=e−z o²/e,
E=T(e),     S=T(s),     K=T(k),
U=[ I ZK ; 0 I ],       L=[ I 0 ; K I ],
T=L diag(E,S) U.
```

Every child symbol has constant term 1; all finite triangular inverses exist,
including when the original tail is 1. Work temporarily in even/odd block
order. Between the completed `U` and the final `L`, let `P_e,P_s` be arbitrary
legal prefixes of the children, with `R_e=P_e E^(-1)` and
`R_s=P_s S^(-1)`. Exact multiplication gives

```
P = diag(P_e,P_s) U = [ P_e  P_e ZK ; 0  P_s ],
R = P T^(-1) = diag(R_e,R_s) L^(-1)
                    = [ R_e  0 ; −R_s K  R_s ].
```

The two off-diagonal blocks occupy opposite positions. In the diagonal blocks,
the child induction gives disjointness of `P_child−I` and `R_child−I`, and
unit diagonals. Thus the invariant holds for every pair of child cuts,
including either child empty or completed. Before `U`, `P=I`; after the
completed `L`, `P=T` and `R=I`. These endpoints also satisfy the invariant.
This covers all cuts and arbitrary legal interleavings. Simultaneous conjugation
by the parity permutation preserves supports and the diagonal, so induction
returns to the original logical basis.

Now set `F=T−I`, so `||F||_infinity ≤ η`, and use `P=RT`:

```
H−G = P−R = R(T−I) = (I+G)F.
```

For row `i` put `h_i=Σ_j|H_ij|` and `g_i=Σ_j|G_ij|`. Disjoint supports and
zero diagonal give the exact equalities `||H_i−G_i||_1=h_i+g_i` and
`||R_i||_1=1+g_i`. Therefore

```
h_i+g_i ≤ η(1+g_i),
h_i+(1−η)g_i ≤ η.
```

Since `0≤η≤1`, this implies `h_i≤η`. The unit diagonal of `P` now yields
`||P||_infinity=max_i(1+h_i)≤1+η`. Absolute values suffice throughout, so
complex coefficients cause no change. No Neumann inverse bound is used.

## Sharpness, the edge η=1, and a domain control

At `N=4`, `f=(1,η,0,0)` has a proper root-`U` prefix with infinity norm
exactly `1+η`. The bound is therefore optimal even without the final endpoint.
At `η=1`, the same proof gives 2. This does **not** bound inverse suffixes
uniformly at that edge: for `f=1−z`, the empty prefix has `R=T^(-1)` with
infinity norm `N`.

The restriction on η matters. At `N=8`, `f=(1,1,1,0,0,0,0,0)` has tail 2,
`e=1+z`, `o=1`, and `k=1−z+z²−z³`; the proper root-`U` prefix has norm 4,
which exceeds `1+η=3`. This is a domain control, not a classification for every
η above 1.

## Scope, family status, and overlap

This is a local quantified precision audit. It closes a sharp **forward macro**
lemma, not a missing general polynomial stability theorem: the retained source
already states polynomial bounds for internal gates and composed circuits.
The proof does not establish sharper bounds inside FFT/circulant/negacyclic
shears, rounding, generator preparation, Gaussian normalization, fixed-tape
bit costs or a full multiplication theorem. The selected conditional frontier
and supplier admission are unchanged. No new mechanism expansion is proposed.

The original `uniform-transfer-audit` card and refinement to `η≤1` are recorded
in [TASK.json](TASK.json). Family coverage before this contribution was:

| Obligation | Status and distinct contribution |
| --- | --- |
| One-level parity tail budget | James Reed's [#4699](https://github.com/CrocSwap/integer-mult-bounds/pull/4699), head `67c70cc7d190fc4f728292d8f384c13f26f90385`; already covered. |
| Individual four/eight-wire prefix symbols | [#4701–#4706](https://github.com/CrocSwap/integer-mult-bounds/pull/4706); finite examples, not repeated as the result. |
| All-depth common four-cut bound | #4731 at the exact head above; already covered, including child interleavings. |
| All-depth forward-only sharp bound | This proof: disjoint support, row tradeoff, and `1+η` through η=1. |
| Internal gates, complete Gaussian/physical accounting | Separate obligations, not discharged here. |

Before the claim, offline `find_overlap.py` inspected the full shared snapshot
of 498 open PRs (2026-10-22 18:24:36 UTC), 3641 Discussion records
(18:25:24 UTC), and all 5860 tracked local package notes, with no local omissions.
The card search and terms `forward-prefix-only`, `triangular-parity`, `1+eta`
found the predecessor thread and finite lineage; no competing general proof
was found. Cache coverage is not proof of novelty and does not include arbitrary
unpublished work or every PR diff.

## Reproduce and evidence limits

From the repository root, using Python 3.12 (standard library only):

```sh
python3 scripts/research_package.py --package research/triangular-parity-forward-bound --check-only
python3.12 scripts/research_package.py --package research/triangular-parity-forward-bound
```

The registered normal and optimized runs use explicit checks that survive `-O`.
The checker enumerates order ideals of the macro dependency DAG, compares
matrices reached by different interleavings, and checks endpoints, both inverse
identities, unit diagonals, disjoint support, the exact row identity and its
tradeoff. Seven rational fixtures of sizes 1, 2, 4, 8 include signed tails,
η=1, proper-prefix sharpness, and all 123 eight-wire DAG cuts. Five negative
controls reject a non-macro midpoint, non-dyadic size, non-unit symbol,
wrong final-shear sign, and applying the theorem beyond η=1. The last control
also checks the exact norm-4 witness above.

These finite controls support implementation review; the preceding induction
is the all-size proof. They are not exhaustive coefficient search, a formal
proof, independent human acceptance, or full historical/native/Lean/Docker
replay. [SOURCES.json](SOURCES.json) pins retained inputs and provenance at
canonical base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`.

## Open next questions

The structured question in [TASK.json](TASK.json) is whether one concrete
retained internal shear implementation has the gate-cut precision accounting
required by the Gaussian caller. Start with a specified section-2 gate cut and
its caller norms, after a separate overlap/claim check. The support invariant
need not hold inside a shear, so this theorem cannot be substituted for that
work. No further minor macro-bound construction round is requested.

## Credit

Prepared for Brian with substantial OpenAI Codex assistance in proof discovery,
implementation and independent AI proof review; no human review acceptance is
claimed. Apache-2.0. The parity compiler is retained from Vlado Vojdanovski's
[#1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673), used by Cinna
Davis's [#4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100) Gaussian
caller. The forward-only question follows Ryanson Jonathan (`one-factor-of-t`),
unpaidmoon/#4371, James Reed's one-level and finite lineage, and #4731.
The checker reuses only the pure `identity`, `multiply`, and `toeplitz` helpers
from [q-toeplitz-factorization](../q-toeplitz-factorization/README.md), whose
retained factorization credits Chafik Boukhalfa/#489, Alexey Kuznetsov, and Jose
Manuel (`jmbarrancoml`)/#3851. Its historical selected-result check and main
program are not invoked.
