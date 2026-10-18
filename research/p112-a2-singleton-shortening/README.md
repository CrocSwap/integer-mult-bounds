# P112 three-endpoint singleton shortening

This package proves a scoped characteristic-zero shortening lemma and excludes
one historical TWOSIDE profile. It does not establish the complete P112 decoder
floor, a supplier or a new kappa.

For collectively independent small pieces and three endpoints whose support
labels each have binary rank at most six, a common small-support union of at
most 21 forces their span's intersection with the P112 evaluation code to
have dimension at most one. The new argument permits arbitrary common shifts,
including nonmodal shifts.

Deleting four unrestricted pieces from the original `(b,t)=(6,5)` profile
`2^3,5,6^3,7^4` retains at least two code dimensions on four small pieces and
three rank-six endpoints. The small-support cap is 18. The required endpoint
support is 68 against allowance 60, a contradiction with margin 8.

The [proof](PROOF.md) gives the quantified statement, root normalization,
nonmodal-shift inequality, caller binding and deletion argument. `RESULT.json`
contains the exact finite certificate. The support-21 theorem is sufficient;
the relaxed bound equals 60 at support 22, with no sharpness claim.

## New finite ingredient

An A2 simplex has three disjoint 27-line singleton classes. Each class's labels
span seven binary dimensions. Its 127 nonzero hyperplane restrictions have
kernel sizes `0:1,11:27,12:36,15:36,16:27`. Thus any rank-six support meets its
own singleton class in at most 16 labels.

At a singleton coordinate belonging to endpoint i, total support is at least
`2 - indicator(endpoint i is nonzero)`. At a three-distinct coordinate it is
at least two. After eight frame punctures and s common cuts, the lower bound
is `104-2s`. At s=21 it gives `62>60`; the named caller gives `68>60`.

The primary checker proves coverage of all 13,440 ordered A2 root pairs and
binds their invertible binary reflection actions. A separate checker generates
all 296,010 six-label subsets of each singleton class, obtaining 3,189 distinct
spans and the same 27 maximizing intersections per class. Their digests agree.
The separate checker imports no primary or predecessor executable code. This
is an independent implementation check, not independent human review.

## Reproduce

From the repository root, using standard-library CPython 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/p112-a2-singleton-shortening
```

The registered commands run the primary certificate, separate checker and
13 behavioral test groups. They check nonmodal shifts, actual deletion and
caller-map guards, changed receipts/source bytes, wrong stars, missing labels
and unsafe output paths. Default replay is read-only. `verify.py --output PATH`
creates an absent external receipt and refuses existing or checkout paths.

The inherited capacities are also replayed on all 3,309,747 binary five-spaces
and 788,035 six-spaces. The chamber and plane ingredients include 960 simple
reflections and 7,140 root planes. All 174 historical target profiles are
retained, and the unchanged predecessor program independently accepts the
named profile before this new exclusion.

Exact local environments, commands, outputs and hashes are in `CHECKS.json`.
The selected cold replay is unrun because the selected construction and its
frozen inputs are unchanged. Hosted CI is separate from local evidence.

## Sources and prior coverage

Scientific base is canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
`TASK.json` declares the change from supplier construction to this scoped
decoder-floor obligation. `SOURCES.json` pins every input and retained copy.

Credit DreamingOfClouds/PR3154, head
`708f0ad8928c383de8294aea3c126e9461d2066d`, for the original reduction, caller
and TWOSIDE filters. Its copied `bx_data.json` is authenticated by SHA256 and
Git blob, without requiring pending Git objects at replay time. A computed
invertible nine-bit map binds all 112 original labels to the declared labels.
Matching root sets alone would not suffice.

Credit Nick Petalas/PR3211 for the endpoint normalization and deletion
predecessor, PR3164/3169/3173 and later A3/A4/A5 shortening work, and the retained
E8/P112 geometry and decoder lineage, including joaqcoo. Geometry and the
historical filter are copied byte-identically from the base-retained sources.
New proof and checks by Nick Petalas, Apache-2.0. Substantial automated assistance
was used. No independent human or proof-kernel review is claimed.

Deleting only three pieces here leaves a weight-seven endpoint. Prior A3
rank-six shortening does not directly apply; the support-twenty A4/A5 endpoint
contracts likewise do not directly apply after fewer deletions. This is not a
complete audit of every implication of earlier profile exclusions.

## Scope and decision

The standard Weyl-chamber theorem and original decoder reduction remain written
dependencies. Full C5, `C(P112)>=64`, native COPY realization, physical costs,
supplier admission, all-size/compiler and multiplication transfer are outside
this result. The selected frontier remains unchanged. Family decision is narrow
and stop after this named implication, not a new construction campaign.

## Open next questions

Which still-open caller meets the three-endpoint contract after deletion?
First reconcile public exclusions, then bind its retained code dimension,
common support at most 21 and literal rank-six endpoint supports. An unresolved
caller or missing support/rank premise is a blocker; another geometric census
alone would not close it. The structured question is in `TASK.json`.

## Engineering checks and deviations

Build the Lever led to the replayable hyperplane certificate. Prove It Works
led to the separate generated-span check and committed/exported-byte tests.
Test Behavior, Not Implementation led to arbitrary-shift and CLI failure controls.

Power-of-Ten managed-runtime deviations are limited to this finite verifier.
Python integers, rational arithmetic, JSON and collections allocate dynamically.
New geometry is bounded by 120 lines, 240 signed roots, 13,440 ordered pairs,
511 ambient functionals, 27 singleton labels, 296,010 six-label tuples and at
most 296,010 retained span keys per class. Actual retained span keys are 3,189;
only one class's generated spans are live at a time. Span sets contain at most
64 vectors. Inputs are capped at 2 MB, source metadata at 32 KiB and original
caller data at 32 KiB. The inherited five/six-flat traversals have fixed counts
listed above. The unchanged historical filter has bounded weight/packing loops
but prints at import; its isolated subprocess has a 120-second timeout and
a fresh private bytecode-cache namespace, removed on exit.

There is no recursive new traversal. Functions are reviewed against the
60-line ceiling. Checks remain active under optimization. Explicit local-path
imports support isolated execution; no source evaluation or plugin registry is
introduced. Applicable Ruff diagnostics, formatting and warning-enabled Python
checks are recorded. No fixed-allocation implementation, allocator profile or
static type proof is claimed. A variable-size service would require a separate
capacity, allocation and diagnostics design rather than relaxing these bounds.
