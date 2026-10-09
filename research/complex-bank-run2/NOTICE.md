# Notice and attribution

This package is Apache-2.0, like the repository. It adds a ledger and a price; it builds no
word and changes no existing file.

## Sources it depends on

* **PR219** (`research/residual-bank-run1`, head `237067f483bccf931507a5386946cf66da0a915a`,
  by halve-bit). Rung 1 itself: the rank-22 retained-ledger schedule, the exact interval
  moment engine as vendored there, the 47-constraint balanced assembly, and the
  obligations this package inherits. **Vendored byte-identically** under
  `references/pr219-run1/` (16 files) and imported at run time -- its `schedule.py` and
  `arithmetic.py` produce rung 1's published grid point inside this package, and the
  vendored copy also self-verifies in place.
* **PR207** (`research/coordinated-crossover-pr200`, head `cd14825`, by Dugongue). The
  frontier row pair and the published kappa this package reproduces exactly, vendored as
  `references/pr207-coordinated-crossover.certificate.json`. The upstream blob is
  `23416f66…` with CRLF line endings; this repository's `* text=auto eol=lf` normalizes the
  vendored copy to LF (`f4e30cca…`), and the parsed JSON is identical to the upstream file.
* **PR208** (`research/composed-diagonal-bit-bootstrap`, by the same author as this
  package). The bank-absorption ladder, the `10^-10` pricing convention and the published
  rung-2 value `3541457/5*10^9` this package reproduces as its independent replica. Not
  vendored; cited by value.
* **PR184 / PR168-v4 and the PR197/PR200/PR205 line**, inherited through #219: the
  balanced assembly with its 47 strict constraints and seven margins, PR200's exact
  rational interval moment, and #205's completed-banks pack of the bit word (its
  `physical.banks`, gauge roles, copies and `bank_controls` are the pinned evidence that
  the queue's only bank construction is the bit word's).

## Credit

The ceiling argument, the complex-side ledger, its price in two conventions, the blocker
report and the verifier are this package's contribution. Everything credited above is
retained, pinned by sha256 in `SOURCE.json` (21 files), and unmodified.

## Assistance

Prepared with Anthropic Claude assistance. No claim in this package is presented as a
formal verification of an unconditional multiplication theorem; see the scope statement in
`README.md` and the open obligations in `obligations.json`.
