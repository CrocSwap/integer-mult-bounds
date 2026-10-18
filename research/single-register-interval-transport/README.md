# Linear transport for a completed leaf's destination error

**Conditional lemma and independent verification; no new kappa.**
For the balanced PR628 ideal word at height h, an interval amplifies an error
confined to one register by at most h+2 for contractive factors.
That case needs no commutation. For commuting factors with every
subset product bounded by G, the bound is (h+2)G.

PR1374 proves quadratic amplification for arbitrary joint-register errors.
The new entrywise deduction distinguishes a single-register input.
It combines Hanson Sun's PR1085 prefix-entry invariant with Charles Bethin's
PR1278 squarefree interval lemma. The contractive case needs only PR1085.

The destination argument in [PROOF.md](PROOF.md) identifies the leaf immediately
before PR1374's lower-family cut. Its destination is z_(h-1), and a unit error
there attains amplification h-1. Thus worst destination-supported transport has
order Theta(h), for h>=2, even with scalar commuting isometries and G=1.
Credit Arham Tahir for the existing family and coefficient formula.

This is a corollary and a source-binding check, not a new dispatcher or supplier.
The proof includes a conditional error-transport consequence. It does not
admit actual rounded leaves, substitute new precision, or price an implementation.
The exact best constant and numerical integration remain open.

## Reproduce

Run from the repository root with standard-library Python 3.12 or later:

```sh
python3 -I -B research/single-register-interval-transport/check.py
```

Expected JSON status: `PASS_SINGLE_REGISTER_TRANSPORT`.
Runtime and executable fields intentionally report the actual interpreter.
All source files have SHA256 and Git-blob pins. The checker writes no files.

The finite checks cover 816,036 chronological destination intervals at n=1..16,
both signs, and three concrete sign patterns per case. This is not exhaustive
over sign patterns. A separate recursive prefix/Gauss-Jordan model checks 276
ordered-cut cases through n=83. The lower-family address and value checks cover
h=1..8; actual completed-leaf destinations apply for h>=2.

Finite tests support the written all-size proof; they do not prove it.
This work includes no proof assistant, independent human review, hosted CI, or selected cold replay.
Python AST extraction binds the ideal dispatcher, not its numerical
leaf implementation. The two checking methods use different traversal models.

## Open next questions

Integrate the column bound into a complete rounded-leaf contract.
Prove that each error has the required destination support at complete boundaries.
Retain negative-leaf preimages, coefficient preparation, internal growth, and the full cost bill.

Determine the exact maximum between h-1 and h+2.
Preserve the actual destination restriction and shared scratch in that argument.

## Credit and license

Prepared for Charles Bethin with substantial OpenAI Codex assistance.
Credit Chafik Boukhalfa (PR628/905), Hanson Sun (PR1085/1244), Charles Bethin
(PR1278), Arham Tahir (PR1374), Philipp/mightyOil (PR1295), Gareth Davidson,
0xkilgore, and the retained lineage. New work is Apache-2.0.
Predecessor sources and notices remain unchanged in vendor/.
