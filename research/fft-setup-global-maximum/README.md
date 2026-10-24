# The sharp FFT setup constant holds at every width

This contribution was produced by Nick Petalas. Apache-2.0.

For every integer `n >= 3`, define

```text
beta = ceil(log2 n),  q = ceil(n/beta),
ell = ceil(log2(2q)), r = 2^ell, p0 = 2 beta + ell,
S = r(ell+1)p0^2 + r p0^3 + p0^3.
```

Then `S <= (1017/7) n beta^2`, with equality if and only if `n=7`.
Moreover, `S < 144 n beta^2` whenever `n >= 513`.

This is a scoped all-width arithmetic proof with a finite exact component.
James Reed's [PR3819](https://github.com/CrocSwap/integer-mult-bounds/pull/3819)
introduced `1017/7` and checked it through `2^22`.
The new contribution is the universal tail argument, which makes that
constant the global optimum and closes the finite-range restriction.
The predecessor executable and its census are not replayed here.

Jose Manuel's [PR3787](https://github.com/CrocSwap/integer-mult-bounds/pull/3787)
defines this geometry and the setup invoice. Reed's
[PR3813](https://github.com/CrocSwap/integer-mult-bounds/pull/3813)
records the separate constants. These three expressions are the quadratic
majorant of the source invoice, after replacing `p0^(8/5)` by `p0^2`.
The bound applies before unspecified implementation constants. It is not
an exact instruction count or a new time theorem.

## Proof

Write `b=beta`. If `n >= 513`, then `b >= 10` and
`2^(b-1) < n <= 2^b`. Since `b >= 4`,

```text
q <= ceil(2^b/b) <= 2^(b-2),
ell <= b-1,  p0 <= 3b-1 < 3b,
ell+1+p0 = 2b+2ell+1 <= 4b-1.
```

The second ceiling inequality holds because `2^(b-2)` is an integer
at least `2^b/b`. Minimality of the power of two `r >= 2q` also gives
`r < 4q < 4n/b+4`. Factoring the sum gives

```text
S = r p0^2 (ell+1+p0) + p0^3
  < (4n/b+4) 9b^2 (4b-1) + 27b^3
  = n b^2 [144 - 36/b + (171b-36)/n].                 (1)
```

For every integer `b >= 10`,

```text
2^(b-1) >= 19b^2/4.                                  (2)
```

At `b=10` this is `512 >= 475`. For the induction step,
`2b^2 >= (b+1)^2` for `b >= 3`, since `b^2-2b-1 > 0` there.
Doubling (2) therefore proves it at `b+1`. Consequently
`n > 19b^2/4` and

```text
(171b-36)/n < 171b/n < 36/b.
```

Equation (1) is strictly below `144 n b^2`. This proves the entire
infinite tail, without extrapolating from sampled widths.

There remain precisely the 510 integers `3 <= n <= 512`.
The standalone [verifier](verify.py) computes their geometry and checks
`7S <= 1017 n b^2` by integer arithmetic. A second construction uses
bounded doubling and quotient/remainder operations, instead of the
primary bit-length and ceiling formulas. It agrees at every prefix
width. The prefix maximum is `1017/7`, attained only at `n=7`, where
`(b,q,ell,r,p0)=(3,3,3,8,9)` and `S=9153`.
Since `144 < 1017/7`, the tail adds no equality cases. This proves
the global maximum and uniqueness.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fft-setup-global-maximum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/fft-setup-global-maximum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fft-setup-global-maximum --check-source-history
```

The registered normal and optimized commands each check the 510-width
prefix, the induction base, 4,087 induction probes and 8,174 tail endpoint
widths through `beta=4096`. These finite tail probes corroborate the
written induction; they do not establish its universal quantifier.
Eight invalid widths, three formula mutations and the smaller constant
145 are rejected. Every run prints a generated receipt bound to SHA256
hashes of all five package files and writes no files.

Replay requires neither Git nor predecessor files. [SOURCES.json](SOURCES.json)
pins their exact historical bytes as provenance. Receipts are generated
on stdout rather than stored as mutable expected results.

The executable enforces a 4,096-bit geometry limit. Every loop has an
explicit finite bound; there is no recursion, dynamic evaluation or
runtime import of predecessor code. Python necessarily allocates integer
objects during the computation. This managed-runtime deviation from
fixed allocation is confined to bounded arithmetic probes and five
receipt files of at most 1 MiB each. Future larger probes must retain
an explicit bit bound. Warning-strict normal and optimized registered
execution supplies runtime diagnostics. Formal proof-kernel checking
and a separate static type checker are unrun.

## Limitations

This result prices only the three stated algebraic setup expressions.
It does not execute the FFT multiplier, bind hidden instruction constants,
admit a physical caller, prove retained numerical/recovery premises,
or change kappa or the selected frontier. The source uses a separate
small-width implementation; equality at seven concerns the declared
setup expression, not a measured production call at that width.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Is 144 the sharp asymptotic upper limit of `S/(n beta^2)`? The tail
   proves only an upper bound. First choose widths just after a
   power-of-two jump in `2 ceil(n/beta)` while keeping `beta` fixed.
   No asymptotic sharpness claim is made here.
2. What explicit constant bounds the unrelaxed invoice with `p0^(8/5)`?
   First enclose that real power at geometry breakpoints and prove an
   analytic tail. Exact instruction constants and physical caller
   admission remain separate obligations.

## Credit and overlap

James Reed retains credit for the finite `1017/7` maximum and separate
setup comparisons. Jose Manuel retains credit for the digit geometry,
FFT word construction and invoice. Their classical FFT/radix and
Karatsuba lineage, PR3709 numerical/recovery implementation, Mason Hale's
PR2313 interval reference, Dugongue's PR2790 scalar interface and retained
Gaussian reports keep their credit. No predecessor credit line is changed.

Live overlap checks covered open PR bodies and Discussions, this account's
recent contributions, main-tree exact-constant/object searches and merged
PR searches. The exact-constant match was the finite PR3819.
No universal successor was found within that coverage. Arbitrary diffs,
unpublished work and a complete literature priority search are not covered.
