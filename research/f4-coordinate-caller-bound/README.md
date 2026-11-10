# Fixed-coordinate F4 decoder: all-p caller cost bound

The four coordinate queries on the classical 24-ray F4 set each need
binary rank at least five. With ambient rank h>=7, nonnegative net helper
cost, and the declared path-caller invoice, the optimistic margin is
negative at saving 0.00310045 for every pair count and every prefix split.
This is a scoped negative result. It gives no new kappa or selected result.

[Proof](PROOF.md), [exact witnesses](WITNESS.json), [receipt](EXPECTED.json),
[source pins](SOURCES.json), and [scope and overlap](TASK.json) define the
claim. The numerical saving is the historical October 26 comparison point.

Four five-cliques force four I5 submatrices for every allowed fitting
matrix, including nonsymmetric matrices. Monotonicity reduces ambient
rank to seven. Exact rational intervals check all 5,050 splits for
1<=p<=100. A separate histogram calculation checks the 100 balanced cases.
A negative tail value and derivative, with a written concavity argument,
cover every larger p. The greatest balanced upper margin is below -6.6777.

The model fixes the four coordinate factors and charges four separate
queries. It grants zero net helper cost and zero additional fees. A complete
implementation with more cost also fails this comparison. Different
factors, h<=6, shared query delivery, a negative net helper bill, or a changed
caller are outside the proof. No universal F4 or kappa ceiling follows.

## Reproduction

Python 3.12 or later and the standard library suffice. From the repository:

```sh
python3 -B scripts/research_package.py --package research/f4-coordinate-caller-bound
```

Both registered modes must print `PASS_F4_COORDINATE_ALL_P_BOUND`. The direct
verifier reads and authenticates the declared interval source before it
executes that source. It rejects six semantic or source changes. The dense
fitting-matrix fixture has query ranks 9,9,9,9; it is only a positive control,
not a minimum or the earlier cost-24 search witness. See
[validation](VALIDATION.md) for the exact checks and remaining limits.

The explicit `--write` option regenerates the expected receipt. Normal
verification does not write files. The registered commands do not use that
option. No solver or numerical optimization is part of this replay.

## Provenance and credit

This package publishes the scoped bound first recorded in the
[October 26 finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19202809).
The old local record used main de5ec2e7a6074068452f45b1a191b5c72832df4a.
This publication starts from main 7c49fe32c55de02c2c873655c804b16e4c3fef0a.
The [publication claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19364138)
limits the work to this existing result. The all-size proof is written
mathematics with exact finite corroboration. It has no independent human
or proof-kernel review.

DreamingOfClouds's [char2-threshold record](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/char2-threshold/README.md)
already reports an F4 cost-24 search across 150 bases. That record and the
classical root system are prior work. This package claims neither a new
root set nor a minimum over decoder bases. The elementary identity-minor
rank argument and concavity are classical.

The interval engine is zxv's unchanged
[higher-moment-strictification source](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/higher-moment-strictification/verify.py).
Credit Cinna Davis for the retained path-caller design and Jacob Alan
Sussman for productive mixed-target recursion. The formula used here is
stated in full in PROOF.md; no physical caller or predecessor scientific
suite is imported. All retained source notices remain unchanged.

New witnesses, declared-caller specialization, proof, and checks: Ali Romman
with substantial OpenAI Codex assistance. No subagents. Apache-2.0.

## Open next questions

Can changed factors, shared delivery, or a negative net helper bill fund
an actual caller? State that changed contract and price its whole signed
invoice before a wider search. Then check native maps, arbitrary inputs,
ownership, restoration, compiler, and outer costs. This package supplies
none of those changed constructions. The structured question is in TASK.json.
