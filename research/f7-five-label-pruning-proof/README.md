# Five-label high-weight pruning has a structural soundness proof

**Scoped combinatorial proof with finite corroboration; no new kappa.**
For every simple restored universal singleton-prefix walk of length twelve
on F2^5, every label-basis functional of weight at least four has
separate-class pair-sum excess at most **15**. Thus the fixed L/2
substitution cannot falsely prune such a word.

This resolves the remaining (5,12) case of unpaidmoon's
[PR4148 Open next question 3](https://github.com/CrocSwap/integer-mult-bounds/pull/4148),
also handed off by Nick Petalas in
[PR4894](https://github.com/CrocSwap/integer-mult-bounds/pull/4894).
The new step is the quotient-cycle obstruction in the (8,4) split.
The earlier packages already measured soundness: that measurement is credited,
not presented as a new census result.

Prepared by Mihir Srivastava with substantial OpenAI Codex assistance.
Apache-2.0. No independent human or formal proof-kernel review is claimed.

## Definitions and theorem

Let q_0=0 and q_(i+1)=q_i XOR e_(w_i), for twelve labels w_i in {0,...,4}.
Restored means q_12=0 and every coordinate is used; simple means
q_0,...,q_11 are distinct. Write S for these twelve states.
Universal means S+S=F2^5. For a nonzero functional f, let A and B be its
two classes in S and define

```text
D(C) = {x XOR y : x,y in C, x != y}
X_f  = C(|A|,2) + C(|B|,2) - |D(A)| - |D(B)|.
base(5,12) = 2 C(6,2) - (2^4-1) = 15.
```

A difference present in both classes is counted once in each support.
Universality implies D(A) union D(B) = ker(f) minus {0}, of size 15.
The claim is X_f <= 15 for weight(f) in {4,5}. It concerns complete
universal walks, not arbitrary twelve-point sets.

## Proof

**1. Matching balance, credited to PR4894.**
If f has weight four, let v be its omitted coordinate vector.
Exactly the v-edges preserve f, and those cube edges form a matching.
Let s=|A| >= t=|B|, let a,b count preserving cycle edges in A,B,
and let c count crossing edges. Cycle degrees give

```text
2s = 2a+c,   2t = 2b+c,   s-t = a-b,
2a <= s,    2b <= t.
```

Hence s-t <= a <= s/2, so s <= 2t. Since s+t=12, the only
unordered splits are (6,6), (7,5), (8,4).
If f has weight five, every edge flips f and its split is (6,6).
This restates the predecessor lemma so the proof is self-contained.

**2. The (6,6) and (7,5) cases.**
At (6,6), the union of the two supports has size 15, so X_f <= 30-15=15.

At (7,5), the 35 ordered cross pairs (a,b) have their sums in one
16-element coset. Two distinct pairs therefore have the same sum.
They must differ in both entries, and their equality supplies a nonzero
difference in D(A) intersect D(B). Consequently the sum of support
sizes is at least 15+1=16, and X_f <= 21+10-16=15.

**3. Equality in matching balance fixes the (8,4) shape.**
Here a-b=4 and a<=4, forcing a=4, b=0 and c=8.
Every vertex of A is on one of four disjoint v-edges. Every vertex of B
has two crossing edges, so cyclic order consists of four blocks

```text
B vertex -- A vertex --v-- A vertex -- B vertex.
```

In particular A is invariant under translation by v.
Delete the v coordinate. The projection T of A has four distinct points
in a parity coset of F2^4, an affine three-dimensional space.
After a cube translation, take that parity coset to be even.

For any four distinct points, the six unordered pair sums are either
all distinct or have exactly three values. Equality between two pair
sums cannot share an endpoint, and is equivalent to XOR of all four
points being zero. In that case the points form an affine plane.
Thus |D(T)| is either 3 or 6, and lifting both v-levels gives

```text
D(A) = {v} union {both v-lifts of each element of D(T)},
|D(A)| = 1 + 2 |D(T)|.
```

If |D(T)|=3, then |D(A)|=7. Since four points B supply at most six
differences, their union has at most 13 elements. This contradicts
universality. Hence |D(T)|=6 and |D(A)|=13.

If B is not an affine plane, |D(B)|=6 and
X_f = C(8,2)+C(4,2)-13-6 = 15.
It remains to exclude an affine-plane B.

**4. A planar B contradicts the projected cycle.**
Suppose B is an affine plane, with three nonzero differences.
The two elements missing from D(A) in ker(f) minus {0} are a v-pair,
say z and z+v. Universality forces both into D(B). The three nonzero
differences of an affine plane are closed under addition, so its third
difference is v. Therefore B is also v-invariant.

Its projection consists of two distinct odd vertices u,w in F2^4, and
u+w is the unique nonzero even direction missing from D(T).
Each u and w has two lifts among the four B vertices.
In the cyclic sequence of these four projected B vertices, there are
at least two transitions between u and w: a closed cycle visiting both
values must enter and leave each value.

Each such transition passes through one of the four distinct projected
A vertices in T. That vertex is adjacent in the four-dimensional cube
to both u and w, since the two crossing edges toggle coordinates other
than v. Thus T contains at least two distinct common neighbors of u,w.

Two distinct vertices of a cube have common neighbors only when their
Hamming distance is two. Then there are exactly two common neighbors,
and their XOR equals u+w. Both would lie in T, implying u+w in D(T).
This contradicts the missing direction. Planar B is impossible.

All cases give X_f <= 15, proving soundness. The argument does not
assert that the upper bound 15 is attained by a universal walk.

## Exact corroboration and boundaries

The standalone verifier is written here without importing or executing
predecessor programs. It checks:

- All 3,695 first-occurrence canonical simple closed words of length twelve
  over at most five labels. Of these, 3,381 use all five labels and 828
  are universal. The other 314 closed words use four labels and cannot
  cover F2^5. This explains the distinction between the two closed counts.
- All six high-weight functionals on the 828 universal words:
  **4,968 cases**. Ordered-pair multiplicity and unordered-support
  calculations agree. Matching and degree identities are checked on
  all **22,170** closed-word/functional cases.
- All **127,400** v-invariant (8,4) set pairs for f=01111:
  70 projected majority subsets times 1,820 minority subsets.
  Translation and coordinate symmetry cover the other orientations.
  There are 13,664 universal sets. Of these, **224** have planar
  minorities: 32 have zero and 192 have one projected common neighbor,
  so none can realize the required two transitions.
- All **120** distinct vertex pairs in the four-dimensional cube check
  the common-neighbor count and XOR identity used in the obstruction.
- Ten invalid-input or lowered-cap rejections, the low-weight boundary
  below, the arbitrary-set boundary below, and two typed receipt mutations.

The word enumeration uses only first-occurrence relabeling, simplicity and
the forced closing singleton edge. Every labeled word has a canonical
representative; all six masks are checked, so relabeling loses no functional.
There is no universality/excess prune or rotation reduction.
The verifier rechecks restoration and prefix sets separately.

The measured maximum is **11 for each of the six masks**, consistent with
the predecessor soundness measurement. No universal (8,4) word occurs.
Those stronger observations remain finite evidence; the written theorem
proves the sufficient bound 15.

The universal word `012343234031` has excess 11 at mask 10111 and
excess **21 > 15** at mask 00001. Dropping the weight hypothesis is invalid.
Dropping the cycle hypothesis is also invalid: the set with classes

```text
A = {0,3,5,9,16,19,21,25}
B = {1,14,17,30},        f = 01111
```

is universal, but its excess is **18 > 15**. Its projected minority vertices
have no common neighbor. This is a control for the exact step that
distinguishes the new proof from a false unrestricted set theorem.

## Reproduction

Use CPython 3.12 and the standard library, from the repository root:

```sh
python -X utf8 -B scripts/research_package.py --package research/f7-five-label-pruning-proof
python -X utf8 -W error -I -B research/f7-five-label-pruning-proof/verify.py
python -X utf8 -W error -I -O -B research/f7-five-label-pruning-proof/verify.py
python -X utf8 -B scripts/check_research_commit.py --package research/f7-five-label-pruning-proof --check-source-history
```

Expected markers are `PASS_F7_FIVE_LABEL_PRUNING_PROOF`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The normal and optimized commands recompute the evidence and compare the
entire canonical JSON payload to generated RESULT.json, including hashes of
the five source files. `--emit-receipt` emits a freshly calculated receipt
to stdout for explicit authoring; normal replay writes no files.
The standalone verifier needs neither Git nor network access.

Checks ran locally on Windows with CPython 3.12.0. The small checks take
approximately one second each; this is not a performance improvement claim.
Enumeration uses a bounded iterative stack (depth eleven, at most five
extensions per node) and streams its domains. Python collections and
interpreter allocations are not instrumented. Explicit exceptions remain
active under -O. No Lean, Docker, seven-label census or selected cold replay
is required or claimed.

## Provenance, overlap and remaining scope

Canonical base is `624de9dc66858af0945e5f8a0942488d62280d43`, priority
revision 7. The `census-pruning-audit` card changes scope to this handoff's
missing structural implication. The current selected-source baseline
passed after materializing its sparse inputs. It is only source-binding
orientation. Selected kappa remains 60403/20000000.

Credit unpaidmoon for PR4148's question, double-transversal proof and
excess convention; Nick Petalas for PR4894's matching-balance lemma and
PR3699/PR3733's measured classification; Nicholas Stone for PR2973's
parity correction; James Reed for PR3096's boundary audit; and Ross
Richardson for PR943's singleton-prefix model. The later five-label
length census retains unpaidmoon's credit. Merged documents are pinned
as provenance in SOURCES.json. The pending PR4894 README is an external
cited document at head `2e95d12a8f1557a90102314a773c74420bcbd4fe`;
it is not a runtime input or an unmerged Git-history dependency.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4903)
records the handoff. Initial overlap coverage included 424 open PRs and
3,950 Discussion records with complete remote pagination. The sparse
initial scan covered only 5 of 6,319 local notes; relevant omitted f7
successors were subsequently read. Live PR4894 and recent handoffs were
checked. PR4871 concerns receipt-domain binding at length 22, and PR3899
concerns a partial union prune at (4,8); neither proves this statement.
The submission refresh covered 425 open PRs and 3,957 Discussion records,
with 51 of 6,319 local notes searched. No competing scoped proof was found.
Omitted notes, arbitrary diffs and unpublished work remain coverage limits.

This result adds no engine change, seven-label exclusion, supplier
admission, all-size multiplication theorem or new kappa. The hypothesis
is simple restored universal length-twelve words in dimension five.
The 224 rejected set configurations show why adjacency and chronology
cannot be removed from this particular argument.

## Open next questions

1. Can one prove the measured sharper cap 11 and the absence of universal
   (8,4) walks structurally? This would explain the remaining gap in the
   sufficient bound. Start by analyzing nonplanar four-point minorities
   in the same quotient cycle. The current proof permits excess 15 and
   does not exclude all such configurations.
2. Can the matching-balance constraint produce a useful partial-prefix
   prune in a maintained engine? First state the remaining-edge capacity
   contract and prove that it retains every universal completion.
   Correct completion bounds and a measured runtime benefit are absent;
   this package does not enable a new pruning rule.
