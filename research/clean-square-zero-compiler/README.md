# Clean scratch lowers the square-zero compilation minimum

For every nonzero square-zero binary coupling N of rank q, the exact paid
reflection-call minimum with returned clean workspace is **q+1**. One clean
role attains the new even-rank result; at rank two it uses three calls,
versus the exact dirty-workspace minimum four of Nick Petalas's PR4912.
Odd ranks retain his q+1 construction. The lower bound covers arbitrary
finite clean and restored dirty workspace and free binary scalar mixing.

The complete endpoint is checked coefficientwise in F2[C2], with one fixed
nonidentity involution g. A paid call has a binary rank-one idempotent
coupling. The clean role is initialized and returned to the zero address
function; using a dirty role in its place fails. [PROOF.md](PROOF.md) states
the uniform theorem and every boundary assumption.

This package also emits a literal coordinate-reflection/CNOT program,
including all inverse scalar work and common basis transport. At even q,
the new canonical word costs (q+1)R+2q(q+2)C+H, compared with
(q+2)R+(2q²-4)C for the explicitly lowered predecessor split compiler.
It wins precisely when R>4(q+1)C+H. In particular rank two is
3R+16C+H versus 4R+4C. R and C must be complete stationary primitive prices;
H is the additional clean-resource reservation/return charge. A saved formal
reflection does not establish a lower native total price.

## Reproduce and exact scope

Python 3.12 or newer, standard library only:

```sh
python3.12 -I -W error -B research/clean-square-zero-compiler/verify.py
python3.12 -I -O -W error -B research/clean-square-zero-compiler/verify.py
python3.12 -I -O -W error -B research/clean-square-zero-compiler/literal.py
python3.12 -B scripts/research_package.py --package research/clean-square-zero-compiler
```

`verify.py --write` regenerates only RESULT.json. Normal verification writes
nothing and compares the exact typed canonical scientific receipt. Every
proof-relevant live source is pinned in SOURCES.json and VERIFY.json. The
package does not import or execute predecessor code or re-run their census.

The scientific checks cover all square-zero binary matrices through four
data roles, conjugated ranks one through eight with extra dirty spectators,
all clean-column one/two-call obstructions for the first rank-one/two
fixtures, literal scalar counts through even rank sixteen, and invalid
matrix/zero-coupling boundaries. The uniform theorem is not inferred from
these finite domains. The separate `literal.py` interpreter checks 351 fixtures, every full faithful
input basis column, 160 dense dirty states, the two independent shortest
clean-column obstructions, all 44 single-reflection omissions, four dirty
ancilla failures and four noninvolutory-label failures. It executes literal
scalar CNOTs and address swaps, without multiplying formal projectors.
`controls.py` executes six actual CLI tests after relocation without Git: normal
and optimized read-only replay, live-source corruption, a Boolean scientific
receipt mutation, an incorrect reflection role, an omitted clean projector
and a missing scalar inverse. The wrong-role mutant intentionally passes the
primary algebra/count checker and is rejected by the literal oracle, showing
why the independently implemented endpoint check is necessary.

Only this isolated opt-in package changes. Frozen predecessors, selected
sources and selected κ=0.00302015 remain unchanged. Native reflection
implementation, clean-resource availability, nonstationary routing/frames,
physical tapes, scalar network optimality, recursive supplier admission,
Lean, Docker and the full selected cold replay are unrun and unclaimed.

## Overlap, sources and credit

The changed premise is precisely the clean-workspace case excluded by
[PR4912](https://github.com/CrocSwap/integer-mult-bounds/pull/4912), retained
head eaea286b055724895adb4ca949b5ac0495be5ff8. Its dirty minimum, odd-rank
construction and q-1 plus one even-rank split retain Nick Petalas's credit.
ywz65 PR2716 supplies the product identity and arbitrary-coupling motivation.
Adam Gall PR1911, eumemic PR288, Ali Romman PR468, woklerx PR1443, Gareth
Davidson PR1333, Arham Tahir PR1589 and Cinna Davis PR2290 retain their
register-model lineage credit. Matrix rank, square-zero normal form and
elementary conjugation are standard background; no literature-priority
claim is made for them.

At the initial fresh main bee95ce88f9f19802f0613f92838895cd0e14a1f checkpoint,
shared overlap searched 310 open PRs (06:05:59 UTC), 4096 Discussion records
(06:06:48 UTC) and all 6690 main package notes on 2026-10-23. The scoped
square-zero/clean query returned twelve related leads and no same minimum.
Live PR4912 head/body/comments and current handoffs were read. Cached text,
arbitrary diffs, omitted history and unpublished work remain limits; no
novelty guarantee follows. Later publication refresh is recorded in the PR.

JoyboyBrian, with substantial OpenAI Codex assistance in proof, compiler,
independent checks and packaging. Apache-2.0. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

1. Can a literal native caller supply one returned clean role at a complete
price H and satisfy R>4(q+1)C+H? Start at rank two and bind all four data
roles, zero template reservation and coordinate reflection to actual source
operations. A native supplier and complete physical invoice are blockers.
2. Can sharing adjacent scalar conjugators improve the matched comparison?
Start with the two explicit rank-two primitive streams and optimize both,
preserving every arbitrary data column and the clean return. No claim of
scalar-network optimality justifies assuming either side already minimal.
Structured questions are in TASK.json; no construction expansion is claimed.
