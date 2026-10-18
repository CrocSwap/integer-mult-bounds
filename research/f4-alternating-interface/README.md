# F4 Hermitian trace: alternating is not automatically uncompileable

## Finding

The alternating-trace observation in Joel Pulikkan's historical
`research/e8-decoder-floors-and-cold14-notes/s1-extension-rings/REPORT.md`
is correct. Its inference that this alone rules out the complex-side phase
calculus needs an interface qualification: alternating nondegenerate binary
blocks do not have an orthonormal basis, but the repository's later
`notes/endpoint-gauge-complex.tex` explicitly compiles them by quadratic
phases, binary address changes and a rank-r child.

This package provides an elementary proof and a fresh exact arithmetic audit
of that distinction. **It does not construct an Eisenstein supplier or claim
any new kappa.** The source report is historical and is left unchanged.

## Reproduce from the repository root

```sh
python -B research/f4-alternating-interface/verify.py
python -O -B research/f4-alternating-interface/verify.py
```

Both runs print the same JSON receipt (including the source digest):
452 quadratic-phase cases, 114,752 kernel entries, four rejected negative
controls, an explicit ordinary-dot-product embedding of a hyperbolic block,
and this complete Hermitian trace-rank census:

| F4 dimension | number of matrices by binary trace rank |
| --- | --- |
| 1 | rank 0: 1; rank 2: 1 |
| 2 | rank 0: 1; rank 2: 5; rank 4: 10 |
| 3 | rank 0: 1; rank 2: 21; rank 4: 210; rank 6: 280 |

The checker uses only Python's standard library, integer Gaussian pairs,
packed F2 vectors, and explicit F4 polynomial multiplication. It imports no
repository implementation. `--output NEW.json` writes an exclusive-create
receipt and never replaces existing evidence. Default runs write nothing.

## Scope and handoff

`PROOF.md` gives the general trace-radical argument and complete-square
identity; finite enumeration checks the specified dimensions, not all sizes.
No proof assistant was used. In particular, this does not establish that
all supplier frames are nondegenerate, that their intersections remain so,
that source-label containment is preserved, or that adapters and physical
copies have an affordable bill. These obligations must precede any claimed
Eisenstein construction. Supporting alternating blocks is necessary here,
not sufficient for a useful decoder.

The selected certificate, suppliers, upstream sources and historical reports
are unchanged. Full `make verify` and the selected cold replay were not run:
this isolated note modifies no production code or selected construction.
See `CLAIM.md`, `SOURCES.json`, `RESULT.json` and `VALIDATION.md` for exact pins,
selection history and executed checks.

Prepared for Maximus Putnam / @Maximooch with substantial OpenAI assistant
(Penguin) assistance in mathematics, implementation, checking and writing.
Apache-2.0, following the repository contribution license.
