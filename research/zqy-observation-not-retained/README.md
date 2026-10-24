# The coupled-exit observation b = Z Q Y is not retained, and no paid response is reusable

**Negative result, no new κ, no change to the selected record.**
Zxv's #5415 shows that Dillon's #5402 coupled provider can return its eight
modes for **8 H1 + 456 ADD + 240 monomial maps** per backward FULL if the
current-version observation `b = Z Q Y` is supplied, and that buying the
observation (120 H1 per FULL) fails the moment screen. With `b` supplied the
#5415 screen is positive at saving .004 (rank surplus 1,776). #5415 (open
question 1), #5419 (ranked experiment 1) and #5425 (open question 1) all ask
whether `b` can be taken from observations that already exist. This package
answers that question **negatively** in the formal free-word grammar used by
the #5377 and #5397 row engines, both inside the native call and at the caller.

## Part 1: b = Z Q Y (`verify.py`, standard library; whole script about 90 s)

**Native level.** Exact rows over (input role, warp word), with the convention
of #5377's `native.py`; paid climbs change only the frame. `Q Y_k` is the row of
the input `y_k = L_{112+k}` standing in the full 9-dimensional frame (`Y` ends in an
8-dimensional frame, `X` ends in the full frame with row `x − y`). Any full-frame
version at any time can be kept in owned storage, so the available set is the
span `V` of all full-frame versions of the whole word.

| word | full-frame versions | rank V | dim(V ∩ pure y) | pure y, any warp word | x-free part |
|---|---:|---:|---:|---:|---:|
| #5402 provider, backward | 4,891 | 546 | **0** | **0** | 400 (helpers) |
| #4610, backward | 5,019 | 554 | **0** | **0** | 408 (helpers) |
| #4610, forward | 4,968 | 554 | **0** | **0** | 376 |

In the full frame `y` never appears without `x`; the only `x`-free content is
helper content.

**Caller level.** The #5415 event semantics over the whole selected p16 caller
(162 events, 18 backward FULLs): `Q` and `D_s` commute, `Q_POWER` and
`SIGNED_SWAP` are free, query responses `Q⁻¹X` and helper returns are kept as
versions. No version word begins with a `Z` letter, so `b = Z_s Q Y` is available
iff `Q Y` lies in the span of all versions after free left factors `Q^{±2}`,
`W_t`. Result: **0 of 18** backward FULL returns, and **0 of 18** when the whole
caller history may be used (a delayed exit). Registered replay uses factors of
length ≤ 1 (21 factors); `--left-depth 2` (419 factors, about 2 minutes) gives
the same 0/0 and is recorded in `RESULT.json`.

**Controls.** Every final full-frame endpoint row lies in `V`; one injected
pure-y version is detected (intersection 1); at every caller return the current
`Y` is found, and at the end `Q² Y` is found. So both tests can answer yes.

**Arithmetic.** All coefficients are dyadic; spans are computed modulo the prime
2^61 − 1. An identity over the rationals reduces to one modulo p, so
non-membership modulo p implies non-membership over the rationals.

## Part 2: no paid response can be reused

#5423 names the next economic object as a global occurrence ledger, in which each
response reuse must have the same chronological input, chart and lifetime.
Part 2 asks the plain version of that question on the same frozen words: can
any paid job be replaced by a combination of responses that already exist?

**Native level.** For every paid climb or centre (frame A → B, row r), the script
tests two windows. EARLY asks whether r lies in the span of every version that
stood in frame B before the climb; owned copies keep all of them. LATE asks
whether r lies in the span of the other frame-B versions that exist before the
next event touching the field, which may be filled late. In LATE the own result
is stored as r + e_tag, so e_tag is in the span iff r is a combination of the
others. If EARLY held, the climb could be replaced by COPY/sub/CLEAR, a
zero-retag and same-frame ADDs, with no Gaussian call.

| word | paid events | EARLY reuse | LATE reuse |
|---|---:|---:|---:|
| #5402 provider, backward | 3,282 | **0** | **0** |
| #4610, backward | 3,298 | **0** | **0** |
| #4610, forward | 3,298 | **0** | **0** |

**Caller level.** The script tests 63 paid caller outputs: 15 thin QUERY
responses, 30 IDLE bank outputs and 18 LOCAL Y outputs. Each is tested against
the span of all earlier versions after free left factors `Q^{±2}`, `W_t` and
`Z_t`. Result: **0 reusable**.

**Controls.** A copy of the first rank-one result injected just before its
climb is found as EARLY. Injected just after it, the same copy is found as LATE
only, and it is the only hit. A thin query repeated on its unchanged bank is
found at the caller level.

This is wider than the single proportional-snapshot traversal of #5397. That
traversal found only the eight known relation sites, which the #5402 provider
word already uses. A κ step from response reuse therefore needs a changed word,
or new relations among inputs of the #5383 type.

## Reproduce

```sh
python3 -I -W error -B research/zqy-observation-not-retained/verify.py
python3 -B scripts/research_package.py --package research/zqy-observation-not-retained
# optional, about 2 minutes: caller test with free factors of length <= 2
python3 -I -B research/zqy-observation-not-retained/verify.py --left-depth 2
```

Expected marker: `PASS_ZQY_OBSERVATION_NOT_RETAINED`.

## Scope

The claim is about the frozen words in the formal free-word grammar (same
scope as #5377/#5397): rows over input roles and native warp words, with only
the Q–D commutation of #5415 at the caller. Not covered: physical identities
beyond that grammar (relations between native warps and Gaussian children, or
between Q and the K_p/K_m monomials), changed native words, other providers, and
the precision, tape and storage obligations that any exit would also carry.
In part 2 the LATE window does not use another climb's raw result as a source; the symmetric case is covered by the EARLY test of the later climb. The result shows that the supplied-observation branch of #5415 section 4 has no
free producer here; it does not bound the price of a new paid producer.

## Open next questions

See `TASK.json`: a numerical full-phase repeat at fiber width one (the only
escape inside the frozen words), and the price of a changed native word that
keeps a pure copy of `R y` before mixing it with `D x`.

## Credit

Dillon (dillona, #5402) supplies the coupled provider word; Cao Yifan (intqwq,
#4610) the native word and frames; zxv (#5415) the exit contract, the caller
semantics and the selected successor controller; Ali Romman (#5377) the row
convention; Clear1nsight (#5425) and zxv (#5419) the open questions.
Mark (Matarener) with substantial Claude Code (Claude) assistance. Apache-2.0;
author-checked, not independent acceptance.
