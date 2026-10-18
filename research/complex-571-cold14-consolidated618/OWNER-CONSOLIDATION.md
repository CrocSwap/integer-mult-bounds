# Twelve helper moves above PR610

This is a literal owner-map improvement on PR610, pinned at
`b7c680ea38b9a25a89fce189bb927b45842362d0`. No verifier guard or mathematical
hypothesis changes. All circuits and the jp8 ×71 / ck ×1 dispatch are inherited.

## Exact result

| Quantity | PR610 | This revision |
|---|---:|---:|
| Conditional κ | 0.00162536523418317 | 0.001625434703655052 |
| Conservative κ | 0.001625365231365566 | 0.001625434700837327 |
| Native complex endpoint | 0.001628011347227810262234 | 0.001628081043082841928025 |

The new κ is exactly `406358675913763/250000000000000000`.
The native complex endpoint is `65123241723313677121/40000000000000000000000`;
the conservative endpoint is `1628081040255934644259/1000000000000000000000000`.
The cited PR543 bit endpoint remains nonbinding. The exact engines must accept
the complex endpoints and reject the endpoints plus 10^-24; the outer assembly
must reject the next κ grid point. These are finite conditional certificates,
not an unconditional multiplication theorem or full Lean certification.

## What changes

PR610's repair leaves several rank-48 owners with just one helper. Moving helpers
from different complete calls into a common owner can concentrate unused rank
into whole rank-48 remainders. Every move requires the destination's idle window
to contain the call, sufficient capacity, and no other helper in that physical
family during the call. Each helper retains its call, identity and residual width.
Offsets are then repacked in chronological order within each owner.

The twelve moves are listed in `data/CONSOLIDATION.json`. Fourteen of the 36,288
role records change: twelve change owner, two change only offset. The idle profile
changes by {2:+1, 4:+1, 35:+1, 39:-3, 41:-9, 43:-1, 44:-2, 48:+12}; all other
entries remain equal, including the 26 rank-one idle remainders. Its rank mass
is unchanged. The global deficit remains 2560 and physical stock remains 7682.

The search greedily decreases the floating-point proxy sum r log(73/r) by
67.4953382699858. This proxy chooses moves only; exact pricing comes from the
unchanged two-engine moment checks and outer assembly. No optimality is claimed.
A separate 120-second, two-worker pattern search, using PR610's documented
pattern/flow and bipartite-edge-colouring method, returned the same paid profile;
its timeout is not evidence of a ceiling.

## Reproduce the nomination

From this directory, with a checkout of the pinned PR610 commit at `/path/to/pr610`:

```sh
python3 -B tools/consolidate_owners.py \
  --data /path/to/pr610/research/complex-571-cold14/data \
  --out /tmp/cold14-consolidation
```

`/tmp/cold14-consolidation` must not exist. Compare PLAN.json and the decompressed
OWNERS.json.gz with the committed data. Compression bytes can vary by environment.
The source hashes in PLAN.json pin PR610's immutable inputs. The candidate hashes
in SPEC.json and MANIFEST.json pin this revision's committed artifacts.

## Admit the result

Use `verify.sh NEW_WORKDIR SOURCE_ROOT` with the exact source checkouts listed in
NOTICE.md, or pass their package directories explicitly:

```sh
python3 -B verify.py --work /tmp/cold14-consolidation-replay --jobs 2 \
  --source multicold=/path/to/pr568/research/complex-multicold \
  --source structural_gain=/path/to/pr571/research/structural-gain \
  --source larger_gain=/path/to/pr569/research/larger-gain \
  --source joint_prefix=/path/to/pr575/research/complex-joint-prefix \
  --source frame_coalescing=/path/to/pr583/research/kernel-frame-coalescing
```

Use a fresh output directory and the default committed SPEC, without discovery
or reuse options. The verifier reconstructs the baseline and both providers,
admits the literal controller, recomputes the finite invoice, checks native and
conservative exact arithmetic and runs all mutation, phase and generated-identity
controls. Expected κ: `0.001625434703655052`. Only the Python standard library is
needed for admission. Solver dependencies are unnecessary.

Prepared by Jeremy Diviney with OpenAI Codex assistance. All predecessor credit
and inherited proof obligations are in NOTICE.md. This revision awaits review.
