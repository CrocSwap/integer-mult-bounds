# Independent review of the five-core bridge lemma

Reviewed `FIVE-CORE-WORD.md` at SHA256
`c24c74b47d34144e0f3c812c192edae92f199c0f25e26f95cc9b7c25dd5d0852`.
The stated all-length restricted-word lemma and its scoped arbitrary-width
rank consequence are sound. Prepared for Jerry Chen / @CubeJerry with
substantial OpenAI Codex assistance; Apache-2.0. This is independent reasoning
within the assisted session, not proof-kernel or external human acceptance.

The paid-generated subgroup hypothesis is essential and now correct. It makes
`H=Z^m/L` with saturated L, hence the full degree-one kernel is `L/2L`.
Endpoint monomials lie in that subgroup because product entries use paid
subset sums. With all five projector types present, the three original
off-pattern coefficient forms `LJ,M12,M34` have nonempty disjoint supports,
so they are independent and exhaust that kernel when relation rank is at
most three.

After the shear, the endpoint's allowed off-diagonal positions are exactly
the two edges. The proof properly retains them. Quotienting by those positions
and `off(J5)` kills the universal constant and linear terms before exponent
substitution. Thus the degree-two argument uses only the linear substitution;
no unjustified assertion that the full Laurent relation ideal is linear is
needed. The displayed entry comparison proves independence of all four stars
in this quotient.

The elimination argument is valid for arbitrarily many calls. After eliminating
the last bridge variable, `qbar_i` involves only the remaining bridge variables
and type-i coordinate variables. One variable from the nonempty partner group
and one from the other pair eliminate `M12,M34`, while fixing that entire
subring. Its intersection with the ideal is therefore zero. Since each call
has its own universal variable, every internal coordinate call would carry a
nonzero proper bridge-prefix coefficient. None can occur. This also handles
one bridge call, where the internal interval is empty.

The remaining bridge block combines to `I+([Z]-1)J5`. An off-position outside
the two allowed edges forces `[Z]=1`, so the block is identity. The exterior
coordinate factors give fifth target one; undoing the shear forces equality
within each edge pair and preserves that diagonal. Assigning each coordinate
type's paid exponents gives the claimed disjoint subsets and rank inequality.

The arbitrary-width application has the needed scope restrictions. Restricting
to the joint image loses no noncoordinate calls, because each projector fixes
its nonzero image line. The pre-shear basis E,w preserves a diagonal endpoint:
the original coordinate axes in E are eigenvectors and all coordinates in w's
outside support have the same monomial label. Crucially, the final text claims
literal bridge deletion only for the restricted five-dimensional word. Equality
on an invariant image alone would not justify editing all ambient spectator
inputs. The actual full-rank conclusion instead uses the identity quotient,
equal-label adapted basis, target multiplicities, and the separately justified
free-coordinate-generator restoration.

If a projector type is absent, there are at most four rank-one image lines;
the theorem correctly leaves that reduced rank-three problem open. The result
retires the stated irreducible five-type exception, not all rank-three words,
one-edge/zero-edge pools, physical BIT suppliers, or the retained framework
assumptions. No kappa improvement follows from this lemma alone.
