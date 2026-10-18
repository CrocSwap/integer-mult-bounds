# Independent symbolic audit of selected BIT fallback words

**Independent verification / adversarial mathematical audit. No new κ.**

Jose Manuel's [PR2207](https://github.com/CrocSwap/integer-mult-bounds/pull/2207)
implements mixed fallback descriptors and tests numerical ancestor weights.
This package independently checks its emitted address word with **192
separate symbolic unit weights** on each of four fixed rank-42 charts.
All four polynomial identities pass. No defect in the pinned compiler was
found in this scope.

The exact comparison covers 589,824 matrix entries and retains all 65,024
shear slots. Three block charts use Z/9, Z/25 and Z/49; a deterministic dense
high lift over Z/25 expands the nonzero shear coverage from 18 to 6,413.
One additional small signed fixture exercises the fixed-sign path.

The new evidence is universal in the incoming unit weights **for those fixed
matrices**, rather than another finite sampling of weights. The separately
written Laurent arithmetic and endpoint oracle import no predecessor
reconstruction routines. [PROOF.md](PROOF.md) explains the substitution
argument, exact instrumentation boundary, fixtures and remaining assumptions.
This is not an all-chart proof or a full multiplication theorem.

## Reproduce

From the repository root, using standard-library Python 3.12:

```sh
python3.12 -I -B scripts/research_package.py --package research/selected-fallback-laurent-audit
```

Expected: normal and optimized replays print

```text
PASS_SELECTED_FALLBACK_LAURENT_AUDIT selected_charts=4 weights_per_chart=192 controls=9 no_new_kappa
```

The eight focused tests also pass normally and with `-O`, followed by
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`. Replay compares the
committed [RESULT.json](RESULT.json); it never regenerates it implicitly.
The explicit `--write-result NEW_PATH` option creates a new file exclusively.

All nine deliberate controls must fail for the expected reason. Six have
concrete unit-assignment counterexamples: final-permutation substitution,
wrong chronology, inverse sign, missing pair weight, physical orientation
and omitted fixed sign. The remaining controls cover a missing zero slot,
nonunit inversion and changed source bytes. These are **injected faults**,
not defects attributed to the predecessor.

## Sources, overlap and limitations

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
OS assignment seed **67**, adversarial track. The exact audited head is
`149d55d90d3c0877ed3d78e1deca8eb2f72e0d00` (PR2207).
[SOURCES.json](SOURCES.json) records every consumed input and vendored file
with SHA256, Git blob and source commit. The selected BIT binding follows
the accepted PR1094 assembly to PR589's actual receipt and template.

[CLAIM.md](CLAIM.md) records three candidates and overlap coverage. Concurrent
PR2084/2105/2120 cover stock/depth, PR2188/2207 cover the descriptor construction,
and Discussion2209 claims recursive implementation. This audit deliberately
uses a different checking method. Public-page searches and local overlap
reports provide partial coverage; GitHub API and posting were unavailable
under the donor's workflow. No claim of complete live overlap is made.

The matrices are in the assumed GL implementation domain, not asserted
emitted orthogonal-cover invocations. Small primes are arithmetic fixtures.
The symbolic bank interface abstracts ancestor evaluation. Physical payload
movement, completed weighted children, other local labels, actual caller,
stock/restoration, precision/tape and analytic transfer remain obligations.
No supplier bill or selected frontier is changed. The selected cold replay,
formal kernel and hosted CI are not part of this audit.

## Open next questions

- Can the actual selected caller discharge the remaining ancestor,
  weighted-child and restoration contracts? Follow the concurrent
  [Discussion2209](https://github.com/CrocSwap/integer-mult-bounds/discussions/2209)
  implementation, then audit one complete invocation with its paid child
  interfaces. This matters for turning the address identity into an
  implemented supplier; that implementation is outside this claim.
- Can symbolic treatment extend to a whole high-fiber chart family while
  fixing its pivot itinerary? Start with a single formal nilpotent high
  lift and an exact coefficient-ring implementation. The present checker
  fixes all chart coefficients and does not provide that extension.

## Credit

The compiler and construction remain Jose Manuel's (@jmbarrancoml) PR2207
work. Ross Richardson's PR2159 supplies fallback covariance and scheduling;
commdata2338's PR2160/2188 supplies selected normal-form and mixed-pair
descriptors; PR2171 supplies Jose Manuel's arithmetic interface. The
source527/eumemic lineage, DreamingOfClouds' PR589 tuning of eumemic's PR555,
and Rohan Arun/Jeremy Kothe's selected PR1094/1087 lineage retain credit.
Stock/depth context comes from Josie Elliston, ToikY, Adam Gall,
Sricharan Vagvala and Nick Petalas. See [NOTICE.md](NOTICE.md).

Prepared for **@CubeJerry** with substantial **OpenAI Codex** assistance in
research, implementation, proof explanation, validation and writing. No
independent human review is claimed. New work is Apache-2.0.
