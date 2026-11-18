# Width-four complete projector actions

There are **386 simultaneous-conjugacy classes**, including **40
irreducible classes**, of complete binary rank-one idempotent pools at
ambient width four, actual off-pattern dimension three, unit-graph
matching number one and full joint image. This answers the width-four
part of the classification question in PR7749.

Read [the scope and proof](PROOF.md), [all classes and assignments](classification.json),
[the factor-pair census](census.py), [the separate matrix path](matrix_check.py),
[the replay entry point](verify.py), [source pins](SOURCE-PINS.json) and
[source credit](CREDITS.md). `classification.json` records a qualifying
pattern space, complete pool, conjugacy class, orbit size and all invariant
subspace counts for each class. Its assignments cover all 2,070 spaces
with the fixed unit E_01. Class labels have meaning only in this package.

The complete checks cover 698,027 quotient planes, all 120 rank-one
idempotents, every one of the 20,160 invertible binary matrices per class,
and all 67 subspaces per class. A second pattern-span enumeration gives
the same complete census. The unchanged source verifier also passes.

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/width-four-projector-classification
```

Both registered commands print:

```text
PASS_WIDTH_FOUR_PROJECTOR_CLASSIFICATION
698027 planes; 2070 anchored spaces; 386 action classes; 40 irreducible classes
120 projectors; 20160 direct matrix conjugacies per class; 67 invariant subspaces per class
Source classes: {"PR7707": "C384", "PR7749": "C347"}
```

No new kappa is claimed. Reducible width-four classes are not global
maximizers. Larger ambient embeddings, useful paid words, native movement,
restoration and the complete caller bill are outside this result. The
selected frontier and all five framework assumptions remain unchanged.

## Open next questions

- Which of the forty irreducible actions admit useful integral exponent
  relations and short paid words? Start with the explicit complete pools
  and count all roles before a word search. A formal identity alone does
  not establish a native supplier or a kappa gain.
- Which actions at larger ambient width have joint image four and the
  same pattern and matching dimensions? The present coordinate census
  does not settle this question. A structural compression theorem or a
  separately scoped embedding classification is required.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
