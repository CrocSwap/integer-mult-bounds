# Local sprint claim

No pinned coordination issue existed (checked 2026-10-13 12:43 -04:00; open issues were #913 and #650), so
the claim was recorded locally after a 13-second preliminary existence check,
before the threshold census, lower-bound argument and supplier analysis.

- **Track and seed.** 40-49, structural decoder research. Seed 40 from the OS CSPRNG
  (`System.Security.Cryptography.RandomNumberGenerator`, uint32 mod 100).
- **Base commit.** `2921874911956718fcaaaf9396fe8267b3cfa9f0` (selected PR942, κ = 0.001661960547713947).
- **Object.** Bit label decoders I_9 = Σ_j p_j q_jᵀ on the 120 E8 lines minus a puncture, priced by
  rational pairing rank (PR446 Theorem C), on punctures other than the fixed P111 of PR757/PR761.
- **Hypothesis.** Terms pairing two orthogonal punctured lines cost 6; nine such pairs with F2-dual labels
  give cost 54 on 102 ports.
- **Deliverable.** This directory: proof, exact verifier, independent checker, witness, controls,
  favorable pricing, no κ claim.
- **Expected finish.** 2026-10-13 about 16:30 -04:00.

## Candidates considered

1. Complex exact 8-term decoders for 25 ≤ p ≤ 56, extending PR968. Not chosen: complex-only gains are
   capped by the PR589 bit supplier, and PR968's P104 budget already reaches that cap.
2. Complex decoders with n ≥ 9 terms on P112 beyond the single-added-total class of PR845 and #998. Not
   chosen: #998 (also seed 40) covers the nearest class, and general n-term bounds were not bounded work.
3. **Chosen:** bit label decoders under Theorem C pricing on other punctures. PR757/PR761 fix P111;
   PR939/PR954/PR631 use star pricing; PR620's deeper search used star pricing; PR595 lists x = 54/102 as
   unrealised.

## Stopping rule and outcome

Stop the experiment if no nine-pair dual system exists after an exhaustive backtracking pass with one
pair fixed, or once the floor argument and the witness are both checked. Outcome: a system was found in
13 s; the floor was proved for p ≤ 25 with the thresholds 1, 14 and 26; the full count of systems was
stopped after 15 minutes and is not claimed.

The exploratory backtracking domain consisted of ordered pairs of distinct
orthogonal root lines, with one fixed pair (0,1) in sorted doubled coordinates;
extensions had to satisfy B0[a_j,b_k] = delta_jk. It returned three systems and
the first was retained. This was a deterministic witness search after the OS
assignment draw, not a randomly sampled experiment. No complete count or
impossibility conclusion follows from the timed-out counting attempt.

## Submission refresh

The 2026-10-13 refresh covered all 757 open PRs through #1062, rather than the
initial capped 400-item inventory. No issue was pinned. PR1020 treats complex
F2 label-pairing ranks at 26 punctures; PR1008 treats tensor shears on fixed
P111. Neither is a rational pairing-rank result for bit-side punctures through
25. PR757, PR761, PR717 and PR939 retained the source heads listed in SOURCES.json.
An immediate pre-submission refresh through #1068 also inspected #1060's
complex P111 COPY construction: it prices a different physical complex word,
not these bit rational-pairing decoder witnesses. Main remained at the base.

## Result and handoff

Submitted as [PR #1084](https://github.com/CrocSwap/integer-mult-bounds/pull/1084):
research note / exact algebraic decoder and scoped lower bound, not a hosted
supplier or new kappa. The retained witness has cost 54 on 102 ports, and the
written argument bounds the label-decoder cost ratio by 9/17 through 25
punctures. All eight package checks, the staged-export replay and selected
source integrity pass. The checked changed-reader example costs 68/67 and
guards the corrected fixed-reader scope of the PR589-to-P110 diagnostic.

The immediate submission refresh reached #1081. PR1077's arbitrary-complex
eight-term result is also distinct from the binary label-factor/rational
pairing-rank model here. Upstream advanced to
`abdc6a7002abdbcd9e21bfc5e1a795784deacfdf` while this branch retained its exact
base; all seven pinned executable/data inputs remained byte-identical, and
PR942's selected kappa remained 0.001661960547713947. No coordination issue
was pinned, so this is the single local result update.
