# A physical, coefficient-bound inverse for one ordinary fine-gap run

Prepared for @CubeJerry with substantial OpenAI Codex assistance; Apache-2.0.
The mathematical Gaussian factorization belongs to Dugongue's
CrocSwap/integer-mult-bounds#5571. The actual signed convolution and exact
word routines are inherited from Jose Manuel's #3851 and #3787, including
the corrected normalized-product dependency of #3709. This proof establishes
their complete run-level physical composition. It does not re-prove those
identities or promote a finite replay into an all-size theorem.

## 1. Proposition and exact boundary

Fix the authenticated rational `Reference` and an ordinary source interval
`[s,s+n)` admitted by `coefficients.prepare`. Its original Beatty phase is
constant, it does not cross the period cut, and `2(n-1)<S`. Let `H_run` be
the principal submatrix at the corresponding *selected target coordinates*
of the fixed rational narrow Reference. Use `X>=1` and an integer `t>=0`.
The producer rejects a fixed Reference whose inherited error/gap does not
fund the requested accuracy. Its returned plan and six streams are part of
the hypothesis, not arbitrary user-supplied coefficients.

For a real input vector `x` on grid `2^-f` with infinity norm at most `X`,
`RunInverse.run` returns a grid vector `y` with

    ||y - H_run^-1 x||_infinity <= plan.total_error <= 2^-t.

The output consists of exactly `n` signed `W`-bit records in increasing
original run order. It preserves all eleven borrowed stream/Count tapes,
including their bytes and origin heads, and erases every owned body other
than the protected return. Its number of physical roles is independent of
all numerical parameters. The caller must physically consume, clear and
erase the protected return before the next invocation.
Protection here is the caller's ownership/consumption contract. It is not
a robust pending-output flag or a promise of clean recovery from arbitrary
out-of-contract manipulation of a private return head or body.

The proposition inherits the precise Gaussian, interval and actual-word
correctness results pinned in `SOURCES.json`. The selected construction's
five framework assumptions remain unchanged. In particular this is neither
the periodic Schur correction nor a complete Gaussian/CRT/multiplication
caller. **No new kappa.** A complex caller can run the real consumer twice
with target `t+1`, paying both passes and its component conversion; their
combined component-l1 error is then at most `2^-t`.

## 2. Source-bound pages and arithmetic semantics

`COEFFICIENTS.md` proves the admitted geometry, bounded source exponential
arguments, inward coefficient error, local gauge reserve, complete carrier
range and accumulation of rounding/tail/source error. No global diagonal
`exp(a beta_i^2/theta)` is evaluated. The producer never queries a Reference
entry or global similarity weight. Its interval/integer preparation is an
explicit separately paid algorithm, not claimed to be an observed
finite-control tape trace.

`run_pages.EncodedPages` emits the actual six tapes using the unchanged
`ring_words.write_signed` function and creates four distinct canonical
Count tapes. Its bounded host tuple inventories are preparation state.
Numerical coefficient values enter the online consumer only as physical
two's-complement, least-significant-bit-first records. Emission and cleanup
are paid; an input-independent Python integer is not treated as an online
unit-cost word. The emitted coefficient body has at most `14nW` bits.

For a signed integer numerator `v`, let `trunc_f(v)` discard the last `f`
magnitude bits toward zero. Every diagonal product uses the actual exact
scalar word engine before that truncation. Every residual convolution uses
the inherited four signed Kronecker products and truncates only after the
entire convolution coordinate is summed. A recurrence row computes

    y_i = trunc_f((z_i << f) - mu_i y_previous).

The product is not rounded separately. The physical probe `f=2,W=8`, input
numerators `(1,1)`, recurrence numerators `(0,1)` returns `(1,0)`; the literal
product-first rounding mutation returns `(1,1)`. Both run on the same actual
word cohort. No implicit exact-real operation occurs in the online program.

## 3. The residual block identity and local access invariant

Use oriented traversal position `k`, block length `b=min(L,n-k)`, overlap
`c=min(L,k)` and window length `N=c+b`. The page supplies, in order, `N`
inverse input gauges, `N` signed kernel values and `b` output gauges. For
an output anchor `u` and orientation `sigma` the inherited recentering is

    d_i = exp(a theta (i-u)^2),
    k_r = (-1)^r exp[-a(3rho-2sigma beta_u)r] / F_r, 0<=r<=L,
    k_r = 0, r>L.

For `i-j=sigma*r`, constancy of the original phase gives
`beta_i=beta_u+theta(i-u)`. Therefore

    d_i k_r / d_j
      = (-1)^r exp[-a(3rho-2sigma beta_i)r-a theta r^2] / F_r,

which is exactly the inherited residual coefficient. All relevant distances
from the anchor are at most `L`; no full-run gauge appears. The prepared
rounded factors and the numerical proof account for perturbing this exact
identity and for omitting `r>L`.

At the start of a physical block, the source head is at record `k-c` and
the page head is at that block's first field. `residual_block` reads exactly
`N` source records, performs their input scales, and consumes the next
`N` page records as kernel bits. The convolution return has `N` records.
It physically consumes the first `c`, scales exactly the final `b`, and
checks the return ends there. The page head now follows the final output
gauge. Its temporary data/kernel tapes and the entire child return are
erased after use.

The source head now lies at `k+b`. If another block remains, the program
moves it backward by `min(L,k+b)` records. This is exactly the next start.
It never rewinds the whole `n`-row source between blocks. At the last block
both source and page must end at BLANK and the encoded completed count is
`n`. Only then are their borrowed origin heads restored. This induction
includes a short final block and proves every access and discarded return
is present in the physical program.

## 4. Complete factor order and preservation

The full schedule in original data order is

    F^-1 ; R_minus ; C_minus ; F ; reverse ;
    R_plus ; C_plus ; reverse ; F^-1.

Each upper-orientation coefficient stream already uses reverse traversal.
The two reversals move whole physical records and preserve their internal
bit order. The `F` and `F^-1` arrays retain their original run index.
Reindexing them by reverse traversal would implement a different matrix.

The two full-run scratch buffers alternate ownership. Before a buffer is
overwritten, its existing physical body is cleared through `borrowed_tape`;
its lease is kept until the end of the invocation. Ending a lease and then
reusing it would violate the predecessor pool contract and is not done.
Each recurrence retains just its preceding signed value. Exact differences
may occupy a wider temporary than `W`; the proved carrier bound applies
after rescaling, not before it.

The consumer validates that all seven numerical tapes and four descriptor
tapes are pairwise distinct and outside every fixed owner/descendant role,
including inactive FFT pools. Variable loop bounds and arithmetic values
are Count/Signed tape words; host booleans and the fixed structural port
tuples are finite control. Diagnostic counters never affect computation.
`sealed_constructors` prevents new physical roles during execution.

The inherited helpers restore Count heads and source heads at their
documented boundaries. The outer `finally` blocks restore all borrowed
origins and close all live leases. Each owner erases its markers when
closed, except the returned body awaiting caller consumption. The finite
verifier inspects every fixed role, not merely the direct caller pool.

For `n=1`, `L=1`; the certified `F` values and three residual fields are
one, and both recurrence fields are zero. The specialized path checks
those exact pages and copies the single arbitrary data record. This is
the exact inverse of the one-row unit block, with no word multiplication.

## 5. Complete online invoice

Let `r=ceil(n/L)` for `n>1`. In either orientation the window lengths obey

    sum_b N_b = n + L(r-1) < 2n.

There are three full diagonal passes, two `n`-row recurrences, two output
gauge passes and two sets of input-window scales. The exact scalar product
count is consequently

    3n + 2n + 2n + 2[n+L(r-1)]
      = 9n + 2L(r-1) <= 11n.

The exact packed-product count is `8r`: four sign products for each of
two orientations. One convolution window has signed magnitude lengths
at most `W`, slot width at most `2W+ceil(log2 N_b)+1`, and packed operand
width at most `N_b[2W+ceil(log2 N_b)+1]`. All four product returns, including
unused high slots, are physically consumed and erased by the inherited
convolution routine.

Let `M(v)` include the actual word engine's setup, numerical recovery and
cleanup. The full online time is

    O(n M(W) + sum_over_both_orientations M(N_b[2W+ceil(log2 N_b)+1])
      + nW + r log(n+2) log(W+2)).

The last terms cover complete reading of encoded input tapes, source
backsteps, both reversals, all local copies/clears, canonical descriptors,
block comparisons and encoded products such as `N_b W`. Page generation
and initial emission are separate preparation, never silently folded into
one arithmetic callback. Binary increment/countdown are the inherited
amortized ripple routines; an iteration does not rescan the entire counter
word. Local W-bit signed scans, shifts and comparisons are charged as well.

The plan enforces `W>=ceil(log2(n+1))+2`. Thus the metadata term and the
extra slot logarithm are absorbed, giving

    O(n M(W) + sum_both M(N_b W))
    = O(n W log^2(LW+2))

under the inherited actual `M(v)=O(v log^2(v+2))` bound of #3787. Its FFT
dependency is acyclic and does not call the proposed improved integer
multiplier. This package inherits that proof; its finite fixtures happen
to exercise the fixed4096 crossover's exact base branch, not its FFT
branch. `n=1` instead costs O(W) complete page checks and copying.

In the fine-gap regime described in `COEFFICIENTS.md`, `L=O(p/log p)` and
`W=O(p)`. The online bill is therefore `O(n p log^2 p)`. For a family of
runs use the actual capped `L_i<=n_i` and sum these invoices; a tiny final
run is not charged an unexecuted full-L convolution. This local invoice
alone makes no claim about the complete assembled multiplication bound.

## 6. Retained space, reuse and independent evidence

The two full-run buffers and output require O(nW) cells. All temporary
windows, packed words and word-child retained storage require O(LW)
cells; numerical controls occupy O(W+log n). The six page bodies require
O(nW) cells and the optional host preparation tuples are separately
charged O(nW) bits as long as retained. There are a fixed number of pools
and roles; their retained high-water storage is charged, even when blank.

The separately priced preparation workspace is not part of this online
tape bound. In particular a fresh preparation's `O(nB+B^2)` workspace
invoice does not remove cached source `pi_interval` values produced by
earlier different-Q preparations. Across preparations add the retained
cache history to the current workspace, or explicitly clear those caches
with paid cleanup. Neither `EncodedPages.close` nor clearing online tapes
claims to erase or deallocate that host interval cache.

Scalar and packed multiplication use separate fixed word owners. Moreover,
the inherited `Tape.clear` scans the live contiguous body only up to its
first BLANK; it never scans an old blank backing tail. A separate reviewer
checked the exact source and compared fresh versus long-then-short traces.
The new program preserves that dense live-prefix invariant. Repeated runs
therefore retain the maxima of their role extents, not the sum of all past
extents, and cleanup does not introduce a hidden L factor per scalar.

The executable checks combine source-authenticated actual tape execution,
an integer rounded-schedule oracle, and a separately authored inverse of
the original rational Reference matrix. The last oracle derives selected
coordinates from source/target sizes, queries original entries, computes
an exact rational inverse and checks every matrix identity entry. It does
not use the coefficient pages or factorization. Its checks of the actual
physical output are independent mathematical verification, not an
independent implementation of the inherited multiplier.

Finite replay and mutation receipts are documented in README/REVIEW. The
all-size conclusion rests on the page proof, the invariants and complete
invoice above together with explicitly inherited source propositions.
