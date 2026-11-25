# Direct product call: the dirty physical implementation gap

**Refined audit of one added connector operation. Partial result; no supplier or κ claim.**

## Question and result

The open [PR #3586](https://github.com/CrocSwap/integer-mult-bounds/pull/3586),
head `cde0d3c3a3be86de0c051dc1d2f270ff0f5ae2cd` on base
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, adds a direct operation on the
one-source, one-output identity instance. Let `B` update dirty connector `z`
by `x`, let `A` update dirty target `y` by `z`, and let `D` update `y` by
`x` while leaving `z` alone. `D` maps all eight dirty states correctly in one
call by definition. The old alphabet needs at least four calls; `B A B A`
attains that bound.

The physical boundary is the missing step: `D` is not implemented by a
one-call word over the existing `A/B` interface. In this exact control, any
old-alphabet word that works for arbitrary dirty `z` uses an even, nonzero
number of `B` calls and an even, nonzero number of `A` calls. Therefore it
costs at least four complete calls. `B A B A` is an explicit realization.

For compatible general linear maps, the same sequence implements
`y += A B x` and restores arbitrary dirty `z`:

```text
B: z += Bx
A: y += Az
B: z += Bx
A: y += Az
```

The two `A` updates cancel `A z_initial`; the two `B` updates restore `z`;
the remaining target update is `A B x`. A hypothetical fused `D_AB` may be
cheaper, but its cost and physical realization are a new supplier premise.
The scalar identity example does not establish that general supplier.

Chronologically, this realization holds `x` live across both `B` events,
keeps `z` available for all four complete calls, and updates `y` at the two
`A` events. It supplies no proof that an actual consumer has those source and
target windows. For a selected caller, the acceptance comparison is the full
`D_AB` price (including preparation and interface overhead) against
`2 c_B + 2 c_A` for the replaced calls.

## Scope and limits

The verified finite control covers arbitrary initial `x,y,z` in `F2`. The
parity argument proves the four-call lower bound for every finite `A/B` word
on that control, not merely words of length at most three. It does not rule
out a distinct native fused implementation, a precomputed composite operator,
or a changed scratch/cleanliness contract. No source-window schedule, operator
preparation, native cost, frame conversion, tape/dispatch bill, hosting,
precision, or complete recursive moment is established here. These unknowns
cannot be treated as zero for supplier admission.

The source contract is the pinned
[universal connector interface](../universal-connector-boundary/README.md).
The exact #3586 proposal head, base, and public PR-body digest are recorded in
[EXTERNAL-PINS.json](EXTERNAL-PINS.json). That external source is a cited
proposal, not a verifier input; the verifier is self-contained and does not
fetch the PR.

## Reproduce

From the repository root:

```sh
python3 -B research/connector-direct-call-physical-gap/verify.py
python3 scripts/research_package.py --package research/connector-direct-call-physical-gap --check-only
```

The verifier uses only the Python standard library. `SOURCES.json` pins the
main-branch interface note; the external PR is cited as the proposal under
audit, not used as a runtime input. The project registered replay is CPython
3.12; this session's interpreter result is recorded separately.

## Open next questions

**Question:** Does a general `D_AB: y += A B x` have a concrete supplier with
complete cost below the dirty `B A B A` implementation at the selected scale?

**Why it matters:** Only a priced fused operation can turn the one-call
abstract alphabet saving into work eliminated from a recursive supplier.

**First step:** Specify the exact source/target windows and frames for one
literal selected consumer, then bind a fused implementation to its input
reads, coefficient preparation, private scratch, dirty restoration, tape,
dispatch, and hosting invoice.

**Blocked by:** No such physical implementation or complete price is present
in the inspected proposal; a one-bit identity control cannot supply it.

## Credit

Credit jwr and the PR #3586 predecessor for the one-by-one direct-call
proposal and its stated dirty-state comparison. The source interface and its
broader five-source context remain attributed to their existing package
authors. Prepared by OpenAI Codex (laptop-09), with no independent human
review claimed. Apache-2.0.
