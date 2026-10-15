# Concentrating eight source-partner corrections away from the cut

The local result is a pair of explicit words with the same 422-helper inventory as PR2588 and a strictly smaller recurrence moment. Their entire paid-profile difference is

\[
\boxed{\Delta=4(H_8-H_7-H_1)}.
\]

Here \(H_d\) denotes one formal charge of degree \(d\), not the number of such charges. The improvement comes from changing which helpers the eight recovered sources replace. It removes four center splits while retaining every source-restoration, target-correction, frame, and cleanup cost.

This note proves the local transformation and its compatibility with a width-preserving owner allocation. The final numerical endpoint and complete finite admission are separately bound by `CLAIM.json`, `evidence/FULL-RESULT.json`, and `evidence/OUTER-LEDGER.json`. The publication verifier requires these records and their exact profile bindings; `--discovery` deliberately proves less.

## 1. Objects, predecessors, and claim

A local word has source registers \(0,\ldots,111\), target registers \(112,\ldots,223\), and initially numbered helper roles \(224,\ldots,703\). Write \(x_r\) for the independent original value of source register \(r\), and \(y_t\) for the target at register \(112+t\). The desired map is \(y_t\leftarrow y_t+x_t\), with non-target live inputs restored. Values may be vectors. Scalar operations are exact dyadic operations, and \(K_G\) denotes the invertible rank-zero chart operator induced by a recorded invertible \(9\times9\) binary matrix \(G\).

Frames are subspaces of \(\mathbb F_2^9\). A monotone increase of frame dimension by \(d\) incurs \(H_d\); a recorded rank-zero chart change carries one frame to another of equal dimension. A helper's hosting width is its terminal dimension minus its entrance dimension. Integers such as `30` and `45` below encode binary vectors, so “line 45” means \(\langle45\rangle\).

The source-partner restoration mechanism is [PR2530 by zxv](https://github.com/CrocSwap/integer-mult-bounds/pull/2530). The comparison words and complete 422-helper interface are [PR2588 by Jeremy Kothe](https://github.com/CrocSwap/integer-mult-bounds/pull/2588). The construction uses [PR2436's lifted-target mechanism](https://github.com/CrocSwap/integer-mult-bounds/pull/2436), the [PR2462 supplier](https://github.com/CrocSwap/integer-mult-bounds/pull/2462), and the preceding PR2322/PR2312 lineage. Exact heads, source hashes, and retained notices are in `SOURCE-PINS.json`, `PREDECESSORS.json`, and `vendor/`. The new local contribution is the following simultaneous reassignment, not the recovery mechanism itself.

| Recovered source \(r\) | Partner | Helper replaced in PR2588 | Helper replaced here | New operator ID |
| --- | --- | --- | --- | --- |
| 49 | 33 | 656 | 680 | 51 |
| 83 | 74 | 657 | 681 | 52 |
| 98 | 85 | 658 | 682 | 53 |
| 101 | 55 | 660 | 684 | 54 |
| 68 | 4 | 632 | 688 | 55 |
| 80 | 88 | 596 | 689 | 56 |
| 88 | 80 | 600 | 690 | 57 |
| 31 | 12 | 633 | 692 | 58 |

Both provider words use this table. Their original 50 chart operators keep their IDs. The candidate words are `inputs/candidate/eight-alias-base.json.gz` and `eight-alias-extra.json.gz`; decompressed content hashes, rather than regenerated compression headers, bind the mathematics.

## 2. Recovering the eight sources

Let \(R_r\) denote the current contents of register \(r\). At the indicated retirement boundaries, the retained word has the following exact source-row identities. These identities hold before introducing the new helper substitutions.

For \((r,p)=(49,33),(83,74),(98,85),(101,55)\), the existing first-axis restoration leaves

\[
R_r=x_r+x_p,\qquad R_p=x_p.
\]

Append \(R_r\leftarrow R_r-R_p\), obtaining \(R_r=x_r\). These additions occur after the source's final original B-phase use.

The other four recoveries use mixed partners; treating their partners as already pure would be incorrect:

\[
\begin{array}{c|c|c}
\text{source}&\text{rows before recovery}&\text{recovery}\\\hline
68&R_{68}=x_4+x_{68},\ R_4=(x_4-x_{68})/2
   &R_{68}\leftarrow R_{68}/2-R_4=x_{68}\\
31&R_{31}=(x_{31}-x_{12})/2,\ R_{12}=x_{12}+x_{31}
   &R_{31}\leftarrow R_{31}+R_{12}/2=x_{31}
\end{array}
\]

For the pair \((80,88)\), initially

\[
R_{80}=x_{80}+x_{88},\qquad R_{88}=(x_{88}-x_{80})/2.
\]

The ordered additions

\[
R_{88}\leftarrow R_{88}+R_{80}/2=x_{88},\qquad
R_{80}\leftarrow R_{80}-R_{88}=x_{80}
\]

recover both values. The order matters. Each recovery occurs at an existing rank-four frame and before the relevant partner's later handoff. No old source use is skipped or moved through a changed source value. At every new positive B-phase warp, the lender is therefore exactly its own original input.

These are algebraic identities over arbitrary inputs, rather than tests on selected values or integer sizes. The literal source rows and retirement positions are also checked against the pinned words by the complete symbolic replay.

## 3. Substitution and the concrete target correction

For each row of the assignment table, delete the replaced helper's early target-only echo reads and use the recovered source register for that helper's subsequent B-phase occurrences. Before its first write, apply its new chart operator. Put

\[
q_r=K_r x_r,
\]

where \(K_r\) means the operator ID in the table. A replaced helper now carries its subsequent linear computation with an additional incoming value \(q_r\). Thus, for example, helper 680's first update becomes

\[
R_{49}=q_{49}-R_{285}.
\]

The four sources \(49,83,98,101\) enter the frame
\(F_A=\langle407,66,36,9\rangle\), and \(68,80,88,31\) enter
\(F_B=\langle258,130,85,45\rangle\). Both have dimension four and contain line 45. Each recovered source frame \(U_r\) has dimension four and contains its original port line. Choose a basis of \(U_r\) beginning with that port vector and a basis of \(F_A\) or \(F_B\) beginning with 45; extend both to bases of \(\mathbb F_2^9\). Mapping the first basis to the second gives an invertible \(G_r\) carrying \(U_r\) to the required frame and the original port line to line 45. The recorded maps are explicit instances of this construction.

The substitutions need compensation: a recovered source is not a zero scratch value. Tracing the retained target-affine suffix gives the following complete additional target response before installing the new prelude:

\[
\begin{array}{c|l@{\qquad}c|l}
t&\text{response}&t&\text{response}\\\hline
14&q_{83}+q_{98}&43&q_{80}-q_{31}\\
41&q_{83}-q_{101}&78&q_{80}+q_{88}\\
52&q_{49}+q_{101}&99&q_{68}+q_{31}\\
106&q_{49}+q_{98}&104&q_{68}+q_{88}
\end{array}
\]

All other new target responses vanish. The same table holds for both providers. It is a linear identity: its columns are the propagated responses to the eight independent incoming symbols \(q_r\).

The correction must account for subsequent mixing of targets, not merely negate this table at the wrong boundary. For target order \((14,41,52,106)\), the remaining target-affine suffix carries an early correction vector by

\[
M_A=\begin{pmatrix}
1&0&1&0\\0&1&0&1\\1&0&-1&0\\0&1&0&-1
\end{pmatrix}.
\]

For target order \((43,78,99,104)\), it carries it by

\[
M_B=\begin{pmatrix}
1&0&0&1\\0&1&1&0\\0&1&-1&0\\1&0&0&-1
\end{pmatrix}.
\]

These blocks have no response into targets outside their displayed sets. With source orders \((49,83,98,101)\) and \((68,80,88,31)\), respectively, install the early corrections

\[
C_A=\frac12\begin{pmatrix}
-1&-1&-1&-1\\-1&-1&-1&1\\1&-1&-1&1\\1&-1&1&1
\end{pmatrix},\qquad
C_B=\frac12\begin{pmatrix}
-1&-1&-1&1\\-1&-1&-1&-1\\1&-1&-1&1\\1&-1&1&1
\end{pmatrix}.
\]

Direct multiplication gives

\[
M_AC_A=\begin{pmatrix}
0&-1&-1&0\\0&-1&0&1\\-1&0&0&-1\\-1&0&-1&0
\end{pmatrix},\qquad
M_BC_B=\begin{pmatrix}
0&-1&0&1\\0&-1&-1&0\\-1&0&0&-1\\-1&0&-1&0
\end{pmatrix}.
\]

These are exactly the negatives of the response table. Therefore every new target error cancels.

Each column is physically expressed in the same lifted-target manner as PR2436/PR2530: at the beginning of A, temporarily apply \(K_r\) to source \(r\), perform the four indicated target additions at line 45, then apply \(K_r^{-1}\) to restore the source and its original port frame. These prelude pairs leave the non-target input state unchanged. Since no non-target operation reads a target, the corrections cannot disturb the later source or helper computations.

## 4. Twelve target levels and the exact bill

The complete target-level map is now

\[
\begin{aligned}
\langle30\rangle &: \{23,34,50,108\},\\
\langle45\rangle &: \{14,41,43,52,78,99,104,106\};
\end{aligned}
\]

all other targets are at the zero frame at the cut. The first four are inherited lifted targets. The eight new line-45 targets are not served by any center COPY in the cut. Their corrections therefore add no center split.

Every center starts at rank eight. The actual target readers give exactly these paths:

| Centers | Descending private-copy path | Charge per center |
| --- | --- | --- |
| 92, 224, 240, 9 | rank 8, line 30, zero | \(H_7+H_1\) |
| 57, 81, 11, 256 | rank 8, zero | \(H_8\) |

PR2588 splits all eight centers as \(8\to1\to0\). The candidate cut changes its bill from \(8H_7+8H_1\) to \(4H_7+4H_1+4H_8\). Accounting for the rest of the word is necessary: A saves eight \(H_1\) charges, while B adds eight \(H_1\) charges. They cancel. Restore and terminal climbs are unchanged.

For completeness, the literal candidate bill by section is:

| Section | \(H_1\) | \(H_2\) | \(H_3\) | \(H_4\) | \(H_5\) | \(H_7\) | \(H_8\) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A, including prelude | 924 | 24 | 0 | 56 | 0 | 0 | 0 |
| Center copies | 4 | 0 | 0 | 0 | 0 | 4 | 4 |
| B | 1071 | 502 | 240 | 64 | 26 | 0 | 0 |
| Restore | 47 | 32 | 14 | 0 | 0 | 0 | 0 |
| Terminal climbs | 317 | 74 | 64 | 0 | 0 | 0 | 0 |
| Total | 2363 | 632 | 318 | 120 | 26 | 4 | 4 |

The complete rank mass is still 5,251. Thus the net local change is exactly \(4(H_8-H_7-H_1)\), not a reduction obtained by omitting prelude or restoration work.

## 5. Cleanup and the unchanged 78 buffers

Let \(N\) be the chronological non-target word consisting of ordinary A, the modified B with all warps at their shifted positions, and restore. The temporary prelude warp pairs compose to the identity on non-targets, and target-only corrections are excluded from \(N\). Every operation in \(N\) is invertible. Its inverse is the reverse list of inverse operations, with inverse chart operators included.

At the cleanup boundary, each of the 78 cold restored helpers is its own independent original input, and no other live row depends on that input. Hence \(N\)'s action on these coordinates is an identity block, separated from its other input columns. Substituting private zero buffers for those coordinates while applying \(N^{-1}\) restores all other coordinates and returns the buffers to zero, without touching the already restored cold helpers. This is the inherited private-buffer argument, applied to the actual changed \(N\).

The resulting explicit cleanup has 4,529 events and equals that inverse-reverse list. All cleanup frames are FULL. Both forward and inverse-transpose symbolic identities hold on all 646 independent live inputs. The `helper_final` map is unchanged: there are still exactly 78 private zero buffers, not eight additional ones. A role “returned” to the live helper inventory below is not a newly restored cold role.

The separate local checker represents binary subspaces as complete vector sets and represents operator products as free noncommuting words with adjacent inverse cancellation. This makes the local identities exact over arbitrary independent inputs; it does not establish the full physical Clifford-phase or all-size multiplication claims.

## 6. Transferring PR2673's owner fill

Both providers retain width inventory

\[
\{4:33,\ 5:9,\ 7:62,\ 8:78,\ 9:240\}.
\]

The removed PR2588 live roles are `680,681,682,684,688,689,690,692`; the roles returned to the live inventory are `596,600,632,633,656,657,658,660`. Each of these roles has entrance dimension one and terminal dimension nine. Common roles retain their local endpoint data. This proves the displayed inventory equality without treating a returned role as a new cold input.

The actual construction uses **sorted compact-index pools by width**. For each width \(w\), list the old compact helper indices of width \(w\) in increasing order and list the new compact indices of width \(w\) in increasing order; map the \(j\)-th old index to the \(j\)-th new index. Equality of the inventory proves this defines a bijection \(\pi\) on all 422 indices. Both providers give the same \(\pi\). The actual matched pairs also preserve entrance and terminal dimensions for these words; full native/global bindings independently reconstruct the actual endpoint geometry rather than inferring it from numeric helper labels.

The final hosting source is [PR2673 by Jeremy Kothe (jeremykothe2)](https://github.com/CrocSwap/integer-mult-bounds/pull/2673). Its two local words are byte-identical after decompression to the PR2588 words used for the local comparison above. PR2673 contributes the stage-priority search, invocation order, dispatch, and owner allocation. Its retained attribution credits [PR2621 (themilkman216)](https://github.com/CrocSwap/integer-mult-bounds/pull/2621) for the priority-ordering idea, [PR2559 (philippeVV)](https://github.com/CrocSwap/integer-mult-bounds/pull/2559) for evacuation, and [PR2530 (zxv)](https://github.com/CrocSwap/integer-mult-bounds/pull/2530) for the realization flows. Those hosting contributions remain separate from this package's local reassignment.

For stages \(0\le s<9\) and replicas \(0\le r<74\), the exact PR2673 order sorts the 666 invocations by

\[
(8s+2r+\delta_s,\ s,\ r),\qquad
(\delta_0,\ldots,\delta_8)=(-10,-1,-5,-8,1,0,0,0,0).
\]

This formula reproduces its literal `new/borrow-fill/ORDER.json`, including tie-breaking. The final composition keeps that source order and its owner fill. There are \(666\cdot422=281052\) whole-helper roles. The source allocation has idle profile

\[
\{1:21978,\ 3:6594,\ 5:554,\ 32:1,\ 48:26558\}.
\]

For every source owner row `(time, helper, owner_replica, child, port, offset)`, change only `helper` by \(\pi\). The row retains its time, strict window, owner, physical family, port, offset, and width. Consequently its occupied interval is identical. Since \(\pi\) is a bijection, every call still hosts each new helper exactly once. Non-overlap, distinct physical families within a call, compacted prefixes, and the entire idle profile are preserved.

The unchanged-interval argument is accompanied by complete literal checks of all 281052 old and new rows against windows recomputed from the original global template and PR2673 order. Those checks establish the discrete owner constraints. Literal chart embeddings, adapters, and native admission remain separate checks; inventory equality alone does not certify them. The completed fresh final native/global/outer admission and its numerical claim are bound by `CLAIM.json` and the completed receipts.

The local proof in Sections 2–5 is independent of this hosting choice. Another fully checked fill could replace PR2673's allocation, but it would need its own strict-window checks, idle histogram, and complete admission. The final proof here uses PR2673's fill without an additional owner-move or order-delay patch.

## 7. Strict positive root improvement over PR2673

Let \(h_d\) be a global paid histogram, with live stock \(L=66304\) and dimension 73. Its recurrence moment is

\[
\Phi_h(a)=\frac1L\sum_d h_d\left(\frac d{73}\right)^{1-a}.
\]

PR2673 uses exactly the compared old local words. The helper-index transfer preserves its full idle histogram. Therefore the complete global paid-profile difference is precisely 666 times the local difference:

\[
\boxed{\Delta_{\rm global}=2664(H_8-H_7-H_1)},
\qquad
\{\Delta h_1=-2664,\ \Delta h_7=-2664,\ \Delta h_8=+2664\},
\]

with every other coefficient unchanged. Its rank-mass difference is zero because \(8-7-1=0\); the full rank mass remains 4,816,512.

Writing \(p=1-a\), the exact moment difference is

\[
\Phi_{\rm new}(a)-\Phi_{2673}(a)
=\frac{2664}{66304}\,73^{-p}\bigl(8^p-7^p-1\bigr)<0,
\qquad 0<a<1.
\]

The strict inequality follows from \((u+v)^p<u^p+v^p\) for \(u,v>0\) and \(0<p<1\), applied with \(u=7,v=1\). One elementary proof observes that \((1+t)^p-1-t^p\) is zero at \(t=0\) and has negative derivative for every \(t>0\).

All charged ranks are below 73, so \(\Phi_h\) is continuous and strictly increasing in \(a\). At PR2673's positive complex root the new moment is strictly below one. The new histogram still has \(\Phi_h(1)>1\), so its unique crossing lies strictly to the right. This proves a strictly larger complex root throughout the exact construction, independently of a floating-point search result. There is no additional packing-profile term in this final comparison.

The complex root and the outer multiplication exponent \(\kappa\) are distinct interfaces. PR2673 itself distinguishes its supplier-only historical `CLAIM.json` value from its headline outer value in `outer/OUTER-CLAIM.json`; comparisons must respect that distinction. Publishing a larger outer \(\kappa\) for the present composition additionally requires the directed rational root bracket, exact outer inequalities, and all binding receipts. The final rational values and admission status belong in this package's `CLAIM.json`, `evidence/FULL-RESULT.json`, and `evidence/OUTER-LEDGER.json`. The retained full replay checks those finite obligations separately from this local and moment argument.

## 8. Conditional scope and Open next questions

The proved local change is a finite symbolic construction and a strict recurrence-moment inequality. Full admission also requires fresh native lowering and phase checks, physical owner geometry, adapters and private stock, the global invoice, bit precision and recovery, and the outer assembly. The inherited all-size/compiler, common-label and mutable-source realization, whole-call hosting, precision/tape, analytic-transfer, recurrence, and bit-side assumptions remain. Neither this proof nor successful finite certificates are a formal verification of a complete integer-multiplication theorem. The maintainer-selected record is unchanged by this package.

This work was prepared by Mason Hale with substantial OpenAI Codex assistance, including separate computational review. No independent human review is claimed.

**Open next questions**

- Can any of the four remaining center splits be eliminated? First enumerate simultaneous helper assignments whose complete correction supports avoid additional center readers, then derive their actual correction and cleanup words. New target lifts and changed source lifetimes must be charged; individual-helper improvements do not guarantee a jointly feasible word.
- Can a larger recoverable source subspace yield another alias? First exhibit an exact inverse-row identity at a legal retirement boundary and a chart into a helper's first-write frame. Reading a donor can enlarge its frame or invalidate a later warp, so an algebraic recovery alone is insufficient.
- Can a compatible owner fill reduce the idle moment further? Start with exact small coupled exchanges or an alternative invocation order, retaining all 281052 whole roles and original strict windows. The local proof above survives such work, but every proposed fill needs its own admission and exact repricing; no packing optimum is claimed.
- Which inherited all-size and physical-realization obligations can be proved independently of a finite certificate? A useful first step is to isolate one precise premise used by the full replay and state a quantified theorem with its implementation model. This local optimization does not discharge those premises.
