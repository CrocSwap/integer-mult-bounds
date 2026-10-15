# Four R420 decoder escapes fail the inherited precision bill

**Scoped negative result, with explicit XOR witnesses. No new kappa.** At one
fully specified R420 decoder, no single restored helper shear saves an ADD.
Exactly four invertible three-helper basis changes save one decoder ADD,
including preparation and restoration. Each saves two ADDs in the complete
word after literal reverse cleanup. All four require a 105-bit positive-prefix
bill and fail the inherited native condition `64 F^3 B^2 < 2^104`.

This rules out a strictly cheaper, precision-admitted circuit in the class
defined below at this fixed prefix. It does not rule out a different prefix,
interleaved decoder, four-helper change, sharper precision argument, or a
different bit supplier. The exact upper bill failing its allowance does not
prove that the physical computation actually overflows.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/r420-triple-bases-seed01
```

Expected markers:

```text
PASS_R420_TRIPLE_BASES_PRECISION_BOUNDARY cases=13802880 escapes=4 admitted=0 columns=660 controls=9 no_new_kappa
PASS_R420_TRIPLE_LITERAL_RECORDS words=7 sparse_matrix_bounds=14 profiles=7 missing_COPY_rejected
PASS_REGISTERED_RESEARCH_PACKAGE
```

The unregistered equivalent is `python3 -I -B
research/r420-triple-bases-seed01/check_records.py`. It runs the same census,
checks the committed certificate, generates the seven literal words in a
temporary directory, runs the pinned exporter and compares independent exact
sparse-matrix invoices. Temporary files are removed on exit. The inherited
geometry checker uses assertions, so the primary verifier refuses `-O`.

## Exact scope and result

Base main is `e6f9716621f4e01fc190617934cdfaf072bd976f`. The accepted conditional
result at that base is `836330098538459/500000000000000000`, or
`0.001672660197076918`, from PR1094 with bit supplier PR589 on PR555. The
selected record, source manifest, assembly, batch1099 review and actual tuned
bit construction were followed. R420 is a historical PR543 word.

The starting decoder recipe is Adam Gall's PR1206, head
`3c0a3240035f1c71ef09251b7be7c4791da8157d`. [PREDECESSOR.json](PREDECESSOR.json)
retains its exact 34 shears, source certificate hash and extraction provenance.
The rebuilt predecessor has canonical word SHA256
`939b5d20013b3d3df09f56e7e153981d2a836e731af881163c53688cf8a84073`, matching
PR1206. The source bytes consumed from main have Git-blob and SHA256 pins in
[SOURCES.json](SOURCES.json).

One deterministic descent scores every one of 6,320 directed shears at each
step. `random.Random(1)` supplies tie keys in sorted helper-pair order. Eleven
positive steps reduce decoder cost from 250 to 236. The twelfth round certifies
zero strictly positive single-shear gains. This is a defined starting point
for the new class, not the contribution's novelty or a global optimum claim.

At that fixed point, choose any three of the 80 non-retained FULL-frame helper
operands. Insert an arbitrary finite sequence of unit XORs between those three
helpers immediately before the nine decoder reads, substitute the covectors,
then restore those helpers immediately after the reads. The existing 45-shear
preparation and its restoration remain literal and fully charged. The new
preparation and restoration cannot cancel or replace existing gates. No
target feedback, additional helpers, frame changes or interleaving is allowed.

The census covers `binomial(80,3) = 82,160` triples times every one of the 168
invertible binary 3-by-3 matrices: **13,802,880 cases**. The full gain histogram,
descent rounds and all four positive cases are in [CERTIFICATE.json](CERTIFICATE.json).
There are no untested triples or matrices. The four positive matrices have
unique shortest preparations and unique shortest restorations.

| Temporary helper triple | Chronological preparation, `a <- a XOR b` | Individual gains at fixed point | F | B | Bits |
|---|---|---|---:|---:|---:|
| 368, 375, 529 | 368 <- 368 XOR 375; 375 <- 375 XOR 529 | 0, -1 | 318897 | 4042946 | 105 |
| 375, 376, 434 | 434 <- 434 XOR 375; 375 <- 375 XOR 376 | 0, -1 | 293955 | 3780434 | 105 |
| 375, 376, 516 | 376 <- 376 XOR 375; 375 <- 375 XOR 516 | 0, -3 | 295145 | 3773682 | 105 |
| 375, 394, 529 | 394 <- 394 XOR 375; 375 <- 375 XOR 529 | 0, -1 | 318897 | 4031762 | 105 |

Each two-shear preparation saves five reads and pays four ADDs for preparation
plus reverse restoration. Each first shear has zero gain; after that first
shear the second saves one. Thus a descent requiring a strictly improving
single step misses every witness. Seed01 selects the second listed witness
for the mutation controls; it does not define a supposedly disjoint search shard.

| Word | Decoder ADDs including restoration | Complete ADDs | F | B | Bits |
|---|---:|---:|---:|---:|---:|
| Original PR543 | 321 | 26916 | 144651 | 2270064 | 100 |
| Frozen PR1206 | 250 | 26774 | 219001 | 2932970 | 103 |
| Single-shear fixed point | 236 | 26746 | 285521 | 3672062 | 104 |
| Each of the four escapes | 235 | 26744 | See above | See above | 105 |

The fixed-point bill is exactly `20086957128916201441054043730176`, less than
`2^104 = 20282409603651670423947251286016`. The smallest escape bill is
`23233029820240979440840951008000`. All four fail even this native allowance.
PR1206's Python wrapper applies the stricter `payload.bit_length() < 104`.
The fixed point fails that wrapper already. We report both predicates and
change neither one. No new supplier admission is asserted for the fixed point.

## Why the finite census covers arbitrary sequence lengths in this class

Let the preparation act on helper columns by `P`. For a decoder covector `r`,
substitute `r P^-1`; then `(r P^-1)(P h) = r h` for arbitrary incoming helper
dirt. In chronological shear order `(a,b)`, toggle coefficient `b` whenever
coefficient `a` is present. Restore in reverse chronological order. Decoder
destinations are excluded from the helper pool. This proves equality of the
complete A operator, including incoming retained-total dirt. Rebuilding C as
the literal reverse of A/B's non-target writes preserves H4.

Breadth-first search from the identity in the six-generator Cayley graph gives
the exact minimum length `d(P)`. Its distance histogram is
`{0:1, 1:6, 2:24, 3:51, 4:60, 5:24, 6:2}`. Enumeration of all 512 binary
3-by-3 matrices confirms that the graph reaches exactly all 168 invertible
ones. Reversing an optimal word proves `d(P^-1) = d(P)`.

For each triple, the nine-bit column signatures give the exact old and new
read counts. Therefore the greatest possible saving for a matrix P is
`old_reads - new_reads - 2 d(P)`. Any longer preparation or restoration costs
at least one extra ADD. The complete census finds precisely four positive
matrix cases, each with saving one and `d(P) = 2`. A longer realization cannot
save strictly. Enumerating all shortest paths confirms one preparation and one
restoration per positive case. Replaying these four unique realizations thus
settles every strictly improving finite word in the declared class. This is a
scoped computer-assisted exhaustion argument, not a proof of the full
multiplication theorem or a global circuit optimum.

## Verification and paid accounting

`verify.py` uses bit-packed column signatures and a matrix-column BFS.
`independent.py` imports no primary code: it enumerates all 512 literal binary
matrices, finds distances using permutations of the eight input bit patterns,
and prices each triple from its row-pattern multiplicities. The complete gain
histogram and every positive matrix agree, not only the best score.

All seven words pass eumemic's unchanged exact E8/frame/H1-H5 checker and
PR708's separate set-valued interpreter on all 660 source, target and helper
columns. Every ordered register-frame path agrees with the original. D,
scatter, B, COPY/ERASE roles, helper stock and frame data are unchanged.

`check_records.py` runs Dylan Crow's unchanged exporter. On each actual record
stream, an independent sparse integer-matrix replay computes every positive
prefix row sum in both orientations, with literal COPY and ERASE resets.
Its fourteen bounds agree with the scalar recurrence. It recounts every ADD,
all nine COPY/ERASE pairs and the entire paid histogram
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`, rank mass 5112. The exact bill is the
`64 F^3 B^2` formula in the pinned `columns_k.cpp`. Unchanged ranks mean no
moment or kappa improvement even if a different precision proof admitted an escape.

Controls reject missing restoration, wrong restoration order, missing decoder
substitution, endpoint-valid nonliteral cleanup, wrong preparation frame,
retained-total temporary storage, unpaid restoration, admitting an over-budget
word, an omitted improving matrix and a missing COPY in an actual export.
The original and PR1206 words are positive precision controls.

## Prior work and limits

Credit eumemic for PR543's R420 construction and checker, Adam Gall for
PR1206's ordered chains, and Sagar Thakrar for PR708's disjoint sharing,
separate replay and PR753's restored stars. PR748 by Chinmay Khaladkar changes
source cosets and D and has larger overall savings; we claim no circuit record.
PR1306's three-helper/three-target zero-frame feedback census concerns a
different operation alphabet and target map. Dylan Crow, DreamingOfClouds,
Zhihao Chen, Douglas Colkitt/OpenAI and the retained geometry, realization and
hosting predecessors retain their existing credit and notices.

The source word's all-size/compiler, common-label/mutable-source realization,
whole-call hosting, precision/tape and analytic assumptions remain inherited.
We did not run a C++ native multistage replay, complete hosted invoice, selected
cold replay, Lean proof or human review. Passing local identities is not
supplier admission. The failing upper bill is a limitation of this inherited
precision certificate, not a claim of necessary arithmetic overflow.

## Open next questions

The next useful question is whether an equal-Boolean-map rewrite of the frozen
preparation can reduce F/B enough to admit escape1. Begin with its exact chain
and invoice in the certificate. This changes the fixed-prefix premise; merely
enumerating more three-helper words does not. A new prefix would need its own
geometry, native and hosted evidence. [TASK.json](TASK.json) records this
question, relevance, first step and blocker.

Prepared for **Sagar Thakrar (@thakrarsagar)** with substantial **OpenAI Codex
assistance** in research, proof, implementation, verification and writing.
One agent; separate implementations are not independent human review.
New work is Apache-2.0, preserving predecessor licenses and attribution.

After production promotion of `xcheck.rref` (`research/r420-rref-production/`), the historical Fraction-era `research/e8-bit-r420/code/xcheck.py` digest is pinned as **provenance** only and is no longer a live VERIFY input.
