# Three arbitrary-support totals on the quadratic five-cube

**Research note / scoped negative result. No new kappa or physical supplier.**

For the 32-port quadratic Gram introduced in PR958, permitting non-affine
port masks lowers the exact **three-total** decoder objective from 35 to
32. A full decoder witness has source sizes 8,24,8 and pairing ranks
**8 + 16 + 8**. Messages remain linear XOR totals of input data; the masks
are non-affine functions of the port index.

Every factorization of the full decoder into at most three arbitrary
binary outer products costs at least 32. Every cost-32 three-term solution
has peak rank 16. For canonical distinct parity/full readers, equality
occurs precisely for the 131,068 nonempty proper masks contained in one
parity class. The proof reduces the entire support domain to two
orthogonal bases; it does not extrapolate from a finite search.

This extends a boundary explicitly excluded by **martinxxx9's PR1046**.
That predecessor already attains total 32 with two affine totals and with
four affine totals of peak eight. We improve neither of those optima.
The new result is the exact three-total boundary after changing the
support class, including its equality and peak classification.

Under the inherited additive copy/stage ledger, the optimistic complete
budget still has `D <= (s-1)32-s*32 = -32` at every `s>=3`. Even free
source access, gathers, frame changes, helpers, restoration and other
required work cannot give this class a positive deficit. No construction
work or kappa improvement is justified by the algebraic 35-to-32 change.

## Reproduce offline

Python 3.9+ and the standard library, from the repository root:

```sh
python3 -I -O -B research/five-cube-three-totals/verify.py
python3 -I -O -B research/five-cube-three-totals/independent.py
python3 -I -O -B research/five-cube-three-totals/test_package.py
```

The primary marker is:

```text
PASS_FIVE_CUBE_THREE_TOTALS masks=65535 arbitrary_min=32 affine_min=35 equality_peak=16 no_new_kappa
```

The first command checks the complete committed [certificate](CERTIFICATE.json).
The second checks its separate [receipt](INDEPENDENT.json), using literal
coordinate-set intersections and `Fraction` elimination, without importing
the primary implementation. The third runs nine test groups, including
isolated relocation, read-only replay, source/receipt corruption, omitted
coverage, and an off-diagonal decoder error that passes a diagonal test.
Both checkers accept `--write-certificate NEW_PATH` for an exclusively
created receipt; ordinary verification does not modify files.

[PROOF.md](PROOF.md) gives the precise theorem, source/reader reduction,
exact cost formula, exhaustive affine reduction and cost boundary.
[VALIDATION.md](VALIDATION.md) records environments and unrun checks.
[SOURCES.json](SOURCES.json) binds seven retained evidence files by Git
blob and SHA256. No predecessor executable code is imported.

## Completed finite coverage and limits

- All 433 reduced affine three-term templates: 61 distinct-reader and
  372 repeated-reader templates. The written rank reduction makes this
  exhaustive up to transposition and term permutation.
- All 65,535 nonempty masks in the coordinate-1-zero slice, selected by
  `46 mod 5`. Exact integer ranks give minimum 32 and 510 equality masks.
  The ordered complete price digest and histogram are in the certificate.
- Separate dense rational checks for 319 reproducibly chosen masks,
  all 189 parity-reader/affine-source pairs, and representatives of every
  equality cardinality. Sampling is corroboration, not a proof premise.
- Literal decoder identities for all 131,068 canonical equality masks.
  Their general ranks follow from the proved orthogonal-clique structure.
- Ten primary mathematical rejection controls. The separate checker
  supplies a valid changed-Gram example with mixed-parity equality and
  ranks 15,15,2: dense cross pairings are necessary for our equality/peak
  classification. The floor itself has a broader orthogonal-basis proof.

Four or more arbitrary-support terms, larger cubes, changed Gram pairings,
masked identities, nonlinear/interactive data messages and different
copy/stage accounting remain outside scope. Neither mask construction nor
pairing-rank attainment proves an actual gather/COPY implementation.
All-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape, bit H1-H5 and analytic obligations remain inherited.
This is a written finite proof with executable evidence, not a formal
multiplication theorem or independent human review.

Exact base: `c0e3631dc24e3c24a861f7d3d79e0608481cccec`. Assignment seed 46,
structural decoder track. At that base the selected conditional result is
PR1094, `836330098538459/500000000000000000`. The selected record and
`upstream/` are unchanged. [CLAIM.json](CLAIM.json) records candidate
selection, live overlap checks and the local claim; no pinned sprint
coordination issue existed.

Prepared by **Ross Richardson (@RossRichardson)** with substantial
**OpenAI Codex assistance** in mathematics, code, verification and writing.
See [NOTICE.md](NOTICE.md) for predecessor credit. Apache-2.0.
