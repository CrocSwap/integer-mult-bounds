# Retained numerical arena backing

PR2825 bounds occupied numerical content in the selected first-range BIT caller,
but explicitly excludes erased backing. For the unchanged PR2697 `words.Arena`,
this package proves the exact high-water identity

```
allocated slots after a completed operation = max(entry slots, peak live slots),
retained Word-array cells = (allocated slots + 1) * (digit width + 2).
```

The extra slot is the permanent template. The two extra cells per Word include
LEFT and the RIGHT position, even after erasure. Two distinct arenas retain
their own historical peaks, which may occur in different phases. A literal
counterexample has maximum simultaneous complete live-cell content 21 but
retains 31 cells. Warm-entry history also matters: identical empty live sets
can retain different numbers of blank arrays.

Conditional on PR2825's successful first-range caller contracts, let `L_R,L_I`
count **all** live entry Words, `K_R,K_I` the already allocated entry slots,
and `b_R,b_I` the fixed digit widths. The resulting bound is

```
T <= (max(K_R,L_R+37672)+1)(b_R+2)
       + (max(K_I,L_I+41)+1)(b_I+2).
```

This counts retained numerical arrays, including blanks and markers. It does
not include Python metadata, other tape categories, physical mapping or movement.
The original phase maximum remains valid for its occupied-content measure;
it must not be substituted for the two retained historical maxima.

[PROOF.md](PROOF.md) gives the all-parameter source induction, the pending-new-
Word qualification inside allocation, and a capacity replay theorem requiring
an independently legal trace or successful reference run. PR2825's successful-
call bound alone does **not** discharge that premise or prove unconditional
actual-caller capacity admission. The fixed-size rectangle example is a legal
allocator relaxation, not an actual `Consumer.apply` execution or a claim of
composed sharpness. There is no new kappa, supplier or full-reserve result.

## Sources and reproduction

Scientific runtime: Jose Manuel/jmbarrancoml's
[PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697),
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. The Word source and notice are
byte-identical exports through Ross Richardson's
[PR2825](https://github.com/CrocSwap/integer-mult-bounds/pull/2825),
`b553e912bcddef550d9fae6033041ff683399ebe`. Its proof is retained as an explicit
conditional premise, with original relative links referring to that source PR.
`INPUTS.json` gives exact original/export paths, Git blobs and SHA256 hashes.
The source loader authenticates and compiles bytes directly, bypassing caches.

Python 3.12 or later; standard library only:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/selected-numerical-arena-backing
python3.12 -I -O -B research/selected-numerical-arena-backing/verify.py
```

Ordinary replay is read-only and compares the complete typed `RESULT.json`.
`verify.py --emit` prints fresh results without replacing the receipt. The
primary finite exhaustive domain is the complete reachable zero/free state
quotient at capacities 1..5 and digit widths 2,5: 1,078 states and 2,106 legal
edges, including all free-slot orders and ten inventory-guard checks. Fixed
literal/copy/rollback, construction/write, entry-history and sequential-phase
fixtures provide different failure modes. A full-sized **synthetic** rectangle
schedule reaches 37,672/41 extra historical slots while restoring nonzero parents.
Nine optimized controls cover erasure, reuse, LEFT/template omission, inventory,
source hashes, effective stale bytecode and typed receipt substitution.

[INDEPENDENT.md](INDEPENDENT.md) and `independent.py` supply a separate AI
derivation/checker. Finite checks corroborate the written proof; they do not
formally prove arbitrary histories or execute the full selected caller. Final
commands, interpreter versions and independent coverage are in `VALIDATION.md`.

## Scope, overlap and credit

The fresh picker suggested formal-interface/moment checks. We took the released
PR2825 backing handoff under priority revision 5 and explicitly narrowed the
selected-stock card to this numerical component. `TASK.json` records source
freshness, exact original card, overlap coverage and remaining obligations.
The canonical scoped claim is in
[Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18961690).

Credit Jose Manuel/jmbarrancoml for the allocator/caller and retained lineage;
Nick Petalas for PR2759/2770/2778/2781/2801/2815; Arham Tahir for PR2796;
Ross Richardson for PR2810/2821/2825; David Arias for the separate PR2753
recursive caller; and ywz65 for the physical parking lineage. PR2758 counts
different continuation tapes. Jose Manuel's PR2769 numerical codec and active
PR2809 physical-controller work remain separate and are not replaced here.
The unchanged `vendor/NOTICE.md` retains source-specific attribution.

New work by Ross Richardson with substantial OpenAI Codex assistance, including
a separately implemented math-storage-lifetimes AI audit. Apache-2.0. No
independent human review, formal-kernel proof or hosted-CI pass is implied.

## Open next questions

1. Join the actual numerical, payload/count/key, program, continuation and
   bookkeeping inventory at common caller cuts, then bind it to physical banks
   and movement. Start with one actual PR2697 caller entry's K/L/widths. The
   missing representation/cost bindings block a complete reserve claim.
2. Establish every inherited live-demand bound on all noncapacity-valid
   prefixes, including the pending allocation, before assuming success. Start
   at the first would-be inventory failure in each coefficient/caller proof.
   This is needed for unconditional capacity admission; successful-call bounds
   alone and the allocator replay theorem leave that premise open.
