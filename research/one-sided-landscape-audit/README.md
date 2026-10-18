# Exact controls for the one-sided residue dominance bridge

**Exact baseline controls and a conditional dominance application; no new kappa.**

At [PR2985](https://github.com/CrocSwap/integer-mult-bounds/pull/2985), pinned
head `01174261e56b3c88f2f66b45051fa25c02fdcf1e`, four eligible profiles are
absent from the inherited 603-row input, yet pass the published baseline
DP/LP/Basis/Pencil/triple pipeline. Their full quotient LPs have exact optimum
112. The named newer cap-only RRC and small-piece plane tests cannot exclude
these profiles either. This exposed a missing provenance bridge in that package.
The author then [identified its additional dominance filter](https://github.com/CrocSwap/integer-mult-bounds/pull/2985#issuecomment-6220157570):
a published-as-claimed `(7,5)` cover has span at most four. With anchors `(5,7)`,
support cap 48 is below 53 and `4<d`, so that premise **conditionally removes all
four cases**. The application is checked here; the span premise is not replayed.
The author plans to attach the full generator, dominance filter and run records.

This finding concerns **input coverage**, not the validity of the proposal's
480 individual exclusions. Aggregate LP feasibility does not supply an actual
root configuration, minimum-weight basis, decoder, window or supplier. The
source explicitly says that completeness of the input list is inherited and
not re-derived. The author's clarification resolves which missing premise
handles these four cases. This is a reusable regression artifact for that
two-stage bridge, not a counterexample to the final 603-row classification.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/pull/2985#issuecomment-6219978398)
and [provenance question](https://github.com/CrocSwap/integer-mult-bounds/pull/2985#issuecomment-6220049485)
record that exchange. The earlier question used a different omitted
profile, `[4,5,6^6]` at d=5; that example is covered by the proposal's new
plane lemma. The final four-profile family below avoids that detour.

## Exact result

For `d=5,6,7,8`, take `a=d+2`, `e=a-d=2` and weights `[5,7^(d+1)]`.
Their cost is `7d+12`, so slack is `12-d`.

| d | weights | slack | required LP coverage | exact LP optimum | in source list |
|---|---|---|---|---|---|
| 5 | [5,7^6] | 7 | 106 | 112 | no |
| 6 | [5,7^7] | 6 | 109 | 112 | no |
| 7 | [5,7^8] | 5 | 111 | 112 | no |
| 8 | [5,7^9] | 4 | 112 | 112 | no |

The independent checker tests every deletion set in C1, plus C2/C3. It does not
use the source's heaviest-tail shortcut. For the quotient LP it expands every
nonempty subset of the actual pieces, with nonnegative variables `m_S`:

```
sum_{S subset U} m_S <= N_(|U|+8-d), capped at 112 when |U|+8-d >= 8;
sum_{S containing j} m_S <= g(w_j);
sum_S m_S >= 112 - N_(8-d).
```

Here `N=(0,1,3,6,12,20,36,63,120)` and `g(1..7)=(1,2,4,8,12,20,36)`
are the source's constants, treated as inherited geometric premises. The four
explicit rational primal witnesses in [WITNESSES.json](WITNESSES.json) attain
112 and satisfy all **1,916** subset constraints and all 34 piece capacities.
The full-set constraint supplies the matching upper bound 112, so this is an
exact optimum, without a solver or floating-point acceptance. Symmetrizing
these feasible points over equal-weight pieces proves feasibility for the
source's symmetric LP as well.

Basis-kill cannot apply: every two-piece anchor set contains a weight-seven
piece, which fits neither six-bin, and no piece has weight one. Pencil has one
anchor of weight at least five, giving cap at least 12 rather than at most four.
The e=2 triple rule has only one piece of weight at most six. The published
7+4, 6+6+3 and 6+6+two-lines anchor extensions also fail to pack either possible
anchor type, `(5,7)` or `(7,7)`.

For the newer tests, a nonempty Lemma-P anchor set has cap at least 12, above
its cap-nine domain. With empty anchors there is just one small piece; L1
requires four, and L2/P-prime require e'=3. Every root-forcing RRC test deletes
exactly d-1 pieces, leaving three. Their smallest possible cap is
`g(5)+2g(7)=84>77`; no first root direction can be certified by that test.
The immediate cap-56 rule also fails. This checks those tests' applicability;
it does not claim that every possible geometric argument fails.

The newly clarified `(7,5)` span premise does apply: choose the actual weight-five
piece and any weight-seven piece as the e=2 quotient anchors. Their support
union is bounded by `12+36=48<53`, so the Basis Lemma makes them independent
and demands d independent qualifying directions. If the qualifying span has
dimension at most four, this is impossible for all four d values. This uses
the author's stated geometric premise, which was missing from the original
package's input-generation account. Its run coverage and independent validation
remain separate obligations. The exact reply is retained in
[inputs/pr2985-provenance-response.md](inputs/pr2985-provenance-response.md).

## Scope and evidence

The original complex-rank-shape card is explicitly changed to this missing
input-coverage implication; see [TASK.json](TASK.json). The source proposal,
retained baseline programs and mathematical explanations are pinned in
[SOURCES.json](SOURCES.json). The CSV and proposal README in `inputs/` are
byte-exact public snapshots, authenticated by SHA256 and Git blob IDs. Existing
sources, selected result and frozen evidence are unchanged.

`verify.py` is independently implemented from the stated predicates and full
unsymmetrized LP. `direct.py` checks the same LP fixtures by explicit sets,
avoiding the primary subset zeta transform; it also reverses every role. These
are two arithmetic methods by the same AI-assisted author, not an independent
human or formal proof. Positive exclusion fixtures and malformed masks,
duplicate/negative terms, subset/piece overflows, missing objective mass and
row-presence controls reject. Receipt: [RESULT.json](RESULT.json).

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3.12 scripts/research_package.py --package research/one-sided-landscape-audit
```

Direct replay also works on Python 3.14:

```
python3 -I -O -B research/one-sided-landscape-audit/verify.py
python3 -I -O -B research/one-sided-landscape-audit/direct.py
```

Expected markers: `PASS_ONE_SIDED_INPUT_BOUNDARY` and `PASS_DIRECT_INPUT_LP`.
Runtime is a few seconds. SciPy/HiGHS nominated the primal fixtures during the
investigation; acceptance is entirely rational and does not rerun that solver.
No full landscape census or geometric root/flat enumeration is certified here.

## Open next questions

Replay the promised full generator and dominance receipts, using these four
cases as controls that must survive the baseline and disappear only after a
justified additional reduction. Independently check the exact `(7,5)` span-run
coverage and its geometric premises before counting it as audited evidence.
The structured next question and remaining obligations are in TASK.json.

## Credit

DreamingOfClouds and Claude Code supplied PR2816/2826/2862/2985, the original
necessary conditions, exact repaired-dual LP, input list, and geometric
reductions. Their mathematics and attribution are retained. New contribution:
Arham Tahir, with substantial OpenAI Codex assistance, input-coverage audit and
exact primal fixtures. Apache-2.0; see [NOTICE.md](NOTICE.md). No independent
human review, supplier admission or hosted-CI success is claimed.
