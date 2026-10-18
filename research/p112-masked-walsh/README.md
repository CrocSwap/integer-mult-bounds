# Two masked Walsh totals cannot improve P112's copy bill

**Scoped negative result; no new kappa.** Two source totals cut from a Walsh
pair do leave the original coordinate column space, but this family still
costs at least **72**, against the original **64**, for every real coefficient
matrix with two nonzero columns. If both masked sources are nonzero, the
certified lower bound is **77**. These are lower bounds, not claims that the
continuous optima are attained.

The separate complete census of 572,320 small unimodular cases has exact minimum
72, or 78 when both sources are nonzero. Its cost distribution is
`{72:672, 73:448, 78:28672, 79:288064, 80:254464}`.
The written reduction below, plus exact finite premises, establishes the
all-real statement; a failed search is not its proof.

## Reproduce

Python 3.10+ and the standard library suffice. From the repository root:

```sh
python3 -I -B research/p112-masked-walsh/verify.py
python3 -I -B research/p112-masked-walsh/independent_check.py
```

The first prints
`PASS_P112_MASKED_WALSH cases=572320 minimum=72 baseline=64 no_new_kappa`.
The second independently reconstructs the direct binary pairing matrices,
checks the full census and the continuous-class relaxation, and prints
`PASS_P112_MASKED_WALSH_INDEPENDENT`. Both compare against [RESULT.json](RESULT.json).
`verify.py --write /new/file.json` exports a fresh receipt and refuses an
existing path. [GEOMETRY.json](GEOMETRY.json) is regenerated and checked against
the pinned geometry implementation, not accepted as an unverified input.

## Model and exact identity

Use the P112 model of DreamingOfClouds' [PR717](https://github.com/CrocSwap/integer-mult-bounds/pull/717),
as independently implemented by Mihir Srivastava's
[PR845](https://github.com/CrocSwap/integer-mult-bounds/pull/845).
The scaled E8 roots, frame, labels and dual labels are in GEOMETRY.json.
Write `X=(x_0,...,x_7)`, with entries `0,+1,-1` and `XX^T=2G`.
For reader/source vectors d,t, define

    beta(d,t) = rank_F2 (l_i S l_j^T)_{i in supp(d), j in supp(t)}.

Every original coordinate term has cost 8. For any pair `p<q` and nonzero
functional `h in F2^9`, define doubled masked sources

    Z_i = (x_pi+x_qi) if h.l_i=0, else 0,
    W_i = (x_pi-x_qi) if h.l_i=1, else 0.

Here `x_pi` denotes the i-th entry of column x_p. The actual sources are Z/2
and W/2. Choose real coefficients `ap,bp,aq,bq`, with both columns of
`A=[[ap,bp],[aq,bq]]` nonzero. In particular every real invertible A is allowed.
Put

    Rp = 2xp - ap Z - bp W,       D1 = ap xp + aq xq,
    Rq = 2xq - aq Z - bq W,       D2 = bp xp + bq xq.

Direct expansion gives, for all coefficients,

    xp xp^T + xq xq^T = (xp Rp^T + xq Rq^T + D1 Z^T + D2 W^T)/2.

The other six coordinate terms remain. Thus the complete copy-rank cost is

    C = 48 + beta(xp,Rp) + beta(xq,Rq) + beta(D1,Z) + beta(D2,W).

Zeros are priced as zero, including the constant-odd functional `h=1`, which
gives Z=0 in this label encoding. The sources at `(p,q,h)=(0,1,48)` each
increase rational rank of `[X|source]` from 8 to 9, explicitly escaping the
in-col(X) class. This does not alter the reader-column restriction.

## Why finite support cells cover all real coefficients

Z and W have disjoint supports and entries in `{0,+1,-1,+2,-2}`. At a port
where Z is nonzero, `2x-ap Z-bp W` vanishes exactly when `ap=2x/Z`.
The only possible exceptional values are `{-2,-1,0,1,2}`. Where W is nonzero
the same statement applies to bp. Where both vanish there is no coefficient
dependence. Consequently the six representatives

    E = {-2,-1,0,1,2,3}

cover every residual support: 3 represents *every* real value outside the
five exceptional values. Minimizing beta over E squared gives the true
individual minimum for each residual term.

Similarly every nonzero `a xp+b xq` has one of five supports. If a or b
vanishes it is a coordinate support; otherwise cancellation is possible only
at `a/b=+1` or `-1`, since coordinate entries are 0 or +/-1. Thus the reader
representatives `(1,0),(0,1),(1,1),(1,-1),(1,3)` cover all possibilities.
X has full column rank, so a nonzero coefficient column gives a nonzero reader.

For each pair and cut the verifier adds the **four independent minima** to
48. This deliberately ignores compatibility between the four minimizing
coefficient choices, so it is a lower bound for every actual A. Exact rank
calculations give:

| Lower bound | Number of pair/cut choices |
|---:|---:|
| 72 | 28 |
| 77 | 112 |
| 78 | 7,168 |
| 79 | 7,000 |

All 14,308 choices are covered; the 28 cases at 72 have a zero source.
This proves the stated bounds. No floating point, solver infeasibility claim,
or assertion that all four minima are simultaneously attainable is used.

## Experiment and controls

The original discrete experiment covers all 28 pairs, all 511 nonzero cuts,
and all 40 matrices with entries in `{-1,0,1}` and determinant +/-1. Seed 48
shuffles cut traversal only; stopping is exhaustion, with no early success
exit. The later support-cell refinement is recorded in [CLAIM.json](CLAIM.json).

The first implementation projects labels against a basis of the reader
space. The second imports neither it nor the vendored geometry code and
eliminates the restricted 112-column binary pairing matrix directly. It
checks a full 112-by-112 endpoint identity for one minimizer of each pair.
The generic identity above covers all coefficients; these are finite controls,
not a proof-assistant verification of the multiplication theorem.

Controls include the cost-64 coordinate baseline, zero terms, dependent binary
rows, a corrupted residual, an omitted added total, the unmasked Walsh cost
66, rational support cells, and a witness that coefficient 2 must not be
treated as generic. Package tests reject changed geometry/source/receipt bytes
and preserve existing export files. See [VALIDATION.md](VALIDATION.md).

## Cost scope and prior work

This tests an explicit attempt to reduce copied information with two added
totals. It assumes the separate-total additive pairing-rank interpretation of
DreamingOfClouds' [PR446](https://github.com/CrocSwap/integer-mult-bounds/pull/446).
Granting zero extra preparation, source access, frame changes, helpers,
restoration and recursive children still leaves this copy bill above 64.
No candidate reaches the point where a complete physical invoice could help.
This excludes copy-rank improvement by this mechanism; it does not exclude
improvements to other costs, alternative recursive rank distributions, other
masks, dense eight-coordinate reader changes, arbitrary source corrections,
masked fitting-matrix completions or interacting delivery programs.

PR620 (Joel Pulikkan / GamingPuzzled) and predecessors supplied the baseline
64. PR717 gives the model, eight-term/gauge obstruction and open mixed-beta
problem. PR845 rules out one arbitrary added total with fixed coordinate
readers. This contribution permits two sources outside col(X), but fixes their
masked-Walsh form and limits modified readers to two coordinate columns. It
does not close the general two-total or mixed-beta problem. No worldwide
priority is claimed for the support-cell method.

Concurrent work checked again on October 14: Philipp / @mightyOil's
[PR1197](https://github.com/CrocSwap/integer-mult-bounds/pull/1197)
excludes two-total savings when added-reader **coefficient** supports are
disjoint, among other cases. Here the two coefficient columns can both use
`{p,q}`; the disjoint row supports of Z and W do not satisfy that hypothesis.
This package gives a quantitative result for an explicit subfamily of the
overlapping-reader case it leaves open. @thakrarsagar's
[PR1327](https://github.com/CrocSwap/integer-mult-bounds/pull/1327)
studies two-sided parity lifts; its strengthened floor requires off-root-code
columns on both factors, whereas all our reader columns remain in col(X).
These are adjacent obstructions, not dependencies of our proof.
[PR1191](https://github.com/CrocSwap/integer-mult-bounds/pull/1191)'s one-sided
mask rigidity reduces masked exactness to all-pairs exactness in its class;
our identity already holds on all pairs. The free-rectangle mechanisms of
[PR1375](https://github.com/CrocSwap/integer-mult-bounds/pull/1375),
[PR1460](https://github.com/CrocSwap/integer-mult-bounds/pull/1460) and
[PR1473](https://github.com/CrocSwap/integer-mult-bounds/pull/1473) change a
different factorization. The added evidence here is the all-pair/all-cut
72/77 certificate, discrete histogram and independent direct-pairing replay;
no general decoder impossibility or priority over those works is claimed.
Their exact heads and other inspected contributions are in OVERLAP.json.

## Open next questions

Can compatibility among the four minimizing coefficient choices sharpen the
continuous 72/77 bounds? A bounded first step is to evaluate the full cost on
compatible residual/reader support cells for one pair and a minimizing cut.
The blocker is tracking reader-ratio and residual-value constraints together;
the current independent-minimum certificate does not assert attainability.
This would refine the obstruction, not produce a cheaper supplier.

Changing the source masks or allowing dense readers could escape this family.
A useful first step is to specify one such class outside the pinned concurrent
obstructions and derive its optimistic complete cost before a new search.
No claim about that broader class follows from this package.

Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. At that base the selected
conditional result is #799 with #589/#555, κ=`1661634653669567/10^18`.
The selected certificate, X4 construction note and maintainer review were read;
no historical or pending headline was used as the accepted frontier.
[SOURCES.json](SOURCES.json) pins consumed source bytes and predecessor heads.
At the final pre-submission refresh, main was `5e554ff58d01921747d27177045c0061f31e1ad1`
and selected #1094 at κ=`0.001672660197076918`. The pinned P112 geometry and
both consumed predecessor heads were unchanged. [OVERLAP.json](OVERLAP.json)
records the October 13 and October 14 overlap checks, including the newer
two-total, parity-lift and free-rectangle work.
The selected frontier and `upstream/` are unchanged. Inherited all-size,
compiler, physical/hosting, precision/tape and analytic assumptions remain.

Prepared for **Denis (@just-mn)** with substantial **OpenAI Codex assistance**
in experiment design, mathematics, implementation, independent AI replay and
writing. No independent human review or formal multiplication proof is claimed.
Apache-2.0; predecessor notice and unmodified source are retained in `vendor/`.
