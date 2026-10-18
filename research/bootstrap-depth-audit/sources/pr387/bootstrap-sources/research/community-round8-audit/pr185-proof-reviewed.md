# Finite stopped-leaf bootstrap

This package changes the ordinary bit supplier used at stopped leaves. It retains PR182's physical graphs, signed/F2 words, frames, handoffs, terminal sinks, coarse histograms, prime witnesses and paid complex bridge. The endpoint and all-size contracts remain conditional in exactly the source-specified sense. The checks establish finite arithmetic and pins; they do not machine-check the following composition argument.

Let `A_0` be the completed ordinary binary interchange supplied by immutable PR182 commit `af90b94783f7d104a0be75c762ade758bec75855`. Its certified ordinary saving is `a_0`, and its coarse saving is `c = 41316503191007/62500000000000000`. This definition names the original, unbootstrapped algorithm, including its old stopped leaves; it does not refer to the new algorithm.

## Required completed leaf contract

`A_0` handles arbitrary widths, two complete address chunks, arbitrary intervening and preceding complete spectators, and restores preceding row coordinates. Its ordinary wrapper borrows and restores its required high-digit stock internally. It uses a fixed finite set of tapes. These are the conclusions of `notes/three-stage-cover-rows.tex`, instantiated by the pinned PR182 bit certificate; they are stronger than a scalar matrix identity.

The retained uses of the old ordinary supplier are explicit:

- Weighted leaves: four ordinary atom interchanges, three paid controlled shifts and one fixed sign (`notes/three-stage-cover-bit.tex`, weighted-leaf subsection).
- Peeled atoms and bounded stopped leaves: a fixed number of ordinary width-`w` calls (`notes/stopped-product-interface.tex`).
- Fixed cover routing: a fixed number of ordinary width-`O(w)` calls, besides ordered shifts and fixed scalings (`notes/three-stage-cover-bit.tex`, finite-cover subsection).
- High-part exchange and residual digits: ordinary calls with complete bodies as spectators (`notes/three-stage-cover-rows.tex`).

None of these uses depends on the old numerical saving being `384599/10^10`. They consume the completed ordinary endpoint and its time bound. A radix-q atom may be numerically padded to the next binary power, applied to this complete ordinary interface, and unpadded at the completed endpoint. Padding the two exchanged ranges costs a volume factor below four; the original old-leaf prime need not match q. The exact same argument permits a new completed ordinary leaf. It does not grant a weighted operation or a reversed operation for free.

## Acyclic construction

Define `A_j`, for `j = 1,2,3`, by the retained PR182 stopped coarse construction with atom width `w = ceil(e^c)`, and use only `A_(j-1)` for the ordinary leaf/routing/high-part calls listed above. All ordered adapters and rare-class fallback children remain paid. Coarse recursive calls still decrease their atom count; calls to an ordinary leaf strictly decrease j. There is no call from `A_0` into any new level and no infinite bootstrapping limit is used.

At each fixed j, the stopped moment proof gives, after ordinary conversion and row borrowing,

`T_j(e)/V = O(e^(1-c) + e^((1-c)(1-c)+c(1-a_(j-1))) + e^c log(e))`.

Consequently define

`a_j = (1-c)c + c a_(j-1)`.

Because `a_0 < c < 1/2`, induction gives `a_(j-1) < a_j < c < 1-a_j`. Thus both the atom-adapter toll (`c > a_j`) and row-borrowing toll (`c < 1-a_j`) are strictly lower order. All gaps are positive fixed rationals. The very small depth-3 gap affects asymptotic constants and thresholds; it is not a practical speedup claim.

Independently, `a_j = c - c^j (c-a_0)`. The verifier checks this closed form against every recurrence step. It also checks `kappa < a_j/(1+a_j) < c/(1+c)`.

## Nested row restoration and fixed tapes

The outer construction's row stock still has `log_q S(e,w)=O(w log e)`: its unchanged cover recursion supplies that stock, and its new ordinary leaves need no *external* extra stock. When an inner `A_(j-1)` borrows high digits, it borrows from the two chunks passed to that ordinary call, retains all outer fields as complete spectators, and restores its row coordinate before returning. Hence the parent sees exactly the original complete ordinary interchange. The parent does not assume a raw reversed operation preserves a borrowed range.

The parent high-part exchange has width `k=O(w log e)` and costs `O(V k^(1-a_(j-1)))`, conservatively bounded by `O(Vw log e)`. Its own internal borrowing is included in that completed bound. Nested padding factors and program/tape counts multiply only across three fixed levels, and each completed interface restores its rows. They remain constants independent of input size. This is finite program composition, not a new unbounded stack of tapes or an uncharged row multiplier.

For fixed positive c and fixed wrapper depth, ancestor and prefix-control descriptors remain polynomial in each active atom width. The complete q^w target fibers absorb their polynomial preparation, as in notes/three-stage-cover-bit.tex. Wrapper constants may depend on the selected level but not on input size; no growing-depth program is used.

The bridge retains the original external row coefficient and its extra 252 ordinary-leaf allocation conservatively. **252 is not asserted to be the new leaf's actual internal reserve.** The new leaf's additional externally supplied stock is zero because it uses its completed internal-borrowing wrapper. The old allocation remains unused slack. All complex finite-group, scalar, router and precision formulas are rechecked unchanged by the parent validator.

## Exact assembly and scope

Only the uniform-bit fields of the bridge change. The validator reconstructs the new leaf saving from the pinned original PR182 certificate and the exact finite recurrence. It rejects a fictitious base, detached saving, unpaid atom exponent or external-row assumption. It separately runs the complete original bridge validator with the original leaf fields, preserving every scalar, complex, finite-group and row formula. The unchanged 47-constraint assembly body then consumes the newly checked ordinary saving.

Depth 3 gives `kappa = 660627334074291/10^18`, approximately `0.000660627334074291`, a `0.062219284%` improvement over PR182. Both physical supplier moments are recomputed with rational intervals; the next coarse grid point is excluded. All 47 constraints, seven margins, and the next final grid exclusion are checked. The finite physical words themselves are inherited as source-pinned evidence and are not claimed to have been newly replayed by the arithmetic verifier.

This is a compositional improvement to the retained conditional ordinary-supplier interface. It does not improve the coarse physical profile, prove the analytic/fixed-tape hypotheses independently, or establish global optimality. PR183 records the existing assembly ceiling; it does not perform this finite ordinary-leaf replacement.
