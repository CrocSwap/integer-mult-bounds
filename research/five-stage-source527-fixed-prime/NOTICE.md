# Attribution and licence

This refinement is Apache-2.0. The baseline package's original source notices are preserved in `../five-stage-source527-banks/` and remain applicable to inherited construction and proof material.

- eumemic (PR244, head `a568d94f941929232ab393c7d33dc5a30e017892`) supplies the exact common-frame retiming witness, retimed 527-source word, and its physical verification. The full parent package is pinned by its manifest hash in `SOURCE.json`.
- eumemic (PR210, head `b0c058ba979c748bb3a8604bfb6502e9fac9b84d`) supplies the parity-fused 527-source helper, five-stage construction, stage-private banks, and inherited finite interfaces used by PR244. Its original notice is retained in the baseline package.
- Gabriele Nespoli (PR235) supplies the fixed-prime refinement method and the unchanged `Prime.lean` proof copied from commit `63e3e9e2f852c72634d4b09d0bbb8fcf1081481d`; its SHA256 is recorded in `SOURCE.json`. The source's OpenAI Codex disclosure is retained. Mathlib contributors supply the Lucas-Lehmer criterion and arithmetic tactics used by that proof.
- Rohan Arun (PR243, head `ab482ea45dd73f0cb80796641528f0ab930c13b5`) supplies the `eta = 10^-24` outer-backoff refinement, first applied there to PR240's older bank profile. Its Anthropic Claude assistance disclosure is retained. This package independently rechecks the smaller backoff on PR244's retimed profile.
- Earlier contributors, including the PR230 frame and PR237 bank lineages, retain the attribution and AI-assistance disclosures in the pinned baseline notices.

The new contribution transfers the exact rare-class density `2m^3/q` and finite ordinary bootstrap to PR244's retimed profile, rechecks PR243's outer backoff, and replays the complete PR244 verifier before accepting the refinement. OpenAI Codex prepared this transfer with substantial AI assistance. These credits do not imply review or endorsement by the named contributors.
