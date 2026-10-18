# UT4 one-slack compression removes the two-target workspace search

**Uniform scoped reduction; no new word or kappa.** In the full formal
`F2[UT4(F2)]` alphabet of [PR1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662),
every central-target word with `r>=w>=2` and unit paid length `L<=7w+1`
has an equivalent word on exactly `w` roles with no more calls. All extra
roles may begin arbitrary dirty and must be restored. Paid couplings may be
any nonzero binary rank-one matrix, including nilpotents; scalar mixing is
normalized first, and every paid call is counted.

Consequently the optimal **two-target unit count is identical for every finite
`r>=2`**, with its exact value still one of **14,15,16**. A 14/15-call witness
or complete exclusion on two roles therefore answers the same question for
arbitrary workspace. No such witness or exclusion is supplied here. This adds
the missing workspace implication to the predecessor's unchanged 14..16 interval.

The [written proof](PROOF.md) sums six scalar span inequalities. At length
`7w` all spans equal the active target plane; at `7w+1` at most one span has
one extra dimension. All paid factors therefore share one block orientation.
Projection to the active corner preserves their product over the **full
noncommutative group algebra**. Projected couplings have rank one or zero;
zero identity factors are discarded, so each label count can only decrease.

This does not claim that every 16-call word compresses, that weighted tariff
optima are workspace independent, or that larger-slack words admit the same
argument. There are no clean roles, free address operations, higher-rank paid
factors, COPY or ERASE. No physical supplier, rational-frame identity,
compiler/hosting contract, multiplication exponent or selected-frontier change
is claimed. Kernel formalization, precision/tape and analytic transfer remain open.

## Exact corroboration and scope controls

The theorem is a written uniform argument with a retained fixed-group lemma;
finite role fixtures corroborate its algebra and do not prove its quantifiers.

| Check | Coverage |
|---|---|
| Common-orientation formal/faithful operator comparison | 3,969 ordered pairs per upper/lower orientation on three roles, active width two |
| Distinct pair coverage | 7,209 distinct pairs; 729 belong to both orientation families, giving 7,938 recorded cases |
| Complete regular basis columns | 1,524,096 full input columns, including arbitrary dirty-role inputs |
| Zero projected factors actually discarded | 2,268 occurrences across the recorded pair cases |
| Integer span-slack profiles | 105 profiles, widths 2..16; all possible zero/one-excess positions |
| Known coordinate upper words | 10 fixtures through five roles, 2,560 complete basis columns |
| Retained quotient homomorphism/associativity | 4,096 group products and 4,913 basis triples |

[CERTIFICATE.json](CERTIFICATE.json) retains exact digests, the fixed quotient
receipt and the separately implemented faithful checker's receipt.
The primary engine multiplies six-coordinate formal group coefficients;
[independent.py](independent.py) uses literal four-by-four address matrices
and simultaneous updates of every regular-basis input. It imports no primary
or predecessor executable. Its four fixtures include both common orientations,
noncoordinate/nilpotent couplings and discarded zero projections. The 16/18-call
endpoint fixtures verify compression's algebraic conclusion; they are not
14/15-call witnesses or instances establishing the one-slack forcing premise.

A mixed upper/lower pair has two individually zero active projections, yet its
full product feeds the dirty role back into the active corner. The checker
rejects it. A rank-two plane missing one active direction demonstrates why
dimension counts alone do not replace the six target-span containments.
The fault suite covers the two-slack threshold, illegal alphabets/domains,
actual model/vendor/receipt corruption, occupied outputs and optimized read-only
relocation. No sampled bits or nonfaithful proof image admits a full endpoint.

## Reproduce

From the repository root, with Python3.12 and standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/ut4-one-slack-workspace
```

Expect `PASS_UT4_ONE_SLACK_WORKSPACE`,
`PASS_UT4_ONE_SLACK_INDEPENDENT`, passing fault tests and
`PASS_REGISTERED_RESEARCH_PACKAGE research/ut4-one-slack-workspace outcome=completed`.
Normal verification writes nothing. Explicit `verify.py --write-receipt NEW_PATH`
and `independent.py --write NEW_PATH` refuse occupied outputs. The registered
manifest is [VERIFY.json](VERIFY.json); actual local commands, environment and
unrun obligations are recorded in [VALIDATION.json](VALIDATION.json).
Standalone optimized replay also works in a source export containing the
declared live model input. Generic provenance checking requires the pinned Git history.

## Scope, coordination and retained source credit

Base main: `a18b4b0136d647529971e9fcb99fa83f5b9a0b81`; revision3 task
`bit-new-register-model`, nonce `e5da093483cfe0c1dfea3262d0f0935b`, scope key
`7f5f4426ef796683c485`. Scope is explicitly **changed** from constructing a
shortest identity to a useful missing-workspace reduction for that construction
problem. [TASK.json](TASK.json) retains the original card, reason, bound and
overlap limitations. The required selected-baseline source-binding control passed;
it was not the selected full cold replay.

This is complementary to **Aaron Wang / navinor's active two-role exhaustive
search**, [claimed here](https://github.com/CrocSwap/integer-mult-bounds/discussions/1647#discussioncomment-18916137)
with Claude Code assistance. That claim leaves extra dirty roles open; this
package removes that gap at 14/15 calls without duplicating its search or
endorsing an unpublished result. [Our claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1647#discussioncomment-18916672)
states the complementary scope. Entry checks covered 537 open PR bodies including
drafts, local package metadata/ledger and bounded live Discussion reads.
Concurrent merges prevent an atomic PR snapshot; full Discussion pagination,
all diffs and unpublished work were not covered. No novelty guarantee is made.

Credit **@ToikY / PR1662**, head `01cc02b164ecc4f9d84df3f56a1fe65b88daf390`,
for the UT4 six span containments and middle quotient. Its `quotient.py` is copied
**byte-for-byte**, with exact Git blob and SHA256 in [VENDOR.json](VENDOR.json),
so replay does not require an unmerged dependency checkout. Its unchanged fixed
homomorphism certificate is inherited evidence, not a new independent implementation.
[SOURCES.json](SOURCES.json) binds the live model input and selected/catalog provenance.

Retain credit **steph4n-gh / [PR1573](https://github.com/CrocSwap/integer-mult-bounds/pull/1573)**
at `0b8c5a69297c794f2de22c04494c83e41300ae36` for all-register zero-sum ranks;
**Arham Tahir / [PR1589](https://github.com/CrocSwap/integer-mult-bounds/pull/1589)**
at `010ec8c01c0edbbb08b541be236ab78d096f2ca1` for nilpotent couplings;
**Hanson Sun (@bbMisk) / [PR1607](https://github.com/CrocSwap/integer-mult-bounds/pull/1607)**
at `9d6117918025cee6a0c5b7ef30ff8d936ca0621f` for coefficient spans, and the
juper997/PR1478, woklerx/PR1443, Gareth Davidson/bitplane/PR1333,
commdata2338/PR1414, eumemic/PR288 and Ali Romman/PR468 lineage retained by them.
No literature-priority claim is made. Prepared for @ToikY with substantial
OpenAI Codex assistance, including two bounded subagents; no independent human
or proof-kernel review claimed. Apache-2.0, with inherited notices preserved.

## Open next questions

Does the two-role 27-factor alphabet attain 14 calls? Coordinate with navinor's
active search and independently audit its eventual complete formal certificate.
The reduction makes a rigorous two-role exclusion decisive for all workspace
sizes; an incomplete census does not. No complete certificate is supplied here.

If 14 is excluded, does a 15-call two-role word exist? Define a complete exact
domain and full endpoint check; extra dirty-role sizes need not be searched.
This remains blocked by the unresolved 14-call question and any overlapping
active investigation. Weighted tariffs and larger-slack workspace use are
separate questions, not conclusions of this package.
