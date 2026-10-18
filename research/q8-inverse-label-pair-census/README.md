# Q8 pair census under unit-priced inverse labels

**Complete finite group-algebra census; no new kappa.** In the formal
`F2[Q8]` register model below, every one of the 64 ordered diagonal pair
targets `diag([g1],[g2])` at `r = 2` costs exactly its direct bill, both when
the labels `x^-1 = -i`, `y^-1 = -j` are priced at one call (24 paid factors)
and under the positive label baseline `x = i`, `y = j` (12 paid factors).
Unit-priced inverse labels therefore enable no cross-register sharing
compression; they change only the re-pricing of the elements `-i` and `-j`
from three calls to one. The bit supplier, the selected result and
`upstream/` are unchanged; the bit side does not bind.

## Changed hypothesis and full price

This answers open question 1 of the merged predecessor
`research/q8-central-commutator-pair`
([PR 1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822)),
extended from its two named endpoints to the complete pair family:

* **Address group.** `Q8 = {+-1, +-i, +-j, +-k}`; `x = i`, `y = j`,
  `z = xyxy = x^2 = y^2 = -1` (central commutator).
* **Alphabet (the changed premise).** Inverse labels `x, x^-1, y, y^-1` at
  unit price. Each paid factor is `D_N(g) = I + ([g]+1)N`, `N = u v^T` a
  binary rank-one idempotent (`v^T u = 1 mod 2`) on `r = 2` scalar registers:
  six `N`, so 24 factors for the inverse alphabet and 12 for the positive
  one. The factor set is closed under inversion:
  `D_N(g) D_N(g^-1) = I` (checked for all 36 factors across both alphabets),
  so the inverse alphabet is a group of units and every word can be priced
  symmetrically.
* **Counted roles.** Exactly `r = 2`, both registers arbitrary dirty inputs,
  the endpoint restored exactly. Every factor is charged; there are no free
  address maps, no COPY/ERASE and no clean ancilla. Free scalar `GL_2(F2)`
  basis changes are free and normalized by augmentation; the conjugation
  closure `S N S^-1` of the six idempotents is rechecked for all six
  `S in GL_2(F2)`, so the generator search covers arbitrary interleaved free
  mixing.
* **Uniform identity standard.** Acceptance is equality in every coefficient
  of the eight-element group algebra `F2[Q8]`, never a finite-column test. A
  word equal to `diag([g1],[g2])` in `M_2(F2[Q8])` is an identity on arbitrary
  dirty register inputs.

Because `i`, `j` are unit-priced in both alphabets and `-i`, `-j` cost one
call instead of three, element lengths are `0,1,1,2,2,2,3,3`
(`1,i,j,-1,k,-k,-i,-j`) in the positive alphabet and `0,1,1,1,1,2,2,2` in
the inverse one; pair bills are at most 6 and at most 4 respectively.

## Exact result

Let `min(a,b)` be the exact paid-call minimum of `diag([a],[b])`. Rows index
the first target, columns the second, in the order
`1, -1, i, -i, j, -j, k, -k`.

```text
inverse labels (min = bill everywhere)
        1  -1   i  -i   j  -j   k  -k
   1    0   2   1   1   1   1   2   2
  -1    2   4   3   3   3   3   4   4
   i    1   3   2   2   2   2   3   3
  -i    1   3   2   2   2   2   3   3
   j    1   3   2   2   2   2   3   3
  -j    1   3   2   2   2   2   3   3
   k    2   4   3   3   3   3   4   4
  -k    2   4   3   3   3   3   4   4

positive labels (min = bill everywhere)
        1  -1   i  -i   j  -j   k  -k
   1    0   2   1   3   1   3   2   2
  -1    2   4   3   5   3   5   4   4
   i    1   3   2   4   2   4   3   3
  -i    3   5   4   6   4   6   5   5
   j    1   3   2   4   2   4   3   3
  -j    3   5   4   6   4   6   5   5
   k    2   4   3   5   3   5   4   4
  -k    2   4   3   5   3   5   4   4
```

Every minimum equals the sum of the two label-geodesic lengths. The 28 pairs
whose minima differ between the alphabets are exactly the pairs with `-i` or
`-j` as an entry, and each difference is the re-pricing of those elements
(3 to 1 per entry). No pair is compressed below its bill in either alphabet.

The predecessor's endpoints are reproduced exactly in the positive alphabet:
`diag([z],[z])` and `diag([xy],[yx])` both have minimum 4
(see `research/q8-central-commutator-pair/CERTIFICATE.json`).

## Evidence

`python -I -B research/q8-inverse-label-pair-census/verify.py` (stdlib only,
about 40 s) recomputes everything and compares with `CERTIFICATE.json`:

* Q8 group laws exhaustively (associativity over all 512 triples,
  `x^2 = y^2 = z`, `xy = k`, `yx = -k`, `z` central, `z^2 = 1`, `[x,y] = z`)
  plus agreement of the two independently built group tables;
* rank-one idempotent completeness (6 of 9 binary pairs have `v^T u = 1`) and
  idempotence; `GL_2(F2)` conjugation closure of the idempotent list;
* generator identities `D_N(g)^2 = D_N(g^2)` and `D_N(g) D_N(g^-1) = I` for
  every factor of both alphabets;
* complete BFS layer sizes and ball SHA-256 digests from **two independent
  engines** (bitmask convolution from a `(sign, axis)` quaternion table vs
  frozenset convolution from explicit Hamilton 4-tuple integer products),
  agreeing on every layer and every ball:
  `inverse [1, 24, 358, 4104]`, `positive [1, 12, 110, 936, 6945, 48080]`;
* calibration with the merged predecessor: the positive-alphabet layers
  through depth 3 are exactly its recorded `[1, 12, 110, 936]`, and its two
  endpoint minima are reproduced;
* all 128 attaining words replay coefficientwise in both engines; 372
  single-call omission controls miss their targets; one mutated-target
  control fails; known-distance controls (`1` at 0, `diag([i],[1])` at 1,
  `diag([z],[1])` at 2); alphabet monotonicity (inverse minimum at most
  positive minimum) holds for all 64 pairs.

The complete shorter-word exclusion is the BFS itself: every word of length
at most 3 (inverse alphabet) or at most 5 (positive alphabet) appears in the
complete ball, and no ball contains a target below the recorded minimum.

## Scope and what is not claimed

* **No kappa, no supplier, no frontier change.** This is a scoped census in
  one explicit finite alphabet at `r = 2`. It says nothing about the
  rational-frame model, other address groups, `r >= 3`, or the multiplication
  exponent. The `a < D/E` moment diagnostic does not apply: no candidate
  improvement is priced, and the scalar-cost relaxation here is more
  optimistic than any physical invoice.
* **Failed compression is not an impossibility theorem.** The statement is
  exact only for these two alphabets, `r = 2`, and these 64 targets. Pairs at
  `r = 3` with a restored dirty role, larger register counts, or alphabets
  mixing positive and inverse labels at other prices remain open.
* **Not a proof-assistant verification.** Two independent Python engines and
  finite exhaustions; no Lean or native C++ replay was run.
* No written structural lower bound is claimed: the minima rest on the
  complete search, not on a paper proof of the no-compression statement.

## Reproduce

```sh
python -I -B research/q8-inverse-label-pair-census/verify.py
python -I -O -B research/q8-inverse-label-pair-census/verify.py
python3.12 -I -B scripts/research_package.py --package research/q8-inverse-label-pair-census --check-only
```

Expected:

```text
PASS_Q8_INVERSE_LABEL_CENSUS pairs=64 inv_layers=[1, 24, 358, 4104] pos_layers=[1, 12, 110, 936, 6945, 48080] compressed_inv=0 compressed_pos=0 omission_controls=372 no_new_kappa
```

## Open next questions

* **Does unit-priced inverse pricing compress the `r = 3` all-central target
  `diag([z],[z],[z])` below the positive-label minimum 6?** Why it matters:
  it tests whether the pricing change found inert at `r = 2` becomes active
  with three central roles. First step: the same BFS with 112 factors (28
  idempotents x 4 labels) to depth 3 plus the invertible-factor
  meet-in-the-middle against the depth-3 ball. Blocker: nothing technical;
  deliberately not taken here because the concurrent
  [PR 2248](https://github.com/CrocSwap/integer-mult-bounds/pull/2248) line
  owns the positive-label version of that object.
* **Is there a written structural lower bound proving min = bill for all Q8
  pair targets?** Why it matters: the first-order rank argument of
  `research/q8-mixed-three-register-seedcbd5ebc4` covers pairs without `+-1`
  entries only. First step: extend its `J_Q^2` coefficient-rank count to
  entries killed by the abelianization. Blocker: the `+-1` entries are
  invisible mod `J_Q^2`, so a second-order invariant is needed.
* **Do the pair tables extend to `r = 3` with one restored dirty role, or to
  `r = 4`?** First step: depth-3 ball digests at `r = 3` with 112 factors and
  a memory-capped meet at `r = 4`. Blocker: state-space growth at `r = 4`
  (the predecessor recorded the same blocker).

## Credit and disclosure

Prepared by **Aaron Wang**, with help from opencode (substantial AI
assistance; no independent human review claimed). Apache-2.0. The model, the
free-mixing normalization and the exact-minimum presentation follow
`research/q8-central-commutator-pair`
([PR 1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822)) and,
through it, woklerx's `research/bit-dihedral-commutator`
([PR 1443](https://github.com/CrocSwap/integer-mult-bounds/pull/1443)). The
scalar-idempotent register model is eumemic's PR 288 section 1.2; the
register-model lineage credits Ali Romman (PR 468), Gareth Davidson
([PR 1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333)) and
`research/bit-three-register-lower-bound`. Concurrent work this is distinct
from: [PR 2248](https://github.com/CrocSwap/integer-mult-bounds/pull/2248)
(`r = 3` three-role minima, positive labels) and
[PR 2303](https://github.com/CrocSwap/integer-mult-bounds/pull/2303)
(one- and two-factor words for `diag(i,j,k)` with all-nonidentity labels).
Refreshed `find_overlap.py` passes at 2026-10-15T04:34Z and 15:0xZ (complete
pagination) found no inverse-label Q8 pair object.
