# Envelope-ordered carry exchanges

The frozen witness in `selected-both` has conditional
κ = **51738676045141/10^18 = 5.1738676045141e-5** and bit saving
**25870676537201/(5*10^17)**. It composes PR #74 envelope-node ordering with
PR #71 anchored split frames and PR #70-style carried-signal exchanges.
Physical width is 134,095,520, with 27,256 and 35,720 auxiliary roles.

Both compiler dirty-basis checks, independent serialized replay, actual paid
transition profiles/CRT and exact moment/assembly checks passed; see
[the completed receipt](validation-receipt.json). Both words and the complete arithmetic certificate also regenerated exactly;
see [the reproduction receipt](reproduction-receipt.json). Broad repository
checks and CI review remain pending. The source and artifact closure is pinned in
[selected-both/MANIFEST.json](selected-both/MANIFEST.json); see the
[proof and attribution](selected-both/PROOF.md) and
[exact certificate](selected-both/arithmetic.json).

Prepare the exact inherited sources from the repository root:

```sh
mkdir -p research/round6-pr71/baseline
git archive 1bef94fd40a746452548c84a4a8f8834670a3113 | tar -x -C research/round6-pr71/baseline
cd research/round7-scheduling
python3 verify.py
# Include deterministic compilation of both complete words:
python3 verify.py --regenerate
```

The archive is ignored and contains no local changes. The proof gives fresh
compiler/profile regeneration commands. Assert-enabled Python and C++17 are
required; `CXX` may specify a compiler and SDK. Inherited repository CI remains unchanged. The commands above provide local
replay and deterministic regeneration of the selected witness. All inherited all-size compiler, analytic, routing, recovery and
fixed-tape hypotheses remain conditional. No global optimality, unconditional
theorem or practical speedup is claimed.

Thomas DiFiore contributed PR #74 ordering; Chafik Boukhalfa, PR #71 anchored
split frames and next-use pricing; Alejandro Zarzuelo Urdiales, PR #70
exchange methodology; Rohan Arun, PR #65/#67 schedules, profile-cost selection
and exact arithmetic; Dominik Scholz, PR #68 live controls and this composition,
with substantial OpenAI GPT-6 Astra assistance. All inherited authors and
license notices remain preserved.
