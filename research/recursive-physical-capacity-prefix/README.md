# Recursive numerical capacity in the actual physical caller

The historical physical caller keeps fixed numerical banks while it parks a
parent and reuses those banks for a child. This package independently proves
that its numerical allocation requests fit those banks at every finite
execution prefix, including the slot requested immediately before an allocator
guard. It does not assume a successful capacity-unlimited reference run.

The conservative bounds are **37,682 residue Words and 78 index Words**.
Consequently capacities 65,536 and 128 suffice, and the actual declared
capacities of 2^24 have ample room. These are sufficient bounds, not new sharp
constants. The proof includes the three child grants copied before parking,
four saved leaf-boundary copies, thirteen projected-coordinate indices, the
original parent slot identities, and arbitrary warm erased free-list order.

This is the archived **dimension-64, rank-at-most-42** caller from
CrocSwap/integer-mult-bounds#2809 and the physical bank implementation in #2899,
used by #3385 and the retained #3627 native lineage. It is not an admission of
the current #6030 geometry or selected supplier. **No new κ.**

## What is new

#2835 already proves the closed coefficient allocation prefixes. Its seven
numerical source files are byte-identical to those actually used here. #2845
and #5191 cover the original first-range Consumer and Node; #5191 explicitly
leaves changed recursive callers and physical suspended parents separate.

The new argument binds those local prefixes to the actual changed machine:
parent numerical Words are serialized and freed before the child starts;
restoration begins with empty banks and forces each original free slot before
calling the allocator. Recursion depth therefore does not multiply live bank
inventory. The requested slot is included before the guard, so a first numerical
inventory rejection contradicts the source-derived bound. It is not inferred
from measured peaks.

PROOF.md gives the all-size conditional argument. INVENTORY.json records every
AST statement and call in the named transition modules and three independently
extracted literal facts. This is a proof-bound source inventory, **not a general
Python resource analyzer or formal proof kernel**. The remaining local effects
are justified by the written proof and credited source lemmas.

## Reproduce

From the repository root, with Python 3.12 and its standard library:

```sh
python3 -B scripts/research_package.py --package research/recursive-physical-capacity-prefix
```

Expected scientific marker: `PASS_RECURSIVE_PHYSICAL_CAPACITY_PREFIX`.
The registered normal and optimized commands compare the complete typed
RESULT.json; missing or changed evidence is not regenerated. The separate
`verify.py --emit` option is author-only receipt creation.

The bounded evidence executes two actual selected recursive cuts
256 → 168 → 84 through PhysicalArena, with the actual high-field directory
producer. Cold and warm runs restore every original parent Word object, value,
head, slot label, stream, and successor. The warm case uses different labels.
Both runs use a declared 23-bit controlled child output and one family; they
do not execute a full selected GL64 payload or production-prime compilation.

Actual short-capacity controls fail at a pending index demand of 27 with
capacity 26 and residue demand of 15 with capacity 14. Those quota-only cuts
use prepared directory inputs outside their working banks. Other controls reject
extra live root residents, preloaded layout/trace/packet/child module aliases,
omitted structural fields, a wrong budget, and Boolean/integer substitutions.
Harness disposal after a forced failure is not a source rejection-recovery claim.

## Scope and remaining assumptions

The full-root contract requires empty working-bank live sets. Warm erased
backing and arbitrary free-list order are permitted; arbitrary extra live
outsider handles are not. Borrowed root inputs live outside those working banks.

The theorem stops at any error other than the fixed numerical register-inventory
guard on the two named banks. ScratchPool exhaustion, codec failures, other
resource errors, invalid representations, arithmetic margins, source semantics
and termination remain separate obligations. Fixed source identity and
numerical-neutral lookups/observers are explicit. The theorem does not erase
ancestor encodings or historical visited backing from a physical-space bill,
and does not derive a total native time/space tariff.

All inputs use canonical base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a` and are listed in SOURCES.json and
VERIFY.json. The source archives and all earlier packages are unchanged.

## Open next questions

1. Independently admit one remaining all-size noncapacity semantic or word-margin
   implication in this exact native source. The numerical quota is now a
   separate discharged clause, not a substitute for that implication.
2. Bind the complete physical action and visited-space invoice to the exact
   runtime, including preparation, encoded ancestors and retained erased backing.
   Live Word counts alone do not supply this invoice.
3. Establish an actual outer or selected-supplier transfer with its complete
   domain and bill. Historical geometry does not transfer merely by sharing
   terminology. TASK.json records first steps and blockers.

## Credit

Prepared for **@CubeJerry**, with substantial OpenAI Codex assistance in source
analysis, mathematics, implementation, independent checks and writing. Separate
AI review is not independent human or proof-kernel acceptance.

Jose Manuel/jmbarrancoml supplied #2809, #2769, #2899 and #3385; David Arias
supplied the logical caller in #2753; Ross Richardson supplied the numerical
prefix/backing work in #2831, #2835 and #2845; JoyboyBrian supplied #5191;
ywz65 supplied the parking controller in #2635. The source fixture in #2809 is
credited for its selected grammar setup; this package adds PhysicalArena,
actual directory production, nested cuts and pre-guard capacity controls.
The separate #3223 stock refinement, #5274 continuation estimate, #5356
retirement interface and open #4172 history/action coupling are not reproved.
All original source notices remain; new work is Apache-2.0.
