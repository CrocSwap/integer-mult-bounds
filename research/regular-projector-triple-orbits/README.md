# Exact orbits of regular fully coupled projector triples

This contribution was produced by Nick Petalas. Apache-2.0.

For an ordered rank-one idempotent triple P1,P2,P3 over any field, put
S=P1+P2+P3. Assume rank(S)=rank(S^2)=3 and all three pair traces are nonzero.
Then the ambient dimension and

    p=tr(P1P2), q=tr(P1P3), r=tr(P2P3), u=tr(P1P2P3)

are a complete invariant under simultaneous GL conjugacy. The admissible
quadruples are exactly the nonzero p,q,r,u with

    1-p-q-r+u+pqr/u != 0.

Over every finite field of order Q there are exactly

    Q^4-5Q^3+9Q^2-9Q+6

such classes, in every fixed ambient dimension n>=3. [PROOF.md](PROOF.md)
gives the all-field proof, explicit representative and centralizer. Two
triples over F5 give different classes with identical
pair traces. Thus a descriptor retaining only the three pair traces loses
information even in this regular class.

Claim type: scoped written algebraic proof with exact finite corroboration.
The new result is the triple normal form and closed class count. It does not
claim global literature priority for rank-one factorizations, diagonal
similarity or cycle products, which are classical methods.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/regular-projector-triple-orbits/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/regular-projector-triple-orbits/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/regular-projector-triple-orbits
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/regular-projector-triple-orbits --check-source-history
```

Another machine can substitute its CPython 3.12 executable. Direct replay
also works from a Git-free export of the six package files. The verifier
writes nothing. It prints a generated receipt with the six file hashes and
`PASS_REGULAR_PROJECTOR_TRIPLE_ORBITS`.

The full six-entry Gram domains contain 1, 64, 729, 4,096 and 46,656 matrices
over F2,F3,F4,F5,F7. They give 0, 6, 50, 186 and 1,070 classes respectively.
Every accepted Gram is compared with its four-trace representative. A second
enumeration expands every representative's complete diagonal orbit, and the
two full sets must agree. Matrix multiplication checks the projector traces;
row reduction separately checks invertibility. F4 uses t^2+t+1.

For every ternary representative, all 11,232 GL3(F3) basis changes are checked,
giving 67,392 conjugated triples and 33,696 distinct endpoints. This agrees
with the proved scalar centralizer. Spectator dimensions zero, one and two,
ten domain rejection controls and an explicit F5 pair-trace ambiguity fixture
also pass. The universal quantifiers come from the proof, rather than an
extrapolation of these finite domains. No predecessor scientific checker is
imported or run.

## Scope, provenance and credit

This is an original state-classification side question, with a changed
`bit-new-register-model` scope recorded in [TASK.json](TASK.json). It concerns
full simultaneous conjugacy on a three-dimensional active direct summand.
The separately claimed width-two monomial/reversal quotient concerns
target-preserving word symmetries and a different equivalence relation.

Credit MatShep's [PR4762](https://github.com/CrocSwap/integer-mult-bounds/pull/4762),
head `3b4e0449262b0b1e07b80e009ef71cc0ca5bf816`, for the related two-idempotent
factor descriptor, and codyw912's
[PR4735](https://github.com/CrocSwap/integer-mult-bounds/pull/4735), head
`4afbea22e79e19d1d65702eb4090d454ee39d967`, for its inclusion/observation
framework. Those results are context, not proof premises or audit targets.
The proof here derives the three-factor reduction directly. Credit the
eumemic/woklerx scalar-projector register lineage and the retained native,
frame, helper, compiler and outer contributors for the application context.
No predecessor files or credit lines are changed.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. [SOURCES.json](SOURCES.json) pins task provenance. There are
no external scientific runtime inputs. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19373460)
records the scope. Live claims, local reservations, recent account work,
main README searches and all-state general/formula PR searches were checked.
The broader cache covered 556 open PRs and 6,605 Discussion records with
complete remote pagination; sparse local coverage was 137 of 8,917 notes.
Arbitrary historical diffs and unpublished work remain limits.

Singular active systems and zero pair traces are excluded. Projector order,
field and ambient dimension are retained. Transpose, reversal, field
automorphisms and projector permutations are not part of this equivalence.
This is not a complete word-state invariant. A search must still restrict
conjugations to its target stabilizer and preserve all other state. Physical
basis changes, native maps, input access, arbitrary dirty restoration,
precision/tape/stock, compiler closure and a complete paid/target invoice
are unpriced. No supplier, paid-call saving, kappa or selected-frontier change
is claimed. All five selected framework assumptions remain.

No selected scientific cold replay, Lean, Docker, independent human review
or formal proof-kernel verification is claimed.

## Open next questions

- Classify a singular or partially uncoupled triple. Begin with one fixed
  singular Gram and retain its factor kernel and observation image. The
  regular direct-sum reduction used here is unavailable there.
- Bind this descriptor to one target-preserving search and charge every
  basis change. Begin with an explicit alphabet and target stabilizer.
  A concrete caller and its full paid invoice are still missing.

Structured first steps and blockers are in TASK.json. No construction
expansion follows from this algebraic count.

## Verifier constraints

All function bodies have fewer than 60 physical lines. There is no recursion,
network, subprocess, dynamic code execution or output-file creation. Public
matrix and field boundaries validate their finite domains. Internal calls
use those validated objects. Loop bounds are Q<=7, matrix dimension<=5,
six Gram entries, four trace parameters, and the 3^9 ternary basis candidates.
Mathematical guards are explicit exceptions and remain active under -O.

Power-of-ten rule 3 deviation: CPython allocates managed integers, tuples,
sets and dictionaries during checking. At most 46,656 raw Gram candidates,
38,520 accepted Grams per set, 1,312 class keys and 33,696 distinct ternary
endpoints are retained in fixed bounded phases. File reads are limited to
one MiB plus one byte for each of six fixed files. The normal and optimized
registered commands exercise these bounds. A fixed-allocation embedded
implementation would require a different runtime. Warning-strict execution
and source compilation are the available diagnostics; no separate static
linter or repository-wide build configuration is introduced.
