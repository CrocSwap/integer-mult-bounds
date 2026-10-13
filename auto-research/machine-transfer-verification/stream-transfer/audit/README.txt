PR76 finite frontier audit at the publication checkpoint
=======================================================

One bounded refresh found76 PRs. The strongest candidate in that snapshot is
Dominik Scholz's PR76, pinned to4b716171d4b3122d6b9db93f802751a41a209955:

  kappa = 51738676045141/1000000000000000000 = 5.1738676045141e-5
  bit saving = 25870676537201/500000000000000000
  roles(h23,h25) = (27256,35720)
  m = 575, W = 134095520, rank mass = 77103077100
  deficit = 1846900, largest child = 529

https://github.com/CrocSwap/integer-mult-bounds/pull/76

Fresh supplied-word validation PASSED: both full input/target/arbitrary-dirty
bases in both orientations, literal frame/event reconstruction, fresh actual
fixed-basis CRT profiles, exact characteristic and adjacent-saving-grid rejection,
and all47 assembly inequalities/seven margins. A separate independent checker
passed exact source/scatter binding, complete F2 basis semantics, reconstruction
of every paid profile component, and independent rational characteristic/assembly
checks without importing contributor arithmetic or semantic routines.

The new W crosses below2^27. The bridge was independently recomputed with
wire_bits27, row coefficient843 and degree gap7007/25. A stale wire_bits28
negative control was rejected. The original PR71 bridge is read from its exact
immutable Git blob; its other fields retain the inherited source values.
The public certificate is copied byte-for-byte as pr76-arithmetic.json with
pr76-SOURCE.json. No normalized substitute is presented as the public candidate.

The exact source/artifact hashes and successful commands are in
pr76-verification-receipt.json. pr76-validation-receipt.json records fresh
public package’s separate serialized replay/profile checks;
pr76-independent-receipt.json records this audit's separate scalar/arithmetical
implementation. The isolated PR76 checkout remained clean.

Limits: the heuristic compiler/discovery process was not regenerated, and no
unchanged whole-repository suite was run. This audit accepts the supplied legal
finite words and paid profiles. The public draft itself marks deterministic
regeneration and integration pending at its source freeze. The completed literal
Lean real-characteristic instantiation in this publication is PR73, not PR76.
The generic physical transfer results retain explicit implementation hypotheses;
no full multiplication-machine theorem at the PR76 exponent is asserted.

Publication reproduction
------------------------

Use Python3.11+ with assertions enabled, a C++17 compiler, and an external
checkout containing exact PR76 commit4b716171d4b3122d6b9db93f802751a41a209955
and its parent71 commit1bef94fd40a746452548c84a4a8f8834670a3113. Below PACKAGE
means the installed research/machine-transfer-verification directory; PR76
means that external checkout. No private task directory is required.

  python3 PACKAGE/stream-transfer/audit/independent_pr76.py \
    --repo PR76 --output /tmp/pr76-independent.json

For fresh CRT replay, prepare the required immutable parent archive within PR76:

  mkdir -p research/round6-pr71/baseline
  git archive 1bef94fd40a746452548c84a4a8f8834670a3113 | \
    tar -x -C research/round6-pr71/baseline
  python3 research/round7-scheduling/validate_selected.py \
    --bundle research/round7-scheduling/selected-both \
    --output /tmp/pr76-validation.json

The package's top-level offline checker separately recomputes the saved PR76
receipt arithmetic. It does not imply that words or CRT were rerun offline.
The imported audit/scatter_binding_audit.py helper's verify_scatter function is
path-independent; its historical standalone entry point is not a reproduction
command for this publication.

Landscape and credit
--------------------

incremental-inventory.json distinguishes changed head hashes, status-only
changes, exact source dependencies and untested compatibility. New74 reorders
scalar envelopes and pays reclamation; new75 toggles zero-signal provider
circuits on71; new76 combines74 ordering,71 split/live frames and70-style
carried-signal exchanges. It does not include75 zero-circuit toggles. PR66/71
head changes were validation receipts only. PR73 is now closed with unchanged
head; its archived numerical and Lean evidence remains valid. The refresh did
not find a public69 balanced-coarse plus71 anchored-split composition.

This is a scoped incremental audit, not a fresh exhaustive review of all76 PRs
or forks. An initial large GraphQL request failed with HTTP502; a smaller full
PR-list request succeeded. Raw network snapshots/logs are omitted from the
publication package. No external comments, pushes or PR modifications were
made by this audit.

The public finite result is credited to Dominik Scholz's PR76 composition,
Thomas DiFiore's PR74 envelope ordering, Chafik Boukhalfa's PR71 split/live
construction and PR60 ranking, Alejandro Zarzuelo Urdiales's PR70 exchange
method, Rohan Arun's PR65/67 schedules/costs, Rohan Garg's PR59 split operation,
Avi Eisenberg/ikeboy's PR62 interval graph, eumemic's PR57 compiler and all
retained data/complex-layer/assembly contributors. PR75's separate contribution
is credited as a comparison and future compatibility lead, not as an incorporated
dependency. All inherited notices, licenses and AI-assistance disclosures remain.
This independent audit was prepared with OpenAI Codex assistance; no exclusive
novelty or full formalization is claimed for the public construction.

elementary-stream-contracts.txt records the concrete counter, reset, residual
order, preimage-selection and head-return requirements reviewed for the ongoing
machine proof. The frozen counter module has its own independent source review
under ../counters/review.txt.
