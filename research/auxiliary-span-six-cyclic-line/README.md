# The twelve cyclic-line exceptions reduce to the existing common-J lemma

**Scoped written reduction, with exact structural checks; no new κ.**

PR4119 left twelve cyclic off-diagonal lines open for eight rank-one calls,
frame span six, three invertible rational 3×3 data targets and one dirty
auxiliary. Each cyclic projector has a literal coordinate 3+1 triangular
split: its core is the 3×3 all-ones projector J, and its tail has at most
one direction. Coordinate calls preserve the split. The core word inherits
at most two rational frame relations, so **Ali Romman's existing common-J
lemma, PR468 README §5.1**, applies. The fourth diagonal block is a separate
coordinate sum. Together they bound the sum of all four target ranks by the
number of coordinate calls, hence by eight. Three invertible targets require
at least nine. The auxiliary endpoint remains an arbitrary diagonal monomial.

This closes PR4119 Open next question 2, **conditional on its retained
common-J written lemma as an inherited mathematical premise**. It is not an
independent proof audit of that lemma. It neither invokes nor reruns PR468's
full computer-assisted theorem, whose statement has an additional
lower-triangular target hypothesis. Our use of §5.1 has no such hypothesis.
See [PROOF.md](PROOF.md) for the exact implication and source boundary.

A general GL₄ normalization could destroy the diagonal target; this proof
uses only a coordinate permutation. It also avoids the unsupported premise
that both frame relations omit the coordinate calls. The surviving subset's
relation space injects into the original one by zero extension, even when
relations involve the removed singleton calls.

## Full obligation ledger and decision

| Obligation | Status |
|---|---|
| Twelve cyclic rank-one projectors and unique lift of each pattern | Proved structurally; two exact finite enumerations corroborate |
| Literal 3+1 block projection, both tail orientations | Proved over every coefficient ring; exact symbolic checks |
| At most two relations on the projected core subset | Proved by kernel injection |
| Common-J diagonal allocation | Inherited written lemma, PR468 §5.1; not independently reproved |
| Cyclic-line span-six exclusion | Follows from the above premises for arbitrary dirty inputs |
| Direct nine calls, three identity targets and restored helper | Exact formal positive control; not a span-six/cyclic realization |
| Flagless two-dimensional patterns; span-five families | Unknown here |
| Native legality, complete physical/precision/compiler costs, supplier transfer | Unknown here; no cost is silently set to zero |

Family decision: **narrow and finish** the explicit cyclic-line handoff.
There is no reason to enumerate a larger cyclic alphabet after this reduction.
The formal obstruction does not justify abandoning other register mechanisms
or announce a new selected frontier.

## Reproduce

Python 3.12, standard library only:

```sh
python3.12 -I -W error -B research/auxiliary-span-six-cyclic-line/verify.py
python3.12 -I -W error -O -B research/auxiliary-span-six-cyclic-line/verify.py
python3.12 -B scripts/research_package.py --package research/auxiliary-span-six-cyclic-line
```

The science check completes in well under one second on the local machine.
It imports no predecessor code. It compares outer-product and binary-matrix
enumerations of all 120 projectors; selects the 12 cyclic ones by graph
reachability; checks the four no-tail, four incoming-tail and four
outgoing-tail cases; checks 300 exact symbolic pair projections and twelve
ordered eight-call products; and corroborates the inherited lemma's final
U(b)DU(c) Laurent formula. An exact rational eight-frame fixture has two
relations meeting the removed singleton and a one-relation surviving core;
it checks the boundary that a disjoint-support shortcut would miss.

Five negative controls expose opposite-tail feedback, unequal internal
diagonals, a deleted direct call, unsafe reduction of address exponents
modulo two, and a noncoordinate conjugation that changes the target.
Full matrix equality tests arbitrary dirty initial columns. These checks do
not enumerate rational frames, classify all two-relation words, or replace
the inherited common-linear-divisor proof. [VALIDATION.md](VALIDATION.md)
records the executed publication checks and their limits.

## Sources and overlap

Base: `4c0a359d88f22f05189d51f48387750b801a45d4`, priority revision 7;
selected conditional κ remains 0.00302015. Exact original blobs/hashes are
in [SOURCES.json](SOURCES.json). Inputs remain unchanged.

- **unpaidmoon, PR4119**, head `ea20dfd71c24072888755e2d03d61278bd25f2db`,
  `research/auxiliary-span-six-flag/README.md`: classification and the open
  cyclic-line question. Its §5 flagged argument does not cover this branch.
- **Ali Romman, PR468**, head `07a78bf335b0b5039a1fecd7cd74a0fe1d1605ea`,
  `research/bit-three-register-lower-bound/README.md`, blob
  `25e41c370c101a33a6deb978de08b03ed7539b79`: exact §5.1 common-J premise.
- **waynenilsen, PR1882**: dirty-auxiliary setting and frame-span reduction;
  retained predecessor context, not an extra executable dependency here.
  Credit eumemic/PR288, huxint/PR203 and the full retained source lineage.

[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19141158)
answers [the original handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19056337).
Final scout coverage was 320 open PRs at 2026-10-23 07:41:25 UTC, 4,168
Discussion records at 07:42:18 UTC, and 6,760 local notes. The fresh parallel
Schur split-incidence claim uses binary idempotents for a different problem;
address-twist PR5003 and dirty-fanout PR5045 also have different alphabets and
endpoints. No exact same-task reservation was observed. Cached text coverage
does not cover arbitrary diffs or unpublished work and is not a novelty proof.

## Open next questions

1. **Does the flagless two-dimensional span-six branch also reduce to a
   source-bound lower-dimensional premise?** This is the other exception in
   PR4119. First keep its literal triple and coordinate projectors in the
   original basis, or transport target projectors together with every basis
   change. The blocker is that an arbitrary GL₄ orbit reduction does not keep
   the target coordinate-diagonal. No claim or census for that branch is made.
2. **Can the inherited common-J quadratic-divisor step receive an independent
   proof audit?** It is the nontrivial premise reused here. Start from PR468
   §5.1, retaining the torsion-free group algebra and saturated relation
   kernel through degree two. Finite terminal identities do not alone verify
   that reduction. Such an audit would strengthen confidence without a larger
   four-register word search.

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. New files
are Apache-2.0; original sources/notices remain intact. No independent human
or proof-assistant verification, selected admission or full multiplication
theorem is claimed.
