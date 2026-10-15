# Constructive halo-layout package

The generic layout task has a positive conditional construction. Gather
only the g low `log N`-bit fields using a coordinate permutation supported
on at most `2g log N` positions. Run ordinary cyclic convolution on each
N^g core. Repair only a disjoint union of output face rectangles, using
sparse addressed input copies and paid radix gathers/scatters.

For `N=dyadic(p^(3/2))`, `L=O(p polylog p)`,
`g=p^(1-epsilon-zeta)`, `log s=Theta(p^(1-epsilon))` and epsilon>5/6,
all sparse halo work is O(V polylog p). The initial gather costs
`O(V g^(1-a_bit) polylog p)` and the grouped convolution costs
`O(V g^(1-q) polylog p)`. The cited bounded-gauge variation is still o(p).
Actual parameter exponents are recorded in `PARAMETER-CHECK.json`.

Read:

1. `SUPPORT-ROUTER.md`: arbitrary-spacing guarded shears, support-sized
   reservoirs, fixed-tape repair, and the support-at-most-2k gather.
2. `HALO-THEOREM.md`: tensor identity, exact sparse halo volume, all record
   movement, key lengths, local transposes, final output order and costs.
3. `RECTANGULAR-EMBEDDING.md`: simultaneous near-one zero embedding and crop
   in one scan, using B=Omega(p) record width and an O(p)-bit descriptor.
4. `RAGGED-PERIODS.md`: arbitrary true periods inside that dyadic container,
   using full ragged tiles as exponentially sparse additional exceptions.

No rank/select oracle or sort of the complete tensor by a computed key is
used. Full scans preserve stream order. Only sparse correction records
are sorted, with every key bit pass charged.

Reproduce, from the chat workspace:

```
python3 -B work/halo_layout_ultra/check_sparse_shear.py
python3 -B work/halo_layout_ultra/check_halo.py
python3 -B work/halo_layout_ultra/check_embedding.py
python3 -B work/halo_layout_ultra/check_ragged.py
```

Controls include an exhaustive 32,768-address shear permutation, 4,000
unequal-spacing probes, 5,632 regular-grid convolution outputs and 6,538
true-period inputs for ragged gather/correction checks. Wrong naive cyclic
flattening is explicitly detected before correction. Source/result hashes
are in `MANIFEST.json`.

This is not a complete Gaussian resampler or a larger multiplication
exponent certificate. The kernel must be translation invariant and
separable; a fixed/polylogarithmic composition with bounded and sequentially
generated diagonal conjugations is admitted. A product tree with many
different short kernels or per-axis factor-two padding is not admitted by
renaming it a convolution. The missing Gaussian representation/normalization
theorem remains separate. The original bit/complex supplier, fixed-tape,
precision and all-size interfaces remain conditional inputs.

Prepared with substantial OpenAI Codex assistance, continuing the retained
arbitrary-source router and bulk-resampling proofs in
`work/integer-mult-current/references/semantic-bulk/rad20/reports/`.
No frozen source or selected certificate was changed.
