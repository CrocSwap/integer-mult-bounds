# Split-pair recursion with dual-suffix strips and ranked joint frames

Under the inherited base theorem, residual-compiler, fixed finite-alphabet
multitape, analytic, routing and recovery hypotheses, the pinned construction
supports

$$
 T(n)=O\bigl(n(\log n)^{1-\kappa}\bigr),\qquad
 \kappa=\frac{120777349}{2500000000000}=4.83109396\times10^{-5}.
$$

The exact bit saving is $a_b=2415663683/50000000000000$; the unchanged
complex saving is $717/10^7$. The saving improves PR60's
$4764513337/10^{14}$ by approximately **1.3974275711%**, and remains strictly
between $2^{-15}$ and $2^{-14}$. These compare conditional asymptotic
exponents, not measured running times.

The new contribution composes Rohan Garg's PR59 split-pair recursion choices
with Rohan Gupta's PR55 dual-suffix layout and its native summand orders.
The PR60 ranked reclamation engine, descended from eumemic's PR57 compiler,
is byte-identical. No paid clone or recorded PR59 permutation is used.
The prior PR60 word, fixed profiles and numerical result remain available
through their original verifier. Its exact published comparison certificate
and source/proof provenance are also preserved independently under
`references/frame-compiler/pr60`.

## 1. Pinned graph construction

PR59's 14 fetched originals are retained byte-for-byte at commit
`641f22e52913db784f3b6ff1176b0c2945aae45b`, including the original notices.
The provider consumes `split_graph.py`, its skip-prefix base and the shared
circuit dependencies. The three circuit dependencies are byte-identical to
PR48's pinned copies. The PR55 layout is retained at
`03e991aa79f9df1a935726213bb6a8631cd0d823`; PR60's complete published baseline
is pinned at `21a121960644b8c6fdf9c06fe39dea1944dd2231`.

The explicit graph configurations are:

| Choice | h=23 | h=25 |
|---|---|---|
| Split-pair group vector | `[1,3,2]` | `[1,2,2]` |
| Total fold order | `reverse` | `desc` |
| Top strip order | `input` | `input` |
| Deeper strip order | `asc` | `support_desc` |

At each recursive level, the selected group vector entry splits one chosen
pair into two singleton groups: 1 chooses the first pair, 2 the middle pair,
and 3 the last pair. Groups remain disjoint, exhaust the current point set,
have size one or two, and strictly reduce the recursive point count. Deeper
unspecified entries retain ordinary pairing. The inherited alternating
common-point order remains unchanged. The explicit configuration omits
PR59's `totals`, `strips` and `points` permutation dictionaries.
The actual recursive point counts are $22\to12\to7\to5\to3\to2$ and
$24\to13\to8\to5\to3\to2$ respectively.

For an ordered vector $v_1,\ldots,v_k$, put
$A_i=\sum_{r\le i}v_r$ and $B_i=\sum_{r\ge i}v_r$, with empty sums zero.
PR55's layout computes

$$
 s_j=(A_{j-1}+v_{j+1})+B_{j+2}\quad(1\le j<k),\qquad s_k=A_{k-1}.
$$

The three summands have disjoint index ranges whose union is exactly the
indices other than $j$. The total is $A_{k-1}+v_k$. Lengths at most two,
zero entries and restoration of output order are handled explicitly.
The recursive split graph uses this exact leave-one-out identity in its
paired-exclusion decomposition. Full finite scalar verification checks every
addition, disjoint support, retained total and indexed partial output on both
complete graphs. Since those checks use the symbolic source basis, they
establish the required fixed-dimensional scalar maps on arbitrary inputs.

`split_dual_graph.py` uses privately loaded source modules. It restores the
generic module binding and import path after loading, and restores the original
strip function after each graph construction, including exceptional exits.
`split_dual_compiler.py` likewise restores the compiler's original graph
provider. No imported original source file is edited.

At dimension $h\in\{23,25\}$ the $v_h=\binom h3$ source symbols correspond
to triples. Each non-source retains the original rational envelope

$$
 E(C,U)=\{x:\operatorname{supp}(x)\subseteq U,\ x_i=t\ (i\in C),
                  \ \sum_i x_i=3t\},
$$

with address metric $I-J/9$ and rank $|U|-|C|$; a source has its triple line.
The replay checks actual cores, covers, lines and output frames. Address
arithmetic and binary payload arithmetic remain distinct. No enlarged positive
frame is introduced.

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
| Auxiliary roles $R_h$ | 30,118 | 39,663 |
| Basis columns $2v_h+R_h$ | 33,660 | 44,263 |
| XORs in $L$ | 113,218 | 149,195 |
| Signal-clearing XORs, included above | 4,653 | 5,665 |
| Full wrapped word length | 477,666 | 628,980 |
| Copied local rank mass | 693,220 | 992,175 |

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
 W=2N+2300R_{23}+1771R_{25}=147,661,173.
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
 s=mW-N+L=84,903,327,575,\qquad mW-s=1,846,900.
$$

Every child width is positive and smaller than 575; the maximum is 529.
The characteristic at saving $u$ is

$$
 F(u)=\frac1{mW}\sum_t n_t t\exp\!\bigl(u\log(m/t)\bigr).
$$

The exact rational certificate proves $F(a_b)<1$, with gap exceeding
$1.55\times10^{-15}$. Logarithms use a 32-term atanh series with explicit
remainder and outward rational rounding. Exponentials use rigorous rational
lower and upper inequalities. No floating-point search value is admitted as a
proof bound. The next bit-saving grid point $a_b+10^{-14}$ has exact lower
moment greater than one. At $a_b$, the complete pinned PR60 child list has a rigorous lower moment
greater than one. The comparison uses the entire old network, including data,
endpoint copies, exteriors and source growth; it is not a comparison of role
counts or a rescaling of the old saving.

## 6. Balanced assembly and conditional scope

The complex branch and its semantic/scalar bounds are retained. The finite
bridge updates the actual bit width while checking its role-bit length and
halving depth. Use the inherited balanced choice with $\eta=10^{-12}$,
$q=a_b(1-2\eta)$, and
$\epsilon=(1-\eta)/(1+q)$. The new certificate checks all 47 strict assembly
conditions and all seven final margins against the displayed $\kappa$, and
recomputes the eventual cutoff inequalities. The smallest margin exceeds
$\kappa$ by more than $2.09\times10^{-16}$. The next $10^{-14}$ kappa grid
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

Run `make split-dual-verify`, then `make verify`. The focused target checks the
complete source/finite-input closure, regenerates both selected physical words
and matches their decompressed bytes, independently replays every dirty basis
column, reconstructs every transition, and recomputes all actual CRT profiles.
It also checks exact moments, the complete old-PR60 exclusion, all assembly
inequalities, eventual cutoffs and next-grid rejection. Mutation controls cover
missing XORs, incompatible frames, aliased terminals, omitted center cleanup,
understated widths, omitted transitions and provider restoration on failures.
Certificate entry points explicitly reject Python with assertions disabled.

The root README, Makefile and NOTICE are pinned by the previous package. Adding
this separate target and attribution therefore refreshes that package's source
binding and derived metadata; its engine, physical words, profiles and exact
numerical theorem remain unchanged. The immutable PR60 comparison snapshot is
not regenerated. The full suite retains its existing verifier, every recovered
upstream audit, all historical patch checks and both inherited formal packages
in CI. Validation receipts record their actual tested states and status.

Rohan Garg / rohangar1 with substantial OpenAI Codex assistance supplied PR59's
split-pair recursion and group vectors. Rohan Gupta / gupt1156 with Anthropic
Claude assistance supplied PR55's dual-suffix layout. Eumemic with substantial
OpenAI Codex assistance supplied PR57's joint frame compiler and independent
word/profile machinery. Chafik Boukhalfa with OpenAI Codex assistance supplied
PR60's ranked reclamation and this separate composition, explicit provider,
comparison and exact integration.

Avi Eisenberg / ikeboy with Anthropic Claude assistance, Rohan Arun with
Anthropic Claude assistance, RaD / hipotures with OpenAI Codex assistance,
icekylinx, Dominik Scholz, James Chang, Zhihao Chen, Aurel Prosz / Paureel,
Swapnil Jain, Douglas Colkitt, OpenAI, David Harvey, Joris van der Hoeven and all
retained contributors remain credited in original source files and notices.
No authorship, review or endorsement by those predecessors is implied.
