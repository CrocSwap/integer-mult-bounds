# QQ16: fifteen-coordinate linear records still lose selected inputs

For the fixed QQ16 `F0/B_1_2` erasure and observation contract, every
read-only rational-linear record with at most **fifteen scalars per
regular-cover owner fails** to restore the original selected inputs.
The new exact fourth moment gives

```text
tr(T^4) = (1823/36)|G|,
rank([B0;B1;B2]) >= (117/5)|G|,
selected A/T defect dimension >= ceil((77/5)|G|).
```

A rank-d record leaves at least `max(0,ceil(77|G|/5)-d)` selected
input dimensions invisible. At width fifteen the residual is at least
`ceil(2|G|/5)>0`. Thus an integer number of coordinates per owner must
be at least **sixteen**, strengthening the necessary width fourteen
from Nick Petalas's [PR #2181](https://github.com/CrocSwap/integer-mult-bounds/pull/2181).
This is a scoped proof with exact finite certificates, author-checked
by two different calculations. It is not an independently reviewed or
formalized theorem, a physical cost bound, or a new supplier or kappa.

The claim is in [discussion #2074](https://github.com/CrocSwap/integer-mult-bounds/discussions/2074#discussioncomment-18935517),
following #2181's higher-moment handoff. The record encoder is linear;
the decoder may be arbitrary. Fixed offsets and common dirty baselines
are allowed. Changed first pairs, changed ordinary trajectories,
nonlinear encoders and uncounted independent payload storage are excluded.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-fourth-moment-capacity
```

The hook runs the primary certificate, the separate block-Gram oracle,
and the semantic/artifact controls in normal and optimized modes. Direct
read-only replay, also usable in a source export:

```sh
python3 -I -O -B research/qq16-fourth-moment-capacity/verify.py
python3 -I -O -B research/qq16-fourth-moment-capacity/oracle.py
```

Expected lines include:

```text
PASS_QQ16_FOURTH_MOMENT_CAPACITY moment4=1823/36 rank>=117|G|/5 defect>=77|G|/5 width>=16 no_new_kappa
PASS_QQ16_BLOCK_GRAM_ORACLE moments=24,28,109/3,1823/36 blocks=9
```

[RESULT.json](RESULT.json) contains the exact pair-product census, its
six full-matrix digests, all stage-word counts and rational coefficients.
[SOURCES.json](SOURCES.json) pins the immutable main inputs; pending PR
checkouts, network access and third-party modules are unnecessary.
[TASK.json](TASK.json) records the scope change and exact predecessor heads.

## 1. Operators and finite premises

Use the actual 96 ordinary ports U and the three query operators
`B_s=R_s iota_U`, for s=0,1,2, of Ali Romman's retained
[joint-query package](../joint-query/README.md). Let G be a finite group
containing the literal owner-route matrices, acting regularly, and put
N=|G|. As in the inherited witness, restrict to fields constant in each
payload block: payload translations disappear, but arbitrary owner
values remain. This is not a quotient that identifies distinct routes.
The packet-to-native interpretation remains inherited.

For ordinary port p, write r_p for its eight-component integer column
and g_s(p) for its owner route. The pinned packet checks establish

```text
g_0(p)=1,     g_s(p)^2=1,
r_p^T r_p=4,                 sum_p r_p r_p^T=48 I_8.
```

The stage-1 and stage-2 routes act on the first 25 binary axes and fix
the remaining 48 of the original 73 axes. The shared source binder
checks the entire 73-column input, the common orthonormal chart-swap
form, the A/T/U partition, both selected Grams, and agreement between
F1/F2 and the current/future B_1_2 alignment maps. Its extraction and
chart checks are adapted, with credit, from #2181.

Let `h_st(p)=g_s(p)g_t(p)^-1` and
`C_st(p,q)=h_st(p)h_st(q)^-1`, for each ordered s!=t. A new exhaustive
exact binary-matrix census checks all **6*96^2 = 55,296** ordered products:

* Each of the six tables has 9,121 distinct products. Its identity
  fibre is precisely the 96 diagonal pairs `(p,p)`; every other fibre
  is a singleton.
* For every s, with t and u the other two stages, the images of C_st
  and C_su intersect only in the identity.

All port pairs are included, even when their scalar coefficient is zero.
Matrix equality is on all active axes with the spectators checked as
fixed. No enumeration of the huge group G or probabilistic hashing is
used for equality; the digests are portable receipts of exact tables.

Under the regular right action `Q_g f(d)=f(dg)`, `tr Q_g` is N for the
identity and zero otherwise. Put

```text
P_s=B_s*B_s/48,        T=P_0+P_1+P_2.
```

Since `B_s B_s*=48 I_(8N)`, each P_s is an orthogonal projection of
rank 8N. Moreover `rank T=rank [B0;B1;B2]`. All matrices are rational,
so real and rational ranks agree.

## 2. The fourth trace

Set `M_st=B_s B_t*` and `A_st=M_st M_ts`. The coefficient of A_st at
route C_st(p,q) is contributed by

```text
(r_p^T r_q) r_p r_q^T.
```

At the identity, summing the diagonal fibre gives `192 I_8`. All other
coefficients have a unique ordered pair. For a self-adjoint group-algebra
matrix A, its regular trace satisfies

```text
tr(A^2)/N = sum_g ||A[g]||_F^2.
```

Here the full root Gram square sum is
`sum_(p,q) (r_p^T r_q)^2 = tr((48 I_8)^2)=18432`; the diagonal contributes
`96*16=1536`. Therefore, for s!=t,

```text
tr(P_s P_t P_s P_t)/N
 = [8*192^2 + 16*(18432-1536)]/48^4
 = 565248/5308416 = 23/216.                         (1)
```

For distinct s,t,u the two A tables have only the identity in common.
The group-coefficient Frobenius inner product consequently gives

```text
tr(P_s P_t P_s P_u)/N = 8*192^2/48^4 = 1/18.       (2)
```

The lower moments retain #2104/#2181's argument. Relative routes are
distinct, so `tr(P_s P_t)/N=1536/48^2=2/3`. In a distinct-stage triple,
the identity condition is
`g_1(p)g_1(q)=g_2(r)g_2(q)`. The checked product intersection and identity
fibres force p=q=r. Thus the triple trace is `96*4^3/48^3=1/18`.
Cyclic invariance and transpose cover its six orderings.

Cyclic removal of adjacent repeated projections partitions all 81
stage words of length four as follows. These are traces, so the first
and last letters also count as adjacent.

| Reduced type | Count | Trace divided by N |
|---|---:|---:|
| one stage | 3 | 8 |
| two adjacent stages | 36 | 2/3 |
| three distinct stages | 24 | 1/18 |
| alternating `s,t,s,t` | 6 | 23/216 |
| repeated-stage `s,t,s,u`, all three stages used | 12 | 1/18 |

Their sum is `1823/36`. The complete first four moments are

```text
(tr T, tr T^2, tr T^3, tr T^4)/N = (24,28,109/3,1823/36).   (3)
```

### Separate contraction oracle

[oracle.py](oracle.py) does not assume the collision classification,
use the primary binary multiplication, or reduce cyclic stage words.
It shares only the credited source binder. It converts routes to binary
row matrices and explicitly forms every group coefficient of the nine
blocks of `C^2`, where `C=(B_s B_t*)_(s,t)` is the 24N-dimensional
block Gram matrix. The two rank-one factors multiply as
`r_p(r_p^T r_q)r_q^T`; equal-stage blocks are `48I`.

Because C is self-adjoint, coefficient Frobenius contractions compute
`tr(C^2)`, `tr(C^3)=<C,C^2>` and `tr(C^4)=||C^2||_F^2`. Dividing by
48^k gives (3), since C/48 and T have the same nonzero eigenvalues.
For the fourth trace each diagonal block contributes 1187/108 and each
off-diagonal block 53/18. Their total is again 1823/36. This is a second
implementation and method, not an independent human review.

## 3. Rational spectral certificate

For every real t,

```text
p(t) = 1-(1-81t/40+9t^2/10)^2 <= 1,       p(0)=0
     = (81/20)t-(9441/1600)t^2+(729/200)t^3-(81/100)t^4.
```

Apply this inequality to each nonzero eigenvalue of T. The zero
eigenvalues contribute zero. Equation (3) gives

```text
rank T >= tr p(T) = (117/5)N.                         (4)
```

No floating-point extremization is used for acceptance. The coefficients
come from the exact 2x2 moment system
`[[28,109/3],[109/3,1823/36]] [a,b]^T=[24,28]^T`, giving
`a=81/40,b=-9/10`, then `p=1-(1-a t-b t^2)^2`. The checker verifies the
polynomial identity and the rational trace evaluation exactly.

## 4. Inherited selected-input implication

This is the joint-defect argument of this account's
[PR #2153](https://github.com/CrocSwap/integer-mult-bounds/pull/2153),
restated to make the contract explicit. For h in `V=ker B1`, use only
pair 0 and set

```text
X_U=h,                         Y_U=0,
X_A=-P_(0,A)B0h-P_(2,A)B2h,    Y_A=-X_A,
X_T=P_(0,T)ell_(0,A)P_(2,A)B2h, Y_T=-X_T.
```

All other banks and helpers are zero. The original selected defect
`J(h)=(X_A,X_T)` determines and is determined by `(B0h,B2h)`:

```text
B0h=-ell_(0,A)X_A-ell_(0,T)X_T,
B2h=ell_(2,A)P_(0,A)ell_(0,T)X_T.
```

The two-sided selected inverse relations preserve the displayed order.
Consequently

```text
dim J(V)=rank([B0;B1;B2])-rank B1 >= ceil(77N/5).       (5)
```

The original QQ16 witness establishes, for every such h, zero F0 query
and zero selected state after B1, with only Y_(0,U)=h remaining. Its
retained ordinary tail moves h into the former-Y hole. The allowed old
observations—selected values after B1 and later selected-only descendants,
completed-X descendants, and all five forward histories—are zero.
An independently saved transient F0 A value or a read of the former-Y
hole is additional information, not part of those old observations.
This trajectory and native-frame interpretation are inherited from the
pinned witness and rational review, not newly replayed by this package.

If C is the restriction of an added record to V and rank C<=d, then
`dim J(ker C)>=dim J(V)-d`: a complement of ker C has dimension at most d
and its J-image adds at most d dimensions. Combining with (5) proves
the stated residual. Positive residual gives two inputs with identical
records and different required selected outputs; no decoder can
separate them. Common dirty baselines and fixed affine offsets cancel
when comparing the two executions.

A q-coordinate record with one rational scalar per owner has capacity
at most qN. Every integer q<=15 fails. The inherited sixteen-coordinate
record `(B0 X_U,B2 X_U)` recovers this particular erased family, so its
integer-coordinate threshold is sixteen. This does not compute its
exact defect dimension, which lies between `ceil(77N/5)` and 16N.

The lower bound also applies when all post-B1 selected values are
granted, as in [PR #2174](https://github.com/CrocSwap/integer-mult-bounds/pull/2174).
It therefore matches that PR's sixteen-coordinate logical upper bound
for pair 0 **under its explicit recorded-cut premise**. Its full-input
recovery proof is credited, not rerun or promoted to a final-only
controller here. Sixteen information coordinates are not sixteen paid
recursive ranks.

## Verification limits

The finite route facts, all four moments, polynomial identity and
rejection controls are executed. The spectral and capacity arguments
are written proofs. The two implementations share the source binder;
no formal kernel or independent human review is claimed. No full QQ16
native replay, selected frontier cold replay, final-only controller,
compact actual-cover null vector, precision bound, chronological hosting,
physical record implementation or completed supplier bill was checked.
All source packages and the selected record remain unchanged.

## Open next questions

1. **Can an actual final-only controller recover the post-B1 selected
   cut values used by #2174?** Trace one literal selected program and
   express its cut values in its final observations. This is the missing
   access premise; the integer width gap for the erased family no longer
   motivates more moment searches.
2. **What is the completed native bill for the sixteen-coordinate
   record and #2174's decoder?** Start by jointly pricing both pre-F0
   ordinary reads and the completed-X B2 read in their actual endpoint
   frames. Record retention, dirty restoration, hosting, tape and
   precision remain blockers. Stop construction if even the favorable
   complete bill misses its target.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New material is Apache-2.0.

Ali Romman and the contributors in [joint-query/NOTICE.md](../joint-query/NOTICE.md)
supplied PR #1969's maps, ordered sections, actual routes and witness
(head `a6e6ad3936f67b8f63b5b68c5e75d540610a65e7`). Ross Richardson's
PR #2104 (`4bdc574da394a39f955e8cf4637075649c43a632`) supplied the
rank-moment method. Nick Petalas's PR #2181
(`e18ca76987f5945c6a4b5b6bebbe73cdab3c4561`) supplied the third moment,
the polynomial approach and the source binder adapted here. This
account's PR #2153 (`5646398dcdc01769df83b939c6b3eb5ecb4d5ebd`) supplied
the joint A/T defect transfer; PR #2174
(`f79470a7931f3943360c10d15b428e0e4e479c22`) supplies the distinct
recorded-cut recovery upper bound. Cinna Davis's #2079/#2122 and Adam
Gall's #2086/#2093 are adjacent observation obstructions. Rohan Arun,
Jeremy Kothe and the retained geometry/native/hosting lineage keep
their existing attribution. The new contribution is the fourth moment,
its separate contraction oracle, and the stronger transcript bound.
