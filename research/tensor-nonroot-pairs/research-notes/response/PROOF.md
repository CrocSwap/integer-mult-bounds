# Response-kernel packet deletion

## Realized improvement

On the source-bound tn11 bit provider, delete the two A events (frame842, helper444, source3) and (frame842, helper246, source3), at original indices1426 and2331. Their transported target-response columns coincide, though neither column is zero. Rebuild the cleanup as the inverse of the modified helper network. The exact paid child delta is -rank1 -rank5 +rank6. All955 formal columns, rational frame dimensions and integer operand-span checks pass. Either one deletion alone fails the endpoint identity.

The complete selection additionally removes ten ordinary duplicate source-injection pairs at the full frame. They give no additional moment gain and are not advertised as a second new technique. In total A and its cleanup lose44 scalar additions. All22 single-deletion negative controls fail.

## General sufficient theorem

Work over any F2 vector space, with arbitrary initial helper and target contents. Sources x are immutable. Each candidate injection is h_d <- h_d + x_s. All other gates are linear. For injection i, let r_i be the column of the map from its destination, immediately after that gate, to the final target outputs. Select a packet S satisfying, for each source s,

    XOR_{i in S, source(i)=s} r_i = 0.

Deleting the packet preserves every target output. To prove it, regard each selected injection as an independently switched additive forcing term. Since sources are immutable, no switch changes any later injected source value. Every target output is therefore affine-linear in the switches, with switch coefficient r_i x_s. The packet changes the output by the displayed zero sum. This is exact simultaneous cancellation; it does not assume a deleted gate is individually invisible or that the gates commute with all intervening gates.

If A writes only helpers and the centre/delivery segment writes only targets, replace cleanup C by the literal inverse of the modified A. Every source and helper is then restored. The original dirty-target compensation D remains valid because the entire target transfer is unchanged. The constructor separately checks A followed by the original C is identity, so it does not assume syntactically reversed original gates.

In low-rank notation the update to target transfer is U*V, with columns of U equal to the transported responses and rows of V selecting immutable sources. The sufficient criterion is U*V=0. This is the annihilator/low-rank viewpoint used in the search. It is substantially stronger than testing whether a single U column is zero.

## Physical admission and strict moment gain

The construction does not move helper ownership or alter entrance/final frames, retained centres, scatter, or target delivery instructions. Every surviving event retains its old frame. Exact checks establish frame-chain inclusion and operand support at every event; the inherited all-size framed compiler is retained as an explicit interface. No new whole-owner splitting or free physical transport is assumed.

For p=1-a in (0,1), strict concavity/subadditivity gives 6^p < 5^p+1. Therefore replacing rank1 and rank5 children by one rank6 strictly decreases the supplier moment by m^(-p)*(6^p-5^p-1). The total child rank stays unchanged. Thus this is a genuine strict supplier improvement throughout the relevant exponent interval, without relying on floating-point entropy estimates. Reusing unchanged residual widths leaves the whole-owner invoice untouched. The parent still must run its complete provider/global assembly and record the resulting kappa; the local check is not an unconditional multiplication theorem.

## Actual library use and novelty scope

The ReasBook Sherman-Morrison-Woodbury proof explicitly reduces a large inverse update A+UV* to a small matrix 1+V*A^-1U. Mathlib's SchurComplement block LDU proofs provide the corresponding exact low-rank/block representation. These suggested representing changes through their transported response columns rather than optimizing gates one at a time. Their inverse identities are not needed as unproved premises of the elementary packet theorem above.

OpenAI's SparseSpectral proof retains the concrete annihilator equation A(1+R)=0 together with a sparse cost; this is a useful parallel to retaining both the exact annihilator and paid profile here. That theorem concerns real/complex symmetric reflections, so it is not imported as an F2 circuit theorem. OpenAI's ConnesRigidity transvection-commutator proof was read as a distinct noncommuting rewrite route, coordinated with the scheduling lane; it is not claimed as an additional implemented mechanism here.

This packet deletion is new in this team's admitted construction. No universal literature-priority claim is made. Ten full-frame duplicate cancellations are routine and explicitly separated from the cross-helper cancellation that improves the moment.

## Reproducibility

Run algebra_constructor.py SOURCE selection.json NEW_OUTPUT with schur_constructor.py in the same code directory. It performs exact rational ranks, all-column/operand checks, backward response propagation, packet-annihilator checks and22 negative controls. Source and candidate hashes are frozen in selection.json. Candidate SHA256 is16bdea122b70946c223b2b7bcd6225ecf233334a57148c8287982b322eb154fd.

Discovery used native C++ to exhaust all per-source subsets:120 source groups,1068 gates, at most13 gates per group. Exactly11 nonempty zero-response packets exist in this restricted representation; they are all pairs. Only the cross-helper pair improves the moment, even when all11 packets are combined. This is a bounded search result, not a barrier to other representations.
