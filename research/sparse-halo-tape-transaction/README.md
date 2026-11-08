# Sequential first-face halo transport and unique return

**Result:** a fixed-role sequential tape implementation of the sparse halo
transport left open by [#4870](../halo-copy-enumeration/README.md). It copies
the original values before core mutation, constructs complete destination
keys without dense long arithmetic, stably sorts the sparse records, and
checks an exact boundary-only return transaction. The numerical halo values
remain the responsibility of an explicitly supplied consumer.

**No new κ.** This addresses a physical sub-obligation of `precision_tape`
and `analytic_recovery`; all five selected assumptions remain. It is not an
unconditional integer multiplier or a numerical inverse implementation.

## Technical result and scope

On the dyadic caller domain, let `L=2^ell`, `S_i=2^(k_i+ell)`, `k_i>=1`,
`0<=b<A`, and `L>4A`. There are `g` active coordinates and an optional
complete binary spectator prefix. Let `M` count dense scalar records, `P`
their opaque payload width, `B` their complete coordinate width, and `C`
the inherited copied-input volume. The emitted key width is

```text
K = 2 B + 3 g + 1.
```

The written theorem in [PROOF.md](PROOF.md) establishes

```text
time:              O(M(P+B) + C K(P+K))
retained backing:  O(MP + C(P+K) + B + P)
physical roles:    30, independent of g, M, P, and key width.
```

The dense scan maintains physical binary core/local odometers. Comparisons
inspect all coordinate fields only a bounded number of times; no full-key
division or multiplication is paid per dense scalar. Unary face descriptors
and repeated full descriptor scans are charged to actual emitted copies,
because every admitted face has at least one leaf. Empty-center sources
still pay their one dense scan. Full-key radix sorting is paid only on
sparse copies and returned targets.

The program uses a 14-symbol tape alphabet. Reported actions are individual
symbol reads, writes, and unit head moves. A four-bit block encoding gives
a constant-factor binary-tape simulation; the raw action totals are not
claimed to be exact binary transition counts. Only the simulator backend
uses host cell indexes. Program control consists of a fixed set of tape
handles, finite flags and symbols, with no input-sized host record array or
integer key. This is a reviewed executable tape program with an all-size
proof, not a formal transition-table certificate.

Every scratch clear scans its current live extent. Historical erased cells
remain in the retained high-water bill, but do not get rescanned after every
later short record. The two radix buckets and all other roles reuse their
origins. These details prevent both an uncharged rewind and a hidden
dimension/history multiplier.

The input is a complete canonical lexicographic stream with equal-width
payloads and a well-formed dyadic coordinate schema. Arbitrary nonbinary
periods, caller layout production, numerical coefficient generation, and
the numerical core/halo algorithms are outside this standalone theorem.
It rejects missing, duplicate, and kept-row returns on the admitted schema;
it is not a hardened parser for every malformed binary input.

## Relation to earlier and concurrent work

Cinna Davis's #4100 proposed the first-face Gaussian schedule and its dense
scan/sparse correction budget. The source combinatorics, volume formula,
zero-copy centers, and corner fanout were already proved and checked by
#4870. Its explicit next question asks for the physical short-field
enumerator, full-key radix distribution, and paid movement/retention.
This package supplies that implementation obligation on the actual dyadic
period domain; it does not claim those earlier lemmas again.

The numerical locality questions studied in Nick Petalas's #4217 and #5986
are distinct. The pending #6880 common-reference rounded core/halo splice
requires copies before mutation and target-only return, which this
transaction enforces. Its exact nonexecuted head/blob/SHA is retained in `OVERLAP.json`, separately
from live source inputs and canonical-base ancestry. A concurrent
shrinking-domain reference-band consumer can use the emitted local offsets,
after an explicitly priced sparse codec; compatibility alone is not an
executed or accepted complete Gaussian caller.

The lead's bounded canonical archive survey and a focused PR search for
`4870` and `"halo" "tape"` located no later implementation of this exact
obligation. Related #486 and #3935 use other physical halo/layout schedules;
generic sequential sorting is not novel. Discussion access and historical
diff coverage were incomplete. This records the evidence used for task
selection, not exhaustive novelty or literature priority.

## Reproduce and evidence

Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
`SOURCES.json` gives exact Git blobs and SHA256 values. The three live
predecessor text inputs are checked even in a Git-free source export.

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/sparse-halo-tape-transaction
```

Expected: `PASS_REGISTERED_RESEARCH_PACKAGE`. `VERIFY.json` registers the
normal and optimized complete transaction replay and the normal and
optimized separately written geometry/radix review. Direct transaction
replay prints a JSON receipt with `"status": "PASS"`; the review prints
`PASS_INDEPENDENT_HALO_GEOMETRY_AND_RADIX`. No assertions are used as
acceptance gates, and no third-party dependencies are required.

The full transaction fixtures are:

| Fixture | Dense M | Copies C | Targets Q | Max fanout | Zero-copy sources | Metered actions including erase |
|---|---:|---:|---:|---:|---:|---:|
| One axis, L16/A2/b1 | 32 | 16 | 8 | 2 | 20 | 356,848 |
| Two axes, L16/A2/b1 | 1,024 | 1,024 | 448 | 4 | 400 | 55,924,621 |
| Spectator and unequal periods, L8/A1/b0 | 1,024 | 448 | 448 | 1 | 576 | 28,502,162 |

All emitted keys and payloads are compared with a destination-first interval
oracle, independent of the source predicates and suffix odometer. The
largest fixture retains 124,785 finite-alphabet cells across 30 roles,
including blank cells after erasure. Exact arithmetic checks cover 1,364
pairs of 1–5-bit operands for comparison, addition, subtraction and modular
increment/decrement. The exact observed receipts are in `EXPECTED.json`.

Controls reject a missing target, duplicated target, unexpected interior
return, core mutation before copying, return before core mutation, and a
nonunit head jump. They also detect reversed radix bucket concatenation and
copying after a destructive core change, and check duplicate-key stability.
A static check excludes observer calls from the program; that check is
limited and is not runtime enforcement of private simulator fields.

The separately assigned source-aware AI review in `independent_review.py`
uses direct modular membership in every destination-core face interval.
It imports the author program but neither the author's geometric oracle nor
fixture builder. It checks 366 selected source points in dimensions one
through four, 830 emitted copies, and five stable-radix/idempotence cases
with duplicate keys. Its independence concerns the membership oracle and
sort expectations; replay of the implementation is not an independently
written tape program. Human and proof-kernel acceptance are unclaimed.

The core operation in transaction fixtures complements payload bits. It is
a destructive ownership test double, not execution of the fast Gaussian
core circuit. Return values are supplied as explicit consumer-contract
inputs. Numerical accuracy is therefore not inferred from these tests.

## Open next questions

Structured versions and blockers are in `TASK.json`.

1. Join a same-reference numerical consumer to the saved stream with a
   physically charged crop/width/key codec, preserving immutable sources
   and target-only output. Start with a dyadic reference fixture crossing a
   period cut. Numerical page production, arithmetic/precision, and the
   resulting joined cost require their own pinned evidence.
2. Bind the transaction to the selected outer caller's actual dense layout,
   core supplier, normalization, and recovery scales. A standalone transport
   result cannot discharge the complete analytic or machine assumptions.

## Attribution

Prepared for **@CubeJerry** with substantial OpenAI Codex assistance in
mathematical construction, implementation, source investigation and a
separately assigned adversarial AI review. Credit Cinna Davis (#4100), the
Astra/OpenAI-assisted #4870 contribution, Nick Petalas (#4217), the #6880
contributors and their retained source lineage. Douglas Colkitt/OpenAI's
tape framework, Vlado Vojdanovski's Gaussian layouts, and Chafik Boukhalfa's
constructions are predecessor work; no claim to those mechanisms is made.
Apache-2.0, following the repository license.
