# Draft: combine clearing relations

Latest candidate: **κ = 510338933/10^13 = 5.10338933e-5**.
Bit saving: **510364979/10^13**. The exact numerical gain over PR #67 is
26543157/(2*10^17). This is a preliminary conditional candidate, pending
independent serialized dirty-state replay and full validation.

At h23, XOR pairs of PR67's fundamental zero relations to obtain alternate
clearing expressions, cancelling expensive control promotions. All candidate
roles satisfy frame containment and selected expressions are emitted as
literal paid XORs. The compiler selected 48 improved clearing witnesses.
Keep PR67's h25 word unchanged at `research/slot-cost-rank-pair/frame-word-25.json.gz`.
Roles remain27918/36586 and W=137151806.

Passed in the research lane: internal complete dirty-basis compilation,
source/target/scatter and frame checks, literal transition reconstruction,
actual C++ fixed-basis profiles/CRT, exact moment and47constraints/seven margins.
Independent serialized replay, parent reproduction, dedicated CI and broad
checks are pending. No full formal theorem or practical speedup is claimed.
The original fully replayed PR68 result remains in `global-anchor-screen`;
the separate cost/live-anchor candidate remains in `cost-live-composition`.

Reproduce from the repository root (C++17 and Python with assertions enabled):

```sh
python3 research/circuit-space-clearing/run.py --h 23 --mode pairs --work-dir /tmp/circuit-space-reproduction
python3 research/circuit-space-clearing/screen.py --h 23 --work-dir /tmp/circuit-space-reproduction --independent-replay
```

`selected/arithmetic.json` and `draft-manifest.json` record the current
candidate and source/artifact pins. These commands have not yet been rerun
in the published checkout; the draft is being made available immediately.

Attribution: Rohan Arun's PR67 cost-aware selection, oracle and baseline;
Dominik Scholz's new combinations of clearing relations with substantial
OpenAI GPT-6 Astra/Codex assistance; Chafik Boukhalfa's PR60 rank-first rule;
eumemic's PR57 joint compiler; Avi Eisenberg's PR62 graph (Claude assistance).
All earlier source notices, Apache-2.0 terms and conditional all-size compiler,
analytic, routing/recovery and fixed finite-alphabet tape assumptions remain.
