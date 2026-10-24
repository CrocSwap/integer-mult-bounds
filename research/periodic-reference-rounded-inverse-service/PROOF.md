# A complete periodic reference inverse action

This package implements a whole-period host-array service for the actual
immutable Reference of PR4205. It does not implement a physical tape service,
claim a sparse-seam discount, improve Gaussian constants or close the outer
multiplication theorem. The original143-row Core has no retained rows under
the sufficient R10 halo; here all385 output rows are deliberately paid for.

## Source binding and support

The retained source is gaussian_reference.py at
c9db4069d59bfad26a15fe000b91cc3a058684e5. Instantiate exactly
Reference(384,1,2,4,18,320), with target period385 and hole192. Its description
hash is4001280a290db7fe1afbbbed80704821796da86c3de8f86516b8debaf099591c.
We call its entry producer, preserving rational weight ratios, cross-cell
and cross-period branches and the hole identity. No translated or rerounded
Reference is substituted. The source coefficients can be non-dyadic rationals.

For a selected row with source index i, the only possible off-diagonal
columns are selected[(i+h) mod384], -4<=h<=4, h!=0. This is exactly the
source's nearest-period lift rule and abs(h)<=source_halfwidth predicate:
2*source_halfwidth<source_size ensures uniqueness. Hole rows contain only
the unit diagonal; a hole column has no off-diagonal entry. The verifier
independently visits every column to check this support description, including
rows0/384 and the hole. Every diagonal coefficient is checked to equal1,
every coefficient nonnegative, and every actual row sum of off-diagonals
is checked against q=1-d. The supplied d is the source gap rounded DOWN to
16 fractional bits, so it retains the inherited analytic gap certificate.
The source's global analytic gap and truncation/rounding error proofs remain
inherited; finite row checks independently corroborate the reference bound.

## Complete recurrence and error

Use the maximum over coordinates of |Re z|+|Im z|. Let H=I+A be the exact
periodic reference, with A nonnegative, zero diagonal and row norm<=q=1-d<1.
Let h=2^-P and round each off-diagonal coefficient downward once to obtain
Ahat. Thus ||Ahat||<=q and ||A-Ahat||<=m*h, where m is the maximum stored
off-diagonal count (8 in the source fixture). Setup verifies these relations
on the actual source values; zero quantized coefficients are still stored
and charged. The data are immutable signed Gaussian integers at scale2^P,
with norm<=Y. No disk-unit oracle is assumed: this service uses its own
funded integer multiply/accumulate operations.

The execution contract requires the unchanged Plan returned by prepare; an
arbitrary caller-constructed Plan is not source-certified.

Start y0=u. Repeat J-1 times:

    y_(k+1) = u - trunc_grid(Ahat y_k),

where the real and imaginary accumulated sums are each truncated toward
zero once. The local complex-l1 rounding error is less than2h (zero is
allowed). Put R=(Y+2h)/d. Since Y<=R and Y+qR+2h=R, every computed iterate
has norm<=R. No state is used outside its stated range.

For x=H^-1 u, the contraction bound gives ||x||<=Y/d and
||y0-x||<=Yq/d. Comparing an update with x=u-Ax yields

    ||y_(k+1)-x|| <= q ||y_k-x|| + m h R + 2h.

Consequently the complete returned vector satisfies

    ||y_(J-1)-H^-1 u|| <= Y q^J/d + (m h R+2h)/d.             (1)

prepare chooses J to fund the first term at most2^-t/4 and P to fund the
second term at most2^-t/4. The sum is at most2^-t/2. The original t20,Y1
fixture uses J276 and P33. This is an entire-period inverse action, not a
comparison of two implementations of a local polynomial. Independently,
the verifier applies the exact original source matrix to the computed
answer; its residual r=Hy-u gives ||y-H^-1u||<=||r||/d. This second bound
uses original non-dyadic coefficients and does not reuse quantized entries.

If an ideal analytic H0 separately satisfies ||H-H0||<=E<d, the resolvent
bound adds Y E/[d(d-E)] to (1). E is the source's retained narrow error,
including its truncation and coefficient approximation. The verifier reports
both contributions separately and admits the analytic combined target only
when funded. This conditional bridge does not independently reprove the
Gaussian analytic source or extend the claim to a production family.

## Complete work and live storage

Let N be the period, M the number of stored off-diagonal coefficients and
L the largest signed state width. Coefficient production calls the actual
Reference entry service exactly N+M times (3457 here). Its interval/pi,
exponential and rational-weight setup is executed and timed, not an O(1)
or free oracle. The original Reference caches, its entries/weights/kernels,
and generated integer table coexist during preparation and verification.
The receipt records setup cache counts and exact coefficient bit maxima;
this phase is distinct from steady-state service workspace. The retained
interval module also stays in sys.modules: its pi_interval cache retains four
precision-specific intervals, while its unused root_of_unity cache is empty.
These are intentional shared setup state, not cleared service scratch.
The maximum declared interval precision is6830bits; the384 weight receipts
have eight fields each and actual rational numerator/denominator widths at
most6831bits in the finite fixture. The receipt records these separately.
Source interval
internals and Python allocator overhead remain inherited implementation costs,
not a proved multitape bit tariff. Peak process RSS is diagnostic only.

The arithmetic service performs exactly2M(J-1) integer products,
2N(J-1) component truncations,2M(J-1) accumulator additions,
2N(J-1) input subtractions and2N(J-1) update writes. Initial scratch
construction writes4N component slots. Each scalar
accumulator has magnitude at most2^(2P) qR; a signed width bound is
2P+ceil(log2(max(1,R)))+2, including a sign/spare bit. Input, current, next
and output have2N,2N,2N,2N components respectively; the returned immutable
output coexists with both scratch arrays until their finally cleanup.
There are M immutable (index, coefficient) records and O(1) loop/accumulator
scalars, plus the plan's exact rational error constants. Preparation and
verification reference caches are not included in the4N scratch figure.
Python immutable integer sharing can reduce physical allocations; these
logical component counts do not assert a byte-exact heap allocation bound.

The input tuple is borrowed and unchanged. At return the output tuple
becomes caller-owned. Both scratch arrays have their slots replaced by zero
and are cleared on success or exception; this does not promise allocator
zeroization of immutable integer storage. Output copying and4N scratch-slot
clears are explicit paid work. The prepared table remains intentionally
resident for reuse. No hidden sequence of earlier output buffers is retained.
With integer multiplication cost M_int(L), steady-state work is bounded by
O(J M M_int(2P+log R)+J N(P+log R)), plus setup, input/output scans and clears.
This is a host-array arithmetic invoice, not random-access-free tape time.

## What is new and what remains open

New: one source-bound complete periodic producer/action, all output rows,
its combined coefficient/data/tail budget, actual work/storage accounting,
and exact original-source residual controls. Inherited: Gaussian source
analytic bounds, ordinary Core, polynomial locality and generic contraction
analysis. This package does not use ordinary Core to claim cheaper outputs.
A future physical implementation must provide an ordered periodic coefficient
and input delivery protocol, charge its scans and cleanup, and compare the
whole-period bill with an admitted ordinary/seam partition. No such saving,
physical tensor caller, multiplication theorem or kappa change is asserted.

Prepared for JoyboyBrian with substantial OpenAI Codex assistance. New work
Apache-2.0. Retained references credit Jose Manuel, Vlado Vojdanovski,
Jeremy Kothe, Cinna Davis, Mason Hale, Chafik Boukhalfa and prior contributors.
