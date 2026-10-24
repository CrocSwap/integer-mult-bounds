# Exact monomial adapters across unequal physical charts

Let E and G be invertible linear coordinate maps on a vector space V. Two physical registers contain u = E x and v = G y for arbitrary independent x and y. A logical two-role monomial map has matrix [[0,a],[b,0]], with nonzero rational a and b.

**Sufficient construction.** Exchange the two physical register contents and multiply them by a and b respectively. Declare the new coordinate tags to be G and E. The first output is a G y = G(a y), and the second is b E x = E(b x). Thus the decoded logical endpoint is exactly (a y,b x), even when E and G differ. No Fourier transport is required by this adapter, and it allocates no additional arbitrary or owned field. Rational scalar multiplication is charged by its existing scalar tariff.

For the standard three-ADD identity x += a y; y += b x; x += a y with a b = -1, its exact logical matrix is [[0,a],[b,0]]. Thus an isolated such scalar block may be replaced by the adapter above. Interleaved operations on entirely different registers commute with the block. An intervening read or write involving either participating register is not automatically movable and is a barrier unless separately proved harmless.

**Subsequent cost and endpoint obligations.** All later scalar contacts and warps must consume the new coordinate tags. Required transports to their declared charts must be synthesized and fully priced, including nonnested transitions. Final native ABI charts and arbitrary-input ownership must be restored. The local adapter itself gives no global paid-profile improvement until this propagation is performed. No Clifford conjugation is assumed free.

The exact source scan in monomial_scan.py found 548 candidate monomial intervals per orientation of #4470's emitted native word. Of these, 536 are three-ADD signed swaps. monomial-blocks.json records event indices, literal operations and exact rational matrices. This scan is discovery evidence; a selected replacement still requires complete physical frame and endpoint replay.

Source: Cinna Davis / 1337isnot1337's #4470 native word, its retained contributor lineage and native_joint.py. New scan and adapter argument prepared for Dugongue with substantial OpenAI assistance. Apache-2.0.
