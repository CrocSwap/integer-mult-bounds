# Infinite dihedral targets: exact separate reflection bills with dirty workspace

**Scoped negative theorem, no new kappa.** Let
`G = <x,y | x^2=y^2=1>`, let `r=xy`, and write each target uniquely as
`g_i=r^{k_i} x^{e_i}`, with `k_i` an integer and `e_i` in `{0,1}`.
For every finite register count `R >= W`, the exact formal endpoint

```
diag([g_1], ..., [g_W], 1, ..., 1)
```

requires at least `A=sum_i |k_i+e_i|` paid **x** calls and
`B=sum_i |k_i|` paid **y** calls. A direct word simultaneously attains both
bounds. Positive per-label prices `alpha,beta` therefore give the exact bill
`alpha*A + beta*B`; in unit prices it is `A+B`.
In particular, arbitrary signed rotation powers cost `2 sum_i |k_i|`, even
with arbitrarily many restored dirty registers. This is a uniform written
proof, not an extrapolation from a finite word census or finite columns.

## Alphabet, boundary, and changed premise

Work in `M_R(F2[G])`. A paid call is
`D_N(g)=I+([g]+1)N`, where `g` is **only x or y** and
`N=u v^T` is a binary rank-one idempotent (`v^T u=1`). Scalar `GL_R(F2)`
changes are allowed free in this optimistic paid-call relaxation. No other
address maps, direct rotation primitive, erasure, COPY or clean state are
free. All W target inputs and all R-W workspace inputs are arbitrary dirty
data. Every workspace input must be restored, with no residual target coupling.
Every paid restoration call counts. This explicitly replaces the rational
abelian frame group of the three-register obstruction by a nonabelian group;
it does not reduce rational frames modulo two.

Free scalar mixing can be normalized away: commute it through the paid calls,
conjugating N within the complete projector alphabet. Augmentation `[g] -> 1`
forces the final scalar matrix to be I. Hence it suffices to bound products of
paid calls alone. This standard normalization is credited to the retained
register-model lineage, not claimed as a new result.

## Uniform lower-bound proof

Put `L=F2[t,t^-1]`, and define two group representations by

```
C = [[0,1],[1,0]],   V = [[0,t],[t^-1,0]],
rho(x)=C, rho(y)=V;   sigma(x)=V, sigma(y)=C.
```

Both C and V square to I, so these are representations of the presented
infinite dihedral group. They induce algebra maps on every formal coefficient.
No converse from represented equality to formal equality is used.

For an invertible Laurent matrix M, let `delta(M)` be the maximum Laurent
degree of every nonzero square minor of M, over **all sizes**, including the
empty minor 1. Thus delta is nonnegative. Cauchy--Binet gives

```
delta(AB) <= delta(A)+delta(B).
```

Indeed each minor of AB is a sum of products of equal-sized minors of A and B;
cancellation can only decrease degree. Every invertible constant binary matrix
and its inverse have delta zero. Applying the inequality in both directions
shows delta is unchanged by constant invertible left or right multiplication.

A rank-one idempotent N is scalar-similar to `diag(1,0,...,0)`: its image and
kernel give a direct sum since N is idempotent. After applying rho or sigma,
a represented paid call is therefore constant-similar to `diag(C,I)` or
`diag(V,I)`. Every minor of `diag(C,I)` is constant. The only nonzero minors
of V have degrees `1,-1,0`; its determinant is 1. Minors of `diag(V,I)` are
zero or products of these with identity minors. Consequently

```
delta(rho(D_N(x)))=0,  delta(rho(D_N(y)))=1;
delta(sigma(D_N(x)))=1, delta(sigma(D_N(y)))=0.
```

For the endpoint, `rho(r)=diag(t^-1,t)` and
`sigma(r)=diag(t,t^-1)`. The block for `r^k x^e` is a monomial permutation
matrix with its two nonzero exponents `-k,k` under rho and
`k+e,-(k+e)` under sigma. A nonzero minor of a monomial permutation matrix
selects some of its nonzero entries, with distinct rows and columns. Its maximum
degree is exactly the sum of positive exponents: select all positive entries
for equality, and none of the negative ones. Identity spectator blocks add
zero. Thus the two endpoint deltas are respectively B and A. Subadditivity
now gives `#y >= B` and `#x >= A` for **every word length and every R**.

## Uniform attaining identity and complete invoice

For a fixed coordinate projector E_i, idempotence directly gives
`D_{E_i}(g)D_{E_i}(h)=D_{E_i}(gh)` in the full group algebra. Calls on distinct
coordinate projectors commute. On role i use the freely reduced literal word
`(xy)^{k_i} x^{e_i}` (negative powers mean repetitions of yx). For `e_i=0`
it has `|k_i|` of each label; for `e_i=1`, it has `|k_i+1|` x labels and
`|k_i|` y labels. This proves the endpoint uniformly as a formal identity,
with the stated matching bills. No representation is used to certify this
upper bound.

Products use the usual left-action convention: the rightmost factor acts first.
To execute a displayed word as successive in-place address permutations, run
its letters from right to left. This does not change either label's invoice.

| Resource | Attaining implementation |
|---|---|
| Arbitrary target registers | W; all input data retained under specified permutations |
| Dirty workspace | R-W allowed by theorem, **zero needed** by attaining word |
| x calls / y calls | A / B, including all endpoint work |
| Free scalar basis changes / scalar row additions | Zero in the attaining word |
| Clean allocation, COPY, frame preparation, extra restoration | Zero in this formal implementation |
| Direct rotation or arbitrary address call | Not admitted |

A concrete action is `x(a)=-a`, `y(a)=-a-1` on integer addresses; `r(a)=a+1`.
The formal identity holds under every action of G, including cyclic addresses
`Z/LZ` for every L. For a concrete finite in-place bit-array implementation,
store W arrays of L bits (plus any explicitly retained spectators), use the
fixed schedule above, and implement each reflection by disjoint swaps. For odd
L each reflection fixes one address and uses `(L-1)/2` swaps; hence the witness
uses exactly `(A+B)(L-1)/2` bit swaps, at most
`3(A+B)(L-1)/2` XOR assignments with the three-XOR swap, no clean data bit,
and O(log L + log(1+max |k_i|) + log(1+W)) address/counter bits. For even L,
x fixes two addresses and y fixes none, giving `A(L-2)/2+B L/2` swaps.
This invoice describes this witness, **not** an optimal physical finite-array
algorithm: finite cyclic quotient relations admit shortcuts absent formally.

No bridge makes these paid reflections admissible native bit-supplier children.
Frame/compiler, hosting, precision/tape, recursive coverage and analytic transfer
are unestablished, not zero-cost claims about the selected construction. Since
there is no formal saving even with scalar mixing priced at zero, this alphabet
fails the local compression target before those nonnegative adoption costs.
The selected complex supplier still binds; no frontier file is changed.

## Reproduce and evidence scope

```
python3 -I -O -B research/infinite-dihedral-register-bound/verify.py
uv run --python 3.12 --no-project scripts/research_package.py --package research/infinite-dihedral-register-bound
```

The standard-library verifier checks the complete projector sets for R=1,2,3,4,
call involutions, all-minor degrees for R<=2, and two independent group laws:
integer-affine normal forms and literal free reduction of x/y words. All 144
two-call words over the full two-register projector alphabet are checked with
both formal engines and both represented degree bounds, including mixed
non-coordinate projectors. It also verifies
100 heterogeneous two-target formal endpoints with exponents in [-2,2], plus
four- and seven-register signed fixtures, exact per-label invoices, every
single-call omission, wrong order/label and dirty-restoration controls. A
finite-quotient alias control demonstrates why finite columns cannot establish
this lower bound. Checks use explicit exceptions and remain active under -O.
The checker corroborates finite instances; the universal conclusion comes from
the proof above. Neither proof-assistant nor independent human review is claimed.

Observed initial verification on 2026-10-14, macOS arm64, CPython 3.12.12:
metadata/pins passed; registered isolated optimized replay passed in 0.23 s;
direct isolated unoptimized replay passed in 0.13 s. Both emitted
`formal_targets=102`, `generator_minor_checks=28`, `omission_controls=540`,
`other_controls=4`, `projectors=155` and `PASS_INFINITE_DIHEDRAL_REGISTER_BOUND`.
The publication replay additionally passed `mixed_words=144`; registered
optimized replay took 0.29 s and direct unoptimized replay took 0.18 s.
Timings are observations, not performance guarantees. No selected cold replay
was run; the prescribed source-binding positive control passed separately.

## Sources, overlap, and credit

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Local predecessor byte pins are in SOURCES.json. Credit eumemic PR288 for the
scalar-idempotent model, Ali Romman PR468 and the retained three-register note,
woklerx PR1443 for the D8 formal-alphabet predecessor, Gareth Davidson PR1333
for the nonabelian affine direction, and the subsequent all-register work.

Closest live work, inspected by complete PR or discussion bodies:

- [PR1573](https://github.com/CrocSwap/integer-mult-bounds/pull/1573), steph4n-gh,
  head `0b8c5a69297c794f2de22c04494c83e41300ae36`: already proves all-register
  D8 central targets cost 4k, with separate label tariffs. We do not claim that
  conclusion anew. Its finite-group zero-projector-sum proof differs from the
  Laurent minor-degree proof here; infinite rotations have no torsion relation.
- [PR1478](https://github.com/CrocSwap/integer-mult-bounds/pull/1478), juper997,
  head `b30fdba48f3db70e3589ba740b0782b56ec0ba2e`: D8 with R=2,3, superseded
  in register scope by PR1573.
- [PR1821](https://github.com/CrocSwap/integer-mult-bounds/pull/1821), Cinna Davis,
  head `a986127fa82b680a5bbb29f49fec4c8c3a944bde`: D16 central pair, R=2,
  exact 16-call search. Our Laurent representation does **not** factor through
  that finite group, so our theorem does not generalize its result.
- [PR1733](https://github.com/CrocSwap/integer-mult-bounds/pull/1733), Cinna Davis,
  head `01ac3f397eaaa9f7a72ecafc7f0fbf128571424a`: four rational registers,
  fixed 15-address two-relation ansatz, finite negative census. Different group,
  target and method; not reopened here.
- [PR1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822), Aaron Wang,
  head `ee736b4b11bbd63b04d94c8edafb3790161ebdea`: Q8 central and mixed pair,
  R=2,3. Different finite group and label-square relation.

Overlap helper snapshot on 2026-10-14 13:15Z covered 540 open PRs (including
drafts) and 524 discussions with complete pagination. Exact `infinite dihedral`,
`Laurent`, `dihedral` search returned no infinite-dihedral match; this is not
proof of novelty. Closed PR coverage is only through local notes/ledger, and
arbitrary code diffs were not searched. Live heads and claims remain provisional.
Before publication, an offline exact-term recheck at 13:42Z used the shared
cache covering 543 open PRs (13:23:53Z) and 529 discussions (13:25:07Z),
both completely paginated. Only this local package matched `infinite dihedral`;
the helper explicitly warned that cached records may miss current changes.
Parent coordination: [Discussion1884](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884).
Prepared for Adam Gall with substantial OpenAI Codex assistance in the proof,
implementation, overlap investigation and writing. Apache-2.0.

## Open next questions

1. Can a finite-dihedral torsion-aware substitute for maximal-minor degree give
   arbitrary-register lower bounds for powers beyond the D8 result? This would
   close the workspace gap in the D16 census. First test the proposed invariant
   on the relation `(xy)^n=1`; the Laurent invariant here fails precisely there.
2. Is either reflection a justified native supplier operation at the claimed
   unit tariff? First derive its actual all-size compiler and full interface
   invoice. No such bridge is supplied; without it this remains a formal-model
   side result, not a multiplication improvement.
