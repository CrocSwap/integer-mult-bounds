## Result

This closes one changing-source consumer boundary after #7154: its actual
encoded balanced-node iterator now feeds a paid whole-node result projection
and same-source commit, producing the complete forward balanced CRT
address-state endpoint without host node/width/precision/coordinate arguments.
The source-relative proof uses **79 stable owned roles**, O(p^4) complete
source-model time and K_source + O(p^2) historical backing. **No new kappa.**

The consumer stages the full framed source while the numerical result is
live, copies whole-node updated-coordinate fields, validates every high bit
beyond its destination width, retires the lease, and commits to the same
owned source. Preserved metadata reestablishes the encoded iterator invariant,
so the next node reads the actual newly committed coordinates.

## Novelty and predecessor work

#7154 supplies the physical numerical-node iterator and leaves its source
read-only. #7152 supplies the full source-state tree at compiled micro-row
geometry. #5053 already supplies whole-node updated coordinates; #5496
correctly discards those values when building a single micro-row. #5625
supplies the earlier retire-before-source-write principle. This contribution
is the exact uniform consumer join, heterogeneous-width projection, encoded
topology preservation lemma, and its complete occurrence/history budget.
It does not claim new CRT identities or generic disjoint-support commutation.

## Source pins and checks

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Runtime frontend #7154: `cc35ecedce6f208d5056fab6d17c58555affc73c`.
Endpoint-comparison #7152: `66adbede4bd4ab603ba3e0a7f6708403905b753c`.
All seven runtime inputs are unchanged byte-pinned exports inside this package;
direct replay requires no network or nonancestor Git object.

From `research/encoded-balanced-crt-endpoint`, Python 3.12:

```sh
python3.12 -I -W error -B verify.py
python3.12 -I -O -W error -B verify.py
```

Both executed modes print:

```text
PASS_ENCODED_BALANCED_CRT_ENDPOINT cases=45 nodes=75 owned_roles=79 controls=8
```

The family includes all 32 padded pairs for (3,5), twelve four-axis states,
and one eight-axis tree. Independent congruence enumeration checks each node;
a different global mixed-radix formula checks valid endpoints. The tests
authenticate source bytes and inspect all 79 role histories, source metadata,
nonblank old tails, stable backing identities, boundary heads and cleanup.
Eight negative controls exercise stale/wrong projection, overflow, lifecycle
ordering and erasure. Runtime geometry/decode functions are poisoned and
constructors sealed after fixed-role acquisition. Full evidence is in
PROOF.md, RESULT.json, INPUT-PINS.json, TASK.json and VERIFY.json.

A separate reviewer read the complete source chain and proof. Its own checker,
which does not invoke the author verifier, uses CRT idempotent sums and passes
18 cases / 46 nodes, including padded-invalid axes, mixed widths, changing
precision and hostile source tails; a stale-coordinate mutant is rejected.
Reproduce with `python3.12 -I -W error -B independent_check.py .`.
See REVIEW.md and INDEPENDENT-RESULT.json for the independent receipt.

## Limitations and open obligations

This is one address-state evaluator. It does not move a payload indexed by
all addresses, produce encoded micro-row/ROM selections, implement inverse
traversal or the complete three-epoch key, or lower the providers to a
bit-Turing-machine program. The source-operation theorem retains an
unspecified fixed finite-control refinement constant. Allocated backing and
visited positions are distinguished: the staging role retains M cells but
transiently visits index M, so a visited-span caller pays M+1. Predecessor
numerical/frontend contracts remain premises. Malformed-provider detection
does not establish arbitrary error rollback or dirty-memory allocation.

All five selected foundational assumptions remain conditional. The selected
complete bound remains at kappa 0.00363005817; this is an enabling lemma,
not supplier admission or an unconditional multiplication theorem.

## Credit

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit #7154/#7152; JoyboyBrian's #5053/#5219/#5505/#5496 numerical, entry,
owner and query work; Ali Romman's #5353/#5625 source/retirement work;
Cinna Davis's #4100 CRT/Beneš construction; Hiroki KUMAZAKI, ToikY,
commdata2338 and all unchanged source notices. Separate AI cross-review is
distinct from independent human or formal-kernel acceptance. Apache-2.0.
