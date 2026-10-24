# Review of the monomial-square gap theorem

The corrected theorem is accepted as a conditional local protocol.
It requires an admitted raw interface, legal access to the stated
monomial square and its inverse, and the productive-frame intertwiners
now stated in the note. It does not construct such a raw interface for
an arbitrary Q.

The review found a missing hypothesis in the first version. A physical
output ADD `u += R X` gives logical coefficient
`F_mode^-1 R F_data`. An arbitrary legal monomial R does not make this
equal to R. For example, with Q equal to I, F equal to a one-qubit
Hadamard, and R equal to Z, this coefficient is X rather than Z.
Thus availability of monomial access alone did not prove the displayed
map. The final note requires

    F_mode R=R F_data,       F_data K=K F_mode.

These conditions repair the proof. They hold for the actual scalar
field matrices R and K. They do not change the emitted original-complex
payload. The note also states the alternative use of conjugated output
coefficients as a separate access hypothesis.

For `S=Q^2`, direct block multiplication gives

    A=[[0,I],[S^-1,0]],
    A Q=Q A,
    Q A=[[0,Q],[Q^-1,0]]=T,
    T^2=I,
    S A=A^-1,
    Q^-1 S A=S A Q^-1=T.

No fourth-power identity is needed. F commutes with Q, hence with S
and A. The forward preload is `u=z-RTx`. The raw mode output followed
by the productive-frame-compatible R addition gives
`v=-z-R(I-T)x`. The raw target is `y+x+Kv`. Its last physical addition
has logical coefficient

    (F_data Q^-1)^-1 A K F_mode = T K.

The final forward map is therefore the stated `y+x+(I+T)Kv`.
This does not move A through K.

In the backward word the first physical source correction subtracts
`8 Q^-1 S A Kz=8 T Kz` from logical x. It reads the old mode z before
the mode preload. Substitution of `u=z-Ry/8` into the raw core gives
`x'=x-y-8(I+T)Kz` and `u'=-z-Ry/8`. The output graph contributes

    F_mode^-1 R S A F_data Q^-1 y/8 = R T y/8.

This proves the stated backward map. The order and both frame
intertwiners are required.

For stage maps that share this one global T, the product of a query
and an injection contains the adjacent factors `(I-T)(I+T)=0`.
Arbitrary stage-dependent R_s, K_t, and invertible mode gauges do not
alter this cancellation. A data bridge may be inserted when it commutes
with T. Unrelated stage operators T_s do not give this conclusion.

For the actual unit-modulus specialization, `norm_inf(R)=56` and
`norm_inf(K)=1`. The literal forward preload has row norm at most 57.
Its ordered suffix has row norm at most 58: the mode can first gain
56 times the source, then the target can gain that updated mode.
The backward preload has row norm at most 9 and its suffix at most 8.
These are bounds for the extra wrappers only. They do not bound the
raw native core, recursive children, the whole controller, or a complete
supplier's precision.

This was a proof review. No new native kernels or controller were run.
The accompanying physical-boundary receipt pins the corrected note.
OpenAI Codex performed this review under the user's direction.
