# Characteristic polynomial of one exhibited 12-dimensional minus space

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the involution `u = (4 7)(5 6)`, all signs `+1`, cuts the eigenvalue-`+1` space of `s = (0 4 3 7)(5 6)` inside the character `eps[1] * eps[2]` by a 12-dimensional minus space. That space is reducible under `A_1`. Its monic characteristic polynomial is

```text
x^4 (x - 2)^4 (x + 2)^4
```

The operator `B = 4 A_1` is diagonalizable on this space, with eigenvalues `0`, `8` and `-8`, each of geometric multiplicity 4. The kernel of `B` is a 4-dimensional proper invariant subspace. Every line in any of the three eigenspaces is invariant under `A_1`.

The twin character `eps[5] * eps[6]`, which PR #7082 also exhibits, has a different polynomial,

```text
x^2 (x - 2)^2 (x + 2)^2 (x^3 - 12x - 8)(x^3 - 12x + 8)
```

with both cubics irreducible over `Q`. That copy is reducible as well. Selected conditional kappa stays `363005817/100000000000`. The argument and the limits are in [PROOF.md](PROOF.md).

## What is certified

The live input is the query pinned in [SOURCES.json](SOURCES.json), SHA256 `5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.

`W` is the set of vectors in the `eps[1] * eps[2]` character space with `s v = v` and `u v = -v`. On the 48-dimensional eigenvalue-`+1` space of `s`, `u` has trace `24`, `u + I` has rank `36`, and `u - I` has rank `12`. Thus `W` is the 12-dimensional minus space exhibited by PR #7082 for this character. The integer matrix of `B` in the canonical lattice basis is pinned in [evidence/minus-space.json](evidence/minus-space.json). Every entry lies in `-8..8`. Ascending-coefficient SHA256 values are

```text
chi_A  589ce5d010f0e4c5cf6d78719150e69afee3650ddf71dd273b58de10a5082e45
chi_B  bf3564eac70bdbb2ff2e0041ca84c8f69f1f215e9ba5678f5a10d8b90804106a
```

The minimal polynomial of `A_1` on `W` is `x(x - 2)(x + 2)`. The same file pins the three 4-dimensional eigenbases. The first vector of the kernel of `B` is `(0, 0, 0, 0, 0, 0, 0, 1, 0, -1, 0, 0)` in that basis, and `B` sends it to zero.

On the twin character the trace is again `24` and the minus space is again 12-dimensional, but the polynomial is the one displayed above. Its SHA256 values are

```text
chi_A  c58d35de18567d24a9abeef5a3e536852d61ab429c03da1477f5792ad0cce841
chi_B  49655042b6738fa130d0297dc04113484e5b85bd2cbe61823f69a7f7bd1e696f
```

The minimal polynomial there has degree 9. The primary decomposition is three scalar spaces of dimensions `2, 2, 2` and two irreducible cubic blocks.

This is a proof by exact linear algebra over `Q` for these two spaces of this one involution. It is smaller than the characteristic polynomial of the 48-dimensional space, and the degree-12 calculation does not replace that polynomial. Each degree-12 polynomial divides the matching coefficient list recorded by PR #7036; that comparison reads coefficients and does not replay the degree-48 matrix.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal caller binding. The open clause is question 1 of [PR #7082](https://github.com/CrocSwap/integer-mult-bounds/pull/7082): whether the exhibited 12-dimensional minus space is irreducible under `A_1`. The stated first step is the characteristic polynomial of `B_1` on the integral kernel basis. The answer for the character `eps[1] * eps[2]` is no: the polynomial above is reducible, and the kernel of `B` is a proper nonzero invariant subspace.

The same conclusion holds for the twin copy that PR #7082 builds for this same `u`. The two polynomials are different. The calculation is only these two spaces of this one `u`. It does not classify the other cutting involutions from the census in PR #7082.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` for kappa `363005817/100000000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c1-12-minus-a1-charpoly/verify.py
python3 -I -B -O -W error research/c1-12-minus-a1-charpoly/verify.py
python3 -B scripts/research_package.py --package research/c1-12-minus-a1-charpoly --check-only
```

The direct marker is `PASS_C1_12_MINUS_A1_CHARPOLY`. Acceptance uses explicit checks, so `-O` does not disable them. Rejection controls cover a coordinate transposition, a sign flip that moves `u` off sector `1`, a single flipped character sign, the 36-dimensional plus space of the same `u`, a corrupted matrix entry, a dropped polynomial factor, and a sign error in one basis vector.

Not run: Lean, Docker, the degree-881 replay, the degree-410 minor, the selected cold replay, a `c = 3` census, the characteristic polynomial of the 48-dimensional space, and the characteristic polynomial of the 36-dimensional plus space.

## Overlap

`scripts/find_overlap.py "12-dimensional minus" "exhibited 12-dimensional"` was run on 2026-11-11 against upstream `e54523517d0f03e58352e647c403a5af3e525a57`. Coverage: local notes `10180` of `10178` HEAD paths, complete; `500` open PR records, pagination complete, fetched `2026-11-11T10:31:47Z`; `7171` discussion records, pagination complete, fetched `2026-11-11T10:32:53Z`.

Both phrases match PR #7082 and discussion reply 19515065. Those records exhibit the 12-dimensional invariant subspace and state that the characteristic polynomial and the irreducibility question are open. No other open-PR record in that snapshot states a polynomial for this minus space. Closed PRs were searched through local READMEs, task metadata, and the ledger only. No code diffs were searched.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- What is the characteristic polynomial of `B` on the 36-dimensional plus space of this same `u`? The degree-12 polynomial does not determine it.
- For one element that preserves the character and does not preserve `E`, what is the exact dimension of `E ∩ h E`? That is question 2 of PR #7082, and this package does not compute it.

## Credit

PR #7082, by unpaidmoon, exhibits the 12-dimensional minus space, proves invariance under `B_1`, and leaves irreducibility open. The moved-character split, the element `s`, and the centralizer obstruction are PR #7009. The degree-48 coefficient lists used for the divisibility comparison are PR #7036. JoyboyBrian recorded the sign-character dimensions and the open decomposition question in discussion comment 19144258. Ali Romman's PR4958 and PR4720 retain the query and the Bell action. Nick Petalas's PR5120 is the degree-410 lower bound. Krzysztof Wojt's PR5168 is the degree-881 one-slot annihilator. The doubled representation comes from PR1719. The lattice and characteristic-polynomial code follows the method in `research/c1-moved-48-charpoly/`, on the 48-dimensional space rather than this minus space. New work is Apache-2.0.
