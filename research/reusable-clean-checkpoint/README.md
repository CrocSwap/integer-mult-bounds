# Reuse one clean checkpoint across weighted binary subtrees

**Recursive-interface research; no new kappa.** With four ordered leaf prices
`(1,3,1,1)` and two scratch arrays, a dirty root reuses the same clean connector
in both children. Its weighted signed-leaf bill is **16**, versus **20** for
the optimal clean-root-only binary tree at that same cap. Both execute twelve
leaf calls: the gain concerns unequal complete leaf prices, not fewer calls.
The two nonuniformly priced children are small fixtures, not measured PR628
supplier costs. For 54 unit-price factors and six arrays the optimum remains
**2112**, matching FanPUYen's PR714. No uniform improvement is asserted.
The changed word adds one internal dispatch. With a common internal dispatch
price g, the full local gain survives only for g<4 in the fixture's units;
the proof also gives the unequal-dispatch threshold. No runtime saving is claimed.

Run from the repository root, Python 3.10+ and standard library only:

```sh
python -I -O -B research/reusable-clean-checkpoint/verify.py
```

Expected final line:
`PASS_REUSABLE_CLEAN_CHECKPOINT 516 census cases; 1016 basis cases; weighted 20 -> 16; uniform54 2112; no new kappa`

The package contains an interval optimizer, a signed word emitter, an exact
reference interpreter, an independent decorated-tree census, complete frozen
trees, source hashes and [the proof and cost recurrence](PROOF.md).
The census covers every `{1,3}` price vector through six leaves and every
scratch cap 1 through n-1. All 109 admissible decorated trees through five
leaves receive full noncommutative 2D basis and nonlinear-restoration checks.
The two larger fixtures also receive complete 2D endpoint and inverse basis checks.
Eight controls detect wrong order/sign, omitted restoration, insufficient
scratch, nonzero clean input, aliases and invalid prices. This is finite
evidence supporting a written class-specific induction, not a formal theorem.

## Comparison and provenance

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Seed: **54**.
PR714 head: `efad8a40094ab453c0525efef0b0eff2a5d8b850`.
Its proof, notice and count implementation are retained unchanged under
`vendor/`, pinned by SHA-256 in SOURCES.json. This verifier freshly runs its
actual count function as an additional comparison. No predecessor dispatcher
or rounded numerical leaf is used by the new interpreter.

Credit FanPUYen's clean-root contract and proof, Chafik Boukhalfa / chafreaky's
PR628 leaves, 0xkilgore's PR663 restoration/count audit, androolloyd's PR673 echo
and integration obstruction, and concurrent PR730 (Sagar Thakrar), PR744 (Ali
Romman), PR758 (Koroffstrogov) for distinct all-dirty scheduling work. No
literature priority or superiority to the all-arity all-dirty class is claimed.
The stronger root-only comparator here even allows unbalanced dirty children;
PR714's original unit-price formula remains intact. Selected #626/#543 and
all its contributor lineage supply context, not this new implementation.

Prepared for **nightangelflowerwin-ops**, with substantial **OpenAI Codex**
assistance in mathematics, implementation, verification and writing.
Apache-2.0; original predecessor notice retained. No independent human review.

Clean-array supply, actual unequal leaf prices, common precision, routing,
physical hosting, all-size compilation and analytic transfer remain obligations.
No PR628 numerical leaf replay, complete supplier or multiplication theorem is
verified. `upstream/`, the selected result and existing generators are untouched.
