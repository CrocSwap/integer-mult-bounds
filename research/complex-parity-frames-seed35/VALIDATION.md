# Validation and access receipt

Local checks completed on 2026-10-13, macOS / Darwin arm64.

| Check | Result |
|---|---|
| `python3 -B research/complex-parity-frames-seed35/check.py` | PASS, Python 3.15.0 |
| Same checker with `-I -O -B` | PASS; checks do not depend on assertions or import paths |
| `/usr/bin/python3 -I -O -B .../check.py` | PASS, Python 3.9.6; agrees with 3.15.0 |
| Separate RREF producer compared to committed certificate | Exact JSON equality |
| Closure enumerator | All 2,825 distinct subspaces; dimension counts `1,63,651,1395,651,63,1` |
| Independent nondegeneracy and residual checks | Gram-rank tests and explicit orthonormal bases; 1,378 nondegenerate frames |
| Finite domain | All 36,100 pair-of-pair choices, 1,890 orthogonal rectangles, 1,170 scalar-rank-one rectangles, 900 admissible |
| Corrupted certificate: admissible count +1 | Rejected, exit 1 |
| Corrupted certificate: source-degenerate class allowed at dimension 3 | Rejected, exit 1 |
| Corrupted certificate: all-record digest replaced by zeroes | Rejected, exit 1 |
| Relocated package in a directory with spaces, launched from `/private/tmp` | PASS in isolated optimized Python 3.9.6 |
| Python syntax and JSON parsing | PASS |

The two enumeration methods agree on the SHA-256 of every rectangle's ordered
labels, scalar-rank flag, common-span flag, separating dimensions and admissible
dimensions, serialized as documented in the programs:

```text
b1faf1d105cf5e6681d856873e9209cc04b87f9b52041e3944e5132aac32cc52
```

Mathematical controls reject a degenerate frame, a scalar-exact separating
frame with an alternating residual, a violated target boundary, and an
incorrect scalar sign / rank-two scalar matrix. Positive controls include
the dimension-four completion and examples in dimensions eight (general
norm-one labels) and ten (triple labels). The latter are controls, not wider
completed searches. The discarded exploratory dimension-eight triple search
found no candidate among 651 distinct rank-four completions of sources
`(7,25)`; this unsuccessful fixed-source search is not used in any theorem,
census or certificate claim.

The replay takes well below one second in this environment. No performance
improvement or cross-platform runtime claim is made. Python 3.11 itself was
not available for a separate run; the documented minimum follows the
repository convention, while the actual tested versions are named above.

## Checks not available

The initial `git clone` failed with `Could not resolve host: github.com`.
`gh auth status` reported no GitHub login. A local addition-only Git branch
was initialized for packaging; it does not contain the upstream base tree.
The intended base and source heads in `SOURCES.json` were read via the
browser, not verified as local Git objects.

`make verify` was attempted once and returned exit 2, `No rule to make target
'verify'`, because the upstream Makefile and full checkout could not be
obtained. This is an unavailable integration check, not a failed mathematical
test or a repository-suite pass. No selected cold replay, source-inventory
verification, hosted CI, Lean build, complete supplier invoice, or exact-base
patch application is claimed. The selected construction was not changed.

The public PR list and issue list were refreshed before handoff. The available
cached list still displayed arrivals through #702; #704 (review-ledger tooling)
was visible as a cross-reference, but its page could not be retrieved. #698's
body confirms that it concerns fixed CK B-phase frames and a paid moment,
distinct from this historical triple-decoder completion problem. No matching
parity-frame completion was found in the accessible material. This was not
an exhaustive current-head queue audit. No pinned coordination issue was
visible, and no comment, issue, pull request, merge or closure was performed.

Research selection occupied less than the first eight minutes of the planned
40-minute budget. The finite result and writeup were complete before final
verification/packaging; verification began early rather than waiting for the
reserved final ten minutes. The local claim is updated once with the result.
