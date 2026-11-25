# QQ16 decoder consumer charge under the selected coverage law

## Question and scope

This is a narrow independent check of the consumer-price branch in open PR
[#3181](https://github.com/CrocSwap/integer-mult-bounds/pull/3181), head
`80fc72d14546088e9fce3c06dc12bc67270da0af`. The audited candidate is one
`CONSERVED-QQ16` `F0 + B_1_2` two-call pair followed by the pinned #2707
zero-retention decoder. The specific question is whether its rank-one decoder
children leave enough recursive budget to reach the selected kappa under the
unchanged `centre=64` coverage law.

The exact local F and B profiles come from
`research/joint-query/evidence/CONSERVED-QQ16.json`; the #2707 child count comes
from `research/qq16-line-normalized-decoder/RESULT.json`. Those source files,
the selected record, and the selected ceiling model are pinned in
[`SOURCES.json`](SOURCES.json). The PR #3181 README was retrieved at its exact
head. Its path, Git blob, and SHA256 are recorded in [`TARGET.json`](TARGET.json).
The fetched PR README is preserved as [compressed raw PR #3181 README](PR3181-README.md.gz).
Its bytes are checked against the exact Git blob and SHA256 recorded in
[`TARGET.json`](TARGET.json), so the numerical premise can be replayed offline.
The PR head itself remains an external source premise; the package does not
claim that this unmerged commit is in local Git history.

## Result

The source profiles are

```text
F0:    {1:2420, 2:418, 3:432, 4:142, 5:82}
B1_2:  {1:2436, 2:418, 3:432, 4:142, 5:82}
#2707: 336 rank-one children across the two-call pair
```

Their per-call average is `{1:2596, 2:418, 3:432, 4:142, 5:82}`. For the
most favorable test, I omit the PR #3181 profile's eight rank-eight children
and allow their 64 units of rank mass to move into rank-51 idle children. This
lowers the relaxed moment. The resulting local mass is 5,706 per call; the
unchanged coverage law gives 7,232 total units per call and 1,526 idle units.

At the exact selected saving
`a = kappa/(1-kappa) = 836330098538459/499163669901461541`, an independent
rational lower bound on the relaxed moment exceeds `100009/100000 = 1.00009`.
The proof uses a 32-term positive atanh expansion after range reduction for
each logarithm and a five-term positive exponential sum. Every operation in
the verifier is exact `Fraction` arithmetic. Since the relaxation is already
above one at the selected exponent, the cap for this fixed local profile and
coverage law is strictly below the selected kappa. The reported rank-eight
profile has an even larger lower bound.

This establishes a scoped recursive-price obstruction for the stated
two-call profile. It does not establish the exact root reported in #3181, a
physical consumer bill, storage/retention feasibility, a global barrier, or a
new kappa. Endpoint adapters, movement, owner placement, routing, cleanup, and
physical hosting are not charged. The `centre=0` alternative is a changed
coverage law and is outside this result.

## Reproduce

From the repository root:

```sh
python3 -B research/qq16-consumer-cap-audit/verify.py
python3 -B scripts/research_package.py --package research/qq16-consumer-cap-audit --check-only
python3.12 -B scripts/research_package.py --package research/qq16-consumer-cap-audit
```

The verifier checks the exact source hashes and Git blob IDs, reconstructs the
per-call profile, computes the favorable rank-51 relaxation, and checks
negative controls for an illegal rank-52 child and an uneven two-call split.
Expected verifier status:
`PASS_QQ16_CONSUMER_CAP_BELOW_SELECTED no_new_kappa`.

## Open next questions

Can a changed, globally valid coverage law remove the 64-per-call centre cost
while an actual F17 consumer accepts the decoder output in its produced frame?
This matters because the fixed centre-64 profile already misses the selected
threshold before physical costs. The first step is to pin a real downstream
caller, state its entry frames and owner lifetimes, then derive its coverage
identity and complete physical bill. The blocker is that the current evidence
does not bind such a caller; a centre-free local surrogate is not that proof.

## Credit and review status

Credit the #2697 `CONSERVED-QQ16` producer and its retained native lineage,
ywz65/#2707 for the zero-retention decoder, Nick Petalas/#2965 for the
completed-output transfer, and dcharb78 for the #3181 profile and cost screen.
This package adds a separate exact one-sided moment proof. No independent
human or formal-kernel review is claimed. New work is Apache-2.0.
