# Proof and scope of the grid-bounded coefficient search

This note concerns the frozen historical PR626 JP8 scalar event streams. It
does not modify the selected supplier or establish a new multiplication
constant. The claim is a finite circuit result in the explicitly defined
single-work-register class below. The executable certificate and independent
checker supply the finite coverage evidence; this note explains why those
checks establish that claim.

## 1. Register contract and admissible words

An addition macro with nonzero dyadic coefficient

\[
q=\sigma a/d,\qquad \sigma\in\{-1,1\},\quad a>0,\quad
d=2^k,\quad \gcd(a,d)=1
\]

has the complete boundary map

\[
(T,S,W)\longmapsto(T+qS,S,0).
\]

The three registers are distinct. Their incoming values are arbitrary and
may be correlated; in particular, `W` is not assumed initially zero. The
source and target stay untouched while the coefficient is prepared. A word
in the searched class consists of:

1. One paid copy `W <- S`.
2. Any finite sequence of `W <- W + S`, `W <- W - S`,
   `W <- 2 W`, `W <- W/2`, or `W <- -W`.
3. One signed target accumulation, using the final `W`.
4. One paid clear `W <- 0`.

At every preparation prefix, including immediately after the copy,
`W = c S` for a dyadic `c` satisfying

\[
c\in d^{-1}\mathbb Z,\qquad |c|\le a.
\]

The terminal coefficient is either `a/d` or `-a/d`. If it is
`epsilon * a/d`, the target update uses sign `sigma * epsilon`. This makes
the final map exactly the displayed contract for either sign of `q`.

Here the bound is on the **magnitude of the coefficient** `|c|`, not on the
reduced numerator of `c` and not on the scaled graph coordinate defined
below. The source range is reduced `a <= 127`, `d <= 16`; the actual corpus
contains 49 nonunit absolute coefficients. The coefficient `|q| = 1` uses
the established direct circuit `T <- T +/- S; W <- 0`, costing two
primitives. Its special two-instruction circuit is outside the mandatory
copy/preparation/accumulation/clear form.

Every instruction uses the macro's original frame. No source modification,
source restoration, extra register, helper, frame transition, recursive
child, or transfer of work across macro boundaries is allowed in this
search. The optimality claim does not cover circuits allowing any of those
operations, multiple target updates, different initialization, or a larger
grid or magnitude envelope.

## 2. Exact finite graph

Write `c = m/d`. The vertex set, initial vertex and terminal set are

\[
V_{a,d}=\{-ad,-ad+1,\ldots,ad\},\qquad m_0=d,\qquad
G=\{-a,a\}.
\]

There is a unit-cost directed edge for each admitted operation:

| Work instruction | Graph edge | Additional condition |
| --- | --- | --- |
| `W += S` | `m -> m+d` | destination belongs to `V` |
| `W -= S` | `m -> m-d` | destination belongs to `V` |
| double | `m -> 2m` | destination belongs to `V` |
| halve | `m -> m/2` | `m` is even and destination belongs to `V` |
| negate | `m -> -m` | destination belongs to `V` |

The parity condition is necessary: halving an odd `m` would produce a
coefficient on a strictly finer grid. Halving can be legal when the source
happens to have special divisibility, but such input-dependent shortcuts
are deliberately excluded: the macro must work for arbitrary source input.

Induction on instructions gives a cost-preserving correspondence between
admissible preparation words and directed walks from `d` to `G`. The
graph therefore contains every preparation word in the stated class, not
merely binary, signed-digit or monotone words. Conversely, each graph edge
is one legal primitive. Removing a repeated-vertex cycle never increases
cost; hence the finite graph suffices even though words of unbounded length
are allowed. There are `2ad+1` vertices, at most 4,065 under the stated
parameter bounds.

If `L(a,d)` is the shortest distance from `d` to `G`, the optimal nonunit
macro cost in this class is exactly

\[
C(a,d)=1+L(a,d)+1+1=L(a,d)+3.
\]

The three charged instructions outside the graph are initialization,
target accumulation and final clearing. Source additions and subtractions,
doublings, halvings and negations each cost one, even if a particular
implementation could combine them. Complex streams execute the same real
coefficient circuit on their real and imaginary components, so their
charged cost is twice the real-component cost.

## 3. Independently checkable optimality certificate

Breadth-first search with unit edge weights finds a shortest witness. The
independent checker does not import that search. It enumerates every vertex
and successor, computes a potential by synchronous Bellman relaxation from
both goals, and checks the following conditions over the entire graph:

* `h(v)` is a nonnegative integer and is zero exactly on `G`.
* Every directed edge `v -> w` satisfies `h(v) <= 1 + h(w)`.
* Every nongoal has a successor with `h(w) = h(v)-1`.

For any walk `v_0,...,v_l` ending at a goal, telescoping the edge inequality
gives `h(v_0) <= l`. Following decreasing successors gives a walk of
exactly `h(v_0)` edges to a zero-potential goal. Thus these checks establish
the exact distance at every vertex, including `v_0=d`. Replaying the
submitted instruction sequence separately checks that it attains that
distance with its claimed terminal sign. Duplicate operations leading to
the same successor and self-loops do not change a unit-cost shortest path.

Coverage requires the coefficient census as well as graph checks. Extract
the reduced absolute coefficients from **both** frozen JP8 orientations,
filter by `a <= 127` and `d <= 16`, and compare that set to the certificate
entries. There are 50 absolute coefficients including the special unit,
100 signed coefficients in their union, and 90 signed coefficients in each
orientation. The filtered occurrence counts are 21,566 forward and 21,574
backward, out of 22,211 and 22,219 additions respectively. A seed may order
this finite corpus; it cannot replace complete coverage.

## 4. Endpoint substitution and exact arithmetic cost

After initialization, the invariant `W=cS` follows directly from the five
instruction rules. The chosen signed accumulation gives the required
target value; the source is unchanged and the final clear erases any work.
The initialization overwrites arbitrary incoming private dirt. This is a
three-register linear identity, so checking independent formal input
columns proves it for all real inputs, including correlated inputs. Applying
the identity to both components proves it for complex inputs as well.

Replace a scalar macro only by a word with the same complete boundary map.
Induction over the unchanged event stream preserves every later macro's
inputs and the complete scalar endpoint. Reuse of the existing scratch is
valid because every replacement clears it at the boundary. Frames, child
calls, adapters and paid-event inventories are untouched by this local
substitution; their inherited physical interpretation is a separate matter.

The reference original binary-Horner cost per real component is

\[
B(a,d)=3+\lfloor\log_2 a\rfloor+\operatorname{popcount}(a)+k.
\]

It pays one initial clear, the leading source addition, all binary shifts
and remaining source additions, `k` halvings, the signed target accumulation,
and the final clear. The accepted copy-based nonunit lowering costs
`B(a,d)-1`; the unit lowering costs two. Scale, copy and clear macros that
are not selected for replacement retain their existing costs.

For a selected replacement set `R` and orientation-specific occurrence
counts `N_o(q)`, the saving against the accepted copy-based baseline is

\[
2\sum_{q\in R}N_o(q)\left(C_{\rm copy}(q)-C_{\rm new}(q)\right).
\]

The factor two charges both real components. A saving against the best of
four Horner comparators is a different quantity; it must be computed with
that comparator's cost in place of `C_copy`. Comparing complete circuit
lengths, including initialization and clearing, avoids assigning a saving
to an uncharged source read. No unchanged child, adapter or wrapper cost
may be removed from a global invoice because a local coefficient is cheaper.

The seven selected absolute coefficients have the following positive
witnesses. `H` means halve and `A` means add the unchanged source. Each
displayed preparation starts immediately after the paid copy `W=S` and is
followed by the paid signed target update and final clear.

| `|q|` | Preparation | Complete new cost | Copy-binary cost | Occurrences in each orientation |
| --- | --- | ---: | ---: | ---: |
| `9/4` | `H H A A` | 7 | 9 | 2 |
| `5/2` | `H A A` | 6 | 7 | 25 |
| `11/4` | `H A H A A` | 8 | 10 | 1 |
| `13/4` | `H H A A A` | 8 | 10 | 1 |
| `7/2` | `H A A A` | 7 | 8 | 10 |
| `15/4` | `H A H A A A` | 9 | 11 | 4 |
| `17/4` | `H H A A A A` | 9 | 10 | 1 |

These are 44 macro occurrences per orientation, saving 52 primitives on
one real component and therefore 104 on both components against the
copy-binary baseline. Each new circuit is also one real-component
primitive shorter than the best of the four pinned PR837 Horner
comparators for that coefficient; the incremental saving against those
comparators at these occurrences is therefore 88 per orientation. That
second figure is a comparator calculation, not an assertion that the
complete PR837 implementation is composed into this package.

## 5. Exact instruction/source-read Pareto certificate

[pareto.py](pareto.py) audits a second coordinate on the **same 49 graphs**:
the number of instructions that read the unchanged macro source `S`.
During preparation, `add` and `subtract` contribute the cost pair `(1,1)`;
doubling, halving and negation contribute `(1,0)`. The paid initial copy
contributes one further source read. Target accumulation reads `W`, and
the final clear reads no `S`. Thus a preparation pair `(l,r)` has complete
macro pair `(l+3,r+1)`. All register operations remain charged by the first
coordinate; the second singles out occurrences of `S` as an operand. It
is not a measured memory-access count.

Operation identities matter for this audit. For example, at `m=d`, both
doubling and adding `S` reach `2d`, but their source-read increments are
zero and one respectively. The search and checker preserve these
differently priced parallel edges.

A pair dominates another pair when it is no larger in either coordinate
and strictly smaller in at least one. Each vertex stores an antichain of
nondominated preparation pairs and one operation-word witness per pair.
The search discards a candidate only when an existing label is no more
expensive in either coordinate. These state-local costs are additive, so
the same comparison holds after every common continuation. Removing a
cycle strictly decreases the instruction coordinate and cannot increase
source reads. Every nondominated pair therefore has a simple-path witness
of at most `|V|-1` instructions. This proves finiteness without a search
depth cutoff or a heuristic read budget.

The checker certifies the resulting antichains independently of the
search's integer successor table and pruning decisions. It requires:

1. Exactly the declared state set `[-ad,ad]`, and the initial label `(0,0)`
   at state `d`.
2. A rational-arithmetic replay of every stored witness from coefficient
   one, with the exact instruction/read counts, endpoint, magnitude bound
   and grid at every prefix.
3. Pairwise nondomination among labels at each state.
4. Local closure for every label and every admissible operation: extending
   a label at `v` must produce a pair dominated or equalled by a stored
   label at its successor. Successors are reconstructed with `Fraction`
   arithmetic, including differently priced operations to one successor.

To prove completeness, take any finite graph walk. The initial `(0,0)`
label covers its empty prefix. If a stored label covers a prefix cost,
monotonicity of addition and local closure give a stored label covering
the next prefix cost. Induction therefore shows that every attainable
pair is covered by a stored pair. Conversely, every stored pair is
attainable by its checked witness. The two sets have the same upward
closure; the checked antichains are consequently their exact Pareto
frontiers. Taking the union at both signed goals and removing dominated
pairs gives the complete endpoint frontier.

Across the corpus, this checks **3,703 vertices, 4,104 labels and 16,096
edge-label closure obligations**. [pareto.py](pareto.py) binds the coefficient
census and occurrence weights to the pinned JP8 payload, replays every
label witness, and returns canonical hashes of the complete label tables.
The receipt also compares each existing [CERTIFICATE.json](CERTIFICATE.json)
word with its frontier: all **submitted** shortest witnesses minimize
source reads among shortest words. This does not mean every shortest word
minimizes reads: for coefficient `2`, `double` and `add` are both one-step
preparations, with zero and one source reads.

Exactly the seven selected coefficients have two endpoint Pareto points;
the other 42 coefficients have one. Pairs below include all macro
instructions and the initial copy's source read, per real component:

| `|q|` | Submitted `(instructions, reads)` | Lower-read Pareto alternative |
| --- | --- | --- |
| `9/4` | `(7,3)` | `(9,2)` |
| `5/2` | `(6,3)` | `(7,2)` |
| `11/4` | `(8,4)` | `(10,3)` |
| `13/4` | `(8,4)` | `(10,3)` |
| `7/2` | `(7,4)` | `(8,3)` |
| `15/4` | `(9,5)` | `(11,3)` |
| `17/4` | `(9,5)` | `(10,2)` |

There is no third intermediate Pareto point. The alternative for `15/4`
prepares the integer coefficient along
`1 -> 2 -> 4 -> 8 -> 7 -> 14 -> 15`, then halves twice. Its complete pair
`(11,3)` dominates PR696's `(11,4)` in source reads at equal instruction
count. This is the bounded signed-Horner construction class credited to
**Chris Pagolu's PR734**, not a newly claimed coefficient construction.
The endpoint frontier and witness words are diagnostic evidence; the
emitted circuits remain the seven submitted shortest words in section 4.

For the 44 affected macro occurrences in either orientation, the source
audit independently counts actual frozen comparator words. The following
totals include both real components and use the pins in
[SOURCES.json](SOURCES.json):

| Lowering at the affected occurrences | Instructions | Source reads |
| --- | ---: | ---: |
| Original pre-PR696 binary Horner | 782 | 216 |
| PR696 / binary-forward comparator | 694 | 216 |
| NAF-forward comparator | 690 | 180 |
| Binary-reverse comparator | 678 | 216 |
| NAF-reverse comparator | 706 | 180 |
| Best of four, PR837's stable instruction-count tie order | 678 | 200 |
| Best of four, minimum reads among instruction-count ties | 678 | 180 |
| Submitted replacement words | 590 | 308 |

The best-of-four rows are coefficient-wise comparator selections, not the
execution of one fixed candidate family. These comparators remain
unrestricted by the search's magnitude/grid constraints, as in the original
instruction-count comparison. For example, NAF-forward for `7/2` has pair
`(8,2)` but reaches coefficient `8`, exceeding the allowed magnitude `7`.
It therefore does not contradict the bounded frontier `(7,4),(8,3)`.

All primitive operand occurrences are counted separately from reads of the
unchanged macro source. A clear reads zero operands, a copy or unary operation
reads one, and an addition/subtraction reads two. The complete submitted
replacement adds 92 additions and removes 196 doublings per orientation;
other primitive-tag counts stay unchanged. It therefore increases source
reads by 92 while reducing total operand reads by `2*92-196 = -12`:
`207138 -> 207126` forward and `207154 -> 207142` backward. These are syntactic
operand occurrences, not physical memory loads, cache traffic or runtime.

### Hypothetical source-read sensitivity

To expose the tradeoff algebraically, define a hypothetical cost

\[
\text{instructions}+p\,\text{source reads},\qquad p\ge0.
\]

Here `p` is an **additional** overhead on a source read that is already
paid as a primitive. No physical or runtime value of `p` is assumed or
inferred. For the fixed submitted schedule, the gain against PR696 is
`104 - 92p` per orientation, with algebraic break-even `p=26/23`.

Choosing the least hypothetical cost independently from each of the seven
frontiers gives exact switch points `1/3`, `1`, and `2`. The other macro
positions stay at their PR696 baseline. The resulting diagnostic deltas
per orientation, including both real components, are:

| Hypothetical extra read overhead | Instruction delta versus PR696 | Source-read delta versus PR696 |
| --- | ---: | ---: |
| `0 <= p < 1/3` | `-104` | `+92` |
| `1/3 < p < 1` | `-102` | `+86` |
| `1 < p < 2` | `-16` | `0` |
| `p > 2` | `0` | `-8` |

Adjacent choices tie at a switch point; intermediate mixtures of tied
choices are also optimal there. The switch points follow from each pair's
instruction difference divided by its read difference: `17/4` switches at
`1/3`; `5/2`, `7/2` and `15/4` at `1`; and `9/4`, `11/4` and `13/4` at `2`.
Because the objective is additive over these fixed occurrences, minimizing
each independently minimizes their summed hypothetical cost.

The zero aggregate read-delta row keeps the submitted words for `9/4`,
`11/4` and `13/4`, and uses the lower-read alternatives for the other four,
including the credited bounded-Horner `15/4` word. This describes a
certified possible schedule, not an implemented alternative or a physical
read-budget guarantee. Equal aggregate read counts do not establish equal
costs for different frames, source locations or access schedules. The
executable lowering and its 104-primitive saving per orientation remain
unchanged.

## 6. Magnitude bound inherited from original binary Horner

The original binary-Horner preparation explicitly reaches `W=aS` before
its terminal halvings. Every candidate preparation value obeys

\[
|W|=|cS|\le a|S|.
\]

The source is unchanged; the target stays at its incoming value until one
final update, after which it equals the original final target. The arbitrary
incoming work and the final zero also occur in the original trace. Therefore
the maximum absolute value over all registers and prefixes in a replacement
macro is no larger than in that macro's original binary-Horner trace, for
each input separately.

For symbolic source row `s`, the same argument gives
`norm_1(c*s) = |c| norm_1(s) <= a norm_1(s)`. Thus the inherited maximum-row
norm or nonnegative original-Horner envelope remains an upper bound under
successive substitutions. This does **not** assert that each replacement
row literally occurs in the original trace, or that all simultaneous
transfer matrices satisfy an entrywise order. New fractional coefficients
usually prevent literal prefix-trace containment.

The complete scalar replays additionally measure the exact maximum row-L1
norm over all 725 formal input columns at every primitive prefix. Initial
basis rows have norm one; after each primitive only the written row can
change the maximum. The Fraction interpreter sums absolute rational entries;
the independent integer interpreter sums absolute integer numerators and
compares dyadic values by cross multiplication. All historical, PR696 and
replacement traces agree at `503316465` forward and `1469388997/2` backward.
These finite values supplement the substitution proof; they do not interpret
physical frame or recursive operators, nor reduce the inherited 192-bit
allocation. Both observed global maxima lie in unchanged macros outside the
bounded coefficient search, so equality of these maxima alone would not prove
every changed macro satisfies its local bound.

## 7. What the fractional-grid constraint guarantees

Locally, if macro-entry `T`, `S` and `W` are on `2^-p Z`, every candidate
value is representable on `2^-(p+k) Z`, with an unbounded integer part.
The coefficient grid does not by itself fix `p`, total register width,
overflow behavior, rounding-error amplification, or the precision needed by
the physical compiler.

There is also a stronger **scalar-projection** comparison with the original
word. Replay scalar primitives as exact dyadic linear maps on the original
formal input columns, leaving physical frame operators outside this model.
Let `s_j` be a coefficient in the current source row. A candidate scratch
coefficient is `m*s_j/2^k`.

If `k>0`, reduction of `a/2^k` means `a` is odd. For nonzero `s_j`, the
2-adic valuation satisfies

\[
\nu_2(m s_j/2^k)\ge\nu_2(s_j)-k
 =\nu_2(a s_j/2^k).
\]

Consequently its reduced binary denominator exponent cannot exceed that
of the original terminal scratch coefficient `q*s_j`. A zero coefficient
has no denominator requirement. If `k=0`, every candidate multiplier is an
integer, so its denominator exponent cannot exceed that of `s_j`; the
original leading-source state `W=S` already attains that bound. These
arguments also cover source rows whose integer coefficients are all even;
it would be incorrect to assume that the clipped denominator depth always
increases by exactly `k`.

All remaining registers, the arbitrary incoming work and the target before
and after its single update have the same values as before. Hence each
replacement has no larger scalar-prefix denominator depth than its original
macro, and boundary induction extends this to the complete scalar
projection. This comparison is against the original/copy binary lowering;
it does not imply that the chosen word minimizes denominator depth among
all shortest words.

The conclusion does not evaluate frame/phase operators, normalization,
recursive children, tape interfaces or floating-point arithmetic. It is
not a full compiler precision certificate or a proof of the all-size
integer multiplication theorem. The distinction matters because a
coefficient on a depth-`k` local grid can be applied to a source already
carrying additional fractional depth from previous macros.

## 8. Adverse checks and review boundaries

Endpoint checks alone would miss several false claims. The implemented
controls exercise distinct failures with the recorded failure reason:

* Remove the initial copy while retaining arbitrary incoming work: the
  three-register endpoint must fail.
* Remove the final clear: private dirt must be
  detected even if the target endpoint is correct.
* Flip the target accumulation sign or the claimed terminal sign: the
  target identity must fail.
* Insert enough halving and inverse doubling to cross the allowed grid
  and restore the original endpoint: the grid check must fail.
* Insert a doubling excursion beyond `|c|<=a` followed by its inverse:
  the magnitude check must fail despite the correct endpoint.
* Insert two negations into a valid optimum: a legal equal-endpoint path
  must fail optimality or exact cost, not arithmetic correctness.
* Understate a potential entry: the full-graph optimality check must fail.
* Omit one corpus coefficient or change a pinned source payload: coverage
  or provenance must fail.
* Supply zero, a nondyadic coefficient or
  aliased source/target/work: domain or register-contract validation must
  reject it.

The Pareto checker adds four controls with specific rejection reasons:
removing a required lower-read label fails edge closure; understating a
label's source-read count fails witness replay; changing the declared
magnitude bound fails domain matching; and omitting the initial source
copy fails macro-boundary/source-read accounting. These checks distinguish
frontier completeness from endpoint correctness and detect an uncharged
source read even when a claimed preparation length looks plausible.

The reproducible verifier output and validation record identify the controls
actually executed. Independent implementation here
means a separate algorithm and interpreter, not independent human review
or formal verification of the full theorem.

## 9. Relation to the closest prior work

PR696 already supplies the copy/unit lowering and dirty-work contract.
PR734 supplies numerator-bounded signed-Horner circuits, a proof within its
restricted recurrence, and a Dijkstra crosscheck. Its crosscheck uses
positive integer states with transitions `c -> 2c+e`, `e` in `{-1,0,1}`,
cost `1+|e|`, and bounded doubled and final states; halving follows after
integer preparation. PR837 chooses among
forward/reverse binary and NAF Horner circuits. PR866 demonstrates why exact
endpoints and small magnitudes do not alone control fractional grids.

The incremental search class here permits arbitrary interleaving of paid
source additions/subtractions and shifts, while preserving both the
original magnitude envelope and coefficient grid. Its finite optimality
claim must be stated relative to this class and corpus. General shift/add
synthesis, bounded Horner optimization, copy initialization, and grid-guard
analysis are not claimed as new ideas. Savings already available from a
prior candidate family must not be presented as an additional improvement
over that family; the certificate should distinguish them from words that
strictly beat every named comparator.

No result here automatically transports to another supplier or to the
currently selected frontier. No new kappa, asymptotic complexity bound,
runtime speedup, physical admission certificate or production integration
is claimed.
