# V45 recovery was already present, and its four directions are already used

The bounded comparison finds **no new fully costed improvement to PR2979**.
It identifies exactly why the proposed information-recovery route stops:

* The same four paired directions are already present on twelve named registers
  of PR2894 and PR2917. Their complete readout maps are identical.
* Those registers are not available at V45 in either shipped literal frame
  schedule. The later paid frame and boundary changes supply access.
* After the four PR2942 extractions, every coefficient from a fresh eligible
  input vanishes from that twelve-register readout. PR2979 retains this exact
  map. The four observable helper coordinates are already restored/protected.

Thus the construction did not create four new algebraic information directions.
It made existing ones usable and then consumed their eligibility. Nonlinear
postprocessing or eligible-only entrance recoding cannot expose a fifth fresh
helper through this fixed readout. Cheaper implementations of the existing four,
changed middle circuits and other observation cuts remain open.

This package adds the exact before/after transfer and its nonlinear consequence,
plus a fixed-target fractional cost screen. It does not repeat the prior pairing
census or claim the existing V45 construction as new.

## Exact comparison

For both base and extra providers, let

```text
V45 = span_F2(256,128,64,35,16,11,5)
U12 = {2,61,62,63,70,71,72,94,249,251,265,267}
P4  = {249,251,265,267}
```

H is the actual eligible-input set after the prelude, excluding restored,
nonzero-frame entrance and initial-correction-source coordinates. U12 is a
specified algebraic observation allowance; it is not asserted to be the complete
set accessible under arbitrary frame refits. Literal supports include protected
and restored registers as well as eligible ones.

| Word | Eligible inputs | Literal V45 readout | Recoverable fresh directions on U12 |
|---|---:|---:|---:|
| PR2894 | 226 | 0 rows | 4 |
| PR2917 | 216 | 0 rows | 4 |
| PR2942 | 212 | 0 rows | 0 |
| PR2979 stage 1 | 212 | all 12 rows | 0 |
| PR2979 final | 207 | 10 rows, omitting 61 and 63 | 0 |

All 98 scalar coefficients of the old U12 map agree between PR2894 and PR2917.
All 42 coefficients of the later map agree across PR2942, stage 1 and final.
The old four-dimensional pairing has determinant -128; eight nuisance directions
and the four observable directions have a square completion of determinant 256.
These dyadic units give the exact four-quantity observation quotient over every
Z[1/2]-module, as detailed in [PROOF.md](PROOF.md).

On each later word, the eligible block is exactly zero. The complete U12 nuisance
minor has determinant 2; the final ten-row literal minor has determinant 1.
Reclassifying P4 as eligible solely as a control recovers precisely their four
identity coordinates. It does not make them new resources.

The nonlinear obstruction also covers finite appended computations at V45 with
fixed output identities and a fixed complete dependency graph, monotone frames,
independent ancillas, and no new warp resets or source/target/earlier-snapshot
reads. It does not cover combining incomparable endpoints. The input cut and
inherited center-cut frame convention are explicit in the proof.

## Cost and stopping decision

The existing V45 local saving is already included in PR2979. [PR3014][3014]
previously proved that retaining PR2942's owner assignment makes that local
saving lose after idle children are charged. PR2979 uses a changed allocation;
we do not transfer the frozen-owner negative to it.

The new cost calculation binds PR2979's actual final inventory, complete profile,
and fixed-bin relaxation. At its rational complex parameter
`b0=0.001729033982646513517717`, write `H_r=r*(73/r)^b0`. An exact basis/dual
calculation over all 2,551 patterns gives the optimal fractional idle charge per
freed helper width:

```text
D = (H48 - H3 - 5 H5)/20
```

For one hypothetical fresh 9-to-7 extraction with actual local change
`E - 2H1`, the best fractional local-plus-idle difference is
`E - 2(H1-D)`. Only approximately **0.0246870954232** tariff units per call
remain for E. The old literal allocation has an additional fractional slack of
about **0.0000367672400** per call; the receipt gives rigorous rational intervals.
The dual has 12 identically tight patterns and 2,539 strictly positive ones.

This screen includes the optimal fractional idle adjustment in the stated bin
model. It is not a completed physical invoice: new private buffers, chronological
owners, native access, stock, precision and outer admission must still be paid.
A favorable screen alone cannot certify a new supplier. Existing packing-only
follow-ups already address the old cap gap.

The comparison yields no unused direction in U12 on PR2979, so no new candidate
reaches the allocation/native/admission stage. We stop this fresh-helper route.
It does not establish global optimality of the existing four-direction circuit.

## Reproduce and evidence

Standard library, Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/v45-recovery-transfer
python3 scripts/check_research_commit.py --package research/v45-recovery-transfer
```

[EXPECTED.json](EXPECTED.json) records complete readout coefficients, eligibility,
terminal frames, left/right bases, pairing matrices and dyadic-unit witnesses.
[RESULT.json](RESULT.json) records the independent checker and exact cost screen.
[VALIDATION.md](VALIDATION.md) states executed checks and review boundaries.

The primary forward engine is the authenticated PR2918 implementation, credited
and reused unchanged. A separately implemented backward-covector/inverse-column
checker imports no predecessor Python and checks every readout coefficient and
basis witness. Both use exact rational arithmetic. The cost basis/dual code is
separate from the predecessor optimizer but uses its authenticated rational
logarithm/exponential enclosure kernel. Neither implementation is a formal-kernel
proof or independent human review.

## Sources, overlap and credit

Canonical base: `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
Scientific heads:

| Source | Exact head |
|---|---|
| PR2894, Jeremy Kothe | `18d03c447886895ef9abf888398178e0428533ca` |
| PR2917, Mason Hale | `224bd5e56041c40078ff6b5fa7393733a215de5c` |
| PR2942, Marius-Paul Dumitrean | `a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf` |
| PR2979, Marius-Paul Dumitrean | `be191346391661f4d35fc0d1508d0a6029572576` |
| PR3172, preceding obstruction | `0a632b00ef59a9f43b1f6c7965ff1ca7a3f188f3` |

The mathematical methods retain Jeremy Diviney's PR2908 paired extraction,
Jeremy Kothe's word/frame/cleanup construction, Mason Hale's extension,
Marius-Paul Dumitrean's coordinated V45 construction and tariff kernel, and
Ross Richardson's PR2918/3172 obstruction. The complete owner/native lineage
retains Yiyang Lu, Tekalign, icekylinx, Dugongue, themilkman216 and the contributors
credited by the frozen packages. Nick Petalas's V45 frame/native/invoice audits
and jwr404's PR3112/3119/3126 audits delimit existing coverage.

PR2979 already reports rank-four V45 pairing in a solver-lowered search model.
Its exploratory script imports absent local `synth`/`lower` modules; we do not
claim to replay that search. The independent literal-support calculation and
fixed U12 map comparison here avoid that dependency. No frozen source is edited
or re-vendored. PR3133/3148 and the separate active whole-word investigation are
outside this bounded comparison.

New work by Ross Richardson with substantial OpenAI Codex assistance, including
separately assigned mathematical, source, cost and verifier reviewers. Apache-2.0.
The underlying quotient and linear-programming principles are standard.

## Open next questions

A useful positive continuation must name a changed middle, observation cut or
implementation of the four already-used directions. Its first step is an exact
before/after program and full local histogram that passes the applicable cost
screen while preserving compensation and restoration. The current zero block
will not price or validate that changed program. Repeating nonlinear decoding
on unchanged U12, or recounting the four existing helpers, cannot reopen this
route. See [TASK.json](TASK.json) for the bounded handoff and blockers.

[3014]: https://github.com/CrocSwap/integer-mult-bounds/pull/3014
