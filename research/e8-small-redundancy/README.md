# Two low-redundancy obstructions for fixed E8 matrices

This package gives two scoped structural results. It does not give a new
supplier, a paid implementation, or a change to the complete kappa bound.
The two results use different scalar fields and different support prices.
Their bounds must not be substituted for each other.

| Fixed matrix | Scalar field | Covered class | Result |
| --- | --- | --- | --- |
| Canonical rank-eight E8 Gram matrix | Q | Nine totals, each supported in its assigned binary coordinate hyperplane | Each total is a nonzero multiple of `a_i-t`. Its support spans the full dimension-eight hyperplane. |
| `K(q,r)=1+(q dot r)/2 mod 2`, for the 120 norm-four root lines | F2 | Any outer-product factorization with at most eleven scalar terms | The sum of rational source-reader pairing ranks is at least 72. |

The first result classifies the coefficients, not just their cost. It allows
all nine totals to change at once. The second result permits arbitrary binary
factors outside the rank-nine code. It closes the ten- and eleven-term cases
left open by the minimal nine-term copy-rank argument.

The proofs are in `COORDINATE-PROOF.md`, `TEN-PROOF.md`, and `ELEVEN-PROOF.md`.
The latter two use finite root-system facts checked in two coordinate models.
The written Weyl-chamber reduction is part of the proof. The scripts check
its finite premises; they are not a formal proof of that reduction.

## Cost interpretation and limits

The binary theorem is an algebraic pairing-rank floor. Its interpretation
as a physical drop-cost floor assumes the separate scalar copy-tree model
of DreamingOfClouds' [PR #446](https://github.com/CrocSwap/integer-mult-bounds/pull/446),
[Theorem C](https://github.com/CrocSwap/integer-mult-bounds/blob/309482849b6ddf34db998f53612d34c19f6e3233/research/format-obstructions/PROOF.md).
The algebraic theorem does not depend on that physical interpretation.
Dynamic mixing during delivery, shared charges, twelve or more terms, changed
fitting matrices, and punctured root sets remain outside the result.
Source access, legal frames, restoration, hosting, and recursive children
are not priced here. No complete kappa improvement follows.

The rational coordinate theorem assumes the fixed canonical scatter and the
nine specified hyperplanes. Its coefficient classification is more specific
than a general copy-cost floor. It does not classify other frame choices.

## Reproduce

Use Python 3.10 or later and the standard library. From the repository root:

```sh
python3 -B research/e8-small-redundancy/verify.py
```

The final line is:

```text
PASS_E8_SMALL_REDUNDANCY coordinate_rigidity=9 binary_terms<=11 pairing_floor=72 no_new_kappa
```

The replay checks source hashes before execution. It uses a temporary copy
for the historical scripts that write receipts. It compares every saved
mathematical receipt with the new result. It checks all 511 nonzero binary
codewords, eight E8 root-hyperplane types, seven E7 maximal proper-flat
types, the outside-word histogram, and the exact map between the two root
models. The coordinate check proves the required finite ranks over Q and
checks all 14,400 scatter entries. A separate 72-variable calculation gives
ranks 71,72,72,72,72 over F107.

The written proofs and these finite premises had separate AI agent reviews.
The retained historical reviews identify their scope. This is not independent
human review, a Lean theorem, a complete circuit replay, or hosted CI success.

## Sources, overlap, and credit

The publication base is `cef4b52f2a59009865bf8eabde1be3f159063703`.
`SOURCES.json` records public pins. `ORIGINS.json` records the original local
sources and the limited path/module changes made for portable replay.
The two input notices retain their source credits. Jacob Sussman supplied
the rational E8 circuit and certificate. The bit word is from Rohan Arun's
historical PR462 head; its notices credit the underlying E8 and supplier
work. This package uses only its root lines, not its claimed supplier bound.

The depth-one binary nine-term floor is prior work, including Joel Pulikkan /
GamingPuzzled's [PR #620](https://github.com/CrocSwap/integer-mult-bounds/pull/620)
and the later [tensor floor](https://github.com/CrocSwap/integer-mult-bounds/blob/cef4b52f2a59009865bf8eabde1be3f159063703/research/tensor-e8-copy-floor/README.md).
Ross Richardson's [R429 reader floors](https://github.com/CrocSwap/integer-mult-bounds/blob/cef4b52f2a59009865bf8eabde1be3f159063703/research/r429-binary-reader-floors/README.md)
cover a different, punctured 111-line matrix. conorholds' [one-coset theorem](https://github.com/CrocSwap/integer-mult-bounds/blob/cef4b52f2a59009865bf8eabde1be3f159063703/research/e8-one-coset-deficiency/README.md)
uses a rational/odd-characteristic rank-eight code and binary support prices.
It does not imply the binary-factor theorem here. Its stronger general
rational floor does subsume our old nine-small-total numerical obstruction;
that superseded experiment is omitted from this package. The coefficient
classification for nine specified coordinate hyperplanes is retained.

Ali Romman directed this work. OpenAI Codex and separate research agents
provided substantial assistance with the proofs, code, audit, and packaging.
New work is under Apache-2.0. Attribution does not imply review or endorsement.

## Open next questions

Can a binary factorization with twelve terms reduce the same pairing-rank
sum? The first step is to classify its factor ranks and the resulting
three-dimensional quotient of the rank-nine code. The two-dimensional
quotient proof here does not cover that case.

Can a useful shared delivery operation escape the separate copy-tree price?
The first step is to give one complete legal map with arbitrary dirt restored.
Support overlap alone does not provide that map or its recursive cost.
