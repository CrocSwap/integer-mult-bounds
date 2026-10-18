# Four-role mixed-target word in the order-eight dihedral model

This package gives the exact minimum of five paid factors for one four-role
target in a fixed nonabelian group-algebra model. It is a scoped finite-model
result; it does not improve the selected integer-multiplication bound.

## Model and result

Let `G = <a,b | a^2=b^2=e, (ab)^4=e>` be the dihedral group of order eight,
represented in the verifier by `a=(0 1)(2 3)` and `b=(1 2)`. Work over the
full group algebra `F2[G]`. There are four scalar roles and a paid factor is

```text
D_(g,N) = I + ([g] + [e]) N,
g in {a,b}, N = x y^T in M4(F2), x,y nonzero, y^T x = 1.
```

One paid factor costs one. The alphabet contains 120 rank-one idempotents and
240 labeled factors. The target is

```text
diag([a], [ab], [ba], [e]).
```

The matrix identity acts on every arbitrary four-tuple of group-algebra
register values. The fourth role is restored exactly. A direct word has five
factors:

```text
D_(a,E00) D_(a,E11) D_(b,E11) D_(b,E22) D_(a,E22).
```

The first three roles receive `a`, `ab`, and `ba`; the fourth remains the
identity. Because `ab != ba`, the order of the middle labels matters.

**Result.** The exact minimum is five in this model. No word of at most four
factors equals the target in `M4(F2[G])`.

## Exact finite exclusion

`verify.py` builds all eight group elements and the complete `F2[G]`
convolution table. Each matrix entry is an eight-bit coefficient mask, so
state equality checks every group coefficient exactly. It then enumerates all
240 factors and all 57,600 ordered two-factor products, retaining 32,651
distinct pair states.

The checks cover every length up to four:

- Lengths zero, one, and two are direct membership checks.
- For length three, a first factor `A` must leave pair state `A*T`, since
  every paid factor is an involution.
- For length four, split `A B C D = T` into pairs. For each right pair
  `Q=C D`, the left pair must be `T*Q^-1 = T*D*C`; exact pair-state lookup
  decides whether such a word exists.

This uses the complete declared alphabet and group algebra, not a bounded
address sample. The search does not consider free inter-call `GL4(F2)` maps,
other paid labels, extra roles, or a different target. The count of pair
states alone is not used as the lower-bound argument; the verifier performs
the target-specific membership tests above.

The positive controls check the group presentation, the paid-factor
involutions, and the five-factor word. Seven negative controls reject a
non-idempotent matrix, ensure the reversed `ab`/`ba` word misses the target,
and show each deletion from the displayed direct word changes the map.

## Task, overlap, and limits

- Track `bit-mechanisms`, task `bit-new-register-model`, seed
  `a97c8efa02e2955139574300f12b9c03`, priority revision 3, exact base
  `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- The selected-record SHA-256 is
  `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- The first considered `F2[GL2(F2)]` scope was dropped after finding open
  PR [#1763](https://github.com/CrocSwap/integer-mult-bounds/pull/1763), which
  uses the same four-role factor alphabet and pair-state method for even
  repeated order-three targets. This package changes the group relation to
  `D8` and the target to one reflection, both orientations of an order-four
  rotation, and one identity role.
- D8 predecessor [#1742](https://github.com/CrocSwap/integer-mult-bounds/pull/1742),
  by 1337isnot1337, proves an eight-call minimum for a three-role duplicated
  central-commutator target. Its claim explicitly left four-role models open;
  it does not include this target. The exact predecessor head is recorded in
  `TASK.json`.
- The fully charged local baseline is five paid factors, so the search tests
  whether the heterogeneous target can be completed for four. Every role and
  restoration is included. The model has no source access, helper hosting,
  recursion, or arithmetic-supplier interface. No source occurrence, supplier
  adoption, paid-moment change, or new kappa is claimed.
- The selector's `research_baseline.py` first-step could not complete in this
  sparse worktree because the selected certificate package inventory is not
  materialized. The exact selected-record pin and the new package replay do
  run here; the failed orientation attempt is not counted as a pass.

The work was prepared with substantial OpenAI Codex assistance. No independent
human review is claimed. No predecessor executable is imported.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/d8-mixed-target-seeda97c8e
```

Expected marker:

```text
PASS_D8_MIXED_TARGET min=5 roles=4 group_order=8 generators=2 idempotents=120 factors=240 pair_states=32651 words_le4=0 controls=7 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/d8-mixed-target-seeda97c8e outcome=negative-result
```

## Open next questions

Can this four-role D8 operation alphabet be mapped onto an actual bit or
integer-multiplication supplier primitive so its exact factor cost affects a
paid moment? It matters only if the labels and rank-one role updates occur in
a realizable source interval. The first step is to identify one source-pinned
supplier word with `a` and `b` as its paid labels; no such mapping is known,
so this result alone does not justify supplier replay or a kappa claim.
