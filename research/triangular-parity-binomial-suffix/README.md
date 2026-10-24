# Exact binomial forward-suffix norms in the parity compiler

This package proves a scoped all-depth formula. For the exact triangular
Toeplitz parity compiler on `f(z)=1+c z`, at dyadic dimension `N=2^h`,
the largest infinity norm of a forward suffix is

```text
B_h(|c|) = 1 + sum_{j=0}^{h-1} |c|^(2^j).
```

The maximum ranges over every complete-shear cut and every legal interleaving
of the disjoint children. The empty sum at `h=0` gives 1. The statement holds
for every real or complex `c`, without a small-tail assumption. If `c!=0` and
`h>=2`, a proper, nontrivial cut attains it.

In particular, at `|c|=1` the exact maximum is `1+log_2 N`. The completed
operator has infinity norm 2 when `N>=2`. Brian's complementary
[#4737 forward-prefix theorem](https://github.com/CrocSwap/integer-mult-bounds/pull/4737)
bounds every forward prefix by 2 here. Thus a bounded endpoint and bounded
forward prefixes do not provide a dimension-independent forward-suffix bound
at the unit-tail boundary. This is a precision-interface obstruction for this
specific compiler, not a supplier or multiplication theorem. No new kappa is
claimed.

## Model and predecessor boundary

Use the exact parity factorization in Vlado Vojdanovski's
[#1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673), retained in
[`SHALLOW-TOEPLITZ.md`, section 3](../unconditional-batched-crt/vendor/SHALLOW-TOEPLITZ.md).
For a unit symbol, write `f(z)=e(z^2)+z o(z^2)` and, modulo `z^(N/2)`, set

```text
k=o/e,       s=e-z o^2/e,
T = L diag(E,S) U,
U = [ I  ZK ; 0  I ],       L = [ I  0 ; K  I ],
E=T(e),    S=T(s),           K=T(k).
```

These blocks use even/odd coordinate order. The circuit applies `U`, then the
two child programs in any order-preserving interleaving, then `L`. A macro is
a whole completed shear. Restored logical coordinates or physical coordinate
permutations have the same infinity norm. Include both endpoint cuts. If `P`
has executed and `Q` remains, the convention is `T=QP`.

Brian's [#4731](https://github.com/CrocSwap/integer-mult-bounds/pull/4731),
head `3fcaa4d4c0568ce474c593d0882296ff43d3705a`, proves the common bound
`1/(1-eta)` for the four macro-cut operators at tail `eta<1`, with a
four-wire binomial suffix of norm `7/4` at `c=1/2`. Its sharpness witness uses
inverse operators and does not give an exact all-depth forward-suffix law.
The new contribution is that law and its unit-tail logarithmic obstruction.
The predecessor results are cited inputs, not re-verification deliverables.

## Proof

Let `M_h(c)` be the maximum forward-suffix infinity norm over the stated cuts
and schedules. The leaf gives `M_0(c)=1`. For a binomial parent,

```text
e=1,       o=c,       k=c,       s=1-c^2 z.
```

The entire even-child program is the identity. Indeed, splitting the identity
symbol gives `k=0` and two identity children at every level. Thus interleaving
its macros never changes a matrix. The sole nonidentity child is the odd child,
which is itself the binomial program with coefficient `-c^2`.

At a cut during the child phase, the remaining operator is exactly

```text
Q = L diag(I,Q_s) = [ I   0 ; c I   Q_s ],
```

where `Q_s` is any legal odd-child suffix. The even and odd column blocks
are disjoint. Therefore each bottom block row has absolute sum `|c|` plus
the corresponding row sum of `Q_s`. Every `Q_s` has unit diagonal, hence
norm at least one. It follows that

```text
||Q||_infinity = |c| + ||Q_s||_infinity.
```

The remaining cuts are before `U`, with suffix `T_N(1+c z)` of norm
`1+|c|`, and after `L`, with suffix identity. Both are at most the child-phase
maximum, because `M_(h-1)(-c^2)>=1`. Conversely an attaining child cut is a
legal parent cut after `U`; finishing an identity child is always possible.
Thus, for every `h>=1`,

```text
M_h(c) = |c| + M_(h-1)(-c^2).
```

Iteration gives the asserted formula for all complex `c`. This argument
covers every legal interleaving, rather than assuming a serial schedule.

An explicit attaining cut runs all right shears along the all-odd descendant
chain before running any left shear on that chain. Its suffix's last row, in
zero-based original coordinates, has diagonal entry 1 and entries

```text
column N-1-2^j:  c_j,       0<=j<h,
c_0=c,                     c_(j+1)=-c_j^2.
```

All these columns are distinct. For `j>=1`, `c_j=-c^(2^j)`, so its row sum is
exactly `B_h(|c|)`. At `h>=2` and `c!=0`, the already executed root `U` is
nonidentity. The unexecuted root `L` is also nonidentity; since it occupies the
opposite off-diagonal block, the prefix has not reached the endpoint. Hence
this is a proper, nontrivial cut. At `h=1` the root `U` is identity, which is
why the nontrivial-cut assertion excludes that case.

For fixed `0<=rho<1`, the finite sums converge and satisfy
`B_h(rho)<=1+rho/(1-rho)`. At `rho=1`, the exact value is `1+h`.
For `rho>1` and `h>=1`, the last summand gives
`B_h(rho)>=rho^(N/2)`, while the completed norm stays `1+rho`. These are
direct consequences of the same formula, not claims about other symbols or
other implementations.

## Exact finite evidence and reproduction

The standard-library checker constructs literal parity matrices independently
of the formula and enumerates all reachable `(P,Q)` matrix pairs bottom-up.
At each node every pair of child cuts occurs in some legal interleaving, so
the Cartesian product covers all schedules without listing equivalent ones.
It verifies `QP=T` at each constructed cut and compares the maximum suffix
norm and an attaining last row with the closed form. It imports no predecessor
executable code.

The fixed domain is `c` in `{0,1,-1,2,-2,1/2,-1/2,3/2}` and `h=0,...,5`.
These 48 rational fixtures enumerate 223 distinct cut pairs, counted separately
for each fixture. Eight controls cover a wrong Schur sign, a missing left
shear, reversed factor order, an endpoint-only bound, extending the binomial
formula to different support, and three invalid-domain inputs. Explicit
checks remain active under `-O`. The script emits a generated receipt binding
the five package files by SHA256. No receipt is hand-written or committed.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/triangular-parity-binomial-suffix
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/triangular-parity-binomial-suffix/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/triangular-parity-binomial-suffix/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/triangular-parity-binomial-suffix --check-source-history
```

Expected direct marker: `PASS_BINOMIAL_SUFFIX fixtures=48 controls=8`.
For `c=1/2`, dimensions 4, 8, 16 and 32 give exact maxima `7/4`, `29/16`,
`465/256` and `119041/65536`. At `c=1`, the corresponding maxima are 3, 4, 5
and 6. The written induction supplies the all-depth complex statement;
finite rational checks do not establish it by themselves.

## Limits and code constraints

No cuts inside a shear, rounded arithmetic, Gaussian gauge conversion,
fixed-tape costs, compiler admission, full selected replay or formal proof
kernel are covered. This theorem does not contradict the retained strict
`eta<1` stability assumptions. No universal suffix optimum over all symbols
with a specified tail budget is asserted.

The verifier has no recursion, dynamic imports, network calls or subprocesses.
Functions fit within 60 lines. Fixed fixtures enforce `N<=32`; the bottom-up
tree has at most 63 entries and each node permits at most 256 cut pairs.
Python's managed allocations and exact-rational temporaries are a documented
deviation from fixed-allocation operation. This finite checker has bounded
collection capacities and no exposed input interface. If the finite fixture
domain grows, its matrix, cut-count and rational bit-size bounds need review
before changing these limits. Warning-as-error and optimized replay provide
the available standard-library diagnostics; no additional linter is installed
or run here.

## Open next questions

What is the sharp forward-suffix envelope over *all* symbols with tail l1 at
most `eta<1`? The binomial lower envelope here and #4731's common upper
envelope leave a gap. It matters for a one-sided precision ledger. A feasible
first step is an exact four-wire optimization with independent even/odd
coefficients, followed by a row invariant that preserves their correlation.
The blocker is that the simple scalar recurrence here uses the identity even
child and does not apply to a general symbol. No further search is included.

## Sources, overlap and credit

Canonical base is `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision
7. [SOURCES.json](SOURCES.json) pins historical catalogue/selected provenance,
the retained factorization, and Brian's two predecessor notes. None is an
executable input to this self-contained checker. The original card's historical
baseline schema is stale; the current selected source-binding orientation
passed, without running a native or operator replay.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132795)
followed live open/own PR lists, recent handoffs and active discussions,
distinctive-term searches of every tracked main-branch package README, merged
PR searches and a local reservation. The card overlap report explicitly has
sparse local omissions; the separate Git-object README searches cover that
textual gap for the target terms. These searches do not prove novelty outside
their coverage. Concurrent signed finite-prefix, superunit forward-prefix,
and internal FFT-cut claims study different questions.

This result was produced by Nick Petalas. Credit Vlado Vojdanovski for the
retained parity compiler, Cinna Davis for its later Gaussian caller, Brian for
the four-cut envelope and forward-prefix theorem, James Reed for the
one-level tail accounting and finite-prefix examples, and the predecessor
lineage retained in their packages. Their files and credits are unchanged.
New work is Apache-2.0. Independent human and formal proof-kernel review are
unclaimed.
