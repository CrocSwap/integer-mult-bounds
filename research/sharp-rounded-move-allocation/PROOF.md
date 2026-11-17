# Smaller lifted records for the complete rounded MOVE

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written proof with exact finite corroboration.

## Statement and precise delta

Use the complete source/provider domain of CubeJerry's PR #6996,
`research/current-rounded-source-move/PROOF.md`, at canonical base
`e54523517d0f03e58352e647c403a5af3e525a57`. In particular, retain positive
parent f<=cutoff, ranks r in {1,...,8}, all nine native blocks, complete rows,
arbitrary signed h-bit real components with h>=2, and all format, source,
disjointness, ownership and valid-return provider premises. Write

    g = r f,    k = ceil(g/2),    w = h + 2k + 1.

The source domain is that package's retained #6030 raw catalogue. Its
placement in the currently selected #7000 caller is a separate obligation.

The following replacement allocation satisfies that provider's exact-prefix
and signed-margin obligations. Physically prepend k low zeros to each original
component and append k+1 sign copies. Run the same complete exact entrance,
positive child and exit at component width w. Drop k low bits only after the
exit, using the same nearest-up rule and complete final signed-range check.
The mathematical return remains

    Delta * floor(Ux/Delta + 1/2)

componentwise, with the original absolute phase. True final h-bit overflow
is the only numerical rejection on the inherited valid provider domain.
This is a sufficient allocation substitution theorem. The physical Count/Tape
substitution has not been implemented or executed here.

PR #6996 instead lifts g bits and uses

    w_old = h + g + ceil((g+1)/2) + 1.

Thus the new width saves s+1 bits when g=2s, and s bits when g=2s+1.
The gain is strict for every g>=2. At g=1 the allocations agree.
Neither this note nor its verifier changes a predecessor file.

## Cited Gaussian facts

The tensor-grid and row-norm statements are prior work. Alejandro Zarzuelo
Urdiales's Gaussian parity/tensor work, Nick Petalas's prefix applications
PR #2772/#3089, and Jose Manuel's physical Gaussian leaf PR #3091 give the
following facts, stated together in section 4 of
`research/physical-gaussian-leaf/PROOF.md`.

For

    C = 1/2 [[1+i, 1-i], [1-i, 1+i]],

every entry of a j-axis tensor is a Gaussian unit times (1+i)^(-j).
Its real and imaginary parts have common binary denominator 2^ceil(j/2),
and each real-component row has l1 norm 2^ceil(j/2). These hold for every
completed Gaussian prefix, and the fused arithmetic checks the stored
component rather than storing a larger four-term numerator at that width.
The physical leaf theorem supplies that fused implementation contract.

These facts and their sharpness are cited premises, not new claims or
predecessor audit results. The new step is their use at the complete raw
MOVE's lifted-record, serial-monomial and once-rounded return boundaries.

## Every exact prefix is integral and fits

Let M=2^(h-1). Original input component magnitudes are at most M, including
the most negative original word. After the k-bit lift their magnitudes are
at most 2^k M. The entrance monomial, including every serialized phase and
permutation step, preserves this bound. It also preserves divisibility by
2^k, because its phases are Gaussian units.

After j of the g Gaussian axes, the cited denominator bound gives integer
components: j<=g implies ceil(j/2)<=k. In particular each next fused half
has an even integer numerator. This argument uses the complete prefix's
exact value. It does not incorrectly require one reserved zero to survive
each successive division by two.

The cited row norm bounds every stored real or imaginary component by

    2^ceil(j/2) * 2^k M <= 2^(2k) M = 2^(w-2).

The same bound covers the entrance, since k>=1. Each serialized exit phase
or permutation also preserves it. Hence no prefix reaches the widened
most-negative word, and every positive component lies strictly below
2^(w-1). In particular both monomials satisfy the strict signed phase
margin. This closes the arbitrary-input numerical obligations without
assuming that an entrance preserves a smaller g-axis fibre norm.

The original source factorization U=L(C on g selected axes)R is retained.
The exact widened return is therefore 2^k U(m) on grid Delta/2^k. A final
drop of k bits gives floor(U(m)+1/2), including negative ties. The complete
signed extension check accepts exactly when that rounded component fits
h bits. Keeping the full final output staged before commit retains the
predecessor's atomic true-overflow behavior under its provider premises.

## Descriptor and lifecycle substitution

The logical Gaussian dimension is still g=r f. It is not replaced by k.
The original parent f, cutoff, all address positions, selected axes and
source triples remain as specified by #6996. Only physical component,
record and row widths change. For B=outer*rows, a=within_bits and c complex
coefficients per record, use

    record_bits_new = 6c(w+1),
    row_bits_new = 2^a record_bits_new,
    V_new = B 2^a 6c(w+1).

The serial-column descriptor still has f'=1, K'=fK and rho'=rho+jK.
The positive view still has f'=r f and cutoff'=r cutoff. Section 3 of the
cited complete-MOVE proof permits physically correct component widths at
both actual monomial consumers. Its record equations recover c with the
new width as before. No logical coordinate, suffix, row or coefficient is
removed. Its exact-prefix proof uses the numerical facts just established.

In the inherited `Provider.prepare` interface the first returned Count is
the number of bits used by lift and drop. Compute the true g from r and f,
then return k in that position, margin k+1, width h+2k+1, and the rebuilt
record/row lengths. The child reads its unchanged logical geometry from the
header. Conflating its logical g with the codec's k would be an incorrect
implementation. The reference allocator distinguishes these fields.

All fixed roles, borrowed contexts, inner and outer protected stages,
constructor/source work, both serial repetitions, cleanup and historical
backing from #6996 remain required. The same lift/drop loops accept k and
k+1 as their respective counts, and both are positive. Preparing these
Counts and rebuilding the complete lengths is paid work. This theorem
proves admissibility of the allocation, not a physical implementation or
measured runtime improvement.

## Exact size improvement and the retained bill

For the same logical field, c, B and a,

    V_new / V_old = (h+2ceil(g/2)+2)
                   / (h+g+ceil((g+1)/2)+2).

The exact difference is B 2^a 6c(w_old-w). At h=2, r=8, f=1, c=B=1 and
a=12, w falls from 16 to 11 and the widened coded field falls from
417792 to 294912 bits, a saving of 122880 bits. The geometry parameters
H=G=K=1, rho=e=0, u=2, z=11 and a=12 satisfy #6996's full nine-block
inequalities with f=1. This is a record-size calculation, not a numerical
whole-MOVE trace or an observed allocation in a selected caller.

The complete invoice of #6996 section 7 must be evaluated at V_new and w.
It retains every provider and metadata term, both serial monomial sums,
the positive numeric service, the inner 22 V_new+35 administrative term,
the original-width commit and all outer codec work. The stripped numerical
length R1, address/control lengths and all historical maxima also change
with w and must be recomputed. A smaller V does not by itself prove that
every control cost or total runtime decreases. No paid/productive rank
profile, selected saving or kappa changes here.

## Verification scope and remaining obligations

`model.py` implements the new arithmetic allocation, complete abstract
monomial/C-tensor/monomial endpoints and signed bit-string lift/drop.
`verify.py` compares it with literal dense tensor entries, formed from
integer powers of 1+i and 1-i rather than butterfly execution. Every small
signed input is enumerated at h=2 and g=1,2 for two explicit monomial pairs.
Additional boundary fixtures cover g=1..8 and h=2,3,9,65,257. They test the
new allocation rather than invoking or replaying a predecessor verifier.
Neither pair of finite monomials is represented as an actual selected
source recipe. The all-source/unbounded statement is the argument above,
conditional on the cited provider and Gaussian facts.

The containing error fibre still includes all 9f native axes. The original
actual-input radius condition and eta_X error allowance from #6996 are
retained, since the returned rounded mathematical map is identical. No new
radius improvement, caller placement, nonleaf rate, native/compiler or
stock admission, analytic recovery or complete multiplication theorem is
proved. All five selected framework assumptions remain. Physical whole-MOVE
execution, selected cold replay, Lean and Docker were not run. Independent
human and formal proof-kernel review are unclaimed.

## Open next questions

1. Implement this Count/Tape preparation substitution and execute a complete
   mandatory-geometry rounded MOVE. Start with one admitted source triple,
   retain both protected stages and every fixed role, and use an adequate
   numerical budget. The reference engine supplies no physical evidence.
2. Bind an actual enclosing caller to the smaller expanded record and
   recompute the long-record, control and historical-backing inequalities.
   The source/caller mapping and full bill remain prerequisites.
