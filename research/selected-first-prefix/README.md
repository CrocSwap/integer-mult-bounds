# Selected call-0 prefix with complete family access

I bind the selected first two scalar events to families119/169 and prove
their whole-family charts agree. I then factor those events out of the
cover loop and implement acquisition, scalar execution, replacement and
commit on encoded sequential tapes:

    F119 <- (-F119 + F169)/2; all other families unchanged.

The executor retains SCALE(-1/2) followed by ADD(+1/2), including their
intermediate arithmetic guards. For a B-bit bank and v-bit whole family,
I charge O(B+v) time and O(B+v+h+log B) additional transient storage.
The caller closes the replacement bank before any recursive tail cut.

Read [PROOF.md](PROOF.md) for the quantified row layout, selected chart
calculation, disjoint-support factorization and complete cost argument.
The scope covers one prefix of call0. I leave its tail gathering, adapters,
children and complete supplier invoice to their existing obligations.
I claim no new exponent or full multiplication theorem.

## Evidence and reproduction

Run from the repository root with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/selected-first-prefix
```

I register source-binding and fault checks, a disjoint-route control model,
the full encoded cover-cardinality calculation, complete finite
14,336-family banks and nested caller/error-return checks. The finite
banks use generic N=1/3 rather than the enormous selected cover extent.
I distinguish those executable fixtures from the written all-N proof.
`RESULT.json` pins the complete typed receipts; `--emit` prints a fresh
receipt for diagnosis without comparing it with that file.

The runtime imports a frozen PR3098 archive and authenticates its inherited
live tape sources. It does not require another contributor's branch or
install a proof assistant. Exact source pins and predecessor credit appear
in [SOURCES.json](SOURCES.json); bounded commands appear in
[VERIFY.json](VERIFY.json).

## Predecessors and contribution

James Chang/jamesyc's [PR2370](https://github.com/CrocSwap/integer-mult-bounds/pull/2370)
states the selected raw2 reference semantics and leaves whole-family chart
equality, allocation and physical costs as premises. Ali Romman's
[PR1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969)
supplies exact cover transport and data-phase analysis. Gareth Davidson's
[PR1255](https://github.com/CrocSwap/integer-mult-bounds/pull/1255)
retains the selected chart/global-phase discipline. ywz65's
[PR2591](https://github.com/CrocSwap/integer-mult-bounds/pull/2591)
supplies prepared half-ADD, with acquisition and routing outside its scope.

I instantiate the chart premise from the actual stage-zero data routes,
give the prefix-tail factorization and complete the physical bank boundary.
I reuse my [PR2287](https://github.com/CrocSwap/integer-mult-bounds/pull/2287)
mixed-radix row specification and
[PR3098](https://github.com/CrocSwap/integer-mult-bounds/pull/3098)
scalar engine. That frozen archive retains Nick Petalas's PR3078/3090
recipe/capacity work, Sagar Thakrar's PR696 dyadic lowering, James Chang's
PR1869 arithmetic and the earlier tape/compact sources and notices.
I preserve those attributions and do not claim their mathematics as new.

## Open next questions

- Connect the returned bank to the actual raw3 tail. First check its
  current owner/frame requirements and consume this prefix work before the
  first recursive cut. The remaining adapters, centres and complete
  caller invoice remain separate obligations.
- Find another prefix with a source-derived common chart and a consumer
  that avoids repaying its access cost. First price its entire entry and
  return boundary. This one call does not establish a general hoisting
  policy or an asymptotic improvement.

I coordinated this scope in
[2238#18986017](https://github.com/CrocSwap/integer-mult-bounds/discussions/2238#discussioncomment-18986017).
Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including analysis subagents. Apache-2.0. I claim no independent human or
proof-assistant verification of this contribution.
