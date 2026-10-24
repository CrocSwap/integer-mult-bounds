# Chronology, fusion, ownership and complete-cost screen

## Formal all-input identities

Write U3(a,b)=(Aa, D b+B a), U2(a,b)=(Aa, A b+F a), where B=D L A, F=A L A, L=P+2Q and all products refer to the source's separately tensorized letters. The exact base pure-word identities `D P A=M C2` and `D Q A=K a` are checked separately; tensorizing each pure identity gives `D_f(P_f+2Q_f)A_f=M_f C2_f+2K_f a_f` at every width. Each port is a finite chronological reversible word on two arbitrary banks. The source implements a monomial-weighted ADD by mapping/restoring its source, so no original input is silently copied or destroyed. The exact inverse of U3 is `(A^-1 t, D^-1 u-L t)` and of U2 is `(A^-1 t, A^-1 s-L t)`.

Composition U3(0,1) followed by U3(1,2) gives

    b0=A x0,
    b1=A D x1+A B x0,
    b2=D x2+B D x1+B² x0.

The second port therefore acts on `D x1+B x0`. It does not have the original x1 as its source. This is a literal substitution calculation, valid over any ring of compatible operators. Repeated substitution gives the u_j recurrence and five-bank endpoint in README. All five original inputs remain independent and present; no extra productive input or helper reward is introduced. The final ownership inventory is one original input per x_j, with an invertible but coupled output map. No output is credited as an autonomous job merely because its diagonal coefficient has a useful rank.

## Exact emitted fusion

Between each three-call port and the next port's first call, the shared bank undergoes the adjacent chronological sequence

    C0, W, C2, V, Z1, C0.

Its total operator is A D. The exact base identity `A D=N K`, with N a monomial whose entries are unit phases, gives the f-fold tensor identity `(AD)^(tensor f)=N_f K_f`. It involves no sum, so it does not make the invalid substitution `(P+2Q)^(tensor f)=P_f+2Q_f`. This replacement is therefore a rank3 Gaussian child followed by one actual monomial pass. The source per-column monomial odometer realizes N_f as an ordinary finite native pass, with owned workspace.

All four matches are present in the literal five-port word. They replace12 rank1 children by4 rank3 children. The first A on bank0 and closing A on bank0 have intervening cross-bank contacts and are retained. Raw profile `{1:14}` becomes `{1:2,3:4}`. The rank mass stays14; the nonlinear recursive moment changes. The all-rank1 small-unit model of #4628 is not silently changed to count a rank3 child as one rank1 call.

The emitted finite bill is6 child invocations (two of rank1, four of rank3),24 monomial passes and10 ADD passes: five with coefficient1 and five with coefficient2. These are array-level primitive counts, not a machine-time or precision certificate. Workspace remains a separately charged native resource. Fusing the Gaussian children also needs the ordinary caller's contract for a rank3 child; no custom arithmetic oracle is supplied by a matrix identity.

## Raw inverse transpose

For chronological gates G1,...,Gr, the primal operator is M=Gr...G1. Then M^-T=Gr^-T...G1^-T, so its chronological gate list has the same order, with each gate replaced by inverse transpose. For a unitary single-bank operator G this replacement is conjugate(G). For `dst += c src`, with real rational c here, it is `src -= c dst`. The raw dual has the same recursive profile `{1:2,3:4}`,24 monomial passes and10 ADD passes (with reversed direction and negated coefficients). The raw dual uses no complex conjugation in its bilinear pairing. Applying inverse primitives in reverse order instead constructs M^-1. The verifier checks these different constructions separately and rejects using the forward word as the raw dual.

## Scoped optimistic bound

Set t=1-C, 0<=C<1. Grant all five independent rank3 jobs, even though their extraction is still unproved, and set every finite bill to zero. This gives the upper bound

    legitimate reward <= 5*3^t,
    recursive cost >= 4*3^t+2,
    moment <= 3^t-2.

This upper bound is positive only for `C < 1-log(2)/log(3)`. It is a relaxation, not a κ value or evidence of a free consumer. If the same target census and paid profile require one additional ordinary rank1 child, the upper bound becomes `3^t-3<=0`, strictly negative for C>0. Hence there is no funded positive moment anywhere in this declared interval for that completion model, before compiler reserve and finite bills. The proof is interval-wide because 0<t<=1 implies 3^t<=3. A changed recursive profile, additional disjoint independent outputs or another consumer lies outside the bound.

## Explicit original-input reset policy

The alternative in WORD.json, `snapshot_restore`, saves each first-port output in an owned zero work field, applies D^-1 to the shared bank and subtracts L times the preceding retained A x. This restores the original input for the next port. Before the closing port it saves A x0 and restores x0 with A^-1. It has five original inputs and five zero-initialized dependent work fields; none of the work fields is a productive independent input.

Its emitted bill is23 rank1 calls,69 monomial passes and23 ADD passes, before returning the five saved outputs/work fields to the caller's required state. The checker verifies the exact original-input observations, not just their rank. Four D^-1 reset paths cost2 calls each; A^-1 costs1. In the restricted single-bank path model with only monomial maps between rank1 Gaussian calls, a column's support is at most2^s after s calls. D^-1 has support4 and A^-1 support2 at width1, so these reset counts are minimal within that path model. This does not constrain split-register free decoders, alternative storage protocols or changed heterogeneous recursive children.

The policy already exceeds the desired14 rank1 calls before full target recovery or work-field cleanup. No further attempt to optimize that unchanged policy is justified by its complete-cost screen. The retained-interface fusion above changes the premise and is the separate constructive lever; its free completion remains open.
