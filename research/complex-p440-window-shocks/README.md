# Pivot 440 needs four short restored donor windows

**Scoped exact obstruction with an algebraic attaining control; no new κ.**
On the pinned PR1297 base word, delete pivot 440's three early B reads. No
combination of at most three restored donor windows repairs the scalar map,
even with arbitrary rational coefficients. Four windows suffice. Each window
may use any nonpivot source register, including helper readers, and span at
most four consecutive reads inside a segment with no write to that donor.
This is an exact minimum in this window class, not an optimum over circuits.

This answers one bounded part of Marius-Paul Dumitrean's
[PR1337 handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/1337).
That work exhausted an output-reader two-shock family and explicitly left
helper-reader windows and three-shock relations open. The present result does
not exclude the handoff's unrestricted window class, longer windows, other
pivots, partial deletion of the old reads, suffix-restored helper cuts, or
cleanup edits.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/complex-p440-window-shocks
```

Expected final line:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/complex-p440-window-shocks outcome=negative-result
```

The three commands registered in `VERIFY.json` run the primary census, a
separate checker, and seven test groups. Direct `verify.py`, `independent.py`
and `test_package.py` runs also work outside the checkout with isolated and
optimized Python. They do not use a solver, network access or predecessor code.
Ordinary verification compares saved receipts and does not regenerate them.

## Exact domain and result

The input is PR1297's `gauge44-word.json.gz`, taken unchanged from PR1337's
`inputs/BASE-WORD.json.gz`. All indices below are zero-based original B indices.
There are 1,844 B gates and 119 early-cleanup gates. Pivot 440 is never written
in B. Remove exactly these three reads:

| Index | Removed ADD |
|---|---|
| 892 | `588 += 440` |
| 928 | `158 += 440` |
| 1192 | `218 += 440` |

In the reduced B word, choose a donor `x != 440` and one to four consecutive
reads of `x` with no intervening write to `x`. Open immediately before the
first read with `x += c*440`; close immediately after the last with
`x -= c*440`. Both operations occur in B, before early cleanup. Unrelated gates
may lie between those reads. Windows may overlap, reuse a donor, or have
dependent effects; the proof does not assume disjointness. Canonical cuts
represent all placements in the adjacent read/write-free gaps with the same
scalar effect. The existing A, cut and cleanup words are unchanged.

The complete enumeration has **2,758 windows**, including one zero response.
The **2,757 nonzero responses have 1,611 distinct rational projective
directions**. The original six-coefficient pilot used
`{-2,-1,-1/2,1/2,1,2}` and found no repair. The delivered proof removes that
coefficient restriction entirely. Since all linear systems have rational
entries, consistency over the complex numbers is equivalent to consistency
over the rationals; complex coefficients cannot evade this obstruction.

`CERTIFICATE.json` records the domain, all-response digest, direction digest,
exact deletion error, four anchor cases and rejection counts. There is no
random sampling in either delivered verifier. Seed 34 chose the track and
pivot; the deterministic stopping rule is completion of this fixed domain.

## Why the exclusion is exhaustive

Write `e_r` for the final-coordinate unit vector at register `r`. Removing the
three reads changes only the column of the unchanged B-entry value of pivot
440. The error to be restored at the end of B plus early cleanup is

```text
d = e153 - e154 + e157 - e158 + e217 - e218 + e221 - e222 + e588.
```

For a donor window, the opening and closing shears have opposite coefficients.
Because neither the pivot nor the donor is written inside its window, the
window's response is the sum of the included read responses. All injected
changes are multiples of the same unchanged pivot value, so simultaneous
windows add their responses, including when they overlap. The primary
implementation obtains each response from exact suffix columns. The separate
implementation instead executes a unit opening pulse and a negative closing
pulse forward through the whole reduced segment.

Only four projective directions have a nonzero register-588 entry. Every repair
must include at least one. Classify any set of at most three directions by
whether it contains one, two or three of these four directions:

1. With one, the register-588 equation fixes its coefficient. Subtract it and
   test whether the residual lies in the span of any two of the other 1,607
   directions. Repeated directions and zero coefficients include repairs using
   fewer than three windows.
2. With two, test each of the six pairs together with every other direction.
   Zero coefficients also include a repair using just the two anchor directions.
3. With three, test all four triples. Repeated anchor directions reduce to an
   already covered smaller set.

A missing support coordinate rejects a proposed span immediately. The
remaining systems are inconsistent by exact elimination. The primary checker
uses a further rare-coordinate reduction and rational RREF. The independent
checker enumerates every unordered pair with repetition in case 1 and uses
fraction-free integer rank comparisons. It classifies **5,177,758 cases**:
**5,177,648 support rejections and 110 integer-rank rejections**. All cases are
covered; none is a timeout or a failed heuristic search.

This is a finite exact linear-algebra certificate for the declared word and
window family. It is not a proof-assistant formalization or a proof of the full
multiplication theorem.

## Four-window control and complete local operation count

The following four single-read windows attain the scalar lower bound:

| Donor | B read index | Opening coefficient | Closing coefficient |
|---|---:|---:|---:|
| 518 | 41 | -1 | +1 |
| 641 | 160 | +4 | -4 |
| 42 | 493 | +1 | -1 |
| 106 | 527 | +1 | -1 |

After removing the three old reads, these windows add **eight ADD macros**,
including every donor opening and restoration. The B word therefore grows by
five ADD macros, from **1,844 to 1,849 gates**. The unchanged source reads
inside the windows and the complete early cleanup are retained. These are
macro counts, not lowered scalar-primitive costs or recursive rank charges.

The independent interpreter verifies equality of the complete B-plus-early-
cleanup linear maps on **all 704 arbitrary input columns**, including dirty
helpers and donor inputs. Omitting a donor close, changing a coefficient, or
omitting the fourth window changes the map. The tests also negate each of the
four opening coefficients, reject a changed source file and forged certificate,
exercise non-dyadic and singular linear systems, reject a pivot write, and
check window boundaries at donor writes.

The four-window identity is a positive algebraic control, **not a proposed
improving supplier**. No physical frame assignment, native phase replay, owner
admission, precision analysis, lowered-primitive invoice or paid recursive
moment is supplied for it. For at most three windows, even a favorable budget
with free added operations and unconstrained frames cannot help: the necessary
scalar identity already fails. No baseline cost is silently credited as a
realized saving.

## Sources, selection and limits

- Research base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- PR1337: `abd7384d9a5e35048723512ae70d970909ffd522`, Marius-Paul Dumitrean.
- PR1297: `4abf710a7f0d2a46f522f3f13c15769d003f9495`, Rohan Arun.
- Exact input Git blob: `eacf8c773cb50637f93a762342b3b5f0853fe29a`.
- Exact input SHA-256:
  `e8e6e78ff7422275c38324499e1f33fb2ecd30de9503aef2b8f1ee80d8c4df8e`.
- Selected conditional κ at the research base remains
  `836330098538459/500000000000000000 = 0.001672660197076918`.

Both source commits were fetched and the original and transported word blobs
compared. `SOURCES.json` records the source chain; predecessor notices and the
Apache-2.0 license are retained. Only this new package is changed. The studied
word belongs to a pending construction lineage, not the selected frontier.
No claim from PR1305/PR1324's separate idle-axis overlays is used.

OS seed **34** selected complex supplier and index `34 % 4 = 2` of
`[438,439,440,444]`. `TASK.json` records the three candidate tasks, overlap
decision, initial bounded search and strengthened scope. The
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1314#discussioncomment-18912079)
joins the predecessor's existing handoff discussion. No pinned sprint issue
existed at entry.

The selected construction's all-size/compiler, common-label/mutable-source,
hosting, precision/tape, analytic-transfer and bit H1–H5 assumptions remain
untouched. This local obstruction does not verify or depend on resolving them.
No full selected cold replay, repository-wide suite, hosted CI success, or
independent human review is claimed.

## Open next questions

- Can a four-or-more-window repair improve a fully realized frame and paid
  profile? The concrete control is a first scalar fixture, but frame
  feasibility, all source-access costs and recursive charges are unresolved.
- Can a longer window or a different high-screen pivot admit a three-window
  repair? Declare and coordinate that new finite domain first; this certificate
  does not cover it.

The structured questions and their blockers are in `TASK.json`.

## Credit

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in mathematics, implementation, verification and writing. Credit Marius-Paul
Dumitrean for PR1337's census and explicit window-donor handoff, Rohan Arun for
PR1297's words and relation lineage, and Jeremy Kothe for the PR1274 helper-donor
mechanism. The retained ancestry includes Jeremy Diviney, Thomas DiFiore,
chafreaky, the PR1195/1218 work and the PR564/571/589/645 construction lineage.
See `NOTICE.md` and the unchanged predecessor notices. Apache-2.0 applies.
