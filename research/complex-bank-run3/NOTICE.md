# Notice and credits — `research/complex-bank-run3`

This package is Apache-2.0, in line with the repository, and changes no existing file. It
vendors two inputs byte-identically and pins them by sha256 (`SOURCE.json`); their licences
and notices are retained with them.

## Vendored inputs

* `references/pr219-run1/` — **PR219**, `research/residual-bank-run1` (head `237067f`). This is
  rung 1 itself: the bit word's rank-22 absorption, the retained-ledger schedule, the exact
  interval-moment engine and the 47-constraint balanced assembly. It is imported, never
  re-implemented, and this package inherits its obligations R1-R4 verbatim.
* `references/pr207-coordinated-crossover.certificate.json` — **PR207**,
  `research/coordinated-crossover-pr200` (head `cd14825`). The frontier certificate: the two
  side child ledgers the ladder is priced against and its published `kappa`. Vendored
  verbatim.
* `references/pr233-source-assisted-v4-layer.certificate.json` and `references/pr233-heads/` —
  **PR233** (chafreaky), `research/source-assisted-v4-layer`. Its layer certificate is a *row*
  for this ledger: on it the complex word's first whole-bank family is rank 3, which is what the
  rank-3 rung of this package is priced on. The branch is **unmerged**, so it is pinned by
  digest -- head `109a857a329d18ed5552d5573f17ddfa886ae57f` — and the branch's earlier heads are
  vendored beside it, because the stability measurement is taken against them and a measurement
  that had to re-fetch a branch could not be re-run in a clone. This package reads only the
  certificate and prices on it; nothing of PR233 is re-implemented, and no part of its claim is
  restated as new.

## Mechanisms this package uses but does not own

* **Rung 2 and the ceiling argument** — PR224, `research/complex-bank-run2`: the rank-11
  complex absorption, the fact that rung 1 sits on the complex branch ceiling, and the
  identification of the complex supplier as the only way up. This package rebuilds rung 2
  from the pinned profile and reproduces its published grid point exactly; it does not restate
  it as new.
* **The bank-absorption ladder and the `10^-10` replica convention** — PR208,
  `research/composed-diagonal-bit-bootstrap`: the ladder whose rungs 3 and 4 this package
  prices, and the pricing model under which rung 2 reproduces PR208's own published value
  `3541457/5*10^9`.
* **The bank proof and the engine chain** — PR200 (Chafik Boukhalfa; bit word and physical
  checkers), PR205/PR206 (the completed entrance banks and the packed bit certificate, the
  only bank construction in the pins), PR197 (Evan McKinney; the completed-bank machinery),
  PR184/PR168-v4 (icekylinx, eumemic; the source-assisted complex word and the physical
  paired-cube framework), PR183 (romainhedouin; the closed-form assembly ceiling) and PR193
  (ikeboy; the complex supplier whose profile this ladder is built on). All upstream
  attributions, notices and licences stand as published.
* **PR219's own upstream credits** are retained inside the vendored directory, unchanged.

## What is new here

The rank-16 and rank-20 absorptions and their exact prices; the exhaustion of the complex
ledger's whole-bank criterion (`66 | r * n_r` holds for exactly three families); the mixed
tiling obligation T1 that the two new families owe and rank 11 did not; the rank-16 and
rank-20 inventory obligations C6 and C7; and the next-step arithmetic showing that
`kappa = 7.2e-4` needs +1.242% more complex saving while anything above `7.277251e-4` needs a
new bit word.

On PR233's row, and read against the same ledger: that the rank-3 family is a **whole-bank**
family there, that `66 = 22 * 3` makes its bank exactly filled so the T1 obligation does not
arise, that the point lands at `1819302815717/25*10^14 = 7.277211262868e-4` bit-bound -- above
the ladder top and above the frontier -- the **stability** measurement that re-prices the rung on
all six ranked heads of #233 and all nine width-66 rows of this repository, and the negative
result for the rung above it (rank 4 moves neither the criterion nor the price).

No new kappa is claimed as a record: every number here is a **priced target**, conditional on
C1-C7, T1 and the inherited R1-R4, priced on a *row whose PR is unmerged*, and the package says
so in its own `status` field.

Prepared by Maxime Fleury with Codebuff assistance.
