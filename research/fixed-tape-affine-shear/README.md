# Runtime affine shear on nineteen literal tapes

One fixed finite program realizes

```
(p,x,g,y,z) -> (p,x,g,y+c*x+C mod Q,z)
```

and its inverse for **all** positive binary-encoded `P,Q,G,S`, `0<=c,C<Q`,
and every Boolean payload of volume `V=P Q^2 G S`. Each generic direction has
**877 local microinstructions, nineteen tapes and seven symbols**. The complete
bounds are **1024V transitions and 64V visited cells**, including conversion,
coefficient loops, cyclic reset, payload copying, every rewind, scratch erasure
and head return. Source and descriptors are preserved; output is separately
owned. Nonunit and zero coefficients are allowed. These are conservative
physical bills, not measured speedups or optimized constants.

The actual [PR4989](https://github.com/CrocSwap/integer-mult-bounds/pull/4989)
frame506 route includes the ordered shift from high coordinate0 to coordinate3
with rational coefficient1/2. Its multiplier modulo `Q=q^(w-1)` is `(Q+1)/2`,
which grows with width. Repeating that many whole unit-shear invocations would
lose a growing factor. The new program advances unary split positions locally;
all Q iterations together pay only O(Q^2), absorbed by the full pair volume.

The retained **linked half program** additionally computes its actual binary
coefficient descriptor from Q by a literal copy/ripple increment and erases
that owned descriptor after use. Preparation is not a free host scalar inverse.
Its total remains inside the same `1024V/64V` bill. General runtime c,C are
supplied descriptors; preparing other rational coefficients remains a caller
cost. No ordinary-interchange oracle, arithmetic callback, nonlocal tape access
or extent-specific program is used.

## Proof and source boundary

[PROOF.md](PROOF.md) gives the all-size invariant, termination, complete
transition ledger and visited-space proof. The advancing offset may have any
period: a separate Q counter prevents early termination when c is a nonunit.
A prefix makes exactly c complete cyclic resets across Q x-values. All buckets,
markers and counters are physically cleared, including cells previously erased.

This extends David Arias's [PR2776](https://github.com/CrocSwap/integer-mult-bounds/pull/2776)
fixed unit shear and Charles Bethin's fixed unit-carry kernel. Their split/merge
method, local instruction vocabulary and paid counters retain full credit.
The actual matcher generator, serialized program and interpreter are pinned:
source high-coordinate address0 precedes address3, and both fields range over
the complete Q-element high fiber. Arbitrary intervening fields are the G
spectator extent. The all-size proof covers that interface; finite executions
compress the huge source spectators and do **not** materialize the full native
high matrix or admit the whole matcher route.

Unimplemented native/raw-body/ordinary callees, unit_scale, reversed-field
routing, low-type cache/ROW padding and whole-bank ownership remain explicit.
Installing this source-preserving, owned-output kernel in the original
in-place caller still needs a paid source-retirement protocol. Complete P3
stock, tape, precision, recurrence and threshold obligations remain open.
No selected frontier or kappa is changed.

## Evidence and reproduction

The separate dense table interpreter imports no assembler or predecessor
execution code; its direct **gather** coordinate oracle knows no split traversal.
A second sparse interpreter executes the same saved tables and matches every
step/span/transcript observation. The main bounded checks cover:

- 610 directional executions and 38,850 payload bits: every c,C for Q<=8,
  all one-hot columns at Q=3, nonunit Q=6,c=2, translated origins and nontrivial
  prefix/gap/suffix layouts.
- Ten complete linked half calls, plus 107 exact descriptor cases including
  long binary carry chains through 40-bit Q. Zero, even and too-small half
  moduli reject. These descriptor checks do not execute their large payloads.
- Malformed extents, out-of-range/noncanonical coefficients, occupied scratch,
  nonlocal motion, wrong orientation, lost coefficient/offset, corrupt output,
  retained scratch, changed source and an endpoint-preserving extra-work mutant.

The new lost-coefficient control initially used x=0 and could not distinguish
that mutation; it now uses x=2. The payload mutant initially changed only an
unreached bucket write; it now corrupts both output branches. These verifier
corrections are retained in the substantive commit history. They are not
claimed as defects in the mathematical source program.

From the repository root, standard-library Python3.12:

```sh
python3.12 -B scripts/research_package.py --package research/fixed-tape-affine-shear
```

Four bounded registered commands run sparse/dense engines normally and under
`-O`; explicit guards remain active. `verify.py` is read-only. Explicit
`--write` regenerates the canonical receipt and gzip table; verification compares
the decoded complete instruction tables, not gzip container bytes. The literal
generic, linked half and descriptor tables are all in `TABLE.json.gz`.
`SOURCES.json` binds live inputs by SHA256 and Git blob; catalogue and selected
record are historical provenance. These source checks are not scientific
acceptance. No Lean, Docker or unrelated historical suite is run.

Validation on CPython 3.12.2 / macOS 27.0 arm64: all four registered modes
pass. Committed-byte and source-history checks pass for 21 files; official
export integrity and all four direct modes pass again with Git absent from
PATH. Actual exported source, table and typed-receipt changes reject, including
`schema_version: 1 -> true`; every original exported byte is restored. A
separate read-only AI peer independently recounted the transfer/comparison,
phase, cleanup, space and half-preparation ledgers and found no blocker.
This is not independent human or scientific acceptance.

## Open next questions

1. Bind one complete actual route's source/output banks and source retirement,
   including shared scratch lifetimes. This is needed to install the kernel;
   full physical ownership and native/ROW protocols remain the blocker.
2. Physically lower one actual unit_scale or reversed-field primitive, with its
   full all-width tape bill. The current program does not cover those positive
   costs. Begin with the source coefficient and explicit owner/tape contract,
   rather than extending this same coefficient grid.

[TASK.json](TASK.json) records the refined card and structured questions.
Canonical [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4945#discussioncomment-19139354).
Base: canonical main `bee95ce88f9f19802f0613f92838895cd0e14a1f`, priority7.
Entry overlap covered310open PRs (06:05:59UTC),4096Discussion records
(06:06:48UTC) and all6690tracked local notes on October23,2026. These cached
metadata searches do not cover arbitrary diffs or unpublished work and are not
a novelty certificate.

## Credit

David Arias / PR2776 supplied the finite machine, counters and copy/erase macros;
Charles Bethin supplied the unit-carry successor and explicit open carry
question. Jose Manuel and the retained upstream authors supplied the selected
stream reduction and ordered-affine method. ai-nanachi #4760/#4814/#4326,
Chris R / Clear1nsight #4957, JoyboyBrian #4989 and the retained native,
ROW/ordinary/stock/routing/precision/tape lineage supply the source boundary.
All predecessor files remain unchanged. New runtime controller, literal half
preparation, linked owned cleanup, proof and checks prepared by JoyboyBrian
with substantial OpenAI Codex assistance. Apache-2.0. No independent human or
proof-kernel acceptance is claimed.
