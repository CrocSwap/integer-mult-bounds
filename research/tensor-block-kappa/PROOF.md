# Owner-block norm accounting and the proposed T114 application

**T114 complete release PASSED.** This proof explains the sufficient
mathematical accounting and the concrete evidence it must use. The source-bound
finite release and kernel/axiom receipts determine the final verification scope.

## Complete boundaries, including arbitrary dirty inputs

The actual R408 programs are retained from PR2802. Independently replaying every
one of their 632 input columns, in both providers and orientations, gives
`Y += X` forward and `X -= Y` backward in the canonical logical coordinates.
Every other live row is its own input; no helper-to-data term remains. Physical
data entry/exit maps are unitary. Each normalized helper endpoint is a Fourier
factor on its assigned coordinates tensored with identity on its spectators,
conjugated by the checked monomial/owner charts. It acts within one actual
physical family. All eight private centres, 72 zero buffers and coefficient
work fields clear before a complete invocation returns.

These statements concern the entire centre/B/cleanup program. The intermediate
reader can depend on arbitrary dirty helpers, as PR2742 correctly emphasizes;
that intermediate dependence must not be mistaken for the complete endpoint.
The exact wrappers and global phases are required, including cold and
hyperplane-ended helpers. A scalar row equality alone does not prove a native
normalization statement.

The owner certificate checks that all 632 live roles in a complete call use
distinct physical families. Its 224 active fields belong to the caller replica.
A helper owned by another replica therefore changes only that owner's family
by a unitary. Each bridge has coefficient +1 or -1 and remains inside one
replica. Idle children, data phases, spectators and terminal translations are
unitary. Shared private fields carry no state between complete calls.

## Universal sufficient energy bound

Let `E_t(r)` be the nonnegative squared Hilbert norm of owner-replica block r at
a completed boundary. Let `c_t(r)` be one for an active data shear/bridge on r and
zero for a block-isometric action. A unit-coefficient shear has norm at most two:
by the triangle inequality and `2ab <= a^2+b^2`, its squared norm is at most
four times the original squared norm. Consequently

    E_(t+1)(r) <= 4^(c_t(r)) E_t(r).

Induction gives

    E_t(r) <= 4^(sum_(s<t) c_s(r)) E_0(r).

If each block has at most d active steps, summing yields

    sum_r E_t(r) <= 4^d sum_r E_0(r).

No statistical independence, product-state assumption or absence of correlations
is used. A unitary inside an owner family preserves the block norm even when
its entries are correlated with other inputs. The Lean results
`block_energy_prefix`, `total_energy_bound`, `eighteen_step_energy_bound` and
`shear_energy_bound` prove the indicated sufficient inequalities. The concrete
endpoint and ownership hypotheses remain separately checked obligations.

Every replica has exactly nine complete local calls and nine bridges, so d=18
and norm amplification is at most `2^18`, independently of the number of
replicas. Work is still charged for every call and bridge. This argument reduces
the amplification exponent; it does not remove serialized work or recursive
children.

## Full regular-representation precision invoice

Use the Hilbert norm over **every group-indexed physical cell**, rather than
assuming that the old 37-bit term bounds the full regular representation. For
this finite geometry let

    |G| = 2^(36^2) * product_(i=1..36) (2^(2i)-1),
    N = |G| * (896*T + 408 + 8 + 72 + 2),
    b = ceil(bit_length(N)/2).

For arbitrary initial values, including correlated values,
`||input||_2 <= sqrt(N)*||input||_infinity < 2^b*||input||_infinity`.
The completed normalized helper factors are unitary on this regular
representation: each factor is a normalized tensor child with exact monomial
wrappers and a bijective within-family label chart. This uses the retained
completed primitive/hosting contracts; it does not infer unitarity from a
scalar row identity alone.

At T114, physical stock is 102634, `bit_length(|G|)=2628` and
`bit_length(N)=2645`, hence b=1323. The exact retained scalar/Horner envelopes
are 63 bits forward and 70 backward, for both providers. Charge the retained
37-bit conversion separately as a conservative overcharge, the 18 active-step
bits, the full 1323-bit stock conversion, one partial-cover bit and four
arithmetic-margin bits:

    70 + 37 + 18 + 1323 + 1 + 4 = 1453 < 2048.

Using the conservative 128-bit local guard instead of the measured 70 gives

    128 + 37 + 18 + 1323 + 1 + 4 = 1511 < 2048.

Thus the charged payload reserve is **2048**, not the earlier proposed 256.
The full-stock bound avoids relying on a specialized mixed norm or omitting a
square-root-of-stock factor. The extra partial-cover bit retains the normalized
cover's partial-sum bound before the current sweep is finished; the exact local
scalar/Horner envelope then applies to the current primitive. Other local
boundaries have already been counted in the replica's eighteen active steps.

All invocation, bridge, routing, coefficient, private-buffer, physical-row and
ordinary compiler costs remain charged. The ordinary row calculation is

    2*2645 + 9909 + 252 + 2*2048 = 19547 < 20161.

Actual T114 topology, regular-representation endpoints, local-prefix guards,
finite invoices and outer admission must all be rechecked before release. The
source-bound independent complete-boundary review and universal energy lemma
support this application; neither alone is a complete new release.

## Paid profile and proposed gain

Retain the already checked periodic paid sum

    P(p) = 216720 + 58320*2^p + 25011*3^p + 11520*4^p
             + 3675*5^p + 720*8^p + 3589*48^p,
    D(p) = 3*3^p - 5*5^p + 5*32^p - 3*48^p,
    R(T,p) = T*P(p)/10 + D(p)/5.

The inherited Mathlib proof gives `D(p)>0` for `0.99 <= p < 1`; hence the complete
normalized moment `R(T,p)/(896*T*73^p)` strictly decreases as positive T grows.
The positive finite residue remains paid. This inequality does not construct
owners for arbitrary T. The application needs the actual T114 literal fill,
which has 418608 complete helper roles and proposed profile
`{1:2470608,2:664848,3:285126,4:131328,5:41894,8:8208,32:1,48:40914}`.
Its rank mass is 7420032 and deficit 36480.

The proposed adjacent root bracket is
`[0.001717795274221416686578, 0.001717795274221416686579]`.
The proposed target is its lower endpoint minus `10^-46` minus `10^-70`.
Compared with the full admitted T104 target, the proposed exact gain is
`51604828943380/10^24`. Directed rational moment checks and the complete ordinary
and modern outer release must independently admit this target. No gain is
claimed from a component saving or a rounded PR title.

The Mathlib proof covers these explicit inequalities, not the full inherited
all-size multiplication pipeline. Final transitive-axiom checks and adversarial
fixtures are separate from source-only indexing and historical artifacts.
