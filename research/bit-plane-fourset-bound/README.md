# P111 four-port upgrades: the ten-term saving is at most 17

For all **49,648** four-port sets left open by the sampled `n1 = 10` case in
[discussion #2278](https://github.com/CrocSwap/integer-mult-bounds/discussions/2278#discussioncomment-18946829),
there are at most **seven compatible cost-six pair terms**. Consequently ten
two-sided label terms have rational pairing cost at least **63**. Adding the
predecessor's four-unit residual-charge bound gives total cost **at least 67**,
which cannot improve the selected bit supplier by upgrading four ports.

This is a complete finite obstruction and a scoped proof. The ten-term bound
and its reader/target premises are checked here independently. The **total-cost
corollary retains the predecessor's residual-charge lemma**; that lemma and
other term-count branches are not re-proved here. No supplier or new κ is claimed.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

## Question, source and added value

Philippe Van Velzen's `plane-step1` package at commit
[`0a60443cf4fad2ff65bff317996c1dce02a4a09f`](https://github.com/philippeVV/integer-mult-bounds/tree/0a60443cf4fad2ff65bff317996c1dce02a4a09f/research/complex-budget-law/bit/plane-step1)
proves several restrictions on common-direction plane upgrades. Its class U
allows label-reader terms on the line ports, arbitrary plane memberships, and
additional terms supported inside the upgraded set on at least one side. Its
README explicitly leaves the four-port, ten-two-sided-term branch sampled.
`classU_small10.py 4 10` checked 4,965 of 49,648 sets, with no saving-18 witness.
The retained log reports 2,464 seconds for that sample.

This package completes the domain through a necessary subproblem: a saving of
18 would require eight cost-six terms. We exclude those eight terms directly,
without enumerating the remaining terms. The checker imports no predecessor
code, derives the puncture from the selected word, and enumerates four-subsets
directly rather than taking subsets of a stored maximal-set list. The source
files needed to identify the contract and prior coverage are retained byte for
byte under `predecessor/`; their exact Git blobs and SHA256 hashes are in
[SOURCES.json](SOURCES.json).

The claim is in discussion #2278. [TASK.json](TASK.json) records the changed
`bit-helper-contract` scope and the explicit decoder handoff. This account's
PR #1421 independently reconstructed the selected bit rank ledger; the present
work changes the decoder question and does not repeat that ledger audit.
PR #2423's R438 hosting proposal concerns a different word and interface.

## Why this bears on the bit wall

At the pinned main commit, the selected BIT primitive is PR #589 on #555, with
saving `0.001733427039589844234749`. The selected nine-stage format has
`m = 64`, `W = 28416`, and 288 local calls. Its nine rank-seven COPY charges
cost 63 per call, giving deficit `W - 288*63 = 10272`. Helper work contributes
recursive cost without increasing this deficit. These are inherited accounting
facts, not new results of this package.

Under the predecessor's partial-upgrade coverage law, upgrading four ports
improves the deficit only when `ΔC < (8/9)*4 = 32/9`. Integer cost would therefore
need `C <= 66`, compared with the incumbent 63. The ten-term branch costs at
least `63 + 4 = 67` under the retained residual lemma: its added cost is at least
four, and its deficit change is at most `4 - (9/8)*4 = -1/2` per call. This is an
optimistic decoder screen. Physical frames, hosting and other charges cannot
rescue this branch by adding cost. A different support class can change the
premises.

The ordinary baseline command is `python3 -B scripts/research_baseline.py`.
It checks selected source bindings and arithmetic, not a complete cold replay.

## Exact domain and tariff

Use the 111 ordered norm-four root representatives from the pinned PR589 word.
Reflection closure produces the 240 roots of E8. Append the nine omitted root
lines in lexicographic order after choosing their first nonzero coordinate
positive; their indices are `P = {111,...,119}`. Write

`G[x,y] = dot(root[x], root[y])/2`, and `B[x,y] = (1 + G[x,y]) mod 2`.

The domain consists of each distinct four-set `S` of live indices such that:

- every two different members of S have nonzero rational inner product;
- some omitted root `r in P` is perpendicular to all four members.

This is equivalent to the predecessor's four-subsets of maximal pairwise-odd
common-r sets: every finite clique extends to a maximal clique. A set admitting
more than one r is tested once; the certificate records every r incidence.
The effective puncture for line-reader costs is `P' = P union S`.

Cost is **rational pairing rank** between the reader and source spans. Binary
label rank is used for the decoder identity, not substituted for this tariff.
The positive control reproduces the incumbent's nine rational costs of seven.
Plane memberships can only enlarge the pairing matrix, so the line-only cost
is a lower bound on each whole term.

## Reader and target premises after any four deletions

Let `u_x` be row `B[x,P]` as a vector in `F2^9`, and let
`Q = inverse(B[P,P])`. The checker verifies all 14,400 identities
`u_x^T Q u_y = B[x,y]`. In particular Q is symmetric and nonsingular.
A label reader with nonzero functional f is
`{x in L : u_x^T f = 1}`. Put `lambda_x = Q u_x`.

The checker constructs five **pairwise disjoint** bases for each of the 511
nonzero functionals, then checks every basis over the rationals:

- For `f = lambda_x`, remove x itself if live. All remaining readers lie in
  `root[x]^perp`, and each of the five bases has rank seven.
- For every other f, all five bases have rank eight.

Deleting four live lines can hit at most four of the five disjoint bases.
Thus every nonzero reader on `L minus S` has rank at least seven. Its span has
rank seven exactly for `lambda_x` with `x in P'`; the span then equals
`root[x]^perp`. If x remains live, x together with a surviving perpendicular
basis gives rank eight. This premise is established for **any** four deletions,
not only the 49,648 common-r sets. Modular elimination only proposes bases;
separate `Fraction` elimination certifies their rational ranks.

For the target premise, partition the 111 live indices into five disjoint
blocks of 22 or 23 lines. In each block the equations on diagonal and
nonorthogonal ordered pairs have rank 81 on the 81 coefficients of a binary
9-by-9 matrix X. The checker verifies all five ranks. After any four deletions
at least one block remains intact. Since Q satisfies those equations, a
label-term decoder on the remaining lines must satisfy

`sum_j f_j g_j^T = Q`.

Terms supported only on S on one side contribute zero to this line-line block.
The five blocks and the hash of the 2,555 constructed reader bases are in the
receipt; all bases are rebuilt and checked on every replay. Fixed permutations
are used only to find witnesses, never as an acceptance assumption.

## Why eight cheap terms are necessary

For two reduced reader spans `H_x = root[x]^perp`, `H_y = root[y]^perp`, the
pairing rank is six precisely when `x != y` and `G[x,y] = 0`. Indeed its left
kernel is `H_x intersect span(root[y])`, which is one-dimensional exactly in
that case. Otherwise their pairing rank is seven. A full eight-dimensional
span paired with a hyperplane costs seven, and two full spans cost eight.

Therefore every two-sided term costs at least six; a term of cost six must be
an orthogonal reduced pair `(lambda_x, lambda_y)` with `x,y in P'`. Every other
term costs at least seven. Ten terms of cost at most 62 would require at least
eight such pairs. Equivalently, measuring savings against ten costs of eight,
each pair saves at most two and every other term at most one.

Let F and H be the 9-by-10 matrices of the two-sided reader and source
functionals. Since `F H^T = Q`, the matrix

`M = F^T Q^(-1) H`

is a rank-nine idempotent. Hence `M = I + w v^T`, where `v^T w = 1` over F2.
For a cheap pair at index i, `M[i,i] = B[x_i,y_i] = 1`, so `v_i w_i = 0`.
Only three types `(v_i,w_i)` are possible: `(0,0)`, `(1,0)`, `(0,1)`.
For two different cheap pairs,

`B[x_i,y_j] = v_j w_i` and `B[x_j,y_i] = v_i w_j`.

Cheap pairs have distinct readers and distinct sources. If two readers
coincided, the corresponding rows of M would coincide, forcing
`v = e_i + e_j` and `w_i != w_j`. But their cheap diagonal conditions would then
force `w_i = w_j = 0`, a contradiction. Transposition proves source distinctness.

## Complete finite certificate

For each P', build a graph with vertices `(v,w,x,y)` for all three types and
all ordered orthogonal pairs in P'. Join two vertices exactly when their
readers and sources are distinct and both cross equations above hold.
Every collection of eight cheap terms would be an eight-clique.

The exhaustive checker finds **no eight-clique in any of the 49,648 graphs**.
The algorithm branches on every possible next vertex. It prunes only by the
remaining vertex count or a proper greedy coloring. Each color class is an
independent set; reverse removal preserves the prefix color bound. Thus a
prune cannot discard a clique of the required size. There is no time, depth,
seed or node cutoff in this search.

Consequently the pair count is at most seven, savings at most
`2*7 + (10-7) = 17`, and the ten-term cost at least 63. The bound is not asserted
to be sharp. No completion of the two other terms, parity condition on the
whole ten-term word, or ancillary repeated-line rule is needed: these are
additional restrictions, and omitting them makes the exclusion stronger.

For the **conditional** whole-cost consequence, the predecessor's class-U
rank argument charges at least `2*g(s-1)` outside these ten terms, where
`g(3)=2`. Thus `C >= 63+4 = 67`, excluding the required `C <= 66`.
This is exactly the sampled savings-18 question in `classU_small10.py`.
We do not promote the residual-charge argument to an independently checked
result merely because its arithmetic agrees.

## Reproduce and controls

From the repository root, Python 3.12, standard library only:

```sh
python3 -I -B scripts/research_package.py --package research/bit-plane-fourset-bound --check-only
python3 -I -B scripts/research_package.py --package research/bit-plane-fourset-bound
python3 -I -O -B research/bit-plane-fourset-bound/verify.py --controls-only
```

The full replay takes about three minutes on one CPU and prints:

```text
PASS_BIT_PLANE_FOURSET_BOUND sets=49648 eight_pair_witnesses=0 pair_cap=7 savings_cap=17 conditional_cost_floor=67 no_new_kappa
```

It authenticates the selected word and retained predecessor bytes before use,
regenerates the entire domain and graph sequence, and compares the complete
[CERTIFICATE.json](CERTIFICATE.json), including case/graph hashes and search
counts. It checks the clique engine against a separate brute-force subset
oracle on all 1,024 labeled five-vertex graphs. The predecessor's real nine-pair
E8 dual system is a positive control: the search finds nine compatible pairs
outside the claimed puncture domain, and its outer products give Q exactly.
Six controls reject wrong pair types, duplicate readers, a forbidden type-11
pair, a nonorthogonal self-pair, corrupted source bytes and a singular form.
Assertions are not used for acceptance, so `-O` cannot remove the checks.

`--write-certificate` regenerates only this package's receipt. It is a research
maintenance command, not part of registered replay. No source package is changed.

## Limits

- The finite pair obstruction and robust reader/target certificates are checked
  here; the four-unit class-U residual bound is an explicitly retained premise.
- The other term counts, the fifteen exceptional three-sets, arbitrary supports
  on line ports and different common-direction models are outside this result.
- No physical decoder word, row-stock bound, native frame implementation,
  chronological hosting, recursive compiler, precision analysis, analytic
  transfer or full supplier cold replay is supplied.
- The code and proof were prepared and checked with AI assistance. They have not
  received independent human review or a kernel-checked formal proof.

## Open next questions

1. **Independently prove the class-U residual charge for punctured r.** The
   ten-term finite gap is closed, but the cost-67 corollary still invokes that
   rank argument. First derive the source/reader quotient maps for the actual
   four-plane mask and prove the required two charged dimensions on each side.
   The blocker is the implication for arbitrary S-supported correction terms.
2. **Resolve the fifteen exceptional three-sets.** The predecessor reports a
   cost-65 boundary there. Reconstruct those exact sets and test the remaining
   nine-term/anchored-correction case; the ten-term branch has separate coverage.
   A new positive construction must include the rational pairing tariff.
3. **Change the line-support premise.** Any saving in the fully arbitrary-support
   model must evade the label-reader reduction. Start with one explicit small
   non-label term and price the complete decoder. A binary factorization of
   labels alone does not establish the port-space endpoint or its cost.

## Credit and provenance

Philippe Van Velzen (@philippeVV) supplied the common-r problem, classes P/U,
necessary ten-term relaxation, sampled four-set result and positive dual-system
fixture. The retained files are from his public fork, not an admitted selected
supplier. The current fork head `2f71bc21dea63204403aefcb83323b6560e70fe4` was
checked at entry and leaves this predecessor subtree unchanged.

DreamingOfClouds supplied PR #589 and related format/decoder work, on eumemic's
PR #555, with DaysSky and the E8 construction/hosting lineage retained. This
account's earlier selected ledger checks are credited above. New code is
Apache-2.0; retained source files preserve their original text and the public
repository's Apache-2.0 license. No predecessor code is executed by this checker.

Base main: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Selected PR #589 head: `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
