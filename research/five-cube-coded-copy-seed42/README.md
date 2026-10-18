# Exact affine five-cube copy floor, with four rank-eight terms

**Research note / scoped negative result. No new kappa or physical supplier.**

Ross Richardson's PR958 excludes coded coordinate-star combinations from
its five-port quadratic obstruction. This package resolves that gap for
the smallest case, `p=k=5`, including arbitrary finite overcomplete affine
factorizations of the full decoder matrix.

The exact algebraic copy-rank sum is at least **32**, equal to the 32 ports.
The decoder has binary rank **two**, even though its ten coordinate-star
observations span **six** dimensions. A two-parity-total witness costs
`16+16`; a different four-total witness costs `8+8+8+8`. The latter attains
both the minimum sum and minimum possible peak pairing rank. These are
objective values, not a paid physical COPY realization.

Under the inherited additive stage ledger, even granting every other cost
zero leaves `D <= (s-1)*32-s*32 = -32` at every `s>=3`. Coded totals therefore
cannot make this cube admit a positive saving in that model. This does
not extend PR958's larger-p ceiling to coded totals.

From the repository root, Python 3.10+ and the standard library:

```sh
python -I -B research/five-cube-coded-copy-seed42/verify.py
python -I -B research/five-cube-coded-copy-seed42/independent.py
python -I -O -B research/five-cube-coded-copy-seed42/test_package.py
```

The first expected marker is:

```text
PASS_FIVE_CUBE_CODED_COPY pairs=3969 copy_floor=32 peak_floor=8 witnesses=2 controls=8 pins=6 no_new_kappa
```

The second checker independently reconstructs every rational rank with
integer elimination, rather than importing the modular implementation.
Both support optimized Python (`-O`) and compare the complete rank table
against the committed certificate. The package checks exercise source and
rank corruption rejection, omission, optimized relocation to a path with
spaces and preservation of an existing output. The exact finite facts and proof are
in [PROOF.md](PROOF.md); [CERTIFICATE.json](CERTIFICATE.json) contains all
3,969 ranks, both witnesses, budget bounds and negative controls.

Optional reduced-factor enumeration:

```sh
python -I -O -B research/five-cube-coded-copy-seed42/independent.py --exhaustive-factorizations
```

This corroborates the lower proof with every distinct-reader factorization
in the reduced two-/three-dimensional containing spaces for two through
five terms. Its complete domain and stopping rule are recorded in the
independent receipt. It is not an unrestricted enumeration of all longer
factorizations. `--write-certificate PATH` writes an exclusively created
receipt; existing files are never overwritten.

The committed [INDEPENDENT.json](INDEPENDENT.json) records 1,687 distinct
reader subsets, 1,324,327 complete source assignments, and 1,226,104
assignments with every source factor nonzero. Reduced-span minima for
two through five terms are 32, 35, 32 and 43. Only exclusion below 32 is
promoted to the global theorem; these per-term-count minima are scoped
to the reduced search. [VALIDATION.md](VALIDATION.md) records the checks.

Exact base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`. OS-random assignment
seed **42**, structural decoder track. [CLAIM.json](CLAIM.json) records the
three considered tasks and overlap checks. [SOURCES.json](SOURCES.json)
pins six original text/JSON inputs by SHA256 and Git blob, retained verbatim.
The selected record at the base is conditional
`kappa=1661960547713947/10^18`; it and `upstream/` are unchanged.

The result is restricted to the displayed rational Gram, affine-code
source and reader supports, full matrix exactness and additive copying.
Gather, frame, restoration and recursive implementation remain open.
This finite theorem is not a proof-assistant verification or a proof of
the full multiplication theorem. No hosted CI or measured runtime gain
is claimed.

Credit **Ross Richardson (@RossRichardson), PR958**, for the quadratic
geometry and separate-star ceiling; **Joel Pulikkan (@GamingPuzzled), PR231**,
and **icekylinx/eumemic** for the paired-port decoder; and **DreamingOfClouds,
PR446/595**, **Jacob Sussman** and **Zhihao Chen** for the inherited copy/frame
and accounting lineage. See [NOTICE.md](NOTICE.md) for pins and related work.

Prepared for **@martinxxx9** with substantial **OpenAI Codex assistance**,
including a separate AI worker's exact-rank reconstruction and review.
No independent human review is claimed. Apache-2.0.
