# Separate model-assisted lead review

The lead orchestrator reviewed the source, mathematical argument and complete
bill separately from this worker. This review shares source context and is
AI-assisted. It is not an independent human or formal-kernel proof.

Critical tested production SHA-256:
`90692dd83d961d61ba3271390185dd21337b4334f388f161c8f8a81b76a884c8`.
Reviewed PROOF.md SHA-256:
`2da659955598934113e236b2ba572825447f735e4fe78ac09b3d65a6b6418c2b`.
Both match the package at this review checkpoint.

The separate checker reuses only the worker's literal physical Tape hardware
fixture. It supplies its own signed integer encoding/decoding, exact integer
rounding oracle, parameter cases, endpoint and cleanup checks. Its result is:

| Check | Completed coverage |
|---|---:|
| Admitted complete fields | 30 |
| Correct late-overflow fields | 120 |
| Signed components | 720 |
| Literal codec actions | 40,507,611 |
| Width/headroom and conditional threefold expansion checks | 59,700 |

The dynamic values are g in {1,2,4,9,31,65}, h in {2,3,5,9,17}, with
randomization seed 20261109. Every private role retires. The arithmetic width
sweep covers h=2..200 and g=1..300. The script and exact receipt were copied
unchanged from the lead's recovery package into `review/` with attribution.
The lead added an optional package-path argument for portability after the
original run; its arithmetic and tested production bytes were unchanged.

Optional reproduction, from the repository root:

```sh
python3 -B research/current-rounded-positive-leaf/review/rounded-leaf-lead-check.py research/current-rounded-positive-leaf
```

This independent script uses assertions and must be run without `-O`. It
regenerates its adjacent `rounded-leaf-lead-review.json`; the four default
registered worker gates remain read-only. The lead checker corroborates the
dynamic drop/overflow and width arguments, not a complete selected producer,
the whole exact native kernel, or a full MOVE. The worker's complete small
kernel fixtures and source proof are separate evidence.

The lead also checked the unchanged exact leaf's preparation/runtime
consumers: record and row byte lengths are the only fields the new widening
must change; active geometry stays the same; the power construction's digit
budget is paid because the original row_bits already contains a digits.
The review retained the valid-shape, actual-provider and disjointness
restrictions, with arbitrary interruption/malformed late output excluded.
