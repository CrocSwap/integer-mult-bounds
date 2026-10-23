# T24 fixed-profile global-coupling obstruction (scoped negative result)

**Scope:** exact necessary-condition argument for a proposed T24 **residual rank profile**, plus a standard-library independent checker. This does **not** construct a physical T24 owner map, repair the prefix, or improve κ.

**Repository base at submission:** `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf` (2026-10-13). Depends on the U8/T21 whole-helper relaxation of [PR #890](https://github.com/CrocSwap/integer-mult-bounds/pull/890), especially `research/complex-t21-owner-bound/PROOF.md`, and its predecessor signed-dual prices from PR #795. Source head pinned for #890: `4b3bd8cbe8e3e81c44161017c9b72c905a8040a8`.

**Current-frontier context:** `research/complex-t37-owners/ALL-T-PROOF.md` already gives a *stronger*, all-replica-count bound on κ for the fixed U8 family and the selected result comes from #942/T37. The claim here is **only** a separate, elementary *non-separability* statement about one hypothetical T24 profile, not a new κ bound or competing optimality theorem.

## Theorem: no independent split for this profile

In the fixed-width whole-helper, nine-complete-calls-per-replica model of #890, the proposed T24 residual profile

```
{48: 7190, 44: 1, 1: 4}
```

cannot be obtained by dividing the 24 whole replicas into **two nonempty independently packed groups**, each using its own exact capacity and helper inventories. This includes disjoint concatenations of T16+T8. The theorem does *not* rule out shared owners, cross-group edits, a changed profile, modified prefix accounting, or a genuine coupled T24 circuit.

### Proof (integer arithmetic)

Each replica has capacity inventory `{8:672,16:448,32:448,48:448}` and nine helper calls, each with width counts `{4:80,5:32,7:54,8:122,9:216}`. Its unused rank mass is

```
M = 672*8 + 448*(16+32+48)
    - 9*(4*80+5*32+7*54+8*122+9*216) = 14382.
```

Use the #890/#795 signed-dual width prices `(-1,-20,-8,-2,+4)` for widths `(4,5,7,8,9)`, and capacity bonuses `(2,4,8,-13)` at capacities `(8,16,32,48)`. Let `U(r)` maximize the bonus-plus-width-price over all legal whole-helper assignments to *one* bin with unused rank `r`. Enumerating all 1163 legal choices gives:

| r | 0 | 1 | 44 | 48 |
|---|---:|---:|---:|---:|
| U(r) | 0 | 19 | -14 | -13 |
| v(r)=48U(r)+13r | 0 | 925 | -100 | 0 |

The actual sum of bin bonuses and width prices is `-3892*g` for `g` independently supplied replicas. Since `U(r)` upper-bounds each actual bin score and their unused mass is `14382*g`, every independently packed group must satisfy

```
sum_bins v(rank) >= (48*(-3892)+13*14382)*g = 150*g.   (1)
```

For a proper group of `1 <= g <= 23` replicas, let `x` of the four rank-1 bins and `y` of the one rank-44 bin belong to it. Its mass must obey

```
x + 44*y == 14382*g (mod 48),
0 <= x <= 4, 0 <= y <= 1.                               (2)
```

Modulo 6, (2) forces `x+2*y == 0 (mod 6)`, leaving only `(x,y)=(0,0)` and `(x,y)=(4,1)`. Both give zero modulo 48, so `30*g == 0 (mod 48)`, hence `g=8` or `g=16`. In *every* such partition, one nonempty group gets **none** of the unusual-rank bins. Its rank-48 and rank-zero bins provide credit zero, violating `(1)` since `150*g>0`. Contradiction.

The full T24 candidate itself passes the global necessary conditions exactly: mass `14382*24` and signed credit `4*925-100=150*24`. This is precisely why the obstruction only applies to **separability**, not global feasibility.

## Reproduce

From the repository root:

```sh
python3 -B research/complex-t24-global-coupling/verify.py
```

Expected: the checker enumerates 1163 local assignments, finds exactly four mass-compatible proper T24 partitions and rejects all four by signed credit, checks the T21 non-separability control, admits a split for a **different** abstract T24 profile, and rejects a deliberately corrupted mass. Requires only Python standard library.

No finite test is presented as a proof of full circuit or multiplication correctness. The textual modular argument supplies the scoped proof; enumeration independently checks the inputs.

## Limits and next questions

- The original T24 prefix estimate `113+18*24=545` exceeds the required strict `<512` condition; **34 real paid units** must be eliminated with validated execution semantics.
- No literal per-call placement, owner scheduling, source access, frame restoration, or recursive outer-assembly invoice is supplied.
- T21 (#890) also fails a naive independent split despite its separately verified coupled owner edits. A possible *unverified* T24 mechanism is analogous cross-component edits (e.g. T16/T8), but these are not constructed here.
- The existing T37 all-T relaxation already limits any κ gain in the unchanged family; this note only isolates one useful local construction constraint.

**Attribution:** PR #890 (Chafik Boukhalfa / chafreaky), predecessor PR #795 and subsequent T37/#942 team retain credit for the underlying inventories, prices and fixed-family frontier. Local T24 candidate and this derived scoped test were developed in a user-directed investigation with **substantial OpenAI GPT-6 assistance**; submitted from the user's fork. Contribution under this repository's Apache-2.0 license.
