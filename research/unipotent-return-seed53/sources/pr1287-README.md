# Three-cycle output frames replace workspace restorations

This **recursive-interface research construction** extends the paid output-frame
idea of Sagar Thakrar's [PR1227](https://github.com/CrocSwap/integer-mult-bounds/pull/1227)
from scalar sign drift to a non-scalar three-cycle. The extension needs a real
admission condition: `R P = Q R`. Arbitrary readers do not satisfy it.

For the frozen five-child example (`N=9` workspace coordinates, `d=3` output
coordinates), the complete source-only dirty echo costs **504 signed ADD
instructions instead of 588**. Both words restore every arbitrary scratch input.
A shortest boundary planner, full emitted recursive words and exact failure
controls make the result checkable. No selected supplier or new κ is claimed.

## Fixed child contract and changed restriction

Let `P` cyclically permute each of `m` workspace triples and `Q` each of `n`
output triples, sending `(a,b,c)` to `(c,a,b)`. Put `N=3m`, `d=3n`. The fixed,
indivisible child contract is

```
C_i(D,W) = (D + R_i W, P W),       R_i P = Q R_i.
```

Children preserve their arbitrary private scratch and expose their literal
inverse at the same signed ADD count. Unlike sign-drifting children, these calls
are **not involutions**. Source/coefficient access and the internal source
permutation are part of the child bill. All maps here are exact and linear.

For this particular `P,Q`, admission is equivalent to every 3×3 block of `R_i`
being circulant. Thus readers may inspect changing workspace coordinates;
they need not be invariant readers. The compiler checks the equality before
emitting a word. A separate dense multiplication check agrees on all 19,683
3×3 matrices with entries in `{-1,0,1}`: exactly 27 are admitted. This is a
finite admission census, not a claim that only those integer readers exist.

The parent may apply only complete-register `P^u` and `Q^v`, `u,v∈{0,1,2}`,
in gaps around the fixed ordered children. Each nontrivial power uses one
six-ADD rotation per triple. The existing six-primitive upper bound is credited
to [PR1145](https://github.com/CrocSwap/integer-mult-bounds/pull/1145); no new
rotation-circuit or minimality claim is made here. For power two, emit

```
a += b; b -= a; a += b; b += c; c -= b; b += c.
```

This sends `(a,b,c)` to `(b,c,a)`. Power one is its literal inverse. Neither
power uses a NEG, extra register, free frame annotation or unpriced temporary.
The executable checks these exact words; PR1145's lower-bound census is not
replayed or needed. Both eager and optimized batches use this same cheaper
rotation backend.

The restriction to indivisible children is essential. The demonstration leaves
expose their terminal permutations, so a compiler allowed to remove those
permutations and sum their matrices directly beats both wrappers. This result
is an exact interface construction, not an optimal matrix algorithm. No actual
supplier with this indivisible boundary has been identified.

## A sharp uniform boundary recurrence

Write `A=m`, `B=n` for workspace/output costs in triple rotations; each costs six ADDs.
Let `p,q∈Z/3Z` be their respective current phases. A uniform correct word must
have `p=q` immediately before each child: after normalization of the output,
that child's contribution is `Q^(p-q) R_i W`. Independently varying `R_i`
among admitted readers includes an identity block in any block position, so a
nonzero phase cannot give the intended contribution for all readers. Arbitrary
incoming output also forces total output phase zero. This argument concerns a
word uniform over that reader class, not an accidentally cancelling fixed tuple.

Calling a child takes aligned phase `t` to `(p,q)=(t+1,t)`. A gap returning to
aligned phase `s` therefore has the unique powers

```
u = s-t-1 mod 3,     v = s-t mod 3,
c(t,s) = A [u != 0] + B [v != 0].
```

Entrance phases cost `F_0(t)=(A+B)[t!=0]`. For each of `k` children, use

```
F_(j+1)(s) = min_t (F_j(t) + c(t,s));     b(k,A,B) = F_k(0).
```

This is an exact three-state shortest-path recurrence, with predecessor paths
retained by `model.plan`. It includes entrance and exit corrections. All gap
operations commute between the two disjoint registers; within one register
they reduce modulo three. Repeated powers cannot be cheaper than their reduced
representative at these positive symmetric prices. Thus every admissible
uniform word has such a path, and every path is realized. Induction proves the
recurrence for **all positive k,m,n**; the finite census below is a separate
implementation check, not its proof. Checkpoints requiring canonical registers
would additionally force phase zero at those cuts and are not optimized here.

For the seed fixture, `b(5,3,1)=8`, versus the eager `5*3=15`. Its word calls
child one directly, rotates output by `Q` before each remaining child, then
applies `P` to workspace and `Q²` to output at exit. Four output rotations cost
4 triple rotations; final workspace/output corrections cost 3+1. Both
registers return to the canonical frame, with `D` increased by `(sum_i R_i)W`.

This is distinct from PR1227's parity formula: a two-child boundary already
admits a three-operation alternative (`A+2B`), and child inversion cannot be
replaced by a forward call. The non-scalar admission and order-three boundary
planner are the added evidence. The output-frame idea and dirty-echo method
remain predecessor credit.

## Complete echo and recursive implementation

Let the completed batch be `H(D,W)=(D+L W,W)`, where `L=sum_i R_i`. Execute

```
W += X; H(D,W); W -= X; H^-1(D,W).
```

It returns `(D+L X, X, W_initial)` for every initial dirty `W,D`. Both copies
and both sets of complete child calls are paid. `H^-1` is the actual reverse
instruction word, with every ADD sign reversed; no involution shortcut is used.
All active ancestors' outputs and sources remain outside descendant scratch.
Siblings reuse a block only after the complete child returns.

A leaf emits its signed matrix ADDs and `P` on its source. An internal reader
emits the above echo using its children and then applies `P` to its own source.
Sums of admitted readers remain admitted, so this recursively satisfies the
same child contract. One width-N dirty block per active internal level suffices;
no initialization or hidden clean accumulator is used.

Let `a_v,c_v` count direct ADDs and triple rotations, respectively, **including all
descendants**. With fixed common dimensions, the complete recurrence is

```
leaf:     a_v = sum of absolute matrix entries; c_v = m
internal: a_v = 2 sum_i a_i + 2N
          c_v = 2 sum_i c_i + 2 b(k_v,m,n) + m
```

For a root echo omit the final `+m`. Eager restoration replaces `b` by `m k_v`.
After expansion, `ADD=a_v+6c_v`, `NEG=0`. At maximum depth `h` (leaf depth 0),
data storage is `d+(h+1)N`, counting output, source and all dirty work blocks.
This is a complete depth recurrence, not an asymptotic input-size recurrence.
With inclusive addressed-machine ADD price `alpha`, the reader bill is

`T_v = 2 sum_i T_i + [2N + 6(2b+m)] alpha`.

Preparation, descriptor access and routing are separate resources, not free
recursive work. The supplied compiler materializes `P_len=ADD` primitives
from description size `M`. Its planner stores complete path tuples, giving
`O(k²)` preparation time and `O(k)` live path space per distinct child count
(cached afterward). A conservative uncached whole-tree bound is
`O((h+1)(M+P_len) + sum_v k_v²)` preparation time and
`O(M+P_len+sum_v k_v+h)` compiler/program storage. This cost is additional to
the execution recurrence; no total preparation-plus-execution improvement is
claimed. The finite word must then be read. The source matrix entries and
signed operands appear in that word; no runtime multiplication or coefficient oracle is assumed for ±1 leaves.

| Complete seed echo | Eager | Output frames |
| --- | ---: | ---: |
| Direct ADDs | 228 | 228 |
| Triple rotations, including child source drift | 60 | 46 |
| Expanded signed ADDs | 588 | 504 |
| NEGs | 0 | 0 |
| Dispatches / writes | 588 | 504 |
| Data reads | 1176 | 1008 |
| Instruction fields | 2352 | 2016 |
| Declared data-address travel | 7286 | 7234 |
| Data registers | 21 | 21 |
| Exact forward prefix row-L1 peak | 31 | 42 |
| Exact inverse prefix row-L1 peak, arbitrary inverse input | 28 | 40 |

ADD reads two cells and writes one; records contain four fields, including
the sign and addresses. Thus reads=`2ADD`, writes=dispatches=`ADD`,
fields=`4ADD`. `oracle.invoice` independently reconstructs the access
records. The travel column visits each ADD's source then destination and
returns a cursor to zero. It is an exact score for this specified layout/access
trace, **not a constructed tape-machine implementation**.

Arithmetic savings need not improve every resource. The depth-three witness
saves 1,548 primitives (9,408→7,860), but its travel score rises
137,726→141,338 and its prefix bound rises 65→106. Even the small fixture's
prefix bound rises 31→42. These costs must not be hidden in supplier adoption.
For this finite exact word, input magnitude ≤M gives coordinate magnitude
≤`prefix_l1_peak*M`; finite bit-width or rational representation costs are not
incorporated into a multiplication bound. No fixed-precision/rounded-leaf
contract, physical routing, hosting, common-label, all-size or analytic result
is established.

## Reproduction and completed coverage

Standard library only; from the repository root:

```sh
python3.12 scripts/research_package.py --package research/cyclic-output-restoration
```

Expected final marker: `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome completed.
The direct checker is `python3 -I -O -B research/cyclic-output-restoration/verify.py`;
its marker reports `saved_rotations=14 saved_primitives=84 no_new_kappa`.
`--emit` regenerates the complete certificate, which ordinary replay compares
field for field. Required checks use explicit exceptions and still run with `-O`.

Completed domains, with stopping rule **exhaust exactly these finite sets**:

- All 66,420 normalized boundary schedules through four children, including
  all entrance and exit choices. The code-disjoint oracle propagates a distinct
  symbolic response for each child through literal output rotations, without
  using the planner's alignment predicate. The 120 admitted schedules give the
  same minima at all 100 `1<=m,n<=5` price comparisons. Another 150 checks test
  price scaling and the eager upper bound through 30 children; these are not
  exhaustive schedule censuses at those lengths.
- All 19,683 ternary 3×3 readers, using indexed admission and independent dense
  matrix products; 27 admitted, 19,656 rejected.
- `1<=m<=3`, `1<=n<=2`, `1<=k<=4`, depths 1 and 2, echo/reader contracts and
  eager/optimized words: 192 cases, 3,744 basis columns and 157,704 forward
  primitive occurrences. Every case checks all arbitrary dirty-state columns,
  literal inverse (also from arbitrary inverse input against a separate block
  inverse formula), macro expansion, recurrence, access invoice and a rational
  dirty probe. A frozen five-child fixture and a separate depth-three witness
  are also fully checked. Leaf entries come from `random.Random(56)` over
  `{-1,0,1}`; the depth-three example uses seed 57.
- Ten mathematical controls reject missing copies/restoration/output frames,
  incorrect rotation expansion, a forward-for-inverse substitution, non-equivariant
  readers, premature canonical observations and nonlinear dirty substitution.
  `test_package.py` adds API input, plan-path, relocation and corruption checks.

No finite replay is a formal proof of the complete multiplication theorem.
Neither human peer review nor hosted CI success is inferred from local passes.
The selected supplier is unchanged, so its expensive cold replay was not run.

## Provenance and credit

Exact base: `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`; OS assignment seed **56**,
recursive interfaces. The selected construction is Rohan Arun's PR1094 on
Jeremy Kothe's retained word/packing and the PR589/555 bit lineage, with
κ=`836330098538459/500000000000000000`. The actual selected construction, review,
source manifest and certificate were inspected and pinned as historical context
in `SOURCES.json`. `upstream/`, the selected record and frozen packages are unchanged.

Sagar Thakrar's PR1227 (`fea44a4d0d78570021d854881d15d9efe62e1713`) supplies the
paid output-sign mechanism and complete echo comparison. MightyOil/Philipp's
PR1203 (`38459854fd5bb93099871a84324413bd0e338d8e`) supplies noncommuting invariant
readers and source-only restoration accounting. Ross Richardson's PR1145
(`fd4d5ffc448361297e717aa30eafed578caf8e61`) supplies the existing six-ADD three-cycle upper bound, found in the final overlap check and
used for both words. Its CK/JP8 lower bounds and PR1216's restored-donor extension
concern different boundary alphabets; neither is re-established here. These
three README files, original notices, Git blob IDs and SHA256 hashes are retained in `sources/` and
`PREDECESSORS.json`; no executable predecessor code is imported. Also credit
Aaron Wang/Navinor PR1155, Sagar Thakrar PR1199, Adam Gall PR1205, and Ross
Richardson/CubeJerry PR889 for the existing restoration and dirty-echo lineages.
Hanson Sun's concurrent [PR1246](https://github.com/CrocSwap/integer-mult-bounds/pull/1246)
adds paid additive defect repair at canonical partition cuts; its head
`5ed1ce17a9df4c853a93f9758ba903d2620c3443` was inspected at submission. It is
distinct from keeping output in a moving cyclic frame between fixed calls.
No code, certificate or mathematical dependency is imported from it.

This package does not claim priority for their compatible-reader corrections,
observation distinctions or output-frame/echo principles.

Prepared by **Ross Richardson** with substantial **OpenAI Codex assistance** in
algebra, implementation, verification and prose, including both code paths.
No independent human audit is claimed. New material is Apache-2.0 under the
repository license; retained sources keep their original credit and notices.
The scoped claim, three considered candidates and overlap coverage are in
`CLAIM.md`; structured outcome and next questions are in `TASK.json`.

## Open next questions

Does a supported supplier expose an indivisible cyclic-equivariant reader with
a cheaper output action than workspace restoration? Test one candidate's exact
source-return map for `R P=Q R`, then price its routing, precision and retained
child boundary. Those missing supplier facts currently block an asymptotic
application. If its source drift can simply be deleted inside the child, reject
it as evidence for this wrapper's algorithmic benefit.

Can canonical intermediate checkpoints retain enough of this saving? A first
step is to constrain phase zero at a specified cut in the same three-state
recurrence, then emit and price that word. This would address observation
requirements; no adaptive observer implementation is supplied here.
