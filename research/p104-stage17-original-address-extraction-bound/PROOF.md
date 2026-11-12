# Original-address stage-17 residual support

Fix exact #7334/#7113, clocks 4646 and 4660 and the changed erased map from #7416. Both literal idles multiply Type B role 36 by D, the stage-17 body on axes 137 through 144. All thirteen intervening events are ADD or SCALE on roles 36, 37, 52 and 53. Let M be their invertible scalar role map. It is tensored with the identity on address coordinates throughout the interval. These events introduce no literal Walsh or other address-basis bridge.

Let e be the coordinate projector onto role 36 and g=M⁻¹eM. Removing M from the output of the old window yields the product of body actions on projectors e and g. The exact normalized replay gives both zero products eg and ge. Thus P=e+g is a rank-two projector, and the old normalized operator is I+P⊗(D−I). Under #7416's grant of the erased action I+P⊗(E−I), the missing operator is P⊗(D−E). The two input lanes are arbitrary and independent in the image of P, where P acts as identity. This matches the exact #7406 normalized projector and leaves the other role directions alone.

## A nonzero entry in every input column

For width f≥1, let m=8f. Set a=(1+i)/2. On the original two-point address basis the binary matrix C has diagonal a and off-diagonal −ia. Consequently D=C^(⊗m) has entry a^m(−i)^k between any two addresses at Hamming distance k. Since a^8=1/16, for a single-bit neighbor the entry is −i·2^(−4f). The replay checks one such pair at width one, row 1 and column 0, using the exact pinned binary entries.

The granted E is ((1+i)I+(1−i)D²)/2. The binary square C² is the address swap by direct multiplication, so D² flips all m bits. E therefore has entries only on equal addresses or full complements. Neither includes a Hamming-distance-one pair because m≥8. The same neighbor entry in D−E is −i·2^(−4f) for every input address at every positive integral width. No additional width experiment is needed for this identity.

## Consequence for fixed-coordinate extraction

Take one fixed parked fibre. Suppose the residual supplier only reads selected original-address coordinates, with arbitrary coordinate permutations or subsets. If it omits one input coordinate of one lane, choose a nonzero input supported just on that omitted lane and address. Every supplied observation is then zero. The missing residual output is nonzero at its Hamming neighbor, so the same observations cannot give the correct residual both for this input and for zero. The erased contribution is already supplied separately and does not count as an observation of the missing operator.

The same argument permits fixed role-scalar mixing at a single address before extraction. If the observed forms at any address have rank less than two on the two-lane space, choose a nonzero lane vector in their common kernel at that address and zero elsewhere. The fixed role-scalar events do not mix different addresses. The residual is again nonzero at the Hamming neighbor. Thus the extractor must retain at least two independent original-coordinate degrees of freedom at every address. This is two full lane volumes in each fixed parked fibre, even for non-affine selection or multiple coordinate-only charts.

Under the inherited volume-linear rank-16 tariff, write H(r)=r^(1−κ). A charged volume t has gross 16H(8)−8tH(16) across the eight Type B ports. With t≥2 this is negative throughout 0<κ<1. Directed rational bounds at the benchmark give gross upper below −126.39 raw. The positive one-volume quote of about 0.320691708235 raw is therefore unavailable to this extractor.

The argument leaves arbitrary address-mixing extractors, a separately proved already-paid outside basis bridge, different erased actions, mixed parked fibres and other tariffs open. It concerns the specified residual operator and coordinate-only inputs. No new physical supplier, dirty-restoration construction or recurrence was built.
