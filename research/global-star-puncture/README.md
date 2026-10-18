# Sharp global-star punctures in the paired hypercube

**Scoped negative result with exact attaining decoders; no new kappa.**
For a power-of-two `k >= 2` and `p = k+1` signed coordinate pairs,
arbitrary off-target proper stars still require **three deleted ports** to
decode one retained target. This extends the target-local puncture result of
[Sam Sung's PR #669](https://github.com/CrocSwap/integer-mult-bounds/pull/669)
to its explicitly excluded off-target class, in this parameter regime.

At `k=4,p=5`, the 80-port coefficient space has dimension **65**. For a fixed
target there are exactly **67** minimum deletion sets: 35 affine planes within
its sign cube and 32 pairs of edges across two cubes. Only four of these work
with target-local stars. Thus off-target stars expand the attaining patterns
without lowering the minimum deletion count.

The proof below is algebraic. The independent standard-library program supplies
literal decoder coefficients and checks every minimum pattern. Neither the
proof nor the finite checks establish a paid supplier or a multiplication bound.

## Model and scope

A port chooses one of two coordinates from each of `k` distinct pairs among
`p` pairs. Let `P` be all `2^k binom(p,k)` ports, and let `x_S` be independent
binary inputs. Fix a retained target `T`, delete `D` disjoint from `{T}`, and
write `F=P\D`. For any signed partial port `L`, define

```text
star_L(F) = sum_{S in F, L subset S} x_S
C_j(T,F)  = sum_{S in F, |S intersect T|=j} x_S.
```

The allowed decoder over F2 is

```text
x_T = sum_{L: 0<|L|<k} a_L star_L(F) + sum_{j=1}^{k-1} b_j C_j(T,F).
```

Coefficients are arbitrary and may depend on the target. `L` need not lie in
`T`. No symmetry of coefficients is assumed. Stars with both signs of a pair
are identically zero and omitted. The empty star, degree-k stars, `C_0`, `C_k`,
and source-dependent coefficients within a correction class are outside the
model. The stars and corrections are recomputed on surviving ports.

PR #231, by Joel Pulikkan / GamingPuzzled, established the symmetric parity
criterion. PR #669 extended it to global proper stars on the full family and
proved a sharp `2(p-k)+1` puncture threshold for target-local stars. This note
uses that same model and addresses global stars after puncturing. It does not
claim a sharp threshold for `p>k+1`, or an E8 result.

## Corrections lie in the proper-star span

Let `E_l` be the sum of all degree-l target-local stars on the full port family.
At a source whose intersection with `T` has size `r`, its coefficient is
`binom(r,l)`. Binary binomial inversion gives

```text
C_j = sum_{l=j}^k (binom(l,j) mod 2) E_l.
```

Indeed, at intersection size `r` the sum is
`binom(r,j) 2^(r-j)`, equal to one exactly when `r=j`. For a power-of-two `k`
and `0<j<k`, `binom(k,j)` is even, so the degree-k term vanishes. Restricting
this identity to surviving sources preserves it. In particular, at `k=4`,

```text
C_1 = E_1 + E_3,   C_2 = E_2 + E_3,   C_3 = E_3.
```

It therefore suffices to study the full-family coefficient space `V` spanned
by proper stars. A punctured decoder exists exactly when a vector of `V` has
coefficient one at `T` and support contained in `{T} union D`.

## Three punctures are necessary and sufficient

Assume `p=k+1`. Every port has one missing pair `m`; the ports with this missing
pair form a `k`-dimensional sign cube `Q_m`. Write `s_i` for the sign bit at a
present pair `i`. Define the following binary functions on the ports:

```text
h_m(S)    = 1[S in Q_m]
h_mi(S)   = 1[S in Q_m] s_i + 1[S in Q_i] s_m,  m<i.
```

Each is a parity check on `V`. A degree-d proper star meets a compatible cube
in `2^(k-d)` ports, which is even, proving the `h_m` claim. For `h_mi`, a
degree at most `k-2` leaves at least two signs free in each compatible cube,
so the sum of any sign bit is even. At degree `k-1`, a nonzero contribution
can occur only when the star uses exactly the pairs outside `{m,i}`. Each of
the two cubes then contributes one; they cancel. If it fixes the tested sign,
its contribution is either zero or two.

Consequently every `v in V` has even weight separately on every `Q_m`. A
nonzero vector of weight at most three would have to consist of two ports in
one cube. The incident checks `h_mi` force their signs to agree at every
present pair, so those ports coincide. This is impossible for two distinct
support points. Every nonzero `v in V` therefore has weight at least four.

A decoder after at most two deletions would give a vector with weight at most
three, so it cannot exist. For the matching upper bound, take any
`(k-1)`-subset `L` of the target. There are exactly four ports containing `L`:
the remaining pair can be either of the two unused pairs, with either sign.
Delete the three other ports. Then `star_L(F)=x_T`.

This proves the sharp threshold **three**, uniformly for power-of-two
`k>=2,p=k+1`. It is a proof about every decoder in the stated linear class,
not an inference from a bounded search.

## The exact 80-port space and its 67 minimum patterns

Now fix `k=4,p=5`. The five `h_m` and ten `h_mi` are independent: on cube `Q_m`,
any relation restricts to a constant plus four independent sign variables.
All their coefficients must vanish. Hence `dim(V)<=80-15=65`.

For the reverse inequality, use coordinate indicators `u_i^0,u_i^1`, put
`z_i=u_i^0+u_i^1`, and `d_m=1+z_m`. Products of indicators at distinct pairs
are precisely star coefficient vectors. For any three distinct pairs,

```text
1 = z_a z_b + z_a z_c + z_b z_c,
```

since at most one pair is missing. Thus constant one belongs to the nonempty
proper-star span. For each `m`, the eleven functions

```text
d_m product_{i in L} u_i^1,   L subset {0,...,4}\{m}, |L|<=2
```

belong to `V`: for nonempty `L` expand `1+z_m`, obtaining degrees at most
three; for empty `L` use the displayed constant identity. They are supported
on `Q_m` and form its independent monomials of degree at most two. Across
the five cubes they give 55 independent vectors. For each pair `{m,i}`, add
the degree-three star using sign one on the remaining three pairs. It has a
cubic coefficient on exactly cubes `Q_m` and `Q_i`, at a position no other
one of these ten added stars uses. These ten vectors are independent modulo
the first 55. Thus `dim(V)=65`, and the 15 checks characterize it exactly.

Fix `T` in `Q_m`. A weight-four vector containing it has either four points
in that cube or two points in each of two cubes, by the `h_m` checks.

- In one cube the four sign vectors must XOR to zero. Four distinct such
  points form an affine plane. There are `15*14/6=35` planes through `T`.
- In cubes `Q_m,Q_i`, the first pair can differ only at sign `i` and the
  second only at sign `m`: the two incident edge-check families intersect
  only at `h_mi`. Distinctness forces those flips to occur. For each of the
  four choices of `i`, the second pair has eight choices of its other signs.
  This gives `4*8=32` possibilities.

All these configurations satisfy the checks and hence belong to `V`. Deleting
the three points other than `T` yields exactly `35+32=67` optimal patterns.
The four target-local patterns are the degree-three stars through `T` from
the upper-bound proof. To see completeness of this local count, PR #669's
cell criterion requires emptying a nonempty proper intersection cell. Here
its size is `1+2(4-j)` at intersection size `j`; only the four cells with `j=3`
fit into three deletions. The verifier checks this count by separate local
elimination as well.

A small off-target witness makes the distinction concrete. Number coordinates
`0,...,9`, with pairs `{0,1},{2,3},...,{8,9}`. The recorded target is
`T={1,2,6,8}`. Delete `{0,2,6,8}`, `{0,2,6,9}`, and `{1,2,6,9}`. Then

```text
x_T = star_{2,6}(F) + star_{2,4,6}(F) + star_{2,5,6}(F).
```

Its coefficient is `u_1^0 u_3^0 (1+z_2)`: it selects four ports in the cube
missing pair 2, three of which were deleted. On every other cube the last
factor vanishes. Two stars use coordinates outside `T`, and this deletion set
admits no target-local decoder. It appears as deleted indices `[32,33,41]`
in the receipt. This is an explicit identity, with no frame or cost claim.

## Reproduce and inspect the certificates

From the repository root, using Python 3.10+ and its standard library:

```sh
python3 -I -B research/global-star-puncture/verify.py
```

Expected output:

```text
PASS_GLOBAL_STAR_PUNCTURE threshold=3 supports=82240 witnesses=67 local=4 dual_rank=15 controls=7 no_new_kappa
```

The program constructs all 80 ports and 130 proper stars, independently checks
the correction expansions, derives a binary row basis with literal star
decompositions, and checks all 15 parity rows. It exhausts exact supports
containing the target of sizes one through four: `1+79+3081+79079=82240`.
This covers every deletion set of size at most three: a smaller actual support
would already have appeared at an earlier size. The only feasible supports
have size four. Each of the 67 resulting decoders is then evaluated directly
at every surviving source, separately from elimination.

[results.json](results.json) records the port and star ordering, 15 check rows,
coverage counts, and all 67 deleted-index triples with hexadecimal coefficient
masks. Bit `i` of `stars_hex` selects star `i` in the receipt. All correction
coefficients for these witnesses are zero. The program recomputes the entire
receipt and requires exact equality. No optimizer, random search, or imported
predecessor implementation is used.

Seed **40** selected the structural track and fixes target ordinal 40 in the
lexicographic port enumeration. The stopping rule is completion of the stated
finite domain; the program has no time-dependent search cutoff. Port symmetry
and the written proof cover other targets, while the explicit witness census
uses the recorded target. A `k=2,p=3` companion check tests the smallest case.

Seven controls reject a one-bit corrupted parity check, a forbidden degree-k
singleton, a zero decoder, restoring a required puncture, deleting the target,
an invalid coefficient mask, and applying the dual obstruction to `k=3`.
The last has a positive counterpart: `E_1+C_1` decodes the unpunctured `k=3`
target, showing why the power-of-two hypothesis matters. Checks use explicit
exceptions and remain active under optimized Python.

Validation on 2026-10-13 passed on Python 3.14.8, 3.12.15, and 3.11.15,
including isolated optimized execution. A separate Codex agent reviewed the
uniform argument, the rank construction and coverage semantics, replayed the
certificates, and checked all source hashes and Git blobs. The selected-record
integrity target and staged whitespace check passed. The repository-wide
`make verify`, selected supplier cold replay, Lean, and remote CI were not run;
this standalone package changes no existing generator, supplier or assembly.

## Cost interpretation and limits

For zero, one, or two deleted ports, even giving helpers, source access, frame
changes, copies, restoration, and recursive children zero cost cannot produce
the required scalar identity in this class. This rules out a proposed saving
from fewer punctures before any costly supplier implementation.

At three deletions, these are only scalar identities for one retained target.
There is no simultaneous all-target construction, geometric frame realization,
dirty-restoration program, complete paid recurrence, or assembly improvement
here. No helper or copy cost is inferred from the number of stars in a witness.
The theorem does not address nonlinear decoders, other correction classes,
other geometries, or the sharp global threshold when `p>k+1`.

The base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The selected accepted
conditional result is `51110230636731/31250000000000000`, or
`0.001635527380375392`, from #626 with #543. Its source construction and
maintainer review were followed; its all-size/compiler/common-label,
mutable-basis, hosting, residual, precision/tape, and analytic assumptions
remain. This note does not re-certify or change that construction.

## Provenance and attribution

[SOURCES.json](SOURCES.json) pins the base, selected context, retained #231 note,
and PR #669's actual head and README bytes. Those are mathematical/context
sources; the new checker imports none of their code. [CLAIM.md](CLAIM.md)
records candidate selection, the local claim, and the final overlap check.
PR #631 studies E8 root flats, #703 studies Hurwitz copy cost, and #669 leaves
the punctured off-target case open. This note resolves that case at `p=k+1`
and classifies the additional minimum patterns at `k=4,p=5`.

Credit Sam Sung / @the-missionary-company for #669's model, full-family dual
obstruction and local puncture theorem; Joel Pulikkan / GamingPuzzled for
#231's symmetric parity criterion; and icekylinx and eumemic for the preceding
paired-cube work. The accepted-frontier context credits Chafik Boukhalfa's
#626, Jeremy Kothe's #622/#623, eumemic's #543, and the cumulative lineage in
the maintainer review.

Prepared by **Sagar Thakrar / @thakrarsagar**, with substantial OpenAI Codex
assistance in proof development, implementation, documentation, and a separate
agent's mathematical review. No independent human review is claimed. New files
are under the repository's Apache-2.0 license.
