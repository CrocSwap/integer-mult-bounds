# Compact literal rounded ADD for current large coefficients

**Result:** a two-private-bank flat table computes total nearest-up rounded
ADD with a controller graph of size `O(LK+o^2+Ko)`, where `L` is coefficient
bit length, `K=L+2`, and `o<=125` is the fixed odd denominator part. It forms
the complete widened numerator before dividing, so valid cancellation is
preserved. The table runs through the unchanged lifecycle executor and
retains all copying, reversals, old backing and retirement costs.
**No new kappa or complete caller admission.**

The current #6936 source has 61,052 ADD events and one COPY, 4,462 reduced
coefficients, `L<=24`, and `o<=125`. We construct and register three exact
local source witnesses, representing the largest numerical coefficient,
largest odd divisor, and largest denominator power of two. We do not
instantiate or install the complete catalogue or infer COPY's caller
zero-target contract from ADD arithmetic.

| Source event | Coefficient | Flat rows | Cancellation witness |
|---|---|---:|---|
| 252 | -14729531/163840 | 100,033 | W8: 100 + Round(q·2) = -80 |
| 1103 | -1379/250 | 187,806 | W4: 7 + Round(q·2) = -4 |
| 2798 | 1085645/393216 | 76,560 | W4: -7 + Round(q·3) = 1 |

In each example the separate rounded product would overflow the public
width. The old direct-carry bound at event252 is 14,975,296; that graph
is never constructed. The new Horner carry is bounded by 4 independently
of coefficient magnitude. The explicit `o^2` term is retained: this is not
a logarithmic-size arbitrary-divisor result.

## Scope and physical contract

`compile_compact(q)` emits immutable branch/write/unit-move/goto/halt/reject
rows for `(target, source, numerator_work, output_work)`. Fixed coefficient
bits determine successive `N <- 2N + beta*x + alpha*y` passes at width
`W+K`, followed by the rounding offset, a signed residue scan, exact odd
quotient and low-bit discard. Per-component numerator markers also guide
rewinds, so only two owned work banks are used.

For all positive widths and all complete fields with matching component
shapes on a common grid, success is exactly final signed representability.
Every component is staged before any target write. The source and contexts
are preserved and successful heads returned; both private historical bodies
are retired. Detected failure before installation protects the public
field but may leave heads and private work dirty. Canonical actual physical
frontiers, distinct tapes, origin markers, and contiguous old scratch are
explicit premises.

Put `S=sum(w_i+1)`, `U=1+S+(K+1)R`, with `R` components. Including finite
control and physical tape actions, the positive per-invocation bound is

    512(L+8)U + 7(A_N+A_O) + 16Q_c.

`A_N,A_O` are old contiguous dirty physical lengths. Historical capacities,
source/table setup and all ancestor/public backing remain charged separately.
This bound is not converted into the previous supplier tariff or optimistic
rounded-scan margin.

## Reproduction

```bash
python3 -I -B research/compact-rounded-add/verify.py --suite all
python3 -I -O -B research/compact-rounded-add/verify.py --suite all
```

Expected: four `PASS_COMPACT_ROUNDED_ADD_*` lines, for SOURCE, ARITHMETIC,
HISTORY and CONTROLS. Every registered attempt has a 120-second limit;
standard library only, with no Git, network or solver needed for replay.

The independent direct-floor oracle checks 1,952 exhaustive pairs plus
endpoints, including W<d. Literal tests also cover late overflow, long-to-short
dirty-bank history and reuse after rejection, source/context preservation,
and signed equal values on physically distinct tapes. Five arithmetic
mutants are detected. The universal result is proved in `PROOF.md`, not
inferred from these finite widths. A separate lead AI additionally checked 219 heterogeneous-width fields with
an independently encoded/decoded oracle and combined tape/control costs;
139 succeeded and 80 correctly rejected overflow. Exact author receipts are `SOURCE.json`,
`ARITHMETIC.json`, `HISTORY.json`, and `CONTROLS.json`.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The tested
source is [CrocSwap/integer-mult-bounds#6936](https://github.com/CrocSwap/integer-mult-bounds/pull/6936)
at `03626137d0bd57f09b0bf9597376183ce6fa9683`. The later `d360b118...`
source head changes only its verification timeout; the tested word pin is
retained. Six unchanged dependencies have exact commit/path/blob/SHA-256
receipts in `DEPENDENCIES.json`.

## Open next questions

1. Build and source-bind the full 4,462-coefficient catalogue with shared
   tables, exact recursive field remapping and a positive setup/storage bill.
2. Assemble this multiple-pass service into the complete physical supplier
   invoice. The previous optimistic scan tariff has not been transferred.
3. Join actual native operators, full formats, rounded error propagation,
   recursive owned history and the outer recovery proof. The five framework
   assumptions remain globally open.

## Credit

Prepared for **@CubeJerry**, with substantial **OpenAI assistance** in
proof, implementation, source analysis and testing. Credit DreamingOfClouds'
#6936 source and [CrocSwap/integer-mult-bounds#6937](https://github.com/CrocSwap/integer-mult-bounds/pull/6937)
rounded-division proposal; CubeJerry's lifecycle, exact-scalar and
[rounded-scalar predecessor](https://github.com/CubeJerry/integer-mult-bounds/tree/6476455a1cf7cd29d6a2a81c3b6f02fd3a3bbf57/research/current-rounded-scalar-tables);
the [source precision package](https://github.com/CubeJerry/integer-mult-bounds/tree/56bc9383594a3efc303148e00bb746851abd1ed5/research/query-only-precision-envelope);
canonical signed-stream arithmetic; and NickPetalas' one-carry circuit
work in [CrocSwap/integer-mult-bounds#3094](https://github.com/CrocSwap/integer-mult-bounds/pull/3094).
Horner multiplication and division are classical. Novelty is the explicit
compact current arithmetic/lifecycle construction and source-bound proof,
not invention of those operations. `OVERLAP.md` and `REVIEW.md` record
bounded overlap review and actual independent-check scope. No selected
certificate is changed.
