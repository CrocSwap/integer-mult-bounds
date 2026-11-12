# One fixed even idle and its displacement

The exact #7113 Type B clock 2866 is `IDLE_ONE` on public role 36 and mask {9}, with ports 15,17,27,34,35,42,47,55. It acts on eight selected stage-9 axes with zero-based indices 73 through 80. At each positive integer column multiplicity f the physical stage body is the m-fold tensor of the exact binary Gaussian matrix C, with m=8f. It acts as identity on all parked axes. The binary matrix C has diagonal (1+i)/2 and off-diagonal (1−i)/2. The two integral Walsh vectors (1,1) and (1,−1) have eigenvalues 1 and i respectively.

For a Walsh address u on the selected axes, the tensor eigenvalue is i raised to the Hamming weight of u. The fourth-root filter gives the identity count at width f as

```text
(2^m + (1+i)^m + (1-i)^m)/4
  = 2^(8f-2) + 2^(4f-1).
```

Here (1+i)^8 and (1−i)^8 both equal 16. The displacement fraction is 3/4−2^(−4f−1), which is at least 23/32 for all f≥1. At f=1 the four eigenphase counts are (72,64,56,64) and the displacement rank is 184 out of 256. The independent calculation checks the literal binary gate in both orientations on all 256 Walsh basis vectors with integer arithmetic.

## Capacity of one smaller child

Fix one parked fibre. Allow arbitrary linear maps A and B independent of the stage body, and one body-dependent child K whose selected dimension is at most 2^(rf) for r≤7. Retain the old bypass, require identity erasure at K=I, and forbid coupling across parked fibres. Relative to erasure, the added operator factors through the child as B(K−I)A. Its displacement rank is at most 2^(rf), at most half the original 2^(8f) selected volume. That is strictly below 23/32 of the original volume. It rules out the entire declared one-child rank range even when routing, setup, ownership and restoration are granted free. The scope includes arbitrary dirty input on each fibre. A bypass depending on the body, mixed parked fibres or a different erased map changes the hypothesis.

The mode count does not grant a physical role split. At f=1 the 184 active addresses do not form one binary affine subcube. The retained complete-root compiler preserves the entire selected factor inside every descendant and partitions only genuine external row coordinates. A fibre-packing provider would need its own complete-factor-compatible layout, arbitrary-input proof and full pricing.

## Price of the known Walsh lowering

Write W for the unnormalized Walsh tensor on these m axes. The exact action has the form W inverse times the diagonal of the Walsh phases times W. The selected exact boundary identity realizes W with one same-rank C child and Gaussian phase/scale maps. Its inverse has the same recursive child cost because W squared is 2^m times identity. Thus the known standalone lowering spends two rank-eight calls per port where the old word spends one.

The full #7334 profile starts with 741 rank-eight paid positions, 110,519 total paid positions, 22,461 productive positions and rank surplus 1,424. This edit would make those values 749, 110,527, 22,461 and 1,360. With h8 equal to 8^(1−κ), the eight-port raw saving is −8h8 before any ancillary work. The exact directed interval at the incumbent crossing is in `receipts/LEAD.json`. Uniformly for κ below the retained BIT ceiling, κ<0.004 and ln(8)<3 give

```text
8 h8 = 64 exp(-κ ln(8)) > 64 (1-0.012) = 63.232.
```

Both conversions are charged. Even one new full rank-eight conversion per port already consumes the whole removed charge. If extraction, active indexing and both conversions were free and #7397's hypothetical volume-linear tariff applied here, the ideal support saving would be strictly below 18 raw units. That is a price relaxation and gives no such extraction, tariff or implementation.

The unchanged productive invoice and all other paid calls are retained. No candidate word, ownership/tape restoration replay or changed recurrence was attempted after both gates failed.
