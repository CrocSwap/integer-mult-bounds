# Validation receipts

Linux Python 3.12.3 completed the full verifier; macOS Python 3.14.8 completed quick mode with E8_REPLAY_PHASES=1. Quick mode skips only inherited PR443 exhaustive controls. Every new check ran on both platforms, including freshly regenerated phase edges. The entire RESULT.json is byte-identical. Both receipts bind the unchanged package manifest and upstream source inventory.

The independent audits, fresh default-program regression, repository make verify-joint output and scoped format-ceiling controls are included. The ceiling verifier also passed on Linux after its final integrity manifest was added. CI results are separate and are not claimed by these receipts.

The first macOS attempt stopped on a parent source-inventory check because an earlier local import had created an untracked Python cache file inside the frozen vendor directory. All source hashes were unchanged. That run-owned cache was removed; the second complete attempt passed. No source change was required. Future verifier subprocesses disable bytecode writing.
