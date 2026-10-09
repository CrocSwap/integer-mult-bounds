Rank-priority interval composition: independent finite reproduction

Run from the repository root with Python 3 and a C++17 compiler available:

    python3 scripts/experiments/verify_ranked_interval.py

Assertions must remain enabled. The verifier independently replays both saved
physical XOR words on the full input and dirty basis in both orientations,
checks every original-envelope frame incidence, reconstructs transitions,
recomputes fixed-I+J profiles with bounded-minor CRT controls, and checks the
exact recurrence, all 47 strict assembly inequalities and seven margins.
It also checks source manifests and both compressed and raw word hashes.

The saved words can be regenerated individually, for example:

    python3 scripts/experiments/ranked_interval_compiler.py --h 23 \
        --output /tmp/ranked-interval-23-receipt.json \
        --word /tmp/ranked-interval-23.json.gz

Repeat with --h 25. Regeneration uses the graph pinned under
references/frame-compiler/pr62 and the local compiler sources. The saved
compiler receipt records complete dirty/frame checks and independent replays.

The fixed rational witness is

    bit saving = 255150939 / 5000000000000
    kappa      = 318922399 / 6250000000000 = 0.00005102758384.

This composes PR62's cyclic interval graph (Avi Eisenberg / ikeboy, with
Anthropic Claude assistance), PR57's joint frame compiler (eumemic, with
OpenAI Codex assistance), and PR60's descending-rank reclamation priority
(Chafik Boukhalfa, with OpenAI Codex assistance). Dominik Scholz's
contemporaneous PR63 reports the same composition with a slightly coarser
rational witness. This package provides an independent reproduction and
finer exact rounding; it does not claim a new graph or priority mechanism.

Outputs are certificates/ranked-interval-{kappa,validation}.json together
with compiler, word, transition and profile records using the same prefix.
The source manifest preserves inherited attribution and license notices.

Scope: this is a finite conditional certificate. The data profile and its
ten exact rational recoveries, ordered affine residual compiler, fixed-tape
recursion, scalar overhead, balanced transfer, analytic, routing and recovery
interfaces remain inherited dependencies. It is not an unconditional proof
of an improved integer-multiplication theorem or a global optimality claim.
