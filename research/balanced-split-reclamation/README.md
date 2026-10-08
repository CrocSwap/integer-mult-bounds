# Coarse-threshold and coordinate refinement on anchored split frames

The selected finite construction gives the conditional bound

\[
T(n)=O\bigl(n(\log n)^{1-\kappa}\bigr),\qquad
\kappa=\frac{52062354654791}{10^{18}}
=5.2062354654791\times10^{-5}.
\]

This is **0.0568021906% above the complete PR82 witness** frozen at
`3410b940aa26e5876202152dfa7c4f66451ee22c`. Newer community submissions have
larger reported values. This is a scoped historical comparison, not a claim
to the latest record, global optimality, or measured multiplication speed.
The initial PR77 witness `5.1547855889988e-5` remains reproducible at commit
`83298467291d3bd4b53f76faaef60dbf585be171`.

| Paid quantity | Pinned PR82 | This construction |
|---|---:|---:|
| Roles at h=23 | 27,075 | 27,043 |
| Roles at h=25 | 35,500 | 35,505 |
| Physical width W | 133,289,600 | 133,224,855 |
| Complete recursive rank mass | 76,639,673,100 | 76,602,444,725 |
| Rank deficit | 1,846,900 | 1,846,900 |

The strict bit witness is `26032532642421/(5*10^17)`. The complete old
PR82 child list, evaluated with its own width, has a rigorous lower moment
above one at this saving. The new list has an upper moment below one. Both
the adjacent `10^-18` bit grid point and the next kappa point are rejected.

## Selected construction

Both axes retain the anchored split vector `[1,1,2]`, the original common-point
envelopes, PR74's envelope ordering, and the inherited reversible compiler.
The h23 region schedule is `cover-core`; h25 uses `reverse-node`.

- At h23, a coarse cell `(i,j)` uses column sums when `i+j < ng+1`, and row
  sums otherwise, with zero-based group indices and current group count `ng`.
  This shifts the earlier half-plane boundary by two. At h25, every cell uses
  row sums. Both parenthesizations compute the same disjoint edge sum.
- Independent unit-completion rows are ordered by compatible future uses,
  as in PR79. Three passes of the inherited improving single carry exchanges
  are supplemented by legal two-region carry cycles. The selected words use
  113 such cycles at h23 and 86 at h25. Open two-region reassignment paths
  were also searched; none was selected in these words.
- h23 retains rank-ordered retired candidates and insertion-ordered live
  controls. h25 orders both by actual profile cost against the next use.
- h23 uses the preserved PR82 coordinate flag. h25 uses the point map
  `i -> (i+1) mod 25` in both oracle pricing and the final physical word.
  h23 oracle pricing remains in the original coordinates.

Every selected scalar operation is a literal XOR and every operand promotion,
center copy, endpoint correction, source growth and cleanup is charged.
The score is a deterministic discovery heuristic. Only the complete actual
physical profile decides whether a candidate improves the bound.

The actual width is below `2^27`. The bridge derives wire bits 27, row
coefficient 843 and degree gap `7007/25`; degree 2000, suffix slope 8000,
the complex branch and its scalar charge remain unchanged. Stale width
metadata is rejected.

## Reproduction

From the repository root, using Python 3.11+ and a C++17 compiler:

```sh
make -C research/balanced-split-reclamation verify
make -j1 verify
```

The focused target regenerates both complete words byte-for-byte, checks every
input/target/arbitrary-dirty basis vector in both orientations, reconstructs
actual frame transitions, recomputes the bounded-minor/CRT profiles, and
rebuilds the complete recursive profile and exact certificate. A separately
evaluated rational logarithm/exponential enclosure confirms the accepted and
rejected grid points. All 47 strict assembly constraints and seven margins
are recomputed. Seventeen tests cover malformed or aliased ports, uncharged
canceling scatter gates, omitted children, adjacent-grid rejection, three
stale bridge fields, assertion-disabled Python, and read-only pin help.

`selected/` contains the frozen words, profiles and certificates. `SOURCE.json`
pins consumed sources and deliverables; verification never refreshes it.
An intentional maintainer update uses `python3 pin.py --record`.
`generate.py --output <directory>` writes a fresh reconstruction outside the
selected artifacts. The proof is in [paper.tex](paper.tex) and [paper.pdf](paper.pdf).
Run receipts, including any environmental interruption of the broad suite,
are recorded separately in `VALIDATION.json`.

## Scope and credit

The base theorem, all-size residual/frame compiler, fixed finite-alphabet tape
representation, semantic/analytic reduction, routing, prime setup and exact
recovery remain inherited hypotheses. These are finite checks and a written
conditional argument, not a complete formal multiplication theorem or
independent human expert review.

The initial balanced split/cost-basis experiment and this explicit shifted
coarse rule, coordinate/cost choice, exchange search and reproducible package
were prepared for **huxint with substantial OpenAI Codex assistance**.
Credit eumemic (PR57/69), Avi Eisenberg (PR62), Rohan Garg (PR59), Rohan Arun
(PR65/67/78/82), Dominik Scholz (PR63/68/76), Chafik Boukhalfa (PR60/71/79),
Thomas DiFiore (PR74), Alejandro Zarzuelo Urdiales (PR70), and all earlier
contributors preserved in [NOTICE](NOTICE). Carry exchanges and coordinate
conjugacy are inherited methods; no general novelty claim is made for them.
Original licenses, contributor snapshots and AI-assistance disclosures remain
attached. No contributor endorsement is implied.
