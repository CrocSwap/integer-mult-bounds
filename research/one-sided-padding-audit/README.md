# Audit the field scope and normalization cost of one-sided padding

**No new κ.** This independently checks the support and cost implication used
by DreamingOfClouds' [PR3074](https://github.com/CrocSwap/integer-mult-bounds/pull/3074),
at `3cc41f260c31052c933d0e75ea02f2b7677e780c`. The padding rule is correct with
the post-merge cost as its reference point. A new exact certificate extends
this local statement from characteristic zero to every coefficient field
whose characteristic is not two, with the same fixed binary cost table.

The larger 120-line decoder floor **L120 remains open**. This package neither
proves a new lower bound nor supplies a faster multiplication construction.

## Established result

- All **511** nonzero binary characters are checked on the literal PR2816
  geometry. On P112, **503** complement matrices have rank eight and **eight**
  have rank seven, with the eight coordinate axes as their exact kernels.
  On P120, all **511** have rank eight. The **1,022 integer minor witnesses**
  have absolute determinants **16, 32 or 64**, proving these ranks over every
  field of characteristic other than two.
- For every finite one-sided decoder in this fixed model, merging corrected
  terms gives `c_normalized <= c_raw`; padding costs exactly
  `c_normalized + 8`, hence at most `c_raw + 8`. The written proof explicitly
  handles a correction disappearing through cancellation.
- A rational cancellation fixture gives **72 → 64 → 72** for raw, normalized
  and padded costs. Skipping merging preserves its endpoint but costs **81**,
  exceeding the raw-plus-eight budget. The original parent checker agrees on
  the new cancellation fixture; its code already uses the correct post-merge
  reference point. This is a clarification, not a counterexample to its
  conditional lower-bound implication.
- The lift implication `L120(K) => cost_w(S) >= 64 + |I|` is rederived with
  explicit hypotheses. All 256 coordinate-code frame subsets calibrate the
  extension. All 6,560 nonzero F3^8 directions corroborate the field extension.
  In characteristic two the nonzero all-ones direction has zero output,
  demonstrating why that field is excluded.

See [PROOF.md](PROOF.md) for the universal argument, the finite-to-universal
bridge, and the distinction between decoder cost and lift weight.

## What is new, and what is inherited

Mihir Srivastava's **PR845** owns the original real support lemma. Adam Gall's
**PR1098** already gives an exact, code-independent Gram-spectrum check; Jose
Manuel's **PR1815** adds an exact coloop/fitting corollary. The 503/8 real
census is **not new**, and we do not suggest those proofs were numerical.

PR2816's particular `checks/w8.py` uses floating `matrix_rank` and SVD for
its copy of that premise. This package provides explicit integer minors for
**that source chart**, verifies the full P120 extension required by PR3074,
and uses their power-of-two determinants to state the field extension.
Neither the new checker nor its minor generator imports predecessor code.
The generator uses rational elimination; the checker verifies integer
determinants and null directions. They share the new geometry authentication.

The padding construction and lift reduction belong to **DreamingOfClouds /
PR3074**, building on **PR2816**. The general proportional-term merge lemma
belongs to **joaqcoo / PR1224**. Our new cancellation fixture supplements the
parent's split-column fixture and makes the normalization reference explicit.
This is an independent implementation and a scoped written audit, not an
independent human or formal-kernel review.

## Reproduce

From the repository root, Python **3.12**, standard library only:

```sh
python3 -B research/one-sided-padding-audit/verify.py
```

Expected final status: `PASS_ONE_SIDED_PADDING_AUDIT`, with 511 characters,
256 lift masks, 6,560 F3 directions, cancellation `72->64->72`, eleven rejected
controls and `no_new_kappa`. The default command reads only and compares the
complete recomputed result with [EXPECTED.json](EXPECTED.json). The checks
also remain active with `-I -O -B`.

The registered command is:

```sh
python3 -B scripts/research_package.py --package research/one-sided-padding-audit
```

To rebuild the certificate independently of the stored minors, choose a new
external output file:

```sh
python3 -B research/one-sided-padding-audit/generate_certificate.py /tmp/new-padding-certificate.json
python3 -B research/one-sided-padding-audit/verify.py --certificate /tmp/new-padding-certificate.json
```

The generator refuses to overwrite. Certificate comparison is mathematical:
all minors, coverage and kernels must verify; a different valid minor choice
is allowed. The completed deterministic regeneration also matches the shipped
certificate byte for byte. `--output /path/to/new.json` writes a new receipt
instead of comparing EXPECTED.json and is explicitly an evidence-generation
mode. It never overwrites an existing file.

Eleven controls reject missing/duplicate characters, false or damaged minors,
wrong null directions, missing full-frame minors, missing frame values in two
decoder types, the exact-but-over-budget unmerged construction, and use of a
frame delta as a one-sided code factor. F3 exhaustive coverage and the F2
kernel witness are additional field-boundary controls.

## Pins, validation and limits

Publication base: **`18aacb215fc3717b06be8ceb9fca62aeca0d3e99`**, priority revision 6.
Orientation began at **`d8e0f83f00191df62174b641e9fff055c357f641`**. Main advanced
during verification; the package was moved forward with all pinned inputs
unchanged. The updated ledger leaves PR3074 awaiting a source-manifest
clarification, which is not a mathematical rejection.
The selected result at that base is κ = 0.001672660197076918, with the complex
supplier binding. Its source, review and actual construction were traced;
`scripts/research_baseline.py` passed as a binding-only check. No selected
cold replay or frontier change is part of this audit.

[SOURCES.json](SOURCES.json) records exact Git blobs and SHA-256s for the four
live inputs, historical guidance and predecessor statements, plus PR3074's
remote source pins. The live PR2816 files also match its original head
**`4c32ac3b88d63ad06d2b30e526aa07a12929db36`** byte for byte. No source archive
or upstream file is changed. [VALIDATION.json](VALIDATION.json) records only
checks actually executed and separates the optional SymPy-based parent replay
from the new standard-library verifier.

The seed-74 assignment, three candidate audits, changed task-card scope, local
claim and overlap limitations are in [TASK.json](TASK.json). The standard
overlap helper could search local notes but could not refresh remote data
because `gh` was unavailable. Connected GitHub all-state searches and public
Discussion reads supplied focused live checks, not a fully paginated novelty
certificate. No pinned coordination issue was present; the available plugin
has no Discussion-write capability, so the claim/result are recorded locally.

The quantified result is restricted to this finite line set, Gram endpoint,
dense binary pairing and algebraic rank-cost model. All-size/compiler,
common-label realization, source access, physical copying/restoration,
hosting, precision/tape and analytic transfer are untouched. We do not audit
PR2816's unrelated LP or residue results, and do not infer a universal decoder
barrier. No native build, Lean, repository-wide suite or hosted CI is claimed.

## Open next questions

1. **Can L120 be proved in characteristic zero?** It would turn the verified
   padding implication into the desired one-sided P112 lower bound. Start
   with the explicitly open cases in PR3074/PR3049, and inspect live follow-ups;
   the present minors alone cannot settle arbitrary lifts.
2. **Can this finite bridge be kernel checked?** The 1,022 small integer minors
   and merge/padding proof are a bounded starting point. Formalize the fixed
   label map and rank restriction lemma first; no proof-assistant development
   is supplied here.
3. **Does L120 hold in positive odd characteristic?** The local padding rule
   now transfers it if available. A first step is a small-field lift example
   or obstruction with the fixed B table; none of PR2816's other
   characteristic-zero arguments is transferred by this contribution.

## Attribution

Prepared for **@CubeJerry**, with substantial **OpenAI Codex** assistance in
selection, mathematics, implementation, verification and writing. No subagents
or independent human reviewer were used. New material is Apache-2.0.

Credit DreamingOfClouds (PR3074/2816, and retained PR717/2338 geometry), Mihir
Srivastava / @mihir-s-05 (PR845), Adam Gall / @adamgall (PR1098), Jose Manuel /
@jmbarrancoml (PR1815), joaqcoo (PR1224), Philippe Van Velzen / @philippeVV
(gain-law and padding context), Joel Pulikkan / GamingPuzzled (coordinate
decoder), Douglas Colkitt and the retained E8/native supplier lineage. The
predecessors' notices and disclosed AI assistance remain unchanged.
