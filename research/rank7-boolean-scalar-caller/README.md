# A Boolean caller for the complete rank-seven scalar layer

The conditional seven-fractional-bit, `P+20` capacity from PR3090 admits a
reversible Boolean implementation of every ordinary prelude/A scalar. This
package supplies the reached ADD guards, in-place SCALE circuits and complete
local cleanup. Both pinned PR3076 providers and both orientations pass.

At 64-bit normalized input precision, the 84-bit direct caller uses 6,806,482
CNOTs and 6,426,884 Toffolis per provider and orientation, for both real
components. An explicit reversible target-walk control uses 17,163,992 CNOTs
and 6,593,136 Toffolis. The saving is **10,523,762 logical Boolean gates** and
one 84-bit coefficient scratch field. Both use an explicit 83-bit clean carry
bank. The control is constructed here; neither implementation is claimed
optimal or an existing upstream physical compiler.

[PROOF.md](PROOF.md) gives the uniform argument, input guards, cleanup and
width-dependent tariffs. [RESULT.json](RESULT.json) records source-bound
histograms, guard ledgers, literal circuit/dispatch hashes and exact counts.
The cold replay reconstructs all 9,992 scalar macros per stream and reruns
the inherited native/capacity checks. It checks 310 small-width circuits over
225,334 exhaustive truth columns and 1,250 larger-width fixtures with a second
bit-array interpreter. Fourteen behavioral groups exercise missing sign fill,
wrong signs, omitted carry/scratch cleanup, source writes, dirty stock, grid
failure and signed overflow.

This is a Boolean implementation of the scalar subsequence, conditional on
exact native adapter endpoints and the intervening non-scalar contracts.
Residual adapter interiors, frame conversions, climbs/warps, recursive children,
centres and later consumers, clean-stock production, routing, ownership and
the complete supplier bill remain open. CNOT and Toffoli counts are logical
gate tariffs, not runtime. No new kappa or selected-frontier change is claimed.

## Reproduce

Python 3.12, standard library only. Set RUN to a fresh external session-owned
directory, then run from the repository root:

```sh
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python \
  -X pycache_prefix="$RUN/bytecode" -W error -B \
  research/rank7-boolean-scalar-caller/verify.py --work "$RUN/replay" \
  > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-boolean-scalar-caller/RESULT.json
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python \
  -X pycache_prefix="$RUN/test-bytecode" -O -W error -B \
  research/rank7-boolean-scalar-caller/test_caller.py
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -B \
  scripts/research_package.py --package research/rank7-boolean-scalar-caller
```

Without `--work`, outputs use a temporary directory under TMPDIR and are
removed. Direct calls should use a fresh bytecode prefix; `-B` alone can read
old bytecode. The registered launcher isolates bytecode automatically.
[FROZEN.json](FROZEN.json) pins the retained PR3090 source and PR3080 adder.
All required sources/notices are included; runtime needs no Git or network.
[CHECKS.json](CHECKS.json) records validation and its limits.

## Open next questions

Can a paid residual adapter and native frame converter supply the exact
scalar entrances on this layout? Choose one literal prelude adapter and bind
its intermediate bit operations and cleanup to the same capacity. Completed
recursive child semantics, owned stock and routing are blockers.

Can the centre and later consumer use the A exit while preserving the local
saving? Price one reached centre and eventual cleanup on this layout, retaining
all 91 inherited private buffers. Child arithmetic and all-size supplier
admission remain open. [TASK.json](TASK.json) records the first steps and
relevance. This result does not justify another coefficient search.

## Credit

Nick Petalas contributed the scalar caller, reversible SCALE/cleanup,
source-bound guard composition and tariff comparison. PR3090's capacity and
recipe replay and PR3080's adder are byte-identical retained sources. PR3081
supplies related local half-ADD caller work; it does not bind this full stream.
Concurrent PR3092 independently audits the reused capacity arithmetic, and
PR3091 supplies separate Gaussian leaf/tape operations. Their distinct scopes
and exact heads are recorded in [OVERLAP.json](OVERLAP.json).
The source lineage includes PR3089/3086/3083/3084/3078/3076/3060/3056,
dcharb78/PR3042, Jeremy Kothe/PR3015, Marius-Paul Dumitrean/PR2979,
Cinna Davis/PR2226, DLamdata's exact Clifford kernel, eumemic/PR411,
icekylinx, Tekalign and the retained native, geometry and owner contributors.
Original notices and credit files remain intact. No priority is claimed for
shifted arithmetic, ripple addition or elementary Boolean identities.
New work is Apache-2.0. Substantial automated development and internal review
assistance was used; no independent human review is claimed.
