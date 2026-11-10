# What two-coordinate sharing would have to pay

This is an **optimistic recursive-invoice audit**, not a delivery mechanism.
[PR6083](https://github.com/CrocSwap/integer-mult-bounds/pull/6083) already leaves
multi-coordinate sharing outside its separate-delivery exclusion. This package
quantifies that acknowledged opening on the complete selected #6030 bill. It does
not refute PR6083 or establish a new kappa.

Fix its declared eighteen LOCAL invocations and retain every original target
and paid job. Allow at most four binary helper splits per LOCAL, including
splits of descendants. Each split replaces one rank-h target by ranks a and
h-a, with positive integer parts and h at most nine. Charge one additional
rank-one job **once in the whole assembly**, hypothetically delivering two new
eligible cut coordinates under PR6083's two-splits-per-coordinate contract.
The relaxation grants those two coordinates at each of the eighteen cuts;
the global charge does not prove that one job can supply or reuse them there.
The new coordinates, their delivery and the target splits are hypotheses, not
consequences of the source's capacity theorem.

For p=1-k, every allowed split earns at most
`delta9 = 4^p + 5^p - 9^p`. Four distinct rank-nine roots attain the
four-ticket relaxation; the source declares 385 such helpers per LOCAL.
[PROOF.md](PROOF.md) explains why descendant splits cannot improve it.
The verifier reconstructs the **entire** original signed profile before
applying this explicit delta. Its certified numerical conclusions are retained
in [RESULT.json](RESULT.json), with uniform-per-LOCAL and total-assembly ticket
counts distinguished.

At selected `k = 781451/250000000`, outward rational certificates give:

| Relaxed edit | Moment after one global rank-one job |
| --- | --- |
| Two splits per LOCAL, 36 total | between -0.306447319 and -0.306447318 |
| Three splits per LOCAL, 54 total | between 0.039416358 and 0.039416359 |
| Four splits per LOCAL, 72 total | between 0.385280036 and 0.385280037 |

The exact minimum total is **52** splits when the allocation may be uneven.
Three is the minimum **uniform per-LOCAL** count. Under the declared `2d`
contract with the same coordinate budget `d` at every cut, `d >= 2` is necessary.
This does not require two coordinates at every cut under an uneven allocation.
The
four-split optimum cannot pay a rank-two job (moment below -0.610391370) or
two rank-one jobs (below -0.614719963). Thus a delivery proposal demanding a
second positive-rank recursive call fails this relaxation before physical
implementation. Additional charges with this same recursive tariff must stay
strictly below the exact remaining allowance, rather than treating the rounded
decimal as an inclusive cap.

Any reported allowance is an additional **recursive raw-moment debit**, in
the same units as `r^(1-k)`. It is not a scalar, routing, storage, precision or
compiler budget. Even a positive raw moment cannot admit a supplier. In
particular, no paid-rank-to-delivered-dimension relation, native chart, cut,
lifetime, arbitrary-input/owned-field restoration contract or target
independence is supplied here. Those fields remain unknown in TASK.json.

## Evidence and reproduction

The new standard-library verifier authenticates the selected invoice and exact
retained predecessor prose before calculating. It uses rational outward bounds
for logarithms and exponentials, an explicit modified complete profile and
semantic failure controls. It does not import or run the predecessor checker,
source word, cut census, constructor or interpreter. The proof and source-aware
AI reviews are separate from the finite executable corroboration; human and
proof-kernel acceptance are not claimed.

```sh
python3.12 -B scripts/research_package.py --package research/coupled-cut-delivery-fee-budget
python3.12 -B scripts/check_research_commit.py --package research/coupled-cut-delivery-fee-budget
```

Both normal and optimized registered commands are bounded. SOURCES.json pins
the current-main catalogue/selected record, live #6030 invoice and #6083 prose.
The two prose copies are byte-identical to the canonical-main versions and
PR6083 head `74c353a2df322ffc0273d538450f6505b76c76e7`; their embedded
attribution and limitations remain intact.

## Open next questions

Can one actual native rank-one job deliver two newly eligible coordinates,
enable the credited independent splits, and restore every owned/dirty field
without another positive-rank recursive call? Start with one exact chart,
chronological cut and scalar-versus-tensor coordinate interpretation, then
price the complete transport/restoration word. No such implementation is
supplied by the inspected sources. A failed physical contract would stop this
route despite the optimistic invoice; a successful raw bill would still need
all compiler, precision, movement, stock and outer obligations.

## Credit and scope

Prepared for [ToikY](https://github.com/ToikY) with substantial source-aware
OpenAI Codex proposal, proof/verifier, overlap and review assistance. Related
roles saw source and provisional proposals; they are not blind independent
acceptance. Credit [zxv](https://github.com/zxv)'s #6064 capacity opportunity,
#6083 single-cut contract, complete-budget obstruction and shared-delivery
question; [DreamingOfClouds](https://github.com/DreamingOfClouds)'s #6030 word
and bill; [Ali Romman](https://github.com/aliromman)'s dyadic/P104 lineage;
[Matarener](https://github.com/Matarener)'s #5994 census (not replayed here);
[Nick Petalas](https://github.com/petalas)'s #6033 carrier pricing; and their
retained predecessors. Concavity, exchange arguments and rational series
enclosures are classical. Apache-2.0. The assigned helper-inventory card is
explicitly changed to this partial invoice audit. All five selected framework
assumptions and the selected frontier remain unchanged.

The inherited source word is by Pierre-Loic Doulcet (hexapode); the complete
caller/helper accounting, controller and productive-recursion lineage also
credit Ali Romman, Cinna Davis and Jacob Alan Sussman. No original word or
accounting theorem is claimed here. This partial result does not meet the
card's full productive/native inventory acceptance gate.
