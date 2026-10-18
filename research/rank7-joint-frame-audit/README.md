# Independent joint rank-seven frame audit

Both #2979 providers pass a code-disjoint chronological frame recount. The
five isolated groups sum to its stage-one invoice. No finite frame defect was
found. This is a partial audit, not supplier admission or a new kappa.

## Shared overhead, with losing controls

For V45, keep the group's 61 gate-frame edits fixed and lower any `k` of
helpers `{249,251,265,267}` from rank eight to rank seven. All 16 endpoint
subsets pass the literal frame and unchanged cleanup-syntax checks. Their
exact paid-profile difference from the parent is

```text
Delta(k) = (2-k) H1 + 10 H2 + 6 H3 - 10 H4,  0 <= k <= 4.
```

Here `Hr` means one rank-`r` child, not a numerical tariff. Thus the partner
cost is paid once and each additional endpoint saves exactly `H1`. The result
holds for any additive rank tariff on these fixed paths. It does not optimize
frames for the proper subsets or prove a global single-lowering bound.

Substituting the source's integer surrogate prices and its approximate
2,091,300-unit width guide gives the following margins:

| Lowered endpoints | Number of subsets | Guide margin per subset |
|---:|---:|---:|
| 0 | 1 | -78,512 |
| 1 | 4 | -53,141 |
| 2 | 6 | -27,770 |
| 3 | 4 | -2,399 |
| 4 | 1 | +22,972 |

These reproduce the source's comparison, but **the guide is not a certified
physical idle tariff**. A positive guide margin does not establish a complete
supplier saving. The symbolic identity above is independent of the guide.

## Whole stage and final boundary

The checker partitions all 139 edits by their unique containing group space,
checks each old gate and frame, and reconstructs each group independently.
No scalar, operator, entrance or cleanup gate changes in stage one.

| Group | Exact paid-profile delta | Gate-frame edits |
|---|---|---:|
| V45 | `-2 H1 +10 H2 +6 H3 -10 H4` | 61 |
| A | `-H1 +20 H2 -14 H3 +2 H4 -2 H5` | 21 |
| B | `-H1 +20 H2 -14 H3 +2 H4 -2 H5` | 21 |
| C | `20 H2 -14 H3 +2 H4 -2 H5` | 18 |
| D | `20 H2 -14 H3 +2 H4 -2 H5` | 18 |

Their sum is `-4 H1 +90 H2 -50 H3 -2 H4 -8 H5`. Paid rank mass falls
5,166 to 5,144, and helper-width mass falls 3,310 to 3,288. Both providers
also reproduce the shipped final local profile, of mass 5,139, and its
six-width inventory, of mass 3,283. The 408 live helpers remain present.

The inverse-cleanup syntax and endpoint/buffer bijection give 86 private names
before and after stage one, and 91 in the final word. This counts names; it
neither proves their zero return nor supplies physical storage admission.

The actual dispatch has 250 base and 416 extra calls. Multiplying the checked
final local profiles by those counts leaves
`17310 H1 +4956 H3 +1728 H5 +28190 H48` when subtracted from the source's
claimed complete invoice. `RESULT.json` labels this remainder conditional:
this check does not reconstruct owner geometry or establish that subtraction
as an independently certified idle bill. [#2987](https://github.com/CrocSwap/integer-mult-bounds/pull/2987)
is the separate chronological-packing audit, not a substitute for native or
physical admission.

## Evidence and reproduction

Exact source [#2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979)
is `be191346391661f4d35fc0d1508d0a6029572576`; scientific base is
`836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, priority revision 6.
All nine live inputs match that original PR's bytes and are bound by Git blob
and SHA256 in `SOURCES.json`. No predecessor Python code is imported or run.
The original author and all inherited source notices retain their attribution.

```sh
python3.12 scripts/research_package.py --package research/rank7-joint-frame-audit
# Direct deterministic JSON, without Git or a network connection:
python3.12 -B research/rank7-joint-frame-audit/verify.py
```

`RESULT.json` records both providers, every subset, each isolated symbolic
invoice, chronological-event hashes and 18 deliberate rejections. Controls
cover stale invoices, a wrong rank-seven space, an omitted gate edit, widened
ends, singular warps, missing cleanup, wrong private names, stale preimages and
extra edits. Five unittest methods also test explicit subspaces, charged
climbs, warp maps, normal/optimized command equality, a Git-free export and
corrupted-source rejection. All acceptance checks survive Python `-O`.

The scope is exact finite frame accounting and cleanup syntax. The scalar
free-operator maps, symplectic/Clifford phases, arbitrary-dirty-input and
private-zero return, owner embedding, full storage, prefix/precision/tape,
outer release and all-size/compiler implications remain unverified here.
The selected bit/complex caps and selected frontier are unchanged. No new
proof-assistant, native build or complete cold replay was run.

## Implementation limits

The frame oracle expands at most 512 points from nine generators, with a
4,096-entry cache. Words have 704 slots, at most 480 warps and 10,000 gates
per section. Input authentication precedes decoding, capped at 2 MB raw and
8 MB decoded per file. All loops traverse these finite domains, five groups
or 16 subsets; no recursion is used. Functions are below 60 physical lines.

Python's managed allocations are a rule-3 deviation from fixed allocation.
The bounds above limit live collections; the cache stores immutable sets.
Rule 9's callback deviation is confined to the nine local rejection actions;
all targets are visible in `controls`. The standard-library cache decorator
only memoizes `span`; it does not generate or evaluate code. Replacing either
mechanism is warranted only if these finite limits or the checker API change.
Diagnostics use `ruff check --select E4,E7,E9,F,B,I`, `ruff format --check` and
Python development-mode warnings as errors. No shared CI settings change.

## Open next questions

Can the independently checked final frame paths and #2987 owner geometry be
joined to one independently checked native residual/phase and physical invoice?
This decides whether the local benefit survives its actual consumer. Start
with one lowered V45 helper's native frame-transition recipe, bind it to this
ledger's chronological events, and check both orientations and its private
buffer endpoint. The missing native/phase, physical storage and precision
bindings block supplier admission; another surrogate-price calculation does
not close them. The full #2979 release remains a separate, larger audit.

## Credit

Marius-Paul Dumitrean/#2979 and #2942 supplied the joint construction and
literal words. Jeremy Kothe supplied the frame/cleanup lineage and #2957
rewrites; Mason Hale/#2917 and Jeremy Diviney/#2908 supplied the paired
extraction chain. This complements ToikY/#2932's older frame ledger and
Ross Richardson's #2960/#2974/#2987 algebra, invoice and packing audits.
Retain Yiyang Lu, Dugongue, Tekalign, icekylinx and the original geometry,
native, owner and compiler contributors' credit. New check by Nick Petalas,
Apache-2.0. No independent human or formal-kernel review is claimed.
