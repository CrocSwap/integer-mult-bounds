# Source-bound six-plane price oracle

This reusable Python standard-library library checks compatibility of a complete
cost candidate with separately trusted, exact-source independent receipts. It
preserves six separate cost planes, exact rational endpoints, explicit unknowns
and source-specific predicate inventories. It does not discover or prove a new
construction, compute a new κ, or establish a global optimum.

The two actual frozen receipt joins return **FUNDED_CONDITIONAL**:

| Source | Exact scientific head | Funded κ | Immutable artifacts |
|---|---|---|---|
| [Ali Romman's #5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383) | `4bd6efa51a495a7c7b7754915cf0244e7e60969e` | `151333/50000000 = .00302666` | 28 |
| [Dugongue's #5387](https://github.com/CrocSwap/integer-mult-bounds/pull/5387) | `b1ab650d36f59e5be682a813145b7c67e219e341` | `605334953/200000000000 = .003026674765` | 32 |

Both have 64,148 paid jobs and 10,800 productive fields. Their literal words,
pivots, retained boundaries, scalar invoices, fresh precision/stock constants
and funded compiler heights differ. The #5387 join uses a fresh independent
physical receipt. Equal histograms transfer no physical coverage. The rejected
ordering-only transfer is not used. These labels consume independently certified
hash-bound receipts; this compatibility replay does not repeat their proofs.

## API and trust contract

`oracle.evaluate(candidate_bytes, artifacts, policy)` takes literal JSON bytes,
a mapping from SHA256 to literal artifact bytes, and a **separately reviewed
policy**. It returns the strongest justified evidence label or raises
`ContractError` for incompatible input. `CONTRACT.md` and `SCHEMA.json` define
the exchange. `TRUSTED-POLICIES.json` fixes the two reviewed policies independently
of evaluation; a candidate cannot supply its own new policy through this replay.
The normalized receipt hashes bind the scientific payload without attached
receipt references, avoiding a hash cycle. Original producer bytes remain intact.

The six planes are paid/productive work, ordinary scalar and routing charges,
ownership and stock, precision and fixed tape, compiler reserves, and BIT outer
admission. Every cost has a unit, state, evidence, dependencies and invalidation
conditions. Unknown is represented by null and blocks funding; optimistic costs
also block funding. Ordinary charges never enter the rank moment as assumed zero.

The library authenticates bytes against reviewer-maintained policy and checks
evidence compatibility. It does not machine-prove arbitrary prose or establish
the reviewer's authority. Physical arguments and applicability require review
before new digest pins enter a policy. Five inherited assumptions remain:
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and
`analytic_recovery`. Requested publication or selected labels require their own
evidence. The selected record is read-only historical provenance here.

The only admitted compiler tuple is power 1024, cutoff 20, floor 21,
tail offset 1/5, theta 63/64 and logarithm power 1000. Each source has its own
funded/tested endpoint and height receipt. Other tuples, physically realizable
words and allocations have not been exhausted. The optional
`source_moment_screen` uses a caller-supplied independent rational interval
backend on an explicit source-certified domain and always returns MODEL_ONLY.

## Frozen inputs and scope

`frozen/` retains the complete 93-file manifest of the original oracle review
draft, plus its manifest itself, byte for byte. Its manifest SHA256 is
`3dd8af4470220929ee516f2d3a97eba6db45ff55908c2cb5ca441f75459fdbed`.
`frozen/SOURCE-PINS.json` and each join's `origins.json` record original paths;
all required bytes are committed locally, so replay does not need those paths,
pending Git heads, network access or scientific engines. Git provenance in
`SOURCES.json` pins the canonical catalogue and selected snapshot at base
`1ec1119972c9aefe42525172d07b332fcff81cb4`. Retained external source identities
are not advertised as ancestor Git pins.

Historical calibration imports selected #4610/.0030217758, independently checked
#5377/.00302235 with verification publication #5384, and the initially pending
#5383 profile. The current #5383 and #5387 joins are separate promotion evidence;
historical pending wording in retained draft documents describes that earlier
checkpoint. This package adds a registered entrypoint, fixed policy pins,
actual-join mutation controls and an adapted read-only calibration whose
predicates remain active under optimized Python. The library is byte-identical
to its frozen reviewed predecessor. This reusable oracle package complements
the separate independent validation package; it does not duplicate its engines.

## Reproduce

From the repository root:

```sh
python3 scripts/research_package.py --package research/source-bound-price-oracle --check-only
python3 scripts/research_package.py --package research/source-bound-price-oracle
```

Python 3.12, standard library only. Both normal and optimized direct commands
are registered, each bounded to 120 seconds:

```sh
python3 -B research/source-bound-price-oracle/verify.py
python3 -O -B research/source-bound-price-oracle/verify.py
```

The direct verifier is portable to a checked source export without Git. It
checks all frozen bytes, both policy pins and actual joins, three calibration
profiles, nine synthetic API test groups and six actual-join test groups. The
controls cover stale or corrupt receipts, missing closure, unknown-as-zero,
changed word with equal histograms, candidate-authored policy domains, unsupported
compiler tuples, incomplete costs, and unsupported publication/selection. Normal
and optimized runs take under one second each locally. A PASS is compatibility
and transport evidence; no native, cold, root, Lean or full theorem replay runs.

## Open next questions

The structured questions in `TASK.json` identify two next steps: independently
review a changed source before adding its policy; or prove applicability and
fund a different compiler tuple before enlarging the domain. These require fresh
source-specific physical and complete-cost receipts. Neither a matching profile
nor a positive necessary moment screen supplies those missing obligations.

## Credit

New oracle, consumer review and packaging by **Chris R / Clear1nsight**, with
substantial OpenAI Codex assistance, under Apache-2.0. Ali Romman owns the
eight-relation #5383 construction and #5377; Dugongue owns successor #5387.
Preserve Cao Yifan's word, Cinna Davis's controller/helper lineage, zxv's
native/compiler/precision work, Jacob Alan Sussman's recursion, ToikY's tensor
lift, the ordinary-BIT contributors, and all retained notices and source credit.
The independent producer receipts and exact engines retain their own authorship.
The generic package generator/runner retain Douglas Colkitt's credit; exporter
credit remains Tekalign's. This submission contributes reusable evidence
compatibility controls, without claiming construction or predecessor authorship.
