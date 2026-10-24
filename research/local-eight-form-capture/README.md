# Eight mixed forms captured in existing dirty helpers

This package proves one exact forward local scalar operation on 800 arbitrary
input fields. It preserves X, sends Y to Y+SX, and sends each of eight
selected helpers to `h_i + C_i(59X/4 + Y)`. Every other helper is unchanged.
The eight helper values remain dirty. The operation does not restore them.
This is a local construction; it gives no complete supplier or kappa gain.

Read the [algebra and operation-order proof](historical/work/complex-next/structural/hamming-factor/HOSTED-CAPTURE-REVIEW.txt)
and the [separate column review](historical/work/doubling-architecture/rank-independent/live-capture/REVIEW.txt).
The frozen word has 120 X fields, 120 Y fields and 560 helper fields.
On its 112 code ports, `S = I - C^T C/4` and `C C^T = 56I`.
The other eight ports have zero S rows and zero C columns. The captured
helper indices are 758 through 751. All original values are arbitrary.

The omitted-centre word has `Y -> Y+SX+Dh` and preserves its helper inputs.
First preload `h1=h+PY`, where P inserts the eight C rows. Then use the
updated h1 to correct `Y1=Y-Dh1`. The base word gives `Y2=Y+SX`.
Finally add `(59/4)PX` to the eight helpers. This yields the stated map.
The base word has 19,449 scalar operations. The capture adds 11,326
dyadic correction operations and two 448-term loads. The total is 31,671
scalar operations: 19,449 + 11,326 + 448 + 448. The replay uses
the updated helper values. The fresh independent review also checked that
every selected helper column of D is zero, so `D P = 0` in this instance.
The historical review's warning about a stale-helper error does not apply
to these eight helpers. It does not affect the verified endpoint.

Preload and dirt correction satisfy the saved zero-frame boundary contract;
postload satisfies its full-frame contract. These are exact local label
statements. They do not supply a paid native or phase realization of the
new boundary operations, a backward program, the routed global controller,
a physical endpoint decoder, restoration of the eight hosts, or an invoice.
The selected future Y owners are live data, not free private workspace.
The included endpoint check records nontrivial chart translations and
rejects a proposed two-tap tensor shortcut. No such shortcut is used.

## Replay

From this package directory, with Python 3.10 or later:

```sh
python3 -B verify.py --build /tmp/local-eight-form-capture-replay
```

The build path must not exist. Only the standard library is required.
The runner checks source hashes and copies historical files into that path.
It then checks the full sparse-row map, a separate 800-column base replay
with symbolic boundary composition, a separate 800-column complete capture
replay, and the saved endpoint/covariance limitations. It compares all four
complete receipts with their unchanged historical results. The final line is:

```text
PASS_LOCAL_EIGHT_FORM_CAPTURE 800 8 11326
```

The finite scalar map checks plus linearity establish the all-input local
identity. They do not revalidate the inherited global supplier.
The two portable scripts replace historical absolute paths with explicit
input/output arguments and add an optimized-Python guard. Their unchanged
originals remain in `historical/`. The other two checkers are unchanged.
Python children run with environment options ignored; no discovery search
runs. `SOURCE-MANIFEST.json` binds every input. `replayed-receipt.json` and
`replay.log` record the fresh cleanup replay.

## Sources and overlap

The retimed R560 word is from the local lineage of
[PR #495](https://github.com/CrocSwap/integer-mult-bounds/pull/495), at
[its source-pinned proof](https://github.com/CrocSwap/integer-mult-bounds/blob/355d9f7ff293e291676ff4a32eed434419692576/research/e8-combined/PROOF.txt).
The two exact historical generated inputs are bound by SHA256 here; they
are not claimed byte-identical to a published generated input. The
[retained notice](historical/work/combined-pr/publication/research/e8-combined/NOTICE)
credits the R560 word to Ali Romman with OpenAI Codex assistance and records
DreamingOfClouds' kernel scripts, chafreaky's paid adapters and distinct-host
construction, icekylinx's split centres, and the earlier geometry sources.
The [source ledger](historical/work/combined-pr/publication/research/e8-combined/vendor/complex/SOURCES.json)
retains their exact pins. Original notices are unchanged.
The capture and its separate reviews were prepared with substantial OpenAI
Codex and research-agent assistance. No independent human review is claimed.

The later [native centre capture](https://github.com/CrocSwap/integer-mult-bounds/blob/cef4b52f2a59009865bf8eabde1be3f159063703/research/native-centre-capture/README.md)
uses 640 inputs, 16 centre records and different native endpoints. This earlier
800-input mixed capture is a different local identity. No cost or theorem
from one model is added to the other. The new contribution here is preserving
the closed exact operation and its limitations, not a new capture principle.

## Open next questions

Can these mixed forms be read by a complete routed controller and then
removed without a larger complete cost? The first step is a literal
composition that includes the arbitrary old host values and all phase
translations. The saved current stage maps differ, so a common-S identity
does not establish that composition. No such controller is supplied here.
