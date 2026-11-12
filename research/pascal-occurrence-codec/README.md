# Construct exact Pascal occurrence and owner addresses without materializing compiler classes

**Scoped constructive compiler lemma; no new kappa.** The finite mixed-target
compiler can resolve its exact chronological matching and the physical field
behind any productive occurrence by arithmetic on one descriptor. A query
uses at most G+1 ancestor decisions and does not build its class, matching
bucket or owner table. The construction covers every positive integer top
rank in the separated-flow domain, with the actual ambient cap A allowed to
exceed every target rank.

This answers one part of [#6878](https://github.com/CrocSwap/integer-mult-bounds/pull/6878)'s
request for an explicit occurrence emitter: the previously implicit ordered
Pascal matching and owner-address lookup now have a concrete, terminating
codec. The selected conditional value stays **0.00363005817**. All five
selected assumptions remain; this package does not claim a complete dispatcher.

## Exact result

For target multiplicities W_i and multiindex alpha, let

`u(alpha)=multinomial(|alpha|;alpha)*product W_i^alpha_i`.

The parent occurrence interval `[0,u(alpha))` partitions into blocks of
length `W_i*u(alpha-e_i)`. In the block for i, quotient and remainder by W_i
give the child occurrence and the exact native role. The inverse reconstructs
the parent ordinal. This is the ordering used by the retained literal compiler,
including native role lists whose equal-rank roles are not adjacent.

At a child occurrence, the actual ambient inequality decides whether that
parent exists. Otherwise the slot is a new source. If it exists, following
the paid occurrence's actual productive or owned owner removes one path
letter. Repeating reaches the canonical source or owned-bank identifier.
Paths distinguish paid *positions*, not merely equal ranks, and retain the
invocation namespace and replica number.

[PROOF.md](PROOF.md) establishes the bijection, exact source classification,
matched-rank equality, owner identity, injectivity within every live class,
termination and descriptor bounds. It separately charges integer arithmetic:
the offline lookup has an explicit polynomial bit-work bound. A symbolic
field name does not grant constant-time access to that field on tapes.

## Evidence and reproduction

From the repository root, after placing this directory at
`research/pascal-occurrence-codec/`:

```sh
python3 -I -W error -B research/pascal-occurrence-codec/verify.py
python3 -I -W error -O -B research/pascal-occurrence-codec/verify.py
```

Standard-library Python 3.12 suffices. Both commands print
`PASS_PASCAL_OCCURRENCE_CODEC` in their JSON result. Local runs agree exactly.

| Executed coverage | Count |
|---|---:|
| Complete small flow instances | 242 |
| Instances with A greater than every target rank | 130 |
| Ordered class streams | 1,665 |
| Native unit occurrences | 3,310 |
| Productive role owner comparisons | 9,934 |
| Exact matched-edge comparisons | 4,998 |
| Fresh source identifiers | 4,936 |
| Terminal paid owner comparisons | 2,132 |
| Negative controls | 10 |

The oracle is the byte-identical retained `finite_dag_audit.py`, pinned by
Git blob and SHA256 in [SOURCES.json](SOURCES.json). For the 130 ambient-cap
fixtures, an explicit test adapter overrides only its `Rule.dimension`
property. Every matching, class, source, exit and field computation remains
the retained oracle's code. This parameter adapter is disclosed rather than
described as unchanged-source coverage of the larger ambient domain.

Separate tests resolve a 128-generation chain into the last of `2^128`
root occurrences without enumerating that population. Controls reject zero
ranks, overlapping paid/target ranks, duplicate productive labels, a missing
Pascal letter, an invalid ordinal, a wrong interval offset, repeated occurrence
identities, an absent unit at the cap boundary and omitted replica identity.
These checks corroborate the written universal proof; they do not establish
it by extrapolation. The oracle is independently authored predecessor work,
but this codec's author read that source, so this is not a blind comparison.

## Novelty and limits

Jacob Alan Sussman's weighted Pascal flow and zxv's finite precompilation
already supply the counting identity, chronological schedule, denominator
clearing and rank descent. [#4691](https://github.com/CrocSwap/integer-mult-bounds/pull/4691)
already proves the general live-role induction and tests an event-level
executor. [#6878](https://github.com/CrocSwap/integer-mult-bounds/pull/6878)
already constructs charged complete-coordinate occurrence routes. Those
results are not claimed again as new theorems.

The addition is a direct arithmetic inverse to the actual ordered bucket
matching and a terminating, table-free owner-address algorithm, with source
equivalence and explicit descriptor/arithmetic costs. Its input is a complete
finite native role/paid-owner specification, not a rank histogram. The selected
1920-fold product and its winning uniform rank are not materialized here.
The codec has not been installed into a full native, numerical or tape caller.
No total-time speedup, smaller threshold, supplier admission, human peer review
or proof-kernel acceptance is claimed.

Bounded overlap inspection covered the pinned compiler, live-role,
completion, source-law and occurrence-layout packages; research-directory
metadata; and GitHub searches for Pascal/codec, lazy/compiler and
occurrence/matching. #7136/#7137 concern a different V02 compiler-input/custody
workstream. Absence of another matching search result is not proof of novelty.

## Open next questions

1. **Rank fresh source names into contiguous row intervals without a table.**
   Start by deriving subtree source counts for the existing paid-path order.
   This would connect the codec to integer batching and actual row ownership;
   count-level source conservation alone does not supply this rank/unrank map.
2. **Bind one complete selected occurrence stream.** Start with the actual
   chronological product at power two and its complete paid-owner manifest,
   then compose the codec with #6878's routes. The enormous final product
   manifest and all native segments remain explicit missing inputs.
3. **Lower the resulting metadata service with its complete physical bill.**
   Choose a descriptor representation and charge scans, big-integer work,
   source access, restoration and nested bank lifetime. The present offline
   algorithm is not a fixed-tape tariff and cannot remove precision_tape.

## Provenance and credit

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Prepared for **Jerry Chen / @CubeJerry** with substantial OpenAI assistance.
Credit Jacob Alan Sussman for the lockstep/Pascal construction; zxv for
`FINITE-PRECOMPILATION.md` and its literal audit; Mark / Matarener for #4691
and the completion/lifetime executor; and @CubeJerry and predecessor authors
for #6878's occurrence-layout theorem. The source oracle retains its original
header and is not modified. Apache-2.0. See [NOTICE.md](NOTICE.md).

## Additional independent review

[REVIEW.md](REVIEW.md) records a separate proof review, byte-identical remote oracle check, and 1,092 literal-word plus 171 owner-graph checks. Reproduce with `python3 -I -W error -B research/pascal-occurrence-codec/independent_check.py`. This AI review is not human or formal-kernel verification.
