# Reflecting roots removes the extra inverse-gap power

For a polynomial P of degree n with a certified unit-circle lower bound
delta>0, this note proves

\[
\|P(\tau Z_L^w)^{-1}\|_\infty\le(1+4n)^2/\delta
\]

uniformly over length, stride, and unit phase. Interior roots are permitted.
Root reflection, the classical Dolzhenko-Spijker arc-length inequality,
and a self-contained Hardy coefficient estimate replace the derivative
bound used in our previous audit. The linear inverse-gap dependence is
necessary even at degree one; optimality of the degree factor is not claimed.

Applied to Ali Romman's incorporated PR621, the dominant logarithmic term
in the sufficient norm bound is half the original and two thirds of our
previous bound. This remains O(r^2 phi(r)). It is not a faster algorithm,
a complete working-precision guarantee, or a new kappa.

Exact ceilings of log2 of the sufficient norm constants illustrate the
change. These are bound sizes, not working precision or measured norms.

| Radix | PR621 | Previous audit | This application |
|---:|---:|---:|---:|
| 3 | 28 | 21 | 19 |
| 9 | 870 | 651 | 441 |
| 25 | 23,997 | 17,992 | 11,999 |
| 71 | 695,757 | 521,801 | 347,859 |

## Review and reproduce

Start with [the source and analytic audit](audit/README.md), which responds
to the PR803 review at `d213ac12d4a1ab8f717d942e844df318ceb395fb`.
It records the classical source locators, normalization, all-frequency
proof steps, and outstanding independent-review obligations. Read
[PROOF.md](PROOF.md) for the expanded argument, then run from the repository root:

```sh
python -B research/rational-circle-bound/verify.py
python -B research/rational-circle-bound/test_package.py
```

Python 3.10+ and only the standard library are required. Expected verifier
marker: `PASS_RATIONAL_CIRCLE_BOUND`. The default run checks immutable
source hashes, package hashes, and exact equality with `EXPECTED.json`.
An explicit `--emit NEW_PATH` writes a new receipt, refusing overwrites;
this mode checks source identity but skips package/expected comparison.

The finite coverage is declared, not a proof of the analytic inequalities:

- 126 exact rational root families, including mixed roots, multiplicity,
  zero roots, and near-circle roots; 756 exact boundary identities.
- 546 independent dense versus finite-geometric cyclic inverse comparisons,
  including zero and noncoprime strides; 9,516 inverse entries agree.
- 6,565 finite Hilbert-matrix inequalities, including all pairs of the
  81 length-four vectors in {0,1,2}^4.
- 128 exact near-circle parameter instances, with geometric-tail identities
  and witnesses showing the inverse-gap power one is necessary.
- 14 exact prime-power budget comparisons and 21 admission/shortcut controls.

See `VALIDATION.md` for the actual platform, package fault tests, and limits.
The cyclic oracle is the standard finite-geometric identity, also used by
Ryan Pinto (@Ambassators) in PR692; it is not a new solver.

## Scope and provenance

This adds only `research/rational-circle-bound/`. The selected result,
upstream sources, and original algorithms are unchanged. Base:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. The local worktree starts from
an explicitly partial snapshot of pinned text inputs because a network
clone was unavailable. The final patch contains only new paths and can
be applied to a full checkout at that upstream base.
The publication commit uses the complete upstream tree and that upstream
commit as its parent.

The package's `.gitattributes` preserves exact bytes across Git checkouts.
When applying the standalone patch on Windows, use
`git -c core.autocrlf=false apply /path/to/integer-mult-rational-circle-bound.patch`
to prevent conversion before those new attributes are installed.

`SOURCES.json` pins six byte-exact source/context files and cites the
classical literature. The previous unpublished audit is included for
comparison; the new proof does not depend on that audit. `CLAIM.json`
records the alternative candidates and overlap review.

This is a new application relative to the inspected repository work, not
a claim of mathematical priority. In particular PR628 and PR764 address
rounded scans. Their per-factor margins, precision recurrences, and paid
costs have not been improved merely by proving this operator bound.
Concurrent PR796 computes nonarchimedean root valuations; it does not
supply a complex conditioning bound and is distinct from this application.

## Open next questions

- Independent analytic review: check the implication map and source normalization
  in `audit/README.md` against `PROOF.md`; finite tests cannot settle this.
- Rounded implementation: determine whether the norm estimate improves a specific
  precision recurrence, with all preparation, restoration and routing charges.
  The analytic theorem alone does not provide that implementation.

Prepared for Rafael Guevara (@alephnan) with substantial OpenAI Codex
assistance. Apache-2.0. See `NOTICE.md`.
