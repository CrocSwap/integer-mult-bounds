# Funded shorter return on exact #7244

The starting program is [#7244 at `215f67247f395c0e15f5ea3980f6a3e4aed155af`](https://github.com/CrocSwap/integer-mult-bounds/pull/7244/commits/215f67247f395c0e15f5ea3980f6a3e4aed155af).
Its canonical word hash is
`56e1a5e60cecf14991b3169b4575f0b7388d48fa39f261d7a20c7627a8d9e540`.
Event indices below are zero-based in that word.

1. Replace the rank-five move of 1499 at 45,667, from chart 1091 to
   chart 127, by the two legs 1091 → 245 → 127. These charts have
   ranks 4, 8 and 9, with strictly nested spans. In normalized coordinates
   the ordered maps are $F_B F_A^{-1}$; their composition equals the
   original map including its phase. The native replay independently
   checks the canonical maps and every affected Gaussian basis column.
2. Let $q$ be the value of 1499 at that move. It is never written
   afterward. Run the eight intervening events at their original charts
   and in their original order; these include both donor arrivals and
   every use of those donors by 996 and 779. Then subtract $8q$ from
   each of 988 and 991 at chart 245 and finish 1499's move. The
   unchanged ADD into 1000 follows that move. It commutes past the eight
   events, which touch neither 1000 nor 1499.
3. At the second cut, let $a,b$ be the two old donor values and $z$
   the new continuation input. The old instructions gather $x=a-b$,
   retire $x$ on 988, and produce the pair
   $(a+(z-x)/2,b-(z-x)/2)$ on 1500 and 991.
   Subtracting $8q$ from both donors before this cut preserves $x$
   and subtracts $8q$ from each member of that pair. Those are exactly
   the two corrections that #7244 applied at chart 127 after the exits.
   The two shifted values have no other readers before the terminal basis.
4. With both corrected fields still at chart 245, apply the original
   three scalar basis operations to 1500 and 991. Send only 1500 to
   chart 127 and return 991 at chart 245. The remaining basis events
   are on different destinations at 127 and use 1499, whose value is
   unchanged. All normalized outputs agree on arbitrary inputs. The
   physical target of 991 is now the rank-eight map from chart 3 to 245.

The [affine delta checker](certificate.py) starts with independent cut
coordinates, verifies both affected boundary blocks and propagates the
common shift through the actual middle word. It rejects an omitted
correction, a premature correction that changes 779, and a wrong
terminal basis. The full replay separately recomputes all arbitrary-input
forward and adjoint coefficients, actual dirty COPY, native chart phases,
ownership, grid, precision, and the signed caller.

Let $H_r=r^{1-C}$ for $0<C<1$. The paid histogram changes by
$P_4+1,P_5-1$: the new rank-one leg of 1499 replaces the removed
rank-one exit of 991. The target histogram changes by $T_8+1,T_9-1$.
Thus the signed moment increases per native by

$$
(H_5-H_4)-(H_9-H_8)>0
$$

by strict concavity. Both rank masses decrease by one and the number of
paid and target positions is unchanged. The signed caller bills this
change at all 17 occurrences. The directed price and outer replay
establish the proposed κ; the concavity comparison is independent of
rounding the new price.

## Attribution and scope

This change uses the two-cut construction and temporal checks from
#7244, the funded rank-eight exit lineage from #7161, and the unchanged
signed caller from #7113. The prior canonical chart and native/compiler
licenses and notices are retained in the exact source archive. The
ChatGPT Pro consultation excluded moving the second retirement earlier
on the fixed itinerary; the present construction uses an already paid
continuation on a changed route. The consultation did not verify this
word. Prepared for Clear1nsight with substantial OpenAI Codex and
ChatGPT Pro assistance, Apache-2.0.
