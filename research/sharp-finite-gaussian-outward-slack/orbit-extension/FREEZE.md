# Frozen finite-radii orbit-flow result

## Scope lock

This package evaluates only the following finite graphs:

- \(H_4/2\), Gaussian integer inputs, Euclidean error cap \(1\).
- Radii \(R=6,7,9,11\), with target thresholds beta_2 at \(R=6\) and
  beta_3, beta_4, beta_5 at \(R=7,9,11\), respectively.
- No other radius, operator, or error cap was evaluated.

The bounded search provenance, all gap counts, binary-search indices, exact
flow probes, positive quotient flows, orbit capacities, and full Hall-cut
orbit predicates are frozen in RESULT.json and summarized in
SEARCH-PROVENANCE.md. The matching lift and complete-neighborhood argument
are proved in PROOF.md.

## Frozen hashes

| Artifact or replay | SHA-256 |
|---|---|
| RESULT.json | f6b3c5be0fd3e619dbbc44496ebef11d0f06ff5f5c1364e854020505baac85ef |
| Normal isolated sweep output | f6b3c5be0fd3e619dbbc44496ebef11d0f06ff5f5c1364e854020505baac85ef |
| Optimized isolated sweep output | f6b3c5be0fd3e619dbbc44496ebef11d0f06ff5f5c1364e854020505baac85ef |
| Normal isolated verifier output | 5669fb69c55a3ede5cd907f59c892ef1e1f020932fc3654af9c1d62c05fb26ca |
| Optimized isolated verifier output | 5669fb69c55a3ede5cd907f59c892ef1e1f020932fc3654af9c1d62c05fb26ca |
| sweep.py | c3eea3f6c9786406cb2448e25f388a140ee782175eb16225e58590f9cf2c5fd4 |
| verify.py | 2bbcd0c87545bbb8054e52cd8dd15bd142031a4bc49bae104e4ed208de4709e4 |

The normal and optimized sweep receipts are byte-identical. The normal and
optimized verifier summaries are byte-identical. Both isolated verification
runs reject the incremented-flow and deleted-neighbor negative controls.
The exact radical gap ordering also agreed with an independent 100-digit
Decimal adjacent-order check at all four radii; this is a numerical sanity
check, not part of the exact proof.

## Independent review receipts

The exact RESULT.json digest above is the receipt digest checked by the
separate full-point verifier at
/workspace/scratch/92c9920affc2/root-work/finite-orbit-review/. That
checker does not import the orbit generator or radical comparator; it
independently enumerated individual points and edges, checked orbit
capacities, positive-flow conservation, complete Hall neighborhoods, and
three mutation/tie controls per radius. Its review summary has SHA-256
68899512d88b253dfb42978e3aa450d2f6a424ce8265757625e92075a18663f3.
The parent separately confirmed the R9 full-vertex matching and strict
deficit.

## Source pins

- Canonical CrocSwap base: e54523517d0f03e58352e647c403a5af3e525a57.
- Published R5 workstream context: 9c75d0b4b6e1cfe74694edf52f2f238a741bbaf5.
- Predecessors and author attribution: SOURCES.json and NOTICE.md.

## Replay

Run from this directory:

~~~~sh
python3 -I -B sweep.py > /tmp/finite-radii-result-normal.json
python3 -I -O -B sweep.py > /tmp/finite-radii-result-optimized.json
cmp /tmp/finite-radii-result-normal.json RESULT.json
cmp /tmp/finite-radii-result-optimized.json RESULT.json
python3 -I -B verify.py
python3 -I -O -B verify.py
~~~~

verify.py loads the sibling sweep.py bytes directly with compile/exec, so
isolated mode does not depend on ambient import paths or stale bytecode.
CHECKSUMS.sha256 pins every package artifact except itself.

This freeze makes no inference about untested radii, no global construction,
and no multiplication-frontier or kappa claim. It is a bounded evidence
package for review and integration.
