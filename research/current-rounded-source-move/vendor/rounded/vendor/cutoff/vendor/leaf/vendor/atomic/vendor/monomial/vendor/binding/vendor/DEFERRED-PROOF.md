# The selected uniform tree and deferred stock

DLamdata, with substantial OpenAI Codex assistance. Apache-2.0.
This is a conditional source-bound specialization, not a new deferred-reservoir method or supplier admission.

## 1. Sources and the precise implication

PR6110 at `7f82486e987e556a221085092d8f7aff271ecb35` asks for an audit of PR1673's `SUPPLIER-SUPPORT-AUDIT.md` §6. That older source replaces eager transformation of reserved axes by deferred phases at `K=128G`. The selected manifest binds its `bd5b06...` copy. A later PR1673 `review20261014/REVIEW-RESPONSE.md` §2 already writes the mixed T74 tree and full product-stock argument; its different bytes are an attributed predecessor, not the selected copy.

More directly, the selected manifest binds `research/kappa-rebuild/transfer-audit/OUTER-TRANSFER-AUDIT.md` §5 and `FINITE-TEMPLATE-CLOSURE.md` §§2,5,6. Those sources already give the changed **uniform** supplier, sublinear BIT stock, deferred reservations and per-phase padding deletion. The present result supplies the exact PR6030 substitution and an explicit threshold certificate. It does not discover a missing proof of the generic mechanism. The strong-induction formulation also follows the credited PR4100 audit in `research/complex-stopped-recursion-cost/PROOF.md`; that different supplier is not rerun.

Hereafter `U` denotes the selected uniform saving (not the historical source's mixed-unit count), `N=2^H` its fixed rank, `W` its productive fields and `P` its paid rank-one calls. The retained compiler contract is

    P/W < N^(1-U).

All of `N,W,P` are fixed before the eventual input size grows. They are not the raw mixed P104 productive-field count or raw paid-call histogram. At an ordinary width `e=Nf+r`, `0<=r<N`, each paid child has width `f=floor(e/N)` and volume `v/W`; all `P` children are counted, including those acting on owned fields. Thus the normalized child moment is

    mu_x = (P/W) N^(-x).

This is the explicit ordinary contract in `FINITE-TEMPLATE-CLOSURE.md` §§2,5,6 and `architecture/FINITE-PRECOMPILATION.md` §6. The selected review applies its compiler to PR6030. This audit assumes that compiler and physical contract; a rational check of its parameters is not a new proof of integer batching, native operators or tape implementation.

## 2. Exact selected substitution

The pinned PR6030 `RESULT.json` supplies

    H = 65807000000000, d = 1/1400000000,
    U = kappa+6d, b = kappa+5d, a = kappa+4d, q = kappa+3d,
    eta = stop = d, alpha = BIT atom = 1/250,
    sigma = 1-b, tau = 1-a, lambda_prime = 1-q,
    gamma = sigma+eta*b = 1-(1-eta)*b.

Here `eta` is the stopping exponent; the outer group exponent named `beta` is a different parameter. Every displayed equality and the following margins are checked with exact rationals:

| Quantity | Exact value |
| --- | --- |
| `H*(U-b)` | `47005` |
| `H*(U-a)` | `94010` |
| `tau-sigma` | `1/1400000000` |
| `lambda_prime-tau` | `1/1400000000` |
| `tau-gamma` | `6978119347/9800000000000000000` |
| `lambda_prime-gamma` | `13978119347/9800000000000000000` |

Consequently

    mu_sigma < 2^-47005 < 1,
    mu_tau   < 2^-94010 < 1.

These are compressed upper bounds, not equality claims for the unknown materialized `P/W`. They follow from the retained normalized compiler bill; no gigantic `N` or word is constructed. In particular `1/(1-mu_tau)<2`. This small contraction factor does **not** bound the enormous other fixed implementation constants.

## 3. One phase, including integer widths

Fix a phase width `h>=1`, a root active width `e<=h`, and `s=max(N,h^eta)`. All descendants use this same phase cutoff. Stop when `e<=s`. For integer positive `e`, assume:

- a leaf costs at most `c_L v e`;
- an internal node's own work, including its fewer than `N` elementary remainder kernels, is at most `c_N Lambda(p) v e^tau`;
- its `P` children have width `floor(e/N)` and volume `v/W`; costs add with the same constants;
- `Lambda(p)>=1` is one fixed polylogarithm, uniform over nodes and phases.

The internal premise absorbs at most `(N-1)c_L v` remainder work into `c_N`, since `e^tau>=1`. It includes local parking, owned storage, monomial adapters, restoration and actual movement; those are inherited physical obligations, not asserted free.

Use a weighted-tree potential, independently of the induction used by the separate checker. For an exponent `x>0`, put node mass `v e^x`. Floor contraction implies that its children's total mass is at most `mu_x` times its own. Therefore the total `tau`-mass at depth `j` is at most `mu_tau^j v e^tau`, even after leaves stop. Summing the strict geometric series bounds all internal tolls by

    c_N Lambda(p) v e^tau/(1-mu_tau).

For the leaf term, replacing an internal frontier node by its children cannot increase total `sigma`-mass, because `mu_sigma<=1`. Repeating this replacement on the finite stopped tree gives leaf mass at most `v e^sigma`. Each leaf has width at most `s`, so `e_leaf <= s^b e_leaf^sigma`. Thus

    T(e,v) <= v [c_N Lambda(p)/(1-mu_tau) e^tau + c_L s^b e^sigma]. (1)

The tree is finite because every internal child has positive width `floor(e/N)<e`. No equal-depth assumption or monotonicity of the cost function is used. Zero-width active calls cost nothing and may be omitted. Since `s^b<=N^b h^(eta*b)`, (1) at `e<=h` implies

    T(e,v) <= v Lambda(p) [c_N/(1-mu_tau) h^tau + c_L N^b h^gamma].   (2)

Both exponents are strictly below `lambda_prime`. The endpoint `e=s`, widths below `N`, and every remainder are covered. Choosing a larger finite elementary base threshold changes `N^b` in this bound to that base threshold's `b`-power, not the exponent.

## 4. Actual BIT atom and an explicit deferred threshold

The historical transfer audit's `0.003` atom cannot be copied numerically. The selected ordinary BIT atom is `alpha=1/250`. Retain the same stock contract, now `log S(e)=O(e^alpha log e)` (an inherited BIT implementation premise). A BIT call has width `O(h (log p)^2)`. For `1<=h<=p` and a further `O(log h)` nesting factor, its logarithmic product stock is `O(h^alpha L^(2alpha+2))`, where `L=max(1,ceil(log2 p))`. Because `alpha<1/2`, this is bounded by `O(h^alpha L^3)`. Complex row stock is `O(log h)`. Taking a product adds logarithmic stocks; replacing that product by a maximum is not justified.

Choose one fixed `C>=1`, independent of `h,p`, that covers these constants and complete-chunk rounding. The conservative reservation premise is

    R(h,p) <= 3h/128 + C*(log2 h + h^alpha L^3 + 1).          (3)

An internal-stock implementation can use less. This audit does not numerically materialize `C`; its finiteness and the local stock law remain part of the inherited physical/compiler contract.

Here is an explicit sufficient threshold, for any additional fixed finite base threshold `M>=1`:

    H0(p) = ceil(max(M, 16, (192C)^2, (192C L^3)^(250/249))). (4)

For `h>=16`, `log2 h+1<=2 sqrt(h)`. Indeed it holds at 16, and the derivative of `2 sqrt(h)-log2 h-1` is positive there and beyond. For `h>=H0`, therefore,

    C*(log2 h+1) <= h/96,
    C*h^(1/250)*L^3 <= h/192.

The latter is exactly the threshold inequality `h^249 >= (192C L^3)^250`. Hence the excess in (3) is at most `h/64`, and

    R(h,p) <= 5h/128 < h/16.                               (5)

The degree of this explicit tail bound is `750/249=250/83` in `L`. All fixed constants, including those of the enormous uniform word, affect its coefficient and `M`. This is not a practical or numerically emitted PR6030 cutoff.

## 5. Completed layer and the removed hypothesis

At phase width `h`, expose complete selected neighborhoods in the **global complete tensor**, reserve `R` chunks, execute the ordinary active call, and return every reserved/spectator coordinate unchanged. Do not first transform reserved selected bits. The next phase acts only on those `R` selected bits. Exposure and restoration cost `O(V Lambda(p) h^tau)` under the retained support router.

One phase pads its row count by a factor below two. Its complete endpoint is identity on the row coordinate, so appended zero rows return to zero and can be deleted **before** inverse placement and the next phase. Thus each phase volume is below `2V`; it is not `2^j V` at phase `j`. Exact return is an explicit premise: this argument does not authorize dropping rounded nonzero rows or clear residual errors for free.

Above (4), successive widths obey `h_(j+1)<=h_j/16`. With `l=lambda_prime>1/2`,

    sum_j h_j^l <= g^l/(1-16^(-l)) <= (4/3) g^l.

By (2), `tau<l`, `gamma<l` and `h>=1`, all active-phase work, padding and exposure sum to `O(V Lambda(p) g^(1-q))`. The remaining at most `H0(p)` selected bits cost `O(V H0(p) polylog p)` elementarily. Since `g>=1` and (4) is polylogarithmic, the full result is

    T_layer(g,V,p) = O(V g^(1-q) polylog p),  1<=g<=p, under the stated contracts.       (6)

The cost implication is uniform over those roots **when the complete-layout and router premises hold**. It does not construct geometric support for every `g<=p`: the selected caller uses polynomially sublinear `g=Theta(p^beta)` with `beta<epsilon<1`, so its `O(g log^2 p)` reservoirs and complete neighborhoods fit eventually. In particular, this audit does not grant that geometry at `g=p` in a `Theta(p)`-bit address.

The original `d^max(1-c,0)` term prices eager transformation of reserved axes with the old power-width choice of `K`. Equations (3)–(6) replace that operation. They neither choose a positive `c` for logarithmic `K` nor instantiate the old theorem literally. At polynomially growing outer group widths, the strict exponent margins absorb any fixed polylogarithm after a new eventual threshold. Arbitrarily small `g` is covered by the explicit polylog factor in (6).

## 6. Boundary of the conclusion

The exact selected arithmetic and conditional potential/threshold argument pass. The source-selected uniform contract, complete global fields, fresh product stock, support router, node-local tape bill, exact return/padding deletion, native all-column behavior, owned erasure and analytic recovery remain inherited. No complete selected replay, rounded multiplier, materialized uniform word or physical compiler proof is supplied. In particular this resolves the cost implication under those contracts, not all five selected framework assumptions.

The added value is a current-source answer to PR6110: cite the already-selected finite-template/outer-transfer sources, use the compiled uniform tree, record the compressed moment witnesses, and replace the historical stock atom. It is not a new kappa or a correction to the selected frontier.
