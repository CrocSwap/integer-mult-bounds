# Executed validation

Executed on Linux, 2026-10-13, with CPython 3.14.4 and CPython 3.12.3,
GCC C++ 15.2.0, C++17 and Boost 1.83 headers. Boost was extracted outside
the repository from Ubuntu `libboost1.83-dev_1.83.0-5ubuntu5_amd64.deb`, SHA256
`c17abc5a40a074c3d959655191ebec1561fa25f14f4948f6788be49417d4b234`.

## Complete replay

The normal isolated CPython 3.14.4 verifier passed against the entire frozen
EXPECTED.json. The optimized `-I -O -B` CPython 3.12.3 verifier also passed
from an unrelated working directory, using only this package and the 14
declared main-source files. The minimal closure had no Git metadata and its
path contained spaces. All input files/directories were made read-only; all
outputs were placed elsewhere. Default verification imported no NetworkX.

Both complete mathematical receipts are identical, canonical SHA256
`3296fcf8afeefd2f15eeea4fbd3a769dbcf95275ea2b9e2795c69a2a396adcd4`.
Each includes:

- Every one of 96,141 undirected edge inequalities, covering 192,282
  orientations, with 1,885 positive edges and 347 tight dual inequalities.
  The 439 vertex prices and 19 odd-set prices give doubled objective 2,520;
  the explicit witness has saving 1,260.
- Set-valued reconstruction of the fixed target basis and all three
  arithmetic-optimum matchings. Every complete word and all 598 single-pair
  deletions are repriced: 601 cases, 17 admitted, 14,390,692 literal positive
  instructions across both orientations.
- All 439 helper unit columns for the secondary discovery proxy, separately
  evaluated from literal suffix instructions.
- Both regenerated word payloads and every certificate field, including
  the adverse arithmetic-floor calibration.
- All 48,729 direct four-term coefficients for the selected candidate,
  including 7,343 nonzero mixed-term entries.
- All 661 separate D input columns in both directions for five complete
  words: PR589, PR915, PR926, the floor calibration and the candidate.
  The unmodified full E8/frame/endpoint checker also passes each word.
  Original H2 and literal K extraction remain false for the four changed
  words, with every other hypothesis and conclusion true.
- Fresh compilation of unchanged native legality and 5/9/11-stage checkers.
  All five words pass their local 104-bit checks on 883/1,327/1,549 formal
  columns, with all 240 omitted-bridge controls rejected. Full MOVE paths,
  COPY/ERASE records, paid histogram and rank mass agree.
- Native/literal ADD counts and both positive maxima agree. The separately
  source-bound nine-stage expression rejects the floor calibration at
  193 bits and admits the selected candidate at 192 bits.
- Nineteen local mathematical rejection controls and the paid neutral
  helper-pair positive control. Eight package tests pass on each interpreter.

The optional nomination was also rerun with NetworkX 3.6.1, whose matching
function source hash is checked in nominate.py. It reproduces every field
of NOMINATION.json, including all three matchings, the dual, proxy columns,
601 priced alternatives and selection. Source-hashed solver introspection
is discovery machinery; the default proof checker validates its output by
integer inequalities and actual circuit replay.

## Base refresh and scope

Research began at `91a2094f2e022930069e8cfdc810a3ea1b81cd09`, selecting PR799.
During final validation, main advanced to
`47481c89fd30a43f8f882eb4b391e89c29273fd0`, selecting the reviewed PR890
conditional κ = 0.001661957774647029 and retaining PR589. The branch was
rebased before publication. All 14 mathematical/tool inputs are byte-identical
on the new base and their pins pass after rebase. No executable, recipe or
receipt changed during that alignment; only contextual base metadata and
documentation changed. The full replays above therefore apply to the same
consumed bytes. `make selected-record-check` passed before and after rebase.
The scoped staged whitespace check also passed.

The instructions gist remained at
`4180bf0d4045ffdcd12d75bb1fec91c234420162`. The final queue snapshot contained
708 open PRs through PR937. PR817, PR915 and PR926 retained their pinned
heads. No competing matching certificate for this frozen R439 helper graph
was found. PR933 changes the gate-order/frame search class, with D fixed;
PR936 extends PR904's phase-A window synthesis. Their savings are not composed
here. PR928's proposed directory standard was not part of main. No pinned
sprint coordination issue existed, so the claim is local.

The result establishes the exact arithmetic floor only for the stated
disjoint-helper recipe class. Its precision-constrained optimum remains
either 11,948 or 11,949 ADDs. The three rejected floor nominations do not
exclude another feasible optimum. Native local success does not discharge
the failed nine-stage charge of the adverse calibration.

Semantic D acceptance, changed whole-hosted emission/audit, complete
finite/precision invoices and outer assembly remain integration work.
Common-label realization and analytic assumptions remain inherited.
No full repository suite, selected-supplier cold replay, formal full
multiplication theorem, new exponent, measured runtime improvement or hosted
CI success is claimed by these local results.
