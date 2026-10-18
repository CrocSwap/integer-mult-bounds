# Three-mode mixing retains COPY64 despite four span-loss exceptions

**Scoped negative result with a written proof and exact finite premises.**
In the P112 coordinate decoder, mix any three original coordinate terms and
one nonzero free rank-one correction by an arbitrary `GL(4,C)` factor change.
If both correction supports contain at least two indices, at least three of
the four replacement terms still have COPY rank eight or more. With the other
five coordinate terms unchanged, the sharp separate COPY sum is **64**. Its
separate power bill cannot improve for `0 < q <= 1`.

This answers the three-coordinate question in
[PR1473](https://github.com/CrocSwap/integer-mult-bounds/pull/1473).
That predecessor's stronger span-preservation lemma does **not** extend:
there are exactly four exceptions for the representative triple, each a
24-by-2 free rectangle. The proof below classifies these exceptions and shows
why they cannot lower the COPY bill. A naive reuse of the two-mode lemma would
miss the main new obligation.

The result does not cover singleton-sided corrections, four or more mixed
coordinate modes, multiple correction terms, or shared COPY billing. No
physical supplier, improved kappa, or full multiplication theorem is claimed.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p112-three-mode-seed40
```

Expected final marker:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/p112-three-mode-seed40 outcome=negative-result
```

The registered replay validates metadata and exact source pins, runs both
mathematical checkers, and exercises six external corruption tests. Default
checker runs only read files; `--write PATH` explicitly regenerates a receipt.
The primary checker also accepts `--check PATH`; the independent checker
accepts `--certificate PATH` and `--check PATH`.

- [verify.py](verify.py): 39 support strata, all 19,926 nonempty
  character-support cuts, 1,521 original pairing ranks, 156 exceptional
  pairing ranks, 56 explicit coordinate transports, six Gaussian-rational
  fixtures / 75,264 matrix entries, and eight controls.
- [independent_check.py](independent_check.py): direct Euclidean E8 roots,
  exact rational row-space flats, and set-based binary elimination. All
  6,216 two-anchor erasures / 242,424 span comparisons are checked, along with
  96 single-row restorations, 702,464 transported pairing entries, an integer
  compensation identity on 12,544 entries, and five controls. It imports
  neither the primary checker nor predecessor code.
- [CERTIFICATE.json](CERTIFICATE.json) and [INDEPENDENT.json](INDEPENDENT.json)
  hold the deterministic receipts. [VALIDATION.json](VALIDATION.json) records
  actual execution and its limits.

Both implementations have the same AI-assisted author. Their agreement is
code-disjoint finite evidence, not independent human review or proof-assistant
formalization of the quantified statement.

## Model and exact statement

Use the PR845/PR717 E8 model pinned in [SOURCES.json](SOURCES.json).
Enumerate the 120 doubled E8 root lines, choose the lexicographically larger
sign of each line, remove the eight frame lines
`f_(2j)=2e_(2j)+2e_(2j+1)` and `f_(2j+1)=2e_(2j)-2e_(2j+1)`, and sort the
remaining 112 lines. For these doubled roots define

```text
G_ij = (r_i dot r_j)/4,
X_ik = (r_i dot f_k)/4,
B_ij = (1 + G_ij) mod 2.
```

Then `XX^T=2G`, `rank_C(X)=8`, each X entry is 0 or +/-1, and B is a symmetric
binary matrix of rank nine. For index sets A,C, put
`rho(A,C)=rank_F2 B[A,C]`. The retained separate-total convention prices a
scalar term `d t^T` by `rho(supp(d),supp(t))`. Complex coefficients determine
supports; they are not reduced modulo two. Each coordinate term costs eight.

Let J be any three distinct coordinate indices and `Y=X[:,J]`. Take arbitrary
complex u,v with their **actual** supports U,V satisfying

```text
|U| >= 2, |V| >= 2, B[U,V]=0.
```

For any `M in GL(4,C)`, set `N=M^(-T)` and

```text
D=[Y,u] M,       T=[Y,v] N.
```

Ordinary transpose gives `DT^T=YY^T+uv^T`. Thus the four terms, together with
the other five coordinate terms, obey the masked decoder identity on every
constrained entry `B_ij=1`. All choices of complex amplitudes on U,V are
included. A support container with zeros is allowed only if the actual
supports still satisfy the displayed size conditions.

**Theorem.** If `r_j=rho(supp(D[:,j]),supp(T[:,j]))`, at least three r_j are
at least eight. Consequently

```text
40 + sum_(j=0)^3 r_j >= 64,
5*8^q + sum_(j=0)^3 r_j^q >= 8*8^q       (0 < q <= 1).
```

Identity mixing attains equality with ranks `(8,8,8,0)` for every admissible
u,v. If all four projected products defined below are active, the whole COPY
sum is at least 72. No claim of sharpness for that all-active subcase is made.

## All complex support patterns, without coefficient sampling

Seed 40 selects lexicographic coordinate triple number 40: `(2,4,5)`.
The 112 projected rows on these coordinates have 13 nonzero projective
directions: all `{0,+1,-1}^3` directions, modulo sign. For a nonzero complex
coefficient vector a, the directions annihilating a span a proper rational
flat of rank zero, one, or two. They are exactly the available directions in
that flat. Rational ranks remain unchanged over C.

There are one rank-zero, 13 rank-one, and 25 rank-two flats: **39 supports**.
For rank two, the primary checker enumerates cross products of every pair of
independent directions. For rank one it constructs a vector annihilating that
direction and no other; it also constructs a generic vector annihilating
none. These representatives certify support patterns, not a bounded search
over possible complex coefficients. The second checker independently closes
proper row spaces by rational RREF, starting from the zero space. It obtains
the same 39 supports without using cross products or importing their producer.

Three supports, the coordinate supports, have binary row-span dimension eight;
the other 36 have dimension nine. The 39-by-39 unmodified pairing table has
every entry at least eight. The table is stored and recomputed exactly.

## The four exceptions to two-anchor span preservation

Write `N(b)={i:B_ib=0}` and let S be one of the 39 supports. Every linear
functional on the row space of B has evaluations on its rows in
`col(B)=row(B)`. Thus the complete 512-element row space supplies all binary
separating characters c. Examine the nonempty cuts
`E=S intersect supp(c)`. Counting character-support pairs, the census is:

| Common odd neighbors of E | Nonempty cuts |
|---:|---:|
| 0 | 15,210 |
| 1 | 4,712 |
| 2 | 4 |

Every exceptional cut has size 24 and equals `N(b) intersect N(c)` for its
two common odd neighbors. The original support has row-span dimension nine;
erasing that cut leaves dimension eight. In the specified sorted root order:

| Coefficients on (2,4,5) | Two anchors | Span before / after |
|---|---|---|
| (1,-1,-1) | (8,16) | 9 / 8 |
| (1,-1,1) | (9,17) | 9 / 8 |
| (1,1,-1) | (14,22) | 9 / 8 |
| (1,1,1) | (15,23) | 9 / 8 |

The certificate gives all four erased sets and their separating character.
Each exceptional survivor set pairs at rank **exactly eight with every one
of the 39 unmodified supports**.

Suppose `B[U,V]=0`, with both supports of size at least two, and erasing U
from S lowers its full binary row span. A separating character has a nonempty
cut E contained in U. Every member of V is a common odd neighbor of E.
The census therefore forces E to be an exceptional cut and V to be exactly
its two anchors. Then `U` is contained in their common odd neighborhood,
which equals E. Since E is already contained in U, **U=E and |V|=2**.
This classifies every possible span loss, including arbitrary smaller
erasures and complex amplitudes.

The independent checker reaches the same classification by a different finite
reduction. It tests the maximal deletion `N(b) intersect N(c)` for every
unordered anchor pair and every support:

| Span before / after | Support and anchor-pair cases |
|---|---:|
| 8 / 8 | 18,648 |
| 9 / 9 | 223,772 |
| 9 / 8 | 4 |

These 242,424 cases exhaust 39 times 6,216. For each exception, restoring
**any one** of its 24 erased rows restores dimension nine. Hence every proper
subset of that deletion preserves span. The four erased sets have exactly
their indicated two common odd neighbors. These checks independently justify
the arbitrary-U classification above, without relying on the character census.

## Paired support bound and the four-term cost argument

For any two strata S,T and admissible U,V,

```text
rho(S minus U, T minus V) >= 8.                       (1)
```

If both deletions preserve full row/column spans, restricting spanning rows
to the surviving columns, and then using the preserved column span, leaves
the original pairing rank unchanged. It is at least eight by the table.

If the left span drops, the classification forces U to be one exceptional
24-row cut and V its two anchors. A two-element V cannot be an exceptional
24-row erasure, so the right column span is preserved. Restriction to the
exceptional left survivor set therefore gives its certified pairing rank
eight. The symmetric case is identical. Both spans cannot drop at once,
because one drop forces the opposite erasure to have size two. This proves
(1) despite the failure of unconditional span preservation.

Write the j-th columns of M,N as `(a_j,c_j)` and `(b_j,d_j)`, with
`a_j,b_j in C^3`. The top-left block of `MN^T=I_4` gives

```text
sum_j a_j b_j^T = I_3.
```

At least three summands are nonzero rank-one products, because the right side
has rank three. Call these products active. For each active j, `Ya_j` and
`Yb_j` have supports S,T from the complete classification. Corrections can
cancel entries only on U,V, so the actual term supports contain
`S minus U` and `T minus V`. Matrix rank is monotone under enlarging index
sets. Equation (1) therefore gives `r_j>=8`. Remaining terms stay in the bill
with nonnegative cost. This proves the theorem and both cost inequalities.

The certificate supplies 56 explicit permutations of the eight frame
coordinates carrying `(2,4,5)` to every unordered triple. Both checkers verify
each signed root-line bijection and every binary pairing entry, as well as
complete triple coverage. Row signs do not change supports; the corresponding
sign changes to arbitrary u,v are allowed. Reordering the three modes is
absorbed into M. Thus the representative proof applies to all 56 triples
without assuming a group-classification theorem.

## Controls, optimistic budget, and limits

The literal exceptional cancellation has ranks `(8,8,8,6)` and whole COPY
sum 70. Omitting its compensation changes constrained entry `(4,9)`. This
illustrates why a span drop alone is not a saving. Other fixtures cover
nonreal rational coefficients, transposition, permutation, identity mixing,
and a 2-by-2 correction. The mathematical controls reject a wrong inverse
transpose, Hermitian substitution, singular mixing, a nonfree correction,
and an invalid coordinate transport. A one-anchor example lowers a coordinate
span from eight to seven; it marks a proof boundary and does not refute any
separate singleton COPY theorem.

Six external tests reject an omitted support stratum, omitted exception,
forged COPY63 claim, invalid transport, missing geometry pin, and changed
geometry bytes. They invoke the checkers with `-I -O -B`; explicit failures
remain active with assertions disabled.

The blocked objective is lowering the separate COPY charge while retaining
the other charges and normalization. For fixed width m and common remaining
bill C, the affected optimistic contribution satisfies

```text
C + sum_j (r_j/m)^q >= C + 3*(8/m)^q.
```

All four replacement terms are counted. Granting zero additional preparation,
source access, frame changes, helper work, restoration, hosting, and recursive
management still cannot improve this objective. No physical implementation or
complete supplier recurrence is asserted. Savings in other work, a different
normalization or a legal sharing convention could change the question.

The finite evidence supports the written quantified argument; it is not a
formal proof of the full multiplication theorem. All-size compilation,
common-label/mutable-source realization, physical frames/owners, whole-call
hosting, precision/tape, exact recovery, analytic transfer, and the retained
bit H1-H5 obligations are outside this result.

## Provenance, overlap, and credit

Exact base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
The selected record, its source manifest, actual construction and maintainer
review identify conditional `kappa=836330098538459/500000000000000000`,
with the complex primitive binding. The baseline source-binding check was run;
the selected cold replay is not needed for this additive research package and
is not claimed. Selected, frozen, and upstream inputs remain unchanged.

[CLAIM.json](CLAIM.json) records OS-random seed 40, three candidate tasks,
the local claim, exact scope, budget and stop rule. No pinned coordination
issue existed. The initial complete overlap snapshot covered 745 open PRs
and 174 discussions. [OVERLAP.json](OVERLAP.json) records the final refresh;
search coverage is not proof of novelty.

Direct predecessor: Hanson Sun / [PR1473](https://github.com/CrocSwap/integer-mult-bounds/pull/1473),
head `ea2f6bf0940580dfaeb393ec0786abc8f7bbb7b4`, poses the three-mode question
and proves the two-mode span lemma. The new proof cannot assume that lemma for
three modes: the four counterexamples above are real. PR1432 supplies earlier
boundary/coupled-factor work. PR1460 and Gareth Davidson / bitplane's PR1468
address two-mode arbitrary and singleton-sided corrections, respectively;
neither theorem is imported here.

Credit commdata2338 / PR1375, Cinna Davis / PR1373 and Arham Tahir / PR1331
for the preceding rectangle and compensation questions; Mihir Srivastava /
PR845 for the pinned geometry implementation used only by the primary
checker; DreamingOfClouds / PR717 and PR446/595 for the decoder and COPY
framework; themilkman216 / PR968 for the pairing-cost model; Joel Pulikkan /
GamingPuzzled / PR620 for the coordinate COPY64 construction; and woklerx /
PR1077 for the complex-coefficient orientation check. The nearby PR1325
sparse-lift result keeps fixed readers and concerns a different class.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex**
assistance in mathematics, both implementations, verification and writing.
New work is Apache-2.0; predecessor attribution and licenses are retained.

## Open next questions

- **Singleton-sided corrections with three modes.** A 24-row cut can coexist
  with more freedom on a singleton side, so the two-anchor classification does
  not settle this case. First classify one-anchor losses among these 39
  strata, then test the coupled four-term bill. The missing step is a bound
  on compensation, not a larger search inside the proved class.
- **Four coordinate modes with one correction.** This changes the projected
  coefficient rank and support arrangement. First enumerate its proper
  rational flats and identify which free erasures change pairings before
  trying `GL(5,C)` synthesis. The 39-stratum lemma and four-term rank argument
  do not transfer automatically; complete helper/physical costs remain open.

[TASK.json](TASK.json) gives the relevance, first step and blocker for each.
