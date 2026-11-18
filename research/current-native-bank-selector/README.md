# Charged selection and return for current native banks

This package proves a local two-head bank-selection theorem and binds it
to the owned MOVE at clock 88263 in
[PR #7663](https://github.com/CrocSwap/integer-mult-bounds/pull/7663).
It adds the travel to and from a private bank to the retained reset cost,
and proves that all other parent and child cells stay unchanged.
No new kappa or complete recursive allocator is claimed.

The exact source head is `b81f40997de646de30749d367484d89e59fc3013`.
The reconstructed word has SHA256
`f95eabd1734c7a74f58428cb12f261a81032bef01aed78c8147a4e4f90636939`.
The source executes `MOVE 1510,477,1090,True` during lifetime ordinal 35,
with 34 parent lifetimes live. A direct binary span check confirms the
nested rank-four boundary. The retained native adapter contract supplies
its canonical post-adapter view; those adapters are not replayed here.

## Result

[PROOF.md](PROOF.md) gives the all-size position and frame-condition proofs.
[RESULT.json](RESULT.json) records source binding, literal charges and
controls. [controller.py](controller.py) uses only guide reads, payload
writes, unit moves of two distinct heads and finite control transitions.
It does not jump to a bank address.

If bank k has L payload cells and two guards, selection, complete reset
and return cost exactly `8k(L+2)+9L+14` in those physical/control units.
The complete 234-lifetime plan, placed after 234 retained parent banks,
has reset overhead `1316484L+2631096`. Guide construction, all numerical
child work, adapters and complete recursive allocation have separate costs.
The general formula for P parent and C child banks is
`C(16P+8C+10)L+C(32P+16C+12)`.

In the canonical view, parent shape `(R,9f,W)` and child shape
`(R*2^(5f),4f,W)` have the same complete records in the same order.
The proof gives an inverse address map. Matching extent alone does not
establish that fact. All banks, including inactive historical homes,
remain resident. Data and immutable guide capacity is `2(P+C)(L+2)`
cells, with positive fixed control and preparation costs in addition.

The source-bound fixture reserves 234 parent and 234 child slots. It
checks every INIT and CLEAR in the native lifetime chronology at L=5.
A separate R=f=W=1 fixture uses L=2560 and 1199016 cells on each tape.
It executes both resets at the first and last child slots, then checks
every other cell and all guards. A confined write-only borrower checks
that parent slot 35 can change while all other parent cells stay fixed.
This borrower is a frame-condition witness, not a Gaussian transform.

The three shape checks cover 263680 complete addresses. Five controls
detect a same-size wrong format, missing spectators, aliased ownership,
a shortened guide and an omitted return. The proof quantifies over all
stated shapes and arbitrary old private symbols; finite cases supplement it.

## Scope and remaining obligations

The source's reset and guide functions are copied unchanged. This work
adds a two-head selector, a precise travel charge and a local composition
proof. Correct complete guides, distinct slots, the same root bit width
and canonical adapter order are premises. The guide producer has a
retained constructive source bound; its full physical compilation is open.

The 234-slot child tuple represents one raw native lifetime plan. It is
not the inventory of an entire compiled recursive child. The general P,C
formula is available once that actual inventory and schedule are supplied.
The complete occurrence tree, numerical child, root format delivery,
adapter movement, private auxiliary stock and common whole-algorithm
tariff remain outside this result. The five framework assumptions and
the selected frontier are unchanged. The full source application and
selected multiplier were not replayed.

## Reproduce

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/current-native-bank-selector
```

Normal and optimized isolated commands must each print
`PASS_CURRENT_NATIVE_BANK_SELECTOR`. The runner must print
`PASS_REGISTERED_RESEARCH_PACKAGE`. Normal verification writes no files
and needs no Git, network or solver. `--write` creates only an initial
receipt and refuses to replace an existing one.

## Open next questions

Export one actual finite compiled parent/child owner map, including every
raw occurrence and all caller and primitive workspace. Then instantiate
the general bank-count and schedule formulas. Separately compile and
charge the guide producer through production, head return and retirement.
[TASK.json](TASK.json) gives the exact scope and stop boundary.

## Credit

Ali Romman supplied the PR7663 construction and its reset/guide source
with substantial OpenAI Codex assistance. CubeJerry supplied the selected
primitive and prior typed reset in
[PR #7586](https://github.com/CrocSwap/integer-mult-bounds/pull/7586).
The exact candidate retains Clear1nsight, DreamingOfClouds, SYLforge,
Rohan Arun and the selected predecessor credit in [source/NOTICE](source/NOTICE)
and its copied notices. [VENDORED.json](VENDORED.json) authenticates each
copied file. The main selected proof is a declared input in
[SOURCES.json](SOURCES.json).

Ali Romman directed this new selector, cost proof and verification with
substantial OpenAI Codex assistance. New work is Apache-2.0. Canonical base:
`e54523517d0f03e58352e647c403a5af3e525a57`.
