# Four-flag compiler interface review

Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
Apache-2.0. Credit: PR2226 (Cinna Davis), PR2269 (Jeremy Kothe), PR2339
(Sagar Thakrar). This is a verification handoff, not a new κ certificate.

The normalized diff of `transport_lifted.py` against pinned
`parent/new/code/borrow/bw_transport.py` is in
`TRANSPORT-NORMALIZED.diff`. After line-ending normalization the changes are:

- attribution;
- a five-field literal warp converter that maps the register and **both**
  literal frames to native identifiers;
- the diagnostic warp-event count now includes the entire program, including
  the new A-phase events.

No inherited mathematical check is removed. Registered-operator lookup,
actual current-frame equality, exact binary frame-image equality, arbitrary
input endpoint replay in both orientations, monotone ordinary climbs,
dyadic coefficients, recursive profile equality and zero-buffer endpoint
checks remain active. New A warps flow through the already existing `do_warp`
path. The new primitive executes after ordinary entry adapters, and source
registers33,55,74,85 are ordinary X registers, so their prelude does not bypass
a residual helper wrapper.

`emit_four.py` prepends four target identity scales at frame[30], causing
actual target climbs, followed by four explicit source warp/add/unwarp
macros. It updates the four target levels used by the center COPY paths.
The main handoff G for each source must match its prelude G; the independent
operator check binds both to the flag receipt and actual emitted words.
Restoration additions inserted before the later handoffs are part of the
ordinary recorded non-target history and need their cleanup inverses.

Omitting the temporary prelude warp pairs from the non-target inverse history
is valid only because each pair's intervening operations write targets and
its forward non-target projection is exactly the identity. It does **not**
mean the inverse-transpose macro is identity: its intended target-to-source
update is part of the whole dual endpoint. Actual whole-program forward and
dual replay is therefore essential. Neither a pristine source snapshot nor
a forward-only scalar diagnostic replaces it.

The predecessor literal `audit_local.py` does not accept A-phase warp items.
Its inability to parse the new schema is not a successful audit. The adapted
native transport and unchanged native emitted-program checker provide the
applicable endpoint/frame coverage; exact physical operator products and
recursive label checks are separate stages.

## Independent physical checks

```
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/check_four_operators.py
```

Expected:
`PASS_FOUR_EMITTED_OPERATORS_EXACT_512_COLUMNS_BOTH_ORIENTATIONS`.
The default native directory is the actual first base transport output;
`--native-base PATH` supports another bound replay directory. The checker
imports only the independent Gaussian-integer implementation in this local
interface package, never the predecessor operator implementation.

It covers the eight provider/operator records (four new operators in each
provider), all16 actual base-native frame classes, and20 distinct exact
products after basis variants are included. Every product is evaluated on
all512 columns. Both forward and inverse-transpose unit-monomial recipes
are recorded. The native FULL-WORD decompressed bytes are required to equal
the tested emitted base word. The receipt is
`FOUR-OPERATORS-INDEPENDENT.json`. Other unchanged operators are the
responsibility of the complete native chain.

## Targeted new-path negative control

```
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/check_transport_flag_control.py
```

Expected: `PASS_HANDOFF_PRESERVING_WRONG_ENTRANCE_FLAG_REJECTED`.
The mutation composes G with a reversible permutation **inside** its
retirement frame. It still carries the retirement frame to the prescribed
handoff frame, so the old handoff obligation remains true. It deliberately
stops carrying the entrance line to[30]. Actual adapted transport rejects
it at `warp G does not carry the frame` and creates no success output.
This tests the new A-phase obligation specifically. The exact mutated G,
source hashes, exit status and failure log are retained in
`TRANSPORT-FLAG-CONTROL.json`.

The companion agent's word controls check omitted target-level interface metadata,
compensation/sign mutations and source-restoration/cleanup omissions. These
checks do not establish owner hosting, physical reserve, recursive labels,
an outer ledger, or a new κ. Those obligations remain with the complete
candidate verification.

## Orientation adapter and completed native chain

`ORIENTATION-NORMALIZED.diff` compares `orientation_lifted.py` with the
pinned PR2339 `interface/orientation_contract.py`. Its only changes are the
import path and candidate-specific inventory assertions/report values:
112 warp classes, 224 oriented recipes, 76 private zero buffers, phases
`A:8, B:52, full_frame_cleanup:52`, paid mass5328, helper width3472 and
428 helpers. The exact Gaussian matrix comparison, rank-zero requirement,
forward/dual conversion, one wrong-global-phase mutation per oriented
recipe, emitted recipe inventory, zero-buffer allocation checks and
profile/width assertions are retained. There is no removed proof-relevant
check. All224 recipes still cover all512 columns in each provider.

The completed chain is a fresh start followed by a continuation: base
transport through recipes ran first; the inherited orientation check then
rejected its obsolete224-class inventory assertion. The corrected
orientation adapter was run on the existing base outputs. All extra stages
and Lemma G then completed. `NATIVE-RESULT.json` records this history and
43 hashes of outputs/logs. `ORIENTATION-REVIEW-VALIDATION.json` independently
checks those43 saved hashes, equality of both actual native FULL-WORD
payloads to their emitted candidate words, each canonical payload's binding
to its orientation receipt, and each oriented recipe payload's binding.

The driver overwrote the original failed base-orientation log on retry.
That original log is unavailable; `STEPS.json` retains its exit1 followed
by the successful retry. A later reconstruction must not be called the
original log. An attempted independent rerun using the system `python3`
failed at missing NumPy before evaluating the assertion; this does not
change the completed native checks made in the dependency environment.

The original base transport receipt's diagnostic `warp_events=104` omitted
the eight A events. It is preserved. A separate corrected transport replay
reports112 and has exactly identical decompressed canonical bytes.
The orientation receipts bind all112 actual events independently of that
old diagnostic counter. No original receipt has been silently rewritten.
