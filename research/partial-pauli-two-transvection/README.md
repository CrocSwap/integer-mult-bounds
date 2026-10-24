# Exact low-length completion of partial Pauli contracts

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with an exact finite certificate. No new kappa.

For an injective binary symplectic partial map h:U -> V, put D=(h-I)U,
r=dim D, and define its residual bilinear form by

    b((h-I)u,(h-I)v) = omega(u,(h-I)v).

The form is well defined even when h is specified only on U. Its rank and
alternating property give an exact decision at the two-transvection cutoff:

| Displacement data | Exact length or proved lower bound |
|---|---|
| r=0 | 0 |
| r=1, b nonzero | 1 |
| r=1, b=0 | 2 |
| r=2, b nonsingular and nonalternating | 2 |
| r=2, b nonsingular and alternating | 3 |
| r=2, b singular | at least 3 |
| r>2 | at least r |

The first four rows classify every partial contract admitting at most two
turns. The fifth row is a sharp boundary. The last two rows leave the longer
optimum open. [PROOF.md](PROOF.md) gives the dimension-uniform argument and
explicit attaining words. The rank-one zero-form case constructs two axes
by a linear system in the existing ambient space, without adjoining ancillas.

For compatible signed Hermitian-Pauli equations, the same lengths are exact
when arbitrary Pauli sign corrections are free and each quarter-turn costs
one unit. Every attaining unsigned word lifts to literal Gaussian-dyadic
Clifford turns, followed by one Pauli conjugation correcting the signs.
The global scalar phase remains free. This is a formal turn-count tariff,
separate from native Gaussian rank and the complete physical invoice.

## What this adds

[JoyboyBrian's PR5051](https://github.com/CrocSwap/integer-mult-bounds/pull/5051),
head `0960807a68ff46acbe6510c8867912ef2324ee71`, supplies the partial signed
compatibility contract and a general completion construction. It leaves
optimization open. This contribution adds the exact low-length test, attaining
words, and the three-turn alternating boundary. It does not replay or audit
that predecessor. Classical symplectic and residual-form theory is credited;
no literature-priority claim is made.

The criterion prevents two false simplifications. Displacement rank one can
require two turns. A nonsingular rank-two residual form can still require
three if it is alternating. A singular rank-two form cannot pass the two-turn
cutoff. The API returns `minimum=None` and a lower bound when no exact optimum
is supplied, so that rejection at this cutoff is never called nonexistence.

## Exact finite evidence

The standalone verifier independently constructs the complete literal
symplectic matrix corpus and complete transvection Cayley distances. For each
source subspace it groups full maps by their restricted images and takes the
minimum word length in that group. It compares the new criterion against every
such partial map, including all its returned attaining words.

| Binary symplectic dimension | Source subspaces | Partial label contracts |
|---|---:|---:|
| 0 | 1 | 1 |
| 2 | 5 | 16 |
| 4 | 67 | 10,096 |

There are 10,113 contracts in total. The verifier checks every independent
Hermitian sign choice for the contracts receiving a sharp attaining word,
giving 23,231 signed basis contracts. The signed checks enumerate all possible
final Pauli corrections and compare the linear-system solution with that
literal fiber. They do not enumerate arbitrary dependent signed lists.

Sixteen further fixed examples cover n=2 through n=9. Eleven malformed
contracts, an inconsistent linear system, and three mathematical boundary
fixtures exercise rejection and distinguish rank-only, nonsingularity-only
and unrestricted two-turn claims. Every check remains active under `-O`.
The receipt is generated on stdout and binds all seven package files by SHA256.
No receipt or replay output is hand-written or stored in the checkout.

## Reproduce

From the repository root, using the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error -X dev research/partial-pauli-two-transvection/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error -X dev -O research/partial-pauli-two-transvection/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/partial-pauli-two-transvection
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/partial-pauli-two-transvection --check-source-history
```

A different CPython 3.12 installation may replace the local interpreter path.
Expected scientific marker is `PASS_PARTIAL_PAULI_TWO_TRANSVECTION no_new_kappa`.
The last command requires the publication commit and full history. Registered
normal and optimized checks each have a 120-second limit. Direct verification
also works in a Git-free copy containing these seven files. The package runner
isolates import bytecode; direct calls assume the local source directory has
no stale bytecode imports.

The source-bound orientation required by the card passed with the current
`scripts/research_selected_baseline.py`; this authenticates selected metadata,
not the selected scientific construction. The `formal-interface-lemma` card
is explicitly changed to original algebraic successor work in TASK.json.
No selected scientific replay, Lean, Docker or historical suite is required
for or claimed by this result.

## Limits and implementation bounds

The proof covers arbitrary finite binary symplectic dimension and arbitrary U.
The executable API accepts n<=9 and a basis of at most 18 vectors; dependent
signed equations must first satisfy the cited compatibility contract. Exact
word minima are exhaustively corroborated only through n=2. The fixed n<=9
examples do not make a larger exhaustive-census claim.

All new code uses direct calls, structured loops and explicit failures, with
no recursion, subprocesses, network, solver, code generation or shared mutable
state. Functions remain below 60 physical lines. API validation rejects Boolean
integers, invalid dimensions, over-capacity bases, dependent bases and maps that
fail to preserve omega. Internal checks verify the nonzero axes and actual
source-to-target action of every returned word.

Power of Ten rule 3 deviation: CPython allocates integers, tuples and sets while
executing. The API's largest span has at most 2^18 entries. The exhaustive
checker is restricted to n<=2, at most 65,536 candidate matrices and a six-round
Cayley search, at most 720 accepted matrices and 67 source subspaces. It retains
one subspace's at most 720 restrictions, one attaining word and small counters.
Each receipt read is limited to seven fixed files of at most 1 MiB. These
finite capacities bound live state; a fixed-buffer implementation is required
before using this code in a runtime that prohibits allocation. Warning-strict
normal and optimized replays provide the available interpreter diagnostics;
no external linter or type-checker run is claimed.

Native paid rank, arbitrary absolute-phase targets, a profitable physical
caller, owner endpoints, routing, dirty restoration, precision, storage, stock,
compiler and outer admission remain open. The selected frontier is unchanged.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. What is the exact minimum when the rank-two residual form is singular?
   Start with fixed source spaces for zero and rank-one residual forms. The
   blocker is the least larger ambient displacement space admitting a completion,
   rather than another two-turn enumeration.
2. Can one actual partial signed source contract use this test to reduce its
   complete physical bill? First fix its caller, phase anchor and dirty-owner
   contract, then price native Gaussian rank and every retained obligation.
   Shorter turn length alone does not remove a paid recursive call.

## Credit and related work

JoyboyBrian's #5051 supplies the immediate signed-contract question. David
Ganz / Dugongue's #4841 supplies native Clifford compilation context. Cao
Yifan / intqwq #4610, Cinna Davis, zxv, Jacob Alan Sussman and the retained
native/owner/compiler lineage retain their credit. None of their code is
copied, modified, imported or replayed here. Citation-only URLs and heads are
recorded separately from the two historical provenance pins in SOURCES.json.
No pending Git object is needed for a clean replay.

Nick Petalas's #4864 studies outputs of constrained simultaneous chart moves,
#4859 studies words between Lagrangian charts, and #4919 studies unrestricted
GL maps between subspace triples. Those are different objects from a prescribed
pointwise partial signed-Pauli map. This contribution targets the explicit
completion-cost gap in the other contributor's #5051, without extending those
recent packages or comparing their numerical counts.

The classical context includes Ronald Brown and Stephen P. Humphries,
[Orbits under symplectic transvections](https://groupoids.org.uk/pdffiles/brown-humphries1.pdf).
The cutoff proof is self-contained and uses no external theorem from that paper.
