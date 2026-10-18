# A third dirty register does not shorten the D8 central pair

**Exact scoped negative result; minimum remains eight paid calls.** In the
three-register formal model over `F2[UT3(F2)]`, the target
`diag([xyxy],[xyxy],[1])` has no word of seven or fewer paid rank-one factors,
even with arbitrary free `GL3(F2)` scalar mixing. The direct eight-call word
therefore remains optimal after adding one arbitrary dirty register to the
two-register model. This is a result about the named finite alphabet and target,
not a universal bound on bit circuits or the multiplication exponent.

## Model and cost

Write group elements as triples with

`(a,b,c)(a',b',c') = (a+a', b+b', c+c'+ab')` over `F2`.

Let `x=(1,0,0)`, `y=(0,1,0)`, and `z=xyxy=(0,0,1)`. The paid alphabet consists
of

`D_N(g) = I + ([g]+[1])N`,

where `g` is `x` or `y` and `N=uv^T` ranges over all rank-one idempotents in
`M3(F2)`. There are 28 such idempotents and 56 paid gates. The target is
`diag([z],[z],[1])`; equality in the full group algebra ensures that the third
register is restored and that the endpoint identity holds for arbitrary dirty
register contents.

Each paid gate costs one unit, including every gate in the direct comparison.
The direct word applies `x,y,x,y` on each of the first two diagonal roles and
costs eight. The proposed saving had to reach seven or fewer. No COPY, clean
state, frame operation, or extra role is in the model. Free scalar `GL3(F2)`
mixing is an explicit favorable relaxation: augmentation sends every paid gate
and the target to the identity, so all interleaved scalar maps multiply to the
identity. Moving them through the paid factors conjugates `N`; conjugation
preserves the complete set of rank-one idempotents. Thus the 56-gate alphabet
already covers every word with such free mixing.

## Exact search and proof

For `g=x,y`, `([g]+[1])^2=0` in characteristic two, and `N^2=N`, so every
paid gate is an involution. Any word of at most seven calls can be split into a
prefix of length at most three and a suffix of length at most four. After
inverting the suffix, its middle state must lie both in the identity ball of
radius three and the target ball of radius four.

The verifier stores exact 3-by-3 matrices with all eight group-algebra
coefficients per entry. It exhausts the unique-state identity and target balls
through radius three, then checks every outgoing gate from each exact
radius-three target state. Those edges cover every target state first reached
at radius four. The complete counts are:

| Evidence | Count |
|---|---:|
| Paid generators | 56 |
| New states by identity radius | 1, 56, 1,750, 45,424 |
| New states by target radius | 1, 56, 1,750, 45,424 |
| Identity/target intersection through radius three | 0 |
| Target radius-four edges checked against the identity ball | 2,543,744 |
| Radius-four intersection edges | 0 |

The certificate includes SHA-256 digests of the canonically sorted radius-three
balls. A separate coefficient-convolution routine checks the full eight-call
direct identity. The verifier also checks associativity, all 56 gate
involutions, all eight one-call omissions, an altered third target, and
agreement between the compact transition and full coefficient multiplication
on fixed reproducible states.

Therefore the exact minimum in this model is eight. The failure of the
seven-call search is not an impossibility claim outside the fixed `UT3(F2)`
labels, three roles, rank-one gates, and free-scalar convention.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/d8-third-register-seed89de
```

Expected output includes:

```text
PASS_D8_THIRD_REGISTER min=8 identity_layers=1,56,1750,45424 right_radius4_edges=2543744
PASS_REGISTERED_RESEARCH_PACKAGE research/d8-third-register-seed89de outcome=negative-result
```

`CERTIFICATE.json` is regenerated only with `python3 -B research/d8-third-register-seed89de/verify.py --write` after reviewing the result. `SOURCES.json` pins the selected record, catalogue, and exact predecessor files; `TASK.json` records the accepted seed, refined scope, stopping rule, and limitations.

## Scope and predecessor

The task narrows `bit-new-register-model` to the explicit open question in
`research/bit-dihedral-commutator/README.md`: whether a restored third dirty
register helps the same D8 central target. That predecessor proves the exact
eight-call minimum with two registers. Its source files are pinned here, and
the predecessor package records base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`;
the current research base is `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.

The refreshed pre-submission overlap snapshot is `OVERLAP.json`; at 2026-10-14
08:24 UTC it covered 419 open PRs and 374 discussion records with complete
pagination and no warnings. It includes this claim, #1738. Nearby work includes
PR #1720's three-register S4 target and Discussion #1317's coordinate-CNOT
model; both use different groups and target words. No other exact D8/UT3
third-register claim appeared. The active four-register claims #1700 and #1727
also use different group objects. The claim and status are recorded in
[Discussion #1738](https://github.com/CrocSwap/integer-mult-bounds/discussions/1738).

This formal mechanism does not supply a bit-supplier word, price physical
hosting for the third role, change the selected recursive profile, or improve
the selected conditional `κ`. It is an exact local obstruction to one
specific workspace-sharing idea.

## Open next questions

Can a fourth arbitrary dirty register lower the paid minimum for the same D8
target and `{x,y}` alphabet? This is the next role count after the exact
three-register obstruction and could supply additional shared workspace. A
feasible first step is to count the 120 rank-one idempotents in `M4(F2)`, derive
an optimistic displacement-rank path budget, and estimate a memory cap for an
exact meet-in-the-middle search. The main blocker is the 240-generator search
growth; even a formal saving would still need a physical interpretation and a
full role invoice.

## Credit

The two-register model, proof and source code are by woklerx, recorded in
commit `965ff75aabb16cdd0978f4bf9222bcdedf514021`. This contribution adds the
three-register extension and its bounded exact result. Prepared by Cinna Davis
with substantial OpenAI Codex assistance in the derivation, implementation,
verification and writing. No independent human review or multiplication
theorem proof is claimed. Apache-2.0.
