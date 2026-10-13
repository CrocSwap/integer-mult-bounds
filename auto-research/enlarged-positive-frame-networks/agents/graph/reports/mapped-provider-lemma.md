# Alternative producers with rewritten provider operands

This extends the conservative [alternative-producer construction](alternative-producer-lemma.md).
The new dependency rule is implemented in `alternative_producer_clones.py`
and exercised by the mapped-provider cohort. It permits a source operand
of one selected replacement to be the scalar form of another selected
replacement. Neither their dirty carriers nor their intermediate values
are identified.

For a selected replacement of x, move one complete original result-carrier
chain, starting at consumer f, to a new gate x' = y + z. The exact disjoint
integer coefficient supports of y and z partition the support of x. Two
distinct unused controller capacities g1 and g2 precede f in the actual
chronology, consume the selected forms, and have spaces contained in F_f.
Each capacity belongs to at most one selected replacement.

When a provider's operand use belongs to another moved chain, resolve that
operand to the new producer of that chain. The second producer is inserted
before its first moved use, which occurs no later than this provider. It
therefore already exists before the provider, and hence before f. Its
inherited first-consumer space is contained in the provider's space by the
literal original chain nesting. This proves chronology and nesting of the
rewritten operand without requiring an unchanged formal producer ID.
Repeating this argument along strictly earlier providers gives an acyclic
construction. The original scalar form of every rewritten operand is
preserved exactly.

Retain g1 and g2 at the two *actual rewritten* input uses of x'. All other
original selected links are transported with their complete chains. The
unused-capacity condition and disjoint selection preserve carrier
capacity, while F_g1 and F_g2 contained in F_f give the required frame
nesting. One new scalar addition and two additional retained links save
one paid role. The native rematcher may find additional savings; those
need the final selected-map audit rather than this local count.

The independent compiler reconstructs exact integer scalar supports,
literal rational bases, physical carriers, all containment incidences and
the forward/reverse rank timeline. Small controls execute the complete
JLV dirty word over F2 for every packed source, target and scratch basis
vector. This is not an assertion that two equal scalar supports contain
equal arbitrary dirty values. Address-space projector identities and
finite-field/machine transfer are separate dependencies.

The search score uses the ordinary child-width excess moment, including
the exterior cost of a paid role. With m=575, alpha=0.0000413 and phi(r)
the actual ordinary rank-r child profile, the local saving estimate is

```
phi_exterior(h) + phi(r_x) + phi(h-r_g1) + phi(h-r_g2)
  + phi(r_f-r_x) - phi(r_f-r_g1) - phi(r_f-r_g2) - phi(h-r_f).
```

The scarce policy discounts capacities used by many offered replacements.
This floating discovery score is not a fixed-matrix certificate. The new
negative-basis winners differ from the smallest ordinary-role winners;
their geometry profiles and final moment assembly are certified separately.

The best selected negative-basis parent DAGs are now recoverable from public
PR36 and portable fixtures. Fresh source-only rebuilds passed all recorded
DAG, frame and ordinary selected-link hashes at h23 R36,219 and h25 R47,461:
[h23 receipt](../results/best-positive-negative-recovery-23.json),
[h25 receipt](../results/best-positive-negative-recovery-25.json).
The subsequently weighted negative-basis maps on these same parents have
a separate [literal compiler receipt](../results/best-weighted-positive-negative-compiler-1539.json).
No global optimum or worldwide priority is claimed.
