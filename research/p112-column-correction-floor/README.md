# Arbitrary one-column free corrections retain COPY cost 64

**Scoped masked-decoder obstruction; no new κ or supplier.** On the fixed
P112 coordinate decoder, mix any two coordinate terms and one free correction
confined to a single column by any GL(3,C) change of factors. The correction
may have arbitrary complex amplitudes on **any subset of all 52 odd neighbors**
of that column. Its three replacement COPY ranks always satisfy

`r1^q+r2^q+r3^q >= 2*8^q`, for every `0<q<=1`.

The other six terms retain rank eight. The complete COPY floor is therefore
**64**, and the complete COPY power floor is **8*8^q**. Identity mixing attains
both for every allowed correction. The theorem covers all 28 coordinate pairs
and 112 singleton sites; transposition gives arbitrary one-row corrections.

This removes PR1375's <=23 support restriction on the nonsingleton side. Its
old per-child conclusion cannot simply be extended: the published 24-row
boundary, with cancellation-aligned amplitudes, gives replacement ranks
**(7,8,7)**. Only one child has rank eight, but charging all three still prevents
a saving. The proof closes the pure-factor branch through its actual COPY
charge and the coupled inverse-factor identity. Concurrent PR1432 already
supplies the fixed 24-row result and example; PR1460 handles arbitrary nonzero
rectangles at pair (4,6). This package provides an independent proof and full
certificate for every pair in the one-row/one-column domain.

## What is proved and checked

[PROOF.md](PROOF.md) gives the quantified complex proof and complete optimistic
COPY comparison. It changes the eight-term all-pairs hypothesis to this
explicit masked nine-term family. All added physical overhead is granted zero
for the rejection screen. Width, normalization, multiplicity, the other six
terms and separate COPY billing are fixed; changing those is outside the result.

Two separately represented engines check every finite geometric premise:

- 140 support strata over all 28 coordinate pairs and 71,540 binary functional
  evaluations, including complete ordinary and free-compatible weight spectra;
- all **15,680 even-neighbor survivor spans** (6,272 of rank seven, 9,408 of
  rank eight), plus 15,680 direct singleton-erasure spans;
- all 700 ordered within-pair support costs and the exact 24-row boundary;
- thirteen Gaussian-rational complete nine-term examples, checking **163,072
  scalar entries**, both correction orientations, nonreal factor changes, full
  52-row supports, the pure-factor branches and zero correction.

The primary geometry comes from the pinned PR845 file. The second engine
builds Euclidean E8 roots and a full Gram-derived binary evaluation code,
without importing either geometry implementation. It rechecks every finite
receipt field. The quantified proof is written; examples do not enumerate
complex matrices. [EXPECTED.json](EXPECTED.json) binds the complete result.

## Reproduce

Python 3.12+, standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/p112-column-correction-floor
python3 -I -O -B research/p112-column-correction-floor/verify.py
python3 -I -O -B research/p112-column-correction-floor/independent.py
```

The registered replay includes the complete computation and seven semantic
test groups. `verify.py --write /new/receipt.json` computes a new receipt and
refuses to overwrite existing output. Default replay checks the stored receipt.
Source, receipt and mathematical guards remain active under `-O`.
[VALIDATION.md](VALIDATION.md) records the tested environments and limits.

Two live inputs have exact Git/SHA256 pins in [SOURCES.json](SOURCES.json):
the retained geometry and PR968's model proof. The selected record and task
catalogue are historical provenance at
`410026dc5513b87db92ae98571d1d5984c69a983`. No selected or frozen file changes.

## Task, overlap and credit

The one OS draw `149d7583c4efedede03fc432c003699f` selected
`complex-mechanisms / complex-masked-decoder`, scope key
`2a6f2c726b78f9ae7d26`, priority revision 2. The required PR1077 starting
example passed. [TASK.json](TASK.json) records the refined scope, and
[Discussion1434](https://github.com/CrocSwap/integer-mult-bounds/discussions/1434)
records the claim and result. [OVERLAP.json](OVERLAP.json) records current heads
and search coverage; absence of a match is not a novelty certificate.

Submitted as [PR1468](https://github.com/CrocSwap/integer-mult-bounds/pull/1468).
Mathematical implementation commit:
`725cc996905139e6ba81053c78e248eb2e29608f`; the subsequent submission-reference
commit changes only this README and TASK metadata.

- **commdata2338 / PR1375**, head `4a533aff2a7a87c9b36e077a31774b332a7f64bd`:
  the small-rectangle theorem, five support strata, erasure facts and 24-row
  free-boundary handoff. The new result removes the size cap when the other
  side is a singleton and accounts for the pure-factor branch.
- **Cinna Davis / PR1373**, head `3eaef3e4427068b33847dc1147c8a2e5709a970e`:
  the arbitrary-rectangle three-active-product obstruction for pair (4,6).
  That branch and the survivor method are credited, not claimed as new.
- **Arham Tahir / PR1331**, head `f08b698cc2bd74e2425486728a008e531fc35f0e`:
  one-coordinate predecessor and handoff. His Discussion1360 independently
  considers all nine factor changes of a singleton completion.
- **Hanson Sun / bbMisk**, concurrent
  [PR1432](https://github.com/CrocSwap/integer-mult-bounds/pull/1432), head
  `4bcc49e3f4041018b0607da46a87d8928a6e0fd0`: the fixed 24-row boundary with
  arbitrary amplitudes and the same (7,8,7) example, independently reproduced
  here. [PR1460](https://github.com/CrocSwap/integer-mult-bounds/pull/1460), head
  `8d53667d9bb09d9b1ffb0f865b5c8dc230eb02f6`, gives an independent
  compensation-support argument for arbitrary nonzero rectangles at (4,6).
  These results were found in the final refresh; neither is a proof dependency.
  A further Discussion1316 claim now investigates two-column corrections.
- **Mihir Srivastava / PR845**, retained exact geometry; **DreamingOfClouds /
  PR717, PR446, PR595**, decoder and separate-total cost model;
  **GamingPuzzled / PR620**, coordinate COPY64 decoder; **themilkman216 /
  PR968** and **woklerx / PR1077**, original floor and complex-field starting
  example. PR1180 already covers factor-linear overcomplete all-pairs decoders;
  this does not repeat that theorem.

Only the retained main geometry is imported. No pending predecessor theorem
is assumed. New work by Gareth Davidson (@bitplane), with substantial OpenAI
Codex assistance in mathematics, both implementations, tests and writing.
Apache-2.0; no subagents or independent human review.

## Open next questions

**Transport the arbitrary-rectangle proof between coordinate pairs.** PR1460
treats nonzero rectangles at (4,6), and a concurrent Discussion1316 claim tests
two-column corrections. Before repeating those searches, derive exact
automorphisms preserving the punctured frame and binary pairing that connect
the coordinate pairs, and check the compensation hypotheses under transport.
The blocker is a proved transfer of the whole contract; the present certificate
itself only establishes the one-row/one-column domain.

**Three or more mixed coordinates.** Classify one three-coordinate support
space, then derive the corresponding GL4 coupling bound. The five-stratum proof
here does not cover that class. New survivor bounds and a complete COPY screen
are prerequisites to physical synthesis. Structured questions are in TASK.

No physical gathering, legal frame itinerary, restoration schedule, owner or
hosting admission, native replay, selected cold replay, precision/tape proof,
all-size compiler or analytic transfer was checked. Different punctures and
shared-copy prices also remain outside scope. No improved multiplication bound
is claimed.
