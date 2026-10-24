# Physical complete-fibre ROW padding

This package lowers the compatible-row padding/return/restriction boundary
to one fixed589-instruction controller on fifteen tapes. For runtime positive
binary P,R,S,B with S<=R and V=PRB, it pays descriptor preparation and
round-up, inserts complete zero fibres, restricts only after the completed
callee returns, and erases every owned temporary. The written bound is
2048V+2048 transitions excluding the callee and64V+64 visited cells.
There is no fixed descriptor bit-width limit.

The actual #4989 helper462/frame506 borrowed branch at q5,w4,k1,S3 pads
five rows to six. With P2 and body/spectator fibre B6,60 bits become72:
twelve physical zeros, not one metadata marker. All sixty basis inputs,
binary carry boundaries, arbitrary dirty data and independently translated
tape origins are checked. [PROOF.md](PROOF.md) separates this finite evidence
from the all-width argument.

The completed row-pointwise, source-preserving callee remains a semantic
premise. Local zero/length/head checks do not certify it; a registered
counterexample demonstrates that distinction. No native_canonical or
raw_reverse_swap implementation, full GL64 payload, new supplier, P3 reserve,
precision/outer admission or new kappa is claimed. Canonical data/shape failures execute owned cleanup and rewind borrowed
heads; callee head violations quarantine state instead of promising recovery.

Jose Manuel's PR2786 supplies the original compatible-row scans and callback
contract. Nick Petalas's PR3503 supplies the exact strict-volume criterion
and capped Count/Tape adapter. Their ratio/least-borrowing results and scans
are credited, not republished as new results. This adds fixed local control
and a uniform complete-fibre cost, while keeping the actual source S<=R domain.
The wider S<2R change is outside scope. #4957's conditional completed BIT API
and #4989's addressed matcher/ROW schedule supply the actual caller boundary.

Run from repository root with standard-library Python3.12:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/bit-row-padding-physical
```

Registered normal/optimized replay checks immutable inputs, complete bytes,
cleanup, malformed returns and the fixed table receipt. Committed bytes,
source history and official Git-free export are separate publication checks.
The simulator uses dictionaries to represent tapes; only its declared local
instructions define the proved machine cost. Test oracles and synthetic
callee execution are not hidden machine instructions.

Canonical claim:
https://github.com/CrocSwap/integer-mult-bounds/discussions/4945#discussioncomment-19141335

## Open next questions

- Supply an actual completed native/raw callback with this exact source,
  row-pointwise, distinct-output and restored-head contract; begin at the
  source inner_return boundary, preserving complete other-high-field fibres.
- Bind this controller to the full selected serialization and actual P3
  reserve/precision constants. The interface calibration alone does not
  instantiate the astronomical complete matcher cover.

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0. Preserve credit
to ai-nanachi, Jose Manuel, Nick Petalas, Chris R/Clear1nsight, David Arias
and the full source-native/ordinary/ROW lineage in the authenticated inputs.
No independent human or proof-kernel acceptance claim.
