# Physical inverse-block boundary pages

This package implements the rounded inverse-block page and two-pass return
function of PR4186 on the actual protected physical Gaussian/word runtime.
Exact rational reference blocks become sequential rounded inverse/coupling
pages. The online solver uses encoded counts, literal signed records,
physical scalar-product children, complete ordered lower/upper passes,
row reversals, and explicit initialization/cleanup.

The multiplication kernel is a **charged classical fallback**. It executes
`2(2ceil(n/B)-1)ceil(R/B)B^3` signed scalar products. It does not implement
the proposed fast seven-product tape kernel or the caller's RHS field gather.
Those remain real adoption gates; this is a partial physical bridge and
provides no new kappa or complete Gaussian/Core admission.

Read [PROOF.md](PROOF.md) for the exact reference, padded batch-major ABI,
ownership, all-size refinement and complete cost ledger. The page producer
uses the pinned encoded rational Matrix/inverse implementation. Its setup
scans and bit complexity are separately paid. The runtime performs no host
matrix arithmetic, payload decode, random matrix lookup or inverse oracle.

```sh
python3.12 -B scripts/research_package.py --package research/physical-boundary-pages
python3.12 -B scripts/check_research_commit.py --package research/physical-boundary-pages --check-source-history
```

The independent Fraction oracle is confined to the checker. Actual setup and
online operations run under the retained `no_decode` guard. The fixtures use
three real/imaginary RHS columns, block widths two and four, a sharp scalar
half-bandwidth-three instance, incomplete rows and RHS batches, nonzero
borrowed dirty state, both ordered passes and owner reuse. Five real guards
reject nonzero padding, trailing pages, aliased page ports, metadata/page aliases and omitted earlier-block
couplings; a valid invocation follows the failed calls. Ordinary/optimized commands
are registered, with complete source/archive pins.

## Open next questions

1. Implement and price a fixed-tape seven-product kernel preserving this exact
   product/rounding ABI, including quadrant motion and parked recursion data.
   The classical kernel's B^3 count cannot justify a B^log2(7) boundary bound.
2. Bind the actual caller's RHS field gather to these explicit batch-major
   records, retaining incomplete rows/columns, all spectator data and return
   order. Its movement is not supplied or assigned zero cost here.
3. Name the exact reference used by the final producer. Existing Preparation
   uses LU(round(S)); bounds against the original S require the separate
   perturbation term. This module does not install itself into that caller.

## Attribution and scope

Base canonical main `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, priority7.
Initial overlap covered320openPRs at06:50:51UTC,4130Discussion records at
06:51:43UTC and all6710trackednotes. This identifies relevant prior work;
it does not search arbitrary diffs or unpublished work or certify novelty.

Credit Jose Manuel/jmbarrancoml PR4186, its numerical bounds and physical
Gaussian core; Vlado Vojdanovski's retained block proposal and prototype;
Cinna Davis PR4100 and the Gaussian/Harvey–van der Hoeven and physical
word/ring/runtime lineage. Frozen source files and archives remain unchanged.
Prepared for JoyboyBrian with substantial OpenAI Codex assistance. No
independent human or proof-assistant acceptance claimed. Apache-2.0.

## The old page ABI is a discriminating control

For the same exact L/U reference and P=6, the retained scalar BandedSolve
returns second entry -13/64 on the stated four-row RHS fixture. The new
literal inverse-block function returns -3/16 = -12/64. Both physical
programs are executed; the independent oracle explains the different
rounding sites. This is a required ABI distinction, not a defect claim
against the old solver. Full values and the source-bound witness are in
RESULT.json and PROOF.md section6.
