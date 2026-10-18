# The P112 right-space extension with free correction has sharp bill 8*8^q

The ten-term boundary in [PR2398](https://github.com/CrocSwap/integer-mult-bounds/pull/2398)
leaves the minimal right factor space and pays eight rank-eight COPY charges,
with two zero-COPY corrections. **No factorization in the following extended
free-correction class does better:** its sharp separate COPY-power minimum is
`8*8^q` for every real `0<q<=1`, including COPY 64 at `q=1`.

The left factors may lie anywhere in `col_C(X,e0)`, the right factors anywhere
in `col_C(X,e0,e1)`, and there may be any finite number of terms. The restriction
is that every term whose left or right eight-dimensional root projection is
zero must have COPY rank zero. This is a restriction on **pure-projection
terms**, not on all added terms or term count. Redundant mixed terms are allowed.

This answers one concrete part of PR2398's proposed one-dimensional right-space
extension. PR2398 proves a different sharp bound inside both minimal factor
spaces and supplies the credited ten-term boundary used here. The new result
is the extended-space classification and all-length free-correction lower
bound. **Positive-COPY pure terms remain outside this theorem.** No physical
supplier or improvement to the selected multiplication exponent is claimed.

## Exact model

Use the pinned root prototype and original binary labels. Delete its first
eight frame rows, obtaining `X` of size 112-by-8. Write `e=e0`, `f=e1`,
`s=X[0,:]^T`, `t=X[1,:]^T`, and `G=XX^T`. The fixed matrix is

```
K = G - (Ge-4e)e^T + ef^T.
```

It is the PR2021/PR2321/PR2398 completion for ports `(0,1)` and coefficient
`+1`. All required binary-mask entries equal those of `G`. The original right
space is `col([(I-ee^T)X,4e+f])`; adjoining `e` gives exactly
`col(X,e,f)`, of dimension ten. The left space has dimension nine. We write
each term uniquely as

```
D_i = X a_i + c_i e,
T_i = X b_i + u_i e + v_i f.
```

All coefficients are complex and all transposes ordinary. Charge the term by
`rho_i = rank_F2 B[supp(D_i),supp(T_i)]`, where `B_ij=lambda_i dot lambda_j`.
Zero physical factors may be removed. A term is *mixed* if both `a_i,b_i` are
nonzero, and *pure* otherwise. The theorem requires `rho_i=0` for every pure
term. This does not assume that mixed factors are inside the smaller spaces.

## Complete finite support facts

For each of all 511 nonzero binary characters `h`, the checker computes the
kernel of the rows of `[X,e]` or `[X,e,f]` whose labels have `h.lambda=1`.
These are exactly the coefficient vectors supported in `h^perp`. Exact
rational RREF is checked against a separate modular-rank lower bound and
literal integer annihilation for every kernel. The latter certifies exact
nullity over characteristic zero without trusting the rational eliminator.
Rational kernel identities extend to complex coefficients.

For a nonzero root projection, the complete catalogue of proper support spans
is as follows. `F_j` denotes the label of removed coordinate root `2e_j`.

| Side | Root projection | Required extra coefficient | Support span |
| --- | --- | --- | --- |
| left | multiple of coordinate `e_j` | any permitted `c e` inside `F_j^perp` | `F_j^perp` |
| left | `a=gamma s` | `c=-4gamma` | `lambda_0^perp` |
| right | multiple of coordinate `e_j` | any permitted `u e+v f` inside `F_j^perp` | `F_j^perp` |
| right | `b=gamma s` | `u=-4gamma`, arbitrary `v` | `lambda_0^perp` |
| right | `b=gamma t` | `v=-4gamma`, arbitrary `u` | `lambda_1^perp` |

Here `gamma!=0`; all other non-pure vectors have full binary support span.
The exact kernels specify the permitted coordinate extras without ambiguity.
No pair of distinct character kernels shares a nonzero root projection,
checked in all 81 relevant pairs, so every displayed span has dimension eight
and cannot secretly have smaller rank.

Pairing two hyperplanes has rank seven or eight; pairing a hyperplane with the
full space has rank eight, and full/full has rank nine. All 110 class pairs
are checked by two binary elimination directions. Coordinate/coordinate costs
eight. Consequently every mixed term costs at least seven, and a cost-seven
term must have left projection in `Cs`, right projection in `Cs`, or right
projection in `Ct`. Left/right `Cs` together cost eight, not seven.

The complete zero-COPY pure classification gives just the linear span of
these three matrix generators:

```
(Xs-4e)e^T,       e(Xs-4e)^T,       ef^T.                (1)
```

Indeed, left-pure means a multiple of `e`, so the right factor must annihilate
`lambda_0`; its kernel is `span((s,-4,0),(0,0,1))`. If the right factor is pure,
its support is `e`, `f`, or both. The left annihilator kernels are respectively
`C(s,-4)`, `Ce`, and their zero intersection. This exhausts zero-COPY pure terms,
including arbitrary complex cancellations and arbitrary term count.

## All-length lower bound

Only mixed terms contribute to the root/root coefficient block of `K`:

```
sum_i a_i b_i^T = I_8.                                  (2)
```

Thus there are at least eight mixed terms.

If there are at least nine, all cost-seven contributions to (2) sum to a matrix
of the form `s x^T + y s^T + z t^T`, of rank at most three. There must therefore
be at least five other mixed terms, each costing at least eight. In particular
the bill dominates one rank-eight and eight rank-seven charges. The profile
`(8,8,8,8,8,8,8,8,0)` majorizes `(8,7,7,7,7,7,7,7,7)`; both sum to 64.
Concavity of `x^q` therefore gives a bill at least `8*8^q`. Extra terms have
nonnegative cost. This part even allows charged pure terms.

It remains to consider exactly eight mixed terms. Let `A=[a_i]`, `B=[b_i]`.
Equation (2) makes them dual bases: `AB^T=I_8`, `b_i^T a_j=delta_ij`.
Combine all free pure terms using (1), with coefficients `alpha,beta,gamma`.
Independence of `[X,e]` and `[X,e,f]` permits coefficient comparison. The
root/e, root/f and e/root blocks give respectively

```
u_i = -(1+alpha) b_i^T s,
v_i = 0,
c_i = -beta a_i^T s.                                    (3)
```

The e/e block, using `s^T s=4`, is

```
sum_i c_i u_i -4alpha -4beta = 4,
4beta(1+alpha)-4alpha-4beta = 4,
alpha*(beta-1) = 1.                                     (4)
```

In particular `alpha!=0` and `beta!=1`. The e/f block fixes `gamma=1`.
Every possible cost-seven case now contradicts (3)–(4):

- A left exceptional factor has `a_i=delta s`, `c_i=-4delta`, forcing `beta=1`.
- A right `s` factor has `b_i=delta s`, `u_i=-4delta`, forcing `alpha=0`.
- A right `t` factor requires `v_i=-4delta!=0`, contradicting `v_i=0`.

Thus all eight mixed terms cost at least eight. Together with the previous
case this proves the universal scoped bound. The coefficient argument is
written mathematics; finite checks do not constitute a formal proof-kernel
verification of it.

## Sharpness, independent checks and boundary controls

The credited PR2398 identity

```
K = sum_j X[:,j] X[:,j]^T + (4e-Xs)e^T + ef^T
```

attains eight rank-eight charges and two free terms. We check all 12,544
entries and actual supports. Four additional exact witnesses use
`alpha=1,2,-2,1/2`, `beta=1+1/alpha` in (3), with coordinate dual bases and
the three free terms (1). Each has profile `(8 x 8, 0,0,0)`.
A twelve-term witness adds a nonzero cancelling mixed pair, showing that the
scope is not restricted to eight mixed terms. An exact Gaussian phase and
reciprocal check also distinguishes ordinary from Hermitian transpose.

Eight rejecting controls cover changed source bytes, an altered compensation,
an omitted free term, a **valid exact factorization containing charged pure
terms**, a false new kernel direction, an undercharged exceptional pair and
the two forbidden coefficient choices. The charged-pure control is accepted
as an algebraic identity and rejected only at the theorem's explicit boundary.
The default replay compares the entire structured receipt. Boundary tests
also exercise wrong/missing receipt, source drift and unchanged Git-free export.

```sh
python3.12 -I -O -B research/p112-free-right-extension/verify.py
python3.12 scripts/research_package.py --package research/p112-free-right-extension
```

Standard library only. Default commands write no evidence. `--out NEW.json`
regenerates exclusively and refuses to overwrite. On Windows TEMP/TMP may
need a writable workspace directory. The prescribed selected baseline binding
check passed; a selected supplier cold replay is not claimed.

## Open next questions

Can positive-COPY pure terms in this same extension beat `8*8^q`? The proof
already excludes nine or more mixed terms without the free-pure restriction,
so the next useful case has exactly eight mixed factors and charged pure
compensation. Start from the complete new character kernels and price those
terms explicitly. Enlarging both factor spaces, sharing COPY work physically,
native frames, dirty restoration, chronological hosting, precision and all-size
admission are separate obligations. This package supplies no completed local
physical profile, 5% ceiling-gate improvement, supplier or new kappa.

## Provenance and credit

Scientific base: canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
priority revision four. [TASK.json](TASK.json) records fresh selection, scope
change and overlap coverage; [SOURCES.json](SOURCES.json) pins the original
prototype and predecessor proof provenance. No pending executable is imported.

Credit commdata2338 / PR2021 for the fixed completion and PR2398 (head
`8051d99dfd91a788d25bfc92c3863a33c658a5a9`) for the overcomplete in-space
theorem, the ten-term boundary and this explicit extension handoff. Hanhong
Zhao / PR2321 supplies the minimal-space support and sharp nine-factor work.
Related root/support lineage includes Arham Tahir / PR1591, Gareth Davidson /
PR1652, woklerx / PR1077 and PR1447, DreamingOfClouds / PR717, and themilkman216 /
PR968. Their results and frozen source bytes remain unchanged.

Prepared for **ywz65** with substantial OpenAI Codex assistance in derivation,
code, verification and writing. A separate AI-assisted reviewer read the full
proof, including the free-pure classification, coefficient compatibility and
majorization step, and found no actionable issue. Apache-2.0. No independent human review,
formal proof-assistant verification or hosted-CI pass is claimed.
