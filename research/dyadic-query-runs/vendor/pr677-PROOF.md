# Restored boundaries for one native unipotent BIT query

This is a local interface result, conditional on the cited ordinary ADDRESS
interchange and ordered-stream primitives. It supplies no complete interchange
supplier and no multiplication exponent. The algebra below proves the stated
identities and scoped query bounds; the finite checker is corroboration, not a
formal proof of a full multiplication theorem.

## 1. Object, predecessor, and boundary contracts

Karl Appel / applecrusher's [PR #521](https://github.com/CrocSwap/integer-mult-bounds/pull/521),
pinned at `a190fdb39f31647fc6f651625353710624627348`, replaces two particular
reflected queries by one unipotent query. Its complete dirty operator retains
a private BIT row. It explicitly does not complete a DATA interchange or
authorize erasure of that row at an unfinished boundary. Its result is not
contradicted here.

We choose a different, modest completed endpoint. For three genuine DATA rows
`(x,y,z)` and one fixed ADDRESS permutation `h`, let

    S_h(x,y,z) = (x + (h+I)y, y, z).                         (1)

All VALUE additions in this note are XOR, over F2. ADDRESS arithmetic below
is rational arithmetic specialized to odd prime-power residue rings; these
two coefficient systems must not be conflated. Equation (1) is a shear,
not the three-DATA interchange. It satisfies `S_h^2 = I`, even though
`h^2 != I`.

The contribution is an explicit comparison of three ways to complete (1):

| Contract | Queries `h` or `h^-1` | Additional full row | Endpoint for that row |
|---|---:|---:|---|
| Query the DATA target | 2 | none | All other dirty rows untouched |
| Queries remain on one private row, with triangular source/target XORs | 4 | one | Arbitrary initial private contents restored |
| Caller owns disposable private storage | 1 | one | Explicit copy initialization and final zeroing |

The first count is optimal in the fixed-`h` query/XOR model of section 4.
The second is optimal in the narrower private-row model of section 5 for
a uniform all-width program. These are **not** lower bounds for arbitrary
ordinary-interchange programs with different free ADDRESS operations.
The third changes the workspace contract: discarding someone else's dirty
row is not allowed. Its successful DATA endpoint makes its *own* final clear
legitimate. It is not evidence that clearing PR #521's private row is safe
inside an arbitrary surrounding construction.

## 2. The retained query, with its actual recursive child

Fix an odd prime `ell`, `b >= 1`, and `m = ell^b`. Use six ordered ADDRESS
fields `(H0,H1,H2,D0,D1,D2)`, all of width `b`, and all complete spectator
ranges. Define

    s = (1,0,1,-1,0,-1)^T,
    r = (1,0,-1,-1,0,1)^T,
    M = I6 + s r^T / 4,       M^-1 = I6 - s r^T / 4.

Here `r^T s = 0`. The permutation `h` moves the BIT at ADDRESS `a` to `M a`;
its action on values reads the inverse ADDRESS image. PR #521's literal
lowering, transcribed in `PROGRAM.json`, is

    a2 -= a0
    a3 += a0
    a5 = (a5 + 5*a0 - a2 - a3)/4
    CHILD_C(a0,a5)
    a2 += a0
    a3 -= a0
    a5 = -4*a5 + 3*a0 + a2 + a3.                           (2)

Substitution gives `M`. Reversing (2) and inverting each scalar event gives
`M^-1`. The child is an ordinary interchange of two `b`-digit ADDRESS fields
on the **entire selected BIT row**, including all other ADDRESS fields.
It is not a pointwise VALUE swap or an uncharged oracle.

All six affine events read only earlier fields. Their diagonal numerators
and denominators are powers of two up to sign; denominators of controls are
also powers of two. Thus every event is well defined for every odd `ell`.
The cited ordered-stream lemma pays the finite coefficient preparation,
counter work, complete spectator scans, temporary work and head returns.
It does not assume unit-cost arithmetic on growing integers.

The same implementation works on a DATA row or a private row: the ADDRESS
primitive's contract is for arbitrary BIT contents and is insensitive to
the role's name. Calls must be sequential and have exclusive access to the
queried row until its completed boundary. No source chart or current supplier
schedule is asserted to provide that permission automatically.

For `a0 = e_H0`, the addresses `a_k = e_H0 + k*s/4`, `k in Z/m`, are distinct
and satisfy `M a_k = a_(k+1)`. Hence on their VALUE array, `(h y)_k = y_(k-1)`.
This supplies a nontrivial orbit of order `m`, as well as a direct finite
check on push/read orientation. There are also fixed points and shorter
orbits at nonunit initial scales; these are included in the replay.

## 3. Three complete programs

### 3.1 No full private row

Apply, chronologically,

    x <- h^-1 x
    x += y
    x <- h x
    x += y.                                               (3)

The output is `x + h y + y`; `y,z` and every unrelated row are untouched.
No row is assumed zero, copied, or erased. A pre-existing private row is
an untouched spectator. Source `y` is never modified, even temporarily.
The queried target may be permuted temporarily, so callers may not inspect
it between events. This is a restored boundary, not a concurrently readable
intermediate representation.

### 3.2 Queries only on a restored dirty private row

For arbitrary initial `q=q0`, use

    q += y
    q <- h q
    x += q
    q <- h^-1 q
    q += y
    q <- h q
    x += q
    q <- h^-1 q
    x += y.                                               (4)

The two contributions read into `x` are `h(q0+y)` and `h q0`. Their sum is
`h y`. The last XOR supplies `y`; both query/inverse pairs restore their
own input, and the two source XORs restore `q0`. Thus (4) implements (1)
on DATA and the identity on arbitrary private input. It has four queries
and five XORs, not four queries plus an implicit cleanup.

### 3.3 An owned, disposable private row

Allocate or reserve one owned full row `q`, whose incoming contents may be
discarded, and use

    q <- copy(y)
    x += y
    q <- h q
    x += q
    q <- 0.                                               (5)

The copy overwrites every private cell and pays source access and
initialization in one scan. Just before the last line, DATA already equals
(1), and `q=h y` is redundant with retained `y`. No later step reads `q`.
The final full-row clear therefore returns owned work storage to zero.
All five events are charged. There is no assumption that unknown dirty
caller state can be thrown away.

Reapplying the *completed* program (5) implements `S_h^2=I` on DATA. This is
different from applying the inverse of PR #521's unfinished dirty module
after clearing its private row; that inverse generally fails. Both facts
are checked, including arbitrary DATA inputs and explicit private-input
rejection when (5) is falsely labeled a dirty-restoring program.

The normal form of PR #521's dirty module is
`H(h)=I+E(h-I)`, `E=(e_x+e_q)(e_y+e_q)^T`. It directly explains the
tradeoff: for initial `q=0`, its DATA output is already (1), but its private
output is `(h+I)y`. Once (1) is declared and verified as the desired complete
endpoint, terminal operations needed solely for later dirty-module recovery
can be removed. Program (5) is the simpler paid copy implementation of that
completed endpoint. It changes neither the predecessor's two-reflection
identity nor its warning about other unfinished endpoints.

## 4. Sharp two-query classification with arbitrary dirty spectators

The model permits any number `d >= 2` of arbitrary dirty rows. Free algebraic
operations are invertible, address-independent XOR maps of the row roles;
actual implementations still pay for these scans. A query applies `h` or
`h^-1` to one row. No other nontrivial ADDRESS map, copying into clean storage,
or erasure is free in this lower-bound model.

Represent `h` by `t`. Work over `F2[t,t^-1]`, or over
`F2[t,t^-1]/(t^m-1)` for an odd orbit length `m >= 3`. In the latter ring,
zero divisors cause no problem: the proof uses determinants and comparison
of distinct basis coefficients, not division or a fraction field.

On an `m`-cycle, identify a BIT row with `sum_k value_k t^k`. The query is
multiplication by `t` on the regular module of the cyclic ring. Thus equality
of these row operators is equivalent to entrywise equality of their matrices
over that ring. The determinant below is taken **in this ring**, not the
ordinary F2 determinant of the expanded bit matrix. Restricting a complete
array to the full-order orbit in section 2 gives a necessary condition for
any claimed full-array identity.

After conjugation by an invertible binary row map, one query is

    D_P(t^e) = I + (t^e-1) P,   e in {+1,-1},
    P = u v^T,  v^T u = 1.                                  (6)

These are precisely binary rank-one idempotents. Any arbitrary interleaving
of free XOR maps normalizes to a product of such factors: commute the
constant maps to the left, conjugating each projector as they pass.
At `t=1`, the desired endpoint is `I`, so the remaining constant factor
must be `I`. Thus allowing arbitrary endpoint XOR maps does not omit a
one-query or two-query solution from this model.

Let `N=a b^T` be a nonzero rank-one nilpotent, `b^T a=0`; the desired shear is

    T_N(t) = I + (t-1) N.                                   (7)

The determinant lemma, valid over each stated commutative ring, gives
`det D_P(t^e)=t^e` and `det T_N(t)=1`. Zero queries cannot give the nonconstant
(7). One query has the wrong determinant. Two queries of the same sign also
have the wrong determinant, since `t^2 != 1` on an odd orbit of length at
least three. Therefore any two-query solution has opposite signs.

For left sign `+1`, expand the product *in operator order*:

    D_P(t) D_Q(t^-1)
      = I+P+Q + t(P+PQ) + t^-1(Q+PQ).                       (8)

The coefficients of `1,t,t^-1` are independent in either ring, so (8)
equals (7) **if and only if**

    PQ=Q,       P+Q=N.                                     (9)

For the other sign order the exact conditions are

    PQ=P,       P+Q=N.                                     (10)

This is an exhaustive classification, not just a necessary filter. In (9),
the two rank-one images coincide and equal the image of `N`. Consequently

    P=a c^T,   Q=a(c+b)^T,   c^T a=1.                      (11)

In (10), the two row spaces coincide and equal the row space of `N`, giving

    P=(c+a)b^T,   Q=c b^T,   b^T c=1.                      (12)

Conversely, (11) or (12) directly verifies the corresponding conditions.
Over F2 there is no nontrivial scalar rescaling of a rank-one decomposition.
Each family has `2^(d-1)` choices, so every nonzero rank-one nilpotent target
has exactly `2^d` ordered, signed two-query factorizations. Program (3)
realizes one of them for `N=e_x e_y^T`, proving the two-query minimum.

For any private index `q` distinct from `x,y`, all these factorizations have
`P_qq=Q_qq=0`: in (11) the image is `e_x`, and in (12) the row space is
`e_y^T`. This observation separates the unrestricted dirty-row model from
the private-only contract below.

The scalar-projector/group-algebra method is established predecessor work:
eumemic's PR #288 and Ali Romman's in-tree `bit-three-register-lower-bound`
package (PR #468) use it for different diagonal interchange targets. We do
not claim that method as new. The present two-query classification targets
one off-diagonal restored shear and includes finite cyclic rings explicitly.

## 5. Why the private-only dirty boundary costs four queries

Here queries are restricted to `q`; the allowed pointwise gates are
`q += y`, `x += q`, and `x += y`. Source `y` and spectator rows remain
unchanged. A free-gate prefix has the triangular form

    K(x,y,q) = (x + a q + b y, y, q + c y).

Both `K` and `K^-1` have `qq` entry one. A normalized query projector
`K^-1 e_q e_q^T K` therefore has `P_qq=1`. Section 4 shows that no
two-query factorization of (1) can have that property. A one-query program
is already excluded. A three-query program has determinant `t^j` for
`j in {-3,-1,1,3}`, so cannot have determinant one in the Laurent model,
or on an odd orbit of length at least five. Thus a uniform all-width
program needs at least four queries. Program (4) attains four.

This proof does not assert a separate three-query exclusion for one isolated
order-three quotient from the determinant alone. The formal finite-word
check below is over Laurent coefficients, not modulo three. The uniform
claim has no gap: for example the actual order-eleven orbit already gives
the stated lower bound, and the program must work at that width too.

Arbitrary XOR maps that swap a DATA role with `q`, arbitrary alternate
ADDRESS maps, non-restored private state, and clean/disposable storage are
outside this private-only restriction. Removing any of those restrictions
requires a new analysis; program (3) deliberately changes the first one.

## 6. Complete typed costs and workspace

Let each genuine DATA row have logical BIT volume `U`, including the full
ADDRESS domain and all spectators. Productive volume is `V=3U`, and nominal
chunk width is `N=3b`. Let:

- `C(U,b)` be the cost of one ordinary interchange of the selected two
  `b`-digit fields on a complete row of volume `U`, with restored child work;
- `A(U,b)` bound each fixed ordered-affine event of (2), including coefficient
  preparation, its source access, temporary work, and head returns;
- `X(U)`, `P(U)`, and `Z(U)` bound one aligned XOR, full copy, and full clear;
- `R_j(V,b)` include row split/merge, routing to the fixed evaluator tapes,
  descriptor setup, parking and recovery, allocation if needed, and head
  returns not already charged in a primitive. Each `R_j=O(V)` under the
  inherited complete-range, fixed-number-of-rows, and stack contract.

The complete local recurrences/charges are

    S_data(V,3b) <= 2 C(U,b) + 12 A(U,b) + 2 X(U) + R_data(V,b),
    S_dirty(V,3b) <= 4 C(U,b) + 24 A(U,b) + 5 X(U) + R_dirty(V,b),
    S_owned(V,3b) <= C(U,b) + 6 A(U,b) + 2 X(U)
                     + P(U) + Z(U) + R_owned(V,b).          (13)

Every query is lowered using (2), so there are exactly 2, 4, and 1 ordinary
recursive children respectively, all of actual volume `V/3` and width `N/3`.
There is no dropped recovery child, additional live query, or implicit
source-copy oracle. All children run sequentially and reuse restored child
workspace. Primitive affine work may itself use temporary streams; those
are covered by `A`, not claimed absent by the phrase "no private row."

Under the cited streaming contracts, the non-child terms of (13) are `O(V)`.
If `c(b)` uniformly bounds `C(U,b)/U`, then

    s_data(3b) <= (2/3)c(b) + O(1),
    s_dirty(3b) <= (4/3)c(b) + O(1),
    s_owned(3b) <= (1/3)c(b) + O(1).                         (14)

The constants are independent of `b,U`, for a fixed permitted radix and
the fixed literal program. Fractions count the **actual child stream
volumes**, not the persistent stock. Persistent role storage is `V` for
(3), and `4V/3` for (4) and (5), before primitive/evaluator/recursive scratch.
For peak workspace, let `B_j(V,b)` include the fixed streaming and parking
workspace and `W_C(U,b)` child workspace. A safe bound is

    W_j(V,3b) <= persistent_j(V) + B_j(V,b) + W_C(U,b),
    persistent_data=V,   persistent_dirty=persistent_owned=4V/3.

`B_j=O(V)` under the same tape primitives; the bound pays their temporary
streams and does not claim an exact number of physical tapes or total cells.
Private-row allocation is not normalized away. In the owned case the initial
copy and final clear are charged on every invocation, even if a later caller
could establish safe reuse.

These are **typed** recurrences: the left side is a DATA shear and `C` is
ordinary ADDRESS interchange. Substituting `S_data` for `C` and solving a
self-recursion would be circular without a separate compiler. No such
compiler, arbitrary-width padding, common-frame schedule, or assembled
supplier is provided. For `N` not divisible by three this packet specifies
no reduction. The old all-size, row/stack, precision and analytic assumptions
are not discharged. In particular none of (13) or (14) is a new κ certificate.

## 7. Reproducible evidence and exact limits

`check.py --check` uses only Python's standard library and this directory.
It does not import the predecessor's checker or any supplier implementation.

1. Enumerate all binary matrices at dimensions 2, 3 and 4; select rank-one
   idempotents by independent rank and square tests; compare against the
   outer-product catalogue. The sizes are 6, 28 and 120.
2. Multiply all **60,880 ordered signed pairs** as matrix Laurent polynomials.
   Check (9)/(10) against the literal polynomial result for every pair and
   every nonzero rank-one nilpotent target encountered. Every target has
   `2^d` factorizations; none for a DATA coordinate shear has both private
   diagonals one.
3. Exhaust all four native triangular charts
   `(e_q+a e_x)(e_q+b e_y)^T`, `a,b in F2`, with both query signs, through
   length four. The full **4,681-word** domain is completed: counts of
   successes by length are `0,0,0,0,24`. This is a finite corroboration of
   the specified model, not a search over arbitrary circuits or frames.
4. Verify (2) and its inverse on all rational ADDRESS basis columns and
   modulo `3,9,27,11,121`, including two additional ADDRESS spectators.
   Check full and shorter orbits from nonunit initial scales, plus fixed
   points. These rings differ from PR #521's `5,25,7,49` replay.
5. Propagate all independent BIT basis columns simultaneously as distinct
   integer bits, so every XOR-column cancellation is exact. Check all three
   literal programs, their completed DATA involution, and the separate
   owned-versus-dirty workspace contracts. No VALUE assignment is sampled.
6. Reject omissions of every recursive query, a wrong inverse, missing XORs,
   missing owned initialization or clear, unpaid ADDRESS children, and the
   false inference that owned clearing restores arbitrary dirty state.
   A concrete order-two, same-sign factorization rejects extending the
   opposite-sign classification to a domain where `t=t^-1`.

The separate `full_domain_check.py` imports no main-checker code. It applies
the literal ADDRESS program to all **729 addresses in `(Z/3)^6`**, including
all 243 fixed addresses, and compares a separately written coordinate
formula. It then tracks individual sparse sets of nonzero BIT positions,
rather than packed symbolic columns, for **2,916 independent inputs per
program**. This covers every row and every address, not just a selected
orbit. Endpoints and completed inverses give **17,496 cases** across the
three programs. The private input is discarded only in the explicitly
owned-storage contract. This second finite method is included in the
single reproduction command.

Assignment seed 57 selects candidate `57 mod 3 = 0` in `CLAIM.md`. The
algebraic domains and stopping rule above were fixed before implementing
the verifier; there is no random search whose losing trials are omitted.
The source pins and original attribution are in `SOURCES.json` and
`NOTICE.md`. `EXPECTED.json` records deterministic finite evidence. The
universal proof in sections 3–5 is a written argument open to review;
neither the exhaustive small-dimensional checks nor a PASS string replace it.
