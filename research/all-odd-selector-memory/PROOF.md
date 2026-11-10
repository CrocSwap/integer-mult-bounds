# Exact classical state memory for the all-odd selector

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and result

Fix `n >= 2`, put `m=n-1`, and read a finite word of columns
`x_j in F_2^n`. For each `v in F_2^n`, set

```text
f(v) = sum_j parity(x_j dot v) mod 4.
```

Accept exactly when `f` is constant on every odd-weight vector `v`.
The input is a classical sequence of Fourier labels. No access to such
labels inside a physical coefficient field is assumed.

At each column boundary, a deterministic recognizer retains a state.
Transitions can be arbitrary nonlinear functions, and accepting is exact.
The size counted is the number of distinguishable retained states, including
any input-dependent control state. Immutable program descriptions and the
current input symbol are not counted as mutable state. For known width,
the position and total width can be supplied externally, and transition
functions may depend on both.

**Theorem.** The minimum number of retained states for all finite widths is
`2^D`, where `D=m(m+3)/2=(n-1)(n+2)/2`. Exactly `D` binary state bits suffice,
with every letter transition reversible. For every separately fixed known
width `lambda >= 2D`, the same state lower bound holds at the cut after
`D` columns, even with position-dependent transitions and nonlinear encoding.
The `D`-bit construction attains that bound at every column boundary.

For `n=73`, the exact minimum is 2^2700 states, or 2700 binary state bits.
The stated fixed-width conclusion applies from `lambda=5400`. No claim
that this sufficient width threshold is smallest is made.

## The credited signature quotient

Ali Romman's PR4714 gives the signature quotient of this selector, in
`affine-centre-access`, QUOTIENT.md Sections 3 and 4. We cite that quotient
as a premise, without replaying its geometry, densities or physical stream.
In coordinates it is the additive group

```text
Gamma_m = (Z/4)^m x (F_2)^(choose(m,2)).
q(t) = sum_i a_i t_i + 2 sum_(i<j) b_ij t_i t_j mod 4.
```

Restrict `f(v)-f(e_n)` to the odd affine hyperplane
`v=(t,1+parity(t))`. Acceptance is exactly `q=0`. A column
`x=(x_1,...,x_m,epsilon)` contributes

```text
y_i = x_i + epsilon mod 2,
q_x(t) = (-1)^epsilon parity(y dot t) mod 4,
a_i += (-1)^epsilon y_i mod 4,
b_ij += y_i y_j mod 2.
```

The displayed update also follows directly by expanding parity modulo four.
Every pair `(y,epsilon)` is an allowed column, so both signs of every step
are available. Complementing all `n` input bits preserves `y` and reverses
the sign. Thus the transition for the complemented column is the inverse.
The zero column has zero contribution and can pad any word.

There are exactly `4^m 2^choose(m,2)=2^D` coordinate states. Distinct
coordinates give distinct functions: values at unit vectors determine
`a_i`, and values at `e_i+e_j` then determine `b_ij`. Maintaining these
coordinates proves the upper bound and reversible-transition assertion.
The quotient and its coordinate compression are predecessor results.
The matching lower bound, bounded suffixes and known-width conclusion
below are the new application.

## Bounded reachability of every state

Every element `g=(a,b)` is represented by a word of length at most `D`.
For each pair with `b_ij=1`, use the positive step `s_(e_i+e_j)` once.
This gives the desired mixed coefficients and some diagonal coefficients
`d_i`, at a cost of at most `choose(m,2)` letters. Correct coordinate `i`
by the residual `a_i-d_i mod 4` using the following signed unit steps:

| Residual | Letters |
| --- | --- |
| 0 | none |
| 1 | `+s_ei` |
| 2 | `+s_ei,+s_ei` |
| 3 | `-s_ei` |

At most `2m` further letters suffice. Hence the total is at most
`choose(m,2)+2m=D`. Pad with zero columns to get exactly `D` letters.
Call one such word `u_g`.

An inverse word is obtained by reversing `u_g` and complementing each
column. It also has length `D` and represents `-g`. Denote it by `v_g`.
These constructions do not enumerate Gamma_m or store an exponential
transition table. The reference implementation bounds its supported
dimension by 73; the written construction holds for every finite `n>=2`.

## Distinguishable prefixes give the matching lower bound

After reading `u_g`, a correct recognizer must distinguish every `g`.
Indeed, append `v_g` to it. The total signature is zero, so the result is
accepted. Appending the same suffix to `u_h`, for `h!=g`, gives nonzero
signature `h-g`, which must be rejected. If those two prefixes had the
same retained state, deterministic processing of their common suffix
would give the same answer, a contradiction.

Thus at least `|Gamma_m|=2^D` states are necessary at this cut. This is
the classical distinguishable-continuation argument, applied to the
credited quotient, rather than a new general automata theorem.

For a known total width `lambda>=2D`, append `lambda-2D` zero columns
after each distinguishing suffix. All prefixes have the same length `D`,
and all compared continuations have the same length `lambda-D`. Therefore
externally known positions, width-dependent transition schedules and
arbitrary nonlinear state encodings do not change the contradiction.
Any binary encoding of `2^D` distinguishable states needs at least `D`
bits. This includes all varying retained data, rather than just a named
signature register.

## Scope and consequence

Any exact one-pass classical selector for this complete sector must retain
the full quotient information at a sufficiently long cut. A proposal to
replace the Haar tree by a smaller deterministic selector cannot merge
these states while retaining exact all-input recognition. The result also
provides an explicit reversible selector with optimal boundary memory.

This is a classical state-count statement. It gives no lower bound on
linear transfer dimension, circuit size, physical workspace or execution
time. The program can be succinct despite its exponential state count.
Computing this classical predicate does not implement its spectral
projector on an arbitrary field. Access, tape layout, encoding, restoration,
precision, complete paid invoices and supplier admission remain separate.
Approximate recognition, randomized error, multiple passes, an input
promise, a different sector or shorter known widths are outside the theorem.
All five selected framework assumptions remain. No new kappa or complete
multiplication theorem follows.

## Finite corroboration

The verifier checks every coordinate state at `n=2,3,4`, represents it
by the new bounded word, and compares it with direct modulo-four phase
evaluation on every odd physical vector. It checks every one-column
transition and its complemented inverse, then every prefix/suffix pair.
The literal oracle does not use quadratic-coordinate updates. The written
proof supplies the unbounded quantifiers; these finite cases corroborate it.
