# Exact earlier-source compact-control agreement

Status: mathematical audit / research note. No new kappa.

## Statement and dependencies

Use the **unchanged earlier-source word** in
[`notes/compact-control-movement.tex`](../../notes/compact-control-movement.tex),
at base `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.
Exact input hashes and the executable's import closure are in
[`SOURCES.json`](SOURCES.json). This is an address identity, conditional on
the source's complete independent fields and controlled rotations.

Let `n >= 1`, `G >= 1`, `K >= G+1`, and `0 <= rho < K`. Set

\[
B=2^G,\qquad A=2^{K-1},\qquad R=2^K=2A.
\]

There are `f=n+1` selected positions. As in the source, the raw word handles
the first `n`; the highest one is supplied separately. Divide out the
unchanged low `rho` target bits. The remaining target has modulus
`Y=2^((n+1)K-rho) >= 2R^n`. Its processed digits are
`v_i=2g_i+a_i`, with `0<=g_i<A` and `a_i` a bit. Write `z_i` for the
source bits, and `t_i` for the radix-`B` dirty temporary digits.

**Claim.** Suppose every `t_i <= B-2`. The raw word produces the intended
low-selected XOR **and restores the complete temporary field** if and only if

\[
\boxed{g_i+z_i t_i<A\quad\text{for every }0\le i<n-1.}
\tag{1}
\]

The arbitrary back field is restored by each swap sandwich. Source bits and
unselected bits must also be preserved. There is no condition on `g_(n-1)`:
the last outgoing carry is harmless. For `n=1`, (1) is empty, agreeing with
the nonsaturated part of @martinxxx9's one-digit law in
[#1108](https://github.com/CrocSwap/integer-mult-bounds/pull/1108).

## Necessity, including dirty-field failures

Let `c_i` be the carry into processed target digit `i` during the first
rotation. Then

\[
c_0=0,\qquad
c_{i+1}=\left\lfloor\frac{v_i+2z_it_i+c_i}{R}\right\rfloor,
\qquad a'_i=(a_i+c_i)\bmod2.
\tag{2}
\]

Since `B<=A` and `t_i<=B-2`, induction gives `c_i` in `{0,1}`.
The following compact load has no carry: every loaded digit is exactly
`t_i+a'_i <= B-1`. Cancelling the `2z_i t_i` terms between the two target
rotations gives

\[
y'-T(y)\equiv
\sum_{i<n}2z_ic_i(2a_i-1)R^i\pmod Y,
\tag{3}
\]

where `T` is the ideal low-selected XOR. This integer sum has magnitude
at most `2 sum_(i<n) R^i < 2R^n <= Y`. Its largest nonzero term strictly
dominates the sum of all smaller terms (`R>=4`). Hence target correctness
is equivalent to `z_i c_i=0` for every processed digit.

Even when this condition holds, a carry into a source-zero digit can
corrupt the temporary. If the target is correct, the final unload subtracts
the original parity vector `sum a_i B^i`. Thus

\[
t'-t\equiv\sum_{i<n}(a'_i-a_i)B^i
=\sum_{i<n}c_i(1-2a_i)B^i\pmod{B^n}.
\tag{4}
\]

The same largest-term argument applies for `B>=2`, and the magnitude is
strictly below `B^n`. Consequently full restoration requires every
`c_i=0` for `0<=i<n`. Conversely those zero carries make both (3) and (4)
zero. With `c_0=0`, recurrence (2) gives exactly (1), by induction.
The last carry `c_n` appears in neither equation. This proves the claim.

For a small exact witness, take `n=2,K=3,G=2,rho=2`, projected `y=6`,
`t=1`, `z=1`. The raw result is `(y',t')=(7,5)`, while the ideal result is
`(7,1)`. The target is correct and the dirty temporary is wrong. In the
physical fields this is `x=4,y=24,t=1` with arbitrary back field. It lies
exactly on the forbidden boundary `g_0+z_0*t_0=A`. The same projected
`(y,t,z)=(6,1,1)` with `n=1` gives the correct `(7,1)` despite its outgoing
carry. These distinguish an interior read from the final boundary.

## Invariant envelope and exact density

Define `H` by nonsaturation of all temporary digits together with (1).
The ideal XOR changes only the `a_i`, so it preserves `H`. The physical
raw word `S` is a bijection on the entire complete address rectangle:
each rotation's offset is independent of its target, and each swap is
invertible. By the claim, `S=T` on `H`. Thus `S(H)=T(H)=H`; its complement
is invariant too. The source's correction `T S^-1`, evaluated on current
addresses, therefore repairs precisely that complement as a permutation.

This is an **exact agreement criterion inside the nonsaturated-temporary
domain**, and an invariant sufficient envelope on the entire rectangle.
It is not the global exact failure support: for example, a zero source
with saturated temporary can still be correct. The census records that
distinction explicitly.

For an interior digit, summing over independent `z,t,g` gives

\[
\#H_i=\sum_{t=0}^{B-2}\bigl(A+(A-t)\bigr)
=2A(B-1)-\frac{(B-1)(B-2)}2.
\]

The last digit needs only nonsaturation. The exact complete-rectangle
good fraction and a corresponding union bound are therefore

\[
\boxed{\Pr(H)=\left(\frac{B-1}{B}\right)^n
\left(1-\frac{B-2}{4A}\right)^{n-1}},
\qquad
\delta=1-\Pr(H)
\le\min\left(1,\frac nB+\frac{(n-1)(B-2)}{4A}\right).
\tag{5}
\]

The original guard additionally requires `2B<=g_i<A-2B` at every digit.
It implies (1). Its exact good fraction is
`[((B-1)/B) * max(A-4B,0)/A]^n`. For `n=2,K=6,G=2`, the new fraction is
`567/1024`, versus `9/64` for the original. These are guard-envelope
fractions, not measured execution speedups.

## Complete retained price and limitations

The earlier-source word still uses four compact swaps and four controlled
rotations, including both source-dependent offset calculations and both
temporary updates. The highest selected XOR still costs `O(V)`. All fields
remain dirty complete ranges; no helper is initialized for free. With `M`
records, payload width `P`, address width `L`, and `V=MP`, the retained
exceptional repair cost remains

\[
O\bigl(V+ML^3+\delta ML(P+L)\bigr).
\]

This includes scanning the predicate, extraction, inverse-address
calculation, destination-key calculation, sorting full records and keys,
reinsertion, rewinds and cleanup. The new comparisons scan at most `n<=L`
digits and stay within the retained polynomial descriptor allowance.
Under the source's `G=4 ceil(log2 p)+6`, `f<=p`, `K/log p -> infinity`,
`L=O(p)` and superpolynomial payload hypotheses, (5) still makes repair
`O(V)`. The existing earlier-source cost remains
`O(V*((f log p)^tau+1))`; no recursive child, supplier moment, or outer
constraint changes. This audit does not install the new predicate in any
production caller or certificate.

Later-source calls, recursive field reservations, physical compilation,
hosting, precision, tape realization and analytic transfer are not
reverified here. No new supplier, kappa, formal proof-assistant theorem,
or full multiplication theorem is claimed. Finite permutations support
the written all-`n` argument; they do not prove that argument by themselves.

## Distinct scope and credit

Douglas Colkitt supplied the compact-control construction, repair argument
and simulator; OpenAI supplied the original framework. John-Michael
Smith's [#763](https://github.com/CrocSwap/integer-mult-bounds/pull/763)
studies later-source compact-load carries while retaining the original
target guard. @martinxxx9's #1108 establishes the one-digit earlier-source
law and repeated-boundary obstruction. This audit adds the multi-digit
target-carry **iff**, the target-invisible dirty-field witness, and (5).
Aryan Sudhir's [#735](https://github.com/CrocSwap/integer-mult-bounds/pull/735)
and Precious Oyetunji's
[#773](https://github.com/CrocSwap/integer-mult-bounds/pull/773) concern the
different eight-rotation wide-slot gadget. No code from those PRs is used.
Their exact inspected heads are retained in `CLAIM.json`.

Prepared for Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance
in derivation, implementation, verification and writing. Apache-2.0.
No independent human peer review or literature-priority claim.
