# Conditional refinement: cap interior length independently of d

This is a separate follow-up to the uncapped proof audit. Its current status is **PASS_CONDITIONAL_PHASE_FUSION_REVIEW**, following the independent capped-gauge and capped-layout audits and an integrated root review. It preserves the weaker `OUTER-ARITHMETIC.json` as history. Under the retained supplier assumptions and the reviewed interfaces, the capped construction below gives `kappa=0.001672922349588871`. The only new analytic change is the anchored O(aB) local gauge; all altered operation counts are derived explicitly here. No upstream selected certificate is changed.

Let the original phase-cell scale remain `d=p^epsilon`, and cap dyadic interior lengths at `B=2^floor(b log2 p)`, where `1/2<b<epsilon`. Continue to use the actual logarithmic alpha and maximum physical bandwidth `W=O(sqrt(p) polylog p)`.

Inside a phase cell of length O(d), reserve W endpoints. Repeatedly take a B-point interior followed by a W-point separator while this fits. Apply the already proved dyadic-tail carving to the remaining interval. There are O(d/B) full interiors, at most O(log B) tail interiors, and at most

`O(W(d/B+log B))`

boundary coordinates per original cell. Every interior is separated from the next by at least W coordinates. Thus the boundary density is `O((W/B) polylog p)`, the inherited Schur half-bandwidth stays O(W), and all blocks remain principal restrictions of the same globally rounded matrix. The original physical period cut remains a boundary.

The larger gauge in the uncapped proof can be replaced by a gauge local to each **capped block**. For the narrow matrix, use the exact diagonal ratios `ahat_j/ahat_m` with m an interior anchor. This does not change `diag(ahat) Ghat diag(ahat)^-1`. Within one original phase cell,

`log a_j=-a(1/4-beta_j^2)/theta`, `beta_(j+1)-beta_j=theta`,

so successive logarithmic differences have magnitude at most O(a). Therefore the range on a B-point block is O(aB). The global downward rounding changes this by O(1) once its retained Cp-bit precision dominates the original O(ad)=o(p) absolute logarithmic range. One must form the anchored ratio, not numerically multiply by the old full-cell gauge and later cancel it.

For the broad forward block, choose the anchor m within that capped block in the exact formula of `FORWARD-SMALL-A-AUDIT.md`. Then `|delta|<=1/2`, and its diagonal logarithms vary by

`O((B+B^2/d)/alpha^2)=O(B/alpha^2)`

because B<=d. Its Toeplitz SPD condition and completed finite-block inverse bound are unchanged. Thus O(aB) is a common conservative gauge bound for both directions.

All capped block circuits in one L-point local axis run as a direct sum, so their count does not multiply the polylogarithmic depth. Coefficient tables remain polynomial in p per local group/coarse block. The tensor compiler now permits

`g=p^beta`, `beta=1-b-r-zeta`.

The guard `g*a*B=o(p)` follows from r+zeta>0. The supplier support proof needs each individual K-neighborhood to fit its original axis and total moved support o(p); it does **not** require all g controls to fit within one original axis. The sufficient auxiliary inequality `beta<1-epsilon` in the uncapped ledger must therefore be removed in this follow-up.

The changed principal exponents, normalized by V, are

| Component | exponent |
|---|---:|
| main transform | `1-epsilon*q` |
| fused Gaussian circuits | `epsilon-q*beta` |
| boundary algebra | `epsilon-b+(omega-1)/2` |
| sparse union movement | `epsilon+beta+1/2-b` |
| grouped scans | `epsilon-beta` |

For the boundary row, one axis has O(V W/B) boundary records. A band solve or coupling product on W simultaneous right-hand sides costs O(W^(omega-2)) per boundary record, so all d axes cost `O(V (d/B) W^(omega-1) polylog p)`. The new factor d/B must not be omitted. For the sparse union, its fraction within a group is O(gW/B polylog p); g sequential axis operations and d/g groups give `O(V (dg/B) W polylog p)`. These are precisely the third and fourth changed rows.

All other costs in `OUTER-AUDIT.md` remain paid. Global routing has saving a_eff; packed polynomial products have saving epsilon. Even a conservative full active-group key surcharge adds only `beta+1-epsilon` to the union exponent. Sparse core-face corrections have exponent at most `epsilon+beta-3`, using the former p² per-record allowance on their O(gA/L) copied volume.

With the rational bound omega<45/16, put c=(3-omega_upper)/2=3/32 and take a positive boundary slack s_boundary=10^-5. Balancing the two dominant rows while leaving that boundary slack gives

```
epsilon=(1+q+q*(c-s_boundary-r-zeta))/(1+q)^2,
b=epsilon*(1+q)-c+s_boundary,
beta=1-b-r-zeta,
kappa_limit=epsilon*q.
```

Using the same q, r and zeta as the uncapped candidate yields approximately

```
epsilon = 0.9984838711085557536432677624420451614...
b       = 0.9064167934681446247757331487619919695...
beta    = 0.0935821965318553752242668512380080305...
kappa_limit = 0.0016729223595888711324653863199468081...
kappa       = 0.001672922349588871
```

The boundary saving equals `kappa_limit+10^-5`. The union movement exponent is below 0.686, and even its optional full-key surcharge leaves it below 0.781. The per-record phase metadata exponent `beta+2(1-epsilon)` is below 0.097, so calculating all g membership predicates remains cheaper than scanning one p-bit record. Core-face repair costs remain negligible at L=p^8.

The common compiled H calls are still made globally across complete coarse-label ranges. Each selected bit needs only its own K=128G neighborhood to fit its original axis. Since `1-epsilon>0`, this holds eventually even though gK is larger than one axis width. The total support is O(g polylog p)=o(p), because beta<1. All support-router reservoirs, product row stock and exact endpoint restoration are those of the independently audited supplier.

At the displayed parameters, `b>1/2`, `epsilon>b`, `beta>0`, `epsilon>beta`, `1-b-r-beta=zeta>0`, and `1-epsilon-r>0`. These respectively pay the wide-band separation, cap below original cell scale, growing group payload, number of groups, compiled local-gauge precision, and global gamma/rounding range. The raw global rounded weights may still have O(ad) logarithmic range during offline generation. The **data** only sees exact anchored ratios of range O(aB); approximating those ratios to the retained precision introduces `exp(o(p))` error amplification, already paid by the strict group guard.

The assembled group endpoints are the same full normalized Haug inverse or Saug/4 operators as in the uncapped proof. Changing the interior partition changes only their factorization. It does not change their completed contraction bounds, intended zero-hole semantics, principal-core locality, or the final `2^D` scale compensation. Consequently the uncapped precision and error argument applies with the improved group gauge budget.

`check_capped_outer.py` computes 44 exact positive slacks, every displayed cost margin, and five rejecting controls. The full-cell-gauge control is especially relevant: it fails, so the stronger result depends on the independently reviewed anchored-gauge proof. The local review retains the original supplier and all-size conditional assumptions.
