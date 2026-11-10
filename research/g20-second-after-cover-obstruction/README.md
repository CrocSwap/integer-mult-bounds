# No second after-cover keeps the one-weight proof and equals C

**Scoped proof. No new κ.** The selected conditional exponent stays
**781451/250000000** (`0.003125804`).

The selected ordinary formula reads one field, `ordinary_BIT.after_cover`.
The thinned controller writes that field once, from `C1=0.00345`, spelled
`69/20000`. The one-weight delayed-cover proof keeps a positive gap:
`before > after`, with before-cover `C0=3459/1000000`. The formula is
strictly increasing, and

    ordinary(C0) = 8613294599/2500000000000

is still strictly below the recorded PR5679 component

    C = 3507410738409/1000000000000000.

Every rational cover strictly below `C0` therefore misses `C`. The unique
cover that hits `C` is `3507256898809/996000000000000`, and that rational is
strictly above `C0`, so the positive-gap comparison does not apply to it.

The second source assignment named here is the retained delayed-cover
bridge, not a second write of `after_cover`. Its writer assigns
`after = Q(11, 4000)` and stores `C1_after_cover`. Those bytes were
authenticated before the arithmetic. The bridge key is not `after_cover`.
Pointing the selected formula at `11/4000` still misses `C`. Emitting it
beside `69/20000` would be a second external weight and would drop the
one-weight sentence.

## Scope

Base commit `17469fff78c22941280f04d39dc5a1faee09c840` on canonical
`CrocSwap/integer-mult-bounds` main. Priority revision 8. The live selected
record, not the older κ quoted in `current-priorities.md`, supplies the
exponent above. Catalogue card `supplier-boundary-audit`. Scope status:
**refined**.

The card asks for one resolved gap on a latest supplier candidate. Merged
PR #6957, `research/g20-source-bound-cover-census`, already showed that the
one emitted after-cover misses `C`. This package takes only open question 1
of that note: a changed contract that emits a second after-cover while
keeping the one-weight delayed-cover proof. The argument is in
[PROOF.md](PROOF.md). The family-status expansion gate was not opened. This
package does not extend a construction.

Overlap recheck on 2026-11-10, after fetching canonical main at the base
commit: 339 open upstream PR bodies and 7,007 discussion records. The
preimage occurs in discussion
[#1166 comment 19492491](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19492491)
and in the #6957 finding
[#1166 comment 19507126](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507126),
and in no open upstream PR body. The phrase "second after-cover" occurs only
in the #6957 package's open question. No match is a novelty certificate.
Question 2 of that package, the caller outside this pricing assembly, is
merged #6958 and is not retaken. The PR5708 preimage remains with
`research/g20-component-stock-gate`.

## Validation

Environment: Python 3.12, standard library only. From the repository root:

```sh
python3 -B research/g20-second-after-cover-obstruction/verify.py
python3 -O -B research/g20-second-after-cover-obstruction/verify.py
python3 -B scripts/research_package.py --package research/g20-second-after-cover-obstruction
```

The verifier prints `PASS_G20_SECOND_AFTER_COVER_OBSTRUCTION`. The launcher
prints `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `negative-result`.
Checks raise `SystemExit`, so `-O` does not disable them.

Source hashes and Git blobs are checked before any scientific `Fraction`
evaluation. The bridge assignment is named and authenticated in that step.
Controls reject an unbound arithmetic call, a second `after_cover` key, a
bridge receipt whose key has been renamed to `after_cover`, a second C1
sentence, and a second controller writer.

Not run: the controller replay, the bridge script, the outer ledger, either
component caller, native maps, a search for an odd prime, the odd-prime
avoidance of denominators and rank witnesses, Lean, Docker, and
`make frontier6030-verify`. The coefficient comparison
`2**26 > 256/(C0-C1)` is evaluated only at the kept gap `9/1000000`. At the
preimage the denominator is negative, so that rule is not a remaining
search. The domain of the gap statement is every rational below `C0`; the
verifier checks the slope and the image of `C0`, and does not enumerate the
ray.

## Credit

The component is Ali Romman's PR #5679, recorded in `research/g20-helper-split`.
The selected pricing and claim are DreamingOfClouds' PR #6030. The one-weight
cover contract is Cinna Davis's `research/query-thinned-controllers`. The
bridge weight is the retained source in `research/kappa-rebuild/bit`. The
single-emission census that left this question open is merged PR #6957.
The outside-pricing caller census is merged PR #6958 and is not retaken.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Open next questions

1. The odd-prime rule also says the prime must avoid the fixed denominators
   and rank witnesses. That avoidance list was not executed. It is not the
   blocker of this negative result: every cover strictly below `C0` already
   misses `C`, and the preimage is not below `C0`. First step, for a later
   single cover that restores a positive gap and is being checked only for
   the fallback surcharge: name one odd prime above `2^26*N^5` and the
   denominator list it avoids. Blocked by the size of the controller's
   compiled `N` and by this package not searching primes.
2. If `before > after` and `256/(C0-C1)` are dropped, the unique preimage
   makes this formula equal `C`. That drops the one-weight delayed-cover
   proof rather than keeping it. First step: write the replacement for those
   two sentences, then say whether `bit_saving` is still `admitted`.
   Blocked here because both sentences are kept. Equality of `ordinary` with
   `C` would still leave this assembly's `bit_saving` equal to `17/5000`.
   This package does not retake the caller census of #6958.
