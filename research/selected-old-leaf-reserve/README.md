# The old-leaf reserve of the selected BIT stage is one

**Source-bound audit with exact finite checks. No new κ.**
The selected conditional exponent stays 60403/20000000.

## Result

This concerns the one ordinary-BIT stage of the selected record #4470. Its
borrowed digits (DELAYED-COVER-BRIDGE §8) are

```text
k ≤ D·(N²(w−1) + ceil(log_q(B·|GL_N(F_q)|))) + ceil(log_q S_old) + 1.
```

[PR #4954](https://github.com/CrocSwap/integer-mult-bounds/pull/4954) left
the old-leaf reserve `S_old` as its last non-numerical factor (open
question 1). This package derives it.

1. **`S_old = 1`.** The external old-leaf factor is trivial, so the
   old-leaf term contributes exactly one digit and `k = k_par + 1`.
2. **Conservative fallback.** Suppose one instead used the
   multiplication-assembly route to supply the old supplier's rows. Then
   `log2 S_old ≤ 252·ceil(log2 e')` at the largest old-supplier call width
   `e' ≤ e`. At #4954's fit threshold this gives `k_old ≤ 103` digits.
3. **Consequences.**
   - #4954's fit side, `log2 e ≥ 52182660963735`, now needs only the `B`
     hypothesis `c_B ≤ N²`. The `S_old` hypothesis holds under either reading.
   - `lockstep-live-role-audit` assumed `log2 A_old ≤ 64`. This becomes
     `A_old = 0` (primary), or `log2 A_old ≤ 9` (fallback).
   - `log2 C` is unchanged, because its complex row share dominates by more
     than `10^13` bits.

The six-bit window of #4954 remains. It depends only on `B` now.

## Chain of custody

Every step below is a verbatim phrase checked against a pinned source.

1. **The stage's old saving.** `research/query-thinned-controllers/PROOF.md`
   uses the "retained old ordinary saving a_old=0.0000384599". The bridge
   reserves `W(w)^D * S_old` and exchanges high pieces "with the old
   arbitrary-width supplier".
2. **Its call sites.** The pinned notes call the old supplier for:
   - weighted leaves (`three-stage-cover-bit.tex`: four old atom interchanges);
   - fixed cover routing (the same note, and bridge §6);
   - peeled atoms and small stopped leaves (`stopped-product-interface.tex`,
     with radix-q atoms padded to a binary power);
   - the width-`k` high-part exchange and residual digits
     (`three-stage-cover-rows.tex`).

   These are exactly the four uses PR185's reviewed proof enumerates. That
   proof also notes that none of them depends on the numerical value
   `384599/10^10`.
3. **Which supplier has saving 384599/10^10.** In
   `certificates/copied-centers-network.json` the BIT saving is
   `384599/10000000000`, with `W_b = 188181929 = 2N + B_a + B_b`,
   `m_b = 575` and largest child 529. `notes/copied-centers-bit.tex` sets
   `a_b = 384599/10^{10}`. It states that the complete-row mixed-width proof
   in `notes/batched-bit-rows.tex` "therefore gives the all-width interchange
   interface".
4. **That interface borrows its own rows.** The paragraph of
   `notes/batched-bit-rows.tex` titled "Supplying the bit rows from existing
   digits" works as follows:
   - At width `e` it takes the least `ρ` with `q^{2ρ} ≥ W^{D(e)}`, so
     `ρ = O(log e)`.
   - It exchanges the high `ρ` digits of **its own two chunks** and gathers
     them into a row field.
   - It pads that field once, by a factor below two, and recurses at width
     `e − ρ`.
   - It removes the padding and undoes the gathering.

   In the note's words, "The row digits were already part of the two input
   chunks". Smaller widths use individual-digit interchange. Every call
   restores its row index.

So each old-supplier call draws its rows from the two chunks it is handed,
which are body atoms or the high parts being exchanged. None of these is the
parent's borrowed range, and outer fields stay complete spectators. The
parent therefore needs no external row factor for its old leaves:
`S_old = 1`. This is the same contract PR185 states for its completed leaves
("no *external* extra stock"). Here it is traced to the actual 384599
supplier, rather than assumed.

**Why the fallback exists.** `notes/copied-centers-assembly.tex` reserves a
product `Q = W_c^{D_c(e)} W_b^{D_b(e)}` with `D_j(e) = t_j⌈log2 e⌉` and
`(t_b, w_b) = (9, 28)`, supplied "by the retained physically preceding
transformed prefix". This is the multiplication assembly's own row supply,
not a requirement of the interchange interface. If an auditor prefers that
route, the bit factor is `W_b^{9⌈log2 e'⌉} < 2^{252⌈log2 e'⌉}`.

The verifier checks the ingredients of this fallback:
- `W_b` has 28 bits;
- `t_b = 9` is the least `t` with `575^t > 2·529^t`;
- the batched-bit-rows depth satisfies `D(e) ≤ 9⌈log2 e⌉` on all tested
  widths. This bound is loose, for example `D(2^40) = 233 ≤ 360`.

This coefficient 252 is also the "252 ordinary-leaf allocation" that
PR185 and the #1094 row bill carry as slack.

## Consequences in numbers

The cover prime satisfies `q > 2^26 N^5`, so `log2 q > 5·H1 + 26` with
`H1 = 25986965159937`, read from `query-thinned-controllers/RESULT.json`.

- **Primary.** `k_old = ceil(log_q 1) + 1 = 1`.
- **Fallback.** At `t = log2 e = 52182660963735`,
  `k_old ≤ ceil(252(t+1)/log2 q) + 1 = 103`, far below `e/4 = 2^{t−2}`. As
  a #4954 envelope, `σ_old = 252/log2 q < 1`.
- **Lockstep.** `252⌈log2 e⌉ ≤ 504·log2 e ≤ 2^9 e^δ log2 e`, so
  `log2 A_old ≤ 9 ≤ 64`.

## Scope

Card `selected-stock-envelope` (adversarial audit), scope **refined** to
#4954's open question 1 (see `TASK.json`). This package does not cover:

- the compiled role count `B` or the six-bit window;
- the old supplier's own finite word or its fixed tapes. Its interface is
  taken as the pinned notes state it;
- the outer constant `C`, the complex row stock, precision, or any supplier
  replay.

The conclusion is a source-bound reading of the retained contract. It is not
a new proof of that contract.

Base: canonical main `b91956876e5b4122fd89179f1b57557ff8378f15`, priority
revision 7. The overlap search for `S_old` found only #4954's own posts.
Claim: [#1166 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19138075).

## Reproduce

```sh
python3.12 -B research/selected-old-leaf-reserve/verify.py
python3.12 -B scripts/research_package.py --package research/selected-old-leaf-reserve
```

It runs in under a second. Mutating `W_b`, the fallback digit count or the
batched-bit-rows phrase makes it fail.

## Open next questions

1. **Close #4954's six-bit window from `B`.** With `S_old = 1`, the least
   fitting width depends only on `c_B = ceil(log_q B)`. *First step:* locate
   the compiled role count of the query-thinned BIT producer and bound `c_B`
   sharply against `N²`. *Blocked by:* the role count is not materialized in
   the pinned sources.

## Credit

- JoyboyBrian, #4954, for the stage band and the open question.
- Mark (Matarener), `lockstep-live-role-audit`, for the `A_old` assumption.
- zxv, #4359/#4470, for the delayed-cover bridge and its stock formula.
- Cinna Davis and zxv, for the #4440/#4470 chain.
- The copied-centers, batched-bit-rows and three-stage-cover authors, as
  credited in their notes.
- The PR182/PR185 completed-leaf lineage.

Prepared by James Reed with substantial Anthropic Claude (Claude Code)
assistance. Apache-2.0. No independent human review is claimed.
