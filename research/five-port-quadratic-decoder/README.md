# Five-port quadratic decoder: an optimistic cost obstruction

**Research note / scoped negative result. No new kappa or physical supplier.**

PR231 shows that five-coordinate ports admit a level-one XOR star decoder,
but leaves its geometry and pricing open. This package checks the natural
quadratic pairing `G(S,T)=2(|S intersect T|-1)(|S intersect T|-3)`.

The old incidence-linear geometry is impossible: 16 mutually orthogonal
nonzero labels inside one cube would have to fit in dimension at most six.
The quadratic lift supplies the required geometry, but its copied stars
and active frame work alone imply

```
supplier saving < 125/76433 = 0.0016354192560804888...
```

This is below the selected conditional **kappa = 0.001661957774647029** at
base **47481c89fd30a43f8f882eb4b391e89c29273fd0**. It covers every `p>=5`
coordinate-pair count and every `s>=3` stage count **within the explicit
separate-star, drop-free-correction, compressed-window premises**.
All other work is optimistically granted zero cost. This is a ceiling on
one proposed format, not an achievable bound or an unrestricted decoder
impossibility theorem. Read [PROOF.md](PROOF.md) for the precise premises.

## Reproduce

From the repository root, offline, Python 3.10+ and the standard library:

```sh
python3 -I -B research/five-port-quadratic-decoder/verify.py
```

Expected:

```text
PASS_FIVE_PORT_QUADRATIC_DECODER witnesses=17 ceiling=125/76433 tail=250/170739 controls=9 no_new_kappa
```

The script checks 17 literal integer minors modulo the checked prime
65521, 37,888 small-instance source/target coefficients, the 16-port parity
clique, the rational logarithm and cost inequalities, four source pins,
and nine adverse controls. A nonzero modular minor is exact evidence of
a rational rank **lower bound**, not a numerical rank estimate.

Two supplementary commands check the same rank obligations using a
separately written feature-pairing implementation and fraction-free
elimination at prime 65519, and exercise six package tests:

```sh
python3 -I -B research/five-port-quadratic-decoder/independent.py
python3 -I -B research/five-port-quadratic-decoder/test_package.py
```

The second implementation also computes two integer determinants exactly.
It was written by the same AI-assisted contributor and is **not independent
human review**. Both checkers support optimized Python and compare their
computed receipts to the committed JSON. `--write-certificate PATH` creates
a new receipt exclusively, so an existing file is never overwritten.

## Evidence and scope

- [WITNESSES.json](WITNESSES.json): explicit row/column port labels for
  corrector minors at `p=5..13` and separate-star minors at `p=5..12`.
- [CERTIFICATE.json](CERTIFICATE.json) and [INDEPENDENT.json](INDEPENDENT.json):
  exact residues and rational comparisons, including the strict gap to
  the selected value frozen at the base commit.
- [PROOF.md](PROOF.md): the scalar identity, linear-label obstruction,
  quadratic lift, finite rank implications, all-p embedding and all-stage
  cost argument. The infinite tail uses the `p=13` minor, not a search
  extrapolation.
- [SOURCES.json](SOURCES.json) and [NOTICE.md](NOTICE.md): dependency pins,
  original attribution and AI disclosure.
- [CLAIM.json](CLAIM.json), [OVERLAP.json](OVERLAP.json) and
  [VALIDATION.md](VALIDATION.md): sprint scope, overlap and handoff evidence.

`discover.py` records a deterministic witness-construction pass with seed
40. It enumerates the full candidate port families, shuffles each list,
and stops each greedy feature-basis selection at the size recorded in
`WITNESSES.json`. It then extracts a nonsingular pairing minor. There is
no optimizer or search-optimality premise; discovery is not imported by
either checker. It refuses to overwrite its committed witnesses.

Different Gram pairings, coded totals, punctures, paid non-drop-free
corrections/gathers, and different stage accounting are outside scope.
The selected frontier and `upstream/` are unchanged. All-size realization,
common-label/mutable-source validity, hosting, precision/tape, bit H1–H5,
and analytic transfer remain inherited obligations for any actual supplier.
No complete multiplication theorem, hosted CI pass, or new kappa is claimed.

Prepared by **Ross Richardson (@RossRichardson)** with substantial **OpenAI
Codex assistance**. Apache-2.0. The written argument and second checker
still need external review.
