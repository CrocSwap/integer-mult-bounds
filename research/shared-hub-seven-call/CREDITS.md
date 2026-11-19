# Sources and credit

Ali Romman (@aliromman) prepared this proof, checker and package with
substantial OpenAI Codex assistance. New material is Apache-2.0.
No independent human or formal proof-kernel acceptance is claimed.

Nick Petalas (@petalas) supplied the six-call theorem, unchanged checker
and seven-call question in [PR #7742](https://github.com/CrocSwap/integer-mult-bounds/pull/7742),
at the [exact proof](https://github.com/petalas/integer-mult-bounds/blob/9394615e9fd3a30b66e23d422da4945258d7923f/research/shared-hub-single-pass/README.md)
and [checker](https://github.com/petalas/integer-mult-bounds/blob/9394615e9fd3a30b66e23d422da4945258d7923f/research/shared-hub-single-pass/verify.py).
All five package files are retained byte-exact. The integer bit-encoded
Laurent engine here adapts that source method; the bivariate set engine
is separate.

Ali Romman supplied the shared-hub projector pool in
[PR #7707](https://github.com/CrocSwap/integer-mult-bounds/pull/7707),
[source proof](https://github.com/aliromman/integer-mult-bounds/blob/57e24923b609d2588b83321f530fa2a1e75ed364/research/edge-matching-even-attainment/PROOF.md),
and the four-relation theorem and cross-commutator lemma in
[PR #7711](https://github.com/CrocSwap/integer-mult-bounds/pull/7711),
[retained proof](https://github.com/aliromman/integer-mult-bounds/blob/ac185e4529a01156f7b574555b50827f8cb645bb/research/shared-hub-triple-word-obstruction/PROOF.md).
The displayed projector matrices are checked directly. The cross-commutator lemma is a dependency. The four-relation theorem is
related prior work; its complete predecessor suite is not rerun.

Jerry Jiaheng Chen (@CubeJerry) supplied the augmentation chronology method
in [PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782),
[source word proof](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/FIVE-CORE-WORD.md).
The source notices identify this credit. This package adds the complete first-nonzero-form case split and the
exact cuts for the repeated call with a higher augmentation order. It does not claim a new geometry theorem or physical realization.

`SOURCES.json` pins canonical main selection and task provenance.
`SOURCE-PINS.json` authenticates six retained source files. Source pins
are content references and do not assert unmerged ancestry.
