# Characteristic polynomial of the 44-dimensional centre block

This finite exact certificate answers Open next question 2 of
[PR #7062](https://github.com/CrocSwap/integer-mult-bounds/pull/7062),
at `d2d59844d7a1f3f739d7add8eeec0d740a3aeca8`. On sign character 7 of
sector `c=3`, the `(u,v)=(+1,+1)` space has characteristic polynomial

```text
x^10 (x^2 - 36) (x^2 - 4)^5
  (x^3 - 12x + 8)^2 (x^3 - 12x - 8)^2 P_+(x) P_-(x)

P_±(x) = x^5 ± 4x^4 - 60x^3 ∓ 176x^2 + 640x ± 768.
```

This is the monic polynomial of `A_3` on the specified block. The two
cubic factors and two quintic factors are given as a product identity.
The multiplicities of 0, 2, −2, 6 and −6 are 10, 5, 5, 1 and 1.

## Certificate

Use the historical eight-by-112 query in [SOURCES.json](SOURCES.json).
Write `r_q` for its column at the nine-bit address label `q`. On a basis
vector with query coordinate `i` and address `a`, the term of `4 A_3` at
`q` multiplies by `r_q r_q^T` on the query coordinate. On the address
it applies `a → a XOR q` if the binary dot product `q·3` is one,
and multiplies by `(-1)^(q·a)` otherwise. The operator definition and
Bell identity come from the retained centre-query work.

Use the four sign flips at odd coordinates 1, 3, 5 and 7. The prescribed
eigenvalues for character 7 are `−1, −1, −1, +1`. The other generators
are `u = (0 2)(4 6)` with minus signs on 0 and 2, and
`v = (0 4)(2 6)` with minus signs on 0 and 4. Both have prescribed
eigenvalue `+1`. Each signed coordinate action induces an address action
by its action on the projective query columns. The verifier derives the
unique linear extension from the spanning port labels, checks it at all
112 labels, and checks that it is orthogonal and fixes sector 3.
It checks that the six signed actions commute and square to the identity.

Multiplying each generator by its prescribed sign turns the equations into
fixed-vector equations. For every address-coordinate orbit, start at the
least index and give it coefficient +1. The 64 subset products of the six
generators force every other coefficient in the orbit. If two products
force opposite coefficients at one index, the whole orbit is zero over
`Q`. Otherwise the signed orbit vector spans the solutions on that orbit.
Disjoint supports make these vectors independent. This accounts for all
4,096 ambient indices. The checker finds 44 surviving orbits, each of
support eight, and 508 discarded orbits.

Apply the Bell formula to each surviving vector and read the resulting
coordinates at the 44 least indices. Reconstruct each image from these
coordinates and compare all 4,096 entries. The 180,224 exact coefficient
comparisons establish the restriction, including its vanishing outside the
basis supports. The compressed integer matrix `M` represents `4 A_3`.
Faddeev–LeVerrier computes its characteristic coefficients by repeated exact
matrix multiplication and trace division. The verifier compares every
coefficient with the displayed product after scaling coefficient number
`j` by `4^j`. It also checks the zero Cayley–Hamilton residual and
rejects a sector-1 substitution for the same basis.

The verifier emits the coefficients in descending order and a generated
hash-bound receipt. SHA256 of the compact JSON matrix is
`b8996e800aec3655bc44e962f8271e33c8188c4b5e99c7fe6167a4376cfc2617`.
The scientific replay uses the Python standard library and writes nothing.

## Reproduce

Run from the repository root. Substitute a local CPython 3.12 executable
for the absolute path on another machine.

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/c3-weight3-plus-plus-charpoly/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/c3-weight3-plus-plus-charpoly/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/c3-weight3-plus-plus-charpoly
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/c3-weight3-plus-plus-charpoly --check-source-history
```

Expected scientific marker is `PASS_C3_WEIGHT3_PLUS_PLUS_CHARPOLY`.
The metadata and committed-byte commands need Git history. The direct
verifier needs the pinned query at its declared relative path.

## Scope and credit

This contribution was produced by Nick Petalas. Credit unpaidmoon for
[PR #7062](https://github.com/CrocSwap/integer-mult-bounds/pull/7062)'s
explicit question and its adjacent 12-dimensional result, and
[PR #6965](https://github.com/CrocSwap/integer-mult-bounds/pull/6965)'s
choice of sign character and joint involutions. JoyboyBrian supplied the
sign-character handoff. Ali Romman's PRs #4958 and #4720 supply the query
and Bell action. Krzysztof Wojt's one-slot annihilator and the doubled
representation from #1719 retain their original credit. Signed-orbit
bases and the trace recurrence are standard. New work is Apache-2.0.

The formal-interface-lemma card is scoped here to one historical finite
spectral calculation. The selected source-binding orientation passed at
`e54523517d0f03e58352e647c403a5af3e525a57`. The result has no new κ or
supplier admission. The other sectors, larger tensor widths, native caller
costs and the full multiplication theorem remain outside this calculation.
No predecessor scientific verifier, selected cold replay, Lean or Docker
was run. Independent human and formal proof-kernel review are unclaimed.

The verifier's finite sizes are fixed by the authenticated query, 64 subset
products per orbit, the 4,096-index ambient action and the 44-dimensional
restriction. It is iterative and uses explicit checks under optimized
Python. Managed Python allocates containers and exact integers during
replay. The fixed dimensions bound the number of live entries.

## Open next questions

Does one signed coordinate symmetry transport this 44-dimensional block to
each of the three other weight-3 `(+1,+1)` blocks? First test the induced
action of the sector stabilizer on the character and the two involutions.
The present certificate imposes character 7 only, and the dimensions alone
do not imply equal polynomials.
