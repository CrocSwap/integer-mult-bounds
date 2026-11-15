# Fixed-trace BIT owned-cache promotion obstruction

This is a negative result for one explicit source and one explicitly enlarged
repair family. It is not an impossibility theorem for BIT algorithms and does
not improve kappa.

Source and modified input contract
----------------------------------
The compressed BIT word has SHA256
51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78.
It has 659 public inputs and 237 owned fields. The nine owned fields770--778
each have one INIT, one rank-seven MOVE from charts510--518 respectively to
chart0, and one CLEAR at chart0. For the proposed promotion, replace these
nine zero initializations by independent formal inputs h0,...,h8 and retain
their contents instead of clearing them. All original scalar and chart
operations are unchanged. This hypothetical late introduction of independent
inputs grants their availability for free; it is not an admission of a new
public-field interface or of productive-target credit.

At each checkpoint use the source's normalized frame coordinates over F2.
Chart0 is the identity frame. A MOVE changes the frame but not the normalized
linear row. Thus a zero normalized row at chart0 is a zero physical field under
the retained native-frame contract. The proof is about these exact source
semantics, not an independent all-width implementation of those operators.

Let x contain all659 old independent inputs and h the nine new independent
inputs. Let M have one row for every observed historical chart0 field. There
are524 initial observations and39,324 post-instruction observations, for39,848
offered vectors. After every operation it suffices to inspect its referenced
fields: all other fields and their charts are unchanged. Consequently this
enumeration includes every historical chart0 row, despite avoiding duplicate
observations after unrelated operations. It grants free temporal storage and
access even to future rows; no chronology or capacity restriction is used.

Independently verified kernel certificate
-----------------------------------------
The independently authored audit propagates all observation functionals
backwards as columns, rather than replaying all input rows forwards. It finds
rank(M_old)=rank(M)=533 by column elimination, using least nonzero pivots.
It then constructs the following exact right-kernel witnesses z_j=(u_j,e_j).
Listed old-input indices are the support of u_j; all arithmetic is over F2.

  owner770 / h0: 0,1,8,9,30,59
  owner771 / h1: 0,2,4,9,59
  owner772 / h2: 4,8
  owner773 / h3: 0,8,14,59
  owner774 / h4: 8,14,30,59
  owner775 / h5: 0,1,2,14,59
  owner776 / h6: 4,8,9,14,59
  owner777 / h7: 1,4,9,30
  owner778 / h8: 2,4,9,30

Every equality M z_j=0 is checked by directly XORing the named old columns
and the h_j column, without trusting the elimination rank. A second concrete
forward execution evaluates all nine witness assignments in parallel using
nine-bit register values. It verifies that every chart0 field is zero at
every relevant checkpoint, and that each retained promoted output is zero.
This forward execution does not use the reverse propagation or elimination.

If V is the row span of M and H the pure new-input coordinate subspace, then
V intersection H={0}. Indeed, for any (0,y) in V, orthogonality to z_j gives
y_j=0 for every j. This excludes every nonzero joint linear combination of
the h inputs, not merely each chosen basis vector separately. A control that
adds only the stock row h0+h1 raises the intersection dimension to one while
leaving every individual h_j absent; it demonstrates why checking singleton
recoverability alone would not establish the joint claim. Altering one old
coordinate of a displayed witness also fails the direct XOR check.

Extension to interleaved chart0 linear repair
--------------------------------------------
The explicit witnesses prove more than absence from one terminal span. Fix
the original chart trace and all original operators. Permit extra linear
gates at any time, provided every operand and result is at chart0. Permit
additional chart0 scratch initialized identically in the two executions.
These inserted gates may feed values into subsequent original operations.
They must not add observations or operations at another frame, alter the
chart trace, or introduce additional address-changing maps.

Compare two executions whose old/new inputs differ by z_j. Inductively, their
state difference equals the original modified word's state difference z_j
propagated to that checkpoint. At each inserted gate, every participating
chart0 field has zero difference by the verified source invariant. The gate
therefore leaves the full difference unchanged; extra scratch also remains
equal. Each next original linear operation propagates the same difference
as before. This establishes the induction through an arbitrary finite
interleaving of permitted gates. In particular, every final chart0 field
has zero difference between the two runs, although h_j differs by one.

No such repair can return h_j as an independent chart0 output. Since the
nine witnesses have the identity matrix in their h coordinates, no nonzero
new-input combination, and hence no invertible joint helper basis, can be
returned at chart0 in this family. The same argument applies to any subset
of the nine promoted fields: other promoted h coordinates can be set to
zero, and their original chart0 clears erase zero difference.

Other checked behavior and pricing limitation
----------------------------------------------
The new h coefficients contaminate55 or63 old public outputs per owner,
matching the independent reverse calculation. None of the other228 owned
CLEARs erases an h coefficient. The nine retained promoted fields have the
identity h block, but also old-input contamination. Erasure elsewhere is
therefore not the cause of this obstruction; chart0 cannot distinguish h
from the displayed old-input shifts.

Giving all nine descenders a new H7 target without any added cost would
credit36*9*7^(1-0.004654)=2247.5531150493211126556... in the complete BIT
moment. This approximate price is explanatory only; the standalone audit records the exact symbolic expression and does not certify the complete caller invoice. This number is only
the price of a hypothetical successful independent-output contract. The
certificate shows that the stated repair family does not supply it.

Changed nonzero-frame gates, different address trajectories, another repair
coframe, new paid maps, a changed original input/output interface, and other
BIT constructions remain outside the proof. Those changes require separate
operators, paid invoices and complete caller/precision/compiler arguments.
