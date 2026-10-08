# Joint frame compilation of dual-suffix strips

Under the inherited base theorem, residual-compiler, fixed finite-alphabet
multitape, analytic, routing, and recovery hypotheses, the pinned construction
supports

$$
 T(n)=O\bigl(n(\log n)^{1-\kappa}\bigr),\qquad
 \kappa=\frac{4764513337}{10^{14}}=4.764513337\times10^{-5}.
$$

The exact bit saving is
$a_b=2382370177/50000000000000=4.764740354\times10^{-5}$.
The unchanged complex saving is $717/10^7$. This improves PR58's
$475073569/10^{13}$ by approximately 0.290011%, and lies strictly between
$2^{-15}$ and $2^{-14}$. These are comparisons of conditional asymptotic
exponents, not measured running times.

The contribution changes the order in which the PR58 composition considers
retired physical slots: larger current frame ranks first, then slot ID. The
PR55 scalar graph, matching algorithm, containment and signal-span tests, and
literal XOR semantics remain unchanged. The dedicated compiler preserves the
original shared PR57 compiler and its baseline. Neither a new frame family
nor a new general transfer theorem is asserted.

## 1. Pinned ingredients and scalar identities

The scalar graph is the exact file `research/skip-suffix/skip_graph.py` from
PR55 at `03e991aa79f9df1a935726213bb6a8631cd0d823`, preserved under
`references/frame-compiler/pr55`. Its three shared circuit dependencies are
byte-identical to the already pinned PR48 files. The compiler, independent
word replay, transition extraction, bounded-minor profiler, and rational
arithmetic are PR57's files at
`cd350f76c9bc01489ec83568bded532cb69be938`. The retained PR57 witness supplies
a complete comparison network; it is not overwritten by this witness.
The complete PR58 certificate and its original source/proof provenance are
preserved under `references/frame-compiler/pr58`, pinned to
`bc2f7ed4c20dc18898305ab17165c0c995cbb804`. Its full child list is used for the
strict comparison at the new bit saving. The only algorithm change in the
dedicated `joint_dual_reclaim_compiler.py` is the retired-slot ordering line;
an explicit runtime guard also rejects Python that disables assertions.

For an ordered vector $v_1,\ldots,v_k$, let
$A_i=\sum_{r\le i}v_r$ and $B_i=\sum_{r\ge i}v_r$, with empty sums zero.
PR55 computes the leave-one-out sums by

$$
 s_j=(A_{j-1}+v_{j+1})+B_{j+2}\quad(1\le j<k),
 \qquad s_k=A_{k-1}.
$$

The three summands have disjoint index ranges and their union is exactly
$\{1,\ldots,k\}\setminus\{j\}$. Thus each output is the required sum.
The total is $A_{k-1}+v_k$. The generator handles vectors of length at most
two, zero entries, and restoration of output indices explicitly. The recursive
paired-exclusion construction therefore preserves the indexed scalar outputs.
The exact finite scalar replay checks all additions, all leave-two-out outputs,
and all retained totals on each complete graph; it does not infer correctness
from the role counts.

At each dimension $h\in\{23,25\}$, the source symbols correspond to the
$v_h=\binom h3$ triples. An addition retains the original rational envelope

$$
 E(C,U)=\{x:\operatorname{supp}(x)\subseteq U,\ x_i=t\ (i\in C),
                  \ \sum_i x_i=3t\},
$$

with address metric $I-J/9$. Non-source cores have size one or two and the
envelope rank is $|U|-|C|$; a source has its triple line. Address arithmetic
and binary payload arithmetic are distinct. The finite graph and replay check
the actual cores, covers, source lines, and output frames. No enlarged positive
frame or additional source-partition clone is introduced by this composition.

## 2. Joint synthesis inside one frame

Group scalar nodes having exactly the same pair $(C,U)$. Every external
input to a region is a binary linear form in the original source symbols.
Write each requested region output as a row over the incoming physical roles.
Choose an independent set of requested rows, followed by independent retained
input rows chosen by the compiler's matching, and complete these rows with
standard unit vectors. The resulting square binary matrix is invertible.

Gaussian elimination reduces this matrix to the identity. Reversing its
literal row-XOR sequence implements the desired invertible map. Row swaps are
implemented by three XORs and are included in the serialized word. Dependent
requested outputs are expressed in the chosen independent output basis and
written to separate physical roles. Multiple uses are also allocated distinct
roles unless an explicitly checked retained continuation supplies the use.

All XOR endpoints in this local sequence have the same address frame. A common
address permutation on all these roles commutes with their binary row map.
Consequently the inherited framed-operation semantics applies to the entire
region, including its arbitrary dirty components. This reasoning does not
require the incoming physical values to be zero or statistically independent.

A retained continuation is permitted only when its target region is strictly
later and its frame contains the source frame. Matching chooses a feasible
set of independent retained rows with distinct requested uses. Optimality of
this search is unnecessary: the selected map is checked through the resulting
physical word. The present result claims no global optimization theorem.

## 3. Paid reclamation and arbitrary dirty scratch

A retired slot may still hold an input-dependent signal plus an arbitrary old
dirty contribution. The compiler reuses it only if its current frame is
contained in the new region's frame and its signal is a binary combination of
compatible available signals. It emits the XORs that remove that signal.
Those XORs, including their frame incidences, are part of the word. Clearing a
signal is not an assertion that the physical slot becomes zero.

The priority examines a snapshot of retired slots in decreasing current frame
rank, with ascending slot ID for equal ranks. Every candidate still passes
the same frame-containment and signal-span tests. All clearing operations
remain literal invertible XORs, and successful reclamation immediately
returns, so no later candidate uses a stale rank after a frame change. The
order is a finite selection rule, not an assertion that greedy reclamation
is globally optimal.

Let $L$ denote the entire invertible auxiliary mixer, $V$ the source
injection, and $J$ the read-only scatter. The finite scalar and terminal
checks establish $JLV=I$ on the intended source coordinates. For source
$x$, target $z$, and arbitrary auxiliary state $d$, use the chronological
sequence

$$
 L,\ J,\ L^{-1},\ V,\ L,\ J,\ L^{-1},\ V.
$$

The first scatter adds $JLd$ to the target. The second adds
$JL(d+Vx)=JLd+JLVx$. Over the binary payload field the two dirty terms cancel,
leaving $z+x$. The last inverse and injection restore $d$, and the source
is unchanged. Thus reclamation inside the invertible mixer does not consume a
zero-initialized scratch assumption. The reversed transposed word gives the
other orientation.

The compiler's own symbolic checks are supplemented by an independent replay
of the serialized word. Bitset columns represent every source, target, and
dirty basis vector simultaneously. Both orientations are checked, including
restoration of every auxiliary, distinct designated output roles, exact output
sums, and all physical frame inclusions. In this witness:

| Quantity | h=23 | h=25 |
|---|---:|---:|
| Sources $v_h$ | 1,771 | 2,300 |
| Auxiliary roles $R_h$ | 30,688 | 40,338 |
| Basis columns $2v_h+R_h$ | 34,230 | 44,938 |
| XORs in $L$ | 112,534 | 148,820 |
| Signal-clearing XORs, included above | 4,284 | 5,714 |
| Full wrapped word length | 474,930 | 627,480 |
| Copied local rank mass | 706,330 | 1,009,050 |

The full word lengths equal $4|L|+14v_h$. These are fixed finite scalar
costs at the fixed dimensions; they are neither omitted cleanup work nor a
claim about practical execution time.

## 4. Actual frame transitions and recursive children

For every physical role, independently reconstruct its chronological frame
path from source incidences, literal XOR endpoints, and final output incidences.
Every move must have containing destination frame. Compare the reconstructed
transition multiset with the compiler's recorded event list. Thus a proposed
saving cannot arise merely from omitting an event in that list.

Use the same common rational $I+J$ bases and original-envelope projector
formulas as the pinned pipeline. The fixed-profile calculation uses all actual
transitions. Its modular ranks are made exact by the retained bounded-minor
argument: denominators are nonzero modulo the selected primes; rank-two minor
numerators are strictly smaller than the first modulus; and rank-three/four
numerator bounds are strictly below the product of the three moduli. Therefore
simultaneous modular vanishing implies rational vanishing in these bounded
classes. The primes $2^{61}-1,2^{31}-1,2^{19}-1$ and all strict bounds are
checked in exact arithmetic. Ordered zero minors and nonzero pivots determine
the charged contiguous blocks. Agreement of sampled modular calculations alone
would not establish this statement.

Copied retained centers remain paid. Transition extraction explicitly charges
the copied center entrance and original center cleanup. Every ordinary output
is distinct and has its remaining growth and endpoint cost, and every other
role has its final cleanup. Consequently the local mass is

$$
 \sum_t t n_{h,t}=hR_h+h(h-1).
$$

There is no width-zero child and no width-$h$ block left over from an uncharged
center cleanup. The actual profiles verify these identities.

## 5. Full network and exact recurrence

Let $a=23$, $b=25$, $m=ab=575$, and
$N=\binom{23}3\binom{25}3=4,073,300$. Replicate the two auxiliary profiles
2,300 and 1,771 times respectively. The physical width is

$$
 W=2N+2300R_{23}+1771R_{25}=150,167,598.
$$

Retain the inherited all-pairs data profile: two copies of
$9[1]+[21]+[17]+[481]$ for every source pair. All 4,073,300 pairs remain
present, including the ten pairs recovered in exact rational arithmetic by
PR46. The common basis and data geometry are unchanged by the auxiliary word.
Also retain all paid endpoint-copy, exterior, and source-growth terms. Their
complete multiplicities, not a surrogate rank histogram, are stored in the
new certificate.

With $L=2,226,400$, the complete rank mass is

$$
 s=mW-N+L=86,344,521,950,\qquad mW-s=1,846,900.
$$

Every child width is positive and smaller than 575; the maximum is 529.
The characteristic at saving $u$ is

$$
 F(u)=\frac1{mW}\sum_t n_t t\exp\!\bigl(u\log(m/t)\bigr).
$$

The exact rational certificate proves $F(a_b)<1$, with gap exceeding
$1.59\times10^{-15}$. Logarithms use a 32-term atanh series with explicit
remainder and outward rational rounding. Exponentials use rigorous rational
lower and upper inequalities. No floating-point search value is admitted as a
proof bound. The next bit-saving grid point $a_b+10^{-14}$ has exact lower
moment greater than one. At $a_b$, the complete pinned PR57 and PR58 networks also have
lower moments greater than one, so the improvement is a physical-word change.

## 6. Balanced assembly and conditional scope

The complex branch and its semantic/scalar bounds are retained. The finite
bridge updates the actual bit width while checking its role-bit length and
halving depth. Use the inherited balanced choice with $\eta=10^{-12}$,
$q=a_b(1-2\eta)$, and
$\epsilon=(1-\eta)/(1+q)$. The new certificate checks all 47 strict assembly
conditions and all seven final margins against the displayed $\kappa$, and
recomputes the eventual cutoff inequalities. The smallest margin exceeds
$\kappa$ by more than $2.96\times10^{-15}$. The next $10^{-14}$ kappa grid
point fails the assembly check. Combining these inequalities with the inherited
transfer theorem yields the conditional bound stated at the start.

The finite checks prove the recorded finite identities and exact inequalities.
Expert review is still required for the all-size residual compiler, the use of
framed physical words within that transfer, the fixed finite-alphabet multitape
layout and routing, analytic multiplication reduction, eligible-prime/eventual
setup, and exact recovery. The equal-frame argument and explicit dirty wrapper
explain why this new finite compiler satisfies its proposed local interface;
executing the finite tests is not a formal proof of the general interfaces.
There is no new Lean formalization, global optimality claim, or practical
speedup claim.

## 7. Reproduction and attribution

Run the new joint-dual verification target and then `make verify`. The target
regenerates the selected words from the pinned scalar producer, compares their
decompressed bytes, independently replays them, reconstructs all transitions,
recomputes the CRT profiles, and checks the exact recurrence and assembly.
The full repository suite retains the PR57 baseline and all main checks,
including the inherited complete data-pair verification. The validation receipt
records the actual tested source state and completion status; this proof does
not substitute for that receipt.

Rohan Gupta / gupt1156 with Anthropic Claude assistance supplied PR55's dual
suffix layout. Eumemic with OpenAI Codex assistance supplied PR57's joint frame
compiler, reclamation, and independent word/profile machinery. Avi Eisenberg /
ikeboy with Anthropic Claude assistance supplied PR53's skip-prefix framework.
Chafik Boukhalfa with OpenAI Codex assistance supplied this composition,
reclamation priority and independent checks, and the earlier PR43/46/48 original-envelope pipeline and
exact data recovery. Rohan Arun with Anthropic Claude assistance, RaD /
hipotures with OpenAI Codex assistance, icekylinx, Dominik Scholz, James Chang,
Zhihao Chen, Aurel Prosz / Paureel, Swapnil Jain, Douglas Colkitt, OpenAI,
David Harvey, Joris van der Hoeven, and all retained contributors are credited
in the inherited notices. Original source files, licenses, and notices remain.
