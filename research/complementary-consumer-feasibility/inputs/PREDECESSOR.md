# The typed quotient has no recursive primitive discount

Prepared for Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Exact direct implementations of the supplied interface

Assume the exact typed ABI of PR4654 at
`dca175fed8ebde8980635fd3b4508b8cba89a1b0`. Its 112 main pairs consist
of 56 type A and 56 type B. On each pair, Q is a symmetric rank-one
Gaussian and D a symmetric rank-seven Gaussian on disjoint axes:

```
A = diag(D,D) S_y(Q^-1),
B = diag(D,QD) S_y(Q^-1) = S_y(1) diag(D,QD).
```

The second identity is exact: both B expressions send (X,Y) to
`(DX, DX+QD Y)`. There is no order-two relation for Q in this proof.

A direct A implementation uses two rank-seven D jobs and one rank-one
query shear. The query copies X into an owned zero temporary, applies
Q^-1 with its actual monomial normalizer, adds into Y and clears the
temporary. This retains the predecessor's owned-erasure hypothesis; it
does not erase a dirty borrowed field. A direct B uses two D jobs, one
Q job on Y and one ordinary output addition. Thus each type costs exactly
`2*7^t+1` in recursive paid moment, t=1-C.

The raw inverse transposes have equally explicit implementations:

```
A^-T = diag(D^-1,D^-1) S_x(-Q^-1),
B^-T = S_x(-1) diag(D^-1,Q^-1 D^-1).
```

The B scalar addition is on the left and acts last. Gaussian inverses
retain their actual monomial normalizers; rank does not change. The
verifier checks all four Laurent matrix identities, with independent D
and Q symbols and every sign and inverse exponent intact.

Across all 112 pairs, direct main execution costs **224 rank-seven jobs
and 112 rank-one jobs**, in either orientation. It uses at most one owned
query temporary at a time. The source's 408 helpers remain independent
arbitrary inputs; implementing each source-normalized helper job directly
adds its complete actual target moment H_t to the paid list. All helper
monomial normalizers are retained. No helper target is counted twice.

Some direct helper jobs have rank nine. The fallback therefore does not
preserve the native word's rank-eight local child cap. The price comparison
is not drop-in compiler admission: any replacement must recheck child ranks,
strictification tails and allocation. If a consumer introduces these helpers
only as fresh independent bystanders, its direct main implementation can
instead omit both their inputs/targets and their matching direct paid jobs;
that cancellation preserves the surplus, but changes the caller's inventory.

This is an operator-level fallback and a comparison of recursive paid
moments. ADDs, copies, clear/erase, monomial wrappers, fixed routing and
helper normalizers have finite volume-linear work. We do not assert
identical machine costs, construct a practical multiplier, or independently
reprove the typed source's native/all-width/phase theorem.

## 2. Strict dominance at every concave exponent

Recounting both emitted source words and their helper endpoints gives

```
P = {1:2177,2:424,3:389,4:147,5:50,8:8},
H = {3:2,6:7,7:47,8:139,9:213}.
```

The native minus direct recursive paid moment is

```
G(C) = P_t - H_t -224*7^t -112,  t=1-C.
```

It has G(0)=8. Normalize K(C)=G(C)/7^t. The constant -224
has derivative zero. In `(P_t-H_t-112)/7^t` the rank coefficients are

```
{1:2065,2:424,3:387,4:147,5:50,6:-7,7:-47,8:-131,9:-213}.
```

For 0<=C<1, all derivative contributions are nonnegative except the
rank-six term. The rank-one term alone contributes at least
`2065/7 * log(7)`; the rank-six negative contribution has magnitude at
most `7 log(7/6)`. Since log(7)>1 and log(7/6)<1,

```
K'(C) > 2065/7 -7 = 288 > 0.
```

The elementary log inequalities are also enclosed by the pinned exact
rational interval engine. Therefore

```
G(C) >= 8 * 7^(-C) > 0,   0<=C<1.
```

The typed native word is strictly more expensive in recursive paid moment
than the direct implementation of the *same* main ABI and helper targets,
for every exponent in the range, including rank mass at C=0.

This is stronger than a failed controller search and different from the
A-only-path obstruction of PR4660. It applies to the local offer before
any controller is chosen. A profitable consumer using this offer could
instead use the cheaper direct implementation, with the same operator
and independent helper targets. It does **not** prove that every such
consumer or every Gaussian algorithm is impossible.

## 3. Comparison with the actual round-three native discount

Freeze PR4610 at `1eb8da6cfb35512c0cc2533413e5ca42f48e13c6`:

```
H0 = {4:28,7:7,8:47,9:326},
P0 = {1:2201,2:412,3:510,4:127,5:40,8:8}.
```

Its ordinary all-A, block-eight main interface has direct paid cost
`H0_t+224*8^t+112`. Put G0=P0_t-H0_t-224*8^t-112.
Its normalized rank-eight gap G0/8^t starts at -6. The corresponding
rank-one coefficient is 2089; the only negative derivative contribution
below rank eight is -7 at rank seven. Hence

```
(G0/8^t)' > 2089/8 -7 = 2033/8 > 0.
```

Exact outward enclosures give G0<0 at C=0.0062073960 and G0>0 at
C=0.0062073961. Thus the original supplier's unique direct-price crossing
is in that interval. Above it the original offer, too, has no recursive
discount over direct main jobs and direct helpers. This is a **local price
crossing**, not an integer-multiplication exponent or a universal ceiling.

At C=.004, the original offer still discounts the direct price by about
16.9818753 per full invocation. This is useful controller budget; the
typed quotient instead has a positive surcharge. Complete controller,
strictification, compiler, BIT, precision and outer conditions remain
necessary for any actual K claim.

## 4. Source and verification boundary

The source word, typed interface and round-three arithmetic are retained
byte for byte, with Git blob and SHA256 authentication. Both paid censuses
and every helper rank are recomputed from the emitted word. The source's
Clifford and free-group proofs are premises here, not newly audited.

The registered Python replay uses exact Laurent arithmetic and outward
rational power/log enclosures. It rejects an unpaid B query, a wrong Q
inverse, missing owned charges and source/profile drift. Passing it does
not establish a new native construction, selected frontier or theorem.

Credit Dugongue and PR4654, DaysSky's quotient source, Cao Yifan and PR4610,
Cinna Davis and the PR4440/PR4470/native lineage, zxv, Jacob Alan Sussman,
the PR4660 B-autonomy observation and all retained predecessor authors.
The direct factorization of B is credited, not rediscovered here.
