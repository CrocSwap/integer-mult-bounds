# Independent skeptical Walsh and frame review

PASS for the stated finite identities and the explicitly restricted character-column frame result. No substantive mathematical or code defect remains in the reviewed files. This review does not admit a helper circuit or infer an improved kappa.

The separate `review/walsh/replay.py` consumed the frozen geometry and the two receipts, without importing either audited script. It checked all **958,521,600 ordered pairs** using int64 arithmetic and a different 173-row chunk. The receipt is `review/walsh/RESULT.json`; replay took approximately 19 seconds with the bundled Python 3.12 / NumPy runtime.

## Exactness, rank, signs and overflow

- The complete histogram independently agrees at every attainable pairing. Its odd-pair support is 480,337,920 and its exceptional count is 3,363,840. The exact fraction is 73/10424, approximately 0.7003069838833461 percent. The replay separately checks the saved integer, fraction and percent against the newly measured histogram; reintroducing the earlier scalar-loop shadowing of the exceptional count would fail these semantic checks.
- All selected vectors have squared doubled norm 16, are distinct, and have positive first nonzero coordinate. Cauchy--Schwarz and that canonical orientation eliminate -4; +4 occurs only on the diagonal. Both the diagonal and the range were checked everywhere.
- Independent Bareiss elimination gives the eight-root Gram determinant 1, and the saved integer inverse multiplies to identity. Together with the binary rank-16 label span and invertible alternating form, this proves `rank_F2(B)=16`. The README's surjection/injection argument is valid. This says nothing about rank 16 over the reals.
- The audit's `P` and dot products are int64. Coordinates have absolute value at most 4; even the deliberately loose 16-coordinate absolute dot bound 256 is far below overflow. Actual pairings lie between -12 and 16 before division by four. With `t` in [-3,4], int16 cubing is bounded by 64, the loose bound for the diagonal-adjusted expression is 108, and all products in the scaled compensation identity are safe. Binary uint8 multiplication in the audited single 16-coordinate stage sums at most 16; packing fits uint32. The full Walsh sum peaks at 65,536 and uses int64.
- The exact signs are `48 delta + 4t - t^3 = 3t B - 24 sign(t)[abs(t)=3]`. In particular t=+3 gives -15, t=-3 gives +15, and the diagonal gives zero. Reversal or omission of the exceptional term is a real error.
- The full 65,536-label Walsh matrix has orthogonal divisor 256: character orthogonality gives `WW^T=65536 I`. This does not apply to the port matrix, whose labels repeat. The weighted compensation coefficient is 1/32 after substituting `B=(J-W)/2`; weights are coordinates of P/2. The factor-four warning for weights P is correct.

## The 16-bit parity labels and 17-bit addresses

These serve different purposes but agree through an affine embedding. The independently replayed identity is

`p_u dot p_v = 1 + B_uv (mod 2)`

on every ordered pair. The 17-bit addresses are odd-weight and the 16-bit symplectic labels and addresses have exactly the same 14,670 fibers; the replay verified the map in both directions. Thus a final Walsh output at one parity label really does feed a single address bucket. The additional affine bit explains why the address span is 17 despite parity rank 16; confusing the two dimensions would invalidate the frame argument.

## Scoped frame conclusion

Every coordinate support has an independently verified rank-17 address span, with the saved 17-port witnesses bound to the actual port coordinates and addresses. Repeating one witness reduces rank to 16. Because character signs are nonzero, an isolated weighted character decoder has that same support. Its supported target caps intersect in zero, and its corresponding directly gathered encoder support spans FULL. A single aggregate whose architecture gathers at one common frame and scatters at one common frame therefore must bridge FULL to zero, a rank-17 private descent under the inherited private-copy interface. This remains a conditional architecture statement, not admission of that descent or a lower bound for all arithmetic DAGs.

The restricted-label positive control independently has address span 1 and common cap dimension 16. It correctly separates final FWHT output buckets from global character columns. Shared intermediate gates, cross-channel cancellation, low-frame routing, virtual entrances, ordinary stock-bearing restored helpers, target chronology and alternative factorizations remain outside the negative result. The README and receipt explicitly preserve these limitations.

## Remaining proof boundary

All computational claims here are conditioned on the pinned `construct_shell()` geometry; this review independently checks its selected vectors and their pairings, rather than replacing the geometric shell enumeration with a new enumeration. The missing contribution remains an emitted, arbitrary-dirt-restoring scalar word with legal common-frame chronology and its full bank invoice. Neither the Walsh identity, the support fraction, label count, binary rank, nor the character-column support witnesses supply that contribution.
