# Notice and attribution

This package is a composition. It adds no word, no construction and no all-size
hypothesis; it prices suppliers that other contributors certified, and it retains
their notices and authorship.

## Vendored inputs, byte-identical

* `references/pr168-v4/scripts/paired_cube_assembly.py` — the exact balanced
  assembly with the RaD (hipotures) balanced prefix and the gates adapted from
  Zhihao Chen's PR23; prepared by **eumemic** with Anthropic Claude assistance,
  PR168 v4 at `fd25adb7fbaa12ee761d02c733c54d1d2a7687ee`. Apache-2.0.
* `references/pr184/assemble_profiles.py` and `references/pr184/FINITE_BRIDGE.txt`
  — the exact rational pricing, the accepted profiles and the finite bridge;
  **icekylinx** and **GPT-6 Astra**, carried by ikeboy's PR194. The rational
  enclosures are retained from icekylinx's `three_stage_cover_network.py`.
  Apache-2.0.
* `references/pr194/certificate.json` — PR194's published complex profile,
  complex saving, assembly record and kappa (`1668581/2500000000`); **ikeboy**
  (evmckinney9), building on icekylinx's source-assisted line and PR168 v4.
  Apache-2.0.
* `inputs/pr200-bit-certificate.json` — the certified fixed-coordinate and
  face-diagonal bit local circuit, its physical layer, 34 terminal sinks and paid
  moment; **chafreaky** (Chafik Boukhalfa), PR200, with substantial Anthropic
  Claude and OpenAI Codex assistance, and with James Chang's PR166 terminal-output
  substitution, DaysSky's PR162 carrier rule, icekylinx's PR144 configurable
  circuit and the PR189/#196 lineage. Apache-2.0.

## Methods credited

* the finite acyclic ordinary-leaf wrapper and its recurrence
  `a_{n+1} = (1-C)C + C a_n` — **rohanarun**, PR185;
* the packing mechanism on a bit word — **evmckinney9**, PR197 (referenced here
  only as a published figure for what lowering `W` was worth on a different word);
* the endpoint-frame descent — **sennemmi**, PR198 (same, referenced as a
  published figure);
* the pricing recurrence applied to a composed supplier — **Maxime Fleury**, PR199,
  from which this package takes the same operation and generalises it to an
  arbitrary certified bit profile.

## This package

`compose.py`, `verify.py`, `certificate.json`, the workflow and this notice were
prepared by Maxime Fleury with Codebuff assistance, 2026-10-09. Apache-2.0.

The result is conditional. A finite certificate checked here is not a formal
verification of the full multiplication theorem, and no claim is made about the
practical cost of the construction.
