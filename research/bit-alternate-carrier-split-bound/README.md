# Exclude clean alternate-carrier splits on the retained BIT word

**Scoped negative theorem. No new κ.** Every eligible alternate-carrier cut on
the exact retained #7001/#6726 BIT word has zero clean helper-endpoint pairing.
Two separate exact implementations cover **3,908 changed bank states and 4,521
bank/group contexts**. All 76 contexts with a nonzero local pairing still have
zero clean endpoint pairing. A proof extends this zero form to every finite
positive multiplicity, including ordered, noncommuting matrix coefficients at
the same interface.

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`. The selected κ remains
`363005817/100000000000`. No supplier, invoice, shared implementation or selected
record changes. None of the five retained framework assumptions is discharged.

## Exact claim and relation to prior work

Fix the native paid word, scalar operation order, frames and owner lifetimes.
Choose one of its nine helper groups with common entrance A and exit D. At any
strict intermediate chart A < C < D, take the entire live C-bank **provided it
contains no original public helper belonging to that group**. Allow arbitrary
linear mixing of all bank fields and free group boundary corrections.

For exact prefix rows P and suffix columns S, let aP and Sb both be supported
only on that group. Then `(aP) · (Sb) = 0` for every such a,b. Thus the necessary
paired conditions `ab = 1` and `(aP) · (Sb) = 1` cannot hold. Even granting all
prospective ordinary work free, this interface supplies no positive-rank clean
exchange. [PROOF.md](PROOF.md) gives the quantifiers, rank identities, coverage
argument and operator-valued extension.

This answers the alternate-ownership opening in
[#7304](https://github.com/CrocSwap/integer-mult-bounds/pull/7304), pinned at
`534a250ab99ec46d3dde0bd2fc9ce5bfd26b8b94`. That predecessor requires an old public
helper pivot in its original owner at a strict intermediate chart and already
allows arbitrary bank mixing. Here **no original target-group helper is in the
bank**. The complementary domain, zero endpoint form and multiplicity
consequence are the additions; the paired-support criterion is prior work.

## Reproduction

Python 3.12, standard library only; the direct verifier needs no network or Git:

```sh
python3.12 -I -W error -B research/bit-alternate-carrier-split-bound/verify.py
python3.12 -O -I -W error -B research/bit-alternate-carrier-split-bound/verify.py
```

Expected status: `PASS_BIT_ALTERNATE_CARRIER_ZERO_PAIRING`, with 3,908 banks,
4,521 contexts, zero nonzero clean forms and 76 local-only contexts. It reads
its own package directory and does not write into the package. Registered replay:

```sh
python3.12 -B scripts/research_package.py --package research/bit-alternate-carrier-split-bound
python3.12 -B scripts/check_research_commit.py --package research/bit-alternate-carrier-split-bound --check-modes
```

The unchanged native gzip has SHA-256
`51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78`.
[SOURCES.json](SOURCES.json) records its original path, commit and Git blob.

- `kernel_screen.py` uses complement orthogonality, projected kernels and witnesses.
- `independent_screen.py` uses rational row-space containment and block-rank
  identities, with separately reconstructed prefix and suffix maps.

Both full frozen receipts are checked. All 1,024 two-field toy contexts are
compared against direct witness enumeration (336 paired positive cases and
409 local-only cases). Both engines reject altered source bytes. Contaminated
prefix/suffix, dirty-carrier and premature-erasure controls also run, including
under `-O`. These are separate AI implementations and proof review, not human
or formal-kernel acceptance. See [VALIDATION.json](VALIDATION.json).

## Limits

The census exhausts this word and cut domain. The block lift is a universal
algebraic implication of the zero forms, not extrapolation from small volumes.
Changed words, frames, new paid moves, mixed helper boundary groups, multiple
times and nonlinear recodings are outside scope. No complete supplier cold
replay or new asymptotic multiplication theorem is claimed.

## Open next questions

1. At one of the 76 local-only cuts, can a charged prefix or suffix change make
   the endpoint pairing nonzero and improve the complete signed budget? Start
   with the explicit example in `EXPECTED-INDEPENDENT.json`; charge every frame,
   storage, restoration and caller cost.
2. Can an explicit interface across different boundary groups or multiple times
   bypass the one-cut zero form? Write its full physical contract first;
   compatibility and the complete invoice remain open.

Structured questions and blockers are in [TASK.json](TASK.json).

## Credit

Prepared for **Jerry Chen / @CubeJerry** with substantial OpenAI assistance in
research, separate implementations, proof review and packaging. Credit
[#7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001) and
[#6726](https://github.com/CrocSwap/integer-mult-bounds/pull/6726) for the BIT word,
ToikY's #7304 for the predecessor and open ownership question, and #5599/#5679
for the preceding paired-support interface. Original input notice retained
under `inputs/`. Apache-2.0.
