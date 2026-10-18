# Independent binding of the T74 raised-entrance wrappers

**Finite audit passed; no new kappa or complete supplier claim.** PR2435 raises
24 helper entrances from dimension one to two in each of two provider words.
This package binds those changed entrances to their actual native frames,
rank-seven residual recipes, and pre/post wrapper events in both orientations.
Two retained independent exact kernels then verify the resulting 12 distinct
operators on all 512 input columns: 3,145,728 complex coefficients per kernel,
including zero coefficients and global phase.

The new contribution is the changed source binding and its failure controls.
The construction, wrapper factorization, and both arithmetic kernels are prior
work. The producer already checks its wrappers; this audit does not report a
construction bug. See [REVIEW.md](REVIEW.md) for the derivation, premises,
source locations, and the Gram-rank obstruction to a simpler orthogonal
relabeling argument.

## Covered domain

The construction is pinned to PR2435 commit
`324d7d3590dc21003940a44cb0cbdc32b3620f25`. [INPUTS.json](INPUTS.json) pins the
original entrance patches and shipped words, freshly generated complete native
words/programs/recipes, and the unchanged exact kernels. [RESULT.json](RESULT.json)
records every affected helper and event position.

- 48 helper occurrences, with 96 forward/backward orientation bindings.
- Twelve distinct rank-two entrances, each with rank-one restricted binary Gram
  form. They cannot be sent to a two-coordinate span by an orthogonal binary map.
- For each entrance E, both kernels verify `L C_[7] R T_E = T_FULL` exactly.
  Conditional on whole-word logical helper restoration, the physical residual
  in **both** orientations is `T_FULL T_E^-1`. Applying `R^-1` before and `L^-1`
  after the invocation gives `C_[7]` on seven axes and identity on two spectators.
- All affected helper accesses are bracketed by the declared wrappers, in the
  actual entry/cleanup phases. Paid climb ranks total seven in each orientation.

The controls reject 72 altered operators per kernel: wrong global phase,
translation, input character, width in either direction, and a true simultaneous
swap of wrapper sides. Twelve redistributed-phase equivalents per kernel must
pass. Six source/event mutations must fail. The separate regression suite checks
missing providers, an altered second-provider recipe, misplaced phase markers,
accept-all kernels, incomplete/corrupt pinned inputs, and the optimized public
entry point.

The audit uses standard-library exact integer arithmetic. It imports neither
the construction's executable nor its PASS receipts. Kernel A is the unchanged
PR1781 packed Gaussian-integer evaluator; kernel B is the unchanged PR2029
closed-form amplitude evaluator. Their prior method is reused openly.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/t74-entrance-wrapper-audit --check-only
python3.12 -B scripts/research_package.py --package research/t74-entrance-wrapper-audit
```

The registered commands use isolated, optimized Python and require no external
packages. The mathematical replay is also independent of Git and the working
directory; a copied package suffices:

```sh
python3.12 -I -O -B /absolute/path/t74-entrance-wrapper-audit/verify.py
python3.12 -I -O -B /absolute/path/t74-entrance-wrapper-audit/test_verify.py
```

Ordinary replay compares the complete committed receipt and does not write it.
`verify.py --write /explicit/destination.json` is the deliberate regeneration
entry point. Exact SHA256 pins authenticate committed containers before parsing
or importing. [SOURCES.json](SOURCES.json) separately records historical selected
record/catalogue provenance; later upstream priority changes do not invalidate
these frozen mathematical inputs.

To reproduce the six generated inputs, export PR2435 at the exact commit above
to a separate directory, preserving its repository-relative paths. With
Python 3.12 and `numpy==2.4.2`, run:

```sh
python3.12 -B research/t74-entrance-wrapper-audit/reproduce_generation.py --source-tree /absolute/path/pr2435-export --output /absolute/path/new-output-directory
```

This optional step authenticates all five producer modules and the six original
input files, then runs `bw_transport.py`, `bw_emit.py`, and `bw_adapters.py` for
both providers. It compares all six generated JSON payloads, ignoring gzip
container differences. This establishes reproducible extraction; it is a
producer replay, not independent mathematical evidence. The ordinary audit
already has these pinned generated inputs and does not require this step.

## Limits and relation to prior audits

The claim is finite and source-specific. The audit does not replay the complete
scalar restoration, native borrow word, global owner/idle-window assignment,
full invoice, moment inequality, precision bound, or all-size recursive theorem.
The whole-invocation derivation in REVIEW.md assumes logical helper identity and
absence of cross terms. It explains the local wrapper implication; it does not
discharge those global premises. There is no formal-kernel proof.

PR2446 independently audits the scalar word and owner constraints while excluding
entrance delivery. PR2447 binds per-helper widths; PR2453 checks width exchange
partners. PR2029 audits earlier selected wrappers with the two methods reused
here. Those scopes differ from binding PR2435's raised entrances to the exact
phase-aware operator and emitted event stream. The overlap search is advisory,
not a novelty certificate. Coordination is in
[Discussion 2463](https://github.com/CrocSwap/integer-mult-bounds/discussions/2463).

## Open next questions

Can an independent complete native replay combine this changed entrance binding
with the borrow word, owner windows, and both paid wrapper ends at the same
PR2435 source pin? Start from these 48 helper bindings and PR2446's scalar/owner
audit; reconcile every global dispatch before evaluating an invoice. That work
requires a separate bounded audit of the full caller contract. This local check
does not itself justify a new exponent or replace the selected-record review.

## Credit and license

Jeremy Kothe supplied PR2435's raised-entrance construction and producer chain,
building on Vlado Vojdanovski's PR2322 and the credited predecessor chain there.
Sagar Thakrar supplied PR1781's packed exact kernel, PR2029's independent
closed-form kernel and wrapper audit, and PR2446's separate scalar/owner audit.
The two kernel files are copied unchanged with their original notices. Source
commits, paths, hashes, and additional provenance are retained in INPUTS.json
and SOURCES.json; all predecessor claims retain their original premises.

New binding, controls, packaging, and review: Ross Richardson with substantial
OpenAI Codex assistance, including one mathematical frame-scheduling specialist.
This package and its retained code use the repository's Apache-2.0 license.
