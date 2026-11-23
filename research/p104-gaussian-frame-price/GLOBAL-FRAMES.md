# An exact price bound for simultaneous changes in a common direction

At κ = 39/10000 the maximum gain in productive-minus-paid Gaussian mass is **exactly zero** when any subset of the 768 unanchored active charts grows by one common line, or any subset is restricted to one common hyperplane. The empty change attains the maximum. This holds even in a price relaxation that makes a paid transfer free when its two endpoint spaces become equal. A productive helper always requires a proper inclusion. The ordinary strict-incidence supplier is a subfamily. The conclusion concerns a fixed normalized word, main interface, public role labels, and occurrence schedule. [Source projection and prior finite families](README.md) · [Exact results](GLOBAL-FRAMES.json)

## Enumerating the directions and writing the price

Every nonzero vector $v$ in $V=\mathbb F_2^9$ specifies exactly one line $\langle v\rangle$ and, using the standard coordinate pairing, one hyperplane $v^\perp$. There are 511 choices of each. For the first family choose a subset of active mutable charts and replace each chosen space $F$ by $F+\langle v\rangle$. For the second family replace each chosen $F$ by $F\cap v^\perp$. A change flag is necessary only at a site where the operation changes the actual subspace. The 210 charts carrying main endpoints are fixed.

Group the 5,674 paid MOVE occurrences and 891 productive helper targets by their original nested pair $A\subset B$. Give each pair weight $w$ equal to its number of helper occurrences minus its number of paid occurrences. Retain every pair as a containment constraint, including any whose weight cancels. Record independently whether it carries a helper. With $r=\dim B-\dim A$, write $p_r=r^{1-39/10000}$, and set $p_0=0$ in the relaxation. A paid-only pair may become equal there. The original positive-grade transfer compiler would need a separate implementation for a contraction. Omitting that expense gives an upper bound for this fixed schedule.

For growth there are three possibilities.

* If $v\in A$, both endpoints are unchanged.
* If $v\in B\setminus A$, only $A$ can change. Choosing it reduces $r$ by one. At $r=1$ equality is forbidden whenever the pair carries a helper. The strict subfamily forbids it also for paid-only pairs.
* If $v\notin B$, both endpoints can change. Growing $A$ forces growing $B$, since the changed $A$ would contain $v$ while the original $B$ does not. Choosing just $B$ increases the grade by one. Choosing both preserves it.

For restriction use $H=v^\perp$. If $B\subseteq H$, neither endpoint changes. If $A\subseteq H$ but $B\nsubseteq H$, only $B$ can change and choosing it reduces $r$ by one, with the same equality rule. If $A\nsubseteq H$, both can change, and restricting $B$ forces restricting $A$. The original $A$ contains a point outside $H$, which the restricted $B$ omits. Choosing just $A$ increases the grade by one. Choosing both preserves it. In each case the listed rules are sufficient for containment as well. An originally strictly lower endpoint can never reverse the inclusion after a one-dimensional change of this kind.

For a pair with both change flags available, write $i\Rightarrow j$ for the required implication. Its price increment on any permitted assignment is
$$
w(p_{r+1}-p_r)(x_j-x_i).
$$
For a pair with only one susceptible site $i$, the increment is $w(p_{r-1}-p_r)x_i$, subject to the equality rule. Propagate every prohibited flag backwards through implications. On the remaining sites the legal subsets are exactly the sets closed under those implications. These formulas give an integer signed histogram $h_{ik}$ at each site. The true gain of a closed subset $C$ is $\sum_{i\in C}\sum_{k=0}^9 h_{ik}p_k$. This representation accounts for every shared edge once even when many helpers and internal frames move jointly.

## Directed upper profits and a rational optimality certificate

Let $S=2^{192}$ and use the outward enclosures $L_k\le S p_k\le U_k$ from the base verifier. Combine all occurrences into $h_{ik}$ **before** pricing. For site $i$ assign the integer profit
$$
u_i=\sum_k\max(h_{ik}L_k,h_{ik}U_k).
$$
Then $S$ times the true gain of any closed set is at most $\sum_{i\in C}u_i$.

Given any integer vertex profits $q_i$, connect a source to every positive-profit vertex with capacity $q_i$. Connect each negative-profit vertex to the sink with capacity $-q_i$. For each implication $i\Rightarrow j$ add a forward arc of capacity strictly greater than $P=\sum_{q_i>0}q_i$. The empty selection gives a cut of capacity $P$. A minimum cut therefore respects all implications. A feasible cut with chosen set $C$ has capacity $P-\sum_{i\in C}q_i$. Each replayed flow is checked for admissible integer arc values and conservation at every vertex. The corresponding feasible cut has the same capacity, which proves optimality.

In all 1,022 networks with $q_i=u_i$ the maximum closure profit is exactly zero. The minimum cut value in each instance equals its own $P$. The empty assignment attains true gain zero, establishing equality for the exact real tariff.

## Midpoint and tie check

A second flow uses $m_k=L_k+U_k$ and site profits $\sum_k h_{ik}m_k$ in units of $1/(2S)$. Every one of its 1,022 maxima is also zero. With $N=6,565$ signed term occurrences per native invocation, the largest error of any new-minus-old midpoint total in doubled-grid units is at most
$$
E=2N\max_{0\le k\le9}(U_k-L_k)=283047917910754750 .
$$
Each original and candidate occurrence contributes at most one interval width in these units. The resulting coarse upper gain is $141523958955377375/S<3\cdot10^{-41}$ per native invocation.

For any cut, its capacity minus the certified flow is the sum of its outward residual capacities, including backward residual arcs for incoming flow. Thus any strictly suboptimal cut is separated from the midpoint maximum by at least the smallest positive residual capacity of that network. Across all 1,022 networks this lower bound is
$$
3440725855595812174076952386583042024909598591777889135>E.
$$
Every midpoint loss remains a strict loss under the actual tariff.

A minimum cut admits no outward residual arc. It must include the source and exclude every vertex having a residual path to the sink. All source capacity is saturated here, so the source forces no other vertex. Every optimal subset is a union of strongly connected components among the remaining residual vertices. The verifier checks that each such component has a zero signed grade histogram in every coordinate. There are 48 component occurrences across the growth directions and 240 across the restriction directions. Their unions preserve the complete signed histogram. These component counts describe residual graphs across separate directions and need no interpretation as counts of distinct frame assignments.

## The 48-call invoice and controls

The priced template appears 48 times. Its raw invoice change is $48D$ for an unscaled single-invocation change $D$, and its two-type change is $48(5+451\cdot2^{1-39/10000})D$. Exactly 847 grade-one MOVE occurrences per native invocation connect two anchored main charts. Together with 480 fixed caller roles they guarantee 41,136 grade-one paid roles before splitting. The source can therefore make its same 1,008 small-type splits in every tested assignment, and their fixed charge cancels from the difference. At the best price the raw invoice still has a deficit exceeding 1.539342547620186178214 and the two-type deficit exceeds 1,406.078231652772. The bound concerns one common direction at a time. Sequences with independently chosen directions, changes of main endpoints, altered contact schedules, and new supplier return contracts require other arguments. [Baseline intervals and split tariff](PROOF.md)

The independent $\mathbb F_2^3$ oracle constructs transformed spaces as literal sets of points on an eight-chart graph. It exhausts both strict and relaxed choices for every line and hyperplane, checking all 736 subsets against containment and exact grade differences. It compares both flow objectives with exhaustive optima. Of 113 permitted selections, 45 contract a paid-only edge. Fourteen of the 28 toy families have positive midpoint optima. A separate four-vertex closure has positive optimum four. The source calculation uses the same authenticated projection as the one- and two-site tests at the original #8075 head. Clear1nsight prepared the common-direction price calculation and separate directed-flow, residual and point-set checks with substantial OpenAI Codex assistance. [Verifier](global_frames.py) · [Base head](https://github.com/CrocSwap/integer-mult-bounds/commit/a4d65b8c7868413bf0fd26803081117a0d9dda3d) · [Attribution](NOTICE.md)

