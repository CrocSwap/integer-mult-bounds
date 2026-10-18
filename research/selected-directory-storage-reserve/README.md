# Numerical storage allowance for canonical source directories

PR2569 leaves the numerical directory reserve open; PR2590 gives its exact
serialized field size and corrects its setup cost. Under their complete-fibre
and depth premises, this package proves an explicit **directory-only** allowance:

```
D < 2^-130 V       fixed-alphabet directory cells
4D < 2^-128 V      a fixed four-bit encoding
5D < 2^-127 V      directory term in the parking formula
20D < 2^-125 V     that parking term in the four-bit encoding
```

Here `D=1+CH(h+1)J` includes the initial LEFT cell and every serialized
delimiter; `V=CHR` is the **complete Boolean payload**. The result assumes
`q>=2^80`, `1<=m<=64`, `w,n,C>=1`, `R>=q^(2nw)`,
`17(h+1)<=20051w`, and a common minimal code width for a vocabulary of at
most 28,278 requests. The depth bound follows from the retained
`w=ceil(e^(17/10000))`, `2^(h+1)<=8e²` coupling.

[PROOF.md](PROOF.md) gives the all-input inequality. The large-q threshold
occurs in the main three-stage note; its historical depth exponent differs,
so we explicitly use PR2569's coupling rather than claim this note already
admits the complete caller. The arithmetic theorem does not test primality;
source-correct GL use additionally requires the predecessor's odd-prime and
chart premises. Large-integer fixtures are arithmetic checks only.

This closes a numerical **storage component** left open in
[PR2569](https://github.com/CrocSwap/integer-mult-bounds/pull/2569) and
[PR2590](https://github.com/CrocSwap/integer-mult-bounds/pull/2590). It does not
replace their producer, claim a runtime improvement, or establish a new bound
on kappa. The selected record is unchanged.

## Boundary and caller bill

The estimate applies separately to each canonical directory, including every
physical duplicate or empty old-prefix position. Summing it over simultaneously
live directories is valid relative to the sum of their complete payloads.
This package does **not** identify that sum with one current packet or root
payload. Both live parent and child directories must be counted.

The role markers, routing buckets, odometer/count tapes, controller, child-private
workspace, owned or borrowed dirty buffers, and restoration state remain separate
items. In particular the old `V+4v` or `5V+19v` reserve is not admitted unchanged.
An inactive directory adds the bounded `5D` term **plus** the predecessor's
separate role markers. The revision-5 family gate in [TASK.json](TASK.json)
therefore stops at this storage theorem; full caller expansion remains paused
until a complete lifetime and cost ledger is supplied.

## Evidence and reproduction

The unchanged producer is replayed on eight complete finite high cubes,
including repeated/empty old tuples and m=64/w=1. A separate literal serializer
checks all **189,338 returned symbols**, the returned counts, source preservation,
and producer numerical scratch restoration. There are 96 large-integer arithmetic
checks and 16 controls. Tiny q, a header-only fibre, unbounded depth and padded
codes give explicit failures of the numerical fraction when its premises are
removed. Serialization controls expose omitted delimiters, LEFT, or duplicate
positions. These controls do not refute either predecessor.

From the repository root with Python 3.12 and no third-party dependencies:

```sh
python3.12 scripts/research_package.py --package research/selected-directory-storage-reserve --check-only
python3.12 scripts/research_package.py --package research/selected-directory-storage-reserve
python3.12 -I -O -B research/selected-directory-storage-reserve/verify.py
```

The registered integrity check replays a Git-free export, rejects three source
corruptions before retained imports, and rejects a bool/int receipt substitution.
On Windows, set TEMP and TMP to a writable directory if the default sandbox
temporary directory is unavailable. [RESULT.json](RESULT.json) is deterministic;
`verify.py --write` regenerates it. [VENDOR.json](VENDOR.json) pins the exact external
source slice by commit, Git blob and SHA-256, and [SOURCES.json](SOURCES.json)
pins the main input. No huge-q producer, complete selected caller, full route,
or selected cold replay was run.

## Open next questions

1. What sum of complete payload volumes actually coexists during the selected
   recursive caller? Start with an explicit parent/child lifetime table, retaining
   frozen and dirty fields. This is required before using the component allowance
   against a root-level reserve; the complete caller is the blocker.
2. What explicit storage coefficients cover the separate route buckets and
   controller/count tapes? Start by binding each retained allocation to its
   lifetime and extent, then combine with the first ledger. This package measures
   only the serialized directory and supplies no free workspace allowance.

## Credit

Prepared by ywz65 with substantial OpenAI Codex assistance for the proof,
implementation, testing and review. PR2569 supplies the canonical producer;
PR2590 supplies the exact field-size calculation and setup-cost correction.
Their source authors and predecessor credits are preserved in
[NOTICE.md](NOTICE.md) and the unchanged vendor notice. New work is Apache-2.0.
