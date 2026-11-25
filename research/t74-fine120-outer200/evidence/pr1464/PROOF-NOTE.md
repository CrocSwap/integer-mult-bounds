# Exact finite endpoint and outer refinement

PR1458 changes the endpoint enclosure grid while retaining the same physical construction. This package takes one further finite grid refinement. Decimal arithmetic only nominates endpoints; exact rational upper bounds below one and lower bounds above one from both engines prove admission and exclusion. The native and conservative surcharge conventions are unchanged.

For 0<a0<s<1, the inherited recurrence a_(j+1)=(1-s)s+s*a_j has exact solution a_j=s-(s-a0)s^j. Thirty steps remain finite; all positive gaps and integer cutoffs are recomputed. The inherited outer engine checks all 47 strict inequalities, including the next-grid rejection. The separate checker uses the closed form and computes all seven work margins. This does not optimize over all witnesses or claim the limiting exponent is attained.

The source-bound owner/invoice/provider data do not depend on endpoint or witness precision. The full finite replay nevertheless reconstructs the owners, rechecks providers and all admission controls. Native supplier evidence is explicitly reused by matching source words. All inherited conditional mathematical assumptions remain.

Credits and exact parameters are in README.md, SPEC.json and SOURCE-PIN-REFINEMENT.json. Historical receipts are segregated in the evidence ancestry folders.
