# Every full-support signed n=8 symbol has prefix maximum 23/16

**Claim type: complete finite certificate**, with an elementary attaining-row
argument. For every one of the 128 symbols

```text
f = (1, s1/8, s2/16, s3/16, s4/16, s5/16, s6/16, s7/16),
sj in {-1,+1},
```

the largest proper forward-prefix infinity norm of the even-first triangular
parity compiler is exactly **23/16**. Every symbol first attains this value
after macro 11 and retains it through macro 21. All 128 symbols are extremizers.
Their tail l1 is 1/2. The completed Toeplitz matrix has norm 3/2.

This replaces individual sign examples by an exhaustive result for this fixed
magnitude family. Brian's [general forward-prefix theorem](../triangular-parity-forward-bound/README.md)
already gives 3/2 at tail budget 1/2. The new finite envelope is sharper by 1/16.
This certificate does not establish a sharper bound for other magnitudes, interior
points of a coefficient box, arbitrary dimensions, or child interleavings.
No new kappa, supplier admission or complete multiplication theorem is claimed.

## Schedule and exact certificate

Use ordinary power-coordinate indices 0,...,7 throughout. At each node split
`f(z)=e(z^2)+z o(z^2)` and compute truncated series

```text
k = o/e,       s = e-z o k,
U = [I, T(zk); 0, I],       L = [I, 0; T(k), I],
T(f) = L diag(T(e),T(s)) U.
```

The displayed blocks use even/odd order. The verifier embeds them directly
on the corresponding ordinary coordinate indices. Execute `U`, the entire
even child, the entire Schur child, then `L`, repeating this order at each
node. Include one identity factor at each scalar leaf. Thus the schedule has
22 factors and 21 nonempty proper prefixes. The identity initial cut, if
included, has norm one and does not change any maximum.

[verify.py](verify.py) independently implements this definition with exact
`Fraction` arithmetic. It constructs the fixed 15-node tree without recursion,
multiplies every chronological 8-by-8 prefix, and compares the final product
to the literal lower-triangular Toeplitz matrix. It imports no predecessor
verifier and does not run a predecessor's certificate.

The maximum at each cut, taken over the complete 128-symbol domain, is:

| Proper cut | Maximum infinity norm over all signs |
|---|---|
| 1 through 5 | 2601/2048 |
| 6 through 9 | 21/16 |
| 10 | 85/64 |
| 11 through 21 | 23/16 |

These are exact maxima from all 2,688 prefix matrices. They are not interval
upper estimates or floating-point results. Each symbol's own maximum is
23/16, even though its earlier cut norms can differ from this table.

The attaining row has a short explanation. At cut 11 the even child is
complete, so the even output rows are the upper block of
`diag(E,I) U`, namely `[E, zO]`. Its last row, which is ordinary row 6,
contains `f0,...,f6` in permuted order. Its absolute row sum is

```text
1 + 1/8 + 5/16 = 23/16.
```

The Schur-child macros change only odd rows. Row 6 therefore retains that
sum through cut 21. The finite exact enumeration supplies the matching upper
bound at every earlier and later proper cut. It also verifies that no symbol
attains 23/16 before cut 11. The completed last row includes f7, giving 3/2.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/triangular-parity-sign-cube/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/triangular-parity-sign-cube/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/triangular-parity-sign-cube
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/triangular-parity-sign-cube --check-source-history
```

Expected status is `PASS_TRIANGULAR_PARITY_SIGN_CUBE`, with `symbols=128`,
`proper_prefixes=2688`, and `maximum_distribution={"23/16":128}`.
Adding `--details` to either direct invocation emits every sign tuple and
all of its 21 exact cut norms. The generated receipt includes the SHA256
of this entire ordered certificate and of all five package source files.
It writes nothing. No receipt is hand-written or retained as a separate claim.

Eight controls reject the wrong root-left sign, a missing root-left shear,
reversed macro order, an omitted symbol, a duplicated symbol, an omitted cut,
a wrong reported maximum, and inclusion of the completed cut as a proper cut.
Explicit exceptions keep every check active under `-O`.

The verifier uses Python-managed allocation and exact rational objects. This
is a Power of Ten rule-3 deviation: literal allocation-free steady execution
conflicts with `Fraction` and the interpreter. All mathematical work is bounded
by 128 inputs, a 15-node tree, 22 factors and 8-by-8 matrices. The five control
copies are bounded by the same domain. The fixed finite input and no-write
interface constrain live storage; no arbitrary input size is accepted.
Functions stay below 60 lines, loops have explicit finite domains, and there
is no recursion, dynamic evaluation or external command. Warning-strict normal
and optimized replay are registered. No separate static analyzer was available on PATH.

## Scope, sources and credit

This contribution is produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

Credit James Reed for the one-split bound, the nested-prefix question and the
single-symbol series, including
[#4811](https://github.com/CrocSwap/integer-mult-bounds/pull/4811),
[#4812](https://github.com/CrocSwap/integer-mult-bounds/pull/4812),
[#4815](https://github.com/CrocSwap/integer-mult-bounds/pull/4815),
[#4816](https://github.com/CrocSwap/integer-mult-bounds/pull/4816),
[#4820](https://github.com/CrocSwap/integer-mult-bounds/pull/4820),
[#4821](https://github.com/CrocSwap/integer-mult-bounds/pull/4821) and
[#4822](https://github.com/CrocSwap/integer-mult-bounds/pull/4822).
Their individual values remain their results. The original addition here is
the complete sign-family certificate and its sharp cut envelope.

Credit JoyboyBrian for the
[all-depth four-cut envelope](../triangular-parity-uniform-prefix/README.md)
and its [sharp forward-prefix successor](../triangular-parity-forward-bound/README.md),
which already settles the general 1+eta question; Vlado Vojdanovski for
the shallow parity compiler retained by Cinna Davis in
[SHALLOW-TOEPLITZ.md section 3](../unconditional-batched-crt/vendor/SHALLOW-TOEPLITZ.md);
and Ryanson Jonathan for the caller's error-ledger context in
[one-factor-of-t](../one-factor-of-t/README.md). No predecessor credit line is changed.

Canonical base is `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
[SOURCES.json](SOURCES.json) pins exact source bytes; [TASK.json](TASK.json)
records the changed scope and bounded overlap coverage. The card's historical
baseline command has been superseded by `scripts/research_selected_baseline.py`,
which passed as a source-binding positive control. The selected conditional
record remains kappa=60403/20000000. That orientation check is not a theorem replay.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132735)
reserved this finite sign-family question.

## Open next questions

1. Is 23/16 still the exact maximum for this finite family under every legal
   child interleaving? Enumerating pairs of legal child cuts is a feasible first
   step. This certificate fixes even-first execution; the general theorem gives
   only the weaker 3/2 bound for these schedules.
2. Can one derive an analytic coefficient-sensitive envelope that explains
   the 1/16 improvement? Start with the row support omitted by the unfinished
   root left shear. The fixed-magnitude enumeration does not supply that formula.

Full gate-level stability, generator normalization, the completed Gaussian
stage, fixed-tape implementation and the dyadic p^100 precision ledger were
not run or proved. There is no complete recursive invoice to admit here.
