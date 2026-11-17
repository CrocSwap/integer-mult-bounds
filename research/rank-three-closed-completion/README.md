# Exact rank-three alternating completion criterion

Scoped written proof with exact finite corroboration, produced by Nick Petalas.

For a partial binary symplectic isometry h:U -> V, put d=h+I, K=ker d,
D=d(U), and b(d(u),d(v))=w(u,d(v)). Suppose dim D=3 and b is alternating
of rank two. Set R=rad b and U_R=d^-1(R). Then the exact unsigned
transvection minimum in the original ambient space is

    L(h) = 5 if U_R is contained in K+D, and 4 otherwise.

Every four-turn extension necessarily has independent, commuting axes.
The new [proof](PROOF.md) excludes four turns for every closed contract,
in every ambient dimension. It settles the r=3 portion of Open next
question 1 in Ali Romman's [#6525](https://github.com/CrocSwap/integer-mult-bounds/pull/6525).
That source already supplies the general interval [4,5], the escaping-lift
four-turn construction and one closed five-turn example. Those are credited
inputs, not new constructions or audit deliverables. No predecessor
scientific verifier or numerical receipt is replayed.

The proof uses the quadratic form of a hypothetical four-turn completion.
A totally singular hyperplane in a four-dimensional binary quadratic space
with nonzero polar form prevents its anisotropic vectors from spanning.
Four independent turn axes must span and each has quadratic value one.
Thus their displacement space is totally isotropic. The completion fixes
that entire image, which contradicts a nonzero closed radical lift.

## Exact finite evidence

[verify.py](verify.py) enumerates the new obstruction's finite coefficient
model, without rerunning the known five-turn fixture:

- All 1,024 four-dimensional binary quadratic forms and their 15 hyperplanes.
  There are 240 totally singular form/hyperplane pairs. All 210 with nonzero
  polar form have polar rank two and anisotropic span dimension three.
- All 64 ordered independent four-axis Gram topologies, each realized by a
  literal chronological word on an eight-dimensional symplectic space.
  All 16,384 input vectors pass displacement and inverse checks; 65,536
  Wall basis equalities agree with a separate triangular formula.
- All 960 topology/hyperplane restrictions. Exactly one canonical pair has
  alternating residual rank two. Its axes commute and all 16 radical lifts
  escape K+D. This counts coefficient-model pairs, not all partial isometries.
- The 180 nonalternating rank-two restrictions with closed left-radical lifts
  show that alternation is essential. All 256 single-turn omissions damage
  their whole endpoints. A changed Wall diagonal and zero axis reject for
  their specific intended reasons.

[RESULT.json](RESULT.json) is generated from these enumerations and binds
six package sources by SHA256. Default replay recomputes and compares it.
The written proof supplies the arbitrary-dimension conclusion; finite checks
corroborate it. The credited upper bounds are mathematical premises, not
independently certified by this verifier.

## Reproduce

CPython 3.12 and its standard library suffice. From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/rank-three-closed-completion/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/rank-three-closed-completion/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rank-three-closed-completion
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rank-three-closed-completion --check-source-history
```

Both direct modes print `PASS_RANK_THREE_CLOSED_COMPLETION`. Each registered
command has a 120-second bound. The standalone verifier needs only this
package, without Git, network or predecessor executables. After a deliberate
source edit, `verify.py --write-report` regenerates the receipt only after
all enumerations and controls succeed.

Base e54523517d0f03e58352e647c403a5af3e525a57, priority revision 8,
selected #7000. The card's selected-binding orientation passed. Live overlap
and main searches checked the rank-three, closed, alternating and radical-lift
formulations and the general completion question. The overlap snapshot covered
558 open PRs, 7,223 Discussion records and all 10,178 tracked top-level package
notes at that base. Nested diffs and unpublished work remain outside that
coverage. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19542394).

## Limits and implementation bounds

Only the closed-case lower bound and commuting necessity are new. Exact
attainment uses #6525's cited upper bounds. The theorem is binary and fixes
displacement rank three. Prescribed fixed spectators belong in U. No ambient
enlargement, signed Gaussian realization, physical costs, owner cleanup,
precision, stock, tape, compiler closure or outer admission is supplied.
The five selected assumptions remain. No new kappa or selected-frontier
change is claimed. Lean, Docker and the selected cold replay are not run.
Independent human and formal proof-kernel review are unclaimed.

There is no recursion or unbounded search. The largest outer census has
1,024 forms; words have four axes, coefficient spaces have 16 elements,
literal spaces have 256 elements and all nested loops have those fixed
bounds. Functions fit within 60 lines. Explicit exceptions remain active
under optimized Python. Managed Python allocations are a documented deviation
from fixed-allocation execution; live collections have the bounds above.
Warning-strict normal and optimized execution and source compilation provide
diagnostics. No static type checker is a declared dependency. Explicit
`--write-report` is the verifier's only mutation.

## Open next questions

1. Classify the alternating closed case at displacement rank four and above.
   The quadratic obstruction here no longer applies directly; #6525 already
   gives a closed r=4 contract attaining six turns. Start with minimal Wall
   extensions containing a totally singular subspace of codimension two,
   retaining the prescribed radical-lift action. A complete criterion and
   constructive attaining words are missing.
2. Bind a qualifying partial contract to an actual signed native contact.
   State its source, fixed spectators and phase anchor, then price every
   turn, sign correction and physical operation. A short unsigned word alone
   gives no recursive supplier improvement.

## Credit

The new lower-bound proof and verifier were produced by Nick Petalas.
Ali Romman #6525 supplies the question, interval, escaping construction and
known fixtures. Krzysztof Wojt #5097 supplies the general lower bound and
zero-form completion; Nick Petalas #5085/#6494 supplies earlier residual-form
and rank-one work; Brian / JoyboyBrian #5051 supplies signed partial-contract
compatibility. Credit also David Ganz / Dugongue #4841, Cao Yifan / intqwq,
Cinna Davis, zxv, Jacob Alan Sussman and the native/compiler lineage retained
by those sources. Wall forms and binary quadratic forms are classical;
no literature-priority claim is made. New work is Apache-2.0.
