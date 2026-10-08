# PR #3 shared sums with retained exclusion totals and shared stage banks

This composition reuses eumemic's Claude-assisted `ComplexSideCircuit` from
PR #3, commit `dfe5b818aad4d386cb5dd7d76df108088107765d`, verbatim in
`scripts/complex_circuit.py`. It adds the grouped-retention and stage-1/3
sharing interfaces from PR #4. The original fixed-tape and analytic interfaces
remain assumptions; this is not a complete formal multiplication theorem.

At h=24 retain the existing nodes

    E_i = sum_{T not containing i} x_T, for i<h-1;
    C_* = sum_T x_T.

Introduce the omitted exclusion E_last only for this derivation. On source
contributions, the sum of all h exclusions equals (h-3)C_*. The central scatter is

    S excluding the last point: C_* - (1/2)sum_{i in S} E_i;
    S including the last point: ((5-h)/2)C_* + (1/2)sum_{i<h-1,i not in S} E_i.

Each source coefficient is (|S intersect T|-1)/2. The unchanged side map
cancels its off-diagonal intersection-zero/two coefficients. The usual
L,-R,-J,L^-1,V,L,R,J,L^-1,-V wrapper therefore gives the shear and restores
arbitrary initial scratch; no relation is assumed among its dirty totals.

Each E_i node has coordinate label F_without_i, with an orthonormal coordinate
basis and unit-line complement e_i. The global node has the full frame and zero
retirement residual. All 120 newly activated base nodes are coordinate or
pair-star nodes with the same nested, nonalternating residual rules as PR #3.
The grouped forward scatter uses the common low frame, dropping h-1 dimensions
per E_i and h for C_*. The reverse uses the common full frame followed by
complemented mixing. Both lose ell=(h-1)^2+h=553.

The coefficient -(h-5)/2 must be implemented as h-5 updates of -1/2. The
first grouped pass does all E_i updates and one global update; the remaining
h-6 passes touch only the global total and targets containing the last point.
All these passes commute and share the same frame, so the additional physical
incidences have zero frame difference and add no child calls. Their two
occurrences add 2(h-6) scalar gates per invocation, included in the guard.
Every actual coefficient remains of magnitude at most one, denominator at
most two. The inverse may reverse and negate the passes, or reorder them
because their target updates commute.

Tensor each local residual by the original norm-one prefix/future lines.
Data boundaries and weight-27 source/sink corrections are unchanged. Every
auxiliary still enters at the low frame and exits at the full frame. Thus
partner-flip matching at even h=24 gives the same stage-1/3 join E<=H, with
unit witness and dimension m-2h; one role and m calls are saved per join.
No independent address coordinate or additional zero-scratch premise is used.
The compact complete-field/child-volume and payload/precision transfer is the
existing written one, instantiated with the new finite constants.

The base side compiler has 66518 additions and 24288 output uses. Retention
activates 120 additional ancestors and h=24 total outputs:

    C=66638, q=24312, R=90950;
    W=761750114048, L=6796219584, D=2990500480;
    s=10530430586099072, eta=365/1285272576.

The actual gate bound is

    3v^2(8v+4C+4+2(h-6))=3475338442752 < 12W.

The standard 36W^3+4s+4W+4 depth enclosure and s<m^5 hold. The exact log
bound log(m)<477/50 gives

    eta-(2970/10^11)(477/50)=406952569/627574500000000000 >0.

Thus a_c=2970/10^11=2.97e-8, about 2.12 times PR #3's certified 1.4e-8.
The bit network remains a_b=296/10^11. Therefore the existing witness
kappa=591/10^12 >2^-31 and its strict margin/gap remain unchanged; this is
additional producer headroom, not a larger headline exponent. Full h24 source
coefficients, retained integer multiplicities, all activated labels and both
compiled orientations are checked. Small exact controls include arbitrary
scratch, inverse/exchange, every normalized scatter pass and all phase edges.
