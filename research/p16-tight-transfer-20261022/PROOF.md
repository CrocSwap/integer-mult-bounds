# P16 tighter critical-root transfer: conditional κ = 0.0030201659769

**Research status (22 October 2026):** a new **exact-rational conditional parameter point** above pending PR #4535 κ=0.003020165, using its *unchanged* PR #4470 physical supplier and PR #4532 critical-root lemma. **No new native algorithm, unconditional theorem, formal proof, independent human acceptance, or maintainer-selected κ** is claimed. Preserve prior contributors and licenses (zxv, Cinna Davis, Jacob Alan Sussman, Dillon, hexapode, Ryanson Jonathan and the complete PR4470 source manifest). New source for @Chrisbryan17 with GPT-6 assistance, Apache-2.0.

## Source pins and exact novel parameter point

- Selected source: `CrocSwap/integer-mult-bounds@b9a13c1673e0e9697de410de16e8bbf3207a7363` (#4470), selected conditional κ=0.00302015.
- Critical-root theorem: `CrocSwap/integer-mult-bounds@644607ba59ebe401ac7ecd627ae7f331f924d1b0` (#4532).
- Pending transfer: `CrocSwap/integer-mult-bounds@a6d7237f697185e857090e174c23c1cb22c6563c` (#4535), κ=0.003020165.
- Original outer equations: `research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py`.

Fix **κ=0.0030201659769**, **d=10^-15**, `s_C=κ+6d=0.003020165976906`. Put `b=κ+5d`, `a=κ+4d`, `q=κ+3d`, `ε=1-d`, `β=1-3d`, `r0=d/10`, `stop=layout=d`; ordinary BIT saving remains 0.0034 and BIT atom=0.004. This uses no new native rank profile.

The pinned PR4470 paid/target histograms, independently checked by `frontier_rational_gate.py`, give a raw critical saving bracket

`0.0030201659770 < κ_raw < 0.0030201659771`,

equivalently critical exponent `θ*∈(0.9969798340229,0.9969798340230)`. Thus `z=1-s_C=0.996979834023094` satisfies

`z-θ_hi=94/10^15>0`.

Under PR4532's fixed critical-root logarithmic majorant `L(n)≤A n^θ*(133+ln n)^(2/5)` with `n0=145×1024^650`, choose the **fixed local compiler rank** `N=2^(10^15)`. Elementary rational comparisons give `ln A<20`, `ln(133+ln N)<50` and `ln N>(2/3)10^15`. Therefore the logarithmic absorption surplus is strictly greater than

`(94/10^15)×(2/3)10^15−20−(2/5)50=68/3>0`.

The derivative `(z-θ_hi)−(2/5)/(133+ln N)>0` guarantees the positive bound persists for all larger ranks. This explicitly funds the logarithmic overhead rather than identifying the raw critical root with a usable saving. PR4535's finite-template closure and arbitrary-height integer compiler are invoked as conditional premises; **their extended code/physical execution has not been independently replayed**.

The exact `Fraction` certificate checks **all 54 original named PR4359 strict inequalities**, **all four functional guards**, **all nine row savings greater than κ**, the unchanged selected raw profile and both moment signs. The smallest positive strict predicate is `d/10=10^-16`; the binding main-transform margin is `εq−κ=2.996979834...×10^-15>0`. The uniform compiler height upper bound becomes `G_depth≤2×10^14`; the conservative class-count bound becomes `C_N<2^(3400000000000031)`. This is astronomically finite and not materialized or practical.

## Acceptance scope

This is an improved **conditional mathematical parameter certificate**, an absolute `0.0000000009769` above the still-open #4535 point and `0.0000000159769` above the official selected point. It does **not** improve the native supplier or certify unconditional `T(n)=O(n(log n)^(1-κ))`: all all-column native, owned scratch, whole-job, physical movement, semantic precision, fixed-tape, analytic decomposition, prime-avoidance, and exact-recovery contracts remain inherited. Peer review and the complete registered PR4532/4535 package replay are still needed. Do not promote this as the maintainer-selected value.

## Reproduction

From this branch:

```bash
python -I -B research/p16-joint-lab/frontier_rational_gate.py
python -I -B research/p16-joint-lab/critical_root_tight_transfer.py
```

The second script emits `TIGHT_TRANSFER_RECEIPT.json` with exact fractions and fail-closed scope flags. A Python 3.11/3.13 GitHub Actions workflow is committed; hosted success is unconfirmed. The 54 check identities are independently transcribed from the credited `endpoint.py`; the smaller conditional proof is an inference from its already documented general transfer theorem, not a second verification of that theorem.

**Next acceptance gate:** separate independent audit of the all-size compiler's quantified arbitrary-rank conclusion and matching source/native premise, then upstream review. Even a tiny exponent record requires both arithmetic and that proof bridge.
