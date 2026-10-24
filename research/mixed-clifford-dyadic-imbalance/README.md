# Exact directional imbalance for mixed Clifford lanes

This contribution is produced by Nick Petalas. Apache-2.0.

Scoped algebraic proof with finite corroboration. For literal tensor widths
f=2 modulo 4, an unbalanced collection of forward and inverse Clifford lanes
can sometimes be one wider child under an arbitrary reciprocal linear
encoding. The first new identity uses three forward width-two lanes and one
inverse lane on 16 coordinates:

```
C_2 direct-sum C_2 direct-sum C_2 direct-sum C_2^-1 = E^-1 (-i C_4) E.
```

Four lanes are necessary and sufficient for a proper width upgrade in this
model. This differs from Arham Tahir's PR1920 balanced-pair result, which
excludes an opposite width-two pair. The spectral and Walsh methods are
inherited; the arbitrary directional multiplicities and exact integer
classification are the new contribution. No literature priority is claimed
for elementary spectral similarity or prime valuations.

## Exact classification

Let a,b be the forward/inverse counts, q=a+b>0, and delta=a-b. With the
convention C=((1+i)I+(1-i)X)/2 and C_f=C tensor ... tensor C, a single
forward child lambda (C_h tensor I_t) is similar to the independent lanes
exactly when, for an integer j>=0,

```
q = 2^j |delta|,    4^j divides q,
h = f+2j,          t = q/4^j,
lambda = sign(delta) i^(-j).
```

In particular a=b never works at these widths. The smallest batch for an
increase 2j is q=4^j. All payload coordinates are independent arbitrary
inputs. Arbitrary restored dirty complements can be mixed by the encoder;
they cannot increase the active child volume. [PROOF.md](PROOF.md) gives
necessity, sufficiency, explicit rational dyadic encoding/decoding, the exact
complement statement and the inherited volume-cost limitation.

This is an algebraic interface identity. The joined child loses the inherited
PR679 full-volume upper expression even with free adapters. Physical/native
encoding, frame conversion, reads, storage, routing, precision, restoration
and every complete consumer cost remain unpaid. Widths in other congruence
classes and a uniform implementation at every column multiplicity are outside
this theorem. No supplier admission, new kappa or multiplication theorem is
claimed. Independent human and formal proof-kernel review are unclaimed.

## Reproduce

From the repository root, using the standard library and CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/mixed-clifford-dyadic-imbalance
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/mixed-clifford-dyadic-imbalance/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/mixed-clifford-dyadic-imbalance/verify.py
```

The interpreter path is local; reviewers elsewhere can substitute their
CPython 3.12 executable. The verifier is read-only and also works in a
Git-free package export. Its JSON receipt is generated, includes file SHA256
hashes, and is printed to stdout. No saved receipt is a proof input.

The finite sweep enumerates every a,b with 1<=a+b<=64 at widths
f=2,6,...,30. It checks 17,152 target multiplicity lists against 1,170,400
dimension-compatible phased candidates. There are 1,360 matches, of which
336 are proper width upgrades. The uniform boundary cases are controls,
not predecessor results claimed anew. A separate cyclic recurrence checks
all 37 binomial spectrum lists used in the sweep.

Four dense rational witnesses cover both imbalance signs, a nontrivial
spectator factor, a four-width increase, and arbitrary dirty identity
complements. They check 5,870 entries of H E=E T, plus both inverse products
for every fixture. Exact Gaussian tensor coefficients are constructed
separately from the Walsh eigenbasis. Controls reject a wrong phase,
direction, encoder, dirty output, balanced batch, nondyadic imbalance and
nonintegral spectator count, plus four invalid domains. All checks remain
enabled under optimized Python.

The written proof establishes the quantified result. Finite enumeration
alone is not an unbounded proof. No predecessor verifier, selected cold
replay, native implementation, Lean or Docker build is run for this result.

## Scope and overlap

Base canonical main is `624de9dc66858af0945e5f8a0942488d62280d43`, priority
revision 7. [The advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133741)
states the delivered target. [TASK.json](TASK.json) records the changed scope
from physical synthesis to an exact prerequisite classification and the
bounded stop rule. The current selected source-binding orientation passed.
The card's historical ceiling command failed with `KeyError: complex_profile`
against the changed selected schema; it supplies no evidence here.

Overlap checks read current open PRs, this account's recent work, recent
handoffs, active Discussions, targeted merged PRs and distinctive terms in
all main READMEs. The cached search covers 379 open PRs and 3,853 Discussion
records, but only 101 of 6,319 local-main notes were materialized. This does
not cover unpublished work or every code diff. Exact predecessor READMEs are
historical provenance in [SOURCES.json](SOURCES.json); no predecessor code is
imported or copied. The standalone verifier has no external proof input.

The implementation has no recursion or background work. The entrypoint fixes
every finite enumeration range; dense matrices have at most 67 rows and
columns. Python allocates integers and collections dynamically, a managed
runtime deviation from fixed allocation. Live matrices are bounded by those
fixture caps. Functions stay below 60 physical lines. Warning-strict normal
and optimized execution are the registered diagnostics; no static type or
native-code analysis is claimed.

## Credit

Arham Tahir, PR1920, supplied the reciprocal full-space contract, equal-width
uniform and balanced-pair results, trace invariants and Walsh construction.
Adam Gall, PR1946, classified two unequal-width equal-volume lanes, a
different multiplicity contract. The exact correction-rank work by ywz65
concerns an additional nonreciprocal adapter, which this theorem does not
allow. Greer Guthrie, PR679, and Ross Richardson's diagonal-child contract
audit supplied the inherited volume-aware scope and tariff. ToikY, PR1924,
and Douglas Colkitt, PR665, supplied distinct clean-injection/spectral
interfaces. Jose Manuel/jmbarrancoml with Cinna Davis/1337isnot1337, PR1779,
and Josie Elliston, PR1817, supplied the batching motivation and retiming
context. Credit icekylinx, DreamingOfClouds, Rohan Arun, Jeremy Kothe,
Hao Yan and the retained native-kernel/construction lineage. Their original
credit and source files remain unchanged.

## Open next questions

- Can a real three-forward/one-inverse width-two caller support a different,
  favorable fully paid operation or volume contract? First name its actual
  charts, inputs, outputs and complete adapter ledger. No such physical
  caller or cheaper tariff is supplied here.
- Can a uniform supplier exploit this exception while supporting every
  required literal width? First pin one caller's column parameter, derive
  its admissible congruences, and price a legal fallback. An actual caller
  and all-size cost contract remain missing.

The structured questions in TASK.json give their relevance, first steps and
blockers. Further reciprocal basis searches under the same losing tariff
are not justified by this algebraic identity.
