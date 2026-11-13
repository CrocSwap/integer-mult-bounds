# Reduce two-coordinate A7+A1 shifts to one 44-vertex code

For every positive block length d and every pair of distinct A7 coordinates,
allow each row independently to cancel either coordinate. The exact minimum
separate-term COPY cost over this whole shift family is

```text
C_d = 64d + beta_d(H44),
7d <= beta_d(H44) <= 8d,
71d <= C_d <= 72d.
```

Here beta_d is minimum log2 message-range size for zero-error index coding
with d-bit inputs. H44 is one explicit graph, independent of the coordinate
pair. It has twelve named vertices A_j,B_j and 32 odd subsets of six points.
[PROOF.md](PROOF.md) defines every edge and proves the reduction.

Claim type: scoped written reduction with exact finite geometric
certificates. The bounds 71d and 72d are not asserted sharp. There is no
below-72 code, unrestricted-shift theorem, physical supplier or new kappa.

## What is new

Matarener's [#5299](https://github.com/CrocSwap/integer-mult-bounds/pull/5299)
leaves the side-information floor for arbitrary complex row shifts open,
after certifying two sharp complete shift assignments. This result handles
arbitrary independent row choices in a specified two-coordinate family.
The protected cores, exact concatenation reduction and attaining row
assignment are new. It does not replay either predecessor witness.

Six mutable terms and the fixed A1 term each contain a protected induced
Petersen graph plus four isolated vertices, forcing 63d altogether.
Concatenating the two remaining messages codes their common 45-vertex
graph. An explicit row assignment attains this reduction. Removing its
isolated vertex leaves H44 and the fixed charge 64d. Coordinate symmetry
covers all 28 coordinate pairs.

Thus the question whether this entire shift family retains the 72d floor
is exactly the question whether beta_d(H44)=8d. A code for H44 below 8d
would give an equally explicit counterexample within the inherited
side-information model. The exact value is left open.

## Evidence and reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/a7-two-coordinate-code-reduction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/a7-two-coordinate-code-reduction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/a7-two-coordinate-code-reduction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/a7-two-coordinate-code-reduction --check-source-history
```

An equivalent CPython 3.12 installation may replace the local path. Direct
replay prints `PASS_A7_TWO_COORDINATE_CODE_REDUCTION` and a newly generated
receipt binding all seven package files by SHA256. `--emit` prints only
that receipt. There is no stored or handwritten receipt and no default
filesystem output. Both registered commands execute all checks, including
with optimization enabled.

The checker rebuilds the root geometry and verifies seven new protected
cores. It checks 1,440 local row-choice conditions, transports all seven
witnesses to each of 28 coordinate pairs, and checks all 946 unordered
H44 vertex pairs against its separate combinatorial definition. The graph
has 462 edges. A seven-vertex independent set proves the 7d lower bound,
and a checked rank-eight fitting encoder proves the 8d upper bound.
Together with the seven new completing term codes, literal decoding checks
22,012 outputs. Nine malformed or false-certificate controls reject.
These are enumerated finite checks, not a census of full shift assignments
or nonlinear codes. The written argument supplies the universal quantifiers.

## Scope, costs and sources

The base is canonical main e54523517d0f03e58352e647c403a5af3e525a57,
priority revision 8, selected #7000. Source-bound baseline orientation
passed; no selected scientific replay was run. The card
`complex-rank-shape-decoder` changes scope to an algebraic side result on
the nonlinear COPY contract. It supplies no complete paid/productive
supplier invoice and does not meet the card's physical construction gate.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19595294)
asked the broader all-shift question. The
[scope update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19595359)
records this two-coordinate reduction and leaves unrestricted shifts open.
Expansion stopped at this first checked result. Initial overlap coverage
included live open PRs, this account's recent PRs, recent handoffs, active
Discussions, canonical-main README searches and merged searches for the
object and its general form. The card cache covered 826 open PRs and
7,444 Discussion records but omitted 9,950 sparse local notes. Direct
canonical-main searches supplemented that cache. Unpublished work and
arbitrary historical diffs remain coverage limits, not novelty guarantees.

[SOURCES.json](SOURCES.json) pins predecessor READMEs as historical
mathematical provenance only. The verifier imports no predecessor
implementation or data, and does not run its scientific checks. Source
frame binding, width pricing and the orthogonal-side-information contract
are cited premises. The Petersen rate 5 is the classical published
[Fact 5.6(1) of Blasiak, Kleinberg and Lubetzky](https://www.cs.cornell.edu/~ablasiak/papers/bkl-beta.pdf).
The isolated-vertex and code-concatenation arguments are given in the proof.

Gathering, routing, native realization, frame changes, retained dirty state,
restoration, precision, tape movement, storage, compiler closure and the
outer caller remain unpriced. Unknown costs are not zero. No selected
assumption is discharged. The selected cold replay, Lean, Docker,
independent human proof review and formal proof-kernel acceptance are unrun.

## Open next questions

1. What is beta_d(H44)? Start with the explicit graph and its rank-eight
   fitting code. Either prove an 8d nonlinear lower bound or construct a
   shorter vector code. This exactly decides the 72d floor within the
   two-coordinate family; a binary minrank computation alone would not
   settle arbitrary nonlinear vector codes.
2. Can a three-coordinate cancellation family beat this obstruction?
   Start by deriving the protected intersections and the remaining joint
   demand interface. The present partition proof has exactly two parts
   and does not give a 71d or 72d bound outside its stated family.

The structured versions and blockers are in [TASK.json](TASK.json). No
follow-up is reserved, and no additional construction round is proposed.

## Related open work and credit

No open PR identified at intake studies the A7+A1 row-shift side-information
optimum or H44. The adjacent open #7169 studies a non-coordinate masked
completion on 93 lines, #7170 its coordinate family, #7168 Gram-class
costs through 24 deletions, and #7174 a 96-line block-realizability question.
Their linear or punctured contracts do not compute this nonlinear
unpunctured optimum. No shared numerical verdict is inferred. #5299 and
Nick Petalas #5958 are merged predecessors; #5958 concerns two A8 simplex
witnesses and is background only. This result builds directly on
Matarener's question and model, not that A8 package. Current P104
helper-split proposals concern a different quantity.

This contribution is produced by Nick Petalas. Credit Mark / Matarener
#5299 for the explicit open question, message model and demand-graph
reduction; Adam Gall / adamgall #2062's `a7-a1-decoder-floor` for the complete
row-shift normal form and frame binding; joaqcoo #1224 for the nine-normal
candidate; Philipp / mightyOil #1248 for the earlier support-deficiency
lineage; and Blasiak, Kleinberg and Lubetzky for the Petersen broadcast
rate. Retain DreamingOfClouds #717/#446/#595, themilkman216 #968,
woklerx #1077, and the #888/#785/#814 width-pricing and decoder lineage.
Classical coding and binary linear algebra retain their classical status.
Global literature priority is unclaimed. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

## Verifier constraints

Build the Lever keeps the new finite premises rerunnable. Prove It Works
checks actual decoded inputs as well as matrix ranks. All loops have fixed
domains of at most 120 roots, 120 binary columns, 28 coordinate pairs,
seven protected terms, or 64 subset labels. There is no recursion,
subprocess, dynamic code evaluation or external dependency. Functions fit
within sixty physical lines. Acceptance uses explicit exceptions under
normal and optimized execution. Python allocation is a bounded
managed-runtime deviation from allocation-free execution; allocator
internals are not inspected. Warning-strict registered runs provide the
recurring interpreter diagnostics. No external static analyzer is assumed.
