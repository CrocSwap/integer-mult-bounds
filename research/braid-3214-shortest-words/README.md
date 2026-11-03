# Shortest paid words for the braid endpoint 3214

This package answers the first open question of unpaidmoon's
[PR6642](https://github.com/CrocSwap/integer-mult-bounds/pull/6642): which
shortest normalized words realize the plane endpoint [w], w=sts=tst=3214, in
the paid alphabet D_r(N)=I+([r]-I)N with r ∈ {s,t,u} and N a rank-one
projector on K^2. PR6642 proves the length is six and fixes the last two
peels. This package finds the words.

## Result

**Every field (scoped proof).** Sixteen explicit families of six-factor words
equal [w]: four with three free projectors (for example
`s(P) s(P') t(X) t(X') s(Y) s(Y')` and `s(P) t(X) t(X') s(Y) s(Y') t(P')`) and
twelve with two (for example `s(P) t(X) s(X) t(X') s(X') t(P')`), where
X'=I-X. The full table is in [PROOF.md](PROOF.md). The proof uses only two
field-independent identities: a line lemma for factors that share one
splitting, and conjugation of a factor by a pure permutation. Over F_q the
families contain 4n^3+12n^2 distinct words, n=q(q+1).

**F2 and F3 (finite certificate, exhaustive).** These families are every
six-factor word equal to [w]: 1296 words over F2 and 8640 over F3. Two
independent searches agree, a tight-peel depth-first search and an unpruned
meet-in-the-middle join, with exact operator equality on A⊗U. The u label
never occurs, and only two projector splittings occur in the two-parameter
families.

Over F2 and F3, every tight two-factor suffix allowed by the PR6642 peel
table extends to a shortest word: r(P') r(P) through the repeated-label
families, and r'(N) r(P) for every rank-one N through the families
`tsstts`/`sttsst`. The concern in PR6642 that a free second peel might not
extend does not occur over these fields. Over every field the same two
families already show that every free suffix extends, since P and Y are
independent there.

This is not an all-field completeness theorem. Completeness over infinite
fields and over fields not enumerated is open.

## Reproduce

From the repository root, with CPython 3.12 and the standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/braid-3214-shortest-words
python3.12 -B research/braid-3214-shortest-words/verify.py        # F2 and F3, about 11 s
python3.12 -B research/braid-3214-shortest-words/verify.py 5      # optional F5 census
```

The registered check prints `PASS_BRAID_3214_SHORTEST_WORDS`. The F5 run is
opt-in because its search is much longer; see the PR body for its local result.

## Scope and remaining obligations

The catalogue card is `formal-interface-lemma`; the scope change is recorded
in [TASK.json](TASK.json), following PR6642. Source pins are in
[SOURCES.json](SOURCES.json). Inherited and not replayed: spectator elimination
(Brian/JoyboyBrian PR4765), the six-factor lower bound and peel table
(unpaidmoon PR6642), the ordered-pair defect (Nick Petalas PR6449) and the st
classification (ToikY PR6550). No caller, tape, precision, stock or compiler
cost is priced. The selected conditional value stays 781451/250000000 and all
five framework assumptions remain. There is no new κ.

## Open next questions

The structured list is in [TASK.json](TASK.json).

* Are the sixteen families complete over every field? First step: derive the
  tight third-peel table symbolically after each second-peel branch of PR6642.
* Do other length-three rank-two endpoints have the same three building blocks
  (complement pairs, single-splitting blocks, conjugation)? First step: change
  the target constant in verify.py and rerun over F2 and F3.
* What does one two-splitting realization cost physically, compared with a
  three-splitting one? Blocked on a caller tariff.

## Credit

Produced by Nick Petalas. The question, the six-factor bound and the peel
table are unpaidmoon's PR6642. Predecessor geometry: ToikY PR6550,
Nick Petalas PR6449, Brian/JoyboyBrian PR4765, Ross Richardson PR1989 and Adam
Gall's cut lineage. New work is Apache-2.0.
