# Exact #7131 two-blocker scalar exclusion

**NO VERIFIED GAIN.** The complete conditional comparison remains
κ = 0.003642408496869 on [#7131](https://github.com/CrocSwap/integer-mult-bounds/pull/7131)
at head `67a6544cf18b2d372fd1d0deee1863e9f6ca9fc5`. This package
closes a finite scalar-chronology search that can be skipped when
investigating the next P104 paid-profile improvement.

## Scope and result

The starting native word is the same-word export at
[dillona/666fd749](https://github.com/dillona/integer-mult-bounds/tree/666fd749ec465de7238633a0c2fd5ee3081477e0/research/p104-output-rechart-composition).
Its canonical decompressed SHA-256 is
`9557c4682056ab7cc7cda89aa73865bef0e3948cc10b3c3061b0a944af05b96a`.
The exact signed caller, word and result are committed under
[vendor/inputs](vendor/inputs). They are authenticated both as
stored bytes and against the scientific pins in the replay. These
are vendored exports of pending sources. No local Git object or
remote download of their commits is required.

The [caller source](https://github.com/CrocSwap/integer-mult-bounds/blob/07a76c5e2738882c0cb322278e56f6cae3c9885d/research/signed-caller-8x9/expected/ODD-TYPE-AB-CALLER.json)
has SHA-256 `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`.
The same-word result has SHA-256
`e4ae0c1cfa809cd780a6e22ce32528e7ca4b4e57f90abf91ad0bde97d30446ab`.

On this word, remove one public bridge ADD and conjugate across
its next two incompatible public ADD or SCALE blockers in either
direction. Recompute the support after each crossing. Lower
disjoint-support conjugates to at most four commuting ADDs.
Allow each term to visit every distinct chart pair in its own
commuting window with all other original scalar events fixed.
For the seven overlap cases, test the exact five-factor conjugation
packet at one common cut. Owned roles and main endpoints stay fixed.

The exact local controls verify 4,200 two-blocker conjugations.
The all-term replay checks **73,461** chart-visit products.
There are 66,914 incompatible span bounds, four incompatible rank
equations, 33 nonpositive rank uppers and six nonpositive mixed
rank and exact uppers. The other 6,504 placements restore the
removed equality and cannot release that scalar contact.
The overlap replay checks **eight** placements, with five
incompatible span bounds and three nonpositive rank uppers.
There are zero unresolved price cases in these scopes.

The full literal #7131 invoice reconstructs 110,400 paid and
22,308 productive calls, surplus 1424. The directed chart price
overgrants zero-rank paid deletion and free added ordinary work.
Its negative result does not establish a global coframe optimum.
No new native or application candidate reached the complete verifier.

## Reproduce

Use the CPython 3.12 standard library from a clean checkout.

```sh
python3.12 -B research/p104-two-blocker-exclusion/verify.py
```

The [registered replay](VERIFY.json) runs the same command.
The verifier checks the exact local identities and sampled full
intervals, compares the compressed enumeration with the exhaustive
signature set, and replays both directed price receipts and the
all-term journal. The omission and invalid-cut controls reject.
The [dependency receipt](DEPENDENCIES.json) uses stable paths and
authenticates both distinct two_blockers.py files. Duplicate keys
are rejected. A local prefix of the package location does not enter
either price receipt.

## Overlap and credit

The nearest archived [#6290 G20 screen](https://github.com/CrocSwap/integer-mult-bounds/pull/6290)
tests 765 local conjugations on a fixed route table. This package
uses the exact P104 #7131 word and checks separate commuting cuts
and changed chart assignments. The [pending causal-history work](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521)
keeps scalar order fixed and changes a helper transfer. The
[canonical Round 2 finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19531093)
records the earlier local checkpoint.

Rohan Arun supplied the [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113),
[#7124 output rechart](https://github.com/CrocSwap/integer-mult-bounds/pull/7124)
and #7131 composition. Dillona supplied the [#7130 pivot split](https://github.com/CrocSwap/integer-mult-bounds/pull/7130)
and the same-word export. This replay retains the exact native,
caller and compiler lineage credited in that export. It rebases
ToikY's earlier local chart solver and adds support-aware conjugation,
independent commuting cuts and the path-keyed replay. Prepared for
ToikY with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

Can a third incompatible scalar blocker change the constrained
paid profile on this exact word? Start with the planner's sparse
rank-one conjugation and its omitted-term control. Extend the
support-aware contact search by one crossing, cap the first pass
at 500 eligible placements, and require a positive directed paid
profile before lowering any nominee. Ownership contacts and
overlapping-support packets at independently moved cuts need
separate exact operator checks.
