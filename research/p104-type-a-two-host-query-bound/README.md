# Fixed J8 and J9 hosts for Type A QUERY demotion

**NO VERIFIED GAIN.** The comparison uses [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, with the signed caller [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The reproduced comparator has κ = 0.00364665195644.

Use [#7404](https://github.com/CrocSwap/integer-mult-bounds/pull/7404) retiming at Type A port 0. Demote QUERY 1580 and 1659 and retire the productive q factors on roots 0 and 18. Permit arbitrary linear changes inside both fixed four-role blocks, J8 at clock 1423 on (8,0,18,26) and J9 at clock 3058 on (9,0,18,27). Keep the remaining word fixed. The two-host edit is impossible even at q = −1 and unit bodies, a legal signed specialization.

## Two exact obstructions

Write P, M and S for the demoted prefix, inter-host middle and suffix. Write A and B for the old J8 and J9 operations, and E and F for the changes confined to the two blocks. The endpoint difference is

```text
S(B+F)M(A+E)P − SBMAP
 = SBMEP + SFM(A+E)P
 = S(B+F)MEP + SFMAP.
```

The first expansion confines the difference to the eight old post-host suffix columns. This column space has rank seven and the required residual has rank three. All 36 residual columns pass this test. The second expansion confines each residual row to the eight old pre-host rows, selected from P and MAP. Their span also has rank seven. Residual rows 0 and 18 lie outside it. The exact input x₀=2, x₁=1, all other coordinates zero, vanishes on the four incoming roles at both hosts. Any linear change within the first block therefore leaves this input unchanged for the second host, which also sees a zero block. The required output 0 nevertheless differs by 2. A second input x₁₈=2, x₁₉=1, x₂₈=1 gives residual output 18 equal to 4.

Independently strip the invertible old prefix and suffix from the desired endpoint T. The required middle is S⁻¹TP⁻¹. With fixed supports, the rightmost host can change only the columns of its own block and the leftmost host can change only its own rows. At row 19, column 19, both are outside those blocks. The required middle entry differs from the demoted middle entry by 4. This is a second exact obstruction on the same scope.

## Price and verification

The inherited optimistic invoice allows zero added paid calls. Its raw upper is below 0.04270044187346692 at one port, or 4.099242419852824 across 96 ports, before added ordinary implementation and proof obligations. Both support arguments exclude the priced candidate before construction. Verified paid saving and Δκ are zero.

Run from a clean checkout with POSIX CPython 3.12 and assertions.

```sh
python3.12 -I -B research/p104-type-a-two-host-query-bound/replay.py
```

The Git-free command authenticates exact input bytes, regenerates the three deterministic receipts, and rejects altered retiming. The support and corner gates took 0.08s and 0.09s with respective caps of 20s and 30s. The first corner invocation stopped on a scope guard that incorrectly disallowed retained QUERY events between the hosts. The corrected guard checks inclusion of both demoted events. The old two-host endpoint is reconstructed as a passing predecessor control. The corner solver is underdetermined for that predecessor, and its arbitrary particular solution alone does not prove infeasibility. The corruption control changes an untouched middle entry and rejects it. The fixed candidate and its 36 coordinates are exhausted. Full native, caller, precision, tape, and recurrence checks were skipped because there is no candidate word.

[#7404](https://github.com/CrocSwap/integer-mult-bounds/pull/7404) supplies the exact retiming and original carrier analysis. [#7407](https://github.com/CrocSwap/integer-mult-bounds/pull/7407) at `79fed9d6765d1b921b8d5e547af301310a9e259e` supplies the one-host comparison, source-bound replay and optimistic price. #7334 and #7113 supply the retained word and caller. #7362 and #7298 supply the signed stock and directed tariff. OpenAI Codex and subagents materially assisted. Apache-2.0.

## Open next questions

A different host clock, enlarged role interface, or change outside the two fixed blocks remains open. Price one actual change against the unchanged paid invoice. Then check whether it sees either committed separating input or alters the untouched middle entry before attempting any native build.
