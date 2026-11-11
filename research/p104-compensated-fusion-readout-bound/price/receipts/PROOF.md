# Fuse the paid return of public helper 319

All clocks are zero-based in the exact #7314 word. Let \(M\) be the normalized
linear operator on the 14 public fields of the 18-event chart-207 block. On
those fields, write \(e_i\) for the coordinate vector and let
\(v=e_{319}-e_{1081}\) and \(u=e_{319}^{\mathsf T}+e_{1467}^{\mathsf T}\).
The constructor checks both identities over the rationals against the
literal ordered ADDs and SCALEs.

\[
 Mv=-e_{1081}+e_{1467},\qquad uM=e_{319}^{\mathsf T}.
\]

At chart 1089, add field 319 to field 1081. Keep \(z=x_{319}\) in physical
field 319 and send the original block \(x-vz\) by using an owned zero field
in chart 207 in place of 319. The prefix operation and this substitution
give exactly that vector on all 14 fields, with no assumption on the dirty
public values. All ordinary fields except 319 follow their original chart
paths. The owned field is created and cleared within chart 207 and is never
transported.

The discrepancy between the virtual block output and the original output is
\(Mvz\). It is supported only on fields 1081 and 1467, and both already have
paid lifts to chart 127. Take field 319 directly from chart 1089 to chart 127.
Subtract \(z\) from field 1081 and add \(z\) to field 1467 there. Then overwrite
319 by subtracting the corrected field 1467 from \(z\). The second identity
states that this is exactly the original field-319 output. Every other block
output, including all fields whose next scalar contact occurs in chart 207,
has its original value.

The block's original clocks interleave work on other fields. The constructor
checks every intervening scalar contact on each of the 14 participants. It
places the replacement at source clock 44616, within the joint allowed range
[44616, 45718], and emits all affected transports using literal nested
subspaces. The two low-chart inputs and the two high-chart correction peers
are coframed before the replacement reads them. Only declared owned field
1567 is used for the additional lifetime. The actual COPY is earlier in
the word. The complete forward and adjoint checks verify the full arbitrary
input contract and the literal COPY guard.

The rank-three chart 1089 is contained in the rank-eight chart 207, which
is contained in rank-nine chart 127. Thus the paid rank-five and rank-one
transports of field 319 become one paid rank-six transport. The per-native
target histogram is identical and the paid delta is \(P_1-1,P_5-1,P_6+1\).
At \(H_r=r^{1-C}\) the gain per native call is \(H_1+H_5-H_6>0\) for
\(0<C<1\). The complete signed #7113 application uses 17 calls. Its paid
positions fall from 110,536 to 110,519, with 22,461 productive positions,
rank surplus 1,424 and zero empty-root credit. Both directed price engines
certify the full price, and the complete application checks the fixed tape
and outer gates at the proposed bound.

The application retains the framework assumptions native_all_columns,
owned_erasure, compiler, precision_tape, and analytic_recovery.
