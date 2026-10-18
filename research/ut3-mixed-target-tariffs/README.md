# Exact tariffs for every mixture of UT3 targets

**Scoped negative theorem; no new kappa.** In the formal two-letter
`F2[UT_3(F2)]` register model, arbitrary mixtures of the eight address labels
cost exactly the sum of their separate direct bills. Free scalar mixing and
any finite number of restored dirty registers cannot lower either generator
count. The result permits all nonzero binary rank-one scalar couplings,
including nilpotents.

For a target `g_i=(x_i,y_i,z_i)`, with each coordinate in `{0,1}`, define

```
A_min = sum_i (x_i + 2(1-x_i)z_i)
B_min = sum_i (y_i + 2(1-y_i)z_i).
```

Every legal word uses at least `A_min` calls of `a` and `B_min` calls of `b`.
One direct word attains both bounds simultaneously. Thus fixed positive
per-letter prices `alpha,beta` give exactly `alpha*A_min + beta*B_min`.
The displayed counts use ordinary integer arithmetic, not arithmetic mod 2.

This extends steph4n-gh's [PR1573](https://github.com/CrocSwap/integer-mult-bounds/pull/1573)
and Arham Tahir's [PR1589](https://github.com/CrocSwap/integer-mult-bounds/pull/1589).
They prove the repeated central-target bill `4k`, first for idempotents and
then for arbitrary rank-one couplings. Their quotient and rank methods are
retained and credited. The new step handles **nonzero first-order endpoint
coefficients**, yielding separate sharp tariffs for every heterogeneous
endpoint, rather than only repeated central targets. For example, the mixture
`(a,b,c,aba,bab,ab,ba)` costs exactly eight a-calls and eight b-calls. No
predecessor executable or unproved predecessor conclusion is assumed.

## Model and complete abstract bill

Let `G=UT_3(F2)`, where `(x,y,z)` specifies entries `01,12,02` of an upper
unitriangular binary 3-by-3 matrix. Its multiplication is

`(x,y,z)(X,Y,Z)=(x+X,y+Y,z+Z+xY)`.

Here and throughout the proof, additions and products of matrix entries are
over `F2`. Put `a=(1,0,0)`, `b=(0,1,0)`, and `c=abab=(0,0,1)`.
For any finite `r >= w >= 1`, require the full formal endpoint

`T = diag([g_1],...,[g_w],1,...,1)` in `Mat_r(F2[G])`.

Every role has arbitrary input. In particular, the last `r-w` roles must be
restored as operators, not merely tested from zero. An allowed paid call is

`D_N(g) = I_r + ([g]+1)N`, where `g` is only `a` or `b`,
`N=u v^T`, and `u,v` are nonzero binary r-vectors.

Both `v^T u=1` (idempotent) and `v^T u=0` (nilpotent) are allowed, at one
optimistic unit each. Since `g^2=1`, `([g]+1)^2=0`; hence every such call is
an involution regardless of `N^2`. Arbitrary scalar `GL_r(F2)` maps are free.
There are no other free address operations, clean allocation, COPY, ERASE,
unpaid inverses, or higher-rank paid factors. This is the expanded abstract
screening alphabet of PR1589, not an implementation claim for the supplier.

Interleaved scalar maps can be collected at one end by conjugating the
rank-one couplings. Augmentation `[g] -> 1` sends every paid call and the
endpoint to `I_r`, so the remaining scalar map is `I_r`. Conjugation preserves
rank and stays inside the declared alphabet. It is therefore enough to bound
a product of paid factors. The conclusion also holds for a common scalar
conjugate of the whole endpoint.

The following coordinate words attain the two bounds. Apply each word to the
coordinate projector `E_ii`, and concatenate across target roles.

| `(x,y,z)` | Address word | a-calls | b-calls |
|---|---|---:|---:|
| `(0,0,0)` | empty | 0 | 0 |
| `(1,0,0)` | `a` | 1 | 0 |
| `(0,1,0)` | `b` | 0 | 1 |
| `(1,1,0)` | `ba` | 1 | 1 |
| `(0,0,1)` | `abab` | 2 | 2 |
| `(1,0,1)` | `bab` | 1 | 2 |
| `(0,1,1)` | `aba` | 2 | 1 |
| `(1,1,1)` | `ab` | 1 | 1 |

These are full formal identities: a coordinate factor acts by `[g]` on its
role and by identity on every other role. The bill uses `w` target roles,
zero extra workspace, the displayed paid calls, and no additional preparation
or restoration. Appending untouched roles gives any `r >= w`. The theorem
also applies to the idempotent-only alphabet, since the lower bound allows
more calls and the attaining words use idempotents.

## Proof: coefficient spans with nonzero first-order terms

Use the five-dimensional algebra

`Q = F2<X,Y> / (X^2, Y^2, all monomials of degree at least three)`.

The map on group elements is

`[x,y,z] -> 1 + xX + yY + zXY + (z+xy)YX`.

Substitution in the group law proves multiplicativity: the `XY` cross term
is `xY` and the `YX` cross term is `yX`. Extending linearly gives an algebra
homomorphism `F2[G] -> Q`. This is exactly PR1589's quotient, equivalently
PR1573's two small representations. It is used only for necessary conditions.
It is not faithful and cannot certify a formal endpoint.

Write a normalized word's quotient as

`I + AX + BY + CXY + DYX`,

where `A,B,C,D` are binary r-by-r matrices. Matrix factors keep their original
order. Collect all a-call column factors into `U` and row factors into `V`,
so `U` is r-by-`n_a`, `V` is `n_a`-by-r, and

`A = UV = sum_{a calls} N_i`.

Every `XY` term chooses an a-call followed by a b-call. Its matrix is
`N_i N_j`, whose image lies in the image of `U`. Thus

`rank [A C] <= rank U`.

Every `YX` term chooses a b-call followed by an a-call, so its row space
lies in the row space of `V`. Thus

`rank [A; D] <= rank V`.

Here `[A C]` denotes horizontal concatenation and `[A; D]` vertical stacking.
No commutation of the scalar matrices is used. Rank-nullity, or Sylvester's
inequality for the product `UV`, gives

`rank U + rank V <= n_a + rank(UV) = n_a + rank A`.

For completeness, restrict `U` to `im V`: its image has dimension `rank(UV)`
and its kernel has dimension at most `dim ker U = n_a-rank U`. This proves
the displayed inequality without a zero-product assumption. Consequently

`n_a >= rank [A C] + rank [A; D] - rank A`.                  (1)

Exchanging a and b gives

`n_b >= rank [B D] + rank [B; C] - rank B`.                  (2)

These two inequalities hold for any endpoint of a legal word, even one that
is not diagonal. They are the useful coefficient-span relaxation.

For the required diagonal endpoint, include the restored roles as triples
`(0,0,0)`. Then

`A=diag(x_i), B=diag(y_i), C=diag(z_i), D=diag(z_i+x_i*y_i)`.

The rank of `[A C]` is the number of indices with `x_i=1` or `z_i=1`.
The same is true of `[A; D]`: if `x_i=0`, the i-th entry of D is `z_i`;
if `x_i=1`, A already contributes that index. Substituting into (1), each
index contributes

`2 * 1_{x_i=1 or z_i=1} - x_i = x_i + 2(1-x_i)z_i`.

The analogous substitution in (2) gives `y_i+2(1-y_i)z_i`. These are the
two claimed lower bounds. The direct table attains both, completing the
proof for every target count, every finite dirty workspace, and every word
length. Positive uniform per-letter tariffs follow by weighting the two
inequalities. Prices depending on roles, chronology, or implementation
costs are outside that corollary.

The subtraction of `rank A` or `rank B` is essential. For a single target
`a`, there is one a-call and `rank A=1`; reusing the central-only zero-sum
inequality would falsely demand two calls. When all targets are `c`, both
first-order matrices vanish and (1)-(2) recover the predecessors' `2k+2k`
central bill. That special case is credited to the predecessors.

## Reproduction and finite evidence

Python 3.12 or later, standard library only, from the repository root:

```sh
python3 -I -O -B research/ut3-mixed-target-tariffs/verify.py
python3.12 scripts/research_package.py --package research/ut3-mixed-target-tariffs
```

Expected: `PASS_UT3_MIXED_TARGET_TARIFFS` and, for the registered command,
`PASS_REGISTERED_RESEARCH_PACKAGE`. Default replay is read-only. `--emit`
prints a fresh deterministic receipt; acceptance compares every field and
value type against [CERTIFICATE.json](CERTIFICATE.json).

The written argument above proves the unbounded statement. The finite checks
corroborate its definitions, inequalities and attaining words:

- All 64 group products verify the quotient homomorphism; all 32,768 triples
  of quotient elements verify associativity. Exact shortest paths independently
  check all eight address tariffs at four positive rational price pairs.
- All 4,369 pairs of binary matrices of shapes `2-by-n` and `n-by-2`,
  `0 <= n <= 3`, check Sylvester's inequality, including 3,735 nonzero products.
- All 111,151 words of length zero through four on two registers are checked
  in the expanded 18-factor alphabet. Both coefficient-span bounds hold;
  all 7,435 diagonal endpoint words satisfy the proposed separate tariffs.
- All 584 ordered one-, two-, and three-target mixtures have full formal
  witnesses with zero or one extra dirty role, both in the coordinate basis
  and after scalar conjugation: 2,336 fixtures and 62,848 basis columns.
  A ten-register fixture also checks all eight labels together, costing 8+8.
- [independent.py](independent.py) imports no local implementation. It uses
  literal binary 3-by-3 address matrices and the faithful 8r-dimensional
  regular action. Both implementations agree on complete witness operators
  and all 324 ordered two-factor products, using canonical SHA256 digests.
  It also checks 566 full paid involutions at r=2,3,4, including 258 nilpotent
  ones. Both implementations were authored in this session; this is not
  independent human review.
- Deleted calls and un-restored dirty roles give 3,925 rejected boundary
  mutations. Model controls exercise the nonzero first-order correction,
  noncommuting order, alphabet/rank restrictions and the nonfaithful quotient.
  In particular, a nonzero four-term off-diagonal perturbation has zero
  quotient image, is invisible on clean-extra inputs, and changes all eight
  dirty-extra basis columns in the faithful check.

Local validation passed on CPython 3.12.13 (registered replay, about 2.5
seconds) and CPython 3.14.6 (optimized, read-only standalone relocation).
A deliberately corrupted certificate was rejected under optimization; the
source package and read-only export stayed byte-identical during those checks.
Exact tested code hashes and validation scope are in TASK.json. Hosted CI is
separate from these local results.

This is a written scoped theorem with exact executable evidence, not a Lean
proof. Full selected-supplier cold replay, physical/compiler/common-label
realization, hosting, precision/tape and outer analytic transfer were not
checked. No selected record, frozen predecessor, or upstream source is changed.

## Provenance, overlap, and credit

The starting main commit is `ebedc0895eb4c06725af020bc1af165722b0a3ce`.
The catalogue chose `bit-new-register-model` in the bit-mechanisms track,
nonce `4aba18fcd52cd4290d0badf705c2dfc3`, priority revision 2. The selected
PR1094 baseline binding check passed; its conditional kappa is unchanged.
[TASK.json](TASK.json) contains the refined scope, stopping rule and overlap
coverage. [SOURCES.json](SOURCES.json) pins the base inputs and contextual
predecessor texts. The contextual remote files are not runtime dependencies.
Coordination: [Discussion1599](https://github.com/CrocSwap/integer-mult-bounds/discussions/1599).

The nearest predecessors are PR1573 at
`0b8c5a69297c794f2de22c04494c83e41300ae36` and PR1589 at
`010ec8c01c0edbbb08b541be236ab78d096f2ca1`; both explicitly restrict their
conclusions to central targets. Hanson's PR1567 treats mixed GL3 targets
with six coordinate letters on exactly two registers by finite enumeration;
it is a different alphabet and method, not a dependency. The all-target UT3
conclusion here follows analytically and permits arbitrary finite workspace.
The final refresh covered 733 open PRs and 244 discussion records with
complete pagination and no warnings, at 2026-10-14 03:52 UTC. Before submission,
the branch was rebased onto main `81e81af67714bdc8d1693b0bf5c29468b92f62ff`;
priority revision 3 leaves this bit task and the selected record unchanged.
Search coverage is not a claim of literature priority.

Credit steph4n-gh (PR1573) and Arham Tahir (PR1589) for the central all-register
bounds, quotient and rank methods; @juper997 (PR1478) and @woklerx (PR1443) for
the finite UT3/D8 predecessors; Gareth Davidson / @bitplane (PR1333) for the
nonabelian register direction and scalar normalization; and the retained
@eumemic, Ali Romman, David Govea and @commdata2338 register-model lineage.
No novelty is claimed for Sylvester's inequality or the quotient itself.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex
assistance** in proof, implementation, validation and writing. No subagents or
independent human proof review. Apache-2.0.

## Open next questions

Can a different, fully priced nonabelian address alphabet escape these bills?
The mixed-target and workspace-only routes in the stated UT3 alphabet are
settled by the theorem. A feasible first step is to specify one additional
physically realizable address primitive, compute its first- and second-degree
coefficient matrices, and charge its rank, frames and restoration. The blocker
is the actual supplier interface: declaring another label to cost one does not
establish a usable improvement. This package does not claim a stronger
obstruction for that changed alphabet.
