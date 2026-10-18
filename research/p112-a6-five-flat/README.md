# A rank-five cover transfer excludes P112 `5,6^8`

Nine independent P112 pieces with weights bounded by `5,6^8` cannot span a
space whose intersection with the root code has dimension at least six,
over any characteristic-zero field. This is the maximal profile without
weight seven in the original TWOSIDE `(6,3)` residue.

The new [affine cover lemma](PROOF.md) puts any twelve odd rank-five support
labels inside a rank-four flat plus four coordinates. That connects the
actual profile to Nick Petalas/PR3186's existing weighted A6 bound. Seven
endpoints permit 140 support incidences; the root branch requires 141 and
the mixed branch 142. The old arbitrary-cut relaxation gives only 137.

The proof is author-checked with exact replay. It does not settle full C5,
the complete P112 decoder floor, supplier admission or kappa. The standard
Weyl-chamber theorem and original decoder reduction remain dependencies.

## Reproduce

From the repository root, using Python 3.12 and only the standard library:

```sh
python3.12 -W error -B scripts/research_package.py --package research/p112-a6-five-flat
```

With uv selecting the interpreter:

```sh
uv run --python 3.12 --no-project python -W error -B scripts/research_package.py \
  --package research/p112-a6-five-flat
```

`verify.py` authenticates retained sources and the declared input, reconstructs
the geometry, replays the relevant predecessor bounds, exhausts all 64,839
admissible four-cube supports and compares the exact receipt in `RESULT.json`.
The thirty-hyperplane oracle also checks all 560 thirteen-point boundary
failures. `test_verify.py` exercises source, input and receipt failures and
separate algebraic controls. `CHECKS.json` records the actual validation.

For an external fresh receipt, supply an absent path outside the checkout:

```sh
python3.12 -B research/p112-a6-five-flat/verify.py --output "$RUN_DIR/result.json"
```

`RUN_DIR` must be your own external scratch directory. The command refuses
to overwrite a receipt. The registered replay writes no research outputs
inside the checkout. Implementation bounds and deviations are in
[ENGINEERING.md](ENGINEERING.md).

## Sources and credit

DreamingOfClouds/PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d`
supplies TWOSIDE and the C5 handoff. Nick Petalas/PR3186 at
`92675b36a8e0ea41b40f0bcda2a3dd9f313abb0e` supplies the retained weighted
cover and seven-vertex routines, building on PR3176 at
`1111a074414c4d2be8b4e230133d873432780814`. The retained notice preserves
the E8/P112 decoder lineage, including joaqcoo's model.
[SOURCES.json](SOURCES.json) pins exact heads, blobs and SHA256 hashes. Retained proof
links use their original package layout; the underlying root-simplex proof
is also retained at `vendor/ROOT-SIMPLEX-PROOF.md`. The generic runner needs
base history and the live input; vendored source checks do not require pending
PR Git objects. Context-only prior-proof pins record applicability checks.

The six original rank-at-most-six profiles are consequences of the new
maximal-profile theorem. Some were previously excluded; this package does
not count them as six new results. The original rank-seven residue and
concurrent common-cut question remain separate.

## Open next questions

- Which actual weight-seven `(6,3)` profile can use a changed support contract?
  First bind its quotient independence and complete edge alphabet. The
  present support-72 classification and 140-incidence invoice do not apply
  automatically. Full C5 remains the wider blocker.
- Does the affine transfer yield another genuinely new caller? First compare
  its exact rank/support hypotheses with existing exclusions. Do not launch
  another flat census merely to restate this finite cover theorem.

[TASK.json](TASK.json) records the changed card scope, handoff and bounded
follow-up questions. [Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19000918).
