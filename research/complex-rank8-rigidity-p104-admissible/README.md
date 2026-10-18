# Rank-8 masked decoders are gauge-rigid on the 896 admissible P104 units (no new κ)

**Status: scoped structural result. No κ claim, no construction.** It extends PR1212 (burntout76,
`research/complex-rank8-decoder-rigidity/`, open, head `57099cb5`) and depends on that PR's zero-exclusion
lemma. It is independent of PR1389, the type-(4,4) and P111 cases.

PR1212 proves the following in PR717's E-graph (masked) model. Every rank-≤8 solution K of
`K_ii = 4, K_ij = 0` on orthogonal live pairs, with odd entries free, is `D(2G)D⁻¹`. As a result, decoders
with exactly eight costly terms keep PR968's floor. Its PROOF.md §10 leaves the **896 admissible P104 units**
open (PR717's P104 among them). On its pivot there, four classes keep only two live rows, and Lemma 5 then
leaves a one-parameter family inside each.

This package closes that gap ([PROOF.md](PROOF.md)) with one new lemma:

- **Lemma 9 (propagation).** Lemmas 5–6 already fix the global scaling `g` on the 22 complete classes, since
  all 14 blocks carry one. A two-row line `i` then needs no in-class argument. Each witness `j` in a complete
  class with `T_i ∩ T_j = {k, k′}` turns (E2) into `a_ik ε_ik / g_k = a_ik′ ε_ik′ / g_k′`, and the reverse
  order gives the same for `b`. If the witnessed pairs connect `T_i`, then `a_i ∝ ε_i ∘ g` and `b_i ∝ ε_i / g`,
  and (E0) fixes the product. On this unit every two-row line has all six pairs witnessed, with 40 witnesses
  per line.

**Consequence.** In the E-graph model, every decoder with exactly eight costly terms has `cst ≥ 56` on every
admissible P104 unit. PR717's P104 decoders attain it.

Together with PR1212 (336 type-(2,2,2,2) units) and PR1389 (28 type-(4,4) units), this covers all 1260 P104
frame complements. That combination is conditional on PR1389, which is unmerged and unreviewed.

## Reproduce

From the repository root, Python 3.10+, standard library only, about 0.1 s:

```sh
python3 -I -B research/complex-rank8-rigidity-p104-admissible/verify.py
```

Expected final line:

```text
PASS_COMPLEX_RANK8_RIGIDITY_P104_ADMISSIBLE: checks 15; classes 22 complete + 4 two-row; 8 two-row lines propagated; floor 56; zero exclusion cited from PR1212
```

To also replay PR1212's zero exclusion for this unit (about 15 s), first make a checkout of PR1212's head.
The verifier checks the git blobs of its `verify.py` and `proof-P104-11111111.drup`. It then runs PR1212's
verifier and matches the unit and pivot by root vectors:

```sh
git fetch origin pull/1212/head && git worktree add --detach /tmp/pr1212 57099cb5
python3 -I -B research/complex-rank8-rigidity-p104-admissible/verify.py --pr1212-dir /tmp/pr1212
```

The last line then ends `... replayed from PR1212` with 22 checks. The replay covers
`G.P104-11111111.zero-exclusion`, `G.P104-11111111.class-witnesses`, `G.frame-orbits` and
`G.pr717-p104-orbit`.

The verifier is independent of PR1212's code: it has its own E8 model, classes, witnesses, gluing and
propagation. It recomputes the orbit type of the punctured frame. It cross-checks Lemma 9's algebra on
the actual (E2) equations (rank 3, with the gauge vector as kernel). The four controls show that:

- the in-class conditions admit a non-gauge two-row solution;
- witnessed cross-block equations reject that solution (28 of 40 fail);
- removing the witnesses at one column leaves a 2-dimensional family;
- a perturbed entry breaks (2).

## Not covered

- **Nine or more costly terms**, including PR717's mixed-β problem. Rank-8 rigidity says nothing about
  rank-≥9 solutions of (E).
- **The intermediate punctures P105–P110.**
- **Zero exclusion** is PR1212's DRUP result, replayed but not re-derived. The flat classification premise
  (F6) inherited through PR968 is unchanged.
- The written proof has had no independent human review. There is no construction and no κ change, and
  every condition of the selected record is unchanged.

## Open next questions

**Intermediate punctures P105–P110.** This matters because, with this package, PR1212 and PR1389, rigidity
holds on P120, P112, P111 and every P104 frame complement. The units in between are the remaining
eight-term gap in the masked model. A feasible first step: enumerate the FRAME0-stabiliser orbits of 2–7
line punctures of P112. For each orbit, pick a pivot and test (I3) and (I4) on the complete classes, then
Lemma 9 connectivity for the other live lines. Lemma 9 needs no in-class equations, so incomplete classes
cost nothing once `g` is fixed. The blocker: zero exclusion is a separate DRUP certificate per unit
(PR1212's CNF builder plus python-sat), and the orbit count is not yet known. See [TASK.json](TASK.json).

## Credit

- **burntout76 / Brett Halligan (PR1212):** the theorem, the proof skeleton and every lemma reused here,
  zero exclusion and its DRUP certificate for this unit, the transport, the pivot, and the §10 record of
  this gap.
- **themilkman216 (PR968):** the eight-term floor.
- **DreamingOfClouds (PR717):** the E-graph model and the P104 decoders.
- **Navinor (PR1292):** local rigidity on all P104 units.

Prepared by JosieElliston with substantial assistance from Claude Opus 5.5 (Anthropic) via Claude Code,
covering the proof, verifier and write-up. Apache-2.0.
