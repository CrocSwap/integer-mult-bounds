# A paid composition of balanced coarse sums, split recursion and frame order

## Statement and boundary

The complete finite profile below certifies

`kappa = 10366199626713/200000000000000000`

for the inherited conditional bound `T(n)=O(n(log n)^(1-kappa))`.
The all-size compiler, analytic transfer, fixed-alphabet tape simulation,
precision, routing, prime selection and exact recovery hypotheses are inherited.
Finite source checks and arithmetic do not establish those general hypotheses.

## 1. Pinned ingredients

PR #71 is frozen at `1bef94fd40a746452548c84a4a8f8834670a3113` in
`references/frame-compiler/pr71/`, including its complete consumed source
closure, selected words, data interfaces, licenses, notices and root documents.
Its own source manifest is preserved without re-pinning. PR #69's original
coarse-sum compiler and notices are frozen at
`91aa1f17e6e3fc063241686a41a34ddd0dc24c50` in the adjacent `pr69/` archive.

The new producer reads PR #69's literal BEFORE/AFTER replacement, applies it
exactly once to the archived PR #62 scalar graph consumed by PR #71, and keeps
PR #71's `[1,1,2]` split choices and lowest-intact-pair anchoring. The original
source files are unchanged. After reordering, it uses the archived PR #71
compiler and its next-use profile-cost selection unchanged.

## 2. Shared intermediate sums preserve the scalar map

For two disjoint groups A and B, replace the chain forming
`sum_{a in A,b in B} e(a,b)` by
`sum_{b in B} (sum_{a in A} e(a,b))`.
Each operand support occurs exactly once. The nested sums are disjoint,
so this is an equality over the inherited scalar field. Existing node
interning shares the column intermediates with later strip computations.
The singleton cases and strictly decreasing recursive partitions retain the
same identity. No negative coefficient or cancellation is introduced.

`graph_audit.py` reconstructs dense global triple-coordinate supports using
its own recurrence. For each dimension it checks every input, addition,
core, cover and prescribed output, and compares the complete output support
inventory with original PR #71. This checks 67,460 / 94,993 additions and
5,336 / 6,925 outputs. Original PR #71 has 68,771 / 96,718 additions.

## 3. Legal node order and fully charged live reclamation

Keep source IDs fixed. Group remaining active nodes by their original
(core, cover), retaining their original order within each group. Sort groups
lexicographically by

`(popcount(cover)-popcount(core), -core, cover, first_original_node)`.

Remap every operand and output ID, clear support caches indexed by old IDs,
and verify again. The independent audit proves that each literal edge and
output is preserved, every operand precedes its consumer, every envelope is
unchanged, and this is exactly the selected renumbering. Matching is recomputed
on the resulting graph and the compiler uses its natural region order.

PR #71's unchanged pending live controls enter a clearing basis only when
their current frame is contained in the present frame and that frame is
contained in their next-use frame. Controls retain their values. The complete
word contains every chosen clearing XOR and every required frame raise.
The discovery score is never substituted for the actual charged profile.

Both complete words are regenerated with dirty-basis checks enabled. A
separate serialized-word checker replays every input and arbitrary dirty
basis column in both orientations. The final roles are 27,136 / 35,744.

## 4. Coordinate relabeling and the data family

Apply each selected permutation to the frame core/cover masks, source-triple
indices, scatter target-triple indices, output common points and output
triples. Literal XORs, scratch IDs and frame IDs remain unchanged. The complete
permutations are frozen in `selection.json`; both relabeled words are replayed.

For permutation matrix P, both fixed bases `I+J` and the inverse metric
`I-J/9` commute with P. Envelope projectors therefore transform by conjugation.
Containment and every legal incidence remain valid. Ordered contiguous child
profiles can change, and every one is regenerated from the literal word
using the inherited exact bounded-minor/CRT profiler, with zero disagreements.

Each coordinate permutation induces a bijection on the complete triple set.
Consequently the complete two-axis data-block family is only reindexed: its
aggregate inherited profile and rational recovery cases remain valid. Copied
centers, endpoints and data growth remain explicitly charged.

## 5. Complete recurrence and assembly

Let `N=4073300`, `m=575`, and let `R_h` and `b_{h,t}` be the verified role count
and exact internal profile. The physical width is

`W = 2N + (N/1771)R_23 + (N/2300)R_25 = 133862024`.

The complete child multiset includes:

- data: `18N` children of size 1 and `2N` each of sizes 21, 17 and 481;
- paid endpoint copies: `N` additional size-1 children;
- internal axis h: `(N/binom(h,3))*b_{h,t}` children of size t;
- exterior axis h: `(N/binom(h,3))*R_h` each of sizes h and `m-2h`;
- data growth per axis: `2N` each of sizes 1 and `h-2`.

The total rank is `76968816900 = mW-1846900`; maximum child size is 529.
The exact characteristic is
`M(a)=sum_t (t*n_t/(mW))*exp(a*log(m/t))`.
At `a=25916842362591/500000000000000000`, a rigorous upper bound is below 1.
At `a+10^-18`, a rigorous lower bound is above 1. Positive logarithms make
the characteristic increasing. The complete original PR #71 profile is
separately excluded at the new accepted saving.

Production arithmetic uses the retained rational logarithm/exponential
helper. The independent checker derives the complete paid multiset and uses
40 exact atanh terms for logarithms and Taylor degree 10 with a geometric
exponential tail. It imports no production arithmetic and checks each of the
47 assembly slacks and seven margins independently. The next kappa grid value
is rejected. Negative controls reject altered role counts, fabricated slacks
and incorrect source hashes.

Use positive backoff `10^-18`. Since W is below `2^27`, its `bit_length()` is
27. The product-row coefficient becomes `9*27+20*30=843`. Keeping degree 2000
and suffix slope 8000 gives degree gap `2000-(51/25)*843=7007/25`.
These values are derived and checked; no stale predecessor constants remain.
Arithmetic cutoff bounds are not complete operational runtime thresholds.

## Credits

The composition, core-order continuation, coordinate choices, packaging and
independent audits were prepared for Thomas DiFiore with substantial OpenAI
Codex assistance. Coarse-sum reassociation is eumemic's PR #69. Anchored split
frames and next-use-aware live selection are Chafik Boukhalfa's PR #71.
Rohan Garg supplied the split operation (#59); Avi Eisenberg supplied interval
strips and core-aware pair assembly (#62); Rohan Arun supplied region schedules
and profile-cost selection (#65/#67); Dominik Scholz supplied ranked composition
and pending live controls (#63/#68); eumemic supplied the reversible compiler
and physical/profile checking interfaces (#57). Our earlier PR #74 supplied the
core node ordering and coordinate-relabeling continuation used here.

The preserved archives retain all earlier credits, including RaD/hipotures,
icekylinx, James Chang, Zhihao Chen, Aurel Prosz, Swapnil Jain, Alejandro Zarzuelo
Urdiales, Douglas Colkitt, OpenAI and Harvey–van der Hoeven, and predecessor
AI-assistance disclosures. No predecessor authorship or endorsement of this
composition is implied. Existing licenses and notices remain in force.
