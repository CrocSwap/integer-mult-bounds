# Vector-valued cocycle floors for formal register words

For any finite-dimensional representation R of a group G over a field F
and crossed homomorphism `c(gh)=c(g)+R(g)c(h)`, every formal rank-one
register word realizing T obeys

```text
number of calls with c(g)!=0 >= rank_F Delta_c(T).
```

Delta replaces each formal group-algebra entry with its c-weighted vector
column. A diagonal target forces one such call for every nonzero target
column, even with arbitrary finite restored dirty workspace and free
constant scalar mixing. [PROOF.md](PROOF.md) proves the statement and its
extension to every split normal p-subgroup via its Frattini quotient.
The complement can be nonabelian and have order divisible by p.

The new step is the rectangular block of the affine cocycle representation.
It removes the need for a scalar twisted functional in Sagar Thakrar's
[PR4032](https://github.com/CrocSwap/integer-mult-bounds/pull/4032), Open next
question 2. The existing A4 and SL2(F3) results are cited and credited;
their checkers and searches are not run. This is a scoped algebraic proof
with finite exact corroboration, with no new kappa or selected-frontier change.

For `G=Fp^d semidirect SL_d(Fp)`, d>=2, w nonzero translation targets have
exact formal paid-call minimum w at every finite dirty-workspace size.
Every abelian quotient kills all those translations, so ordinary group
abelianization sees no target defect. The general proof uses elementary
transvection commutators. The finite example is F3^2 semidirect SL2(F3),
whose complement is nonabelian and has order divisible by the characteristic.

## Reproduce

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/vector-cocycle-rank-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/vector-cocycle-rank-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/vector-cocycle-rank-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/vector-cocycle-rank-floor --check-source-history
```

Any installed CPython 3.12 may replace the interpreter path. The expected
markers are `PASS_VECTOR_COCYCLE_RANK_FLOOR` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The standalone check needs neither Git
nor a network. Its stdout receipt is generated from exact computations and
SHA256 hashes of all six package files. `--emit /absolute/new/file.json`
writes that receipt with exclusive creation and refuses an existing path.
No generated output is required or retained in this package.

The verifier enumerates the finite group's affine/cocycle identities, every
rank-one idempotent on one through three F3 roles and every group label.
It compares formal group-algebra products with their affine images for a
declared deterministic sample of words with interspersed invertible scalar
mixing on two through five roles. It
checks all nonzero translation-target lists of length at most three with
two restored dirty roles, using exact full formal endpoints. Two explicit
commutators establish the finite translation basis. Semantic controls cover
the ignored module action, invalid nilpotent and rank-two projectors,
zero-cocycle replacement, reversed order, an omitted target, and the
nonidentity kernel. This is not an exhaustive word census or a formal
proof of the quantified theorem.

Both local modes pass 46,656 group pairs, 28,080 call images, 252 prefixes
of 72 sampled words, and 584 sharp full formal target lists. The projector
counts on one, two and three roles are 1, 12 and 117. Thirty-five sampled
words have strict slack in the rank inequality; no characterization of all
strict cases is claimed. Each direct command takes about 2.4 seconds
locally, comfortably below its registered two-minute limit.

## Scope and credit

Canonical scientific base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8, selected PR6030. The selected binding control passed.
The task is a declared change from the formal-interface card to a written
formal-model lemma. It is a side result for the portfolio of changed
interfaces, without a claim to discharge a selected framework assumption.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360783).
Entry overlap checks included live open PRs, this account's recent PRs,
recent handoff comments, active Discussions, local reservations, main-tree
README searches and merged searches for radical rank, cocycles, Frattini
quotients and nonabelian complements. The cached helper reported complete
main-note inventory and remote pagination, with its own freshness times.
Arbitrary diffs, unpublished work and historical text outside those searches
remain outside coverage; this is not a literature novelty certificate.

Credit Sagar Thakrar / thakrarsagar PR4032 for the twisted radical-rank
method and its normal-subgroup extension question; Cinna Davis
PR2116/2047/2248/2085 for the formal register and first-order lineage;
Nick Petalas PR4898 for the earlier SL2(F3) instance; and their retained
register-model predecessors. [SOURCES.json](SOURCES.json) pins predecessor
texts as provenance, with no executable import or scientific replay of them.
Affine cocycle representations, Frattini quotients and matrix-rank
subadditivity are classical. No literature-wide priority is claimed.

Nick Petalas's PR6008 supplies the earlier full-operator representation
rank cut. This result extracts a common rectangular block, giving a
one-unit charge even when a full paid operator defect has larger rank.
Its main result is the general block invariant, rather than a counterpart
obtained by changing a group or target in the full-operator cut.

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

The gate is necessary rather than sufficient. It can miss nonidentity
elements in ker(c), including Frattini defects in the normal-subgroup
specialization. A nonsplit extension needs its own cocycle. Native maps,
scalar conversions, source access, ownership/erasure, physical restoration,
hosting, precision/tape, compiler closure and the complete signed supplier
and outer bills remain unproved here. No heavy native, Lean, Docker or
selected scientific cold replay is part of this claim.

## Open next questions

- Can several cocycle blocks give a strictly stronger joint weighted-call
  bound for one supplied alphabet and full endpoint? This could rule out
  words that pass each bound separately. First derive the linear call-count
  constraints for one explicit alphabet and give a feasible dual witness.
  Native prices and a promising physical endpoint are missing.
- Can a second-order representation detect a specified Frattini defect
  that this gate kills, without losing the one-call charge? This could
  separate central targets hidden from all first-order quotients. First
  state an exact block-product law and its per-call rank change. A
  suitable second-order invariant, rather than a larger census, is missing.

## Implementation bounds

The finite verifier uses fixed F3 arithmetic, group order 216, at most
seven roles, matrix dimension at most 21, words of length at most six,
and bounded Cartesian products. It has no recursion, dynamic code
generation, subprocesses or third-party imports. Functions are below
60 physical lines. Checks use explicit exceptions in normal and optimized
execution. Two exception-control callbacks have fixed visible targets.

Power-of-Ten deviation, rule 3: CPython allocates integers, tuples and
dictionaries during this one-shot computation. Fixed finite domains bound
live memory; no caller-supplied size or unbounded search is accepted. A
fixed-buffer implementation would be needed for literal allocation-free
operation. Warning-strict normal and optimized commands are the available
diagnostics; no proof-assistant or independent scientific acceptance is
claimed by their success.
