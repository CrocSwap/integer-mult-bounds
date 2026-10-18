# Exact evidence for PR620's free asymmetric sink exclusion

The archived PR620 screen reports zero free asymmetric sinks among 28,560
P112 target/sink pairs, using NumPy floating-point ranks. This package
confirms that specific result with 4,030 nonzero integer minors, independent
Fraction replay, complete binary row-code enumeration, and 112 feasible
same-label controls. It resolves an evidence gap, not a mathematical error
in the original reported count.

The exact ranks are **7 for 448 cases and 8 for 28,112 cases**; the target
lies in the source span in every alternative. [PROOF.md](PROOF.md) gives
the domain equivalence and explicit upper bounds. A replay that simply
expects all cases to have rank eight would be wrong.

From the repository root:

```sh
python -I -O -B research/p112-free-sink-audit97/verify.py
python -I -O -B research/p112-free-sink-audit97/independent.py
python -I -O -B research/p112-free-sink-audit97/test_package.py
```

The producer prints `PASS_P112_FREE_SINK_EXACT cases=28560 free=0 self_controls=112 no_new_kappa`.
The independent checker reports the same case count, the exact rank
histogram and 4,030 minors. Controls report `mathematical=6 package=5`.
Python standard library only; no solver, NumPy or native compiler required.
Use `verify.py --write` to regenerate the certificate.

The immutable input inventory in SOURCES.json is exact: missing or extra
entries fail. Text hashes normalize CRLF to LF. BASE-SELECTED.json freezes
context at base `2921874911956718fcaaaf9396fe8267b3cfa9f0`; replay does not
depend on the future live selected pointer. No source package is imported
or modified. The only executable source extraction is an AST literal read
of the four-row Hamming generator, with no source execution.

The PR620 review is still partial: this does not settle its paid-extra-total
search, solver barriers, general decoder floors or pricing claims. It
does not change the selected kappa or admit a physical supplier. See
[OVERLAP.json](OVERLAP.json) and [VALIDATION.md](VALIDATION.md).

Credit: Joel Pulikkan / GamingPuzzled for PR620's observation and model;
DreamingOfClouds for PR595's geometry/format and paid-extra-total lineage.
Original attribution in the pinned README, report and geometry source
remains authoritative. Contributor @woklerx with substantial OpenAI Codex
assistance. Apache-2.0 under the repository license.
