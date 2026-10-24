# Sharp invocation count for rank-bounded UT3 block calls

**Scoped alphabet extension; no new kappa.** For `w` central UT3 targets,
arbitrary restored dirty workspace, and paid a/b calls of scalar rank at most
`k`, the exact minimum number of calls is

`2t`, where `t = max(2, ceil(2w/k))`.

Search aliases: D8 (the dihedral group of order eight), UT3(F2), UT_3(F2),
Heisenberg group mod 2, central commutator, rank cap, higher-rank block calls.

Every word has at least `2w` charged rank units of **each** letter. One
construction simultaneously attains the minimum invocation count and both
rank bounds. Under nonnegative per-letter complete prices
`alpha_g + beta_g rank(N)`, the sharp abstract tariff is therefore

`t(alpha_a + alpha_b) + 2w(beta_a + beta_b)`.

The smallest batching improvement is `w=3,k=2`: six rank-two calls, rather
than twelve rank-one calls or eight calls from disjoint blocks of sizes two
and one. All three constructions charge twelve total rank units. At uniform
price `alpha + beta rank`, their bills are respectively `6alpha+12beta`,
`12alpha+12beta`, and `8alpha+12beta`. This improves an invocation overhead
only when the hypothetical block call really has that complete price.
It is not a recursive-moment or physical supplier improvement.

## Exact model and predecessor boundary

Let `G=UT_3(F2)`, with triples `(u,v,z)` and group product

`(u,v,z)(U,V,Z)=(u+U,v+V,z+Z+uV)`.

Set `a=(1,0,0)`, `b=(0,1,0)`, `c=abab=(0,0,1)`. Work in the **full formal**
group algebra `R=F2[G]` on any finite `r>=w>=1` scalar registers. For an integer
`k>=1`, the expanded paid alphabet is

`D_N(g)=I+([g]+1)N`, `g in {a,b}`, `1<=rank_F2(N)<=k`.

`N` is any binary `r-by-r` matrix; it need not be idempotent. This is one
optimistically priced **block primitive**, not a claim that its implementation
costs one rank-one call. Each factor is reversible with inverse itself:
`([g]+1)^2=0` gives `D_N(g)^2=I` even when `N^2` is neither zero nor `N`.
The endpoint is `diag([c] repeated w, 1 repeated r-w)` on arbitrary inputs.
All restored roles, every invocation and its full scalar rank are counted.
There are no free address maps, central-letter calls, clean ancillas, COPY,
ERASE, or uncharged inverse calls.

Scalar `GL_r(F2)` mixing is free **only in this abstract screening model**.
Conjugate it through paid factors, retaining scalar rank. Augmentation sends
every paid factor and the target to identity, so the residual free scalar
map must be identity. The expanded alphabet contains all these conjugates.
Consequently the normalized paid-word model covers arbitrary free scalar
mixing with the declared complete dirty boundary.

steph4n-gh's [PR1573](https://github.com/CrocSwap/integer-mult-bounds/pull/1573)
already proves `4w` for rank-one idempotents with arbitrary workspace.
Arham Tahir's [PR1589](https://github.com/CrocSwap/integer-mult-bounds/pull/1589)
extends that bound to all rank-one matrices; Hanson Sun's
[PR1607](https://github.com/CrocSwap/integer-mult-bounds/pull/1607) treats mixed
rank-one targets. Their zero-sum/coefficient-span proof supplies the method
below. The new part is the sharp rank-cap invocation count, cyclic block
construction and simultaneously optimal rank/invocation tariff. At `k=1` it specializes
to their central-only result. woklerx's
[PR1841](https://github.com/CrocSwap/integer-mult-bounds/pull/1841) adds a paid
central label while keeping scalar rank one, a different changed premise.
Josie Elliston's [PR1792](https://github.com/CrocSwap/integer-mult-bounds/pull/1792)
already observes that a rank-s coupling splits into s same-label rank-one
calls, preserving the rank-linear bill. That fact and the `4w` rank-volume
floor are credited consequences of predecessor work, not new savings here.
Exact heads are recorded in [SOURCES.json](SOURCES.json). No predecessor code
or source archive is imported.

## Uniform lower bound

The predecessor floor can also be obtained by splitting each rank-d `N`
as a sum of d rank-one matrices. Since `([g]+1)^2=0`, their same-label factors
multiply to `D_N(g)`. The rank-one lower bound therefore applies to total
rank mass. The self-contained coefficient argument below records that
inherited implication without requiring a pending executable or theorem.

Use the predecessor quotient

`A=F2<X,Y>/(X^2,Y^2, all monomials of length >=3)`.

Its basis is `1,X,Y,XY,YX`; the map

`(u,v,z) -> 1+uX+vY+zXY+(z+uv)YX`

preserves the displayed group law. Thus `a->1+X`, `b->1+Y`,
`c->1+XY+YX`. This is only a necessary-condition quotient; acceptance of
the upper words uses the full formal algebra. Put `Q=diag(I_w,0)`, rank `w`.
The target's degree-one coefficients vanish and its two mixed coefficients
both equal `Q`.

For the a factors write `N_i=U_i V_i`, where `d_i=rank(N_i)`,
`U_i` has `d_i` columns and `V_i` has `d_i` rows. Concatenate them into
`U=(U_1 ... U_p)` and `V=(V_1^T ... V_p^T)^T`, with inner dimension
`s_a=sum_i d_i`. The `X` coefficient gives `UV=sum_i N_i=0`.

The `XY` coefficient is a sum of `N_i` times later b factors, so its column
space is contained in `col(U)`. The `YX` coefficient is a sum of earlier b
factors times `N_i`, so its row space is contained in `row(V)`. Since both
are `Q`, `rank(U)>=w` and `rank(V)>=w`. But `UV=0` implies
`image(V) subset kernel(U)` inside `F2^{s_a}`, hence

`s_a >= rank(U)+rank(V) >= 2w`.

Exchanging a,b proves `s_b>=2w`. No scalar commutation, idempotence,
determinant parity, register bound, or finite-search assumption is used.
Since every rank is at most `k`, `p,q >= ceil(2w/k)`. Each letter must occur
at least twice: zero occurrences cannot give the mixed coefficient `Q`,
and one occurrence would require its nonzero `N` to equal zero in the
degree-one coefficient. Therefore `p,q>=t`.

For nonnegative tariff coefficients the complete bill is at least
`t(alpha_a+alpha_b)+2w(beta_a+beta_b)`. Negative prices are outside the model.

## Uniform attaining construction

Let `t=max(2,ceil(2w/k))`. Assign target coordinate `i=0,...,w-1` to two
block indices

`2i mod t` and `(2i+1) mod t`.

These indices differ because `t>=2`. For each block `j`, let `P_j` be the
diagonal projector onto its assigned target coordinates, zero on all dirt.
The `2w` consecutive residues distribute across `t` indices with loads
`floor(2w/t)` or `ceil(2w/t)`. Since `t<=2w` and `t>=2w/k`, every block is
nonempty and has rank at most `k`. Execute, in increasing block order,

`D_{P_j}(a) D_{P_j}(b)`.

Each target belongs to exactly two blocks. Its complete formal word is
`abab=c`; all other factors act identically there. Every extra dirty
coordinate sees only identity. Thus the word has the required full endpoint,
`t` calls of each letter, and rank mass `sum_j rank(P_j)=2w` per letter.
There is no preparation or extra workspace requirement. Adding any number
of identity roles preserves the construction. This proves the sharp count
and tariff for every finite `r>=w` and integer `k>=1`, including `k>w`.

For `w=3,k=2`, the supports are `{0,1}`, `{0,2}`, `{1,2}`. Apply a then b
on each support. Overlapping these blocks removes two invocations relative
to disjoint batching; it does not remove any charged rank.

## Exact evidence and reproduction

The written proofs establish the arbitrary-size statement.
[verify.py](verify.py) supplies bounded exact corroboration:

- All 64 group products check the quotient homomorphism; all 32,768 quotient
  triples check associativity.
- All 530 binary scalar matrices at `r=1,2,3`, including zero as an algebra
  control, check two rank implementations, rank factorizations, all 1,060
  same-label decompositions and full formal
  and faithful regular involutions for both letters. The `r=3` rank counts
  are `1,49,294,168` at ranks `0,1,2,3`.
- All 27,931 two-register words through three calls, over both letters and
  all fifteen nonzero scalar matrices, check ordered coefficients against
  both a separate dynamic recurrence and full-formal quotient projection.
  Actual carrier spans and zero-sum rank bounds are checked. All 900 ordered
  two-factor products additionally compare formal and faithful regular maps.
- 102 attaining fixtures cover `w=1..12`, `k=1..w+2`, each with two dirty
  roles. Both engines check complete forward and inverse operators, including
  16,160 regular basis columns and exact counts/rank invoices.
- A scalar-conjugated pilot mixes dirty input into a target and restores the
  complete boundary with the two permitted free scalar maps. Omitting those
  maps fails in both engines. Sixty-two single-call omissions and ten model,
  rank-invoice, label and dirty-boundary controls reject. A nonzero formal
  off-diagonal perturbation in the quotient kernel is rejected by the faithful
  engine even though the lower-bound quotient cannot see it. 306 exact rational
  tariff fixtures include zero overhead, pure overhead and unequal prices.

The formal engine uses triple convolution. The regular engine uses literal
binary 3-by-3 address matrices and their faithful eight-element action, with
different enumeration and multiplication. They share scalar bit-matrix
arithmetic and were written in one session; this is not independent human
review. [CERTIFICATE.json](CERTIFICATE.json) stores the deterministic receipt
and construction-profile digest. `--emit` prints a fresh receipt without
changing the package. Checks remain active under `-O`.

From the repository root, standard-library Python 3.12:

```sh
python -I -O -B research/ut3-rank-bounded-block-calls/verify.py
python -I -B research/ut3-rank-bounded-block-calls/test_verify.py
python scripts/research_package.py --package research/ut3-rank-bounded-block-calls --check-only
python scripts/research_package.py --package research/ut3-rank-bounded-block-calls
```

The registered command covers normal/optimized checking, read-only source
export, regenerated receipt equality, and certificate-corruption rejection.
The source exports need only verifier and certificate; generic provenance
checks additionally require Git history. Task selection, scope, exact main,
overlap and validation environment are in [TASK.json](TASK.json).

## Limits

The rank units above are **scalar coupling ranks in this formal alphabet**,
not an admitted supplier's recursive child ranks. Rank-linear pricing gives
the same `4w` rank bill at every cap. A nonlinear recursive tariff requires
its own analysis; this result does not optimize it. The expanded block
primitive, free scalar maps and fixed invocation overhead have no supplied
physical realization, rational-frame translation or H1-H5 admission.
Selected-source orientation passed; the selected cold replay, compiler,
common-label realization, hosting/ownership, precision/tape, outer analytic
transfer, Lean proof and independent human review were not performed.
No new multiplication exponent or maintainer acceptance is claimed.

## Open next questions

Can a physical bit interface realize one rank-k block call below the sum of
its rank-one complete prices? That determines whether the invocation savings
matter. Start with this `w=3,k=2` six-call boundary and charge frame changes,
scalar preparation, hosting, precision, restoration and dispatch against all
twelve rank-one calls. The blocker is a legal physical realization; neither
formal rank nor fewer invocations provides it. Structured scope and this
handoff are in [TASK.json](TASK.json).

## Credit and license

Credit steph4n-gh/PR1573 for the all-register rank-one central bound and
zero-sum rank argument; Arham Tahir/PR1589 for the nilpotent rank-one extension
and two-coefficient quotient; Hanson Sun (@bbMisk)/PR1607 for mixed-target
coefficient tariffs; woklerx/PR1841 for the distinct priced-central alphabet.
Credit Josie Elliston/PR1792 for the family index, D8/UT3 alias warning and
explicit rank-s decomposition/rank-linear pricing observation.
Retain juper997/PR1478 and woklerx/PR1443's finite UT3/D8 predecessors,
Gareth Davidson (@bitplane)/PR1333's scalar-normalization context and the
eumemic/PR288, Ali Romman/PR468 and David Govea/PR720 register-model lineage.
No literature-priority claim is made for rank-nullity or cyclic load balancing.

Prepared by **Arham Tahir with substantial OpenAI Codex assistance** in proof,
implementation, verification and writing. No subagents or independent human
proof review. New work is Apache-2.0; frozen inputs and notices are unchanged.
