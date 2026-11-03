# The fixed F4 coordinate decoder needs query rank at least 24

For every field, each of the four coordinate blocks of a fitting matrix on
the 24 real F4 root rays has rank at least six. Arbitrary nonzero diagonals
and nonsymmetric matrices are allowed. Thus the four fixed coordinate queries
have total binary rank at least 24, and separate power charges at least
4*6^t for every t>0.

Claim type: **scoped written proof with exhaustive finite corroboration**.
The new nine-ray forcing argument in [PROOF.md](PROOF.md) strengthens the
rank-five-per-coordinate lower bound of Ali Romman's
[PR6512](https://github.com/CrocSwap/integer-mult-bounds/pull/6512), exact head
`37c3eb9ec87cc735a413a8fc20bf3cae2cc31e95`. That package's caller calculation
is cited, not audited or replayed. This result supplies no new kappa.

The independent checker generates the real ray set and confirms the nine-ray
embedding in all four coordinate supports. On one nine-ray support, it checks
all 262,144 binary fitting matrices, with 18 independently free directed
entries. Two rank engines agree on every matrix:

| Rank | Matrices |
| --- | ---: |
| 6 | 321 |
| 7 | 21,497 |
| 8 | 148,302 |
| 9 | 92,024 |

It also rejects all 36 possible binary rank-five factor tuples after fixing
the forced I5 minor. Their first violated constraints are a/u in 30 cases,
b/v in five cases, and a/b in one case. A relaxed zero-pair fixture admits
rank five, and three invalid rank inputs reject. All contracts remain active
under optimized Python. These checks exercise the mathematical obstruction;
they do not repeat a predecessor's numerical result.

## Reproduction

From the repository root, using CPython 3.12.15 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/f4-coordinate-rank-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/f4-coordinate-rank-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/f4-coordinate-rank-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/f4-coordinate-rank-floor --check-source-history
```

Another CPython 3.12 interpreter can replace the absolute path. Expected
scientific marker: `PASS_F4_COORDINATE_RANK_SIX`. Stdout is a generated JSON
receipt containing the enumerated results and hashes of all six package files.
No generated files are written to the checkout. Source metadata binds the
catalogue, selected record and PR2125 README as historical provenance.
There are no imported predecessor programs or live external scientific inputs.

## Limits

This is a lower bound for the fixed four-coordinate Gram decomposition and
separate query pricing. It does not settle other bases, rectangular decoders,
shared query delivery, helper credit, a physical caller or the complete signed
invoice. The rank-six witness is only for the nine-ray subproblem. No full
15-ray rank-six completion or common 24-ray attaining matrix is claimed.
The all-field quantifier is the written proof. No proof-kernel check,
independent human review, selected cold replay or complete multiplication
theorem is claimed. The selected frontier and its five assumptions are unchanged.

## Open next questions

1. Can one binary fitting matrix attain rank six in all four complete
   coordinate blocks? Start with the reported nine-ray witness and solve the
   common full-support completion constraints. This would settle sharpness in
   this fixed coordinate model; an attaining matrix remains missing.
2. Can a changed basis or shared query boundary evade the floor with a
   favorable complete bill? First specify one exact decomposition and price
   every support, delivery and restoration. No such consumer is constructed.

[TASK.json](TASK.json) records the scope change and structured next questions.

## Engineering bounds and credit

Functions stay below 60 lines, loops have fixed finite bounds, and checks use
explicit exceptions.
Power of Ten rules 3 and 9 have managed-Python deviations: runtime allocation
and standard-library iterator dispatch are unavoidable. Live mathematical
state is bounded by 24 four-vectors, two nine-row matrices, four factor domains
of at most six pairs each, four spectrum bins and one six-file hash receipt.
The largest loop has 262,144 iterations. No recursion, external process,
callback chain or steady collection of census matrices is used. A fixed-buffer
port would be the follow-up if this verifier were moved to a lower-level
runtime. Warning-strict normal and optimized replay are the available
diagnostics; no standalone linter or type checker is installed in the command
environment.

This contribution was produced by Nick Petalas. Credit Ali Romman for
PR6512's model and rank-five minor; DreamingOfClouds for PR2125's prior cost-24
F4 search across bases; Aaron Wang for the distinct fixed-pairing screens in
PR2272/2518; and the root-unit decoder, Cinna Davis path-caller and Jacob Alan
Sussman productive-recursion lineage retained there. Classical rank
factorization and zero-pattern methods are not claimed as new. Apache-2.0.
