# A QQ16 shear does not remove the transcript floor

**Scoped obstruction; no new supplier or multiplication exponent.**
Adding the proposed invertible A-to-T shear between QQ16's F0 and B1
does not make one dense old-chart query sufficient. Even granting the
shear, observations and all implementation costs for free, an additional
eight-coordinate query leaves at least `ceil(37|G|/5)` dimensions of
original joint A/T input invisible under the contract below.

More generally, **at least sixteen rational-linear scalar owner arrays
remain necessary** after any fixed invertible paired shear in this class.
Each such array has one scalar per owner. Fifteen leave at least
`ceil(2|G|/5)` hidden dimensions. For an unrestricted nonuniform record,
the necessary total rank is `ceil(77|G|/5)`, not `16|G|`. Sixteen arrays
is a necessary floor, not a sufficiency or cost claim.

The contribution is a quantitative transcript floor for the sheared pair,
with an ordered kernel construction and its full-tail implication. The
fourth-moment rank certificate is credited to
[commdata2338's PR #2189](https://github.com/CrocSwap/integer-mult-bounds/pull/2189),
which treated the unsheared first pair. Its finite premises are recalculated
here by a separately implemented, exact text-source checker. The proof is
in [PROOF.md](PROOF.md); [TASK.json](TASK.json) records the precise refinement
of priority-revision-4 card `joint-query-controller`.

## Exact contract

Keep the retained QQ16 local maps and ordinary bank schedule. At the
complete F0/B1 boundary, apply

```text
X_T += Q X_A
Y_T -= Q X_A
```

where Q is a fixed invertible rational operator from the selected A fields
to T fields on the payload-constant regular-cover subspace. This includes
the displayed-order raw pairing proposed in
[PR #2216](https://github.com/CrocSwap/integer-mult-bounds/pull/2216).
Ordinary fields stay unchanged. Permit an extra rational-linear record of
total rank at most d; a dense `B0 X_U` query has at most `8|G|` coordinates.
Additional paired taps driven only by this record and vanishing when the
record is zero are also harmless to the counterexample.

Grant selected values **after the complete sheared F0/B1 pair**, all later
selected cuts and selected-only homogeneous controls, all five forward
query histories, and all completed-X descendants. The former-Y final hole
is excluded, exactly as in the retained witness.

The transient post-F0 A value is generally nonzero. Saving it, or another
pre-B1/within-B1 selected value, is additional information whose rank must
be counted in d. Unlike PR #2326's coordinate-tap witness, this theorem
does not grant all pre-B1 selected cuts for free. The bound concerns the
**joint original A/T input**, not the A input alone.

## Result and evidence

Writing `r = rank[B0; B1; B2]` and `N = |G|`, the ordered construction gives

```text
hidden joint selected-input dimension >= r - 8N - d.
r >= (117/5)N.
```

It leaves zero selected state and zero ordinary X after B1, with an
ordinary Y residue `g = (I - K_(1,U) B1/11) h`. The retained tail carries
g only to the former-Y hole. This residue map is invertible, with inverse
`I - K_(1,U) B1`; it is not a discarded zero-input construction.

Verification covers:

- The native root order, selected minors and ordinary Gram `48 I`,
  reconstructed from exact main-branch source files.
- All 336 stage-0/1/2 owner routes on 73 binary axes, including the 48
  fixed spectator axes; all six tables of 9,216 ordered relative-route
  products and their required intersections.
- The exact moments `24, 28, 109/3, 1823/36` and the rational polynomial
  rank certificate, without floating-point acceptance.
- The ordered changed-pair algebra, full retained tail and rational
  model checks, including deliberately incorrect alternatives.
- Source and receipt integrity in normal and optimized Python execution.

Local validation passed on Linux x86_64, CPython 3.12.3: registered normal
and optimized replay, all 18 mathematical/schedule failure controls,
and five integration tests (including Git-free read-only relocation,
source drift, receipt type corruption and overwrite refusal). These are
author/agent checks, not hosted CI or independent human review.

The universal statement rests on the written ordered argument and rank
inequality. Small matrix fixtures corroborate the algebra; they do not
stand in for the full regular cover or an all-size supplier proof.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-shear-transcript-floor --check-only
python3 -I -B scripts/research_package.py --package research/qq16-shear-transcript-floor
```

The direct checker also works in a source export containing the pinned
input files:

```sh
python3 -I -O -B research/qq16-shear-transcript-floor/verify.py
```

Replay is read-only and compares every deterministic field of
[RESULT.json](RESULT.json). `--emit-result NEW_PATH` explicitly creates a
new receipt and refuses to overwrite an existing file. Exact upstream
commit, Git blob and SHA256 pins are in [SOURCES.json](SOURCES.json).
The catalogue and selected-result record are historical provenance;
the declared mathematical inputs are checked as live source bytes.

## Source boundary and limitations

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The prototype, native phases, centre constructor and port transport are
individually bound to the selected source manifest. R is reconstructed
from root-coordinate totals and the literal `tau=43` port permutation.
Owner maps are reconstructed from the orthonormal-chart definition in
main's native verifier. The payload-constant restriction retains arbitrary
independent cover-owner values; it is not a cover-invariant approximation.

The tail uses the retained QQ16 witness's bridge trajectory and the pair
sequence recorded in Brody Arbon's main-branch replica-prefix audit. It
checks this logical schedule, not the compressed parent template itself.
The compressed QQ16 packet, its map registry, the complete scalar words,
native field types and the full supplier are **not replayed**. Their
identification with these source definitions and the retained logical
interface remains inherited. The prescribed selected-baseline command
was attempted but could not verify the complete selected package inventory
in this bounded text export. No baseline pass is claimed. The new scoped
checker does not weaken or replace that baseline check.

This excludes only the stated shear, record and observation model.
Ordinary-state changes, a different local pair, nonlinear encoders,
uncounted independent payload storage and access to the former-Y hole
are outside it. No native rank tariff, favourable moment invoice,
supplier adoption, new kappa, proof-assistant result or independent human
review is claimed. The existing selected frontier remains unchanged.

## Overlap and credit

- Ali Romman / PR #1969: conserved QQ16 maps, cover action, native words
  and original selected-output witness.
- Adam Gall / PR #2093 and CubeJerry / PR #2306: the nonzero-chart and
  selected-only obstructions. Cinna Davis / PR #2216 and PR #2268:
  the shear and coordinate-tap witness repairs.
- commdata2338 / PR #2326: the full-input coordinate-tap obstruction and
  explicit dense-observation handoff taken here. That result also grants
  earlier selected cuts; the distinction above is essential.
- commdata2338 / PR #2189, Nick Petalas / PR #2181, Ross Richardson /
  PR #2104 and commdata2338 / PR #2153: trace-moment and transcript
  capacity methods. The fourth moment and polynomial are reused with
  credit, not presented as a new numerical discovery.
- commdata2338 / PR #2174: two-query recovery with a recorded first-pair
  cut. Charles Bethin / PR #2252 and commdata2338 / PR #2328: separate
  native-frame and shear-tariff results.
- Brody Arbon's `replica-prefix-audit`: the retained complex parent
  stage-to-pair sequence used to bind the logical tail.
- The source construction and transport retain icekylinx,
  DreamingOfClouds, Chafik Boukhalfa, Jeremy Kothe, Rohan Arun, Hao Yan,
  Zhihao Chen and the remaining lineage in the unchanged
  [QQ16 notice](../joint-query/NOTICE.md).

Prepared for Jason (@jgilfoil) with substantial OpenAI Codex assistance
in derivation, implementation, checking and writing. A separate agent
reviewed the ordered proof; this is not independent human review.
New material is Apache-2.0. No predecessor executable is imported or
vendored. Live PR overlap was checked with complete pagination; Discussion
coverage and publication limitations are recorded honestly in TASK.json.

The final overlap refresh found concurrent
[PR #2346](https://github.com/CrocSwap/integer-mult-bounds/pull/2346), which
rules out one specified set of 64 initial query coordinates without a
pre-F2 selected intervention. It grants final selected values but not a
free B1 cut. Its family and observation contract differ from this changed
shear result; neither result supersedes the other.

Publication was delayed by shell network restrictions. During that delay,
@starship-s published [PR #2368](https://github.com/CrocSwap/integer-mult-bounds/pull/2368),
head `e5d4d78dcfdd55d323fcbc60df477b9f25c7abff`, with an independently
derived graph-intersection obstruction for the shear plus the initial B0
record. Its proof also permits an arbitrary fixed invertible pairing. We
read that proof during the publication refresh and credit its overlapping
changed-pair kernel and tail argument; no first-closure claim is made here.
The original local package was committed at 06:08 UTC before that reading.
This package adds the arbitrary rank-d transcript bound, the stronger
`ceil(37N/5)` one-query defect and sixteen-array floor using PR #2189's
fourth moment, and a separate exact text-source moment implementation.
PR #2354's sharp 66-port threshold concerns its specified common-axis family
and coordinate observations; it does not settle this transcript bound.

## Open next questions

1. **Which changed first pair evades this kernel?** Specify one ordinary
   update or local-map change and test the entire observation kernel on
   dirty inputs. This matters because pricing the excluded repair cannot
   close its information gap. The retained map/schedule is the blocker.
2. **Can sufficient records survive to the final cut at favourable cost?**
   Start with PR #2174's two-query recovery and trace how its B1 cut
   values become accessible final records. PR #2346 excludes replacing
   that cut by its specified 64 initial queries without pre-F2 intervention;
   a different retention mechanism is needed. Native frames, storage,
   restoration, hosting, tape and precision must all be charged. The
   information floor alone establishes none of these obligations.
