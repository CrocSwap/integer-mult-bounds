# Independent prefix audit of PR2287's exact Gaussian grid

This package checks the arithmetic bridge in Jose Manuel's pending
[PR2287](https://github.com/CrocSwap/integer-mult-bounds/pull/2287), pinned at
`8c60765b5dea9d862b3b190d55da102a576031bf`. Its construction uses one root grid
through recursive complex children. The contribution here is a quantified
proof for its actual word primitives and independent exact boundary tests.
We find no primitive arithmetic defect under the stated hypotheses.

The [proof](PROOF.md) separates three requirements: enough fractional reserve
at every intermediate operation, signed headroom for its actual intermediates,
and a legal shift extent. Completed-child cancellation can restore divisibility
without changing representation. A correct final endpoint alone does not
establish these prefix conditions.

## Result and added coverage

For incoming height `t` and reduced dyadic scalar `n/2^k`, the actual Horner
implementation and scalar ADD need at most `t+max(bit_length(abs(n)),k)`.
The predecessor's scalar charge `2*bit_length(abs(n))+k+4` dominates this
bound. A C or inverse-C pair needs prefix height at most `t+2`, although its
completed endpoint needs only `t+1`. Normalization by `((1-i)/2)^D` needs
at most `t+ceil(D/2)`. These are written quantified lemmas, not conclusions
extrapolated from finite enumeration.

Three exact examples explain the boundary:

- On eight signed bits, `60*(3/2)=90` fits, but Horner first forms `180` and
  must reject. Additional intermediate headroom makes the same calculation pass.
- For `a=(5-5i)/8`, `b=(5+5i)/8`, the C kernel's first numerator is `5/2`
  while its completed first output is `5/4`.
- Zero has height zero, but `Grid(3,0).scale(0,1/8)` still rejects because
  the required shift has extent three. Value bounds do not replace `k<w`.

The predecessor already checks sample C/inverse, scalar and normalization
executions and one rounded-return failure. This audit adds a separately
implemented integer/rational oracle, exhaustive signed-word boundaries,
complete quarter-grid Gaussian unit-disk pairs, actual primitive prefix
observations, and nested cancelled-shear returns. The fixed-grid rounding
failure is credited to PR2287; the proof states its all-precision family.
PR2313's Gaussian recovery and the live wider-chunk outer-transfer work address
different interfaces.

Gareth Davidson's incorporated [PR1282](https://github.com/CrocSwap/integer-mult-bounds/pull/1282)
already accounts for signed R480 prefix norms, Horner scratch and partially
stored components. Its Horner monotonicity argument is credited prior work;
we do not repeat its whole-word maxima or claim that endpoint-only warnings
are new. This package checks the later PR2287 bit-word implementation,
denominator/divisibility conditions, legal shifts and completed-child grid
behavior, which PR1282 explicitly leaves outside its fixed-point scope.

The committed [receipt](RESULT.json) records:

| Coverage | Count |
|---|---:|
| Every signed addition on word widths 4 through 8 | 87,296 |
| Signed negations / valid-extent divisions | 496 / 3,552 |
| Overflow / nonintegral-division rejections | 21,829 / 2,570 |
| Reduced dyadic scalars / scalar input cases | 59 / 1,947 |
| C/inverse-C unit-disk input pairs | 4,802 |
| Normalization cases across 22 dimensions | 1,078 |
| Nested completed-child returns, depth up to four | 20 |

The nested fixtures use three outer rows and correlated dirty helpers, execute
the actual retained primitives, and check 25,284 intermediate primitive
operations. They are deliberately bounded compositions, not execution of the
selected R480 supplier. Removing the exact-division or overflow guard from an
in-memory subject is detected by the independent oracle. Corrupting retained
source bytes is rejected by the same authentication routine used before imports.

## Reproduce

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 scripts/research_package.py --package research/complex-grid-prefix-audit
```

The registered hook runs the direct audit normally and with `-O`:

```sh
python3.12 -I -B research/complex-grid-prefix-audit/verify.py
python3.12 -I -O -B research/complex-grid-prefix-audit/verify.py
```

Default replay writes no artifacts and compares the complete computed receipt.
`--emit NEW_PATH` explicitly writes a new receipt without overwriting an existing
file. Six retained source files are unchanged snapshots with SHA256 and Git blob
pins in [SOURCES.json](SOURCES.json). Their path-to-commit correspondence was
checked with Git during preparation; offline replay checks their pinned bytes,
not live GitHub state. The subject implementation is imported for testing;
expected arithmetic values do not come from its checker or producer.

Local validation used CPython 3.12.11 on Windows. Hosted CI is separate.
The [task card](TASK.json) records the revision-4 assignment, exact base,
overlap and [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2253#discussioncomment-18941296).

## Open next questions

Does the complete chronological selected program satisfy all the prefix-height
and shift-extent premises? An independent reviewer can begin with PR2287
section 6 and bind each scalar, remainder kernel, completed child and parked
value to its proposed height recurrence. Full native and hosting identities
remain a blocker to complete supplier admission; this primitive audit does
not resolve them. The structured question is in `TASK.json`.

There is no new moment, supplier adoption, selected-frontier change, complete
payload execution, tape/stock/time proof, or Lean multiplication theorem here.

## Credit and license

Jose Manuel (`jmbarrancoml`) supplied PR2287's construction, arithmetic code,
existing controls and precision proposal. Its retained [NOTICE](sources/pr2287/NOTICE.md)
preserves the selected supplier and dependency lineage. Gareth Davidson
(`bitplane`) supplied PR1282's earlier prefix/Horner analysis. AAAmirinu's contribution
is this independent proof/audit package, prepared with substantial OpenAI Codex
assistance in mathematics, implementation, writing and separate-agent review.
No independent human or formal-kernel review is claimed. Apache-2.0.
