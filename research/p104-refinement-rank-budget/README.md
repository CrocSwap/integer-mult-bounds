# P104 nested refinements need at least 48 added paid ranks

Identity completion in the model below requires **at least 48 added paid ranks per call**. Under the retained no-progress-credit coverage contract, the completed zero-saving moment is at least **585/584 > 1**. This excludes a positive saving within that contract, even with free scalar work and ideal idle packing.

This is a quantitative extension of [Tairitsu-Aya's PR2136](https://github.com/CrocSwap/integer-mult-bounds/pull/2136), head `9b8689e0153e038b2c1179b06026adfaa7f7593b`. Its survivor separator and 56-array unaugmented bound are not new here. The new step prices arbitrary added nested transports around arbitrary refinements of the retained intervals. The bound is not claimed sharp. There is no new supplier or kappa.

## Model and boundary

The input is the 4,058-event PR1972 channel retained by PR1991 at `research/p104-native-channel/inputs/LOWRANK-WITNESS.json`, SHA256 `0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e`. It implements the low-rank `G/2` channel, not identity.

Retain each of its 1,410 transport occurrences as a single-array obligation. Replace any occurrence `L -> U` by an arbitrary monotone nested chain between those same endpoints. Each original obligation is consumed once and cannot branch into independent arrays. Grant arbitrary valid interleaving, common-chart linear resynthesis, and arbitrary fresh source-independent storage, including same-chart copy/discard. Scalar coefficients and dirty restoration restrictions are relaxed for this lower bound. Source and final target endpoints remain fixed.

In addition, allow arbitrary **added** nested transport steps on any available arrays, including persistent buffers and new storage. A step between distinct charts has paid rank equal to their dimension difference, or a larger charge. Their total added rank is `B`. Added paths need not be globally monotone: every step is charged. Refining an original monotone interval preserves its original total rank.

Every cross-chart operation must be either a retained obligation's refinement or an added paid step. No original obligation may be removed, fused away, duplicated or credited against the added bill. A changed producer, a free cross-chart map, or a branching original descent is outside this model. In particular, the replacement mechanisms in [Discussion2131](https://github.com/CrocSwap/integer-mult-bounds/discussions/2131) and [PR2139](https://github.com/CrocSwap/integer-mult-bounds/pull/2139) are not excluded.

This differs from [Ross Richardson's PR2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127), head `befebf0f4ae7a3f69fe9c5e136262559dcac125f`, whose 96-added-transport bound keeps the original occurrences unsplit. Here arbitrary intermediate subspaces inside their nested intervals are allowed. Neither theorem justifies a new coverage credit.

## Inherited separator, checked from the source

Let `a_0,...,a_7` be the private descent survivor labels and `A` their binary span. The reconstructed survivor set is

```text
{95, 127, 243, 383, 447, 486, 500, 502}.
```

It has dimension eight. Label a chart `W` target-side, or T, precisely when it is proper and either `W <= A` or it contains at least two survivors. All other charts are R, including the full chart. This uses binary subspace membership, not ordinary dot products on compressed labels.

The verifier reconstructs literal XOR spans without importing a predecessor checker and confirms:

- 56 initial singleton sources are R and the other 48 are T.
- All 104 final target hyperplanes are T.
- The eight original descents start outside A, end in their survivor line, and their starting hyperplanes contain exactly one survivor each.
- Every upward original interval satisfies one of the following sufficient conditions.

| Condition, applied in order | Occurrences |
| --- | ---: |
| Upper chart contains at most one survivor | 701 |
| Upper chart is contained in A | 421 |
| Lower chart contains at least two survivors | 136 |
| Dimension-eight chart to full chart | 144 |

These are PR2136's separator premises, independently reconstructed here. In the first case ascent cannot enter A from outside A, and no chart contains two survivors. In the second all charts are T. In the third every proper chart is T and full is R. The last case has no strict intermediate chart. Thus no upward refinement enters T from R. Each descending refinement enters A exactly once and cannot leave it again. It therefore crosses R to T exactly once, carrying one array, irrespective of its seven paid ranks.

## Added-rank theorem

Let each register carry a `d`-dimensional vector over a characteristic-zero field containing the native constants. Vary only the 56 R-side source inputs; fix the other inputs to zero. Every initial T-side register is independent of those inputs.

Record an array whenever information crosses R to T. The original refined obligations contribute exactly eight such array positions. Each added strict transport step contributes at most one, and its paid rank is at least one. Consequently added steps contribute at most `B` positions, even when arbitrary common-chart copies, storage and feedback are allowed.

Induction through execution shows that every T-side value is a linear function of transcript entries already received. T-to-R feedback can affect later entries, but cannot increase the number of entering positions. The final target dependence on the 56 varying inputs therefore has rank at most

```text
rank(X_R -> Y) <= (8 + B)d.
```

Identity transfer on that source block has rank `56d`, so **B >= 48**. Invertible per-register native endpoint adapters do not change this rank. Granting non-restored dirty helpers only enlarges the class, so imposing restoration cannot invalidate the lower bound.

This also covers subdivided **added** rank-r intervals. A strict monotone refinement has at most r steps, hence at most r entering positions. It is unsafe to count just one crossing per added obligation: the verifier exhibits a descending path from full to zero whose side sequence is `R,T,R,T`. Its ranks are `6,2,1`, so it enters twice but pays nine ranks. The theorem counts paid rank, not endpoint side changes or the number of new obligations.

The transcript implication is a written proof, not a proof-assistant certificate. A single rank-r native child transports one whole array; it is not assumed to transport r independent arrays. Bounding its contribution by r is a favorable relaxation for the lower bound.

## Conditional complete-mass screen

Use the explicit no-progress-credit contract of [David Arias's PR2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082), head `60f4e337ffba470e09727dd435b1f1be3b67d03d`: width `m=73`, `W=8*104=832` families, `N=9` calls per replica, mandatory original coverage `72W+56N`, and no reduction of that baseline from the added transports. No chronological P104 hosting construction is asserted by this assumption.

The independently recounted local mass is `2368 = 2312 + 56`. Monotone refinements preserve it. The complete replica bound is

| Quantity | Rank mass |
| --- | ---: |
| Capacity `73*832` | 60,736 |
| Mandatory baseline `72*832+56*9` | 60,408 |
| Necessary addition `48*9` | 432 |
| Completed lower bound | 60,840 |

Thus `M(0) >= 60840/60736 = 585/584`. For every admissible child rank `0 < r <= 73` and saving `0 <= a < 1`, `(r/73)^(1-a) >= r/73`. No regrouping of this paid mass or nonnegative overhead can restore acceptance. The 48-rank requirement exceeds the `328/9` per-call headroom.

A changed coverage proof must credit **more than 104/9 rank units per call** even to make the raw moment strictly below one at this minimum added cost. In general it must credit more than `B-328/9`. This is a necessary condition, not permission to subtract that credit from idle work. A different template, removal/fusion of old obligations, or justified credit for new monotone progress needs a separate bill. Neither the rank theorem nor this conditional screen rules out all P104 suppliers.

## Reproduce

Standard-library Python, no network or producer/compiler imports:

```sh
python3.12 -I -B research/p104-refinement-rank-budget/verify.py
python3.12 -I -O -B research/p104-refinement-rank-budget/verify.py
python3.12 -I -B research/p104-refinement-rank-budget/test_verify.py
python3.12 scripts/research_package.py --package research/p104-refinement-rank-budget
```

The default verifier is read-only and compares the entire computed receipt with `EXPECTED.json`. `--out NEW_FILE` writes exclusively. The registered hook runs both assertion modes and the CLI/export tests. Source pins and task provenance are in `SOURCES.json` and `TASK.json`.

Five semantic controls reject uncharged or nonnested bridges, treating a new crossing interval as an old interval, a ninth old descent and a falsified original rank. Positive controls exhibit a real paid bypass and the two-entry descending path. Nine tests check normal/optimized replay, missing/corrupt/oversized input, receipt corruption, read-only behavior, exclusive output and the two-entry counterexample. No native phase, original scalar endpoint, chronological owners, precision/tape, all-size or full selected cold replay is newly checked. The selected record is unchanged.

## Open next questions

A useful next candidate must either remove or fuse an original obligation, or justify enough new coverage credit to overcome this bound. Start by identifying the exact displaced idle progress and a complete source/target path with independent dirty inputs. The blocker is a physical hosting/coverage lemma, not the rational mass calculation. `TASK.json` records the structured question. Computing the sharp capacity of the refinement-only model is not needed for this no-credit decision and is not proposed as a separate task.

## Credit and engineering limits

Nick Petalas prepared the added-rank implication and conditional budget extension. Tairitsu-Aya/PR2136 supplies the interval separator. Ross Richardson/PR2127, David Arias/PR2082, Jeremy Diviney/PR2113 and Adam Gall/PR2090 supply the earlier access cuts. Rohan Arun/PR1972 supplies the channel, Chafik Boukhalfa/PR1991 its native realization, and Adam Gall/PR1940 its schedule. Geometry credit continues through Josie Elliston/PR1071, Ali Romman/PR1125 and the lineage retained by PR1991. The coverage model retains Dominik Scholz's paired-chain model, Sagar Thakrar's PR1012 and Douglas Colkitt's PR1240. No predecessor files are modified or vendored. Apache-2.0.

The verifier uses no recursion and has functions below 60 lines. Source geometry is fixed to nine bits, 280 persistent roles and 4,058 events. Python's managed allocation is a Power of Ten rule-3 deviation; live space sets contain at most 512 labels and at most 1,410 transport records are retained. Tests use one bounded subprocess at a time with a 30-second timeout, scoped temporary storage and one explicit dynamic module import. The verifier's four indirect control calls have fixed local targets. These are scoped rule-8/9 deviations; no runtime registration or external code loading is used. Follow up with direct calls if that fixed control table changes. Python warnings are errors in the registered CLI tests. No static type checker or linter was available locally; no repository-wide configuration was changed.
