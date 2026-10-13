# Complex phases cannot improve a fixed-reader P112 single lift

**Research note / scoped negative result; no new kappa.** Every complex
single-lift decoder retaining the eight P112 coordinate readers has a
real single lift with **identical supports and identical individual copy
costs in all nine terms**. Consequently its total pairing-rank copy cost
is at least **64**, just as in the real-coefficient theorem of
[Mihir Srivastava's #845](https://github.com/CrocSwap/integer-mult-bounds/pull/845).

The new [support-transfer theorem](PROOF.md) holds for **any finite real
matrix X**, not only P112. It constructs a real representative by choosing
a real-linear projection that avoids finitely many zeros, and projecting
the **reciprocals** of nonzero source coefficients. It closes #845's
explicit exclusion of complex scalars. It does not change the eight
readers or allow multiple added totals.

## Reproduce

From the repository root, Python 3.10+ and the standard library only:

```sh
python -I -S -B research/p112-complex-single-lift/verify.py
```

This single command checks immutable source hashes, replays **both** #845
finite-premise checkers, verifies the new primary certificate, and runs
the new independent checker against its committed receipt. Its final line
is:

```text
PASS_P112_COMPLEX_SINGLE_LIFT: 14 exact projections; 8 negative controls; identical term costs; floor 64
```

The independent checker imports neither primary checker nor the predecessor
geometry code. It reads a hash-pinned geometry snapshot and uses set-based
binary elimination and scaled-integer matrix identities:

```sh
python -I -S -B research/p112-complex-single-lift/independent_check.py --check research/p112-complex-single-lift/INDEPENDENT.json
```

Its expected marker reports **460 exact cases, 4,140 support pairs, 460 cost
vectors, 56 entrywise identities, and six controls**. Both commands also
work under `-O`; all verification guards use explicit exceptions.

The defaults are read-only. Explicit regeneration is available with
`verify.py --write PATH` and `independent_check.py --write PATH`. The first
still checks the committed independent receipt. `--check PATH` checks an
alternate receipt. JSON comparisons cover every field semantically;
container or newline differences are not mathematical differences.

## Mathematical scope and evidence

The investigated identity is

    XX^T = sum_j x_j (x_j-a_j z)^T + (Xa)z^T,
    a in C^8, z in C^112.

Transpose is algebraic, without conjugation. The cost beta is the inherited
binary label-pairing rank on each term's reader/source supports. The real
representative preserves the **ordered cost vector**, not merely its sum.
With rank-eight X, this includes all exact nine-term factorizations
retaining the original eight reader columns, including nonzero rescalings,
and the corresponding transposed family. [PROOF.md](PROOF.md) supplies the
argument and boundary cases. [REVIEW.md](REVIEW.md) records separate AI
reasoning review; it is not independent human or proof-assistant review.

Finite regression coverage is deliberately distinct from the theorem:

- Primary: every active coefficient count 0 through 8, common/distinct
  complex phases with forced cancellations, a single-port source, and two
  sharp equality examples; 14 P112 cases. Three cases check all entries
  of both complex and real 112-by-112 identities. A separate rectangular
  rational matrix forces cancellations at nonintegral coordinate entries.
- Independent: all 28 coordinate pairs times all 16 ordered coefficient
  choices from `{1,i,1+i,2-i}`; eight imaginary singleton cases; two zero
  boundaries; two full-support cases. All **460** preserve every support
  pair and individual cost. Pair `40 mod 28 = 12` plus the 12 boundary
  cases check all matrix entries: **56 matrices / 702,464 entries**.
- Eight primary and six independent controls cover missing exclusion
  conditions, direct rather than reciprocal projection, omitted or
  corrupted terms, complex conjugation, and binary-rank arithmetic.
- The inherited replay re-establishes 511 support minors, 3,272 sign cases,
  and 128 incompatible kernels. These remain #845's evidence and credit.

Assignment seed **40** was drawn once from OS randomness. It fixes the
primary diagnostic values and the independently selected full-matrix pair.
Every stated finite domain is completed; the stopping rule is completed
coverage, not a failed search or timeout. The arbitrary-complex statement
comes from the written finite-avoidance proof, not from these samples.

## Accounting and limits

Even granting zero extra cost for preparation, source access, frame
changes, restoration and recursive children, scalar-domain freedom cannot
lower the support-based copied-information charge in this mechanism. No
complete improved supplier was advanced. The conversion need not preserve
coefficient sizes, physical schedules, or preparation/precision costs;
possible advantages there remain open.

The physical interpretation inherits #446 Theorem C's separate-total
copy-tree assumptions. Changed readers, several added totals, masked
matrix identities with free corrections, complex underlying geometry and
interacting delivery programs remain outside this result. The general
support-transfer theorem itself does not require the physical interpretation.

## Provenance and handoff

Exact base: `407d52ff15b2217b6e22bce44728b4c3907b6515`. At that base the selected
conditional kappa is `1661960547713947/10^18`, the reviewed #942 T37
construction. Its original assembly and source manifest were consulted;
neither that selection nor `upstream/` is modified. The all-size/compiler,
common-label/mutable-source, hosting, precision/tape and analytic obligations
remain inherited.

[SOURCES.json](SOURCES.json) pins all ten inherited input files by SHA-256
and Git blob at the exact base. The package depends on those repository
files in place, not on a mutable PR head or network access. Read
[NOTICE.md](NOTICE.md) for attribution to #845, DreamingOfClouds #717/#446,
Joel Pulikkan / GamingPuzzled #620, and construction predecessors.

The [claim](CLAIM.md) records candidate selection, the method refinement,
coordination and overlap checks. The adjacent #968 work concerns exact
eight-term frame-pair decoders; it is credited as related work, not used
as a premise. This package contributes a scalar-domain transfer for a
ninth term with eight retained readers.

Validation evidence is in [VALIDATION.json](VALIDATION.json). The isolated
package and selected-record check are the relevant checks; the unrelated
repository-wide suite and selected-supplier cold replay are not rerun.
No full multiplication theorem or hosted-CI success is claimed.

Prepared for **@woklerx** with substantial **OpenAI Codex** assistance.
Apache-2.0.
