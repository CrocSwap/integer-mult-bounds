# Kernel-checked guarded Compact repair

This package formalizes the successful-completion endpoint of PR2250's
exception extraction, inverse destination keys, whole-record radix passes and
guarded reinsertion. It addresses the sequential-repair handoff explicitly
left by [PR2378](https://github.com/CrocSwap/integer-mult-bounds/pull/2378).
It does not discharge that package's complete physical primitive premise.

The [Lean theorem](Repair.lean) proves, for arbitrary payload type, address
list and compatible raw/ideal maps, that a successful repair emits
`input composed with idealInverse`. Raw inverse/good-set laws and successful
destination and exhaustion guards remain explicit hypotheses. The complete
proposition, induction and source correspondence are in [PROOF.md](PROOF.md).
Radix preserves whole key/payload pairs; sorting order and total successful
completion are not proved here.

## Evidence

The fresh Lean4.34.1 kernel run proves four named roots, using only `propext`
and `Quot.sound`, and rejects four false propositions about wrong payloads,
wrong destinations, incomplete consumption and missing good agreement. The
axiom-output guard has a separate negative control. No `sorry`, custom axiom,
`native_decide` or externally evaluated proof admission occurs. [KERNEL.json](KERNEL.json)
binds the actual run to the exact formal source hash and toolchain version.
The installed compiler and Std compiled library are trusted, not independently
rebuilt. This core-only result is not an integration into PR2378's different
Lean/Mathlib environment.

Separately, authenticated unchanged PR2250 code passes complete-address tests:

| Fixture | Addresses | Payload bits | Exceptional / good |
|---|---:|---:|---:|
| Earlier source, n=1, K=2, G=1 | 2,048 | 11 | 2,048 / 0 |
| Constant toggle, n=1, K=5, G=1 | 8,192 | 13 | 6,144 / 2,048 |

Every address has a distinct binary payload. The replay checks both raw
inverse orders, ideal involution, bad-set preservation, good-set agreement,
the list model against the physical repair, complete primitive output, and a
second invocation restoring the initial array. It records physical repair
meters but asserts no new asymptotic bound. The all-bad earlier fixture alone
would not test good-stream handling; the mixed constant fixture does.

Ten semantic/control cases include accepted-but-wrong inverse-key and
key/payload-separation variants, destination and exhaustion rejection,
missing good agreement, and the empty boundary. These are assumption controls,
not alleged defects in the original source. The integrity checker verifies a
Git-free optimized replay is read-only and rejects seven source, formal-source,
axiom receipt, typed-result and CLI corruptions.

The Python receipt intentionally states `kernel_checked_by_this_command=false`.
Its formal receipt check is structural provenance only. A fresh proof requires
the separate Lean command below; Python execution cannot establish it.

## Reproduce

From the repository root, standard-library Python3.12:

```sh
python3.12 -I -B scripts/research_package.py --package research/compact-repair-guarded-refinement
```

This registers normal/optimized finite replay and the Git-free integrity test.
Use a writable TEMP/TMP directory if a sandbox disallows its default.
For fresh kernel verification, obtain the official Windows x86_64 Lean4.34.1
release, commit `5045d0056413266e57c625dcd7c365b10e377c52`, then run:

```sh
python3.12 -I -O -B research/compact-repair-guarded-refinement/kernel.py --lean /absolute/path/to/lean.exe
```

The harness copies only the formal source to a fresh temporary directory,
compiles it, checks the named axioms, compiles the false probes and compares
the result with the committed kernel receipt. `--out /new/receipt.json`
creates a separate receipt exclusively. The toolchain check is intentionally
platform-specific; porting a receipt requires an explicit reviewed change.
`verify.py --write` is exclusive and cannot overwrite `RESULT.json`.

## Milestone and expansion decision

This is a **local formal module**. Proved: the all-list, arbitrary-payload
successful repair endpoint and whole-pair preservation. Constructively tested:
the original two finite layouts, including dirty address fields, source
consumption, output origin and full primitive roundtrip. Unknown: all-size
raw Compact laws, guard success, tape/list refinement, physical scratch and
runtime, final highest-bit formal semantics, compatibility with the older
Mathlib consumer and a complete supplier allowance. Unknown costs are not zero.

Following guidance revision5, stop at this narrow handoff. Further expansion
requires a named consumer and a plan to close its remaining primitive/tape
contract; additional finite samples do not close it. No selected frontier,
exponent, full supplier or completed primitive is claimed.

## Open next questions

**Can the actual earlier-source repair be proved to complete?** Prove the
raw inverse and bad-set laws for its parameter/layout domain, identify the
exceptional-key multiset with the holes, and prove the actual address-bit
radix schedule sorts it. This closes the explicit `hcomplete` premise, but
still needs tape refinement. The blocker is a source-faithful all-size proof,
not another tagged finite fixture.

**Can this endpoint be integrated into the completed-primitive consumer?**
Start with a tape/list relation preserving whole records, exhaustion and
scratch closure, then bridge the final highest-bit permutation and the exact
consumer toolchain. Physical traversal and resource obligations remain open.

## Credit and provenance

Original PR2250 code is retained byte-for-byte at
`d404b48a1e7b147556b309497d55089c837dddb2`; the PR2378 handoff is pinned at
`5816f94741709e8082e06a2cc9a114ff87411f3d`. [VENDOR.json](VENDOR.json) records
blobs and SHA256. [SOURCES.json](SOURCES.json) binds retained context and
guidance. [OVERLAP.json](OVERLAP.json) records search coverage and limits;
absence of a match is not a novelty certificate.

Jose Manuel / jmbarrancoml supplied the original repair implementation and
proof; AAAmirinu supplied the formal consumer and explicit handoff; Gareth
Davidson / bitplane, Douglas Colkitt and DreamingOfClouds supplied the credited
foundations. See [NOTICE.md](NOTICE.md) and the unchanged original notice.
Prepared by ywz65 with substantial OpenAI Codex assistance, including separate
AI review. No human or maintainer acceptance is implied.
