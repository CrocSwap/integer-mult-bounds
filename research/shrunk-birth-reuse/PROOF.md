# Birth-read slot reuse on shrunk, saturated frames

Base: PR125 (`research/shrunk-frames`, head dda535b) on PR114 `7dfa16edfa5d6452f2b10dadcbef20d26222827e`. Its complex profile, certificate and PR117 DAG are pinned by SHA-256 in `BASE_INPUTS.json`. The birth-read reuse operation, its lemma check, matcher, readout bill, literal frame audit and assembly checker are James Chang's PR124 (`f36782865dfe81abaa40254e8f41b8ccb3c54556`). They are used here on different frames.

PR124 keeps all of its retained hypotheses: analytic, exact-recovery, prime, whole-residual, complete-row and fixed-tape. Under those hypotheses,

    T(n)=O(n(log n)^(1−kappa)),
    kappa=11239534209971/10^17=0.00011239534209971.

This is an author-checked conditional draft. Independent review is pending.

## What changes relative to PR124

PR124 matched dead donor roles to deferred recipients on PR118's frames. Those had 3,020 deferred readouts under PR110's greedy placement and the maximal lifted frames. This package keeps the DAG, carrier matching and 28,705 virtual roles. It replaces the frames with PR125's.

1. **Saturated placement (PR114).** Candidates are ordered by 2^dim/targets². A degenerate target intersection keeps its regular part instead of being discarded. This gives 4,706 deferred readouts.
2. **Shrunk frames (PR125).** In one forward pass, U_x is replaced by Lb_x = label(x) + Σ U_pred when four conditions hold:
   - Lb_x is nondegenerate;
   - Lb_x lies inside U_x;
   - Lb_x lies inside every successor frame;
   - the local one-child cost of the role chains holding x drops.

   The pass shrinks 16,031 frames. Lb_x ⊆ U_x ⊆ lifted kernel and Lb_x ⊇ every predecessor frame. So PR110's frame contract holds: label ⊆ U ⊆ kernel, nondegenerate, and monotone along successors.

`build_frames.py` rebuilds both steps from scratch and has no upstream imports. It checks every role chain for nesting and nondegeneracy. It reproduces PR125's complete complex histogram bin for bin, with 24,792 lifted additions after shrinking.

PR124's operation is applied to these frames unchanged:
- Choose an old role A whose last forward gate and every terminal read are finished in phase one.
- Its final frame E must lie in σ_B for an untouched deferred recipient B.
- Raise A to σ_B.
- Feed A's actual value into B's existing negative readout.
- Route B's future virtual life through A.

The birth-cut identity cancels every dirty offset (`check_birth_lemma.py`). Each pair removes children 24−e and 552+s and adds s−e. It also removes one physical role. Weighted rank drops by 576. The pair improves the paid moment by strict concavity and majorization. A residual with equal characteristic vector and E≠σ_B is excluded, which avoids an unproved alternating normal form.

## Actual witness

| | PR124 | this |
|---|---:|---:|
| deferred readouts | 3,020 | 4,706 |
| shrunk frames | — | 16,031 |
| reuses | 2,106 | 2,108 |
| R | 26,599 | 26,597 |
| W | 115,865,904 | 115,857,808 |
| weighted rank | 66,736,898,624 | 66,732,235,328 |
| complex saving | 11040781/10^11 | **11242073/10^11** |
| κ | 1.1038332094346e-4 | **1.1239534209971e-4** |

The largest child is 574 of 576. The deficit 1,862,080 is unchanged.

**Literal frame audit.** The forward word and the reversed/sign-negated/bank-exchanged/complemented word each have 234,516 frame transitions and 24 copied centres. Their complete paid histograms agree with the matcher's histogram bin for bin.

**Scalar bill.** Old-readout responses depend only on the scalar word, which is unchanged. Exact backward integer propagation therefore gives the same bill as PR124, with the same conservative global scalar group G=3113921927424.

**Assembly.** `check_assembly.py` is PR124's exact checker, with the new profile pinned. It checks:
- all three strict moments;
- the 47 inequalities and seven final margins;
- the row stock coefficient 15561 at degree 32000;
- rejection of the next 10^-17 κ grid point;
- added here, rejection of the next 10^-11 complex grid point.

## Scope

PR124's retained hypotheses all remain explicit:
- copied stream and residual-to-child normal form;
- translated gauges and routing;
- all-size transfer and the analytic estimates;
- the inherited stopped-product bit supplier.

The finite checks verify the shrunk frames, placement and reuse pairs on the actual witness. They do not prove a new general theorem. This is neither an unconditional theorem nor a practical-time or global-optimality claim.

Credit:
- James Chang / jamesyc: PR124 birth-read reuse, its lemma, matcher, readout bill, literal audit and assembly checker, developed with OpenAI assistance.
- eumemic: PR117 DAG and PR114 saturated placement.
- Rohan Arun: PR118.
- Avi Eisenberg: PR110.
- Swapnil Jain: round-seven bit word and deferred readouts.
- icekylinx: stopped-product interfaces.
- Zhihao Chen and all contributors named in the base NOTICE/SOURCES.

The shrunk-frame step and this composition were prepared by Joel Pulikkan with Anthropic Claude assistance.
