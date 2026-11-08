# Independent audit of the physical finite-run inverse

Prepared for @CubeJerry with substantial OpenAI assistance by a separate
source-aware verifier. This review supports the integrated contribution;
it is not a separate mathematical claim or a formal kernel proof.

## Scope and provenance

The q-LDU inverse, residual factorization and local gauge identity are
inherited from CrocSwap/integer-mult-bounds#5571. Signed exact convolution
and the actual word multiplication routine are inherited from
CrocSwap/integer-mult-bounds#3851 and
CrocSwap/integer-mult-bounds#3787. The review concerns their concrete
finite ordinary-run consumer and certified coefficient pages. It claims
no periodic Schur recovery, no complete Gaussian or integer caller and
no new kappa.

The executed consumer fixture uses Reference(61,3,1,4,8,80), source
indices 11 through 30, target indices 12 through 31, and phase one.
The interval of 21 rows starting at 11 crosses a phase change and is
invalid. This distinction was checked directly from the original
nearest-integer definition before the final fixture was chosen.

## Algebra and numerical contract

Reading the inherited factorization from right to left gives the
physical schedule Finv, Rminus, Cminus, F, reverse, Rplus, Cplus,
reverse, Finv. The F index is relative to the interval origin, while
the phase and recentering anchors are original absolute source indices.
The upper residual uses reversed traversal and its own absolute anchor.
No F diagonal is moved across that reversal.

For a block starting at traversal k, b=min(L,n-k), c=min(L,k), the
parent reads [k-c,k+b), applies its N=c+b short lower convolution,
and discards the first c results. This is exactly the portion of the
truncated triangular residual affecting its b assigned output rows.
The source head ends at k+b and moves backwards by min(L,k+b) rows
before the next block. Thus the implementation neither loses overlap
nor returns to the start of the full input for each block.

The recurrence forms the entire doubled-grid difference before one
toward-zero shift. For example, grid precision two, rhs numerators
(1,1) and mu numerators (0,1) must produce (1,0). Rounding the product
first instead produces (1,1), so the two conventions are observably
different even though a loose final error bound can accept both.

The producer's completed-stage error induction applies to actual
rounded incoming values. Its coefficient errors include interval
uncertainty; contraction uses inward mu. Telescoping against ideal
linear factors avoids assuming that the rounded program is linear.
The separate allowance for local gauge intermediates is necessary:
the bounded final residual norm does not itself bound those temporary
values. The current W additionally covers log(n+1), including generic
parameters outside the optimized production regime.

The rounded Reference block and the unperiodized ideal Gaussian block
are distinct matrices. The admitted interval satisfies 2(n-1)<S, so
all its pairwise nearest lifts are zero. Shared-weight-ratio entry
errors plus the omitted Gaussian row tail then compare these blocks
directly. A principal periodic-N comparison alone would leave an
alias term. The producer keeps the exact source-defined gap, including
the identity d_ideal=d_reference+E_N, rather than silently substituting
an unrelated larger empirical gap.

## Independent original-matrix test

`original_matrix_oracle.py` derives q_i=floor(T*i/S+1/2) directly from
S,T, asks the original Reference for those entries, and performs
rational Gauss-Jordan inversion. It checks every entry of H*Hinv=I.
It does not use the run producer's F, mu, residual kernels, local
gauges, recentering pages or stage simulator for its expected result.
The source service is authenticated by the integrating test; accepting
a Reference object here does not replace that authentication.

For the observed physical n=20 output, f=57,W=95,L=6 and input
numerators floor((-1)^i*(i+1)*2^57/41), every exact rational identity
residual passed. The maximum output error against Hinv*x was
approximately 6.409736255753634e-16, and the original equation residual
approximately 6.074680426261895e-16. The declared allowance is
approximately 0.001953125. The source identity is
02ae3c17493233eba218d1b6b11a51b1cdfc48274bed47d28f368c77a86f5c1b.

The following direct-oracle controls reject: transposing the original
matrix, reversing the physical output, adding one whole unit to one
returned value, and using the invalid 21-row cross-phase interval.
The oracle also self-checks two rational-exponential Gaussian matrices
whose entries are constructed directly from the original exponent;
it verifies exact inverse/action residuals and separates transpose
controls. These are finite checks, not a universal inverse proof.

## Complete online invoice

For n>1 let r=ceil(n/L). The sum of window lengths in either orientation
is n+L(r-1). Consequently the literal schedule invokes

* 9n+2L(r-1) <= 11n scalar word products;
* 8r packed word products, on widths O(LW);
* O(nW) additional sequential payload/page/reversal/erasure movement.

The observed n20 fixture used exactly 216 scalar and 32 packed products.
Both used the inherited routine's finite base branch; this fixture does
not newly test that routine's FFT branch. Its asymptotic tariff remains
an inherited, explicitly pinned dependency.

All record and block counters are encoded. `indices` uses an
amortized ripple increment and countdown, rather than a full logarithmic
scan at every payload bit. Descriptor arithmetic fits the displayed
word tariffs; W includes the counter width. Thus the online bound is
O(n*M(W)+r*M(LW)+nW), where the inherited M(v) is
O(v log^2(v+2)). The singleton has its separate exact copy path.

The parent has a fixed pool, two full-run buffers and fixed scalar
and packed child owners. Retained capacity is O(nW), including erased
backing, because L<=n and the inherited word owner has linear space.
The six prepared pages also have O(nW) storage. Across changing calls,
retain the maximum previous capacity for every role; do not claim that
erasure deallocates it. Input-independent coefficient preparation and
its larger exact-rational workspace are separate priced terms.

## Historical extent and ownership audit

The authenticated `records.Tape.clear` scans only the current dense
prefix to its first blank, erases it, then returns to the origin. It
does not iterate over the backend's retained length. Count cleanup,
lease cleanup and pool admission preserve this invariant; pool guards
inspect a fixed number of origins. Two states with equal live prefixes
and heads but different blank tails therefore take the same subsequent
primitive actions. Historical backing still counts toward space.

`cleanup_check.py` (portable adaptation of the reviewer's exact-source script) confirms this on the exact retained Tape:
histories of 1,8,128,4096 cells followed by current lengths 0,1,3,7
give the same read/write/move counts as fresh tapes in all 16 cases.
This addresses the feared packed-to-scalar cleanup factor. The
consumer also uses separate packed and scalar owners.

The initial consumer guarded its seven numerical ports but left the
borrowed-count nonalias condition implicit. The author added a guard
requiring all eleven physical ports to be external and pairwise
disjoint before descriptor comparisons. This is an interface repair;
it does not change the valid-path numerical schedule. The integrating verifier exercises that current guard, including an alias
into an inactive descendant pool.

## Verification boundary

The original20-row numerical test above consumes the author's observed
physical output; it is an independent expectation, not an independent
implementation of the physical multiplier. Its source matrix inversion
uses host rational arithmetic only in the test oracle. No host inverse
or unmetered regrouping is substituted into the production algorithm.
The narrow Tape-history replay likewise tests exact primitive methods
but is not a full multiplier benchmark. The integrated `SOURCES.json` and `VERIFY.json` pin the inputs and register
normal and optimized-Python checks. The default full physical fixture has
8 rows; the 20-row extended replay is available with `--long`. Its current
consumer SHA256 is
`3fa40a34d86a88ff38d413f91c32f7a511d3f14904aaa12003f03d04b9bf770c`.
