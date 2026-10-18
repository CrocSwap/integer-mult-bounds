# Reversible execution of the reached A13 native climb

The actual A13 source83 warp, target126 climb and half-ADD in both pinned
PR3076 providers admit a reversible Boolean implementation at the proved
quarter grid and `P+5` signed bits. At `P=64`, the complete local boundary
uses 1,916,736 CNOTs and 996,672 Toffolis, two existing complex arrays of
141,312 data bits in total, and one reusable 68-bit clean carry bank.
It uses no component scratch.

A constructed control materializes HALF and DOUBLE inside the same in-place
Gaussian C lift. Reading shifted source wires instead saves **209,920 CNOTs**
at 69 bits, with the same Toffoli count, data arrays and carry bank.
Both counts charge every real-word permutation SWAP and sign change in the
source monomial and target frame, as well as the final half-ADD.
This comparison claims no circuit minimum or improvement to an existing
upstream physical compiler.

[PROOF.md](PROOF.md) proves the lifting identity, input alignment, every
arithmetic microstate's range and the width-dependent tariff.
[RESULT.json](RESULT.json) records the two fresh complete native bindings,
exact dispatch hashes, tariffs and fixture digests. The cold replay checks
279,616 parity-matched truth columns for each sign and implementation,
including literal inverse and clean return, then executes 18 complete
512-coordinate native fixtures at input precisions 3, 64 and 128.
It also executes the complete control and inverse on the dense 64-bit fixture.
Nine behavioral groups cover failed alignment, dirty carries, overflow,
ownership/capacity errors, wrong signs and omitted gates.

This closes a local frame-operation gap left by PR3094's scalar-only caller.
It is conditional on PR3086's exact physical entrance and the available clean
carry bank. The full prefix, residual adapters, recursive children, storage
ownership, routing, later consumers and supplier bill remain open.
The recursive paid profile and selected kappa do not change.

## Reproduce

Python 3.12, standard library only. From the repository root, choose a fresh
session-owned directory outside the checkout and run:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/a13-climb-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/bytecode" \
  uv run --python 3.12 --no-project python -W error -B \
  research/rank7-reversible-native-climb/verify.py --work "$RUN/replay" \
  > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-reversible-native-climb/RESULT.json
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/test-bytecode" \
  uv run --python 3.12 --no-project python -O -W error -B \
  research/rank7-reversible-native-climb/test_climb.py
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/registered-bytecode" \
  uv run --python 3.12 --no-project python -B scripts/research_package.py \
  --package research/rank7-reversible-native-climb
```

Without `--work`, replay removes temporary outputs beneath TMPDIR.
[SOURCES.json](SOURCES.json) pins all 24 live inputs, including the retained
native sources and notices. [VERIFY.json](VERIFY.json) declares every live
input for CI invalidation. No predecessor source is copied or edited.
Full Git history is needed for the generic provenance check; direct replay
only needs the declared source files. [CHECKS.json](CHECKS.json) records
validation and [ENGINEERING.md](ENGINEERING.md) records resource limits.

## Open next questions

Can an actual prelude residual adapter supply this kind of physical entrance?
Pin one literal `residual_adapter` event and specify its normalization,
owned arrays and clean stock before choosing a reversible factorization.
Recursive child semantics and the producer's full physical contract are blockers.

Can the A13-A16 consumer retain the saving on an actual layout? Place the two
arrays and carry bank, price accesses and movement, then include subsequent
uses and eventual cleanup. Arbitrary-wire CNOT counts do not establish a
multitape time bound. The complete producer, consumer and supplier costs remain
unresolved. [TASK.json](TASK.json) gives the scoped handoff and expansion stop.

## Credit

Nick Petalas contributed this in-place lift, literal native dispatch,
reversible implementation, proof and control comparison. PR3086 supplies the
reused exact A13 native-format boundary and Gaussian operator interpreter;
PR3094 supplies the reusable scalar circuits; PR3080 supplies the shifted
read-only ripple adder. Their source bytes and original notices are unchanged.
PR3088 covers the related A13-A16 operator/format boundary, rather than this
in-place bit implementation. No priority is claimed for elementary lifting,
Clifford identities, shifted arithmetic or ripple addition.

The retained lineage includes PR3076/3078/3060/3056, dcharb78/PR3042,
Jeremy Kothe/PR3015, Marius-Paul Dumitrean/PR2979, Cinna Davis/PR2226,
DLamdata's Clifford kernel, icekylinx, Tekalign and the credited native,
geometry and owner contributors. New work is Apache-2.0. Development and
internal read-only review used substantial automated assistance; no independent
human review or proof-kernel verification is claimed.
