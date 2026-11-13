# The sharp four-wire forward-suffix envelope

This is a scoped algebraic proof with exact finite corroboration. For the
retained triangular Toeplitz parity compiler on any complex symbol
`f(z)=1+bz+az²+cz³`, the maximum forward-suffix infinity norm is exactly

```text
M(a,b,c) = 1 + max(|a|+|b|+|c|,
                  |b|+|a-b²|+max(|c|,|c-ab|)).
```

The maximum includes both endpoints and every complete-shear cut of every
legal order of the two disjoint children. Consequently, for every real
`eta >= 0`,

```text
sup_{|a|+|b|+|c| <= eta} M(a,b,c) = 1+eta+eta².
```

Equality holds exactly when `a=c=0` and `|b|=eta`. The statement has no
small-tail or sign restriction. It solves the explicit four-wire optimization
suggested in [#4831](https://github.com/CrocSwap/integer-mult-bounds/pull/4831),
whose all-depth theorem concerns only binomial symbols.

For `0<eta<1`, the new four-wire suffix bound improves Brian's
[#4731](https://github.com/CrocSwap/integer-mult-bounds/pull/4731) common
four-operator bound `1/(1-eta)` by exactly `eta³/(1-eta)`. In particular,
the sharp bound is **7/4** at `eta=1/2`. The binomial value 7/4 was already
known. The additional result is the upper bound over every complex
three-coefficient tail, the complete per-symbol formula and the equality
classification. There is no new kappa or selected-frontier change.

## Contract and proof

Use the parity factorization of Vlado Vojdanovski's #1673, retained in
[SHALLOW-TOEPLITZ.md section 3](../unconditional-batched-crt/vendor/SHALLOW-TOEPLITZ.md)
and Cinna Davis's #4100 caller. In even/odd order `(0,2,1,3)`, write

```text
e=1+az, o=b+cz, k=o/e=b+(c-ab)z mod z²,
s=e-z o²/e=1+(a-b²)z mod z²,
T_4(f) = L diag(E,S) U,
E=T_2(e), S=T_2(s), K=T_2(k),
U=[I ZK;0 I], L=[I 0;K I].
```

Execute `U`, then the two child programs on disjoint coordinates, then `L`.
A macro here is one whole Toeplitz shear. The right shear in each two-wire
child is the identity, so its only nonidentity macro is its lower shear.
Identity macros add no new cut matrices. The two children can execute in
either order or in a simultaneous layer. Their possible remaining suffixes
are independently `E^epsilon` and `S^delta`, with
`epsilon,delta in {0,1}`. Every pair is realized by some legal order and cut.

Put `d=a-b²`. At a cut in this child phase, the remaining suffix is

```text
Q(epsilon,delta) = L diag(E^epsilon,S^delta)

                  [ 1                       0   0        0 ]
                = [ epsilon*a               1   0        0 ]
                  [ b                       0   1        0 ]
                  [ c-(1-epsilon)*a*b        b   delta*d  1 ].
```

Its last row has absolute sum

```text
1+|b|+|c-(1-epsilon)ab|+delta*|d|.
```

The other nontrivial row sums are `1+epsilon*|a|` and `1+|b|`.
The completed endpoint has norm `1+t`, where `t=|a|+|b|+|c|`, and dominates
both of those rows. The identity endpoint has norm one. Maximizing the last
row sets `delta=1`, then chooses the larger of `|c|` and `|c-ab|`.
Together with the completed endpoint this proves the formula for `M`.
Coordinate permutation preserves every row sum, so it also holds in the
original coefficient order. These cases exhaust the macro cuts.

For the uniform bound put `A=|a|, B=|b|, C=|c|`. The triangle inequality gives

```text
|b|+|a-b²|+max(|c|,|c-ab|)
    <= B+A+B²+C+AB
     = t+B(A+B)
    <= t+t².
```

Thus `M<=1+t+t²<=1+eta+eta²`. If `eta>0`, equality forces `t=eta` and
`B(A+B)=t²`. Since both `B` and `A+B` are at most `t`, this forces
`B=t`, hence `A=C=0`. Conversely, for every complex `b` of modulus `eta`,
the formula gives `M(0,b,0)=1+eta+eta²`. If `eta=0`, all coefficients vanish
and the same classification holds. This proves the sharp envelope and all
its extremizers. The comparison with #4731 follows by subtracting the
geometric-series envelope. No predecessor scientific executable is replayed.

## Exact finite corroboration

The standard-library verifier constructs the literal root and child macros
by truncated Gaussian-rational polynomial division. It executes both child
orders, multiplies the prefix and suffix matrices at every cut, and compares
the maximum with the separate closed formula. It also checks the bound and
the extremizer criterion for every fixture. Matrix entries are exact pairs
of rational real and imaginary parts.

Norms are exact sums of square roots of rationals, reduced to rational
multiples of squarefree radicals. Equality compares these canonical sums;
ordering uses outward rational intervals built with integer square roots.
Unresolved ordering raises an error after 256 fractional bits. No binary
floating-point comparison or tolerance decides acceptance.

The complete fixture grid uses zero and the five phases
`1,-1,i,-i,(3+4i)/5` at amplitudes `1/4,1/2`, independently for `a,b,c`.
Thus it includes non-real inputs whose derived coefficients have irrational
moduli. All 1,331 grid fixtures and 13,310 order-labelled cuts pass; exactly
11 fixtures attain their own tail envelope, and 605 give a larger maximum
under even-first execution than under odd-first execution. These cut counts
retain duplicated matrices at different chronological cuts. Ten controls
pass, including the two invalid-coefficient cases. Controls reject omitted
Schur and root-left macros, wrong chronology, endpoint-only bounds, applying
the binomial value to all symbols, omitting the necessary child order, and
invalid coefficients. Separate arithmetic controls exercise irrational
comparison and exact Pythagorean modulus equality.

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -X dev -B research/four-wire-parity-suffix/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -X dev -B research/four-wire-parity-suffix/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/four-wire-parity-suffix
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/four-wire-parity-suffix --check-source-history
```

Another CPython 3.12 executable may replace the local interpreter path.
The expected marker is `PASS_FOUR_WIRE_PARITY_SUFFIX`. The script writes
nothing and emits a generated receipt binding the five package-file hashes.
The registered replay runs normal and optimized warning-strict checks.
Universal complex claims rely on the written proof, rather than finite
extrapolation. Independent human and formal proof-kernel review are unclaimed.

## Limits and code constraints

The result concerns exactly four wires and complete-shear boundaries. It
does not bound cuts inside a dirty-shear implementation, arbitrary larger
symbols, rounded arithmetic, complete Gaussian stages, tape costs or the
selected supplier. All five framework assumptions remain at their existing
strength. No selected cold replay, Lean or Docker was run.

The verifier has no recursion, dynamic imports, subprocesses or network
access. Every function is under 60 lines. The fixed grid has 1,331 fixtures,
two four-macro words per fixture and five cuts per word. Matrices are always
four by four. Radical factorization accepts integers at most `2^40`, uses at
most `2^20` trial divisors and at most 41 divisions per divisor. Exact norm
ordering makes at most five interval refinements. Python's managed allocation
and arbitrary-precision temporaries are a documented Power of Ten deviation;
this is a bounded finite checker, with no public unbounded input interface.
Internal helpers consume only the fixed grid and fixed four-wire structures.
Warning-strict and optimized runs are the available interpreter diagnostics.

## Open next questions

1. Determine the sharp forward-suffix envelope for general eight-wire symbols.
   This would give the next precision-interface bound beyond this theorem.
   Start with the child-cut row formulas and preserve correlations between
   the even child and its inverse. A finite candidate grid would not prove
   the complex optimum, and binomial optimality at larger sizes is unclaimed.
2. Bind one actual four-wire shear implementation to this macro envelope.
   Start with its complete literal gate sequence and rounding convention.
   Internal gates, coefficient delivery and the complete physical bill
   remain additional obligations.

## Sources and credit

This contribution was produced by Nick Petalas. Apache-2.0.

The source question is #4831's explicit four-wire optimization. That package's
binomial values, all-depth recurrence and attaining family remain credited
predecessor results. Brian / JoyboyBrian #4731 supplies the common macro-cut
contract and four-operator envelope. Vlado Vojdanovski #1673 supplies the
parity compiler, retained by Cinna Davis #4100. James Reed #4699 supplies
one-level tail accounting; Ryanson Jonathan and unpaidmoon #4371 supply
the earlier conditioning question. The new contribution is the full complex
four-wire formula, its sharp uniform upper bound and its extremizers.

Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8, selected #7000 unchanged. The catalogue's older selected context
was recognized; current selected source bindings passed. [TASK.json](TASK.json)
records the changed scope from audit to an original precision-interface lemma.
[SOURCES.json](SOURCES.json) pins historical provenance only. Direct replay
requires this package alone; no predecessor numerical claim is rechecked.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19595240)
states this same scope. Live PR, main-branch README, merged-work and local
reservation checks found no resolving general four-wire suffix formula.
This textual overlap search does not cover unpublished work or every diff.
