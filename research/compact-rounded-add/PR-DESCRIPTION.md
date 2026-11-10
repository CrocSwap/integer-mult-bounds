## Summary

The literal rounded scalar predecessor leaves the current large-numerator
ADD class unbuilt because its direct carry graph grows with numerical
coefficient size. This package supplies a compact two-bank fixed-rational
ADD table, an all-size signed/cancellation/lifecycle proof, and three exact
current source witnesses. **No new kappa and no complete caller admission.**

For fixed reduced q=a/b, b=2^d o, L=max(bitlength|a|,bitlength b), K=L+2,
the table forms the signed widened numerator b*x+a*y+floor(b/2) by L
binary Horner passes. Each pass has carry bounded by 4. A signed residue
scan, exact odd quotient and low-bit discard implement total nearest-up
rounding. The graph has O(LK+o²+Ko) states/rows, with the explicit current
restriction o<=125. This is not a logarithmic-size arbitrary-divisor claim.

The complete sum is checked after division, preserving cancellation even
when the separate product exceeds the public width. Per-component numerator
markers provide rewind geometry, so the service needs exactly the existing
two private work roles. All components are staged before public installation.

## Exact result and source pins

Canonical parent: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

The source is DreamingOfClouds' CrocSwap/integer-mult-bounds#6936 at tested
head `03626137d0bd57f09b0bf9597376183ce6fa9683`. Its later
`d360b1182b6d21b1ee2354856abcb50646ad618b` changes only VERIFY.json timeout;
the tested word pin remains unchanged. Six immutable dependencies have
exact commit/path/Git-blob/SHA-256 receipts in `DEPENDENCIES.json`.

The current coefficient census contains 61,052 ADD and one COPY event,
4,462 reduced coefficients, L<=24 and o<=125. Only three exact local ADD
tokens are constructed and registered:

| Event | Coefficient | Rows | Actual cancellation check |
|---|---|---:|---|
| 252 | -14729531/163840 | 100,033 | W8: 100 + Round(q·2) = -80 |
| 1103 | -1379/250 | 187,806 | W4: 7 + Round(q·2) = -4 |
| 2798 | 1085645/393216 | 76,560 | W4: -7 + Round(q·3) = 1 |

These represent the largest coefficient, odd denominator and denominator
two-adic power. The old direct carry bound at 252 would be 14,975,296;
that large graph is not instantiated. COPY's caller zero-target contract
is not inferred from generic ADD and no COPY token is installed here.

## Complete primitive bill and limits

For R components, S=sum(w_i+1), U=1+S+(K+1)R, initial contiguous dirty
lengths A_N,A_O and borrowed context charge Q_c, the proof gives

    512(L+8)U + 7(A_N+A_O) + 16Q_c

for physical tape actions plus executed control rows. Every source reread,
reversal, widening, staging, copying, head reset and retirement is retained.
Historical private backing is max(H_N,3U)+max(H_O,3S), plus inherited
public/context/ancestor and finite-controller storage. Positive finite
coefficient/table/source setup is separate. No exchange rate to an old
supplier tariff or optimistic rounded-scan margin is asserted.

Canonical encoding, matched common-grid shapes, physically distinct tapes,
public origin heads and contiguous old private bodies are explicit premises.
Successful calls preserve source/contexts, restore heads and retire private
history. Detected failure before installation protects the whole public
field but may leave work and heads dirty. This is an actual unchanged
`Controller.primitive`/`execute_table` service, not host arithmetic on
runtime payloads, but it does not execute the complete recursive Controller.

## Reproduction and verification

```bash
python3 -I -B research/compact-rounded-add/verify.py --suite all
python3 -I -O -B research/compact-rounded-add/verify.py --suite all
```

Expected: four PASS_COMPACT_ROUNDED_ADD_* lines. Registered attempts have
120-second caps; standard library only and no runtime Git/network/solver.
The independent direct-floor oracle covers 1,952 exhaustive pairs plus
signed endpoints and W<d. Literal history tests include dirty long-to-short
reuse, late overflow and failure reuse, source/context preservation and
canonical shape errors. Five arithmetic mutants are detected. The proof,
not the finite tested widths, establishes the universal statement.
`VERIFY.json` and the four JSON receipts define exact replay coverage.
A separate lead AI reviewed the proof/cost and independently ran 219 mixed-
width fields (139 successes,80 correct overflow rejections), including all
source maxima, dirty history and displaced context heads. Its unchanged
script and receipt are included with exact reviewed hashes in `REVIEW.md`.

## Novelty, credit and open obligations

Prepared for **@CubeJerry**, with substantial **OpenAI assistance** in proof,
implementation, source analysis and verification. Credit DreamingOfClouds'
CrocSwap/integer-mult-bounds#6936 and CrocSwap/integer-mult-bounds#6937;
CubeJerry's lifecycle/exact-scalar predecessors and rounded-scalar package
at `6476455a1cf7cd29d6a2a81c3b6f02fd3a3bbf57`; the source precision package
at `56bc9383594a3efc303148e00bb746851abd1ed5`; canonical signed-stream
arithmetic; and NickPetalas' CrocSwap/integer-mult-bounds#3094 one-carry
circuit work. Binary Horner arithmetic and division are classical.
`OVERLAP.md` records the bounded predecessor check. `REVIEW.md` distinguishes
independent AI mathematical checks, physical execution and regression replay.

The new result is the compact literal current arithmetic/lifecycle join,
its cancellation-safe signed proof and full positive cost, and actual large
coefficient source witnesses. Full catalogue construction/recursive bindings,
native operators, formats/error/owned history, complete physical supplier
invoice and outer recovery remain open. The five inherited assumptions are
not globally discharged. No selected certificate or accepted exponent changes.
