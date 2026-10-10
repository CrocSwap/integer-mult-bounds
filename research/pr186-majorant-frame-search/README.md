# Global majorant contraction search on the h=22 coordinated witness

This directory records the search that produced a further exact improvement
of `research/coordinated-frames-and-entrance-banks`.

## Parent

`PARENT-COMMIT` contains the exact repository commit on which the search
started.

The `baseline/` directory freezes the selected complex artifacts that differ
from the final improved witness.

## Search

`majorant_search.py` applies a directed minimum-cut concavity majorant to a
least feasible contraction schedule for the existing h=22 physical operation
frames.

The floating/min-cut computation is candidate generation only. It is not
relied on for proof and no claim of global optimality is made.

The selected search result has:

- 32,971 operations.
- 11,021 operations with a nontrivial least-frame contraction.
- 923 selected operation contractions.
- majorant proxy delta approximately -616.8628316074464.
- actual reconstructed paid-entropy delta approximately -619.3135273094522.
- 13,085 physical-frame overrides before this search.
- 13,810 physical-frame overrides after this search.

The exact repository physical verifier independently accepts the resulting
frames.

`replay.txt` is the captured deterministic search replay. `replay-check.json`
records equality of the replayed search receipt and the exact certified
physical-frame witness. `SHA256SUMS` pins those artifacts and the frozen
pre-pass inputs.

## Exact final complex witness

The terminal compiler retains all 46 terminal sinks.

The final inventory is

- m = 66
- W = 13,326
- rank = 878,196
- deficit = 1,320
- maximum child = 20
- compensated aliases = 2,310
- terminal sinks = 46

The exact outward-rational moment certificate accepts

    b = 662942072695346 / 10^18

and rejects

    b + 10^-18 = 662942072695347 / 10^18.

The unchanged balanced assembly certifies

    kappa = 662502871668435 / 10^18
          = 0.000662502871668435

and rejects the next 10^-18 kappa grid point.

The preceding selected repository headline was

    kappa = 0.000661885549259598.

## Provenance and scope

This search adapts the repository's existing concavity-majorant /
directed-min-cut frame-search machinery to the earlier h=22 coordinated
PR181/PR186 witness.

No novelty claim is made for directed minimum cut, concavity/majorization,
the underlying Clifford-frame theorem, the PR181 scalar construction, the
PR186 rematching/frame construction, or the terminal-sink construction.

The contribution here is the application to this specific selected witness,
the resulting 923-operation contraction schedule, the generated exact frame
witness, and its integration into the complete exact certificate.

Developed with substantial OpenAI ChatGPT assistance.

This remains a conditional finite certificate under the inherited interfaces;
it is not a proof of global frame optimality or an unconditional multiplication
theorem.

Contributor: @dataisfire
