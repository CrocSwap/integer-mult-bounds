# What the kernel checks and what the hardware-model argument supplies

## The exact hypotheses at the cutoff

In `S008.Piecewise.LabelSchedule.schedule_natural_clock n cost a`, put $t=\log_2\log_2 n$, $X=\lceil\log_2(a+2)\rceil$, and let $H_{29}$ be the continuous piecewise-affine schedule obtained from the 29 integer-scaled true-label rows. Define the following function on a natural width $x$.

$$
E(H,x)=48\Phi(x)+\max\bigl(0,\max_{v\in\{0,\ldots,x\}}[H(v)-(159/4)\Phi(v)]\bigr).
$$

The theorem assumes precisely (i) $n\ge2^{2^{7519517465920988}}$, (ii) $X\le t+2$ and (iii)

$$
\mathit{cost}\le I(n,a):=n\sqrt{\log_2 n}\,
  2^{182+4\log_2(t+2)+E(H_{29},X)}.
$$

It concludes $\mathit{cost}\le n(\ln n)^{501/1000}$. Here (i) is the input domain. For the machine's actual packed address width $a=k$, `IntegerBounds.rounded_width` discharges (ii), including both discrete roundings. Condition (iii) concerns the steps of an actual run. The analytical schedule is an upper continuation even when the machine selects further arities. Its comparison and density prove the implication for every later real $t$. [Schedule and hypotheses](S008/LabelSchedule.lean) · [Packed width](S008/IntegerBounds.lean) · [Continuation and all-later proof](S008/LabelSharp.lean) · [Derivation of the true-label slopes](proof/routing-label-walsh.md)

## Extracting a dispersed occupied role

At a finite Walsh node the parent has $P$ leading prefixes, $r=C_r(m+1)q_F^{L_F}$ roles per prefix and $B$ payload bits per role. The symbols $q_F,L_F$ describe the label alphabet here. They are independent of the requested exponent. A fixed valid slot occupies $K=PB$ of the $W=PrB$ bits. The mark is set by the address layout, so a zero data bit can be occupied. `occupied_role` proves both counts. The transfer rule reads the staged tape with one Boolean mark per parent position. Its six-letter alphabet and three scan phases are finite. The tape set consists of the parent, mask, compact tape and the child's fixed private tapes. [Role layout](S008/RoleMask.lean) · [Transfer transitions](S008/OccupiedBank.lean) · [Written physical layout](proof/routing-review-walsh.md)

| Operation | Physical theorem |
|---|---|
| Gather and rewind | Exactly $2W+2$ transitions. Each selected parent symbol is copied at its prefix rank, in order, followed by a delimiter at $K$. The parent is preserved. |
| Issue and return | Two stationary control changes. An arbitrary halting child starting on the gathered compact word and returning its result with the compact head home takes exactly its own $k_i$ steps. Parent and mask stay parked during the child. |
| Scatter and rewind | Exactly $2W+2$ transitions. Each marked position receives the corresponding result, all other parent positions retain their old contents, and compact cells $0$ to $K$ inclusive are cleared. |
| Repeated calls | Each occurrence contributes $4W_i+6+k_i$ steps. For absolute child fences $[l_j,h_j]$ that contain all child visits, one set of cells covers all calls. Parent and mask use $[-1,\max W_i]$, while the compact head during the transfers stays in $[0,K_i]$. |

The result includes both endpoints of every trace. A child may use private cells or compact cells beyond $K$ during its own execution. These count against its supplied physical fences. `Call.repeated_visits` takes the sum of the sizes of the head intervals once across all calls. Each head may attain its maximum in a different invocation. [Halting wrapper and exact content](S008/BankReturn.lean) · [Repeated time and cumulative space](S008/CallLedger.lean)

## Remaining physical obligation

Fix a legal input on the coprime branch and let $T$ be its number of transitions to the correct output. Exhibit the ordered list $C$ of occupied wrappers actually issued, with one entry per occurrence and in-place phase/port identifications. For entry $i$, exhibit its staged slot, $W_i,K_i$, newborn and returned banks at the same origins, halting native child with duration $k_i$, and measured wrapper duration $d_i$. Give ordinary time $u$, bounds $O,M$, setup charges $s_i$ and per-bit movement prices $p_i$ satisfying

$$
\begin{aligned}
T&=u+\sum_{i\in C}d_i, &
u+\sum_{i\in C}(4W_i+6)&\le O,\\
k_i&\le s_i+K_i p_i, &
\sum_{i\in C}(s_i+K_i p_i)&\le M, &
O+M&\le I(n,k).
\end{aligned}
$$

The independent wrapper observations must start with the marked bank of that occurrence. The new theorem `IntegerBounds.from_role_runs` applies trace determinism to prove $d_i=4W_i+6+k_i$, derives $K_i$ from its actual slot layout and feeds the summed cost into the original sharp theorem. Its predecessor `from_occupied_calls` takes the equivalent partition directly. The outstanding controller proof must construct those observations for the multiplier, including the cost of making the marks, empty-role skips, multiplicities, restorations of other live data, and the native prices. For a nested call, charge an inclusive child trace at its parent boundary or expand its children and take exclusive work there. The time partition must count every transition exactly once. [Formal implication](S008/IntegerBounds.lean) · [Walsh event counts and setup](proof/walsh-node.md) · [True slot movement and induction](proof/routing-refined-walsh.md) · [Full reserves, group sizes and contraction](proof/child-volume.md) · [Caller transfers and return](proof/recount-handoff.md)

For space the outstanding statement is that on this same run each real invocation maps its logical heads to the specified physical tapes and respects their common absolute fences, also during construction of the masks. The union with the ordinary heads, including both routing families, must have cardinality at most $453759460Nk$. The wrapper theorem supplies the union for its calls under these fences. `IntegerBounds.fast_space` then proves the final $2^{32}n$ comparison. A bound on the maximum per-call total alone cannot justify this step. [Written tape-by-tape fences](proof/routing-outer-space.md) · [Native arena and stack](proof/node-integrated.md#arena-stack-and-visited-cells)

## Which conclusion uses which proof

| Conclusion | Kernel-checked component | Written connection to the specified multiplier |
|---|---|---|
| $n\sqrt L\,2^{63\Phi(x)}$ for all $n\ge2$ | All-input implication from the three branch costs, three-slope bounds, packing | Actual raw, dyadic and coprime branch costs and their assembly into one machine. [Dispatcher](CONSTRUCTION.md) |
| Unit coefficient for every $1/2+1/q$ | Termination of the integer search and implication from the large-branch smooth cost | The complete coprime multiplier satisfies that smooth cost. [Construction of the coefficient 60](proof/profile-limit.md) |
| Unit coefficient for $0.501$ above the worked cutoff | Exact endpoint signs, valid 29-row schedule, extension to every later input, wrapper and occupied-volume implication | Actual mask/controller schedule, child prices and combined cost in the displayed partition. [Whole Walsh transfer](proof/routing-refined-walsh.md) |
| Full $2n$-bit product with at most $2^{32}n$ distinct visited cells | Selected Walsh and rounding identities, carry/readout from recovered coefficients, wrapper fences, packed-space comparison | Compiled full transform, precision, recovery on each branch, and common physical fences for all operations. [Recovery](proof/outer-layers.md) · [Space](proof/routing-outer-space.md) |

An end-to-end theorem would exhibit one finite machine in the original specification and prove output, time and visited space on every input for that machine. The statements above identify the remaining translation from the written construction to such a theorem.
