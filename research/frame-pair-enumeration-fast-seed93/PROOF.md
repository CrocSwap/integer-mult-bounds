# Exact order-preserving enumeration

The reference is themilkman216's PR968 `frame_pair_solutions`. We change
its representation of eight-element neighborhoods, not its search domain,
acceptance condition, multiplicity, or output ordering. Both ordered frames
must have eight distinct members and be disjoint. The consumed inner-product
matrix is the source's exact integer matrix on all 120 root lines.

For a fixed selected subset S of the first frame, a second-frame member g
is a permitted partner of f in S exactly when its nonzero neighbors inside
S are the singleton {f}. Encoding those neighbors as an eight-bit integer
turns this condition into `hit != 0 and hit & (hit-1) == 0`. The sole bit
identifies f. Iterating g in its original frame order appends precisely the
reference partner list in precisely its original order. The outer subsets
still run from 0 through 255, and the same Cartesian product runs over f in
the original first-frame order. The injectivity check is retained.

For each first choice, T is the complement of the chosen second-frame
members. A remaining first-frame member f is a permitted partner of g in T
exactly when its nonzero neighbors in T equal {g}. The reverse-neighborhood
mask tests this identical condition. Iterating remaining f in frame order
preserves every second partner list and therefore the second Cartesian
product's order. We retain its injectivity check and construct the same
ordered concatenation of pairs. Empty selected sets use the same empty
Cartesian-product convention. Thus every returned list, including empty
outputs, agrees exactly with the reference, not only up to permutation.

The two adjacency directions are computed separately, so this equivalence
does not silently assume symmetry. Entries are tested for nonzeroness exactly
as in the reference. No sign, coefficient, rank, or downstream duality check
is replaced by a Boolean approximation. Masks only represent membership.

The benchmark includes every one of the 1,260 second frames at the pinned
source, including all 364 without solutions. Both implementations return
the same complete ordered stream, containing 7,168 decoders. In the larger
replay, only the enumeration function is substituted. PR968 sections D, E
and H retain their source code: all 57,344 term-rank checks, all decoder
duality checks, the entrywise example, the 25 attaining puncture cases and
all six inherited controls run in both paths. The default checker compares
the complete proof-relevant output, including order-sensitive stream hashes,
rank-check inputs/results, every log line, all chain fields and census data.

Source assertions are explicitly compiled with optimization level zero,
including when the wrapper runs under `python -O`; an actual nonintegral
pairing input checks this assertion boundary. Missing/changed source pins,
solution omission, duplication, reordering and partner mutation are rejected.
The receipt is compared canonically, with timings kept outside mathematical
equality. A fast machine or a timing fluctuation cannot change acceptance.

This is a scoped enumeration optimization. Sections A/B/C/F/G, full supplier
verification and the multiplication theorem are not claimed as replayed here.
The source E8 matrix initialization and frame construction still run. No
finite census alone proves the universal decoder floor; PR968's proof and
classification premises are unchanged.
