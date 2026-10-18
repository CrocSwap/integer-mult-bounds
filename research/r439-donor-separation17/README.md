# Short donor certificates for the R439 509/521 exclusions

PR891 already excludes whole-block single-write programs for frames 509 and
521. Four source-derived integer inequalities explain these two previously
DP-only exclusions without reasoning about realization order. The key is to
treat each donor's entry and final rows as mutually exclusive alternatives.

For example, frame 509's wire 468 requires coefficient 3 on input wire 33,
but all legal donor choices supply at most 2. For frame 521's wire 32,
coefficient(42)-coefficient(10) requires 2 but donor supply is at most 1.
[PROOF.md](PROOF.md) gives these and the other two witnesses, their class
assumptions, and the standard separating-functional argument.

From the repository root, Python 3.11+ standard library only:

```sh
python -I -O -B research/r439-donor-separation17/verify.py
python -I -O -B research/r439-donor-separation17/independent.py
python -I -O -B research/r439-donor-separation17/test_package.py
```

Expected: 23 rows, 6,118 tested functionals, four separated rows and six
mathematical controls; independent enumeration of all grouped donor choices
with four infeasible rows and 58,320 dual assignments; one relocated replay
and six package controls. The main verifier regenerates and compares every
field of [EXPECTED.json](EXPECTED.json). `--write-certificate /new/path.json`
creates an output exclusively. All consumed source entries must be present
and match [SOURCES.json](SOURCES.json). Text hashes normalize CRLF to LF;
the immutable gzip is pinned byte for byte. The selected snapshot is fixed
context and does not depend on future movement of the selected pointer.

The old exclusion is credited to Aaron Wang (@navinor), PR891; its original
valid coordinate supply test is only too coarse to expose these witnesses.
This is a simpler independent explanation, not a claim to have discovered
the exclusions. Multi-write programs, repeated donors, subtraction and
F2-only resynthesis remain outside the restricted model. No circuit, gate
saving, supplier admission or new kappa is claimed. No native toolchain is
required or used. The whole supplier's H1-H5 and physical/analytic obligations
are unchanged. See [NOTICE.md](NOTICE.md), [OVERLAP.json](OVERLAP.json), and
[VALIDATION.md](VALIDATION.md).
