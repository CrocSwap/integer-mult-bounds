# Public candidate snapshot

Checked against the open PR list and reported GitHub checks on 2026-10-10, before opening this refinement. Exact values below are conditional κ claims. A priced target without a physical witness is excluded.

| Candidate | Exact κ | Commit | Status and comparison |
|---|---:|---|---|
| [PR244](https://github.com/CrocSwap/integer-mult-bounds/pull/244) | `710346589668175/10^18` | `a568d94f941929232ab393c7d33dc5a30e017892` | Open; 57/59 reported GitHub checks passed and 2 were still running. Its pinned certificate records two identical full eight-stage replays. This refinement is stacked on its common-frame retiming. |
| [PR245](https://github.com/CrocSwap/integer-mult-bounds/pull/245) | `693078488574615/10^18` | `e347f31c5960323f6dca8bfb5a1f529ebac4537e` | Open; its body explicitly makes no record claim, and its exact κ is below PR244. |
| [PR246](https://github.com/CrocSwap/integer-mult-bounds/pull/246) | target `7.277211262868e-4` | `b21f0963da45e7728a47ed1138d438141ef3c1db` | Open; no GitHub checks reported. Its own proof section says C1-C7 and R1-R4 remain open, six required construction bodies are absent (0/6), and calls the number a priced target, not a witness. Excluded from the valid leaderboard. |
| [PR210](https://github.com/CrocSwap/integer-mult-bounds/pull/210) | `710069340338651/10^18` | `b0c058ba979c748bb3a8604bfb6502e9fac9b84d` | Open; all 59 reported checks passed. It is PR244's parity-fused, pre-retiming source527 base. |
| [PR243](https://github.com/CrocSwap/integer-mult-bounds/pull/243) | `709424410568125629699/10^24` | `ab482ea45dd73f0cb80796641528f0ab930c13b5` | Open; all 60 reported checks passed. It applies PR235's fixed prime and `eta=10^-24` to PR240's older profile; its κ is below PR244. |
| [PR242](https://github.com/CrocSwap/integer-mult-bounds/pull/242) | `355023096796131/500000000000000000` | `ef47efc3256a57bacf4273c35faf4b5148be5014` | Open; no GitHub checks reported. Its body pins an earlier PR210 head and its κ is below PR244. |
| [PR240](https://github.com/CrocSwap/integer-mult-bounds/pull/240) | `28376976266399/40000000000000000` | `1068237fdb977f45e68107d118d0eaf0c7a4b516` | Open; all 58 reported checks passed; its profile is below PR244. |
| [PR235](https://github.com/CrocSwap/integer-mult-bounds/pull/235) | `354291207342277673841/500000000000000000000000` | `63e3e9e2f852c72634d4b09d0bbb8fcf1081481d` | Open; no GitHub checks reported. It supplies the fixed-prime method and `Prime.lean` reused here; its κ is below PR244. |
| [PR232](https://github.com/CrocSwap/integer-mult-bounds/pull/232) | target `7.11175695867958e-4` | `e2189f4717eebb5664c20c95924603909d17a47b` | Open, but explicitly a priced target rather than a witness; physical composition obligations remain open, so it is not a valid κ result. |

PR244 is the strongest comparable reproducible physical candidate found in this snapshot. Its full GitHub CI was not yet complete. PR246 has a higher priced number but no physical witness and open proof obligations, so it is not comparable as a result. The table is point-in-time; recheck the public frontier before review and after CI.
