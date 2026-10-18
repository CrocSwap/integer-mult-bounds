# Anticipatory dirty borrowing on the selected complex word

**Verified local component; no admitted supplier or new kappa.** A change of
logical address reference, coupled with compensation from initial frame-zero
helper inputs, reduces the fixed complex word from 480 to 400 helpers.
The complete local proposal has rank mass 5276 instead of 5586.

The witness includes all 64 initial compensation terms, 80 handoffs, 48 early
cleanup gates and full logical cleanup. It preserves 40 cold outputs and
restores every arbitrary non-target input. Every column of all 160 exact
Gaussian handoff/exit products is checked, including scalar phases.
[PROOF.md](PROOF.md) explains the construction and its limits.

## Reproduce

Python3.12 with NumPy1.26.4:

```sh
python3 scripts/research_package.py --package research/anticipatory-dirty-borrowing
```

Expected: `PASS_ANTICIPATORY_DIRTY_BORROWING` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The entry point checks exact source pins,
all 624 independent inputs in the fixed word, all 512 columns of each local
adapter, cold restoration, inverse cleanup, four external mutations and the
embedded missing-basis/inverse controls. Child assertions are explicitly
preserved even when the entry point is run with `-O`. Normal verification
uses temporary files and writes no tracked artifacts.

## Exact price and limitations

The local profile is `{1:2382,2:445,3:406,4:128,5:42,8:8}`. COPY64 remains
included. Exact rational interval pricing generously allows fractional idle
packing at the outer halving cap. For the nine-stage model, the favorable
primitive-saving ceiling lies in
`[0.001754331546940,0.001754331546941]`. Every tested odd-stage model still
rejects a=0.00177. These ceilings are not attained savings or kappa values.

Full native word lowering, both hosted orientations, whole-call ownership,
precision, tape, finite work constants, the bit rail and the strict outer
assembly remain open. The private zero buffers are used only in final inverse
cleanup; no recursive child runs while they are live. No selected production
file, selected-result pointer or predecessor package changes.

## Predecessors and contribution

The selected PR1042/1094 word, Ali Romman's fixed-block extraction and proof,
Thomas DiFiore's block discovery, general Clifford-frame normal forms and the
provider/controller lineage retain credit. The exact interval engine is copied
unchanged from Douglas Colkitt's incorporated `complex-local-word-ceiling`,
with its notice. See SOURCES.json, NOTICE.md and OVERLAP.md.

The addition is the fixed 80-alias changed-reference construction, its initial
monomial compensation and complete logical/frame replay. This is distinct
from recursive additive-port borrowing or a claim to host a clean scatter at
zero cost while restoring its host. No unrestricted borrowing theorem is claimed.

## Open next questions

First emit and verify the entire native chronological word in both orientations,
including all compensation and private cleanup. Then find and price an actual
whole-call owner map for an odd-stage controller. The current exact favorable
price already misses the campaign target, so a further structural change is
needed before attempting a kappa claim. The bit rail is a separate obstacle.

## Credit

Prepared by Cinna Davis (@1337isnot1337) with substantial OpenAI Codex assistance.
Apache-2.0; predecessor notices are retained. No independent human review or
formal proof of the full multiplication theorem is claimed.
