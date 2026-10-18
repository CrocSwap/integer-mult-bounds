# Local sprint claim

- Track: bit supplier; OS-random assignment seed **17** (`secrets.randbelow(100)`).
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Claimed: 2026-10-13 05:23:34 UTC; expected finish: 05:58 UTC (13:58 Hong Kong).
- Object: PR543 R420 phase-B block **7 = 17 mod 10**, frame 549,
  original B[471:512], on the unchanged selected supplier word.
- Method: split the original 41-XOR block into its upper/lower triangular
  factors and use an exact subset-state dynamic program to minimize each
  factor among schedules that finish each destination in one contiguous
  batch, using only positive additions from the current other wires.
  Check integer transfer equality, both positive envelopes, literal reverse
  cleanup, all arbitrary-input columns, frames and complete native bill.
- Deliverable: frozen circuit, finite-class optimality certificate, verifier,
  source pins and a scoped research note; no new kappa assumed.
- Three candidates considered: (1) block-7 factor scheduling; (2) punctured
  R439 mini-node basis changes (close overlap with #728); (3) full-frame
  decoder resynthesis (close overlap with #708/#748/#753). Selected (1).
- Distinct coverage: #670 and #674 optimize blocks 3 and 5, respectively;
  #691 changes quad 13; #754 synthesizes cleanup windows on at most four
  wires. This experiment checks all subset states for two twelve-wire
  factors with a precisely stated schedule class, not another stochastic
  rewrite seed or a claim of unrestricted XOR optimality. #681 integrates
  the earlier circuits but does not change block 7.
- Coordination: browser inspection of the issue listing and API inspection
  found only issue #650 (request for Discussions), no pinned sprint issue.
  No reservation issue was created. Initial metadata covered 586 open PRs
  through #767. The repository review ledger ends at #626; later proposals
  are not treated as accepted frontiers.
- Contributor: Yuzhou Wang / @yzhouwang, with substantial OpenAI Codex
  assistance. Apache-2.0. No delegated workers or independent human review.

## Result update (once)

Completed 2026-10-13 05:39 UTC. Submitted
[PR #789](https://github.com/CrocSwap/integer-mult-bounds/pull/789).
The 41-XOR block is replaced by 28 XORs, with exact fixed-factor minima
14 + 14. Charging the literal reverse cleanup saves 26 native ADDs overall:
26,916 → 26,890. No new κ. All 660 dirty columns and frame paths pass;
fresh 5/9/11-stage native checks pass with 96 bridge-omission controls.
Python 3.9/3.14, optimized/relocated/committed-source replay, source and
certificate controls and selected-record integrity pass. Scope, source pins,
proof, inherited obligations and full validation are in README/VALIDATION.
Final overlap refresh through #786 found no block-7 factor-schedule duplicate.
