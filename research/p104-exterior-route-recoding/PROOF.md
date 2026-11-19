# Port rigidity, two retirements and a cut certificate

## Word and observations

The source is Clear1nsight's literal rational continuation word at `89a67c404226d51028e135de2b9169e9020d57af`. Its 1,289 public coordinates are independent over $\mathbb Q$. A paid step deposits one scalar at its destination chart. A terminal reads its chart's local stock. The original program has 5,709 paid sends, 902 distinct demanded outputs at receiver 127, and 387 exterior outputs. Chart 278 owns no public atoms. Its ten paid ingresses all precede its ten egresses. The receiver also owns no public atoms and all its demands are linear combinations of its 902 deposits. Write $v_k$ for the original scalar at step $k$. A step identifier does not specify its chronological time. [Source and method pins](SOURCE-PINS.json)

First fix the original ingresses and permit arbitrary rational-linear changes to all ten chart-278 egresses. Propagate them through the fixed intervening program. Preserve all exterior terminal operators and allow arbitrary deterministic readout at the receiver. The local equations below give the exact deficit in receiver observations for any such recoding. We then fix either of two specific mergers and charge every additional positive-grade send, while granting each chart all its original local public atoms and all of its **post-merger** paid arrivals at any time. This grants a stronger observer than a causal one for the lower bound. The matching upper bounds reinstall the actual chronology. An additional paid transfer connects comparable original binary spans and costs $p(g)$ for their absolute rank difference $g$. Sharing a value between equal spans may be free. Only the payloads of new corrective sends and the final receiver readouts may be coded during the additive repair. Every native paid formula outside the named merger keeps its post-merger meaning. Reusing a funded channel to convey new information would change this last premise.

## All ten jointly recoded egresses

Write $A=95887$, $B=100336$ and $C=95914$. Inject ten independent scalar perturbations at the chart-278 outputs. Following the fixed native formulas gives a rational $387\times 10$ exterior response matrix of rank eight. Its kernel has the basis $e_A-e_B,e_C$. Therefore equality at the exterior on every public input allows exactly

$$
\Delta v_A=h,\qquad \Delta v_B=-h,\qquad \Delta v_C=j
$$

with every other egress unchanged. Since chart 278 owns no other stock, $h,j$ lie in the span $U$ of its ten ingress functions. Upon propagating these two directions the only changed receiver deposits are

| Receiver deposit | Change |
|---|---:|
| 103472 | $h$ |
| 104080 | $-h/2$ |
| 88 | $j$ |

The corrections for $h$ and $j$ can be chosen independently since all ingresses precede the three egresses. The response check uses exact rational elimination and all 387 exterior rows. [Pulse-matrix and receiver replay](check_rigidity.py)

Let $R$ be the span of the 902 original demanded receiver outputs. Jointly expand these outputs and the ten ingress functions in the 1,289 public coordinates modulo 1,000,003. This is a prime and all denominators in the program are units there. The 912 rows have rank 912. A nonzero minor modulo this prime lifts to a nonzero rational minor. Thus $\dim R=902$, $\dim U=10$ and $R\cap U=0$. Since all 902 targets lie in the span of exactly 902 deposited rows, the original deposits form a basis of $R$. [Full row-rank certificate](check_rigidity.py)

In $R\oplus U$, the new arrivals are the graph of a linear map $T:R\to U$ on this basis. The table gives $\mathrm{im}\,T=\mathrm{span}(h,j)$. If $d=\dim\mathrm{span}(h,j)$ and $R'$ is the new row span, then

$$
\dim R'=902,\qquad R\cap R'=\ker T,\qquad \dim(R+R')-\dim R'=d.
$$

In particular **the only successful zero-addition recoding is the original one**. For linear observations and targets, deterministic decodability implies inclusion of the target rows in the observation span. Indeed, observations agree on two inputs differing by a vector in their common kernel, so every recoverable linear target annihilates that kernel. More generally, exactly $d$ additional rational-linear receiver deposits are necessary. Sending a basis of $\mathrm{span}(h,j)$ directly from 278 suffices. Insert these sends after the last ingress and before the first chart-278 egress (zero-based source positions 1704 and 1749). The only changed terminal operators under the old readout are 155442 with shift $h/2+j$ and 155490 with shift $-h/2+j$, at positions 6950 and 6888. Subtract these shifts when the two readers execute. Earlier terminal reads remain valid with their native stock. This count allows arbitrary decoder functions. It counts rational-linear corrective scalars, a material restriction when $d=2$.

## Two complete mergers and their literal repairs

The paid slots on $278\to561$ (grade one) and $278\to660$ (grade five) have local payloads

$$
v_A=v_{94217}-v_{94218}-v_{95884},\qquad v_B=-v_A+v_{100334}.
$$

Retire either slot and remove all its old reader references. Put $v_{100334}$ in the surviving slot. This is an exterior-preserving perturbation with $j=0$. For retiring $B$ take $h=v_B$, and for retiring $A$ take $h=-v_A$. The old receiver decoder then yields changes of $+h/2$ at terminal 155442 and $-h/2$ at 155490, with every other terminal preserved. A new paid send $278\to127$ of the retired native payload lets the two terminal readers subtract their respective errors. Both payloads are known at 278 before either original slot. The fresh send can run in the chronological position of the retired send. The verifier checks native ownership and schedule, propagates the exact operator difference through all 1,289 terminal rows, and separately expands the two changed rows back into public coordinates. [Causal word builder and replay](check_mergers.py)

## A two-coordinate witness and all minimum-grade routes

Compare zero with $x_{674}=1, x_{722}=-1$ and all other coordinates zero. The public source charts are 11 and 58, both of rank one. Before either merger $v_A=2$, $v_B=-2$, and the original terminal 155442 at rank-nine chart 127 equals one. After **either** merger, exactly two of the 5,708 paid arrivals are nonzero on this input. They are $v_{94217}=1$ and $v_{94218}=-1$, both arriving at rank-two chart 278. Thus every post-merger chart stock at rank three or above agrees with its stock on zero. The verifier evaluates every surviving paid scalar. [Separating input and full-stock test](check_cuts.py)

In a fixed finite corrective network of deterministic scalar messages, if the receiver distinguishes this pair then a chronological path must run from a chart with distinct stock to the receiver. Induct on sends. A first difference at a previously indistinguishable chart must arrive from a chart where some difference is already observable. Local deterministic computation does not create a difference from equal stock. Hence a path starts at rank at most two and reaches rank nine. The sum of absolute rank changes is at least seven. This holds even with arbitrary deterministic encoders for a single copy and free deterministic final readers. A data-dependent route or timing choice used as an uncharged communication channel is outside this fixed-schedule model.

Equality in total grade forces the starting chart to be 278. Every positive-grade send must lie on one strictly ascending path. Up to free equal-span steps, its vertices form a strictly nested chain of original spans between 278 and 127. Enumerating the spans of all 1,103 original frames gives 56 charts in this interval, all with distinct spans. Their counts in ranks two through nine are $1,3,4,3,6,14,24,1$. Recursing from each vertex over **every** strict superchart in this interval gives 933 chains.

| Positive sends in the chain | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Minimum-grade chains | 1 | 54 | 229 | 325 | 226 | 86 | 12 |

Every chain attains grade seven by forwarding the retired scalar consecutively in the retired chronological position, before the affected terminal readouts. The direct and a seven-leg word are built for each merger, including all local-reader corrections. Branches with additional positive-grade sends cannot attain total grade seven. The chain count describes positive-grade route topologies and allows arbitrary local coding and free steps.

## Tariff and independent copies

Let $L$ independent copies of the post-merger word be available. Either orientation of the merger works in each copy. Allow scalar **rational-linear** corrective messages arbitrarily mixing those copies on a fixed network of original chart labels. The decoder may be deterministic nonlinear. Restrict the input in copy $i$ to $t_i$ times the two-coordinate witness. For each cut between ranks $r$ and $r+1$, $2\le r\le8$, the upper side initially sees zero on this $L$-dimensional space. Its observable linear row space restricted to the test increases in dimension by at most one per upward scalar and cannot increase from internal or downward messages. Correct outputs at 127 recover $(t_1,\ldots,t_L)$, requiring at least $L$ upward scalar crossings of each of the seven cuts. Downward feedback and arbitrary local linear side information already present above the cut cannot evade this count.

An oriented edge $(a,b)$ between ranks crosses $m=\#\{2\le r\le8:a\le r<b\}$ upward cuts. For a nondecreasing concave tariff $p$ with $p(0)=0$, $p(|b-a|)\ge m p(7)/7$. For grade at most seven this follows from the chord to $(7,p(7))$, and for grade at least seven it follows from monotonicity and $m\le7$. Sum over all paid sends and then over cuts to get

$$
\text{added tariff}\ \ge\ L\,p(7).
$$

One direct send per copy attains this bound. For one copy with arbitrary deterministic encoders the same inequality follows from the distinguishing path traversing each of the seven cuts. At the enrolled strictly increasing, strictly concave $p(g)=g^{1-0.00387981257853}$, all positive-grade inequalities are strict except a rank-two to rank-nine jump. For one copy only chart 278 can start such a distinguishing jump, and the receiver must get it, so the unique optimum positive-grade topology is $278\to127$. For independent copies joint linear coding has no tariff advantage. Special correlations among inputs of an actual caller are outside the independent-copy argument.

For the separate signed paid-port accounting of the 48 rational calls, retirement removes either $48p(1)$ or $48p(5)$. The verifier recomputes the complete grade-one through grade-eight count vector $(3842,792,487,230,314,40,3,1)$ on all 5,709 baseline sends and compares both repaired words. Each moves one count from its retired grade to grade seven. Replacing that slot by $48p(7)$ gives

$$
285.472830172972358520270568 < 48[p(7)-p(1)] < 285.472830172972358520270569,
$$
$$
94.966797106425725799489376 < 48[p(7)-p(5)] < 94.966797106425725799489377.
$$

The replay encloses logarithms with a rational positive-series tail and exponentials with rational alternating bounds. It checks the directed inequality for all 100 ordered rank pairs. These are exact paid-port comparisons for the specified changes. A new complete multiplication record would require the local arithmetic and caller obligations of the source construction as well as a favorable total. [Directed interval verification](check_cuts.py)
