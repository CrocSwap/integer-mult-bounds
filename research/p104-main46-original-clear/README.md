# Main-46 final-hop merge on the original #7605 CLEAR contract

The complete signed application certifies **conditional κ = 0.003650666180757** for
`T(n) = O(n (log n)^(1−κ))` under the original five premises. It applies
[#7610's main-46 edit](https://github.com/CrocSwap/integer-mult-bounds/pull/7610)
to [exact #7605](https://github.com/CrocSwap/integer-mult-bounds/pull/7605)
with **the same 74 lifetimes, exact CLEAR forms and owned interfaces**. This
isolates a same-contract gain from a previously published local repair.

| Comparator | Exact certified or reported value | Exact absolute increase | Increase |
| --- | ---: | ---: | ---: |
| #7605 published value | 0.0036504442446 | 0.000000221936157 | +0.0060797027% |
| #7605 independently reproduced framework value | 0.003650444244716 | 0.000000221936041 | +0.0060796995% |

The respective exact percentages are `73978719/12168147482 %` and
`5548401025/912611061179 %` as checked against the decimal inputs by
the replay. The bound also strictly exceeds the upper endpoint of #7605's
exact raw crossing. The selected #7000 record remains `0.00363005817`.
The larger [#7637 report](https://github.com/CrocSwap/integer-mult-bounds/pull/7637)
of `0.0037` relies on an unimplemented common-U supplier.

## Construction and full price

Role 46 skips `914→245→127` for a direct rank-two `914→127`. A basis change
at chart 3 and signed corrections using the existing role-818 arrival restore
both chart-245 recipients before their first outward reads. No paid return
is added. The read at ADD47959 sees the original main-46 value.
[Exact proof and inherited all-size argument](PROOF.md)

| Signed #7113 resource | #7605 | This edit |
| --- | ---: | ---: |
| Paid positions | 110,366 | 110,349 |
| Productive positions | 22,461 | 22,461 |
| Rank surplus | 1,424 | 1,424 |
| Ordinary upper bound | 782,699,212 | 782,685,204 |
| Context precision coefficient | 2,430 | 2,430 |
| Scalar services upper bound | 43,923,200 | 43,929,184 |
| Elementary tape records upper bound | 25,451,474,528 | 25,448,575,552 |

The 17-stage signed caller [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
is pinned at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The native word has canonical
SHA-256 `aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916`.
Local scope includes 1,501 public endpoints, 68 empty owned endpoints, 74
erased rows, 1,599 exact owned-interface comparisons, the COPY guard, all
affected phase and forward/adjoint checks, 3,040 signed catalogue maps,
104 main boundaries, 54 strict and four functional outer inequalities.

## Replay from a clean checkout

From this package directory, use **CPython 3.12**, Git and a POSIX environment.
It fetches the exact public #7605 head and authenticates 138 dependency paths
and the exact #7610 edit list before running the complete candidate.

```sh
python3.12 -I -B replay.py --work ../main46-replay
```

Use a fresh evidence directory outside the package. A local sparse checkout at exact #7605 head
`e1d2756eecf03e146338239fee81772a99ba8d4c` can be supplied with
`--source-checkout PATH`. The optional `--finite-only` mode stops after the
exact literal, signed phase and full invoice screens. The replay needs no
machine-specific tool paths and retains all logs and exit receipts under
the specified work directory. Each complete stage has a 480-second cap.

From the repository root, the registered command checks the sealed artifacts and a directed
invoice independently, with a missing-paid-position control. It uses no network.

```sh
python3.12 -B scripts/research_package.py --package research/p104-main46-original-clear
```

[Verification evidence](receipts/) includes baseline readback, exact differential,
phase and invoice receipts, the native and signed results, and the first
30-second capped exact checker. The differential method resolved that case
with a separate finite check. The clean replay passed both complete stages against their frozen receipts. Native took 257.83 seconds and signed took 250.60 seconds. An empty-checkout acquisition independently fetched and authenticated all exact source files before the finite gates. The artifact/price command covers those narrower checks.

## Credit

DreamingOfClouds supplied the edit and eleven initial coefficients in #7610.
[#7611](https://github.com/CrocSwap/integer-mult-bounds/pull/7611) extends the
main-46 stay removal on #7608. [#7616](https://github.com/CrocSwap/integer-mult-bounds/pull/7616)
previously transferred that larger set to the uncollapsed #7605 basis and
added 39 new lifetimes. The exact paid sequence and ownership extent here
are those of the narrower #7610 repair on the original 74-lifetime source.
Ali Romman's #7605 supplies that source, his replay wrapper and its retained
#7604 lineage. Rohan Arun's #7113 supplies the signed caller. The retained
native, compiler, recovery and interval engine lineage is in [NOTICE](NOTICE).
OpenAI Codex and subagents materially assisted the port, proof, verification
and packaging.

## Open next questions

- Can the #7612 contact rechart coexist with this edit under all 74 original
  lifetimes? Check the five literal role-134/329 events at the next scope and
  require unchanged owned interfaces before fully repricing the composition.
- The five original premises `native_all_columns`, `owned_erasure`,
  `compiler`, `precision_tape` and `analytic_recovery` remain. Start review
  with the exact fork table, #7605 dependency manifest and the two complete
  stage receipts. Admission and formal all-size verification remain open.
