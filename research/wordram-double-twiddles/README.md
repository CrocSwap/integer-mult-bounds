# Save 930 further instructions at constant-two twiddles

A source-bound program-refinement proof with finite corroboration. In the fixed
fused `s=t=256`, `n=512` bounded Word RAM multiplier, replace 31 constant-two
butterfly reductions **after** Nick Petalas's [#6802 unit pass](https://github.com/CrocSwap/integer-mult-bounds/pull/6802).
The new pass preserves complete memory, including TEMP, and saves exactly
**930 executed instructions on every admitted input**, conditional on the
credited producer/setup/range/control premises. Static length drops by 1,395,
from 435,650 to 434,255. These are additional ISA counts; #6802's existing
47,523 unit saving is predecessor work.

[PROOF.md](PROOF.md) supplies the written full-domain local identity and
fixed-template block simulation. This is not a new multiplication theorem,
global instruction optimum, all-length optimizer or proof-kernel acceptance.
Only this new scoped package is added; original sources remain unchanged.

## Exact boundary and cost

Use David Ganz/Dugongue's [#5466](https://github.com/CrocSwap/integer-mult-bounds/pull/5466)
64-bit modular Word RAM ISA and modulus 65,537. Its bounded multiplication,
residue/setup, executed-initialization and traversal contracts are cited
premises, not independently re-audited. There is no invented shift/div/mod
instruction or native arbitrary-integer multiplication tariff.

For each eligible residue b in 0..65,536 and coefficient cell containing 2,
the new body retains MUL and the final SUB/BLTZ/conditional copy. The 15 higher
threshold groups always branch past their copies. Four static instructions
replace 49; `3+delta` executed instructions replace `33+delta`, saving 45/30.
Both leave VALUE equal to 2b modulo p and TEMP equal to **unreduced `2b-p`
modulo 2^64**, independent of incoming VALUE/TEMP dirt. In particular TEMP is
not always reduced VALUE minus p. Every exterior word agrees at block exit.

Complete write inventories bind one initialization, adjacent doubling and final
self-clear. Exact macro/alias/lifetime checks and a once-applied old-to-new
entry map preserve the retained last branch and reject surviving entries into
removed interiors. Source execution/initialization hypotheses are necessary;
the matcher does not certify arbitrary instruction lists from syntax alone.
All setup, literal constants, thresholds, unaffected work, inverse normalization,
carrying, clearing and charged halt remain. No address/liveness pass is composed.

## Observed fixed-template certificate

The first new diagnostic passed on CPython 3.12.14 in **4.108 seconds**, with
**220.625 MiB** maximum host RSS, under its 120-second/256-MiB forecast. This
is checker resource use, not a physical workspace bill or elapsed-time speedup
against a predecessor. All 20 package files retained identical before/after hashes.

The exact emitted source has 31 eligible sites, all in the inverse transform:
16 at width 32, 8 at 64, 4 at 128, 2 at 256 and 1 at 512. The coefficient is
cell 23590; its post-unit writes are at 288639, 288640 and 431300. Every site
records original, post-unit and new PCs, stage/block/exponent, operands and
lifetime. Pointwise products and inverse scales are excluded.

Normalized-JSON program SHA256 identities:

- Original producer: `d48881159830fd17c13a244816999136dc1e1ef23f7ee40986ff2e1e546b7534`, 507,701 instructions.
- Post-unit comparison: `2f8c8aa0c2c2cf0d5c8f8d4d6b1ce9a0d423598801d0a2320dee8eba1bbb4559`, 435,650 instructions.
- New program: `43a0fe618b3a03cf6e0550ce0daa76047b5f34c9fdb2e2cdc2f73f8886537928`, 434,255 instructions.

The unit count 1,533 is regenerated for source binding. Its associated 47,523
executed saving is the credited theorem's value, **not** a newly executed
original-versus-post-unit whole-program comparison. New whole cases compare
post-unit P1 with new P2.

## Finite corroboration and reproduction

The new checker executes literal source-ISA programs for all 65,537 local
residues, with one dirty scratch/exterior pattern per residue, complete memory
and write-frame comparison, independent VALUE/TEMP oracles and exact 30-step
deltas. Arbitrary dirt/exterior preservation rests separately on the written
write-frame proof. The local transcript SHA256 is
`c8e7dc7b9ae30a07444fb714f984d2fe0b0ec315abbbdbc6fd84bbc099e7b236`.

Three complete fixed-template dirty-memory fixtures passed:

| Fixture | Post-unit steps | New steps | Additional saving |
| --- | ---: | ---: | ---: |
| Zero | 314,002 | 313,072 | 930 |
| Maximum digits | 343,556 | 342,626 | 930 |
| Declared deterministic patterns | 342,989 | 342,059 | 930 |

Each checks complete memory/write sets, integer multiplication, cleanup and
operand/exterior preservation. Eight controls pass: six exact-reason structural
rejections (coefficient 3, missing self-clear, threshold, internal branch,
external interior entry, scratch alias), a VALUE-correct/TEMP-wrong execution,
and an actual difference outside the admitted residue domain. The latter
illustrates a necessary premise; it is not rejection of a valid producer input.

```sh
python3.12 -I -B research/wordram-double-twiddles/verify.py
python3.12 -I -O -B research/wordram-double-twiddles/verify.py
python3.12 -B scripts/research_package.py --package research/wordram-double-twiddles
```

The two registered commands have 120-second caps and no dependencies beyond
Python 3.12's standard library. The deterministic stdout receipt binds all
actual package files, exact sources, all 31 sites and fixture/control evidence.
Normal/optimized, committed/exported and hosted outcomes are later delivery
observations and must be checked separately. No runtime Git/network/subprocess
or installation is used. `VERIFY.inputs=[]` means the nine runtime/proof inputs
are package-local, not that no files are read.

The authenticated original builder, ISA interpreter and unit transformer
**actually executed** as credited components. The original broad #6802 verifier
was fetched/read inertly in preparation and was not imported/run. This is not
code-disjoint end-to-end verification. No nine-template census or exhaustive
256-digit operand/length-pair test is claimed. Related source-aware static
proof/code reviews found no blocker; no blind, human or kernel acceptance follows.

## Provenance, credit and limits

[TASK.json](TASK.json) retains the complete canonical formal-interface-lemma
card, explicitly CHANGED/partial: no Lean proposition is formalized and its
original selected-interface gate is unmet. [SOURCES.json](SOURCES.json) binds
canonical provenance; [SOURCE-PINS.json](SOURCE-PINS.json) authenticates nine
local bodies, 51,318 bytes, before imports. Imported module paths must also
match their expected local files. LICENSE/NOTICE and the additional original
source notice are retained. [CREDITS.md](CREDITS.md) distinguishes #6802,
#5466, separate #5886/#6435, tcslib/Anthropic-PBC, FastPoly, CatCrypt, mpfx
and the original compiler/multiplication lineage.

Substantial source-aware OpenAI Codex proposal, implementation, proof/code
challenge, overlap and metadata assistance is disclosed. Source/provisional
recipe exposure before claim and pre-first provenance/import-origin corrections
are preserved. The first receipt binds initial metadata; later metadata-only
updates must not be described as its original document hashes.

CPython dynamic allocation, pinned module imports and emitted literal labels
are scoped Power of Ten deviations; no fixed-allocation implementation or
static-analyzer certification is claimed. Host generation is separate from
the emitted ISA bill and does not establish an all-size paid compiler.
Native/physical word-to-bit costs, selected caller/consumer conversion, routing,
storage, precision, ownership/restoration and the complete supplier invoice
remain open. All five selected assumptions remain; no new kappa/frontier,
supplier/adoption change or merge is claimed. Stop at this first verified gain.

## Open next questions

1. **Bind one selected consumer with a complete bill.** Name its operand sizes,
   word/bit tariff, conversions, constant delivery, layout, precision and
   restoration/ownership. The bounded ISA delta cannot supply that contract.
2. **Install only the exact scoped refinement after review.** Retain the source,
   site/lifetime/control evidence and post-unit baseline; first review the
   emitted fixed template. Other coefficients, liveness composition, asymmetric
   lengths and global optimality require separate claims and evidence.
