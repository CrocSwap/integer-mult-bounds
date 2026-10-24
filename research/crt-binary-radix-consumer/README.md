# A literal binary radix consumer for the CRT repair stream

This closes **Open next question 1 of [PR4982](https://github.com/CrocSwap/integer-mult-bounds/pull/4982)**:
execute the next actual sparse-repair consumer in bit control. The fixed
[program](radix.py) uses the unchanged predecessor compiler/bit machine to
lower the retained `bridge.one_pass` stable-radix algorithm. The entry
representation, payload semantics and actual caller are preserved.

The [written proof](PROOF.md) covers **every finite stream** with n opaque
12-bit payloads and nonempty binary keys of total length K. One pass has
complete literal bit-action bound

```
7740 * (8*n + 12*K + 10) + 144.
```

It includes framing validation, all bit reads/writes and unit head moves,
finite Boolean/control steps, stable bucket partition/merge, bucket erasure,
head return, and initialization/erasure of all 72 finite-control bits.
For equal key width L, L repeated passes stably sort the full keys and
restore their orientation. This is an explicit finite-tape program and a
uniform source-control proof, not an extrapolation of a symbolic cell meter.

The program is static: 180 source instructions, 3885 binary instructions,
three tape roles, and no input n, L, key integer or decoded stream in the
assembler/executor. It recognizes opaque records using the declared source
alphabet, without inspecting their payload value. Entry requires aligned
13-bit predecessor codewords and clean owned buckets. Unused codewords,
dirty buckets, missing/duplicate outer markers and misaligned entry heads are outside this
port contract. Record/key grammar errors inside a uniquely LEFT/END-framed
stream reject
before output, preserving the borrowed input and clearing finite control.

## Evidence

[RESULT.json](RESULT.json) records these independent endpoint/representation
checks, executed in both ordinary and optimized Python:

- All 371 streams with up to four one-bit-key records, or two keys of width
  one through four; both empty buckets, all-zero/all-one partitions and
  duplicate keys are covered. Distinct payloads detect loss of stability.
- Three complete source-instruction-boundary simulations against the
  predecessor's independently represented source semantics. Every physical
  head scale, register result and written codeword matches. The exact
  backward-transfer counts corroborate the all-size control proof.
- Complete stable sorting through three and 37 passes, width-one keys,
  payload boundary values 0/4095 and variable positive key lengths for a
  single pass. Every legal endpoint also matches the original literal
  `bridge.one_pass` and an independent stable sort/rotation oracle.
- Five faults reject: reverse bucket order, wrong key rotation, retained
  bucket data, short physical cell strides and omitted control erasure.
  Eight malformed uniquely framed packets reject with borrowed data and bucket
  preservation, returned heads and cleared control.
- **Actual source caller connection:** original `bridge.split` emits two
  completed pairs through the real bit-level key service, then continues
  to the third marked address. Its completed prefix is explicitly closed
  by verifier setup. The new radix consumer receives those **same physical
  tape objects**, uses 37,969 actions, and returns the expected payloads,
  key rotations, heads, blank buckets and cleared control. The outer
  caller's facades remain an unlowered boundary. No whole layer is implied.

Finite tests corroborate the quantified written proof; they are not formal
kernel verification. The static 43-action compiler-block simulation is a
pinned predecessor premise. This package adds source-control proof and
consumer/caller checks instead of rerunning its complete alphabet census.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/crt-binary-radix-consumer --check-only
python3.12 -B scripts/research_package.py --package research/crt-binary-radix-consumer
```

The registered hook runs ordinary and optimized checks, authenticates all
thirteen live inputs and compares every proof-relevant receipt field.
Direct `verify.py` replay also works in the package's standard Git-free
export; `--write-result` alone regenerates its receipt.

## Family decision, sources and overlap

**Narrow, then stop:** this is one named actual-consumer obligation. Full
binary split/reinsert, physical descriptor and ROM production, variable CRT
geometry, compiler creation/serialization and whole CRT E(p,ell) remain
unknown. The inherited fixed key fixture does not become a uniform key
compiler. No complete 2944-hole layer, historical suite, Lean/Docker or
selected supplier replay is run. No new kappa or selected-frontier change
is claimed.

[SOURCES.json](SOURCES.json) pins canonical base
`bee95ce88f9f19802f0613f92838895cd0e14a1f`, priority revision 7, and all
imported source bytes. The key/binary predecessor is PR4982 at
`67154122b2867e6dee5b9b25f2f1c862a3e81e95`; its PROOF.md supplies the
compiler simulation. The original bridge and key/source lineage remain
unchanged. Pending PR4990 supplies a two-target unary stencil, a different
producer boundary. Symbol-level repair and abstract radix predecessors
already supply stable sorting; that algorithm is not claimed as new.

Initial overlap covered all 6690 current tracked notes, 310 open/draft PR
bodies at 2026-10-23 06:05:59 UTC and 4096 Discussion records at 06:06:48
UTC, with complete inventory/pagination. The targeted `one_pass`/`binary`
search found only PR4982's README/TASK and its canonical result. Arbitrary
diffs and unpublished work remain outside coverage; no novelty guarantee
is claimed. Canonical coordination is [Discussion4709](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19139345); [TASK.json](TASK.json)
retains the scoped card, stopping rule and next questions.

## Open next questions

1. Specify one complete actual encoded split/sort/reinsert caller, with its
   transport and restoration obligations, before expanding implementation.
   This decides whether local stages can share one complete paid invoice.
2. Specify the encoded variable-geometry key/ROM producer and its lifecycle
   allowance. A different finite key seed would not resolve the current
   uniform producer/serialization gap.

The structured questions and blockers are in TASK.json. Neither is claimed
or implicitly assigned by this package.

## Credit

Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
Retain PR4982/PR4795/PR4752 authorship and the original PR4637 scanner/repair
lineage: Cinna Davis, ToikY, Hiroki KUMAZAKI, Ryanson Jonathan, unpaidmoon,
Jose Manuel, Douglas Colkitt and John-Michael Smith (PR763 lineage). The
[source-specific notice](../unconditional-batched-crt/NOTICE.md) remains in
its declared source inputs. All frozen predecessors are unchanged. No
independent human or formal proof-kernel acceptance is claimed.
