# Current result

The current conditional saving is
`kappa = 6149999/50000000000000 > 2^-23`.
See the [proof](../../artifacts/batched-23-note.pdf),
[certificate](../../certificates/batched-network.json), and
[combined patch](../../patches/batched-23.patch).

The result uses the PR7 finite producers with controlled projector-block
recursion, whole complex residuals, integer-width row handling, and a dependency
path precision guard. Parameters and strict margins are in the certificate.
The inherited Gaussian scaling enclosure is corrected while retaining `P=34p`.

[The review guide](batched-review.md) maps the proof obligations and correction.
The statement remains conditional on the pinned upstream interfaces; finite
checks are not a formal proof of the full multiplication machine.

The earlier main-branch result `83/10^12` remains in the
[compact-control note](../../artifacts/compact-control-note.pdf) and
[certificate](../../certificates/compact-control-layer.json).
Older research pages document their historical assumptions and targets.
