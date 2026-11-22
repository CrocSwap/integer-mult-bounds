# Conditional T74 supplier substitution review

The two recomposed outer rates are arithmetically and functionally compatible
with the reviewed phase-fusion proof. **The complete fresh T74 finite/native
admission has passed; the corollaries retain the inherited all-size hypotheses**:

- Strassen transfer: kappa = 0.001677160151714381.
- Additional omega_C<=9/4 transfer: kappa = 0.001677600129305161.

This review did not infer validity merely by rerunning the proposed ledger.
It independently solved the two balance systems and checked the concrete
supplier interface against the proof's actual uses. Its exact controls are
`independent_substitution_check.py` and `INDEPENDENT-SUBSTITUTION-RECEIPT.json`.

## Arithmetic derivation

Write E=epsilon, X=cap, B=1-X-r-z, with r=10^-6,z=10^-8. The common dominant
balance is E*q=1-E+q*B. It is equivalent to

    E(1+q)+qX = 1+q(1-r-z).

For Strassen, use c=3/32 and force the boundary saving c+X-E to equal E*q+s,
where s=10^-5. This is the independent second equation

    X-E(1+q)=s-c.

Solving yields exactly the proposed E and X. For the matrix-conditioned
corollary c=5/16, the sparse-union saving is 2X+r+z-E-1/2. Equating it to
E*q+s gives the second equation

    2X-E(1+q)=1/2+s-r-z.

Again its solution is precisely the proposed balance. The independently
computed minimum margins equal E*q; the stated kappas are the floor at the
10^-18 grid, followed by a strict 10^-11 backoff. The backoff is positive
for both, and all retained cost rows lie above it. In the Strassen case the
conservative full-group-key sort remains included; in the matrix case its
omission relies on the earlier proved one-field union schedule, as before.
The exact inequality 7^16<2^45 justifies the Strassen exponent bound; the
other branch separately requires the supplied omega_C<=9/4 hypothesis.

The short b=.00167971337478 is strictly below the pinned T74 endpoint and
strictly below retained bit c=.001733427039589844234749. With q=b-10^-10 and
a=(q+b)/2, q<a<b<c. The old stopping parameter 10^-9 also satisfies
(1-stop)*b>a. These are the actual strict rate relations used by the
support-local compiler and its stopped recursion, not an assumption that
all bit operations have the complex supplier's exact endpoint.

## Functional interface

The reviewed outer proof consumes a globally complete dyadic tensor call
which applies normalized H0 simultaneously on the selected active bits,
acts as identity on arbitrary dirty helper/coarse/spectator coordinates at
completed-call boundaries, accepts O(p)-bit coefficient encodings, and costs
O(V g^(1-q) polylog p). The supply is used as a completed operator, with its
own scalar phases and working storage included. Outer Gaussian blocks do
not directly inspect the local donor edits, per-rank multiplicities, owner
replica count, or a particular parent-word ordering.

The T74 source retains the same local normalized target, common-label and
mutable-source contract, whole-call hosting, exact wrappers/phases, and
restoration interface. Its new parent uses m=73 as before, with maximum
residual rank48 and fixed finite W=66304. Replacing the old finite stock W
by this fixed W changes constants and the O(log g) product-row reservation,
not any exponent in the support-local argument. The local word has480
helpers, also unchanged in its interface. All donor reads are intended to
preserve the exact full local endpoint; our separate rational rebuild check
confirmed that algebra. The complete unmodified native/frame/phase replay has
now passed and certifies the recorded normalized implementation of those endpoints.
The source pin and hashes of the native, strict, control, and physical-invoice
receipts are bound in `NATIVE-ADMISSION-BINDING.json`.

The larger fixed prefix allowance (2048 bits in the T74 global invoice)
also changes a constant in the linear semantic guard. The capped proof allows
a fixed supplier-dependent constant in O(g), and later O(g*a*B), with an O(p)
record constant chosen accordingly. It does not require the former numeric
prefix constant to remain512 or1024. The strict power guards B+X+r<1 and
E+r<1 remain in force and were checked independently.

The neighborhood exposure still involves O(g log p) actual selected bits;
the T74 finite word neither requests ambient-p address permutations nor
changes the complete-field requirement. The retained bit supplier supplies
the same arbitrary-width equal-chunk interchange interface with more rate
than the chosen a. Source and sink scalings converting H0 to the raw H used
by the tensor compiler remain O(g) guard terms. There is no new finite-field
bridge or a new assumption that per-microbox coarse labels are complete.

Thus the substitution does not require a new analytic lemma, removal of a
charged row, or a new kind of workspace. The updated finite supplier is now
verified by `work/target002_upstream/full-1661-verification/RESULT.json`, whose
status is `PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION`. The binding includes
the complete source manifest and actual fresh native, strict-assembly, physical
invoice, and control receipt hashes. The two rates above are completed conditional
substitutions: their remaining conditions are exactly the inherited all-size,
hosting, precision/tape, exact-recovery, and analytic hypotheses described above;
the matrix branch additionally requires omega_C<=9/4.
