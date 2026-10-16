# Paid replica-tail dilution

This is a sufficient cost result for an explicitly specified profile, with physical realization certified separately. The formal module imports only Mathlib. It does not assume an unproved owner-allocation oracle.

For 0.99 <= p < 1, let

    D(p) = 3*3^p - 5*5^p + 5*32^p - 3*48^p.

`tail_power_positive` proves D(p)>0. Writing t=1-p, elementary exponential estimates and Mathlib bounds on log(2), log(3), and log(5) give the strict lower bound 30*t - 2404*t^2 > 0 for 0<t<=0.01. All inequalities and numerical constants are checked by Lean.

The complete ten-replica periodic paid sum P is

    215100 + 58230*2^p + 27621*3^p + 10800*4^p
      + 3045*5^p + 720*8^p + 3589*48^p.

The exact actual predecessor sum A is

    1591740 + 430902*2^p + 204396*3^p + 79920*4^p
      + 22532*5^p + 5328*8^p + 32^p + 26558*48^p.

`profile_difference` proves A/74-P/10=D/370. `periodic_moment_strict` proves the strict normalized inequality for every positive integer number of ten-replica blocks. `periodic_rank_mass` verifies the complete deficit of3200 per ten replicas.

For a real replica parameter T, define R(T)=T*P/10+D/5. `predecessor_residue` proves R(74)=A. `retained_tail_dilution` proves, universally for T>74 and 0.99<=p<1,

    R(T) / (896*T*73^p) < A / (66304*73^p).

The proof splits the normalized sum into the T-independent periodic term and the strictly decreasing positive charge (D/5)/(896*T*73^p). This prices the finite residue; it never declares it free.

## Composition with the stronger PR2802 supplier

The final checked application uses the complete native words from PR2802, whose seven retired-lender aliases remove seven width-five helper registers. The surviving helper widths and labels are independently checked against its actual providers. Every width-five slot of the constructed allocation occupies a rank32 owner bin together with three width-nine slots. Removing it therefore creates a paid rank-five remainder; it does not create free workspace.

The complete per-call change from the prior supplier is

    18*H1 + H2 - 29*H3 + 8*H4 + 7*H5.

The seven H5 terms include the newly exposed owner remainders. The complete new ten-replica periodic sum is

    216720 + 58320*2^p + 25011*3^p + 11520*4^p
      + 3675*5^p + 720*8^p + 3589*48^p.

The actual PR2802 T74 predecessor profile is

    {1:1603728,2:431568,3:185082,4:85248,5:27194,8:5328,32:1,48:26558}.

`frontier_predecessor_residue` and `frontier_profile_difference` prove that precisely the same D(p)/5 residue remains. `frontier_retained_tail_dilution` proves the universal strict normalized inequality for this stronger supplier for every real T>74 and 0.99<=p<1. This is the formal cost theorem relevant to the final composed candidate.

The literal T94 candidate independently reconstructs

    {1:2037168,2:548208,3:235104,4:108288,5:34544,8:6768,32:1,48:33736}.

There are 846 calls and 345168 whole-helper owner roles, with 84224 live and 84714 charged physical cells. Independent integer-time source, family, coordinate-mask and compact-prefix checks certify the allocation separately from the Lean cost identity. Complete native/global/outer admission remains separately required; see the final status in CLAIM.json and validation/COMPLETE.json when present.

## Application certificate duties

A concrete integer T must have an actual complete ORDER, FILL and provider DISPATCH. Integer-time source availability, indivisible helpers, physical-family distinctness, capacity, disjoint coordinate masks, and compact prefixes must independently reconstruct its complete paid profile. A formula for R(T) is not a construction of that allocation.

Native programs, their dirty-input endpoints, all frame vectors, private-buffer cleanup and phase bindings remain mandatory. Changed parent geometry, the physical invoice, router/tape/precision bounds, ordinary-recursion/bootstrap and every modern outer inequality must also pass. Those finite checks establish the conditional finite-supplier claim under the inherited all-size contracts; this Mathlib module does not prove a new unconditional multiplication algorithm.

The inherited contracts include the all-size compiler, common-label/source-access realization, physical hosting/routing, precision and fixed-tape contracts, exact recovery, ordinary recursion, bit supplier and analytic transfer. The separate all-size BIT routing/leaf obligation remains inherited. See the pinned baseline PROOF.md and FRONTIER.md for the exact comparison lineage.

## Independent formal verification

`replay.py` builds every owned module in a fresh external output directory with the pinned Lean4.34.1/Mathlib revisions. `Check.lean` enumerates declarations by their defining module, including private and generated declarations, and traverses their axiom dependencies. A positive build permits only `propext`, `Classical.choice` and `Quot.sound`. A private-ownership fixture and actual unused-private-axiom, public-axiom and unproved-private-theorem fixtures test that the audit rejects incomplete proofs.
