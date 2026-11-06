# A sharp five-dimensional BIT core at three pattern dimensions

A three-dimensional binary off-diagonal pattern space containing exactly
two single edges has complete noncoordinate rank-one-idempotent joint image
of dimension at most **five**, at every ambient width. This is sharp even
for an irreducible pool. Its unique five-dimensional irreducible restriction
is conjugate to **{E11,E22,E33,E44,J5}**.

More generally, if P has dimension r, contains e single-edge patterns, and
E spans all their endpoints, the joint image has dimension at most
`dim E + 2^(r-e) - 1`. One-edge spaces at r=3 also have dimension at most
five; no attainment or irreducible classification is claimed for that
subclass. This answers an edge-containing slice of Nick Petalas's #5921
joint-image question, whose general cardinality estimate gives ten at r=3.
The formula also gives the universal bound `max(2^r-1,2r)`, hence seven
for all r=3 pools; attainment of seven is not claimed.

The explicit irreducible example refutes a four-dimensional-only **pool**
reduction. A further all-length word theorem shows that this five-dimensional
exception cannot save rank with at most three exponent relations: if all
five projector types occur, every bridge call lies in one consecutive
block whose total exponent is zero. Deleting that block preserves the
diagonal endpoint and leaves disjoint paid-frame sums. Otherwise the actual
word has joint image at most four. See [FIVE-CORE-WORD.md](FIVE-CORE-WORD.md).

Bridge deletion is asserted only for the restricted five-dimensional word,
not as a spectator-preserving edit of the ambient program; the ambient
rank conclusion uses target-monomial multiplicity matching.

The remaining four-dimensional and one-/zero-edge cases are open. This is
not a complete three-relation no-saving theorem, supplier, or new kappa.

The new quotient observation says two projectors whose patterns differ only
on a coordinate block cannot have independent image classes outside it
unless they are the two lifts of another single edge. Apply this to each
coset of the edge span. Three-edge spaces have coordinate graph components
of size at most four, while total image can be six.

[PROOF.md](PROOF.md) gives the theorem. The sharp pool's (image,covector)
bit masks are `(1,3),(3,2),(4,12),(12,8),(26,21)`, retained in
[WITNESS.json](WITNESS.json). These are scalar projectors, not physical calls.

## Evidence and replay

From the repository root, using Python 3.12 and its standard library:

```sh
python3 -I -W error -B research/bit-three-relation-core/verify.py
python3 -I -O -W error -B research/bit-three-relation-core/verify.py
python3 -B scripts/research_package.py --package research/bit-three-relation-core
```

Expected marker: `PASS_THREE_RELATION_TWO_EDGE_CORE`. A standalone copy needs
only this package. Optional `--output /absolute/receipt.json` writes a receipt;
ordinary runs do not modify the package.

The primary reconstructs the pool from all 496 width-five rank-one binary
idempotents, checks irreducibility by cyclic closure and all 372 proper
nonzero subspaces, and verifies the exact shear. Twenty bounded domains
cover all coordinate-permutation types of two directed edges at widths
four through seven. Separate pair checks exercise the quotient lemma and
its nonvacuous edge exception. These corroborate the written all-width proof. The separate bridge-word
checker verifies all 11,064 degree-two words with one occurrence of each
coordinate type and one through six bridge calls. A separately authored
full Laurent checker covers all 720 labeled six-call orders and a wrong-sign
control with the same linear kernel. The all-length conclusion uses the
written augmentation and chronology argument, not these bounded checks.

Controls reject omitted/nonidempotent/reducible bridges and false image
bounds. A width-seven coordinate-gate example tests the excluded hypothesis.
An exact six-call word with three relations has a diagonal endpoint and a
nonzero omitted-cleanup error, but its bridge calls cancel: it is a scope
control, **not a saving**.

Separately assigned agents reconstructed finite evidence without importing
the primary or predecessor code and reviewed the written proof. Their
checkers and reports are included; REVIEW.md records scope. These are
OpenAI-assisted reviews, not human acceptance or proof-kernel verification.
The selected scientific cold replay and physical compiler were not run.

## Scope and provenance

The pure pool theorem and word reduction have separate hypotheses.
PROOF.md Section 7 supplies the cube-relation/free-coordinate split before
applying the result to a word. The normal-form shear can create **two
off-diagonal endpoint positions**: assuming a diagonal transformed endpoint
would be invalid. Zero-edge three-dimensional spaces only have the general
bound seven here. Uniqueness applies specifically to two edges.

Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Credit Nick Petalas/#5921
for the fiber theorem and joint-image question; David Govea/#720, Ali
Romman/#468 and woklerx/#1456/#1846 for the relation/pattern lineage;
eumemic/#288 for historical model attribution. #5921, #720, #1456 and #1846
are merged. #288 is closed unmerged. #6777 is open at
`e62a9d0d4143e11c190fcb4d81d83dc1662da782`; its exact proof is retained with
origin, hash and notices. Its two-relation theorem is inherited, not replayed.

Targeted overlap found #6618's distinct regular projector-triple invariant.
Historical four-register rational-frame floors, twisted feedback and
two-idempotent invariants have different hypotheses. The full Discussion
archive and all closed code diffs were not searched; no-hit results do not
prove novelty. A broader four-register census and failed hexagon experiment
were exploratory, not proof dependencies or new exclusions.

Prepared for **@CubeJerry**, with substantial OpenAI assistance in proof,
checking, writing and separately assigned review. Apache-2.0. SOURCES.json,
ORIGINS.json and TASK.json retain source and scope metadata.

## Open next questions

1. Can an at-most-four-dimensional core with three exponent relations yield
   total rational target rank above paid rank? First use the two-edge
   reduction and bridge-cancellation theorem to isolate a genuinely remaining
   scalar alphabet before searching words. The five-projector exception
   analyzed here is closed; no saving word is supplied.
2. What is the sharp bound for zero-edge three-dimensional spaces, and
   what are the irreducible five-dimensional one-edge cores? Start with
   one analytically specified coset configuration; the general quotient
   bound supplies neither missing classification.

TASK.json gives first steps and blockers. A positive formal word would still
need native realization, arbitrary-dirty restoration, a complete invoice,
stock/precision and outer admission before any multiplier improvement.
