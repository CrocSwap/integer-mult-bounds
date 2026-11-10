# Unit06 caller/preparation review — retained early findings

This version records early source findings and is not acceptance of a complete caller, preparer or entry operation. No candidate/original code or test was executed by this reviewer. The parent fixed the sole repair window at13:20:31–13:35:31 UTC; the original hard deadline remains unchanged.

## U6-CALLER-01: unowned observation pass, rejected initial draft

The initially read200-line predecessor_entry.py defined observe_regular with a separate os.open/read/fstat/finally-os.close pass before invoking the owned retained reader. That first pass had no Owner pending/busy/descriptor capture, primary retention or raw-buffer capture. A concrete source counterexample is read/fstat raising A followed by close raising B: Python finally raises B, while Owner.primary remains None and Owner can appear ready. No test execution is claimed for this witness.

The author reports a self-correction at13:20:31 before receiving this review finding. The initial whole-file bytes were overwritten before this reviewer captured their same-read hash. The author reconstructed the initial9,950-byte draft by an exact inverse and verified it against an independent original tool-read hash: d7512ffe6c9ee2b7a51b98672032fd14f50f5d47e193131873ea426a47f25cbd. It is retained as fixtures/initial-draft-VERIFIED-RECONSTRUCTION.py.txt, with fixtures/RECONSTRUCTION-v1.json explicitly labeling VERIFIED_RECONSTRUCTION_NOT_DIRECT_SAVED_COPY and preserving the original-overwrite gap.

The subsequently measured9,247-byte35b99508cbc4b686f18b29ecd1458c21f4139ffd0a8cc62a774a49570e20c10f draft is ALREADY AFTER that self-correction. It must not be relabeled as the failed initial body. This corrected shape has one Owner-controlled _retained_read with optional observation-only digest, a public retained_read that requires a prior digest, and observe_regular delegating once. That removes the naked first pass by source inspection; meaningful new fake I/O failure fixtures remain required.

## U6-CALLER-02: original blob-path mismatch, rejected35b draft

35b path_text73–76 accepted Unicode/control characters other than NUL and more than64 components. validate_blob delegated to it. Original epoch_schema_v5.path121–128 requires printable ASCII32..126 and at most64 components. Examples accepted by the old helper but refused by the actual schema are a path containing é, a newline filename, and a path with65 components. This is an incompatible claimed schema/preparation result, not evidence of actual runtime admission.

The9,574-byte T0-support prefix SHA c20523438a6bb49ef43ea527cf6c96a07542cadea72a77eb822c54f8f64fb863 corrects printable ASCII/component bounds and exact cap typing. It retains the single owned observation/read path. Parent separately preserved35b as pre-path-fix evidence. Current corrections are source-inspected, not an executed success or complete operation milestone.

## Current scope and pending complete review

At13:26 the reviewable implementation contains only the T0 support prefix of predecessor_entry.py. The complete generic entry/actual source loader, prior-admission caller successor, real P/Q/M/JOBS/STAGE preparer and output DATA bridge have not yet been reviewed as complete actual code. Architectural input acceptance does not accept those missing bodies.

The final source review must inspect prior selection checks before config/policy/stage/queue use, canonical R/history/locks and genuine outer ownership, separate real K resources, actual exclusive preparation and post-mode identity observations, acyclic source/policy/plan/manifest finalization, actual result verification before the science DATA receipt, all first-error/partial-FD states and exact new fixture isolation. No callback or serialized successful-owner substitute is accepted.

No edits were made to author source. Only this review pair is written. Original C05/V03, runtime qualification and activity credit remain false/zero. All previous units stay closed; costs OPEN_NOT_ZERO.

