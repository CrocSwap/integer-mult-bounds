# Scalar coefficient construction within the 84-bit A-stage capacity

The complete ordinary prelude/A coefficient recipes fit PR3089's conditional
**84-bit common arithmetic capacity at 64-bit input precision**. Both pinned
PR3076 providers and both orientations pass. This closes PR3089's explicitly
excluded coefficient-microstate obligation without adding fractional or
integer guard bits.

The target digit walk uses **57,710 real unit instructions**, compared with
64,782 for the explicit scratch control, saving 7,072 through the prelude/A
interval per provider word and orientation. It never writes its source.
These are logical arithmetic instruction counts. Physical bit costs and the
complete recursive invoice are not supplied.

[PROOF.md](PROOF.md) gives the contract and uniform `P+20` common-width bound
with seven fractional bits. Every changed recipe row is checked by rational
substitution and a separately written fixed-denominator integer interpreter.
The replay covers all 9,992 macros and 29 scalar templates per stream, with
source restoration and initially-zero scratch cleanup checked after every
macro. [RESULT.json](RESULT.json) records deterministic capacities, counts,
witnesses and instruction hashes. Twelve behavioral groups include transient
grid and signed overflow with correct final endpoints, wrong signs/ports,
missing source restoration and missing scratch cleanup.

The two interpreters share the pinned source generator and normalized-row
propagation. This is author-checked finite arithmetic evidence, not an
independent supplier admission or formal multiplication proof. The exact
residual adapter endpoint hypothesis remains. Adapter interiors, recursive
approximation, centres/later phases, clean stock, routing, ownership and the
complete physical bill remain open. No new kappa or selected-frontier change
is claimed.

## Reproduce

Python 3.12, standard library only. Set RUN to a fresh external session-owned
directory. From the repository root:

```sh
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python \
  -X pycache_prefix="$RUN/bytecode-replay" -W error -B \
  research/rank7-coefficient-capacity/verify.py --work "$RUN/replay" \
  > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-coefficient-capacity/RESULT.json
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python \
  -X pycache_prefix="$RUN/bytecode-tests" -O -W error -B \
  research/rank7-coefficient-capacity/test_microstates.py
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -B \
  scripts/research_package.py --package research/rank7-coefficient-capacity
```

Without `--work`, the verifier removes its outputs beneath TMPDIR. The
registered command runs both the cold replay and optimized behavioral checks.
Use fresh bytecode-prefix paths for direct calls, because `-B` alone can read
existing bytecode. The registered launcher creates private prefixes itself.
Runtime needs no Git or network. [VENDOR.json](VENDOR.json) pins every reused
source byte; [SOURCES.json](SOURCES.json) preserves baseline provenance.
[CHECKS.json](CHECKS.json) records the observed environment, commands and limits.

## Open next questions

Can a paid exact residual adapter supply the assumed A entrance values?
Start with one emitted residual adapter and specify its actual input, dirty
state, intermediate grid/range and cleanup. Recursive child semantics and
physical backing are blockers.

Can a complete physical caller realize these recipes and consume the A exit?
Bind the target walk and one initially-zero scratch to signed fixed-point
operations, then charge shifts, copies, clear, stock, movement and the centre
consumer. The present instruction saving does not price these obligations.
[TASK.json](TASK.json) records their relevance and first steps. No further
coefficient search is justified by this result.

## Credit

Nick Petalas contributed this capacity-extension lemma and replay. PR3078's
coefficient recipes and PR3089's capacity proof are retained unchanged. The
source lineage includes PR3086/3083/3084/3076/3060/3056, dcharb78/PR3042,
Jeremy Kothe/PR3015, Marius-Paul Dumitrean/PR2979, Cinna Davis/PR2226,
DLamdata's exact Clifford kernel, eumemic/PR411, icekylinx, Tekalign and the
retained native, geometry and owner contributors. Original notices and credit
files remain intact. No priority is claimed for digit arithmetic or Fourier
identities. New work is Apache-2.0. Development used substantial automated
assistance; no independent human review is claimed.
