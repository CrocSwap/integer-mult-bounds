# Exact product replay improvement

Ali Romman, with substantial OpenAI Codex assistance, changed only the
matrix-product arithmetic and added direct product controls. Apache-2.0.
The proof, fixtures, inverse algorithm, original controls, source pins and
registered commands are unchanged. This work follows the remaining `mul`
question in [PR #4947](https://github.com/CrocSwap/integer-mult-bounds/pull/4947)
by Brian (JoyboyBrian). His inverse-cache result is separate work. At the
checked main `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, the checker still uses
the original inverse algorithm. The timings below compare those exact
main-branch bytes with this change; they do not compare against his cache.

For row `i` of `A`, let `d_i` be the least common multiple of its entry
denominators. For column `j` of `B`, define `e_j` in the same way. Then

```text
(AB)_ij = sum_k ((d_i A_ik)(e_j B_kj)) / (d_i e_j).
```

Both scaled factors are integers. The implementation forms integer dot
products and reduces one Fraction per output. It uses no cache or floating
point arithmetic. The denominator identity proves equality for the valid
rectangular rational matrices used here. Fixed matrix capacities still
apply; this is not an arbitrary-size performance guarantee.

A separate literal Fraction dot-product oracle checks 90 signed, zero-row
and rectangular cases, including dimensions one and ten. Each case checks
input preservation, Fraction result types and independent output storage.
Three further controls check empty inputs, shape mismatch and zero output.
The receipt adds `product_controls: 93`. Every field in the original
`finite_evidence` object remains equal, including all rejection-witness
counts. No original check is skipped or cached.

Local sequential CPython 3.12.13 trials on macOS measured full normal
replays of 19.488/21.431 seconds before and 16.765/16.696 seconds after,
before the small new product-control group was added. These are two trials
per version on a shared host, not a statistical or cross-platform guarantee.
A final sequential pair, including the new controls, measured 19.814 seconds
before and 16.715 seconds after (about 16% less time). Both registered
normal and optimized replays pass with identical original evidence. No new mathematical
bound, kappa change, compiler change or selected replay is claimed.

The proof document remains byte-exact because `full-downset-allocation`
authenticates it as a frozen input. This runtime note is separate.
