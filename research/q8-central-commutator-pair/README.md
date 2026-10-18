# Quaternion alphabet: central commutator pairs still cost their direct bill

**Scoped finite search result in a fresh nonabelian alphabet; no new kappa.** In the formal
`F2[Q8]` register model below, cross-register sharing cannot compress three central or
noncommuting pair targets below their direct four-call bill. The exact minimum is **four**
paid calls for each endpoint, at `r = 2` and at `r = 3` with one restored dirty register.
The bit supplier, the selected result and `upstream/` are unchanged; the bit side does not
bind.

## Changed hypothesis and full price

The scoped three-register obstruction (`research/bit-three-register-lower-bound`) works in
the abelian rational frame group `M_3(Q)`. Its model and the dihedral predecessor
(`research/bit-dihedral-commutator`, woklerx,
[PR 1443](https://github.com/CrocSwap/integer-mult-bounds/pull/1443)) both state that they
do not cover other address groups. This note changes exactly that hypothesis:

* **Address group.** `Q8 = {+-1, +-i, +-j, +-k}`, the quaternion group. Write `x = i`,
  `y = j`, `z = xyxy = x^2 = y^2 = -1` (the commutator, central of order two). Unlike the
  dihedral case the central commutator is a *paid-label square*, so the direct bill is 4
  rather than 8.
* **Counted roles.** `r = 2` arbitrary dirty scalar registers; the secondary endpoint uses
  `r = 3` with the third register restored exactly. Every paid call is charged; there are
  no free address maps, no COPY/ERASE, no clean ancilla and no unpriced `z` primitive.
* **Alphabet.** Paid labels are `x` and `y` only (no inverse labels). Each paid factor is
  `D_N(g) = I + ([g]+1)N`, `N = u v^T` a binary rank-one idempotent (`v^T u = 1`) on `r`
  scalar registers: six `N` and twelve generators at `r = 2`, twenty-eight `N` and
  fifty-six generators at `r = 3`. Free scalar `GL_r(F2)` basis changes are free and
  normalized by augmentation, exactly as in the predecessor: conjugating by a free scalar
  map conjugates `N` within the rank-one idempotents (this closure is rechecked for every
  `S` in `GL_2(F2)` and `GL_3(F2)`), free maps move through the paid factors, and
  augmentation `[g] -> 1` maps every paid factor to `I`, forcing the residual scalar map
  to the identity. The generator search therefore covers arbitrary interleaved free
  scalar mixing. This normalization argument is inherited from
  `research/bit-dihedral-commutator` and eumemic's PR 288 section 1.2; only its finite
  closure step is reproved here.

**Uniform identity standard.** Acceptance is equality in every coefficient of the full
eight-element group algebra `F2[Q8]`, not equality at one finite address size. A word that
equals `diag([g_1],...,[g_r])` in `M_r(F2[Q8])` is an identity on arbitrary dirty register
inputs.

## Exact results

| endpoint | direct bill | exact minimum | certificate |
|---|---:|---:|---|
| `r = 2`: `diag([z],[z])`, `z = xyxy = x^2 = y^2` | 4 | **4** | complete BFS to depth 3 misses; direct word attains |
| `r = 2`: `diag([xy],[yx])` (noncommuting pair, both orderings) | 4 | **4** | same |
| `r = 3`: `diag([z],[z],[e])`, third register dirty and restored | 4 | **4** | same |

The BFS layer sizes (new states per distance) are `1, 12, 110, 936` at `r = 2` and
`1, 56, 2324, 89574` at `r = 3`; ball digests are in `CERTIFICATE.json`. Because the state
of the formal matrix monoid determines every continuation, complete layer expansion to
depth 3 excludes all words of length at most 3, and the direct four-call word
(`z` on one register = two `x` calls on that register's idempotent) attains 4. No split
argument is needed; unlike the dihedral generators, the `Q8` factors `D_N(x)` are not
involutions (`D_N(x)^2 = D_N(x^2) = D_N(z)` is checked for every generator).

## Evidence

`python -I -O -B research/q8-central-commutator-pair/verify.py` (stdlib only, about 25 s)
recomputes everything and compares with `CERTIFICATE.json`:

* Q8 group laws exhaustively (associativity over all 512 triples, `x^2 = y^2 = z = xyxy`,
  `z` central, `[x,y] = z`), plus agreement of two independent quaternion multiplications;
* rank-one idempotent counts 6 / 28 and idempotence;
* the generator identity `D_N(g)^2 = D_N(g^2)` for all 12 / 56 generators;
* `GL_2(F2)` (order 6) and `GL_3(F2)` (order 168) conjugation closure of the generator set;
* complete BFS layer sizes and ball SHA-256 digests to depth 3 for both register counts;
* engine A (bitmask group-algebra convolution) and engine B (independent frozenset formal
  matrices with Hamilton 4-tuple quaternion multiplication) agree on every witness and
  direct word;
* omission controls: every single-call deletion of each direct word misses the endpoint
  (12 controls);
* known-distance controls: `I` at 0, `diag([x],[e])` at 1, `diag([z],[e])` at 2;
* mutated-target failure control: the certified word does not verify a target with one
  flipped coefficient.

## Scope and what is not claimed

* **No kappa, no supplier, no frontier change.** This is a scoped obstruction in one
  explicit finite alphabet. It says nothing about the rational-frame model, other address
  groups, inverse or larger label sets (the labels are `x, y` only), `r >= 3` active
  targets, or the multiplication exponent.
* **Failed search is not an impossibility theorem.** The statement is exact only for this
  alphabet and these endpoints: no word of length at most 3 exists in the 12/56-generator
  alphabets, and length 4 suffices.
* **Not a proof-assistant verification.** Two independent Python engines and finite
  exhaustions; no Lean or native C++ replay was run.
* The `a < D/E` moment diagnostic does not apply: there is no candidate improvement to
  price, and the scalar-cost relaxation here is more optimistic than any physical invoice.

## Reproduce

```sh
python -I -O -B research/q8-central-commutator-pair/verify.py
python -I -B research/q8-central-commutator-pair/verify.py
python3.12 scripts/research_package.py --package research/q8-central-commutator-pair
```

Expected:

```text
PASS_Q8_CENTRAL_COMMUTATOR diag_z_z_r2:4 diag_xy_yx_r2:4 diag_z_z_e_r3:4 r2_layers=[1, 12, 110, 936] r3_layers=[1, 56, 2324, 89574] no_new_kappa
```

## Open next questions

* **Does a label set including the inverses (`x, x^-1, y, y^-1`) compress any pair target?**
  It changes the word-length pricing and is the first alphabet variant neither this note nor
  the dihedral one covers. First step: the same BFS with 24 generators at `r = 2` against
  `diag([z],[z])` and `diag([xy],[yx])`. Blocker: none technical; bounded follow-up.
* **Is the minimum still 4 for `diag([z],[z],[z])` at `r = 3` (direct bill 6)?** Three
  active roles would test whether sharing scales beyond pairs. First step: depth-3
  meet-in-the-middle with layer digests and a memory cap. Blocker: state-space growth.

## Credit and disclosure

Prepared by **Aaron Wang**, with help from opencode. Apache-2.0; no independent human
review claimed. The model, the free-mixing normalization and the exact-minimum presentation
follow woklerx's `research/bit-dihedral-commutator`
([PR 1443](https://github.com/CrocSwap/integer-mult-bounds/pull/1443)), which fixes address
group `UT3(F2) = D8` and explicitly leaves other address groups open. The scalar-idempotent
register model is eumemic's PR 288 section 1.2; the register-model lineage credits Ali
Romman (PR 468), Gareth Davidson (PR 1333) and the pinned three-register note. Concurrent
work this is deliberately distinct from: the `F2[GL2(F2)]` coordinate-CNOT/SWAP line
(order-six group, isomorphic to `S3`), the `UT3/D8` commutator line (closed at `4k` for all
registers; third dirty register closed negatively), and the `S4`/`S5`/`AGL2`/`GL3` target
searches of October 14, 2026. The refreshed overlap survey (2026-10-14T10:17Z, complete
pagination) found no `Q8` object.
