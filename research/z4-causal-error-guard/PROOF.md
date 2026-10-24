# A causal sufficient guard for relative ADD errors

This scoped proof uses exactly the relative-error model in ywz65's PR2502.
The signed word and its exact endpoint are inherited from Cinna Davis's
PR1391 and PR1410. Their correctness is a cited premise, not the result of
this package. The new conclusion concerns the error at every chronological
cut of that unchanged word.

## 1. Quantified model

Let a finite signed word act on n real registers. An ADD replaces register d
by register d plus sgn times register s, where s differs from d and sgn is
1 or -1. NEG is exact. Initial register values are exact and have absolute
value at most B, with B >= 0. All registers, including workspace, may be dirty.
Each implemented ADD i adds a possibly adversarial error e_i after its exact
signed update, satisfying

    |e_i| <= u (|approximate d before i| + |approximate s before i|).

Here u is nonnegative and uniform. There is no overflow, input error or other
error source. In particular this theorem does not model rounded child calls,
nonlinear leaves, inexact NEG or finite integer range.

Let P_c be the exact input-to-register matrix after c signed records. Let
G_c[r,j] be the signed coefficient of error j in register r after cut c.
Set G_c[r,j]=0 before ADD j occurs. Linear superposition gives

    approximate x_c[r] - exact x_c[r] = sum_j G_c[r,j] e_j.

For the cut immediately before ADD i, define the nonnegative integers

    a_i = ||P_before[d,:]||_1 + ||P_before[s,:]||_1,
    H_ij = |G_before[d,j]| + |G_before[s,j]|,   j < i.

Then

    |e_i| <= u (B a_i + sum_(j<i) H_ij |e_j|).                 (1)

The coefficients H form a strictly lower-triangular matrix. No self-dependent
maximum error, geometric series or contraction hypothesis is needed.

## 2. Integer certificate theorem

Choose integers q >= 0 and S > 0. Put U=2^q. In chronological ADD order set

    b_i = S a_i + ceil(sum_(j<i) H_ij b_j / U).                (2)

For every u <= 1/U, induction in (1) proves

    |e_i| <= B u b_i / S.                                   (3)

Indeed all earlier errors obey (3), and replacing u by 1/U in the resulting
nonnegative inner sum gives precisely the right side of (2). The ceiling
only enlarges that side. This also proves (3) when B=0 or u=0.

Define the integer

    C_num = max_(c,r) sum_j |G_c[r,j]| b_j.                   (4)

Equations (3) and superposition imply the uniform all-cut bound

    E <= B u C_num / S.                                    (5)

Only the updated destination row changes at each record. All initial error
rows are zero. Taking the maximum over each newly updated row therefore
computes the maximum over every row and cut in (4), including the final cut.
NEG changes signs without changing absolute row bounds, and is still executed.

If C_num <= S*2^q, then for every real b >= 0 and every
u <= 2^(-b-q), equation (5) proves E <= B*2^-b. The same certificate works
for all b because the induction already covers every u <= 2^-q.

This is a sufficient guard theorem. It neither minimizes actual precision
nor asserts that adversarial error signs can arise from a specific rounding
implementation. The absolute values in (1) can still overestimate errors.

## 3. Application to the persistent joint forward word

Use PR1410's ten-child joint forward word on 56 registers. Its exact word
SHA256 is

    901dc9ffbd0f59b8988a3796cef037fbba8caa3ffeb6053b1b816b53e818b844

The word has 1,904 signed records and 1,720 ADD events. These identify the
inherited word; no new endpoint or word-count result is claimed.
The new recurrence (2), with q=13 and S=2^32, gives

    C_num = 30186730759261,
    C_num / S < 7029 < 8192 = 2^13.

The maximum is at record cut 1730, register 4, with cuts numbered from 1
and registers from 0. Thus the unchanged forward joint word satisfies

    E <= B*2^-b   whenever u <= 2^(-b-13), for every b >= 0.

PR2502's uniform feedback argument gave a sufficient q=14 in this same
model. The causal argument saves one sufficient fractional guard bit.
It does not contradict that predecessor theorem or claim q=13 is necessary.
The predecessor's separate-call or inverse guard values are not recomputed
and no improvement of those values is claimed.

## 4. Exact evidence and independent calculation paths

The primary algorithm propagates sparse exact input rows and signed error
impulse rows forward. It evaluates (2) using integer upward rounding and
retains the maximum in (4). No floating-point arithmetic occurs.

The second algorithm starts a dense coordinate covector at each requested
cut and traverses the signed word backward. Immediately after an ADD, its
destination component is that event's error coefficient. Before the ADD,
its source component gains sgn times its destination component. NEG negates
the destination component. The resulting input covector and chronological
error coefficients independently reconstruct every a_i, every feedback sum
in (2), and every updated-row value in (4). There are 1,720 recurrence
comparisons and 1,904 all-cut comparisons, using 5,344 adjoint traversals.
It shares the word and integer bounds with the forward algorithm, but no
coefficient-propagation implementation.

The two-ADD word x+=y; x-=y gives a_1=2, a_2=3 and H_21=1.
At q=3, (2) gives b/S=(2,13/4), so C=21/4 and the guard passes.
Its exact endpoint is identity, yet its error bound is positive. Controls
reject an omitted previous error and a one-unit understatement, verify a
negative impulse across NEG, reject invalid gates, and reject q=2 for this
same tiny word. All checks remain enabled with optimized Python.

## 5. Limits and implementation bounds

The Python path accepts at most 2,048 records on at most 56 registers and
0 <= q <= 32. All loops have finite input-derived bounds; functions remain
below 60 physical lines. Sparse input rows have at most 56 entries and each
error row at most 2,048. At most 2,048 error bounds and cut values are live.
Python integers, dictionaries and the pinned emitter allocate dynamically;
this is a bounded research computation, not a fixed-allocation runtime.
The inherited emitter has finite phase-dependent helper calls and is not
changed. Source hashes bound the dynamically imported emitter to one file;
its main verifier and search are never called. The verifier uses explicit
ValueError checks that survive -O and warning-strict registered execution.

The proof is written mathematics with exact finite corroboration, not a
proof-kernel result. It establishes no physical host precision bucket,
workspace lifetime, supplier admission, exponent or selected-frontier change.
