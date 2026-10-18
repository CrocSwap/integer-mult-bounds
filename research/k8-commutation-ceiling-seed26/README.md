# Commuting reorders plus free frames cannot lift the selected k8 ceiling by 5%

**Scoped obstruction with an exact certificate. No new κ, and no existing check is changed.**

- Track: 20–39 (complex supplier), assignment seed 26, drawn with the OS CSPRNG via Python `secrets`.
- Card: `complex-rank-shape-decoder`, with the scope **refined** in [TASK.json](TASK.json).
- Base: `0fdd7d82`. The selected record frontier1094 is unchanged.

## The question

Two merged scoped results bound the selected gauge44/k8 complex word (`c2b29430`; 3,451 A + 1,846 B + 116 tail gates):

- **#1671** (bitplane) frees **every frame** while keeping the **chronology fixed**. No assignment lowers the paid moment.
- **seed27** (woklerx) frees **commuting-ADD order** while keeping **frame slots fixed**.

Neither covers both at once, and PR1671 lists that combination as open question 1. This package takes the joint class:
- every within-segment reordering of A, B and the tail that keeps the order of non-commuting gates;
- with every legal nested frame assignment under PR1671's rules (starts, ends, charged pins, cone caps, operand-shared frames).

It asks whether any member lifts the packing ceiling by the card's 5% gate.

## Answer: no

At a* = (21/20)·a_hi, with a_hi = 1690054109089/10¹⁵, an exact Lagrangian lower bound on every member's bill is

**bill_lo − 1 = +2.146289027469049 × 10⁻⁴ > 0.**

So every member's ceiling is below a*, and none lifts it by 5%. A second certificate at (1007/1000)·a_hi gives +4.86 × 10⁻⁶ > 0, so no member lifts the ceiling by even **0.7%**.

| Bound at a* | Value | Verdict |
|---|---|---|
| The selected word itself | 1.000245413040 | (member) |
| Stage 1, chronological intervals | 1.000227868002 | rejects (PR1671's case) |
| Stage 1, commutation intervals (decoupled) | 0.999971231189 | **does not reject** |
| Stage 2, Lagrangian coupling (`LAMBDA.json`) | 1 + 2.146289 × 10⁻⁴ | **rejects: class excluded** |
| Stage 2 at 1.007·a_hi (`LAMBDA-1007.json`) | 1 + 4.86 × 10⁻⁶ | rejects |

Coupling the two operands of each ADD gate is what decides the question. The per-register (decoupled) bound leaves room once the chronology is relaxed.

## How ([model.py](model.py), [PROOF.md](PROOF.md))

1. **Commutation.** Elementary row operations commute when:
   - two ADDs t←t+cs and t′←t′+c′s′ have t ≠ s′ and t′ ≠ s;
   - they are two SCALEs;
   - or they share no register.

   This rule is checked against exact rational composition, in both orders, on all **109,388** same-register gate pairs. Of the 9,092 adjacent within-segment pairs, 4,519 commute.
2. **Intervals.** A dependency DAG joins non-commuting same-segment pairs, all cross-segment same-register pairs, and the starts, pins, cap nodes and ends. It gives every gate an interval [lo2, hi2] that contains its frame in every member under every legal assignment.
   - Two implementations agree on all 5,413 gates: propagation, and a closed form over ancestor and descendant closures.
   - In chronological mode both reduce to PR1671's intervals exactly.
   - Forced gates drop from 3,672 to 2,979, and 1,391 intervals change.
   - The word's own frames lie inside.
3. **Stage 1.** For each register, the cheapest chain of subspaces from its start to its end that passes through every item's interval. The order inside the register is free, and an item's first entry must stay inside its upper end. This lower-bounds the register's paid climbs in every member.
4. **Stage 2.** Each free ADD gate has two copies, one on each register. They are coupled by dimension-linear multipliers, +λ on the target copy and −λ on the source copy. The target copy is charged at its entry point and the source copy at its exit point. Operand agreement cancels the multipliers in any real member, so the sum of the per-register optima stays a lower bound for every λ.
5. **Exact arithmetic.** The child costs use `ceiling.child_cost`'s lower enclosures, which lie on the 2⁻²⁵⁶ grid, and the multipliers are k/2⁴⁰. The bound is therefore computed in exact integers, and the bill is compared with 1 exactly. The certificates store the integers k:
   - 1,008 nonzero values in `LAMBDA.json`;
   - 962 in `LAMBDA-1007.json`.

   [discover.py](discover.py) can regenerate such multipliers by float subgradient ascent. The verifier never imports it.

## Controls

- **Commutation rule.**
  - The rule agrees with exact composition on every pair.
  - A wrong rule (one that ignores t = s′) disagrees.
- **Intervals.**
  - The chronological intervals equal PR1671's.
  - The two interval implementations agree.
  - The word's frames lie in the commutation intervals.
- **Subspace enumerators.** Two enumerators (closure and reduced echelon) agree on every distinct interval. The number of subspaces of F₂^k is 1, 2, 5, 16, 67, 374 and 2,825 for k = 0…6.
- **The given word.**
  - It reproduces PR1671's profile {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}, and the ceiling bracket.
  - The Stage-2 bound stays below the given word's own bill, as it must, since that word is a member.
- **Toy exhaustive check** ([toy.py](toy.py)).
  - Over 150 random small words, the check enumerates every linear extension and every nested frame assignment. 93 of those words have several orders.
  - The intervals contain every legal assignment.
  - The Lagrangian bound never exceeds the exact minimum for random multipliers.
  - The invalid rule (charging negative multipliers at entry) is caught.
- **Certificate files.** A multiplier on a forced gate, or a certificate for a different word, is refused.
- **Coupling is what rejects.** With λ = 0 the bound does not reject in the commutation class.

[test_package.py](test_package.py) has 13 tests.

## Scope

**Covered.**
- Every within-segment linear extension of the A, B and tail dependency orders, with coefficients unchanged.
- Every frame assignment under PR1671's contract.
- Every exponent ≥ the certified one.

**Not covered.**
- Moves across segments: across the cut, or into and out of the tail.
- Coefficient-rescaling rewrites.
- Changes to the cut, precondition, cleanup, compensation, pins or endpoints (for example `selected-k8-unrestricted-ends`).
- New child interfaces: fanout (open #1865), C3 gathers (Discussion 2032), and rank-sum children.
- Open #1186's different cost model.
- Other words.
- A lift below 0.7%, which is neither shown nor excluded.

**No κ.**

## Reproduce

```sh
python3 -I -B research/k8-commutation-ceiling-seed26/verify.py        # about 30 s; PASS_K8_COMMUTATION_CEILING
python3 -I -B -m unittest discover -s research/k8-commutation-ceiling-seed26 -p test_package.py
python3 scripts/research_package.py --package research/k8-commutation-ceiling-seed26 --check-only
python3.12 scripts/research_package.py --package research/k8-commutation-ceiling-seed26
```

It needs standard-library Python 3.10 or later, and imports merged PR1671 code with its digests pinned. It was run on Python 3.12.15 and 3.14.8 (macOS 26.5, arm64).

## Open next questions

1. **Does the 0.7% band contain a real reorder?**
   - Why it matters: the certificates exclude 5% and 0.7%, but not smaller lifts. A concrete reorder in that band would be the first gain from commutation.
   - First step: run `discover.py` at 1.006·a_hi, take the registers with the most slack, and replay a nominated reorder through PR1671's retained `audit_local.py`.
   - Blocked by: none.
2. **Does allowing moves across segments change the answer?**
   - Why it matters: the class keeps the cut. 217 adjacent commuting pairs straddle a segment boundary.
   - First step: add the cross-segment commuting edges as optional, and recompute lo2/hi2 and the Stage-2 bound.
   - Blocked by: the cut's compensation semantics (#1128-style restoration).
3. **Can a new child interface (fanout, gathers) beat the class ceiling?**
   - Why it matters: rank-shape gains need non-commuting rewrites or new children, not reorders.
   - First step: price #1865's fanout children inside this bound's per-register DP.
   - Blocked by: a merged fanout contract.

## Relation and credit

- **#1671** (bitplane, Gareth Davidson): the complete frame ceiling with fixed chronology. Its model, code and word are imported here with digests pinned.
- **seed27** (woklerx): commuting frame slots.
- **#1817** (JosieElliston): diagonal batches under register commutation.
- **navinor** (Aaron Wang): the frame method and `frame_model.py` (`complex-x4-frame-bound`).
- **`ceiling.py`:** `complex-local-word-ceiling`.
- **Related open work:** #1186 (mdumitrean), #1865 (1337isnot1337) and Discussion 2032.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic) via Claude Code.
- Parallel read-only scout and judge subagents selected the question; both judges ranked it first.
- Reader subagents and a synthesizer specified the model, and found that operand coupling decides it while the proposed precedence strengthening adds nothing. Their prototype bills replaced the scout's unreproducible figures.
- The package code, the certificates and the controls were then written and checked.

No claim was posted to Discussions. New material is Apache-2.0.
