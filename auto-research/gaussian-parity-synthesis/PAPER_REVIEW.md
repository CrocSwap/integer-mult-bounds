# Independent review of the community synthesis package

Reviewed at 15:12 UTC, 8 October 2026.

The mathematical claims in `outputs/community-parity-synthesis.tex` pass
review. The scalar proof uses the actual mixed-center producer image,
requires one common scalar frame, cancels arbitrary dirty auxiliaries by
finite differences, and collects the final numerator before exact division.
Six additional fractional bits versus zero is correct for the two explicitly
named scalar reference schedules. Their quotient counts are schedule-specific
and exclude image regeneration and physical transports, as the paper states.

The completed-child profile formula and stated 49.8644396% reduction are
correct for that charge component. For even D, the real matrix of C_D has
2^D nonzero coefficients per real row, each of magnitude 2^(-D/2). For odd
D, each row has 2^(D+1) real coefficients of magnitude 2^(-ceil(D/2)).
Consequently the component-box amplification is bounded by 2^ceil(D/2).
The distinction from complex-modulus amplification at odd D is correct.
Unit phases and whole-record address permutations preserve both return grids
and the component-box norm. The scalar constant, unfinished recursion,
normalized H0 boundary and physical schedule remain separate obligations.

The initial review requested four corrections: the precise fast-path function
name in README, explicit integer-image typing in Eq(3), old/new port arity
checks before zip plus source arity checking, and validation of the profile
against its actual pinned certificate rather than only stored hash metadata.
All four are now implemented. Eq(3) requires a Gaussian-integer candidate
Q(delta) and P(Q(delta))=delta. The source certificate is vendored and its hash
and exact child rows are compared before profile evaluation.

The new `mixed_center_adapter.py` correctly connects canonical Gaussian
dyadics with the integer image proof. It aligns the heterogeneous sources and
dirty ports to an explicitly promised common pi tag, operates on their integer
numerators, and reconstructs exact Gaussian values at the same tag. Since
the Gaussian class canonicalizes, the recovered values literally equal the
original canonical values. This preserves a common input grid; it does not
make arbitrary physical fractions into Gaussian integers. Two full-size
adapter receipts at tag 11 cover 3276 sources and 13132 dirty ports each.

The unresolved scope is accurately stated: this is a scalar reference and
certificate boundary. The physical implementation has independent role phase
frames and paid transports; common-frame fusion is not licensed without a
transport/scheduling argument. The full tape machine, analytic recovery and
new multiplication exponent are not proved. The new finite all-D tensor
execution formalization is included in the final package and reflected in the
formalization map; it still does not certify the full physical compiler.

No further mathematical correction is required. One optional metadata cleanup:
rename `scalar_E_and_magnitude_guard_unchanged` to
`scalar_E_and_global_guard_unchanged`, since the completed-child component
box charge is sharper while the published global guard remains unchanged.
