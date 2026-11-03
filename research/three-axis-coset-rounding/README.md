# Optimal centres for three-axis reversible Gaussian rounding

An eight-point coset map now has an exact inverse, exact complex sum, exact
fourth power and uniform error 2h. This error is globally optimal among all
integer-output rules for the ideal three-axis operator: a half-grid witness
forces squared error at least four. Zero is fixed.

This pushes the larger-block question from PR6534. A complete 700,833-vector
search first gives optimal fixed-coset centres with squared error five. A
sum-preserving permutation of those 64 classes reduces the uniform value to
four. The checker regenerates every centre, matching edge and runtime byte.
A pointwise nearest rule cannot work: both zero and e0 have unique nearest
output zero. The new rule changes that contract. It does not promise phase
covariance, the ideal square rewrite, native admission or new kappa.

The complete call groups axes to minimize its certified error, then data
additions, among groups of sizes one, two and three. Its error bound is
ceil(f/3) h sqrt(N/2), compared with ceil(f/2) h sqrt(N/2) for PR6534.
Full retained ports return both dirty banks. The runtime table has 3,072
payload bytes. Reads, comparisons and checks remain explicit costs; no
physical speedup is claimed.

Run `python3 -B research/three-axis-coset-rounding/verify.py`.
`VERIFY.json` registers normal and optimized CPython 3.12. `PROOF.md` gives the
all-input and search-radius arguments. `CENTERS.json`, `TABLE.bin` and
`RESULT.json` retain the exact finite evidence. No external solver is needed.

## Attribution

Ali Romman prepared this contribution with substantial OpenAI Codex assistance.
Credit PR6534 for two-axis fusion and its inverse/port analysis; PR6509 for the
conservative single-axis kernel and independent matrix oracle; JoyboyBrian /
PR5485 and the retained PR4743 lineage for the complete ports. Exact predecessor
bytes remain in `inputs`, with source pins and origins. Walsh transforms,
lattice quotients and closest-vector enumeration are classical. Apache-2.0.

## Open next questions

- Can four or more axes attain their uniform grid lower bound with an explicit
  inverse, preserved sum and a practical classification table?
- Bind the changed grid contract to one actual selected multi-axis scalar.
  Check its entry and exit charts without phase or square rewrites.
- Lower the block to a reversible Boolean and tape protocol. Charge the table,
  residues, division checks, address work and cleanup before claiming a tariff.

## Verification limits

The all-input result follows from the finite quotient and radius proof. Data
checks cover all 64 cosets with large signed shifts, complete calls through f=4
and full ports through f=3. Normal and optimized replay, export and byte checks
are separate from hosted CI and independent scientific review. The optional
full-history audit was not run because the checkout is shallow. All live source
inputs are retained in this branch's ancestry. No selected record is changed.
