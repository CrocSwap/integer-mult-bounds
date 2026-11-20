# Independent P104 chart-cut replay

The replay qualifies three exclusions on the two pinned native words. The result earns zero signed credit toward the enrolled target. Both complete signed invoices match the fixed inputs to the rebalanced binary cutoff. [PR #7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830) · [PR #7831](https://github.com/CrocSwap/integer-mult-bounds/pull/7831)

| Scope | Exact obstruction |
| --- | --- |
| Rational chart 282 with all five original reader payloads held | Chart 282 has no original inputs. Removing slot 90369 leaves four scalar arrivals against five independent demanded rows. With 90605 and 90604 fixed, the first three readers already require three quotient directions by clock 2828. |
| Rational two-retarget topology with two chart-282 payloads released | At fixed event order, four funded scalars cannot restore three chart-288 receipts and two public terminals. Pooling all 74 fixed exterior stock rows gives rank 62, which rises to 67 after adding the five demands. |
| Binary chart 266 and one of five saved peers | The five protected cuts have six fixed original crossing arrivals each. The first payload has zero coefficient at public input 252 and the peer return stays inside. Four required exterior rows distinguish that input. At least three of those rows survive any single funded payload edit. |

## Rational reader and exterior checks

The determinant on public axes 11, 21, 62, 129 and 142 is `−615/37888` for both the five original arrivals and the five demanded rows. The first three readers have quotient determinant 1 in the original arrival coordinates modulo the two held arrivals. The checker enumerates each original reader, its clock, literal coefficients and downstream consumers. Releasing 98703 or 91131 alone leaves quotient rank three. Releasing both lowers the local quotient rank to two with 90605 and 90604 still held.

The exterior extension fixes receipts 89198, 91110 and 94251 at chart 288, and restores public terminals 154930 and 154935. It permits the eight direct consumers of released slots 98703 and 91131 to change, along with every physically reachable later send. The forward reachability check grants such sends all earlier same-chart inputs. It independently reconstructs the chronological fixed stock and confirms that no new receipt feeds back into chart 282 or the donor and retarget charts 3, 273, 276, 278, 288 and 304. It checks the 88 identity, all readers of vacated 94019 and source-side reader 89187.

On five exact public-input probes, the 74 fixed stock forms all vanish and the five demanded values form the identity matrix. Four arbitrary rational-linear channels on these inputs have rank at most four. Releasing either named terminal gives a rank-four control for the pooled exterior condition alone. The four-channel chart-288 restoration control also misses a named exterior terminal. A fifth grade-three arrival can carry old 90369 on its original route. Substituting the two equal restoration rows verifies all 1,289 terminal operators and 5,704 retained paid values on the full public domain. That restoration is a scalar-operator control and carries its stated signed cost.

## Binary ingress and the early-payload condition

The five saved peers are 326, 439, 457, 475 and 493. In each case the new return to 266 is internal to the two-bank cut. The new first send from chart 11 must retain the line represented by `x9 + x247` modulo the four retained arrivals. That line and the retained stock all vanish on the unit input at coordinate 252. The second desired line is represented by `x11 + x252`. The replay derives all original paid and terminal reader expressions from the tape, including the independent grade-four packet 3553 restoring output owner 411.

If the one recoded old packet enters the cut, its external producer receives only unchanged old arrivals, even when events are retimed. The two replacement packets end at chart 266 and the recoded crossing ends inside the cut, so none delivers a new early payload to that producer. Each row in the external producer's *whole* original stock vanishes on input 252. If the recode ends outside the cut, all six original crossing payloads stay fixed. In either case the two banks see identical stock on zero and on the unit input. Of the four required nonzero rows leaving the cut, the single funded edit can release at most one.

The control at chart 507 checks that packet 1366 already carries input coordinate 11. Adding a new input-252 component there would allow a recoded packet 2292 to import it. This is a test of the boundary condition. It does not show that such an early input is available in the original stock, or that changing both payloads would solve the operator. The original 753 also breaks the cut when restored. A proposal that allows another changing crossing payload, changed endpoints, an unconstrained first line, or a different peer requires its own ingress proof.

## Complete signed price at the enrolled target

The model charges (P_g=g^{1-κ}) and debits surrendered productive targets at the same tariff. At κ = 0.003889928046155, the two interventions have the following counterfactual prices. The baseline shortfalls are positive numbers.

| Complete bill | Calls | Baseline shortfall | Nominal credit | Margin after one extra grade-one job per call |
| --- | ---: | ---: | ---: | ---: |
| Rational | 48 | 9.9729391999983059261 | 48.4218097282314662394 | −9.5511294717668396868 |
| Binary | 36 | 3.8511918070636000041 | 35.7333159277265461170 | −4.1178758793370538871 |

The rational paid delta is `{3: -48, 5: -48, 7: +48}`. Its demonstrated grade-three shadow costs more than the nominal saving by 94.9641160598864314390. The binary paid delta is `{2: +36, 3: -36}`. The unchanged productive and ordinary bills are baseline inputs. Losing one grade-one productive target per binary call gives the same signed result as introducing the extra grade-one job per call.

The independent tariff calculation uses integer square-root bounds on a 224-bit dyadic grid. The replay checks both directed signs of each published raw crossing and prices both unchanged bills at #7831's qualified lower 0.00387992802506 and the binary raw upper 0.003879928046155. The pinned cutoff uses 416 factors, paid cutoff `10^416`, productive floor `16^416` and logarithm power 44. Its separate finite replay is bundled as a receipt. This package verifies its input words and invoices and does not rerun the tensor theorem, the Lean artifact, or the outer analytic application. The enrolled target remains 0.00001 above the binary raw upper.

## Scope

The rational exterior result assumes literal endpoints, relative order, the named retargets and the stated protected receipts. The binary result covers precisely the five saved S8 paths, the fixed first line and one changed old payload at fixed endpoints. Neither proof qualifies a changed physical program, recoding across the different caller visits, or a wider search over return charts. The full signed bills establish the prices of the specified controls. Physical restoration, compiler width and ordinary-cost qualification of new words would be separate obligations.

The rational retarget follows Clear1nsight’s earlier chart-278 observation. Related studies cover the adjoint chart-3 receiver, other chart-278/288 contracts and Ali Romman’s independent scalar broadcast. [PR #7795](https://github.com/CrocSwap/integer-mult-bounds/pull/7795) · [PR #7804](https://github.com/CrocSwap/integer-mult-bounds/pull/7804) · [PR #7814](https://github.com/CrocSwap/integer-mult-bounds/pull/7814) · [PR #7818](https://github.com/CrocSwap/integer-mult-bounds/pull/7818) · [PR #7819](https://github.com/CrocSwap/integer-mult-bounds/pull/7819) · [PR #7793](https://github.com/CrocSwap/integer-mult-bounds/pull/7793)

## Reproduction

Python 3.10 or newer, with only the standard library. From this directory:

```sh
sh reproduce.sh
```

`SOURCE-LOCK.json` records the commit-pinned byte inputs and SHA-256 values for each local frozen receipt. `review.py` authenticates them before executing. It reconstructs rational rows by forward substitution, derives fixed exterior stock by a forward reachability pass, and checks the rational minors directly by the Leibniz formula. The binary tape uses chart-local packet expressions to reconstruct the public coefficients. `REVIEW.json` contains the independent result. The three producer receipts and the prior independently qualified cutoff receipt are under `receipts/`.

The clean replay from a standalone temporary copy matched `REVIEW.json` byte for byte. It used 11.55 CPU seconds and peaked at 338,280 KiB RSS. Resource measurements are in `receipts/`.

Goal `goal-c9b923e487624c27b9078b5182fc7dee`, step `s13-independent-cuts`, binding receipt `progress.goal-c9b923e487624c27b9078b5182fc7dee.00000209`. Clear1nsight and the original archive contributors retain credit for the pinned carriers and prior cut evidence. Dugongue prepared the unchanged cutoff comparison. OpenAI Codex prepared the independent verification.
