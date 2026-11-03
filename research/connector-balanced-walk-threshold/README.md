# Balanced closed walks improve unsigned connector capacity

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped written proof with an exact finite construction certificate.** In the
unsigned dirty-connector interface of PR4231/PR4248, define

```text
C(k) = 2 ceil(2^(k-1)/k),
L(c) = max { k >= 1 : C(k) <= c }.
```

For every integer characteristic `c >= 2`, the source capacity satisfies

```text
N(c) >= L(c) floor(c/2) + 2(c mod 2).
```

Moreover, `C(k)` is the exact maximum-coordinate-flip threshold among **closed
binary-cube covering walks** on `k` coordinates. This is a classical Gray-code
consequence applied here to the connector construction. It is not a lower bound
for arbitrary depth-two connector words.

For `c >= 8`, put `b = floor(log2 c)` and `m = floor(log2 b)`. Then

```text
b + m <= L(c) <= b + m + 2.
```

Thus the explicit lower bound gains the `log2 log2 c` source term missing from
PR6071's reflected-Gray specialization. At `c = 256`, it gives `N(256) >= 1408`;
PR6071's displayed reflected-Gray guarantee is 1152. This comparison concerns
those two guarantees, not a claim to know the best construction on main.

The new part is the explicit optimized connector threshold, its source-capacity
consequence, and a literal realization. Balanced Gray cycles are classical.
PR6071 supplies the covering-walk split; PR6107 explicitly suggests the balanced
direction without deriving this bound. Neither predecessor is audited here.
There is no new kappa or change to the selected frontier.

## Interface and proof

Let `R` be any nonzero unital ring of characteristic `c >= 2`. Sources `x_j`,
the borrowed connector `z`, and outputs `y_m` begin arbitrarily dirty. The only
complete calls are `B_j: z += B_j x_j` and `A_m: y_m += A_m z`, for compatible
linear maps. Each call restores its private scratch and heads, preserves every
other row, and has fixed ports. Sources and coefficients are immutable. Outputs
are unobserved until completion. There are no negative calls, extra connectors,
free copies, scalings, direct product calls, or mutable-source operations.

The desired action is `y_m += sum_(j in m) A_m B_j x_j`, with `z` restored.
The identity specialization forces every used operator to occur a positive
multiple of `c` times. A complete-call floor word uses each exactly `c` times.
PR4248's depth-two block criterion asks for every binary mask to be the sum
modulo `c` of at most two prefixes of a source word containing each source
exactly `c` times. Repeated read boundaries are allowed.

### Exact closed-walk threshold

Consider any finite closed single-coordinate walk that starts at zero and
visits every vertex of `{0,1}^k`, allowing repeated vertices. Let its length be
`s`, and let `f_j` count flips of coordinate `j`. Since it returns to its start,
each `f_j` is even. Its `s` distinct time slots before the repeated endpoint
must cover `2^k` vertices, so `s >= 2^k`. Consequently

```text
max_j f_j >= 2 ceil(s/(2k)) >= 2 ceil(2^(k-1)/k) = C(k).
```

The classical balanced cyclic Gray-code theorem supplies a Hamilton cycle
whose even coordinate flip counts differ by at most two. Their sum is `2^k`,
so their largest value is precisely `C(k)`. The two-step walk treats `k = 1`.
This attains the lower bound for every `k`. Existence is a cited classical
theorem, not a conclusion inferred from the finite witness.

Primary reference: G. S. Bhat and C. D. Savage, [Balanced Gray Codes, Theorem 1](https://doi.org/10.37236/1249),
Electronic Journal of Combinatorics 3, R25, 1996, pages 8-10.
Their [2005 historical comment](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v3i1r25/comment/)
credits the earlier Bakos construction recorded by A. Adam in 1968. The
Robinson-Cohn construction and Bhat-Savage subsequence selection also produced
the supplied literal cycle. No new Gray-code existence theorem is claimed.

### Positive calls from a closed walk

Take a balanced cycle with `C(k) <= c`. In the notation of Armin Pourshafeie's
PR6071, let `U(t)` and `D(t)` count upward and downward flips through time `t`.
Then `U(t)-D(t)=g_t`, the visited binary vertex. Let `A` and `B` be the label
subsequences of upward and downward flips. Form the positive source word

```text
W = A · product_j j^(c-f_j) · reverse(B).
```

Each source occurs `c` times. At the two actual boundaries

```text
a(t) = |U(t)|,       s(t) = kc - |D(t)|,
```

the integer prefix vectors are `U(t)` and `c*1-D(t)`. Their sum is `c*1+g_t`.
Both boundaries exist, lie in chronological order, and represent `g_t` modulo
`c`. The compiler retains the first occurrence of each mask. All executable
calls are positive, including those designed using downward flips.

Two output reads at these boundaries deliver the requested contribution.
Add `c-2` output reads at boundary zero to cancel the arbitrary connector
baseline. Every output is called exactly `c` times, including its padding.
Every source is also called exactly `c` times, restoring `z`. This uses only
linearity and characteristic `c`; neither primality nor commutation of the
operators is required. It is PR6071's split applied to a better walk.

### Capacity and the second-order term

Concatenate `floor(c/2)` disjoint `L(c)`-source blocks. Completed blocks have
zero prefix modulo `c`, so any global binary mask uses at most two reads per
nonzero block. If `c` is odd, add PR4248's depth-one two-source block
`a b a^(c-1) b^(c-1)`. Its prefixes at `1,2,c+1` give the three nonzero masks.
The total depth is at most `c`; pad each output with boundary-zero reads to
exactly `c`. This proves the displayed lower bound on `N(c)`. It does not
materialize the exponentially many outputs of a large composed batch.

For the lower estimate on `L(c)`, take `k=b+m`, with `b>=3`. Then
`2^k <= cb`, `k>=b+1`, and `c>=2^b>=2(b+1)`. Hence

```text
C(k) < 2^k/k + 2 <= cb/(b+1) + 2 <= c.
```

For the upper estimate, any allowed `k` obeys `2^k <= ck`. The function
`2^k/k` increases for integer `k>=2`. At `k=2b+2` it is at least `2^(b+1)>c`,
so `k<=2b+1`. Since `2b+1<2^(m+2)`, this yields
`2^k <= ck < 2^(b+m+3)`, and therefore `k<=b+m+2`.

These are bounds on the closed-walk subclass capacity `L(c)`. They do not
close PR6107's gap for unrestricted depth-two words or improve its leading
constant `1/2` for depth-at-most-two concatenations.

## Literal certificate and complete invoice

[WITNESS.json](WITNESS.json) contains one nine-coordinate Hamilton cycle.
Independent traversal finds 512 distinct vertices and coordinate counts
`56,56,56,56,56,58,58,58,58`. At characteristic 58, [connector.py](connector.py)
constructs a 522-call source word and two prefix boundaries for all 511
nonzero masks. Its complete interleaved word has exactly **30,160 calls**,
with each of the nine source operators and 511 output operators called 58
times. All padding reads are present. The 27 executed fixtures include every
source-coordinate basis vector, both connector basis vectors, zero, and six
mixed dirty inputs over `Z/58Z`, with dirty outputs and singular matrices.

Let `I` pay admission and layout, `P_F` pay coefficient preparation, `D_W` pay
the actual word's dispatch and instruction storage, and `c_F` be the complete
fixed-port call price, including private restoration and head return. For a
batch on `n` sources, the conditional bill is

```text
I + sum_F P_F + D_W + c sum_j c_Bj + c sum_(m != 0) c_Am.
```

No physical price is set to zero. Full-row storage, output layout, instruction
volume, compiler closure, native frame compatibility, precision, routing and
the outer caller remain uninstantiated. This abstract call-floor construction
does not supply a favorable physical supplier bill. The selected PR6030 and
all five framework assumptions retain their status.

The values `N(58)>=261`, `N(64)>=288`, `N(256)>=1408`, and `N(512)>=3072`
are evaluations of the proved formula. The complete composed batches at
these source counts were not executed. The literal executed batch has nine
sources and 511 outputs.

## Reproduction and verification scope

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/connector-balanced-walk-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/connector-balanced-walk-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/connector-balanced-walk-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/connector-balanced-walk-threshold --check-source-history
```

Expected marker: `PASS_CONNECTOR_BALANCED_WALK_THRESHOLD`. The verifier emits a
generated receipt bound to package hashes. Use `--output /absolute/scratch/result.json`
to retain it outside the checkout. The replay requires only the standard library.
Local interpreter: CPython 3.12.15, macOS, Clang 23.1.3. Hosted CI is recorded
separately in the PR body.

The finite corroboration checks 120 closed covering walks: dimension one at
lengths 2 through 4, and dimension two at lengths 2 through 8. Their compiled
blocks supply 356 mask checks. It also checks the literal nine-source cycle,
all 511 prefix pairs, 27 complete dirty-input executions, 1,023 exact capacity
rows for `c=2..1024`, and ten rejecting controls. These controls cover malformed
walks, insufficient characteristic, changed source pins, wrong reads and an
unpaid source or output call. No predecessor scientific verifier is imported.

The infinite result uses the written proof and the cited classical theorem.
It is not a proof-kernel result. Independent human and formal proof-kernel
review are unclaimed. No selected cold replay, Lean, Docker, physical native
supplier, rounded multiplier or complete multiplication theorem was run.

### Code limits

The literal compiler accepts dimension at most ten, characteristic at most
512, and at most `2^(dimension+1)` walk steps. Its largest complete word has
528,896 calls. The arithmetic-only threshold API accepts dimension through
4096. Every traversal is bounded by these inputs or the fixed replay domain;
there is no recursion or subprocess execution in the verifier.

Python and its standard containers allocate dynamically. This is a managed
runtime deviation from fixed steady-state allocation, with the explicit
limits above bounding live objects. Python also has no pointer-depth or
compile-time warning equivalent. Runtime checks remain active under `-O`;
warning-as-error replay and in-memory syntax/function-size checks cover the
kept code. No claim of a constant-workspace implementation follows.

## Open next questions

1. Does an open cube-covering path improve the threshold at dimensions where
   only one coordinate has the largest flip count? This could reduce the
   characteristic for the same split. First delete each edge of one balanced
   cycle and price the resulting path counts. General path balancing is open
   here, and no open-path optimality is claimed.
2. Can an unrestricted depth-two source word beat this closed-walk capacity by
   more than a constant number of coordinates? First compare literal prefix
   geometry with PR6107's weight-count obstruction. This package supplies no
   unrestricted upper bound beyond the credited predecessor.
3. Can a named characteristic-c consumer use the extra sources at a favorable
   complete price? First specify its immutable sources, physical endpoints,
   output layout and complete `I,P,D,c_F` ledger. No such consumer is supplied.

## Sources and credit

The scope comes from Josie Elliston / [PR6107](https://github.com/CrocSwap/integer-mult-bounds/pull/6107),
Open next question 3. The main construction is Armin Pourshafeie / apoursh's
[PR6071](https://github.com/CrocSwap/integer-mult-bounds/pull/6071).
Nick Petalas's PR4231/PR4248 supplies the unsigned interface, prefix criterion,
concatenation and the depth-one pair, with Ross Richardson's PR934/PR943 and
Riquelme Soares's retained lineage. Josie Elliston's PR6061 and zxv's PR6057
supply earlier finite blocks. Bakos, Robinson-Cohn, and Bhat-Savage retain
credit for the classical Gray-code mathematics and construction. Source
READMEs and all predecessor credit lines remain unchanged.

[SOURCES.json](SOURCES.json) pins the canonical base, task card, selected record
and three live predecessor READMEs. [TASK.json](TASK.json) records the changed
card premise and structured next questions. Live overlap checking preceded
the [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370235).
Sparse local notes and unpublished work remain coverage limitations.
