# Cycle 4 research claim

- Seed: `a27baaa734817e395db88b840bf4a089`
- Track and task: `bit-mechanisms` / `bit-new-register-model`
- Priority revision: 3
- Exact base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`
- Scope status: refined to a four-register nonabelian address model.

## Question

For the ordered noncommuting pairs `([a],[b])` drawn from
`a,b in {s1*s2, s2*s1, s2*s3, s3*s2}`, can one added restored dirty
scalar role let the complete paid alphabet realize
`diag([a], [b], [e], [e])` with at most three calls? Here
`s1=(12)`, `s2=(23)`, and `s3=(34)`. Each paid call is
`I+([s]+[e])N`, for `s` one of the three adjacent transpositions and any
rank-one idempotent `N` in `M4(F2)`; free scalar `GL4(F2)` mixing is included
through this full idempotent alphabet. The finite family has eight ordered
noncommuting pairs.

## Changed assumption, method, and bounded domain

The three-register abelian result excludes extra roles and arbitrary free address maps. This scope adds one restored role and uses the explicit nonabelian address group `S4`. Enumerate the exact 360 factors (3 paid labels times 120 rank-one idempotents), all 129,600 ordered two-factor products, and all 2,880 target-side products for the eight targets, giving a complete meet that excludes words of length at most three. Verify the explicit four-call diagonal construction for every target. Stop after this exact radius-three meet.

## Cost screen

Optimistically price every paid transposition call at one and scalar mixing, register hosting, and restoration interface overhead at zero. The direct identity costs four; a three-call identity would save one call (25%) in this abstract model. No selected supplier, bit primitive, recursive moment, or `kappa` change is inferred without a physical realization.

## Nearest work and overlap

- PR #1720, head `edb4a289a5f32c8209140144e384dcd3fa8cbfd1`: two identical 4-cycle targets at three roles.
- PR #1734, head `48855b620b23af3a7fe87d53bde05cd2211342c8`: two identical double-transposition targets at three roles.
- PR #1705, head `ad6b7d641b3e8576a95add7981fa75b6a8278fbc`: four coordinate-SWAP targets over a different `F2[GL2(F2)]` alphabet at four registers.
- PR #1742, head `679f3624a0a41ed14942825dd7f413132412d1e3`: three-role `UT3(F2)` D8 central-commutator pair with labels `{x,y}` and a seven-call lower-bound search; the group, alphabet, target, role count, and call floor differ from this four-role S4 family.

The pre-submit REST refresh at 08:37 UTC covered 424 open PRs. The complete Discussions overlap snapshot covered 383 records at 08:33:44 UTC; this claim and its two update comments are the only exact S4 four-role matches. Discussion #1738 / PR #1742 is a structurally related D8 third-role result with a distinct group, target, alphabet, and search depth. The S4 predecessor PRs above are related but use different targets and only three roles. The initial focused target was `diag([s1*s2],[s2*s3],[e],[e])`; the exact radius-three search was then extended over the full eight-pair family without changing the alphabet or method.

## Expected handoff

A small registered package with exact group-algebra arithmetic, state counts and hash, the direct word, omission/target mutation controls, source pins, cost accounting, and an explicit scoped conclusion. Claim expiry: `2026-10-14T10:23:00Z`.
