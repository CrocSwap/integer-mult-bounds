# Certify structural prefix widths for generated two-output routes

The earlier carry width bound grows with the expanded nonswap count and
loses the disjoint-coordinate structure of tensor and guard copies.

This supplement certifies every forward/inverse prefix of the retained
recipe grammar. Direct sums use maxima; products and tensors use sums;
conjugations and guards pay both boundary factors. The proof includes
partial copies and ordered-addition/signed-scale lowering.

A fixed denominator 2^d gives d+e+9 signed work bits after combining the
complete update numerator and dividing exactly. Fixed-base tensor families
have O(log N) width despite exponentially expanded words. No analogous
depth bound is asserted for arbitrary or complete selected recipes.

Exact source-bound tests compare matrix-prefix certificates and rational
low/carry outputs in both directions. Controls challenge wrong norm
direction, endpoint-only bounds, missing boundary factors, undersized
denominators and invalid separate division.

This is a local width discharge, with #5841 and the previous two-output
producer credited as dependencies. Native private-H grids, physical payload
permutations, owner return and complete admission remain retained. No
canonical assumption or kappa changes. Intended as a coherent supplement
to existing PR #8092.
