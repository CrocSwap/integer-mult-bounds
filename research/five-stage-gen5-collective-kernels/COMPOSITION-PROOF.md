# Kernel-disjoint composition of PR289 with PR290

Prepared with substantial OpenAI Codex assistance. Apache-2.0.

## Result

Conditional kappa = 372359941334341/500000000000000000
= 0.000744719882668682. This exceeds PR290's
186178624839407/250000000000000000 by exactly
2691655527/500000000000000000, or about 0.0007229 percent.
This is a composition of existing public mechanisms, not a new multiplication
algorithm, unconditional theorem, or measured runtime improvement.

Baseline: PR290, commit e5f16c5dfc1c3fcf16a8894915b083819b3cf8dd.
Retiming source: PR289, commit 04e14102a36a33b9f9eef4e4c76119fd6e54b445.
PR287, commit ea7ca18, supplies the inherited descent and target-prefix stages.

## Selection and composition

PR289 selects 87 role-disjoint ADD gates on PR287's post-target word.
The complete original selection is retained byte for byte in
`notices/PR289-extreme-selection.json`. Of these gates, 22 touch helper
streams in PR290's frozen kernel families. We exclude those gates and retain
exactly the other 65: 24 moves from dimension 12 to 14, and 41 moves from
18 to 19. Their 130 operand streams are distinct and disjoint from every
pivot and donor of the 450 kernel entries.

`composition_check.py` independently derives this exact subset from the
original 87-gate selection and the actual frozen kernel membership. It checks
input bindings and rejects inclusion of a conflicting gate, omission of a
compatible gate, a changed basis, and a changed input binding. This stage is
mandatory in `verify.py`, with its own omitted-stage control.

The order is the physical producer, parity fusion, PR287 descent, PR287 target
squares, the compatible extreme retiming, the 450 kernel entries, and global
lowering. `discovery/build_selection.py` recomputes the kernel word binding
and local histogram delta on this actual retimed input. Its entry membership,
bases, and scalar cut bindings remain the same; numerical gains are never
added to independently reported kappas.

A separate complete discovery replay of all 87 retimings followed by the same
450 kernels produces kappa = 37234667777807/50000000000000000
= 0.000744693355556140, below PR290. Thus blindly composing both
submissions is counterproductive; the compatibility selection matters.

Disjointness is a selection rule, not the correctness proof. The actual emitted
word is checked for nested frame paths, fixed endpoints, unchanged scalar/COPY
projection and COPY lifetimes, exact integer source-span inclusions, and both
reflected annihilator ledgers. The kernel stage checks every literal prefix
relation, all 19,406 formal columns forward and inverse, and nonvacuous omitted
setup/restore controls. All subsequent scalar, prime, chart, allocation, complex,
moment and finite checks are retained.

The extreme stage additionally retains the preceding physical frame inventory
in its output. The prime checker continues to verify all producer obligations
and every consumed intermediate frame, including frames absent from the final
word.

## Exact accounting

The extra local paid histogram delta, relative to PR290, is

    {1: 41, 2: 154, 3: -82, 4: -48, 12: -24, 14: 24, 18: -41, 19: 41}

Its rank mass is zero and its call count is +65 locally (+325 in five stages).
The concave cost decreases despite the higher number of calls. Literal stock,
entrance ranks, endpoint deficits, scalar additions, and completed-bank patterns
are unchanged. The actual final histogram is priced afresh by both rational
moment engines, with the complete 10^-16 fallback envelope, three finite
ordinary bootstrap levels, eta = 10^-12 and beta = 10^-9 unchanged.
The adjacent 10^-18 final grid point must fail the unchanged outer assembly.
All updated counts and hashes are recomputed and frozen in
`expected/kernel-pins.json`; verification forbids recording mode.

## Reproducibility repair

At the pinned PR290 commit, MANIFEST.json lists three files absent from its
Git tree: `discovery/twin-census.log`, `discovery/coll/selG5.log`, and
`discovery/coll/families34.log`. The unmodified verifier stops at integrity.
This composition removes those absent discovery-log entries and pins every
actually present file, including all added source and proof files. No proof
input or admission stage is removed. A separate baseline replay with only
that inventory repair reproduces PR290's original kappa.

## Credits and scope

PR290's gen5 collective kernels and discovery are Chafik Boukhalfa's work,
with Anthropic Claude assistance. PR289's extreme-meet selection is Rohan
Gupta's work, with Google DeepMind Antigravity assistance, as disclosed in its
PR. Its transformation header carries its original Anthropic assistance line,
which is preserved verbatim. The present contribution filters the compatible
subset, binds and verifies the composition, retains intermediate determinant
obligations, repairs the manifest, and recomputes the final certificate.

DreamingOfClouds supplies gen5 (PR285, on PR276); Rohan Arun supplies PR287's
retiming and target-square application; eumemic supplies the retiming,
target-prefix and scalar/physical package lineage; Dugongue supplies the
response-kernel mechanism; Henry Grant and Jacob Sussman supply the five-stage
layout; Evan McKinney supplies the entrance-bank lineage. All inherited
licenses, notices, and assistance disclosures are retained.

The all-size compiler, common weighted chart, restored rows, selectors, routing,
prime supply, precision/recovery, complex symbolic correctness and analytic
reduction remain inherited conditional interfaces. Finite replay does not
formally verify the integer-multiplication theorem. The smaller concave cost
is an asymptotic exponent improvement, not a practical speedup claim.
